"""
AI Views: скидки, рекомендации, AI чат
"""

from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DiscountRequest, Recommendation, ChatMessage
from .serializers import DiscountRequestSerializer, RecommendationSerializer, ChatMessageSerializer, ChatRequestSerializer


# СКИДКИ
@extend_schema(
    summary="Создать запрос на скидку"
)
class DiscountRequestCreateView(generics.CreateAPIView):
    serializer_class = DiscountRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        from .models import Card
        try:
            card = Card.objects.get(pk=self.kwargs.get('pk'))
            serializer.save(user=self.request.user, original_price=card.price)
        except Card.DoesNotExist:
            raise serializers.ValidationError({"card": "Card not found"})


@extend_schema(
    summary="Список запросов на скидки пользователя"
)
class UserDiscountRequestsView(generics.ListAPIView):
    serializer_class = DiscountRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DiscountRequest.objects.filter(user=self.request.user)


# РЕКОМЕНДАЦИИ
class RecommendationAlgorithm:
    """Алгоритм рекомендаций на основе предпочтений пользователя"""

    def __init__(self, user):
        self.user = user

    def generate_recommendations(self, limit: int = 10):
        from .models import Card, Favorite, CardQuestion
        
        # Получить исключаемые карточки
        excluded_ids = set(Favorite.objects.filter(user=self.user).values_list('card', flat=True))
        excluded_ids.update(CardQuestion.objects.filter(user=self.user).values_list('card', flat=True))
        
        # Получить предпочтения
        preferred_cities = Card.objects.filter(id__in=excluded_ids).values_list('city', flat=True).distinct()
        preferred_types = Card.objects.filter(id__in=excluded_ids).values_list('house_type', flat=True).distinct()
        
        # Построить запрос с предпочтениями
        queryset = Card.objects.exclude(id__in=excluded_ids)
        
        if preferred_cities:
            queryset = queryset.filter(city__in=preferred_cities)
        if preferred_types:
            queryset = queryset.filter(house_type__in=preferred_types)
        
        return queryset.order_by('-rating', '-created_at')[:limit]

    def save_recommendations(self, recommendations):
        """Сохранить рекомендации с оценкой"""
        for i, card in enumerate(recommendations, 1):
            score = max(0.5, 1.0 - (i * 0.05))  # Минимум 0.5
            reason = f"Похожа на ваши избранные (рейтинг: {card.rating})"
            
            Recommendation.objects.get_or_create(
                user=self.user,
                card=card,
                defaults={'score': score, 'reason': reason}
            )


@extend_schema(
    summary="Получить рекомендации для пользователя"
)
class GetRecommendationsView(generics.ListAPIView):
    serializer_class = RecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        recommendations = Recommendation.objects.filter(user=self.request.user)
        
        if not recommendations.exists():
            algorithm = RecommendationAlgorithm(self.request.user)
            cards = algorithm.generate_recommendations()
            algorithm.save_recommendations(cards)
            recommendations = Recommendation.objects.filter(user=self.request.user)
        
        return recommendations.order_by('-score')


# AI АССИСТЕНТ
@extend_schema(
    summary="Chat с AI ассистентом"
)
class AIChatView(generics.GenericAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from .ai_service import AIAssistantService
        ai_service = AIAssistantService()
        
        mode = serializer.validated_data.get('mode', 'search')
        
        result = ai_service.chat(
            user_message=serializer.validated_data['message'],
            user_preferences=serializer.validated_data.get('user_preferences', {}),
            user_id=request.user.id,
            mode=mode
        )
        
        if result.get('success'):
            # Получить последнее сохраненное сообщение
            chat = ChatMessage.objects.filter(user=request.user).order_by('-created_at').first()
            if chat:
                response_data = ChatMessageSerializer(chat).data
                
                # Добавить информацию о карточках в ответ
                referenced_card_ids = result.get('referenced_cards', [])
                if referenced_card_ids:
                    from .models import Card
                    cards = Card.objects.filter(id__in=referenced_card_ids)
                    from .serializers import CardSerializer
                    response_data['referenced_cards'] = CardSerializer(cards, many=True).data
                else:
                    response_data['referenced_cards'] = []
                
                response_data['ai_response'] = result.get('response')
                response_data['mode'] = result.get('mode', 'search')
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response({'error': 'Chat not saved'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(
            {'error': result.get('error', 'Unknown error'), 'message': result.get('response')},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@extend_schema(
    summary="История чатов пользователя"
)
class ChatHistoryView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user).order_by('-created_at')


@extend_schema(
    summary="Оценить полезность ответа AI"
)
class RateAIResponseView(generics.UpdateAPIView):
    queryset = ChatMessage.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatMessageSerializer

    def get_object(self):
        """Получить чат и проверить права доступа"""
        chat = super().get_object()
        if chat.user != self.request.user:
            self.permission_denied(self.request)
        return chat

    def patch(self, request, pk, *args, **kwargs):
        chat = self.get_object()
        is_helpful = request.data.get('is_helpful')
        
        if is_helpful is not None and isinstance(is_helpful, bool):
            chat.is_helpful = is_helpful
            chat.save()
        
        return Response(ChatMessageSerializer(chat).data, status=status.HTTP_200_OK)
