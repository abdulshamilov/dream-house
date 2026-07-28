from rest_framework import generics, permissions

from .models import CardStream
from .serializers import CardStreamSerializer


class StreamListView(generics.ListAPIView):
    """Список активных эфиров с камер — для страницы «Стройка онлайн»."""
    serializer_class = CardStreamSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = CardStream.objects.filter(is_active=True).select_related('card')
        card_id = self.request.query_params.get('card')
        if card_id:
            qs = qs.filter(card_id=card_id)
        return qs
