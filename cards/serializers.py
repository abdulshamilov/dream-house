from rest_framework import serializers
from .models import Card, CardImage

class CardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardImage
        fields = ['id', 'image']

class CardSerializer(serializers.ModelSerializer):
    images = CardImageSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Card
        fields = ['id', 'title', 'address', 'description', 'price', 'owner', 'images', 'created_at']
