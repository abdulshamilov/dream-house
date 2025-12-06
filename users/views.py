from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: UserSerializer},
        tags=["Auth"]
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: {"detail": "Logged in"}},
        tags=["Auth"]
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone_number"]
        password = serializer.validated_data["password"]

        user = authenticate(request, phone_number=phone, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=400)

        login(request, user)
        return Response({"detail": "Logged in"})


class LogoutView(APIView):

    @extend_schema(
        responses={200: {"detail": "Logged out"}},
        tags=["Auth"]
    )
    def post(self, request):
        logout(request)
        return Response({"detail": "Logged out"})


class MeView(APIView):

    @extend_schema(
        responses={200: UserSerializer},
        tags=["User"]
    )
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=401)

        return Response(UserSerializer(request.user).data)
