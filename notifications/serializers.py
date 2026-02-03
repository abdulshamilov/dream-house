from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from .models import Notification, NotificationSettings


class NotificationSerializer(serializers.ModelSerializer):
    card_id = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    old_price = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "message",
            "type",
            "is_read",
            "created_at",
            "card_id",
            "image_url",
            "price",
            "old_price",
        )
        read_only_fields = (
            "user",
            "title",
            "message",
            "created_at",
            "type",
            "card_id",
            "image_url",
            "price",
            "old_price",
        )

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_card_id(self, obj) -> Optional[str]:
        if not obj.card_id:
            return None
        return str(obj.card_id)

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_image_url(self, obj) -> Optional[str]:
        card = getattr(obj, "card", None)
        if not card:
            return None

        first_image = card.images.first()
        if not first_image or not first_image.image:
            return None

        request = self.context.get("request") if hasattr(self, "context") else None
        try:
            # build absolute URL if request is available
            return request.build_absolute_uri(first_image.image.url) if request else first_image.image.url
        except Exception:
            return None

    def _to_int(self, value):
        # Convert Decimal/float/str to rounded int for API contract
        decimal_value = Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return int(decimal_value)

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_price(self, obj) -> Optional[int]:
        card = getattr(obj, "card", None)
        if not card or card.price is None:
            return None
        return self._to_int(card.price)

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_old_price(self, obj) -> Optional[int]:
        if obj.old_price is None:
            return None
        old_price_decimal = Decimal(str(obj.old_price))
        return int(old_price_decimal.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationSettings
        fields = ("enabled",)
