# users/urls.py
from django.urls import path
from .views import (
    RegisterEmailView, RegisterPhoneView,
    LoginEmailView, LoginPhoneView,
    ResetPasswordEmailView, ResetPasswordPhoneView
)

urlpatterns = [
    path("register/email/", RegisterEmailView.as_view()),
    path("register/phone/", RegisterPhoneView.as_view()),
    path("login/email/", LoginEmailView.as_view()),
    path("login/phone/", LoginPhoneView.as_view()),
    path("reset/email/", ResetPasswordEmailView.as_view()),
    path("reset/phone/", ResetPasswordPhoneView.as_view()),
]
