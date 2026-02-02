from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from .models import Notification


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

    def get_card_id(self, obj):
        if not obj.card_id:
            return None
        return str(obj.card_id)

    def get_image_url(self, obj):
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

    def get_price(self, obj):
        card = getattr(obj, "card", None)
        if not card or card.price is None:
            return None
        return self._to_int(card.price)

    def get_old_price(self, obj):
        if obj.old_price is None:
            return None

        price_value = None
        if obj.card and obj.card.price is not None:
            price_value = Decimal(str(obj.card.price))

        old_price_decimal = Decimal(str(obj.old_price))

        # Only return old_price if it is greater than current price when price is known
        if price_value is not None and old_price_decimal <= price_value:
            return None

        return int(old_price_decimal.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
