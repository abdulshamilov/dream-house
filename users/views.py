from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


# --------------------
# Register
# --------------------
@extend_schema(
    tags=["Auth"],
    summary="Регистрация пользователя",
    description=(
        "Регистрация нового пользователя через **email**. "
        "Если пользователь уже существует, возвращает ошибку.\n\n"
        "Поля для запроса:\n"
        "- `email` — адрес эл. почты\n"
        "- `name` — имя пользователя\n"
        "- `password` — пароль"
    ),
    request=RegisterSerializer,
    responses={
        201: {
            "application/json": {
                "example": {
                    "ok": True,
                    "code": "OK",
                    "reason": ""
                }
            }
        },
        400: {
            "application/json": {
                "example": {
                    "ok": False,
                    "code": "REGIST_FAILED",
                    "reason": "ALREADY_REGISTERED"
                }
            }
        }
    },
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        email = request.data.get("email")

        if email and User.objects.filter(email=email).exists():
            return Response({"ok": False, "code": "REGIST_FAILED", "reason": "ALREADY_REGISTERED"}, status=400)

        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"ok": True, "code": "OK", "reason": ""}, status=201)

        return Response({"ok": False, "code": "REGIST_FAILED", "reason": serializer.errors}, status=400)


# --------------------
# Me
# --------------------
@extend_schema(
    tags=["User"],
    summary="Информация о текущем пользователе",
    description=(
        "Возвращает профиль текущего авторизованного пользователя.\n\n"
        "Требуется **JWT-токен** в заголовке Authorization."
    ),
    responses={
        200: {
            "application/json": {
                "example": {
                    "ok": True,
                    "code": "OK",
                    "reason": "",
                    "user": {
                        "id": 1,
                        "email": "test@example.com",
                        "name": "Test"
                    }
                }
            }
        },
        401: {
            "application/json": {
                "example": {
                    "ok": False,
                    "code": "AUTH_FAILED",
                    "reason": "WRONG_PASSWORD"
                }
            }
        }
    },
)
class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response({"ok": True, "code": "OK", "reason": "", "user": serializer.data})


# --------------------
# Users List
# --------------------
@extend_schema(
    tags=["User"],
    summary="Список всех пользователей",
    description="Возвращает список всех пользователей. Требуется **JWT-токен**.",
    responses={200: UserSerializer(many=True)}
)
class UsersListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
