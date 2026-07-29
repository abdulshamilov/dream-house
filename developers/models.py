# developers/models.py
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Developer(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, default='92-62-66', verbose_name='Телефон')
    logo = models.ImageField(upload_to='developers/logos/', null=True, blank=True)
    avatar_override = models.ImageField(
        upload_to='developers/avatars/', null=True, blank=True,
        verbose_name='Аватар (вручную)',
        help_text=(
            'Если задано — используется на выдаче вместо автоматического фото '
            'с объектов. Если пусто — аватар берётся автоматически: первое фото '
            'первой карточки застройщика.'
        ),
    )

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
