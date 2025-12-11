from rest_framework import serializers
from .models import (
    Card, CardImage, CardVideo, CardDocument, CallRequest,
    CardReview, CardQuestion, SearchHistory,
    Favorite  
)
# 🔑 НОВОЕ: Импорт модели Developer из приложения developers
from developers.models import Developer

# -------------------------------
# 🔑 НОВЫЙ: Сериализатор для Застройщика (для вложения)
# -------------------------------
class DeveloperInCardSerializer(serializers.ModelSerializer):
    """Отображает ID, имя и логотип застройщика для вложения в карточку."""
    # Логотип (фото) в Django называется 'logo'
    class Meta:
        model = Developer
        fields = ['id', 'name', 'logo'] 


# -------------------------------
# Изображения, Видео, Документы
# -------------------------------
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


# -------------------------------
# Основной сериализатор карточки
# -------------------------------
class CardSerializer(serializers.ModelSerializer):
    images = CardImageSerializer(many=True, read_only=True)
    videos = CardVideoSerializer(many=True, read_only=True)
    documents = CardDocumentSerializer(many=True, read_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    reviews = serializers.StringRelatedField(many=True, read_only=True)
    questions = serializers.StringRelatedField(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()
    
    # 🔑 ИЗМЕНЕНО: Теперь отображает ID, имя и фото застройщика
    developer = DeveloperInCardSerializer(read_only=True) 

    class Meta:
        model = Card
        fields = [
            'id', 'title', 'address', 'description',
            'price', 'rooms', 'city', 'house_type',
            'area', 'building_material', 'category', 'floors_total', 
            'elevator', 'parking', 'balcony', 'ceiling_height',
            'latitude', 'longitude',
            'rating', 'rating_count',
            'owner', 
            'developer',  # 🔑 ДОБАВЛЕНО: Теперь Developer будет сериализован полностью
            'images', 'videos', 'documents',
            'reviews', 'questions',
            'created_at',
            'is_favorite'
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, card=obj).exists()
        return False


# -------------------------------
# Сериализаторы для добавления данных
# -------------------------------
class CardImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardImage
        fields = ['image']

class CardVideoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardVideo
        fields = ['video']

class CardDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardDocument
        fields = ['title', 'file']


# -------------------------------
# Сериализаторы для CallRequest, Reviews, Questions
# -------------------------------
class CallRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallRequest
        fields = ['id', 'phone_number', 'name', 'preferred_time', 'card']
        read_only_fields = ['card']

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


# -------------------------------
# Сериализатор для избранного (для MyFavoritesListAPIView)
# -------------------------------
class FavoriteSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'card']

# -------------------------------
# Сериализатор для истории поиска
# -------------------------------
class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['id', 'query', 'created_at']
        read_only_fields = ['user']

class CardQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardQuestion
        fields = ['id', 'card', 'user', 'question', 'answer', 'created_at']
        read_only_fields = ['card', 'user', 'answer', 'created_at']