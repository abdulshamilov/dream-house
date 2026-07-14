# Написана вручную: локальный makemigrations не работает из-за отсутствующей
# в этой копии репозитория миграции cards.0041_merge_20260712_2045.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("notifications", "0005_alter_notification_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationUserState",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_read", models.BooleanField(default=False)),
                ("is_hidden", models.BooleanField(default=False)),
                (
                    "notification",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_states",
                        to="notifications.notification",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_states",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Состояние уведомления у пользователя",
                "verbose_name_plural": "Состояния уведомлений у пользователей",
                "unique_together": {("user", "notification")},
            },
        ),
    ]
