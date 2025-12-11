import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Card
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
        # создаём уведомление в базе
        Notification.objects.create(
            user=sub.user,
            title="Новая квартира от вашего девелопера",
            message=f"{instance.title} — {instance.price}₽, {instance.rooms} комн."
        )

    # Если channels установлен, отправляем WebSocket уведомление
    if HAS_CHANNELS:
        try:
            channel_layer = get_channel_layer()
            for sub in subs:
                async_to_sync(channel_layer.group_send)(
                    f"user_{sub.user.id}",
                    {
                        "type": "send_notification",
                        "title": "Новая квартира от вашего девелопера",
                        "message": f"{instance.title} — {instance.price}₽, {instance.rooms} комн."
                    }
                )
        except Exception as e:
            logger.exception("Ошибка при отправке WebSocket уведомления: %s", e)
