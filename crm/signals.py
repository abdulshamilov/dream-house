import logging
import threading
import requests
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Lead

logger = logging.getLogger(__name__)


def _notify_bot(event: str, lead_id: int):
    bot_url = getattr(settings, 'BOT_NOTIFY_URL', 'http://127.0.0.1:8001')
    secret = getattr(settings, 'BOT_API_SECRET', '')
    try:
        requests.post(
            f'{bot_url}/notify/{event}',
            json={'lead_id': lead_id},
            headers={'X-Bot-Secret': secret},
            timeout=3,
        )
    except Exception as exc:
        logger.warning('Bot notify failed [%s lead=%s]: %s', event, lead_id, exc)


@receiver(post_save, sender=Lead)
def lead_post_save(sender, instance, created, **kwargs):
    if getattr(instance, '_skip_bot_notification', False):
        return
    event = 'new_lead' if created else 'lead_updated'
    threading.Thread(
        target=_notify_bot,
        args=(event, instance.pk),
        daemon=True,
    ).start()
