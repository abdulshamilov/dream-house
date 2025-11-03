# developers/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Developer(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='developers_created'
    )
    logo = models.ImageField(upload_to='developers/logos/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    developer = models.ForeignKey(
        'Developer',  # строка вместо прямого импорта
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'developer')  # нельзя подписаться дважды

    def __str__(self):
        return f"{self.user} → {self.developer}"
