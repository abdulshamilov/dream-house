from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Developer, Subscription
from cards.serializers import CardSerializer


class DeveloperLightSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списков подписок (без карточек)."""
    class Meta:
        model = Developer
        fields = ['id', 'name', 'logo']

class DeveloperSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Developer
        fields = ['id', 'name', 'logo', 'cards', 'is_subscribed']

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
