from django.contrib import admin
from django.db import transaction
from django.utils.html import format_html
from .models import (
    Card, CardImage, CardFloorPlan, CardVideo, CardDocument, CardReview, CardQuestion, ReviewLike,
    CallRequest, NewCallRequest, InProgressCallRequest, ProcessedCallRequest,
    DiscountRequest, Recommendation, AIAssistant, ChatMessage,
    CardDocumentList, ViewHistory, Promotion, PromotionItem, PrivacyPolicy
)
from .models_deeplink import DeepLinkConfig


# ==================== INLINES ====================

class CardImageInline(admin.TabularInline):
    model = CardImage
    extra = 1
    max_num = 15
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px; border-radius:4px;">', obj.image.url)
        return "—"
    image_preview.short_description = "Превью"


class CardFloorPlanInline(admin.TabularInline):
    model = CardFloorPlan
    extra = 1
    max_num = 10
    verbose_name = 'Планировка'
    verbose_name_plural = 'Планировки'


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
    readonly_fields = ('user', 'question', 'created_at')
    can_delete = True
    show_change_link = True


class PromotionItemInline(admin.TabularInline):
    model = PromotionItem
    extra = 1
    autocomplete_fields = ['card']
    fields = ['card', 'discount_percent', 'benefit_amount', 'valid_until']
    readonly_fields = ['benefit_amount']


