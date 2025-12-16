from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import generics, permissions, status, serializers, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Card, CardReview, CardQuestion, CardVideo, SearchHistory, Favorite, Review
from .serializers import (
    CardSerializer,
    CardReviewSerializer,
    CardQuestionSerializer,
    CardVideoSerializer,
    CallRequestSerializer,
    FavoriteSerializer,
)
from .filters import CardFilter
from .permissions import IsAdminOrReadOnly

# -------------------------------
# Сериализаторы рейтинга
# -------------------------------
class RateCardSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)

class RateCardResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    new_average = serializers.FloatField()
    total_votes = serializers.IntegerField()

# -------------------------------
# 1. Список карточек
# -------------------------------
@extend_schema(
    summary="Получить список карточек",
    description="Возвращает список всех карточек недвижимости с поддержкой фильтров.",
    responses=CardSerializer(many=True)
)
class CardListView(generics.ListAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CardFilter

    def get_serializer_context(self):
        return {'request': self.request}

# -------------------------------
# 2. ФИЛЬТРАЦИЯ КАРТОЧЕК (POST)
# -------------------------------
@extend_schema(
    summary="Получить список карточек с фильтрами (POST JSON)",
    description="Принимает параметры фильтрации в теле JSON. Возвращает список карточек.",
    responses=CardSerializer(many=True)
)
class CardFilterPostView(generics.GenericAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filter_data = request.data
        filtered_queryset = CardFilter(data=filter_data, queryset=queryset).qs
        serializer = self.get_serializer(filtered_queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

# -------------------------------
# 3. Детальная карточка
# -------------------------------
@extend_schema(
    summary="Получить подробную информацию о карточке",
    responses=CardSerializer
)
class CardDetailView(generics.RetrieveAPIView):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        return {'request': self.request}
    
    def retrieve(self, request, *args, **kwargs):
        """Переопределить retrieve для автоматического сохранения просмотра"""
        response = super().retrieve(request, *args, **kwargs)
        
        # 🔑 НОВОЕ: Автоматически сохранить просмотр если пользователь аутентифицирован
        if request.user.is_authenticated:
            from .models import ViewHistory
            card = self.get_object()
            ViewHistory.objects.create(
                user=request.user,
                card=card,
                duration_seconds=0  # Будет обновлено на фронте
            )
        
        return response

# -------------------------------
# 4. Избранное
# -------------------------------
@extend_schema(
    summary="Добавить/удалить карточку из избранного",
    description="POST: добавить карточку в избранное. DELETE: удалить из избранного. Только для авторизованных пользователей."
)
class FavoriteAPIView(generics.GenericAPIView):
    """Управление избранными карточками пользователя"""
    queryset = Card.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        card = get_object_or_404(Card, pk=pk)
        if Favorite.objects.filter(user=request.user, card=card).exists():
            return Response({'message': 'Карточка уже в избранном'}, status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.create(user=request.user, card=card)
        return Response({'message': 'Карточка добавлена в избранное'}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        card = get_object_or_404(Card, pk=pk)
        deleted_count, _ = Favorite.objects.filter(user=request.user, card=card).delete()
        if deleted_count == 0:
            return Response({'message': 'Карточка не была в избранном'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

@extend_schema(
    summary="Список избранных карточек пользователя",
    description="Получить все карточки, добавленные в избранное текущим пользователем"
)
class MyFavoritesListAPIView(generics.ListAPIView):
    """Список избранных карточек текущего пользователя"""
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('card')

    def get_serializer_context(self):
        return {'request': self.request}

# -------------------------------
# 5. Оценка карточки
# -------------------------------
@extend_schema(
    summary="Поставить оценку карточке (1-5 звёзд)",
    description="Увеличить рейтинг карточки. Вычисляет среднюю оценку из всех голосов.",
    request=RateCardSerializer,
    responses={200: RateCardResponseSerializer}
)
class RateCardView(generics.GenericAPIView):
    """Добавление оценки карточке и обновление рейтинга"""
    queryset = Card.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        card = get_object_or_404(Card, pk=pk)
        serializer = RateCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rating = serializer.validated_data['rating']
        total_rating = card.rating * card.rating_count
        card.rating_count += 1
        card.rating = (total_rating + rating) / card.rating_count
        card.save()
        return Response({
            "message": "Оценка добавлена",
            "new_average": round(card.rating, 2),
            "total_votes": card.rating_count
        })

# -------------------------------
# 6. Заявка на звонок
# -------------------------------
@extend_schema(
    summary="Оставить заявку на звонок",
    description="Создать заявку на звонок от потенциального покупателя. Уведомляет владельца карточки.",
    request=CallRequestSerializer,
    responses={201: OpenApiResponse(description="Создано")}
)
class CallRequestCreateView(generics.CreateAPIView):
    """Создание заявки на звонок для контактирования с владельцем"""
    serializer_class = CallRequestSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        card_id = kwargs.get('pk')
        card = get_object_or_404(Card, pk=card_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(card=card)
        return Response({"ok": True, "code": "OK"}, status=201)

# -------------------------------
# 7. Видео, отзыв, вопрос
# -------------------------------
@extend_schema(
    summary="Загрузить видео на карточку",
    description="Добавить видео-обзор к карточке. Требует авторизацию.",
    request=CardVideoSerializer
)
class CardVideoCreateView(generics.CreateAPIView):
    """Добавление видео-обзора к карточке"""
    serializer_class = CardVideoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        card = Card.objects.get(pk=self.kwargs.get('pk'))
        serializer.save(card=card)

@extend_schema(
    summary="Оставить отзыв на карточку",
    description="Добавить текстовый отзыв с оценкой. Требует авторизацию.",
    request=CardReviewSerializer
)
class CardReviewCreateView(generics.CreateAPIView):
    """Добавление текстового отзыва о квартире"""
    serializer_class = CardReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        card = Card.objects.get(pk=self.kwargs.get('pk'))
        serializer.save(card=card, user=self.request.user)

# -------------------------------
@extend_schema(
    summary="Список вопросов по карточке",
    description="Возвращает все вопросы к квартире (можно фильтровать по card_id через query параметр)",
    responses=CardQuestionSerializer(many=True)
)
class CardQuestionListView(generics.ListAPIView):
    """Список вопросов о квартире"""
    serializer_class = CardQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        card_id = self.request.query_params.get('card_id')
        if card_id:
            return CardQuestion.objects.filter(card_id=card_id)
        return CardQuestion.objects.all()

# Создание вопроса к конкретной карточке
@extend_schema(
    summary="Создать вопрос к карточке",
    description="Задать вопрос о карточке. Ответ может оставить только владелец или администратор.",
    request=CardQuestionSerializer,
    responses={201: CardQuestionSerializer}
)
class CardQuestionCreateView(generics.CreateAPIView):
    """Создание вопроса о квартире"""
    serializer_class = CardQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk, *args, **kwargs):
        card = get_object_or_404(Card, pk=pk)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(card=card, user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Ответ на вопрос (только админ/девелопер)
@extend_schema(
    summary="Ответить на вопрос о квартире",
    description="Ответить на вопрос. Доступно только владельцу карточки или администратору.",
    request=CardQuestionSerializer,
    responses={200: CardQuestionSerializer}
)
class CardQuestionAnswerView(generics.UpdateAPIView):
    """Добавление ответа на вопрос о квартире"""
    queryset = CardQuestion.objects.all()
    serializer_class = CardQuestionSerializer
    permission_classes = [IsAdminOrReadOnly]
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(answer=self.request.data.get('answer'))

# 9. Детали отзывов/вопросов
# -------------------------------
@extend_schema(
    summary="Получить отзыв по ID",
    responses=CardReviewSerializer
)
class CardReviewDetailView(generics.RetrieveAPIView):
    """Получение полной информации об отзыве"""
    queryset = CardReview.objects.all()
    serializer_class = CardReviewSerializer
    lookup_field = "id"

@extend_schema(
    summary="Получить вопрос по ID",
    responses=CardQuestionSerializer
)
class CardQuestionDetailView(generics.RetrieveAPIView):
    """Получение полной информации о вопросе и ответе"""
    queryset = CardQuestion.objects.all()
    serializer_class = CardQuestionSerializer
    lookup_field = "id"

# 10. Поиск карточек
# -------------------------------
@extend_schema(
    summary="Поиск карточек по тексту (умный поиск)",
    description="Поиск по названию, описанию и адресу. Сохраняет историю поиска авторизованных пользователей. Учит система на основе истории."
)
class CardSearchView(generics.ListAPIView):
    """Поиск квартир по текстовому запросу с умной фильтрацией и исправлением ошибок"""
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]

    def _correct_query(self, query):
        """Исправить опечатки и синонимы в запросе"""
        from difflib import get_close_matches
        import re
        
        # Словарь синонимов и исправлений
        synonyms = {
            'хорошие': 'премиум рейтинг',
            'хорошая': 'премиум рейтинг',
            'хорош': 'премиум рейтинг',
            'качественн': 'премиум рейтинг',
            'новые': 'новое',
            'свежие': 'новое',
            'красивые': 'дизайн интерьер',
            'красивая': 'дизайн интерьер',
            'дешевые': 'цена бюджет',
            'дешевая': 'цена бюджет',
            'дорогие': 'премиум люкс',
            'центр': 'центральный',
            'спальни': 'комнаты',
            'апартаменты': 'квартира',
            'апарт': 'квартира',
        }
        
        corrected = query.lower()
        
        # Заменить синонимы
        for old, new in synonyms.items():
            pattern = r'\b' + old + r'\b'
            corrected = re.sub(pattern, new, corrected, flags=re.IGNORECASE)
        
        return corrected

    def _build_filters(self, query):
        """Построить фильтры на основе анализа запроса"""
        from django.db.models import Q
        
        filters = Q()
        query_lower = query.lower()
        
        # Ценовые фильтры
        if 'дешев' in query_lower or 'бюджет' in query_lower:
            filters |= Q(price__lt=3000000)  # < 3млн
        if 'премиум' in query_lower or 'люкс' in query_lower:
            filters |= Q(price__gte=5000000)  # >= 5млн
        
        # Районы/Местоположение
        if 'центр' in query_lower:
            filters |= Q(city__icontains='центр') | Q(address__icontains='центр')
        
        # Качество/Рейтинг
        if 'хорош' in query_lower or 'рейтинг' in query_lower:
            filters |= Q(rating__gte=4.0)  # Рейтинг 4 звезды и выше
        
        # Новые предложения
        if 'новое' in query_lower:
            filters |= Q(created_at__year=2025)
        
        return filters

    def get_queryset(self):
        from django.db.models import Q
        from django.utils import timezone
        from datetime import timedelta
        import re
        
        query = self.request.query_params.get("q", "").strip()
        
        if not query:
            return Card.objects.none()
        
        # Исправить ошибки и синонимы
        corrected_query = self._correct_query(query)
        
        # Сохранить оригинальный поиск если пользователь авторизован
        if self.request.user.is_authenticated:
            SearchHistory.objects.create(user=self.request.user, query=query)
        
        # Основной поиск с исправленным запросом
        queryset = Card.objects.filter(
            Q(title__icontains=corrected_query) |
            Q(description__icontains=corrected_query) |
            Q(address__icontains=corrected_query)
        )
        
        # Применить умные фильтры на основе содержания запроса
        smart_filters = self._build_filters(corrected_query)
        if smart_filters:
            queryset = queryset.filter(smart_filters)
        
        # Умная сортировка на основе истории поиска пользователя
        if self.request.user.is_authenticated:
            # Получить популярные фильтры из истории этого пользователя за последние 7 дней
            recent_searches = SearchHistory.objects.filter(
                user=self.request.user,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).values_list('query', flat=True)
            
            # Если в поиске есть числа (цена, комнаты), отдать приоритет релевантным результатам
            numbers = re.findall(r'\d+', corrected_query)
            if numbers:
                # Поднять карточки где есть эти числа в цене или комнатах
                number_matches = queryset.filter(
                    Q(price__icontains=numbers[0]) |
                    (Q(rooms=int(numbers[0])) if numbers[0].isdigit() else Q())
                )
                if number_matches.exists():
                    queryset = number_matches | queryset.exclude(id__in=number_matches.values_list('id', flat=True))
        
        # Ограничить результаты (макс 20 для избежания перегруза)
        return queryset.order_by('-rating', '-created_at')[:20]

    def get_serializer_context(self):
        return {'request': self.request}


# 🔑 НОВЫЕ: Views для истории просмотров и подборок документов

@extend_schema(
    summary="Сохранить просмотр карточки",
    description="Записать время просмотра карточки пользователем для аналитики и рекомендаций"
)
class CardViewHistoryView(generics.CreateAPIView):
    """Сохранение истории просмотров квартир пользователем"""
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        from .models import ViewHistory
        
        card_id = self.kwargs.get('card_pk')
        duration = request.data.get('duration_seconds', 0)
        
        try:
            card = Card.objects.get(id=card_id)
            view = ViewHistory.objects.create(
                user=request.user,
                card=card,
                duration_seconds=int(duration) if duration else 0
            )
            return Response(
                {'message': 'View saved', 'id': view.id},
                status=status.HTTP_201_CREATED
            )
        except Card.DoesNotExist:
            return Response(
                {'error': 'Card not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    summary="История просмотров текущего пользователя",
    description="Получить список всех просмотренных карточек с временем просмотра"
)
class UserViewHistoryListView(generics.ListAPIView):
    """История просмотренных квартир пользователя"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from .models import ViewHistory
        return ViewHistory.objects.filter(user=self.request.user).order_by('-viewed_at')
    
    def get_serializer_class(self):
        from .serializers import ViewHistorySerializer
        return ViewHistorySerializer


@extend_schema(
    summary="История поиска пользователя",
    description="Получить историю всех поисков текущего пользователя с аналитикой популярных запросов"
)
class SearchHistoryView(generics.ListAPIView):
    """История поиска пользователя с аналитикой"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Получить последние 30 дней поиска
        return SearchHistory.objects.filter(
            user=self.request.user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """Добавить аналитику в ответ"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Добавить аналитику популярных запросов
        popular_queries = SearchHistory.objects.filter(
            user=request.user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('query').annotate(count=Count('id')).order_by('-count')[:5]
        
        return Response({
            'total_searches': queryset.count(),
            'popular_queries': [
                {'query': item['query'], 'count': item['count']} 
                for item in popular_queries
            ],
            'recent_searches': serializer.data
        })
    
    def get_serializer_class(self):
        from rest_framework import serializers
        
        class SearchHistorySerializer(serializers.ModelSerializer):
            class Meta:
                model = SearchHistory
                fields = ['query', 'created_at']
        
        return SearchHistorySerializer


@extend_schema(
    summary="Подборки документов для карточки",
    description="Получить списки (подборки) документов, загруженные для этой квартиры"
)
class CardDocumentListsView(generics.ListAPIView):
    """Список подборок документов для квартиры"""
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        from .models import CardDocumentList
        card_id = self.kwargs.get('card_pk')
        return CardDocumentList.objects.filter(card_id=card_id)
    
    def get_serializer_class(self):
        from .serializers import CardDocumentListSerializer
        return CardDocumentListSerializer


@extend_schema(
    summary="Создать подборку документов",
    description="Создать новый список (подборку) документов для карточки. Доступно только администратору."
)
class CardDocumentListCreateView(generics.CreateAPIView):
    """Создание подборки документов к квартире"""
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        from .serializers import CardDocumentListSerializer
        return CardDocumentListSerializer
    
    def perform_create(self, serializer):
        from .models import CardDocumentList
        card_id = self.kwargs.get('card_pk')
        card = get_object_or_404(Card, id=card_id)
        serializer.save(card=card)


# 🔑 НОВОЕ: Отзывы на карточки
@extend_schema(
    summary="Список отзывов на карточку и создание отзыва",
    description="GET: получить все отзывы на квартиру от других пользователей. POST: оставить новый отзыв с оценкой 1-5 и текстом (автоматически обновляет рейтинг)"
)
class ReviewListCreateView(generics.ListCreateAPIView):
    """Список отзывов и создание нового отзыва. Автоматически обновляет рейтинг карточки."""
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        card_id = self.kwargs.get('card_pk')
        return Review.objects.filter(card_id=card_id)
    
    def get_serializer_class(self):
        from .serializers import ReviewSerializer, ReviewCreateUpdateSerializer
        if self.request.method == 'POST':
            return ReviewCreateUpdateSerializer
        return ReviewSerializer
    
    def perform_create(self, serializer):
        from .models import Review
        card_id = self.kwargs.get('card_pk')
        card = get_object_or_404(Card, id=card_id)
        review = serializer.save(user=self.request.user, card=card)
        # Обновляем рейтинг карточки
        card.update_rating()


@extend_schema(
    summary="Получить/Обновить/Удалить отзыв",
    description="GET: получить полный отзыв. PUT/PATCH: обновить отзыв (только автор). DELETE: удалить отзыв (только автор). Автоматически обновляет рейтинг."
)
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Получить, обновить или удалить отзыв. Только автор может редактировать/удалять."""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.all()
    
    def get_serializer_class(self):
        from .serializers import ReviewSerializer, ReviewCreateUpdateSerializer
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return ReviewCreateUpdateSerializer
        return ReviewSerializer
    
    def check_object_permissions(self, request, obj):
        # Только автор может редактировать/удалять
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            if obj.user != request.user:
                self.permission_denied(request, message="You can only edit your own reviews")
        super().check_object_permissions(request, obj)
    
    def perform_update(self, serializer):
        review = serializer.save()
        # Обновляем рейтинг карточки
        review.card.update_rating()
    
    def perform_destroy(self, instance):
        card = instance.card
        instance.delete()
        # Обновляем рейтинг карточки
        card.update_rating()


# 🔑 НОВОЕ: Подборка для карточки
@extend_schema(
    summary="Получить подборку похожих карточек с полной информацией",
    description="Возвращает JSON-список похожих квартир с информацией: id, address, price, rooms, city, rating. Автоматически генерирует если не существует."
)
class CardCurationsView(generics.RetrieveAPIView):
    """Подборка похожих квартир (curations) - список с полной информацией"""
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    permission_classes = [permissions.AllowAny]
    
    def retrieve(self, request, *args, **kwargs):
        """Переопределить для возврата кураций"""
        card = self.get_object()
        
        # Генерируем кураци если нужны
        if not card.list_curations or card.list_curations == '[]':
            card.generate_curations(user=request.user if request.user.is_authenticated else None)
        
        # Возвращаем курации
        import json
        try:
            curations_data = json.loads(card.list_curations)
        except:
            curations_data = []
        
        return Response({
            'card_id': card.id,
            'curations': curations_data
        }, status=status.HTTP_200_OK)
