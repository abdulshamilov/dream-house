# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Referral

@receiver(post_save, sender=User)
def create_referral(sender, instance, created, **kwargs):
    if created:
        ref_code = getattr(instance, 'ref_code', None)
        if ref_code:
            try:
                referrer = User.objects.get(referral_code=ref_code)
                Referral.objects.create(referrer=referrer, referred=instance)
            except User.DoesNotExist:
                pass
