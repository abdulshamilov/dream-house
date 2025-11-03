from django.db import models
from cards.models import Card

class Document(models.Model):
    card = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    title = models.CharField(max_length=255, help_text="Название документа")
    file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)  # 🔹 добавляем поле

    def __str__(self):
        return f"{self.card.title} - {self.title}"
