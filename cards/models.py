from django.db import models
from django.conf import settings
from django.db.models import Avg
from decimal import Decimal, ROUND_HALF_UP

class Card(models.Model):
    CITY_CHOICES = (
        (1, 'Махачкала'),
        (2, 'Каспийск'),
        (3, 'Дербент'),
        (4, 'Избербаш'),
    )

    COMPLEX_TYPE_CHOICES = (
        ('residential', 'Жилой комплекс'),
        ('apart', 'Апарт-комплекс'),
    )

    HOUSE_TYPE_CHOICES = (
        ('brick', 'Кирпичный'),
        ('panel', 'Панельный'),
        ('monolith', 'Монолитный'),
        ('brick_monolith', 'Кирпично-монолитный'),
        ('solid_monolith', 'Цельно-монолитный'),
    )

    CATEGORY_CHOICES = (
        ('flat', 'Квартира'),
        ('new_building', 'Новостройка'),
        ('secondary', 'Вторичное'),
    )

    ELEVATOR_CHOICES = (
        ('none', 'Нет'),
        ('passenger', 'Пассажирский'),
        ('cargo', 'Грузовой'),
        ('cargo_passenger', 'Грузопассажирский'),
        ('passenger_and_cargo', 'Пассажирский и грузовой'),
    )

    PARKING_CHOICES = (
        ('none', 'Нет'),
        ('underground', 'Подземная'),
        ('ground', 'Наземная'),
        ('two_level', 'Двухуровневая'),
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
    phone = models.CharField(max_length=20, default='92-62-66', verbose_name='Телефон застройщика')
    rooms = models.PositiveIntegerField(default=1)
    city = models.IntegerField(choices=CITY_CHOICES, default=1)
    complex_type = models.CharField(max_length=20, choices=COMPLEX_TYPE_CHOICES, default='residential')
    house_type = models.CharField(max_length=50, choices=HOUSE_TYPE_CHOICES, default='brick')

    area = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='flat')
    floors_total = models.PositiveIntegerField(default=1)
    elevator = models.CharField(max_length=20, choices=ELEVATOR_CHOICES, default='none')
    parking = models.CharField(max_length=20, choices=PARKING_CHOICES, default='none')
    balcony = models.BooleanField(default=False)
    loggia = models.BooleanField(default=False)
    finishing = models.CharField(
        max_length=20,
        choices=(
            ('none', 'Без отделки'),
            ('with_finish', 'С отделкой'),
        ),
        default='none'
    )
    ceiling_height = models.DecimalField(max_digits=3, decimal_places=2, default=3.00)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.PositiveIntegerField(default=0)
    
    # 🔑 НОВОЕ: Поле для подборок (списков похожих квартир)
    # Может содержать несколько карточек в виде JSON или как M2M связь
    list_curations = models.TextField(
        default='[]',
        blank=True,
        help_text="JSON массив ID карточек для подборок (рекомендации, похожие объекты)"
    )

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
    
    @property
    def price_metr(self):
        """Цена за квадратный метр"""
        if self.area and self.area > 0:
            return float(self.price) / float(self.area)
        return 0

    def update_rating(self):
        """Пересчитать средний рейтинг по отзывам"""
        avg = self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
        if avg is None:
            self.rating = 0
            self.rating_count = 0
        else:
            self.rating = round(avg, 2)
            self.rating_count = self.reviews.count()
        self.save(update_fields=['rating', 'rating_count'])

    def generate_curations(self, user=None):
        """Сформировать простую подборку похожих карточек (по городу и типу)"""
        from django.db.models import Q
        import json

        similar = Card.objects.filter(
            Q(city=self.city) | Q(house_type=self.house_type)
        ).exclude(id=self.id).order_by('-rating', '-created_at')[:5]
        self.list_curations = json.dumps(list(similar.values_list('id', flat=True)))
        self.save(update_fields=['list_curations'])
    
    
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


