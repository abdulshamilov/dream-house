from rest_framework import serializers
from .models import Card, CardImage
from .models import CallRequest

class CardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardImage
        fields = ['id', 'image']


class CardSerializer(serializers.ModelSerializer):
    images = CardImageSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Card
        fields = [
    'id', 'title', 'address', 'description',
    'price', 'rooms', 'city', 'house_type',
    'area', 'building_material', 'category', 'floors_total',
    'elevator', 'parking', 'balcony', 'ceiling_height',
    'latitude', 'longitude', 'housing_account',
    'rating', 'rating_count',
    'owner', 'images', 'created_at'
]



class CallRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRequest
        fields = ['id', 'phone_number', 'name', 'preferred_time', 'card']
        read_only_fields = ['card']  # 🔹 card теперь не нужно отправлять в теле запроса
