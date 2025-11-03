from rest_framework import serializers
from .models import Developer, Subscription
from cards.serializers import CardSerializer


class DeveloperSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)  # ЖК (карточки) застройщика

    class Meta:
        model = Developer
        fields = ['id', 'name', 'logo', 'cards']


class SubscriptionSerializer(serializers.ModelSerializer):
    developer = DeveloperSerializer(read_only=True)  # ✅ Показывает весь объект застройщика

    class Meta:
        model = Subscription
        fields = ['id', 'developer', 'created_at']
        read_only_fields = ['created_at']
