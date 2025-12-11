from django.db import models
from django.conf import settings

class Card(models.Model):
    CITY_CHOICES = (
        (1, 'Махачкала'),
        (2, 'Каспийск'),
        (3, 'Дербент'),
    )

    HOUSE_TYPE_CHOICES = (
        ('private', 'Частный дом'),
        ('apartment', 'Квартира'),
    )

    BUILDING_MATERIAL_CHOICES = (
        ('brick', 'Кирпичный'),
        ('panel', 'Панельный'),
        ('monolith', 'Монолитный'),
    )

    CATEGORY_CHOICES = (
        ('flat', 'Квартира'),
        ('new_building', 'Новостройка'),
    )

    ELEVATOR_CHOICES = (
        ('none', 'Нет'),
        ('passenger', 'Пассажирский'),
        ('cargo', 'Грузовой'),
    )

    PARKING_CHOICES = (
        ('none', 'Нет'),
        ('underground', 'Подземная'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    developer = models.ForeignKey(
        'developers.Developer',
        on_delete=models.CASCADE,
        related_name='cards',
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    rooms = models.PositiveIntegerField(default=1)
    city = models.IntegerField(choices=CITY_CHOICES, default=1)
    house_type = models.CharField(max_length=50, choices=HOUSE_TYPE_CHOICES, default='apartment')

    area = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    building_material = models.CharField(max_length=50, choices=BUILDING_MATERIAL_CHOICES, default='brick')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='flat')
    floors_total = models.PositiveIntegerField(default=1)
    elevator = models.CharField(max_length=20, choices=ELEVATOR_CHOICES, default='none')
    parking = models.CharField(max_length=20, choices=PARKING_CHOICES, default='none')
    balcony = models.BooleanField(default=False)
    ceiling_height = models.DecimalField(max_digits=3, decimal_places=2, default=2.50)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['city']),
            models.Index(fields=['house_type']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
            models.Index(fields=['city', 'house_type']),
        ]

    def __str__(self):
        return self.title
    
    
class CallRequest(models.Model):
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='call_requests'
    )
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    preferred_time = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Заявка от {self.name} ({self.phone_number})"


class CardImage(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cards/img/')

    def __str__(self):
        return f"{self.card.title} Image"


class CardVideo(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='cards/videos/')

    def __str__(self):
        return f"{self.card.title} Video"


class CardDocument(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='cards/documents/')
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.card.title})"


class CardReview(models.Model):
    card = models.ForeignKey(Card, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} for {self.card.title}"


class CardQuestion(models.Model):
    card = models.ForeignKey(Card, related_name='questions', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Question by {self.user} for {self.card.title}"


class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='search_history', on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    card = models.ForeignKey(
        'Card',
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'card')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.phone_number} added {self.card.title} to favorites"


class DiscountRequest(models.Model):
    """Запрос на скидку - пользователь может предложить свою цену"""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, 'На рассмотрении'),
        (APPROVED, 'Одобрено'),
        (REJECTED, 'Отклонено'),
    ]
    
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='discount_requests'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discount_requests'
    )
    original_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Текущая цена карточки"
    )
    requested_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Желаемая цена от пользователя"
    )
    discount_percent = models.FloatField(
        null=True,
        blank=True,
        editable=False,
        help_text="Процент скидки (вычисляется автоматически)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    message = models.TextField(
        blank=True,
        null=True,
        help_text="Причина или комментарий к запросу"
    )
    admin_comment = models.TextField(
        blank=True,
        null=True,
        help_text="Комментарий администратора при отклонении/одобрении"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['card', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):
        """Вычислить процент скидки перед сохранением"""
        if self.original_price and self.requested_price:
            discount = ((self.original_price - self.requested_price) / self.original_price) * 100
            self.discount_percent = round(discount, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Скидка {self.user} на {self.card.title}: {self.original_price} → {self.requested_price}"


class Recommendation(models.Model):
    """Рекомендации карточек для пользователя на основе AI алгоритма"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='recommended_to'
    )
    score = models.FloatField(
        default=0.0,
        help_text="Оценка релевантности (0-1)"
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        help_text="Причина рекомендации (город, тип, цена и т.д.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'card')
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Рекомендация {self.card.title} для {self.user} (score: {self.score})"


class AIAssistant(models.Model):
    """Конфигурация AI ассистента для проекта"""
    name = models.CharField(max_length=100, default='Dream House Assistant')
    api_provider = models.CharField(
        max_length=50,
        choices=[
            ('openai', 'OpenAI (GPT-4)'),
            ('anthropic', 'Anthropic (Claude)'),
            ('disabled', 'Отключен'),
        ],
        default='openai'
    )
    api_key = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Ключ API для провайдера (не видим в админке)"
    )
    model_name = models.CharField(
        max_length=100,
        default='gpt-4',
        help_text="Название модели (gpt-4, claude-3-opus и т.д.)"
    )
    system_prompt = models.TextField(
        default="""Ты профессиональный консультант по недвижимости. Помогай пользователям найти идеальный дом.
Ты имеешь доступ к базе данных карточек недвижимости и можешь давать персонализированные рекомендации.
Отвечай на русском языке, будь вежлив и информативен.""",
        help_text="Системный промпт для AI"
    )
    temperature = models.FloatField(
        default=0.7,
        help_text="Температура модели (0-1). 0 = детерминированно, 1 = творческо"
    )
    max_tokens = models.IntegerField(
        default=500,
        help_text="Максимальное количество токенов в ответе"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Включен ли ассистент"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Ассистент"
        verbose_name_plural = "AI Ассистенты"

    def __str__(self):
        return f"{self.name} ({self.get_api_provider_display()})"

    def get_api_key(self):
        """Получить API ключ из переменных окружения для безопасности"""
        import os
        env_key = os.environ.get(f'{self.api_provider.upper()}_API_KEY')
        return env_key or self.api_key


class ChatMessage(models.Model):
    """История чатов пользователя с AI ассистентом"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    message = models.TextField(
        help_text="Сообщение пользователя"
    )
    response = models.TextField(
        blank=True,
        null=True,
        help_text="Ответ от AI"
    )
    referenced_cards = models.ManyToManyField(
        Card,
        blank=True,
        related_name='mentioned_in_chats',
        help_text="Карточки, упомянутые в чате"
    )
    tokens_used = models.IntegerField(
        default=0,
        help_text="Количество токенов использовано"
    )
    is_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="Был ли ответ полезным (для улучшения AI)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Chat от {self.user} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"
