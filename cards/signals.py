import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Card, DiscountRequest, Promotion
from developers.models import Subscription
from notifications.models import Notification

logger = logging.getLogger(__name__)

# Опциональный импорт channels (может быть не установлен в dev)
try:
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    HAS_CHANNELS = True
except ImportError:
    logger.warning("Channels не установлен. WebSocket уведомления отключены.")
    HAS_CHANNELS = False

@receiver(post_save, sender=Card)
def notify_developer_subscribers(sender, instance, created, **kwargs):
    """
    Отправляет уведомление пользователям, подписанным на девелопера,
    когда создаётся новая карточка.
    """
    if not created or not instance.developer:
        return

    subs = Subscription.objects.filter(developer=instance.developer)

    for sub in subs:
        # создаём уведомление в базе с привязкой к карточке
        Notification.objects.create(
            user=sub.user,
            card=instance,  # 🔑 Привязка к карточке для image_url/price
            type=Notification.TYPE_SUBSCRIPTION,
            title="Новая квартира от застройщика",
            message=f"{instance.developer.name}: {instance.title} — {instance.price}₽, {instance.rooms} комн."
        )

    # Если channels установлен, отправляем WebSocket уведомление
    if HAS_CHANNELS:
        try:
            channel_layer = get_channel_layer()
            if channel_layer is not None:
                for sub in subs:
                    async_to_sync(channel_layer.group_send)(
                        f"user_{sub.user.id}",
                        {
                            "type": "send_notification",
                            "title": "Новая квартира от застройщика",
                            "message": f"{instance.developer.name}: {instance.title} — {instance.price}₽, {instance.rooms} комн."
                        }
                    )
        except Exception as e:
            logger.warning(f"WebSocket error: {e}")


@receiver(post_save, sender=DiscountRequest)
def notify_on_discount_request(sender, instance, created, **kwargs):
    """
    Создаёт уведомления для владельца квартиры и пользователя при скидке
    """
    if not created:
        return

    # Уведомление для владельца квартиры
    if instance.card.owner:
        Notification.objects.create(
            user=instance.card.owner,
            title="Запрос на скидку",
            message=f"Пользователь предложил {instance.requested_price}₽ за {instance.card.title} (было {instance.original_price}₽)"
        )

    # Уведомление для пользователя
    Notification.objects.create(
        user=instance.user,
        title="Ваш запрос на скидку отправлен",
        message=f"Запрос на скидку отправлен владельцу {instance.card.title}. Статус: На рассмотрении"
    )

    # WebSocket уведомления (только если channels настроены)
    if HAS_CHANNELS:
        try:
            channel_layer = get_channel_layer()
            
            # Проверить что channel_layer не None
            if channel_layer is None:
                return
            
            # Уведомление владельцу
            if instance.card.owner:
                async_to_sync(channel_layer.group_send)(
                    f"user_{instance.card.owner.id}",
                    {
                        "type": "send_notification",
                        "title": "Запрос на скидку",
                        "message": f"Пользователь предложил {instance.requested_price}₽ за {instance.card.title}"
                    }
                )
            
            # Уведомление пользователю
            async_to_sync(channel_layer.group_send)(
                f"user_{instance.user.id}",
                {
                    "type": "send_notification",
                    "title": "Ваш запрос на скидку отправлен",
                    "message": f"Запрос отправлен владельцу {instance.card.title}"
                }
            )
        except Exception as e:
            logger.warning(f"WebSocket error: {e}")


@receiver(post_save, sender=Promotion)
def notify_users_on_promotion(sender, instance, created, **kwargs):
    """
    Отправляет пуш-уведомления всем пользователям при создании новой акции.
    Уведомляет только пользователей с включенными уведомлениями об акциях.
    """
    if not created or not instance.is_active:
        return

    from django.contrib.auth import get_user_model
    from notifications.models import NotificationSettings
    
    User = get_user_model()
    
    # Получить всех пользователей с включенными уведомлениями об акциях
    users_with_promo_enabled = User.objects.filter(
        is_active=True
    ).exclude(
        notification_settings__promotions=False
    )
    
    # Получить первую карточку из акции для превью (если есть)
    first_item = instance.items.first()
    card = first_item.card if first_item else None
    
    notifications_to_create = []
    for user in users_with_promo_enabled:
        notifications_to_create.append(
            Notification(
                user=user,
                card=card,
                type=Notification.TYPE_SALE,
                title=f"Новая акция: {instance.title}",
                message=f"Посмотрите выгодные предложения в акции «{instance.title}»"
            )
        )
    
    # Bulk create для производительности
    if notifications_to_create:
        Notification.objects.bulk_create(notifications_to_create)
        logger.info(f"Created {len(notifications_to_create)} notifications for promotion '{instance.title}'")
    
    # WebSocket уведомления
    if HAS_CHANNELS:
        try:
            channel_layer = get_channel_layer()
            if channel_layer is None:
                return
            
            for user in users_with_promo_enabled:
                async_to_sync(channel_layer.group_send)(
                    f"user_{user.id}",
                    {
                        "type": "send_notification",
                        "title": f"Новая акция: {instance.title}",
                        "message": f"Посмотрите выгодные предложения!"
                    }
                )
        except Exception as e:
            logger.warning(f"WebSocket error for promotion: {e}")

