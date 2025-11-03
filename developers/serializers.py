from rest_framework import serializers
from .models import Developer, Subscription
from cards.models import Card


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'title', 'address', 'price', 'rooms', 'city', 'house_type']


class DeveloperSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)  # ЖК застройщика

    class Meta:
        model = Developer
        fields = ['id', 'name', 'logo', 'cards']


class SubscriptionSerializer(serializers.ModelSerializer):
    developer = DeveloperSerializer(read_only=True)  # ✅ показываем данные застройщика

    class Meta:
        model = Subscription
        fields = ['id', 'developer', 'created_at']
