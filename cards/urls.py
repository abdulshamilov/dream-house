from django.urls import path
from .views import CardListView, CardDetailView, RateCardView, CallRequestCreateView  # ✅ исправлено

urlpatterns = [
    path('', CardListView.as_view(), name='cards_list'),
    path('<int:pk>/', CardDetailView.as_view(), name='card_detail'),
    path('<int:pk>/rate/', RateCardView.as_view(), name='card_rate'),
    path('<int:pk>/call_request/', CallRequestCreateView.as_view(), name='call_request'),

]
