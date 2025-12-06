from django.contrib import admin
from .models import Card, CardImage, CardVideo, CardDocument, CardReview, CardQuestion

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
    readonly_fields = ('user', 'question', 'answer', 'created_at')
    can_delete = True
    show_change_link = True

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

# 🔹 Отдельная регистрация остальных моделей (если нужно)
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
    list_display = ['card', 'user', 'rating', 'created_at']
    readonly_fields = ['card', 'user', 'text', 'rating', 'created_at']

@admin.register(CardQuestion)
class CardQuestionAdmin(admin.ModelAdmin):
    list_display = ['card', 'user', 'question', 'answer', 'created_at']
    readonly_fields = ['card', 'user', 'question', 'answer', 'created_at']
