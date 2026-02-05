from django.contrib import admin
from .models import Developer, Subscription

@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'logo')
    list_editable = ('phone',)
    search_fields = ('name', 'phone')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'developer', 'created_at')
    list_filter = ('developer', 'created_at')
    search_fields = ('user__phone_number', 'developer__name')
