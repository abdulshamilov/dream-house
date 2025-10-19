from django.db import models
from django.conf import settings

class Card(models.Model):
    HOUSE_TYPE_CHOICES = (
        ('private', 'Частный дом'),
        ('apartment', 'Квартира'),
    )
    CITY_CHOICES = (
        ('Махачкала', 'Махачкала'),
        ('Каспийск', 'Каспийск'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    rooms = models.PositiveIntegerField(default=1)
    city = models.CharField(
        max_length=255,
        choices=CITY_CHOICES,
        default='Махачкала'
    )
    house_type = models.CharField(
        max_length=50,
        choices=HOUSE_TYPE_CHOICES,
        default='apartment'
    )

    # Поля рейтинга
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # 0.00 - 5.00
    rating_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CardImage(models.Model):
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='cards/img/')

    def __str__(self):
        return f"{self.card.title} Image"
