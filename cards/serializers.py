from rest_framework import serializers
from .models import (
    Card, CardImage, CardVideo, CardDocument, CallRequest,
    CardReview, CardQuestion, SearchHistory
)

# --- Изображения и видео ---
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

# --- Основной сериализатор карточки ---
class CardSerializer(serializers.ModelSerializer):
    images = CardImageSerializer(many=True, read_only=True)
    videos = CardVideoSerializer(many=True, read_only=True)
    documents = CardDocumentSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    reviews = serializers.StringRelatedField(many=True, read_only=True)
    questions = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'title', 'address', 'description',
            'price', 'rooms', 'city', 'house_type',
            'area', 'building_material', 'category', 'floors_total',
            'elevator', 'parking', 'balcony', 'ceiling_height',
            'latitude', 'longitude',
            'rating', 'rating_count',
            'owner', 'images', 'videos', 'documents',
            'reviews', 'questions',
            'created_at'
        ]

# --- Создание документа ---
class CardDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardDocument
        fields = ['title', 'file']

    def create(self, validated_data):
        card = self.context['card']
        return CardDocument.objects.create(card=card, **validated_data)

# --- Заявки на звонок ---
class CallRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRequest
        fields = ['id', 'phone_number', 'name', 'preferred_time', 'card']
        read_only_fields = ['card']

# --- Отзывы и вопросы ---
class CardReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = CardReview
        fields = ['id', 'user', 'text', 'rating', 'created_at']

class CardQuestionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = CardQuestion
        fields = ['id', 'user', 'question', 'answer', 'created_at']

# --- История поиска ---
class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'created_at']
