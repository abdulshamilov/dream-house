from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_PRICE_DROP = "price_drop"
    TYPE_SALE = "sale"
    TYPE_DISCOUNT = "discount"
    TYPE_SUBSCRIPTION = "subscription"
    TYPE_NEW = "new"
    TYPE_SYSTEM = "system"

    TYPE_CHOICES = (
        (TYPE_PRICE_DROP, "Price drop"),
        (TYPE_SALE, "Sale"),
        (TYPE_DISCOUNT, "Discount"),
        (TYPE_SUBSCRIPTION, "Subscription"),
        (TYPE_NEW, "New"),
        (TYPE_SYSTEM, "System"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    type = models.CharField(
        max_length=50, choices=TYPE_CHOICES, null=True, blank=True
    )
    card = models.ForeignKey(
        "cards.Card",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    old_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Previous price before discount",
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class NotificationSettings(models.Model):
    """Per-user notification preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_settings",
    )
    push_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=False)
    new_cards = models.BooleanField(default=True)
    price_changes = models.BooleanField(default=True)
    subscription_updates = models.BooleanField(default=True)
    promotions = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Настройки уведомлений"
        verbose_name_plural = "Настройки уведомлений"

    def __str__(self):
        return f"Notification settings for {self.user_id}"
