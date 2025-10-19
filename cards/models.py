from django.db import models
from django.conf import settings

class Card(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CardImage(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='cards/')

    def __str__(self):
        return f"{self.card.title} Image"