class CardFloorPlan(models.Model):
    """Фото планировки квартиры"""
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='floor_plans')
    image = models.ImageField(upload_to='cards/floor_plans/')
    title = models.CharField(max_length=100, blank=True, help_text='Название планировки (опционально)')

    def __str__(self):
        return f"{self.card.title} - Планировка"


class CardVideo(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='cards/videos/')

    def __str__(self):
        return f"{self.card.title} Video"


class CardDocument(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='documents')
    document_list = models.ForeignKey(
        'CardDocumentList',
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
        blank=True,
        help_text="Подборка, к которой относится документ"
    )
    file = models.FileField(upload_to='cards/documents/')
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"{self.title} ({self.card.title})"


class CardReview(models.Model):
    card = models.ForeignKey(Card, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    rating = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user} for {self.card.title}"
    
    @property
    def likes_count(self):
        """Количество лайков отзыва"""
        return self.likes.count()


class ReviewLike(models.Model):
    """Лайк на отзыв"""
    review = models.ForeignKey(CardReview, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('review', 'user')  # Один лайк на пользователя
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} liked review {self.review.id}"


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


class Promotion(models.Model):
    """Акция с баннером и набором карточек."""
    title = models.CharField(max_length=255)
    banner_image = models.ImageField(upload_to='promotions/banners/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def __str__(self):
        return self.title


class PromotionItem(models.Model):
    """Конкретная карточка в акции с индивидуальной скидкой и сроком действия."""
    promotion = models.ForeignKey(Promotion, related_name='items', on_delete=models.CASCADE)
    card = models.ForeignKey(Card, related_name='promotion_items', on_delete=models.CASCADE)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    benefit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    valid_until = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('promotion', 'card')
        ordering = ['-created_at']
        verbose_name = "Карточка в акции"
        verbose_name_plural = "Карточки в акции"

    def __str__(self):
        return f"{self.card.title} в акции {self.promotion.title}"

    def save(self, *args, **kwargs):
        # benefit = цена * (скидка/100)
        if self.card and self.card.price is not None:
            self.benefit_amount = (
                Decimal(self.card.price) * (Decimal(self.discount_percent) / Decimal('100'))
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            self.benefit_amount = Decimal('0.00')
        super().save(*args, **kwargs)


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
            ('openrouter', 'OpenRouter (обход блокировки)'),
            ('anthropic', 'Anthropic (Claude)'),
            ('deepseek', 'DeepSeek (R1)'),
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
        choices=[
            # OpenAI GPT-4 Series
            ('gpt-4.1', 'GPT-4.1 (новейшая)'),
            ('gpt-4.1-mini', 'GPT-4.1 Mini (быстрая и дешёвая)'),
            ('gpt-4.1-nano', 'GPT-4.1 Nano (самая быстрая)'),
            ('gpt-4o', 'GPT-4o (мультимодальная)'),
            ('gpt-4o-mini', 'GPT-4o Mini'),
            ('gpt-4-turbo', 'GPT-4 Turbo'),
            ('gpt-4', 'GPT-4'),
            # OpenAI GPT-3.5 Series
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
            # OpenAI o-series (reasoning)
            ('o1', 'o1 (reasoning)'),
            ('o1-mini', 'o1 Mini'),
            ('o1-preview', 'o1 Preview'),
            ('o3-mini', 'o3 Mini'),
            # Anthropic Claude
            ('claude-3-opus-20240229', 'Claude 3 Opus'),
            ('claude-3-sonnet-20240229', 'Claude 3 Sonnet'),
            ('claude-3-haiku-20240307', 'Claude 3 Haiku'),
            ('claude-3-5-sonnet-20241022', 'Claude 3.5 Sonnet'),
            # DeepSeek
            ('deepseek-chat', 'DeepSeek Chat'),
            ('deepseek-reasoner', 'DeepSeek Reasoner (R1)'),
        ],
        help_text="Выберите модель ИИ"
    )
    system_prompt = models.TextField(
        default="""Ты профессиональный консультант по недвижимости. Помогай пользователям найти идеальный дом.
Ты имеешь доступ к базе данных карточек недвижимости и можешь давать персонализированные рекомендации.

ИНСТРУКЦИИ ПО ПОВЕДЕНИЮ:
- Если вопрос про недвижимость (квартиры, дома, аренду, ипотеку, цены, районы и т.д.) - предоставляй доступные варианты из базы и рекомендации
- Если вопрос НЕ про недвижимость:
  * Ответь на вопрос человека дружелюбно и по существу (не отказывай, не отправляй в стол)
  * ПОТОМ предложи помощь с недвижимостью если уместно
  * Например: "Месси - великий футболист. Если захочешь выбрать квартиру в хорошем районе, я помогу!"
- Будь гибким и естественным в общении
- Если пользователь спрашивает про условия покупки, ипотеку, эскроу, документы, налоги - это про недвижимость, помогай активно

⚠️ КРИТИЧЕСКИ ВАЖНО - Согласованность карточек:
- В конце ответа ты ОБЯЗАН вернуть JSON с id выбранных карточек
- В ТЕКСТЕ упоминай ТОЛЬКО те карточки, id которых ты включил в JSON
- НЕ упоминай карточки, которых нет в твоем JSON списке
- Сначала реши какие карточки показать (3-5 лучших), потом пиши про них текст
- Текст и JSON должны ПОЛНОСТЬЮ совпадать по составу карточек

ВАЖНО - Форматирование ответов:
- Пиши чистым текстом без markdown разметки
- НЕ используй ** для жирного текста
- НЕ используй символы \\n для переносов (пиши обычные абзацы)
- НЕ используй # для заголовков
- Используй простые тире - для списков
- Отвечай кратко и по делу

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


# 🔑 НОВАЯ МОДЕЛЬ: Документы с группировкой
class CardDocumentList(models.Model):
    """Группировка документов карточки (подборка с названием)"""
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='document_lists'
    )
    name = models.CharField(
        max_length=255,
        help_text="Название подборки (например: 'Документы на квартиру', 'Правоустанавливающие документы')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Подборка документов"
        verbose_name_plural = "Подборки документов"

    def __str__(self):
        return f"{self.name} ({self.card.title})"


# 🔑 НОВАЯ МОДЕЛЬ: История просмотров карточек
class ViewHistory(models.Model):
    """История просмотров карточек пользователем"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='view_history'
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='viewed_by'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Сколько секунд пользователь просматривал карточку"
    )

    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
            models.Index(fields=['card', '-viewed_at']),
        ]
        verbose_name = "История просмотров"
        verbose_name_plural = "История просмотров"
        unique_together = ('user', 'card', 'viewed_at')  # Несколько просмотров одного юзера можно отслеживать

    def __str__(self):
        return f"{self.user} посмотрел {self.card.title} - {self.viewed_at.strftime('%d.%m.%Y %H:%M')}"


