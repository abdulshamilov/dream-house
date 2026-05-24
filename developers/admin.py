from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import Developer, Subscription


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', 'phone', 'cards_count', 'subscribers_count')
    list_display_links = ('logo_preview', 'name')
    list_editable = ('phone',)
    search_fields = ('name', 'phone')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _cards_count=Count('cards', distinct=True),
            _subscribers_count=Count('subscriptions', distinct=True),
        )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:40px; width:40px; object-fit:cover; border-radius:50%;">',
                obj.logo.url
            )
        return format_html('<span style="color:#ccc;">—</span>')
    logo_preview.short_description = 'Лого'

    def cards_count(self, obj):
        return obj._cards_count
    cards_count.short_description = 'Карточек'
    cards_count.admin_order_field = '_cards_count'

    def subscribers_count(self, obj):
        return obj._subscribers_count
    subscribers_count.short_description = 'Подписчиков'
    subscribers_count.admin_order_field = '_subscribers_count'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'developer', 'created_at')
    list_filter = ('developer', 'created_at')
    search_fields = ('user__phone_number', 'developer__name')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'developer')
