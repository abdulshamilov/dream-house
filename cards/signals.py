import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Card, DiscountRequest, Review
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
            if channel_layer is not None:
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


@receiver(post_save, sender=Review)
def update_card_rating_on_review(sender, instance, **kwargs):
    """
    Автоматически обновляет рейтинг карточки при создании/обновлении отзыва
    """
    instance.card.update_rating()
