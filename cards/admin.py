from django.contrib import admin
from .models import (
    Card, CardImage, CardVideo, CardDocument, CardReview, CardQuestion, ReviewLike,  # 🔑 НОВОЕ: ReviewLike
    CallRequest, DiscountRequest, Recommendation, AIAssistant, ChatMessage,
    CardDocumentList, ViewHistory  # 🔑 НОВЫЕ
)

# 🔹 Inlines для связанных моделей
class CardImageInline(admin.TabularInline):
    model = CardImage
    extra = 1
    max_num = 15

class CardVideoInline(admin.TabularInline):
    model = CardVideo
    extra = 1
    max_num = 10

class CardDocumentInline(admin.TabularInline):
    model = CardDocument
    extra = 1
    max_num = 10

class CardReviewInline(admin.TabularInline):
    model = CardReview
    extra = 0
    readonly_fields = ('user', 'rating', 'text', 'created_at')
    can_delete = True
    show_change_link = True

class CardQuestionInline(admin.TabularInline):
    model = CardQuestion
    extra = 0
    readonly_fields = ('user', 'question', 'created_at')  # answer редактируем только суперпользователем
    can_delete = True
    show_change_link = True

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ['answer']
        return self.readonly_fields


# 🔹 Основная админка для карточки
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'owner', 'price', 'rooms', 'city', 'house_type',
        'category', 'floors_total', 'elevator', 'parking',
        'rating', 'rating_count', 'created_at'
    ]
    list_editable = [
        'price', 'rooms', 'city', 'house_type', 'category',
        'floors_total', 'elevator', 'parking'
    ]
    search_fields = ['title', 'address', 'description']
    list_filter = ['city', 'house_type', 'category', 'floors_total', 'elevator', 'parking']
    inlines = [CardImageInline, CardVideoInline, CardDocumentInline, CardReviewInline, CardQuestionInline]
    
    def save_model(self, request, obj, form, change):
        """Сохранить карточку и создать уведомления подписчикам"""
        is_new = not change  # change=False для новых
        super().save_model(request, obj, form, change)
        
        # Если это новая карточка с девелопером, создать уведомления подписчикам
        if is_new and obj.developer:
            from developers.models import Subscription
            from notifications.models import Notification
            
            subs = Subscription.objects.filter(developer=obj.developer)
            
            for sub in subs:
                Notification.objects.create(
                    user=sub.user,
                    title="Новая квартира от вашего девелопера",
                    message=f"{obj.title} — {obj.price}₽, {obj.rooms} комн."
                )


# 🔹 Отдельная регистрация остальных моделей
@admin.register(CardImage)
class CardImageAdmin(admin.ModelAdmin):
    list_display = ['card', 'image']

@admin.register(CardVideo)
class CardVideoAdmin(admin.ModelAdmin):
    list_display = ['card', 'video']

@admin.register(CardDocument)
class CardDocumentAdmin(admin.ModelAdmin):
    list_display = ['card', 'title', 'uploaded_at']

@admin.register(CardReview)
class CardReviewAdmin(admin.ModelAdmin):
    list_display = ['card', 'user', 'rating', 'likes_count', 'created_at']  # 🔑 НОВОЕ: likes_count
    readonly_fields = ['card', 'user', 'text', 'rating', 'created_at']
    
    def likes_count(self, obj):
        """Количество лайков"""
        return obj.likes.count()
    likes_count.short_description = 'Лайки'


@admin.register(ReviewLike)  # 🔑 НОВОЕ: Register ReviewLike
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    readonly_fields = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__phone_number', 'review__text']


@admin.register(CardQuestion)
class CardQuestionAdmin(admin.ModelAdmin):
    list_display = ['card', 'user', 'question', 'answer', 'created_at']
    readonly_fields = ['card', 'user', 'question', 'created_at']  # answer редактируем только суперпользователем

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ['answer']
        return self.readonly_fields

    list_filter = ['card__title', 'card__city']
    search_fields = ['question', 'answer', 'user__phone_number']


# ==================== ЗАЯВКИ НА ЗВОНОК ====================

@admin.register(CallRequest)
class CallRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'card', 'preferred_time', 'is_processed', 'created_at']
    list_filter = ['is_processed', 'created_at', 'card__city']
    search_fields = ['name', 'phone_number', 'card__title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('name', 'phone_number')
        }),
        ('Квартира', {
            'fields': ('card',)
        }),
        ('Время звонка', {
            'fields': ('preferred_time',)
        }),
        ('Статус', {
            'fields': ('is_processed', 'created_at')
        }),
    )


