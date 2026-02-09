from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from .models import Notification, NotificationSettings

User = get_user_model()


class MassNotificationForm(forms.ModelForm):
    """Форма для массовой рассылки уведомлений"""
    send_to_all = forms.BooleanField(
        required=False,
        initial=False,
        label="Отправить всем пользователям",
        help_text="Если отмечено, уведомление будет отправлено всем активным пользователям"
    )
    
    class Meta:
        model = Notification
        fields = ['title', 'message', 'type', 'card']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем user необязательным для массовой рассылки
        if 'user' in self.fields:
            self.fields['user'].required = False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__phone_number']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'message', 'type')
        }),
        ('Получатель', {
            'fields': ('user',),
            'description': 'Оставьте пустым и используйте действие "Массовая рассылка" для отправки всем'
        }),
        ('Связи', {
            'fields': ('card', 'old_price'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_read', 'created_at'),
        }),
    )
    
    actions = ['send_mass_notification', 'mark_as_read', 'mark_as_unread']
    
    @admin.action(description="Отправить массовое уведомление всем пользователям")
    def send_mass_notification(self, request, queryset):
        """Создать копию выбранного уведомления для всех активных пользователей"""
        if queryset.count() != 1:
            self.message_user(request, "Выберите только одно уведомление для массовой рассылки", level='error')
            return
        
        template = queryset.first()
        users = User.objects.filter(is_active=True).exclude(
            notification_settings__promotions=False
        )
        
        notifications = []
        for user in users:
            if user != template.user:  # Не дублировать автору
                notifications.append(
                    Notification(
                        user=user,
                        title=template.title,
                        message=template.message,
                        type=template.type,
                        card=template.card,
                        old_price=template.old_price,
                    )
                )
        
        if notifications:
            Notification.objects.bulk_create(notifications)
            self.message_user(request, f"Отправлено {len(notifications)} уведомлений")
        else:
            self.message_user(request, "Нет пользователей для отправки", level='warning')
    
    @admin.action(description="Отметить как прочитанные")
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"Отмечено как прочитанные: {queryset.count()}")
    
    @admin.action(description="Отметить как непрочитанные")
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"Отмечено как непрочитанные: {queryset.count()}")


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'push_enabled', 'email_enabled', 'new_cards', 'price_changes', 'promotions']
    list_filter = ['push_enabled', 'email_enabled', 'promotions']
    search_fields = ['user__phone_number', 'user__name']
    list_editable = ['push_enabled', 'email_enabled', 'new_cards', 'price_changes', 'promotions']

