from django.db import models


class Manager(models.Model):
    name = models.CharField(max_length=150, verbose_name='Имя')
    telegram_id = models.BigIntegerField(unique=True, db_index=True, verbose_name='Telegram ID')
    telegram_username = models.CharField(max_length=100, blank=True, verbose_name='@username')
    is_admin = models.BooleanField(default=False, verbose_name='Руководитель')
    active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Менеджер'
        verbose_name_plural = 'Менеджеры'

    def __str__(self):
        return self.name


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('assigned', 'Назначена'),
        ('in_work', 'В работе'),
        ('meeting', 'Встреча/показ'),
        ('deal', 'Сделка'),
        ('rejected', 'Отказ'),
    ]

    name = models.CharField(max_length=200, verbose_name='Имя')
    phone = models.CharField(max_length=20, db_index=True, verbose_name='Телефон')
    jk = models.CharField(max_length=200, blank=True, verbose_name='ЖК / объект')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='new', db_index=True, verbose_name='Статус',
    )
    assigned_to = models.ForeignKey(
        Manager, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='leads',
        verbose_name='Менеджер',
    )
    source = models.CharField(max_length=50, default='site_form', verbose_name='Источник')
    raw_data = models.JSONField(default=dict, blank=True, verbose_name='Сырые данные')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Создана')
    assigned_at = models.DateTimeField(null=True, blank=True, verbose_name='Назначена')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='Закрыта')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'{self.name} ({self.phone}) — {self.get_status_display()}'


class LeadHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Создана'),
        ('assigned', 'Назначена'),
        ('reassigned', 'Переназначена'),
        ('status_changed', 'Смена статуса'),
        ('comment', 'Комментарий'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='history')
    manager = models.ForeignKey(
        Manager, null=True, blank=True, on_delete=models.SET_NULL,
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'История заявки'
        verbose_name_plural = 'История заявок'

    def __str__(self):
        return f'{self.lead} — {self.get_action_display()}'
