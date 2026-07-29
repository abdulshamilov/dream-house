from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Developer, Subscription
from cards.serializers import CardSerializer


def _developer_avatar(obj, request):
    """Первое непустое фото объектов застройщика (логотип не используется).

    Идёт по префетченным cards/images (см. prefetch_related во вьюхах),
    поэтому на списках не создаёт N+1.
    """
    for card in obj.cards.all():
        if getattr(card, 'is_hidden', False):
            continue
        for img in card.images.all():
            if img.image:
                url = img.image.url
                return request.build_absolute_uri(url) if request else url
    return None


class DeveloperAvatarMixin(serializers.Serializer):
    avatar = serializers.SerializerMethodField()

    @extend_schema_field(serializers.URLField(allow_null=True))
    def get_avatar(self, obj):
        request = self.context.get('request') if self.context else None
        return _developer_avatar(obj, request)


class DeveloperLightSerializer(DeveloperAvatarMixin, serializers.ModelSerializer):
    """Упрощенный сериализатор для списков подписок (без карточек)."""
    class Meta:
        model = Developer
        fields = ['id', 'name', 'phone', 'logo', 'avatar']

class DeveloperSerializer(DeveloperAvatarMixin, serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Developer
        fields = ['id', 'name', 'phone', 'logo', 'avatar', 'cards', 'is_subscribed']

    @extend_schema_field(serializers.BooleanField)
    def get_is_subscribed(self, obj):
        req = self.context.get('request') if self.context else None
        user = getattr(req, 'user', None)
        if user and user.is_authenticated:
            return Subscription.objects.filter(user=user, developer=obj).exists()
        return False

class SubscriptionSerializer(serializers.ModelSerializer):
    developer = DeveloperSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'developer', 'created_at']
        read_only_fields = ['created_at']


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Легкий вывод подписок для мобильного списка."""
    developer = DeveloperLightSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'developer', 'created_at']
        read_only_fields = ['created_at']
