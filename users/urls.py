from django.urls import path
from .views import RegisterView, LoginView, LogoutView, MeView, ReferralListView, get_referral_link


urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("me/", MeView.as_view()),
    path('referrals/', ReferralListView.as_view(), name='referral-list'),
    path('referral-link/', get_referral_link, name='referral-link'),
]
