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
