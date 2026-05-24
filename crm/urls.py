from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeadViewSet, ManagerViewSet

router = DefaultRouter()
router.register('managers', ManagerViewSet, basename='crm-manager')
router.register('', LeadViewSet, basename='crm-lead')

urlpatterns = [
    path('', include(router.urls)),
]