# ==================== CARD ====================

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = [
        'thumbnail', 'title', 'developer', 'price', 'area', 'rooms', 'city',
        'category', 'house_type', 'rating', 'created_at'
    ]
    list_display_links = ['thumbnail', 'title']
    list_editable = ['price']
    search_fields = ['title', 'address', 'description', 'developer__name']
    list_filter = [
        'city', 'complex_type', 'house_type', 'category', 'finishing',
        'elevator', 'parking', 'balcony', 'loggia'
    ]
    date_hierarchy = 'created_at'
    exclude = ['owner']
    inlines = [CardImageInline, CardFloorPlanInline, CardVideoInline, CardDocumentInline, CardReviewInline, CardQuestionInline]
    actions = ['duplicate_cards']
    actions_on_top = True
    actions_on_bottom = True

    class Media:
        js = ('cards/admin_dirty_guard.js',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('developer', 'owner').prefetch_related('images')

    def thumbnail(self, obj):
        first = obj.images.first()
        if first and first.image:
            return format_html('<img src="{}" style="height:48px; width:64px; object-fit:cover; border-radius:4px;">', first.image.url)
        return format_html('<span style="color:#ccc;">—</span>')
    thumbnail.short_description = "Фото"

    def save_model(self, request, obj, form, change):
        is_new = not change
        if is_new and not obj.owner_id:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
        if is_new and obj.developer:
            from developers.models import Subscription
            from notifications.models import Notification
            subs = Subscription.objects.filter(developer=obj.developer).select_related('user')
            Notification.objects.bulk_create([
                Notification(
                    user=sub.user,
                    title="Новая квартира от вашего девелопера",
                    message=f"{obj.title} — {obj.price}₽, {obj.rooms} комн.",
                    card=obj,
                )
                for sub in subs
            ])

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not actions and request.user.has_perm('cards.add_card'):
            if hasattr(self, 'duplicate_cards'):
                actions = {
                    'duplicate_cards': (
                        self.duplicate_cards,
                        'duplicate_cards',
                        "Скопировать выбранные карточки"
                    )
                }
        return actions

    @admin.action(description="Скопировать выбранные карточки")
    def duplicate_cards(self, request, queryset):
        created_count = 0
        with transaction.atomic():
            for original in queryset:
                images = list(original.images.all())
                videos = list(original.videos.all())
                documents = list(original.documents.all())

                # Создаём копию без мутации оригинала
                new_card = Card.objects.get(pk=original.pk)
                new_card.pk = None
                new_card.id = None
                new_card.rating = 0
                new_card.rating_count = 0
                new_card.title = f"{original.title} (копия)"
                new_card.created_at = None
                new_card.save()

                for img in images:
                    img.pk = None
                    img.id = None
                    img.card = new_card
                    img.save()

                for vid in videos:
                    vid.pk = None
                    vid.id = None
                    vid.card = new_card
                    vid.save()

                for doc in documents:
                    doc.pk = None
                    doc.id = None
                    doc.card = new_card
                    doc.save()

                created_count += 1

        self.message_user(request, f"Создано копий: {created_count}")


# ==================== IMAGES / VIDEO / DOCUMENTS ====================

@admin.register(CardImage)
class CardImageAdmin(admin.ModelAdmin):
    list_display = ['card', 'image_preview']
    search_fields = ['card__title']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px; border-radius:4px;">', obj.image.url)
        return "—"
    image_preview.short_description = "Превью"


@admin.register(CardVideo)
class CardVideoAdmin(admin.ModelAdmin):
    list_display = ['card', 'video']
    search_fields = ['card__title']


@admin.register(CardDocument)
class CardDocumentAdmin(admin.ModelAdmin):
    list_display = ['card', 'title', 'uploaded_at']
    search_fields = ['card__title', 'title']


# ==================== ОТЗЫВЫ ====================

@admin.register(CardReview)
class CardReviewAdmin(admin.ModelAdmin):
    list_display = ['card', 'user', 'star_rating', 'likes_count', 'created_at']
    readonly_fields = ['card', 'user', 'text', 'rating', 'created_at']
    search_fields = ['card__title', 'user__phone_number', 'text']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('card', 'user')

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Лайки'

    def star_rating(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = '#f5a623' if obj.rating >= 4 else ('#e74c3c' if obj.rating <= 2 else '#f39c12')
        return format_html('<span style="color:{};">{}</span>', color, stars)
    star_rating.short_description = 'Рейтинг'


@admin.register(ReviewLike)
class ReviewLikeAdmin(admin.ModelAdmin):
    list_display = ['review', 'user', 'created_at']
    readonly_fields = ['review', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__phone_number', 'review__text']


# ==================== ВОПРОСЫ ====================

@admin.register(CardQuestion)
class CardQuestionAdmin(admin.ModelAdmin):
    list_display = ['card', 'user', 'short_question', 'has_answer', 'created_at']
    readonly_fields = ['card', 'user', 'question', 'created_at']
    list_filter = ['card__city', 'created_at']
    search_fields = ['question', 'answer', 'user__phone_number', 'card__title']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('card', 'user')

    def short_question(self, obj):
        return obj.question[:60] + '…' if len(obj.question) > 60 else obj.question
    short_question.short_description = 'Вопрос'

    def has_answer(self, obj):
        if obj.answer:
            return format_html('<span style="color:green;">✔ Есть ответ</span>')
        return format_html('<span style="color:#e74c3c;">✘ Без ответа</span>')
    has_answer.short_description = 'Статус'

    # Менеджеры (staff) могут отвечать на вопросы, только api_key скрыт у не-суперпользователей
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields


# ==================== ЗАЯВКИ НА ЗВОНОК ====================

CALL_STATUS_COLORS = {
    'new':          ('#e74c3c', '🔴 Новый'),
    'in_progress':  ('#f39c12', '🟡 В работе'),
    'processed':    ('#27ae60', '🟢 Обработан'),
}

CALL_NEXT_STATUS = {
    'new': 'in_progress',
    'in_progress': 'processed',
}


class CallRequestAdminBase(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'card', 'preferred_time', 'status_badge', 'created_at']
    list_filter = ['created_at', 'card__city']
    search_fields = ['name', 'phone_number', 'card__title']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    actions = ['move_to_in_progress', 'move_to_processed', 'move_to_new']

    fieldsets = (
        ('Контактная информация', {'fields': ('name', 'phone_number')}),
        ('Квартира', {'fields': ('card',)}),
        ('Время звонка', {'fields': ('preferred_time',)}),
        ('Статус', {'fields': ('status', 'created_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('card')

    def status_badge(self, obj):
        color, label = CALL_STATUS_COLORS.get(obj.status, ('#999', obj.status))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Статус'

    @admin.action(description="→ Перевести в «В работе»")
    def move_to_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress', is_processed=False)
        self.message_user(request, f"Переведено в «В работе»: {updated}")

    @admin.action(description="→ Перевести в «Обработан»")
    def move_to_processed(self, request, queryset):
        updated = queryset.update(status='processed', is_processed=True)
        self.message_user(request, f"Обработано: {updated}")

    @admin.action(description="→ Вернуть в «Новый»")
    def move_to_new(self, request, queryset):
        updated = queryset.update(status='new', is_processed=False)
        self.message_user(request, f"Возвращено в «Новый»: {updated}")


@admin.register(CallRequest)
class CallRequestAdmin(CallRequestAdminBase):
    """Все заявки сразу — для общего просмотра."""
    list_filter = ['status', 'created_at', 'card__city']


@admin.register(NewCallRequest)
class NewCallRequestAdmin(CallRequestAdminBase):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=CallRequest.STATUS_NEW)


@admin.register(InProgressCallRequest)
class InProgressCallRequestAdmin(CallRequestAdminBase):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=CallRequest.STATUS_IN_PROGRESS)


@admin.register(ProcessedCallRequest)
class ProcessedCallRequestAdmin(CallRequestAdminBase):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=CallRequest.STATUS_PROCESSED)


# ==================== СКИДКИ ====================

STATUS_COLORS = {
    'pending':  ('#f39c12', '⏳ На рассмотрении'),
    'approved': ('#27ae60', '✔ Одобрена'),
    'rejected': ('#e74c3c', '✘ Отклонена'),
}

@admin.register(DiscountRequest)
class DiscountRequestAdmin(admin.ModelAdmin):
    list_display = [
        'card', 'user', 'original_price', 'requested_price',
        'discount_percent', 'status_badge', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'card__city']
    search_fields = ['card__title', 'user__phone_number', 'message']
    readonly_fields = ['discount_percent', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    actions = ['approve_discounts', 'reject_discounts']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('card', 'user', 'card__owner')

    def status_badge(self, obj):
        color, label = STATUS_COLORS.get(obj.status, ('#999', obj.status))
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:10px;font-size:11px;">{}</span>',
            color, label
        )
    status_badge.short_description = 'Статус'

    fieldsets = (
        ('Информация о запросе', {'fields': ('card', 'user', 'message', 'created_at', 'updated_at')}),
        ('Цены', {'fields': ('original_price', 'requested_price', 'discount_percent')}),
        ('Решение менеджера', {'fields': ('status', 'admin_comment')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        if obj.status != 'pending':
            return ['card', 'user', 'original_price', 'requested_price', 'discount_percent', 'created_at', 'updated_at', 'message']
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        old_status = None
        if change and obj.pk:
            try:
                old_status = DiscountRequest.objects.values_list('status', flat=True).get(pk=obj.pk)
            except DiscountRequest.DoesNotExist:
                pass

        is_new = not change
        super().save_model(request, obj, form, change)

        from notifications.models import Notification

        if is_new:
            if obj.card.owner:
                Notification.objects.create(
                    user=obj.card.owner,
                    title="Запрос на скидку",
                    message=f"Пользователь предложил {obj.requested_price}₽ за {obj.card.title} (было {obj.original_price}₽)"
                )
            Notification.objects.create(
                user=obj.user,
                title="Ваш запрос на скидку отправлен",
                message=f"Запрос отправлен владельцу {obj.card.title}. Статус: На рассмотрении"
            )
        elif old_status == 'pending' and obj.status in ('approved', 'rejected'):
            status_text = "одобрена" if obj.status == 'approved' else "отклонена"
            Notification.objects.create(
                user=obj.user,
                title="Решение по вашей скидке",
                message=f"Ваша заявка на скидку по {obj.card.title} {status_text}."
                        + (f" Комментарий: {obj.admin_comment}" if obj.admin_comment else "")
            )

    @admin.action(description="Одобрить выбранные запросы на скидку")
    def approve_discounts(self, request, queryset):
        pending = queryset.filter(status='pending')
        from notifications.models import Notification
        notifications = []
        for obj in pending.select_related('user', 'card'):
            notifications.append(Notification(
                user=obj.user,
                title="Скидка одобрена",
                message=f"Ваш запрос на скидку по {obj.card.title} одобрен.",
                card=obj.card,
            ))
        pending.update(status='approved')
        if notifications:
            Notification.objects.bulk_create(notifications)
        self.message_user(request, f"Одобрено: {pending.count()}")

    @admin.action(description="Отклонить выбранные запросы на скидку")
    def reject_discounts(self, request, queryset):
        pending = queryset.filter(status='pending')
        from notifications.models import Notification
        notifications = []
        for obj in pending.select_related('user', 'card'):
            notifications.append(Notification(
                user=obj.user,
                title="Скидка отклонена",
                message=f"Ваш запрос на скидку по {obj.card.title} отклонён.",
                card=obj.card,
            ))
        pending.update(status='rejected')
        if notifications:
            Notification.objects.bulk_create(notifications)
        self.message_user(request, f"Отклонено: {pending.count()}")


# ==================== РЕКОМЕНДАЦИИ ====================

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['card', 'user', 'score', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['card__title', 'user__phone_number', 'reason']
    readonly_fields = ['user', 'card', 'score', 'reason', 'created_at']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('card', 'user')


# ==================== АКЦИИ ====================

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'active_badge', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title']
    inlines = [PromotionItemInline]
    readonly_fields = ['created_at', 'updated_at']

    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="background:#27ae60;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">Активна</span>')
        return format_html('<span style="background:#bdc3c7;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px;">Неактивна</span>')
    active_badge.short_description = 'Статус'


# ==================== AI АССИСТЕНТ ====================

@admin.register(AIAssistant)
class AIAssistantAdmin(admin.ModelAdmin):
    list_display = ['name', 'api_provider', 'model_name', 'active_badge', 'updated_at']
    list_filter = ['api_provider', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {'fields': ('name', 'is_active', 'created_at', 'updated_at')}),
        ('API конфигурация', {
            'fields': ('api_provider', 'api_key', 'model_name'),
            'description': 'Ключ API можно установить через переменные окружения для безопасности'
        }),
        ('Параметры модели', {'fields': ('system_prompt', 'temperature', 'max_tokens')}),
    )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ['api_key']
        return self.readonly_fields

    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#27ae60;font-weight:bold;">● Активен</span>')
        return format_html('<span style="color:#bdc3c7;">● Выкл</span>')
    active_badge.short_description = 'Состояние'


# ==================== ИСТОРИЯ ЧАТОВ ====================

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'short_message', 'helpful_badge', 'tokens_used', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['user__phone_number', 'message', 'response']
    readonly_fields = ['created_at', 'referenced_cards', 'tokens_used']
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def short_message(self, obj):
        return obj.message[:70] + '…' if len(obj.message) > 70 else obj.message
    short_message.short_description = 'Сообщение'

    def helpful_badge(self, obj):
        if obj.is_helpful is True:
            return format_html('<span style="color:#27ae60;">👍</span>')
        if obj.is_helpful is False:
            return format_html('<span style="color:#e74c3c;">👎</span>')
        return '—'
    helpful_badge.short_description = 'Оценка'

    fieldsets = (
        ('Пользователь', {'fields': ('user', 'created_at')}),
        ('Сообщение', {'fields': ('message',)}),
        ('Ответ AI', {'fields': ('response', 'tokens_used')}),
        ('Связанные карточки', {'fields': ('referenced_cards',)}),
        ('Обратная связь', {'fields': ('is_helpful',)}),
    )

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        return ['user', 'message', 'response', 'referenced_cards', 'tokens_used', 'created_at']


# ==================== ДОКУМЕНТЫ ====================

@admin.register(CardDocumentList)
class CardDocumentListAdmin(admin.ModelAdmin):
    list_display = ['name', 'card', 'created_at', 'updated_at']
    list_filter = ['created_at', 'card__city']
    search_fields = ['name', 'card__title']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {'fields': ('card', 'name')}),
        ('Метаданные', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


# ==================== ИСТОРИЯ ПРОСМОТРОВ ====================

@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'card', 'viewed_at', 'duration_seconds']
    list_filter = ['viewed_at', 'card__city']
    search_fields = ['user__phone_number', 'card__title']
    readonly_fields = ['viewed_at', 'user', 'card']
    date_hierarchy = 'viewed_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'card')

    def has_add_permission(self, request):
        return False


# ==================== ПОЛИТИКА КОНФИДЕНЦИАЛЬНОСТИ ====================

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ['title', 'version', 'is_active', 'has_document', 'effective_date', 'updated_at']
    list_filter = ['is_active', 'effective_date']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']

    fieldsets = (
        ('Основная информация', {'fields': ('title', 'version', 'is_active', 'effective_date')}),
        ('Содержание (текст или файл)', {
            'fields': ('content', 'document'),
            'description': 'Можно добавить текст (поддерживает HTML) и/или загрузить PDF/Word документ'
        }),
        ('Метаданные', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#27ae60;font-weight:bold;">✔ Активна</span>')
        return format_html('<span style="color:#bdc3c7;">✘ Архив</span>')
    active_badge.short_description = 'Статус'

    def has_document(self, obj):
        return bool(obj.document)
    has_document.boolean = True
    has_document.short_description = 'Файл'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


# ==================== DEEP LINK ====================

@admin.register(DeepLinkConfig)
class DeepLinkConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'ios_bundle_id', 'android_package_name')

    fieldsets = (
        ('iOS (Universal Links)', {'fields': ('ios_team_id', 'ios_bundle_id', 'appstore_url')}),
        ('Android (App Links)', {'fields': ('android_package_name', 'android_sha256_fingerprint', 'playstore_url')}),
        ('Deep Link пути', {
            'fields': ('deep_link_paths',),
            'description': 'Пути, которые будут перехватываться приложением. Через запятую.',
        }),
    )

    def has_add_permission(self, request):
        return not DeepLinkConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
