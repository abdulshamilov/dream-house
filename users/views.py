# users/views.py
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import (
    RegisterEmailSerializer, RegisterPhoneSerializer,
    LoginEmailSerializer, LoginPhoneSerializer
)
from .models import User

class RegisterEmailView(APIView):
    def post(self, request):
        serializer = RegisterEmailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True, "code": "OK", "reason": ""}, status=status.HTTP_201_CREATED)
        return Response({"ok": False, "code": "REGIST_FAILED", "reason": serializer.errors}, status=400)


class RegisterPhoneView(APIView):
    def post(self, request):
        serializer = RegisterPhoneSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"ok": True, "code": "OK", "reason": ""}, status=status.HTTP_201_CREATED)
        return Response({"ok": False, "code": "REGIST_FAILED", "reason": serializer.errors}, status=400)


class LoginEmailView(APIView):
    def post(self, request):
        serializer = LoginEmailSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"ok": True, "code": "OK", "reason": ""})
        return Response({"ok": False, "code": "AUTH_FAILED", "reason": serializer.errors}, status=400)


class LoginPhoneView(APIView):
    def post(self, request):
        serializer = LoginPhoneSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"ok": True, "code": "OK", "reason": ""})
        return Response({"ok": False, "code": "AUTH_FAILED", "reason": serializer.errors}, status=400)


class ResetPasswordEmailView(APIView):
    def post(self, request):
        email = request.data.get("mail")
        if not User.objects.filter(email=email).exists():
            return Response({"code": "AUTH_FAILED", "reason": "DONT_REGIST"}, status=400)
        # тут потом логика отправки письма
        return Response({"code": "OK"})


class ResetPasswordPhoneView(APIView):
    def post(self, request):
        phone = request.data.get("number_phone")
        if not User.objects.filter(phone_number=phone).exists():
            return Response({"code": "AUTH_FAILED", "reason": "DONT_REGIST"}, status=400)
        # тут потом логика отправки SMS
        return Response({"code": "OK"})
