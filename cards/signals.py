from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Card
from developers.models import Subscription
from notifications.models import Notification
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=Card)
def notify_developer_subscribers(sender, instance, created, **kwargs):
    """
    Отправляет уведомление пользователям, подписанным на девелопера,
    когда создаётся новая карточка.
    """
    if not created or not instance.developer:
        return

    subs = Subscription.objects.filter(developer=instance.developer)
    channel_layer = get_channel_layer()

    for sub in subs:
        # создаём уведомление в базе
        Notification.objects.create(
            user=sub.user,
            title="Новая квартира от вашего девелопера",
            message=f"{instance.title} — {instance.price}₽, {instance.rooms} комн."
        )

        # пуш через WebSocket
        async_to_sync(channel_layer.group_send)(
            f"user_{sub.user.id}",
            {
                "type": "send_notification",
                "title": "Новая квартира от вашего девелопера",
                "message": f"{instance.title} — {instance.price}₽, {instance.rooms} комн."
            }
        )
