from django.conf import settings
from rest_framework.permissions import BasePermission


class WebhookPermission(BasePermission):
    """For POST /api/leads/ — site sends X-Webhook-Token"""
    def has_permission(self, request, view):
        token = request.headers.get('X-Webhook-Token', '')
        expected = getattr(settings, 'WEBHOOK_SECRET', '')
        return bool(expected and token == expected)


class BotAPIPermission(BasePermission):
    """For all bot→API calls — bot sends X-Bot-Secret"""
    def has_permission(self, request, view):
        token = request.headers.get('X-Bot-Secret', '')
        expected = getattr(settings, 'BOT_API_SECRET', '')
        return bool(expected and token == expected)
