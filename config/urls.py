from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from django.conf import settings
from django.conf.urls.static import static




# --- Расширенные схемы для токенов ---
@extend_schema(
    tags=["Auth"],
    summary="Получение JWT-токенов (логин)",
    description=(
        "Авторизация пользователя по email или номеру телефона и паролю.\n\n"
        "При успешной авторизации возвращает пару токенов:\n"
        "- **access** — используется для доступа к защищённым эндпоинтам (жизнь ~5–15 мин)\n"
        "- **refresh** — используется для обновления access-токена, когда он истечёт.\n\n"
        "Поля запроса:\n"
        "- `email` или `phone_number`\n"
        "- `password`\n\n"
        "**Важно:** отправляй `Authorization: Bearer <access>` в заголовке запроса для защищённых методов."
    ),
    request=TokenObtainPairSerializer,
    responses={
        200: {
            "application/json": {
                "example": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                }
            }
        },
        401: {
            "application/json": {
                "example": {
                    "detail": "No active account found with the given credentials"
                }
            }
        },
    },
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """Получение пары токенов"""


@extend_schema(
    tags=["Auth"],
    summary="Обновление JWT-токена",
    description=(
        "Позволяет обновить **access-токен**, когда он истёк.\n\n"
        "Поля запроса:\n"
        "- `refresh` — старый refresh-токен\n\n"
        "Возвращает новый `access` токен."
    ),
    request=TokenRefreshSerializer,
    responses={
        200: {
            "application/json": {
                "example": {
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                }
            }
        },
        401: {
            "application/json": {
                "example": {
                    "detail": "Token is invalid or expired"
                }
            }
        },
    },
)
class CustomTokenRefreshView(TokenRefreshView):
    """Обновление токена"""


urlpatterns = [
    path("admin/", admin.site.urls),

    # --- Схема и Swagger ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # --- Users ---
    path("api/users/", include("users.urls")),

    # --- JWT токены ---
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),

    # --- Cards ---
    path("api/cards/", include("cards.urls")),

    path("api/documents/", include("documents.urls")),
    path("api/developers/", include("developers.urls")),

    
]

# --- Медиафайлы ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
