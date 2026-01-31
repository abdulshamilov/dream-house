# DRF
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

# Local
from .models import (
    Card, CardImage, CardVideo, CardDocument, CallRequest,
    CardReview, CardQuestion, SearchHistory, ReviewLike,
    Favorite, DiscountRequest, Recommendation, ChatMessage, AIAssistant,
    CardDocumentList, ViewHistory, Promotion, PromotionItem
)
from developers.models import Developer

# ============ USER SERIALIZERS ============
class UserSimpleSerializer(serializers.Serializer):
    """Упрощенные данные пользователя для отзывов и вопросов"""
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    profile_photo = serializers.ImageField(read_only=True)


class CardQuestionSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    answer = serializers.CharField(read_only=True)

    class Meta:
        model = CardQuestion
        fields = ['id', 'user', 'question', 'answer', 'created_at']

# -------------------------------
# 🔑 НОВЫЙ: Сериализатор для Застройщика (для вложения)
# -------------------------------
class DeveloperInCardSerializer(serializers.ModelSerializer):
    """Отображает ID, имя, логотип застройщика и статус подписки"""
    is_subscribed = serializers.SerializerMethodField()
    
    class Meta:
        model = Developer
        fields = ['id', 'name', 'logo', 'is_subscribed']
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_subscribed(self, obj):
        request = self.context.get('request') if self.context else None
        user = getattr(request, 'user', None) if request else None
        if user and user.is_authenticated:
            from developers.models import Subscription
            return Subscription.objects.filter(user=user, developer=obj).exists()
        return False 


# -------------------------------
# Изображения, Видео, Документы
# -------------------------------
class CardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardImage
        fields = ['id', 'image']


# 🔑 НОВЫЙ: Упрощенный сериализатор для подборок карточек (быстрый результат)
class CardCurationSerializer(serializers.ModelSerializer):
    """Минимальная информация о карточке для подборок"""
    developer = DeveloperInCardSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField()
    price_metr = serializers.SerializerMethodField()  # 🔑 НОВОЕ: Цена за кв.м
    
    class Meta:
        model = Card
        fields = [
            'id', 'title', 'address', 'price', 'price_metr',  # 🔑 НОВОЕ: Цена за кв.м
            'rooms', 'area', 'city', 'rating', 'developer', 'is_favorite',
            'latitude', 'longitude'
        ]
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, card=obj).exists()
        return False
    
    @extend_schema_field(serializers.FloatField)
    def get_price_metr(self, obj):
        """Получить цену за квадратный метр"""
        return round(obj.price_metr, 2) if obj.area and obj.area > 0 else 0


class PromotionItemSerializer(serializers.ModelSerializer):
    card = CardCurationSerializer(read_only=True)

    class Meta:
        model = PromotionItem
        fields = ['card', 'discount_percent', 'benefit_amount', 'valid_until']


class PromotionSerializer(serializers.ModelSerializer):
    banner_image = serializers.SerializerMethodField()
    items = PromotionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Promotion
        fields = ['id', 'title', 'banner_image', 'items']

    def get_banner_image(self, obj):
        if obj.banner_image:
            request = self.context.get('request')
            url = obj.banner_image.url
            return request.build_absolute_uri(url) if request else url
        return None

class CardVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardVideo
        fields = ['id', 'video']

class CardDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardDocument
        fields = ['id', 'title', 'file', 'uploaded_at']


# 🔑 НОВЫЙ: Сериализатор для подборок документов
class CardDocumentListSerializer(serializers.ModelSerializer):
    """Подборка документов с названием"""
    files = serializers.SerializerMethodField()
    
    class Meta:
        model = CardDocumentList
        fields = ['id', 'name', 'files']
    
    @extend_schema_field(CardDocumentSerializer(many=True))
    def get_files(self, obj):
        """Получить все файлы в этой подборке"""
        files = obj.files.all()  # Используем related_name 'files'
        return CardDocumentSerializer(files, many=True).data


