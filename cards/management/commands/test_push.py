"""
Команда для тестирования push-уведомлений.

Использование:
  python manage.py test_push --user=<phone>
  python manage.py test_push --user=<phone> --type=property
  python manage.py test_push --user=<phone> --type=promotion
  python manage.py test_push --check          # только проверить конфиг
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = "Тест push-уведомлений через FCM"

    def add_arguments(self, parser):
        parser.add_argument("--user", type=str, help="Номер телефона пользователя")
        parser.add_argument(
            "--type",
            type=str,
            default="system",
            choices=["system", "property", "promotion"],
            help="Тип уведомления (default: system)",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Только проверить конфигурацию Firebase",
        )

    def handle(self, *args, **options):
        if options["check"]:
            self._check_config()
            return

        phone = options["user"]
        if not phone:
            self.stderr.write("Укажи номер телефона: --user=+7...")
            return

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            self.stderr.write(f"Пользователь {phone} не найден")
            return

        # Показать токены пользователя
        from users.models import FCMDeviceToken
        tokens = FCMDeviceToken.objects.filter(user=user, is_active=True)
        if not tokens.exists():
            self.stderr.write(
                f"У пользователя {phone} нет активных FCM-токенов.\n"
                "Зайди в приложение и вызови POST /api/users/fcm-token/ с токеном устройства."
            )
            return

        self.stdout.write(f"Найдено {tokens.count()} активных токен(ов):")
        for t in tokens:
            self.stdout.write(f"  [{t.platform}] {t.token[:40]}...")

        # Отправить пуш
        from users.push_service import PushNotificationService

        notif_type_map = {
            "system": None,
            "property": PushNotificationService.TYPE_PROPERTY,
            "promotion": PushNotificationService.TYPE_PROMOTION,
        }
        notif_type = notif_type_map[options["type"]]

        self.stdout.write(f"\nОтправляю тестовый push [{options['type']}] → {phone}...")

        result = PushNotificationService.send_to_user(
            user,
            title="Тестовое уведомление",
            body=f"Это тест типа «{options['type']}». Если видишь — всё работает!",
            notification_type=notif_type,
            data={"test": "true"},
        )

        self.stdout.write(
            f"\nРезультат: успешно={result['success']}, "
            f"ошибок={result['failed']}"
        )
        if result["errors"]:
            for err in result["errors"]:
                self.stderr.write(f"  Ошибка: {err}")

    def _check_config(self):
        self.stdout.write("=== Проверка конфигурации Firebase ===\n")

        cred_path = getattr(settings, "FIREBASE_CREDENTIALS_PATH", None)
        if not cred_path:
            self.stderr.write("FIREBASE_CREDENTIALS_PATH не задан в settings/env")
            return

        import os
        if not os.path.exists(cred_path):
            self.stderr.write(f"Файл не найден: {cred_path}")
            return

        self.stdout.write(f"Credentials файл: {cred_path} — OK")

        try:
            import firebase_admin
            from firebase_admin import credentials, messaging
            self.stdout.write("firebase-admin пакет: установлен — OK")

            if not firebase_admin._apps:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self.stdout.write("Firebase инициализация: OK")
            else:
                self.stdout.write("Firebase уже инициализирован: OK")

        except ImportError:
            self.stderr.write("firebase-admin не установлен. Запусти: pip install firebase-admin")
        except Exception as e:
            self.stderr.write(f"Ошибка инициализации Firebase: {e}")
