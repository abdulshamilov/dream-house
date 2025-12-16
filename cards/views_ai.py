"""
AI Views: скидки, рекомендации, AI чат
"""

from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import DiscountRequest, Recommendation, ChatMessage, Card
from .serializers import DiscountRequestSerializer, RecommendationSerializer, ChatMessageSerializer, ChatRequestSerializer, CardSerializer


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


@extend_schema(
    summary="Получить рекомендации для текущего пользователя"
)
class GetRecommendationsView(generics.ListAPIView):
    serializer_class = CardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from .models import Favorite, ViewHistory
        
        user = self.request.user
        
        # Получаем карточки которые пользователь просматривал
        viewed_card_ids = ViewHistory.objects.filter(user=user).values_list('card_id', flat=True)
        
        if not viewed_card_ids:
            # Если ничего не просматривал, показываем ТОП рейтинговых
            return Card.objects.all().order_by('-rating', '-created_at')[:10]
        
        # Получаем параметры из последнего просмотра
        from django.db.models import Q
        last_viewed = ViewHistory.objects.filter(user=user).latest('viewed_at')
        card = last_viewed.card
        
        # Ищем похожие карточки
        similar_cards = Card.objects.exclude(id__in=viewed_card_ids)
        similar_cards = similar_cards.filter(
            Q(city=card.city) | 
            Q(price__gte=card.price * 0.7, price__lte=card.price * 1.3)
        ).order_by('-rating', '-created_at')[:10]
        
        return similar_cards


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
        # Возвращаем последние 10 сообщений
        return ChatMessage.objects.filter(user=self.request.user).order_by('-created_at')[:10]


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