# ==================== СКИДКИ ====================

@admin.register(DiscountRequest)
class DiscountRequestAdmin(admin.ModelAdmin):
    list_display = [
        'card', 'user', 'original_price', 'requested_price',
        'discount_percent', 'status', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'card__city']
    search_fields = ['card__title', 'user__phone_number', 'message']
    readonly_fields = ['discount_percent', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Информация о запросе', {
            'fields': ('card', 'user', 'message', 'created_at', 'updated_at')
        }),
        ('Цены', {
            'fields': ('original_price', 'requested_price', 'discount_percent')
        }),
        ('Решение администратора', {
            'fields': ('status', 'admin_comment')
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        # Если уже обработан, заблокировать редактирование
        if obj.status != 'pending':
            return ['card', 'user', 'original_price', 'requested_price', 'discount_percent', 'created_at', 'updated_at', 'message']
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        """Сохранить и создать уведомления"""
        is_new = not change  # change=False для новых, True для обновления
        super().save_model(request, obj, form, change)
        
        # Если это новая скидка, создать уведомления
        if is_new:
            from notifications.models import Notification
            
            # Уведомление для владельца квартиры
            if obj.card.owner:
                Notification.objects.create(
                    user=obj.card.owner,
                    title="Запрос на скидку",
                    message=f"Пользователь предложил {obj.requested_price}₽ за {obj.card.title} (было {obj.original_price}₽)"
                )

            # Уведомление для пользователя
            Notification.objects.create(
                user=obj.user,
                title="Ваш запрос на скидку отправлен",
                message=f"Запрос на скидку отправлен владельцу {obj.card.title}. Статус: На рассмотрении"
            )


# ==================== РЕКОМЕНДАЦИИ ====================

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['card', 'user', 'score', 'reason', 'created_at']
    list_filter = ['score', 'created_at']
    search_fields = ['card__title', 'user__phone_number', 'reason']
    readonly_fields = ['created_at']

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        # Рекомендации автоматически создаются, редактировать нельзя
        return ['user', 'card', 'score', 'reason', 'created_at']


# ==================== AI АССИСТЕНТ ====================

@admin.register(AIAssistant)
class AIAssistantAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_provider', 'model_name', 'is_active', 'updated_at']
    list_filter = ['api_provider', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'is_active', 'created_at', 'updated_at')
        }),
        ('API конфигурация', {
            'fields': ('api_provider', 'api_key', 'model_name'),
            'description': 'Ключ API можно установить через переменные окружения для безопасности'
        }),
        ('Параметры модели', {
            'fields': ('system_prompt', 'temperature', 'max_tokens'),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # Ограничить редактирование api_key в админке для безопасности
        if not request.user.is_superuser:
            return self.readonly_fields + ['api_key']
        return self.readonly_fields


# ==================== ИСТОРИЯ ЧАТОВ ====================

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'is_helpful', 'tokens_used']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['user__phone_number', 'message', 'response']
    readonly_fields = ['created_at', 'referenced_cards', 'tokens_used']

    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'created_at')
        }),
        ('Сообщение', {
            'fields': ('message',)
        }),
        ('Ответ AI', {
            'fields': ('response', 'tokens_used')
        }),
        ('Связанные карточки', {
            'fields': ('referenced_cards',)
        }),
        ('Обратная связь', {
            'fields': ('is_helpful',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        # История чатов только для чтения
        return ['user', 'message', 'response', 'referenced_cards', 'tokens_used', 'created_at']


# 🔑 НОВАЯ: Админка для подборок документов
@admin.register(CardDocumentList)
class CardDocumentListAdmin(admin.ModelAdmin):
    list_display = ['name', 'card', 'created_at', 'updated_at']
    list_filter = ['created_at', 'card__city']
    search_fields = ['name', 'card__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('card', 'name')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# 🔑 НОВАЯ: Админка для истории просмотров
@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'card', 'viewed_at', 'duration_seconds']
    list_filter = ['viewed_at', 'card__city', 'user']
    search_fields = ['user__phone_number', 'card__title']
    readonly_fields = ['viewed_at', 'user', 'card']
    
    fieldsets = (
        ('Просмотр', {
            'fields': ('user', 'card', 'viewed_at')
        }),
        ('Информация о просмотре', {
            'fields': ('duration_seconds',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Просмотры создаются автоматически через API
        return False
