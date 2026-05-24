from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from .models import Notification, NotificationSettings

User = get_user_model()


class NotificationAdminForm(forms.ModelForm):
    """Форма для создания уведомлений с возможностью массовой рассылки"""
    send_to_all = forms.BooleanField(
        required=False,
        initial=False,
        label="Отправить всем пользователям",
        help_text="Если отмечено, уведомление будет отправлено всем активным пользователям (поле 'Пользователь' будет игнорироваться)"
    )
    
    class Meta:
        model = Notification
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем user необязательным для массовой рассылки
        if 'user' in self.fields:
            self.fields['user'].required = False
            self.fields['user'].help_text = "Оставьте пустым и отметьте 'Отправить всем' для массовой рассылки"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    form = NotificationAdminForm
    list_display = ['id', 'user', 'title', 'type', 'promotion', 'is_global', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'is_global', 'created_at', 'promotion']
    search_fields = ['title', 'message', 'user__phone_number']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    autocomplete_fields = ['user', 'card', 'promotion']
    
    fieldsets = (
        ('Массовая рассылка', {
            'fields': ('send_to_all',),
            'description': 'Отметьте для отправки уведомления всем активным пользователям',
            'classes': ('wide',)
        }),
        ('Основное', {
            'fields': ('title', 'message', 'type')
        }),
        ('Получатель', {
            'fields': ('user',),
            'description': 'Оставьте пустым для массовой рассылки или выберите конкретного пользователя'
        }),
        ('Связи', {
            'fields': ('card', 'promotion', 'old_price'),
        }),
        ('Статус', {
            'fields': ('is_read', 'is_global', 'created_at'),
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        """Показывать send_to_all только при создании нового уведомления"""
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # Редактирование существующего объекта
            # Убираем поле send_to_all
            return tuple(
                (name, opts) for name, opts in fieldsets 
                if name != 'Массовая рассылка'
            )
        return fieldsets
    
    def save_model(self, request, obj, form, change):
        """Обработка сохранения с возможностью массовой рассылки"""
        send_to_all = form.cleaned_data.get('send_to_all', False)
        
        if send_to_all and not change:
            # Массовая рассылка - создаем уведомления для всех пользователей
            obj.is_global = True
            obj.user = None
            super().save_model(request, obj, form, change)
            
            # Получаем всех активных пользователей
            users = User.objects.filter(is_active=True)
            
            # Исключаем пользователей, которые отключили рассылку промо (если уведомление связано с акцией)
            if obj.promotion or obj.type in ['discount', 'sale']:
                users = users.exclude(notification_settings__promotions=False)
            
            notifications = []
            for user in users:
                notifications.append(
                    Notification(
                        user=user,
                        title=obj.title,
                        message=obj.message,
                        type=obj.type,
                        card=obj.card,
                        promotion=obj.promotion,
                        old_price=obj.old_price,
                        is_global=False,  # Индивидуальные копии не глобальные
                    )
                )
            
            if notifications:
                Notification.objects.bulk_create(notifications)
                self.message_user(request, f"Создано глобальное уведомление и отправлено {len(notifications)} копий пользователям")
            else:
                self.message_user(request, "Глобальное уведомление создано, но нет активных пользователей", level='warning')
        else:
            # Обычное сохранение
            super().save_model(request, obj, form, change)
    
    actions = ['send_mass_notification', 'mark_as_read', 'mark_as_unread']
    
    @admin.action(description="Отправить массовое уведомление всем пользователям")
    def send_mass_notification(self, request, queryset):
        """Создать копию выбранного уведомления для всех активных пользователей"""
        if queryset.count() != 1:
            self.message_user(request, "Выберите только одно уведомление для массовой рассылки", level='error')
            return
        
        template = queryset.first()
        users = User.objects.filter(is_active=True)
        
        # Исключаем пользователей, которые отключили рассылку промо (если связано с акцией)
        if template.promotion or template.type in ['discount', 'sale']:
            users = users.exclude(notification_settings__promotions=False)
        
        existing_users = set()
        if template.user:
            existing_users.add(template.user.id)
        
        notifications = []
        for user in users:
            if user.id not in existing_users:
                notifications.append(
                    Notification(
                        user=user,
                        title=template.title,
                        message=template.message,
                        type=template.type,
                        card=template.card,
                        promotion=template.promotion,
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

