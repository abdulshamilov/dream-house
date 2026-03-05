"""
Push Notification Service

Отправка push-уведомлений на Android (FCM) и iOS (APNs)

Типы уведомлений (type в data):
- "property" — новые объекты недвижимости
- "promotion" — акции и скидки
- без type — системные уведомления
"""

import logging
from typing import Optional, List, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

# Firebase Admin SDK (для Android)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logger.warning("firebase-admin не установлен. Push для Android недоступны.")

# APNs (для iOS)
try:
    import jwt
    import httpx
    APNS_AVAILABLE = True
except ImportError:
    APNS_AVAILABLE = False
    logger.warning("PyJWT или httpx не установлены. Push для iOS недоступны.")

import time
from pathlib import Path


class PushNotificationService:
    """Сервис отправки push-уведомлений"""
    
    # Типы уведомлений для каналов
    TYPE_PROPERTY = "property"      # Новые объекты
    TYPE_PROMOTION = "promotion"    # Акции
    TYPE_SYSTEM = None              # Системные (без type)
    
    _firebase_initialized = False
    _apns_token = None
    _apns_token_expires = 0
    
    @classmethod
    def _init_firebase(cls):
        """Инициализация Firebase Admin SDK"""
        if cls._firebase_initialized or not FIREBASE_AVAILABLE:
            return
        
        cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
        if not cred_path:
            logger.error("FIREBASE_CREDENTIALS_PATH не настроен в settings.py")
            return
        
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            cls._firebase_initialized = True
            logger.info("Firebase Admin SDK инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации Firebase: {e}")
    
    @classmethod
    def _get_apns_token(cls) -> Optional[str]:
        """Получить JWT токен для APNs"""
        if not APNS_AVAILABLE:
            return None
        
        # Проверяем, не истёк ли токен (обновляем за 5 минут до истечения)
        if cls._apns_token and time.time() < cls._apns_token_expires - 300:
            return cls._apns_token
        
        key_path = getattr(settings, 'APNS_KEY_PATH', None)
        key_id = getattr(settings, 'APNS_KEY_ID', None)
        team_id = getattr(settings, 'APNS_TEAM_ID', None)
        
        if not all([key_path, key_id, team_id]):
            logger.error("APNs настройки не полные: APNS_KEY_PATH, APNS_KEY_ID, APNS_TEAM_ID")
            return None
        
        try:
            with open(key_path, 'r') as f:
                private_key = f.read()
            
            now = int(time.time())
            cls._apns_token_expires = now + 3600  # 1 час
            
            payload = {
                'iss': team_id,
                'iat': now,
            }
            
            cls._apns_token = jwt.encode(
                payload,
                private_key,
                algorithm='ES256',
                headers={'kid': key_id}
            )
            
            logger.info("APNs JWT токен создан")
            return cls._apns_token
            
        except Exception as e:
            logger.error(f"Ошибка создания APNs токена: {e}")
            return None
    
    @classmethod
    def send_to_user(
        cls,
        user,
        title: str,
        body: str,
        notification_type: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Отправить push-уведомление пользователю на все его устройства
        
        Args:
            user: Объект User
            title: Заголовок уведомления
            body: Текст уведомления
            notification_type: Тип ("property", "promotion" или None для системных)
            data: Дополнительные данные
        
        Returns:
            {"success": int, "failed": int, "errors": list}
        """
        from .models import FCMDeviceToken
        
        tokens = FCMDeviceToken.objects.filter(user=user, is_active=True)
        
        result = {"success": 0, "failed": 0, "errors": []}
        
        for device in tokens:
            try:
                if device.platform == 'android':
                    success = cls._send_fcm(device.token, title, body, notification_type, data)
                else:  # ios
                    success = cls._send_apns(device.token, title, body, notification_type, data)
                
                if success:
                    result["success"] += 1
                else:
                    result["failed"] += 1
                    
            except Exception as e:
                result["failed"] += 1
                result["errors"].append(str(e))
                logger.error(f"Ошибка отправки push на {device.platform}: {e}")
                
                # Деактивируем невалидные токены
                if "not registered" in str(e).lower() or "invalid" in str(e).lower():
                    device.is_active = False
                    device.save()
        
        return result
    
    @classmethod
    def send_to_users(
        cls,
        users: List,
        title: str,
        body: str,
        notification_type: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Отправить push-уведомление нескольким пользователям
        """
        total_result = {"success": 0, "failed": 0, "errors": []}
        
        for user in users:
            result = cls.send_to_user(user, title, body, notification_type, data)
            total_result["success"] += result["success"]
            total_result["failed"] += result["failed"]
            total_result["errors"].extend(result["errors"])
        
        return total_result
    
    @classmethod
    def _send_fcm(
        cls,
        token: str,
        title: str,
        body: str,
        notification_type: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Отправить push через Firebase Cloud Messaging (Android)"""
        if not FIREBASE_AVAILABLE:
            logger.warning("Firebase не доступен")
            return False
        
        cls._init_firebase()
        
        if not cls._firebase_initialized:
            return False
        
        # Формируем data payload
        data = extra_data.copy() if extra_data else {}
        if notification_type:
            data['type'] = notification_type
        
        # Конвертируем все значения в строки (FCM требует string values)
        data = {k: str(v) for k, v in data.items()}
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data,
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        channel_id=cls._get_android_channel(notification_type),
                        sound='default',
                    ),
                ),
            )
            
            response = messaging.send(message)
            logger.info(f"FCM отправлен: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка FCM: {e}")
            raise
    
    @classmethod
    def _send_apns(
        cls,
        token: str,
        title: str,
        body: str,
        notification_type: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Отправить push через Apple Push Notification service (iOS)"""
        if not APNS_AVAILABLE:
            logger.warning("APNs не доступен")
            return False
        
        jwt_token = cls._get_apns_token()
        if not jwt_token:
            return False
        
        bundle_id = getattr(settings, 'APNS_BUNDLE_ID', None)
        if not bundle_id:
            logger.error("APNS_BUNDLE_ID не настроен")
            return False
        
        # Production или Sandbox
        use_sandbox = getattr(settings, 'APNS_USE_SANDBOX', True)
        host = "api.sandbox.push.apple.com" if use_sandbox else "api.push.apple.com"
        
        # Формируем payload
        data = extra_data.copy() if extra_data else {}
        if notification_type:
            data['type'] = notification_type
        
        payload = {
            "aps": {
                "alert": {
                    "title": title,
                    "body": body,
                },
                "sound": "default",
                "badge": 1,
            },
            **data
        }
        
        headers = {
            "authorization": f"bearer {jwt_token}",
            "apns-topic": bundle_id,
            "apns-push-type": "alert",
            "apns-priority": "10",
        }
        
        try:
            with httpx.Client(http2=True) as client:
                response = client.post(
                    f"https://{host}/3/device/{token}",
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    logger.info(f"APNs отправлен успешно")
                    return True
                else:
                    logger.error(f"APNs ошибка {response.status_code}: {response.text}")
                    raise Exception(f"APNs error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Ошибка APNs: {e}")
            raise
    
    @classmethod
    def _get_android_channel(cls, notification_type: Optional[str]) -> str:
        """Получить ID канала для Android в зависимости от типа уведомления"""
        if notification_type == cls.TYPE_PROPERTY:
            return "property_channel"
        elif notification_type == cls.TYPE_PROMOTION:
            return "promotion_channel"
        else:
            return "default_channel"


# Удобные функции для быстрого использования
def send_property_notification(user, title: str, body: str, card_id: Optional[int] = None):
    """Отправить уведомление о новом объекте"""
    data = {"card_id": card_id} if card_id else None
    return PushNotificationService.send_to_user(
        user, title, body, 
        notification_type=PushNotificationService.TYPE_PROPERTY,
        data=data
    )


def send_promotion_notification(user, title: str, body: str, promotion_id: Optional[int] = None):
    """Отправить уведомление об акции"""
    data = {"promotion_id": promotion_id} if promotion_id else None
    return PushNotificationService.send_to_user(
        user, title, body,
        notification_type=PushNotificationService.TYPE_PROMOTION,
        data=data
    )


def send_system_notification(user, title: str, body: str, data: Optional[Dict] = None):
    """Отправить системное уведомление"""
    return PushNotificationService.send_to_user(
        user, title, body,
        notification_type=None,
        data=data
    )