# -------------------------------
# Сериализатор отзывов (используется в CardSerializer)
# -------------------------------
class CardReviewSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    likes_count = serializers.SerializerMethodField()  # 🔑 НОВОЕ: Количество лайков
    is_liked = serializers.SerializerMethodField()     # 🔑 НОВОЕ: Лайкнул ли текущий пользователь
    # Поля под фронтовый интерфейс IReview
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    helpful_count = serializers.SerializerMethodField()
    not_helpful_count = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    developer_response = serializers.SerializerMethodField()
    
    class Meta:
        model = CardReview
        fields = [
            'id', 'user', 'text', 'rating', 'likes_count', 'is_liked', 'created_at', 'updated_at',
            # Совместимость с IReview
            'user_name', 'user_avatar', 'comment', 'images',
            'helpful_count', 'not_helpful_count', 'user_vote', 'developer_response'
        ]
        read_only_fields = [
            'likes_count', 'is_liked', 'user_name', 'user_avatar', 'comment', 'images',
            'helpful_count', 'not_helpful_count', 'user_vote', 'developer_response'
        ]
    
    @extend_schema_field(serializers.IntegerField)
    def get_likes_count(self, obj):
        """Получить количество лайков"""
        return obj.likes_count
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_liked(self, obj):
        """Проверить лайкнул ли текущий пользователь этот отзыв"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            from .models import ReviewLike
            return ReviewLike.objects.filter(review=obj, user=request.user).exists()
        return False

    # --- Дополнительные поля под IReview ---
    @extend_schema_field(serializers.CharField)
    def get_user_name(self, obj):
        return getattr(obj.user, 'name', '') or obj.user.phone_number

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_user_avatar(self, obj):
        photo = getattr(obj.user, 'profile_photo', None)
        if photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(photo.url)
            return photo.url
        return None

    @extend_schema_field(serializers.CharField)
    def get_comment(self, obj):
        return obj.text

    @extend_schema_field(serializers.ListField(child=serializers.CharField(), allow_empty=True))
    def get_images(self, obj):
        # Сейчас картинки у отзывов не храним
        return []

    @extend_schema_field(serializers.IntegerField)
    def get_helpful_count(self, obj):
        # Используем лайки как "полезно"
        return obj.likes_count

    @extend_schema_field(serializers.IntegerField)
    def get_not_helpful_count(self, obj):
        # Не реализовано — возвращаем 0
        return 0

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_user_vote(self, obj):
        if self.get_is_liked(obj):
            return 'helpful'
        return None

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_developer_response(self, obj):
        # Ответ девелопера не реализован
        return None


# -------------------------------
# Основной сериализатор карточки
# -------------------------------
class CardSerializer(serializers.ModelSerializer):
    images = CardImageSerializer(many=True, read_only=True)
    videos = CardVideoSerializer(many=True, read_only=True)
    documents = CardDocumentSerializer(many=True, read_only=True)
    document_lists = CardDocumentListSerializer(many=True, read_only=True)  # 🔑 НОВОЕ
    owner = serializers.StringRelatedField(read_only=True)
    reviews = serializers.SerializerMethodField()
    questions = CardQuestionSerializer(many=True, read_only=True)
    is_favorite = serializers.SerializerMethodField()
    list_curations = serializers.SerializerMethodField()  # 🔑 НОВОЕ: Подборки как объекты
    
    # 🔑 ИЗМЕНЕНО: Теперь отображает ID, имя и фото застройщика
    developer = DeveloperInCardSerializer(read_only=True)
    price_metr = serializers.SerializerMethodField()  # 🔑 НОВОЕ: Цена за кв.м

    class Meta:
        model = Card
        fields = [
            'id', 'title', 'address', 'description',
            'price', 'price_metr',  # 🔑 НОВОЕ: Цена за квадратный метр
            'rooms', 'city', 'house_type',
            'area', 'building_material', 'category', 'floors_total', 
            'elevator', 'parking', 'balcony', 'loggia', 'finishing', 'ceiling_height',
            'latitude', 'longitude',
            'rating', 'rating_count',
            'owner', 
            'developer',  # 🔑 ДОБАВЛЕНО: Теперь Developer будет сериализован полностью
            'images', 'videos', 'documents', 'document_lists',  # 🔑 ИЗМЕНЕНО
            'reviews', 'questions',
            'list_curations',  # 🔑 НОВОЕ: Подборки квартир
            'created_at',
            'is_favorite'
        ]

    @extend_schema_field(CardReviewSerializer(many=True))
    def get_reviews(self, obj):
        qs = obj.reviews.all().order_by('-created_at')
        return CardReviewSerializer(qs, many=True, context=self.context).data
    
    @extend_schema_field(serializers.FloatField)
    def get_price_metr(self, obj):
        """Получить цену за квадратный метр"""
        return round(obj.price_metr, 2) if obj.area and obj.area > 0 else 0

    @extend_schema_field(serializers.BooleanField)
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, card=obj).exists()
        return False
    
    @extend_schema_field(serializers.ListField(child=serializers.IntegerField()))
    def get_list_curations(self, obj):
        """Получить рекомендуемые карточки из list_curations"""
        import json
        try:
            curations_ids = json.loads(obj.list_curations)
            return curations_ids if curations_ids else []
        except (json.JSONDecodeError, ValueError, TypeError):
            return []


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


# ==================== СКИДКИ ====================
class DiscountRequestSerializer(serializers.ModelSerializer):
    discount_percent = serializers.ReadOnlyField()
    card_title = serializers.CharField(source='card.title', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    
    class Meta:
        model = DiscountRequest
        fields = [
            'id', 'card', 'card_title', 'user', 'user_phone',
            'original_price', 'requested_price', 'discount_percent',
            'status', 'message', 'admin_comment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'original_price', 'discount_percent', 'created_at', 'updated_at', 'admin_comment']


# ==================== РЕКОМЕНДАЦИИ ====================
class RecommendationSerializer(serializers.ModelSerializer):
    card = CardSerializer(read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ['id', 'card', 'score', 'reason', 'created_at']
        read_only_fields = ['id', 'card', 'score', 'reason', 'created_at']


# ==================== AI АССИСТЕНТ ====================
class ChatMessageSerializer(serializers.ModelSerializer):
    referenced_cards = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'message', 'response', 'referenced_cards',
            'tokens_used', 'is_helpful', 'created_at'
        ]
        read_only_fields = ['response', 'referenced_cards', 'tokens_used', 'created_at']

    @extend_schema_field(CardSerializer(many=True))
    def get_referenced_cards(self, obj):
        # Детеминированный порядок: по рейтингу и свежести
        qs = obj.referenced_cards.all().order_by('-rating', '-created_at')
        return CardSerializer(qs, many=True, context=self.context).data


class ChatRequestSerializer(serializers.Serializer):
    """Serializer для отправки сообщения AI"""
    message = serializers.CharField(max_length=2000, required=True)
    user_preferences = serializers.JSONField(
        required=False,
        help_text="Предпочтения пользователя: {city: int, price_min: int, price_max: int, rooms: int и т.д.}"
    )
    mode = serializers.ChoiceField(
        choices=['search', 'free'],
        default='search',
        required=False,
        help_text="'search' - поиск квартир в БД, 'free' - обычный чат без поиска"
    )


# 🔑 НОВЫЙ: Сериализатор для истории просмотров
class ViewHistorySerializer(serializers.ModelSerializer):
    card_title = serializers.CharField(source='card.title', read_only=True)
    card = CardSerializer(read_only=True)
    
    class Meta:
        model = ViewHistory
        fields = ['id', 'card', 'card_title', 'viewed_at', 'duration_seconds']
        read_only_fields = ['id', 'card', 'card_title', 'viewed_at', 'duration_seconds']


# 🔑 НОВЫЙ: Сериализатор для отзывов
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    
    class Meta:
        model = CardReview
        fields = ['id', 'user', 'rating', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class ReviewCreateUpdateSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = CardReview
        fields = ['rating', 'text']