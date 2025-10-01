from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    # схема OpenAPI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),

    # Swagger UI по нужному адресу
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # юзеры
    path("api/users/", include("users.urls")),
]
