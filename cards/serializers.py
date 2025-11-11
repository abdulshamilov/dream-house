from rest_framework import serializers
from .models import Card, CardImage, CardVideo, CardDocument, CallRequest

# Сериализаторы изображений и видео
class CardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardImage
        fields = ['id', 'image']


class CardVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardVideo
        fields = ['id', 'video']


class CardDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardDocument
        fields = ['id', 'title', 'file', 'uploaded_at']


# Основной сериализатор карточки
class CardSerializer(serializers.ModelSerializer):
    images = CardImageSerializer(many=True, read_only=True)
    videos = CardVideoSerializer(many=True, read_only=True)
    documents = CardDocumentSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'title', 'address', 'description',
            'price', 'rooms', 'city', 'house_type',
            'area', 'building_material', 'category', 'floors_total',
            'elevator', 'parking', 'balcony', 'ceiling_height',
            'latitude', 'longitude',
            'rating', 'rating_count',
            'owner', 'images', 'videos', 'documents', 'created_at'
        ]


# Сериализатор для добавления документа
class CardDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardDocument
        fields = ['title', 'file']

    def create(self, validated_data):
        card = self.context['card']
        return CardDocument.objects.create(card=card, **validated_data)


# Сериализатор заявок на звонок
class CallRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRequest
        fields = ['id', 'phone_number', 'name', 'preferred_time', 'card']
        read_only_fields = ['card']  # привязка к карточке будет через view
