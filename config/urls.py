from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.urls import path, include

admin.site.site_header = "Dream House — Управление"
admin.site.site_title = "Dream House Admin"
admin.site.index_title = "Панель управления"
from django.views.decorators.http import require_GET
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from users.serializers import CustomTokenObtainPairSerializer
from django.conf import settings
from django.conf.urls.static import static


# ------------------------------------------------------------------ #
#  Deep-link verification files  (.well-known)  — данные из БД (админка)
# ------------------------------------------------------------------ #

def _get_deeplink_config():
    from cards.models_deeplink import DeepLinkConfig
    return DeepLinkConfig.load()


@require_GET
def apple_app_site_association(request):
    """iOS Universal Links — /.well-known/apple-app-site-association"""
    cfg = _get_deeplink_config()
    return JsonResponse(cfg.get_apple_app_site_association(), json_dumps_params={"indent": 2})


@require_GET
def asset_links(request):
    """Android App Links — /.well-known/assetlinks.json"""
    cfg = _get_deeplink_config()
    return JsonResponse(cfg.get_asset_links(), safe=False, json_dumps_params={"indent": 2})


# ------------------------------------------------------------------ #
#  Referral fallback (app not installed → store links page)
# ------------------------------------------------------------------ #

@require_GET
def referral_fallback(request, code):
    """
    Если приложение не установлено, ссылка dreamhouse05.com/ref/<code>
    открывается в браузере — показываем страницу с кнопками на сторы.
    """
    cfg = _get_deeplink_config()
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Dream House</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex; flex-direction: column; align-items: center;
            justify-content: center; min-height: 100vh; margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff; text-align: center; padding: 20px;
        }}
        h1 {{ margin-bottom: 8px; }}
        p  {{ margin-bottom: 32px; opacity: .85; }}
        .btn {{
            display: inline-block; padding: 14px 32px; margin: 8px;
            border-radius: 12px; text-decoration: none; font-weight: 600;
            font-size: 16px; color: #fff; transition: transform .15s;
        }}
        .btn:hover {{ transform: scale(1.05); }}
        .ios     {{ background: #000; }}
        .android {{ background: #34a853; }}
    </style>
</head>
<body>
    <h1>Dream House</h1>
    <p>Установите приложение, чтобы воспользоваться реферальной ссылкой <b>{code}</b></p>
    <a class="btn ios" href="{cfg.appstore_url}">App Store</a>
    <a class="btn android" href="{cfg.playstore_url}">Google Play</a>
</body>
</html>"""
    return HttpResponse(html, content_type="text/html; charset=utf-8")




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
        "- `phone_number` или `email`\n"
        "- `password`\n\n"
        "**Важно:** отправляй `Authorization: Bearer <access>` в заголовке запроса для защищённых методов."
    ),
    request=CustomTokenObtainPairSerializer,
    responses={
        200: OpenApiResponse(
            response=inline_serializer(
                name="TokenPairResponse",
                fields={
                    "access": serializers.CharField(),
                    "refresh": serializers.CharField(),
                },
            ),
            description="JWT token pair",
        ),
        401: OpenApiResponse(
            response=inline_serializer(
                name="TokenPairError",
                fields={"detail": serializers.CharField()},
            ),
            description="No active account found with the given credentials",
        ),
    },
)
class CustomTokenObtainPairView(TokenObtainPairView):
    """Получение пары токенов"""
    serializer_class = CustomTokenObtainPairSerializer


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
        200: OpenApiResponse(
            response=inline_serializer(
                name="TokenRefreshResponse",
                fields={"access": serializers.CharField()},
            ),
            description="New access token",
        ),
        401: OpenApiResponse(
            response=inline_serializer(
                name="TokenRefreshError",
                fields={"detail": serializers.CharField()},
            ),
            description="Token is invalid or expired",
        ),
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


    path("api/developers/", include("developers.urls")),

    
    path('api/notifications/', include('notifications.urls')),

    # --- CRM (Leads & Managers) ---
    path('api/leads/', include('crm.urls')),

    # --- Deep-link verification ---
    path('.well-known/apple-app-site-association', apple_app_site_association),
    path('.well-known/assetlinks.json', asset_links),

    # --- Referral fallback ---
    path('ref/<str:code>', referral_fallback, name='referral_fallback'),
]

# --- Медиафайлы ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
