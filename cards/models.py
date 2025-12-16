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
    
    # 🔑 НОВОЕ: Поле для подборок (списков похожих квартир)
    # Может содержать несколько карточек в виде JSON или как M2M связь
    list_curations = models.TextField(
        default='[]',
        blank=True,
        help_text="JSON массив с объектами карточек для подборок. Каждый объект содержит: id, address, price, rooms, city, rating"
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
    
    def update_rating(self):
        """Обновить рейтинг на основе отзывов"""
        from django.db.models import Avg
        avg_rating = self.user_reviews.aggregate(Avg('rating'))['rating__avg']
        if avg_rating:
            self.rating = round(avg_rating, 2)
            self.rating_count = self.user_reviews.count()
            self.save(update_fields=['rating', 'rating_count'])
    
    def generate_curations(self, user=None, limit: int = 5):
        """
        Генерирует подборку похожих квартир
        Алгоритм: если есть user, ищет похожие на его предпочтения
        Иначе ищет похожие по параметрам (город, цена, комнаты)
        """
        import json
        from django.db.models import Q
        
        similar_cards = Card.objects.exclude(id=self.id)
        
        # Если есть пользователь, смотрим его просмотры/избранное
        if user:
            from .models import Favorite, ViewHistory
            # Карточки которые он уже смотрел
            viewed_cards = ViewHistory.objects.filter(user=user).values_list('card_id', flat=True)
            # Карточки которые добавил в избранное
            favorite_cards = Favorite.objects.filter(user=user).values_list('card_id', flat=True)
            # Исключим уже просмотренные
            similar_cards = similar_cards.exclude(id__in=list(viewed_cards) + list(favorite_cards))
        
        # Сортируем по параметрам:
        # 1. Тот же город
        # 2. Похожая цена (±30%)
        # 3. Похожее количество комнат
        from decimal import Decimal
        price_min = self.price * Decimal('0.7')
        price_max = self.price * Decimal('1.3')
        
        q_filter = Q(city=self.city)
        q_filter |= Q(
            price__gte=price_min,
            price__lte=price_max,
            rooms=self.rooms
        )
        
        similar_cards = similar_cards.filter(q_filter).order_by('-rating', '-created_at')[:limit]
        
        # Формируем JSON с полной информацией
        curations = []
        for card in similar_cards:
            curations.append({
                'id': card.id,
                'address': card.address,
                'price': float(card.price),
                'rooms': card.rooms,
                'city': card.get_city_display(),
                'rating': float(card.rating),
                'title': card.title,
            })
        
        self.list_curations = json.dumps(curations, ensure_ascii=False)
        self.save(update_fields=['list_curations'])
        
        return curations
    
    
class CallRequest(models.Model):
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='call_requests',
        verbose_name="Квартира"
    )
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone_number = models.CharField(max_length=20, verbose_name="Телефон")
    preferred_time = models.CharField(max_length=100, blank=True, verbose_name="Предпочитаемое время")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    is_processed = models.BooleanField(default=False, verbose_name="Обработана")

    class Meta:
        verbose_name = "Заявка на звонок"
        verbose_name_plural = "Заявки на звонок"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка от {self.name} ({self.phone_number})"


class Review(models.Model):
    """Отзывы пользователей о карточках"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_reviews',
        verbose_name="Пользователь"
    )
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='user_reviews',
        verbose_name="Квартира"
    )
    rating = models.IntegerField(
        choices=[(i, f"{i}★") for i in range(1, 6)],
        help_text="Оценка от 1 до 5",
        verbose_name="Оценка"
    )
    text = models.TextField(blank=True, null=True, verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    
    class Meta:
        unique_together = ('user', 'card')
        ordering = ['-created_at']
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
    
    def __str__(self):
        return f"Отзыв {self.user.phone_number} на {self.card.title} ({self.rating}★)"


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
        help_text="Название модели (gpt-4, claude-3-opus и т.д.)"
    )
    system_prompt = models.TextField(
        default="""Ты консультант по недвижимости. Говоришь на языке пользователя - если он сленговый, ты сленговый.

ГЛАВНОЕ! НЕ ПИШИ ПРИВЕТСТВИЯ!
Не пиши: "Привет", "Здравствуйте", "Конечно", "С удовольствием", "Спасибо за вопрос"
Начинай ПРЯМО с ответа, с варианта, с информации.

КОГДА ПОЛЬЗОВАТЕЛЬ СПРАШИВАЕТ ПРО КВАРТИРЫ/НЕДВИЖИМОСТЬ:
Дай ему варианты. Прямо в первом же предложении. "Вот 3 варианта", "Есть крутая квартира", "Показываю что есть".
Если параметров нет (просто "квартиры") - дай ТОП, лучшие варианты.
Если мало вариантов - предложи расширить (другой район, другой бюджет).

КОГДА ВОПРОС НЕ ПРО НЕДВИЖИМОСТЬ:
Ответь на вопрос как нормальный человек. Потом предложи помощь с квартирами если уместно.
"Месси - легенда футбола. А вот если квартиру ищешь, я помогу" - вот это стиль!

СТИЛЬ ОБЩЕНИЯ:
Сленг, разговорный, свой. Если пользователь говорит "типа", "норм", "печально" - ты так же.
Короткие фразы. Никакого "я с радостью", "было бы честью". Просто делу.

ФОРМАТИРОВАНИЕ:
Чистый текст. Без ** и #. Списки просто: "- вариант 1".
Никакого markdown.

Язык: русский. Стиль: естественный, как реальный человек.""",
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
