from django.urls import path
from .views import CardListView, CardDetailView, RateCardView

urlpatterns = [
    path('', CardListView.as_view(), name='cards_list'),
    path('<int:pk>/', CardDetailView.as_view(), name='card_detail'),
    path('<int:pk>/rate/', RateCardView.as_view(), name='card_rate'),  # 🔹 Добавлено
]