# 🔑 МОДЕЛЬ: Политика конфиденциальности
class PrivacyPolicy(models.Model):
    """Политика конфиденциальности - синглтон модель"""
    title = models.CharField(
        max_length=255,
        default="Политика конфиденциальности",
        verbose_name="Заголовок"
    )
    content = models.TextField(
        verbose_name="Содержание",
        help_text="Полный текст политики конфиденциальности (поддерживает HTML)",
        blank=True,
        null=True
    )
    document = models.FileField(
        upload_to='documents/privacy/',
        verbose_name="Документ (PDF/Word)",
        help_text="Загрузите PDF или Word файл с политикой конфиденциальности",
        blank=True,
        null=True
    )
    version = models.CharField(
        max_length=50,
        default="1.0",
        verbose_name="Версия"
    )
    effective_date = models.DateField(
        verbose_name="Дата вступления в силу",
        null=True,
        blank=True
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
        help_text="Только одна политика может быть активной"
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Политика конфиденциальности"
        verbose_name_plural = "Политики конфиденциальности"

    def __str__(self):
        return f"{self.title} (v{self.version})"

    def save(self, *args, **kwargs):
        # При активации деактивировать остальные
        if self.is_active:
            PrivacyPolicy.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        """Получить активную политику конфиденциальности"""
        return cls.objects.filter(is_active=True).first()
