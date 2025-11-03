from django.urls import path
from .views import (
    DeveloperListAPIView,
    DeveloperCardsAPIView,
    SubscribeAPIView,
    MySubscriptionsAPIView,
)

urlpatterns = [
    path('', DeveloperListAPIView.as_view(), name='developer_list'),
    path('<int:developer_id>/cards/', DeveloperCardsAPIView.as_view(), name='developer_cards'),
    path('<int:developer_id>/subscribe/', SubscribeAPIView.as_view(), name='subscribe'),
    path('<int:developer_id>/unsubscribe/', SubscribeAPIView.as_view(), name='unsubscribe'),
    path('me/subscriptions/', MySubscriptionsAPIView.as_view(), name='my_subscriptions'),
]
