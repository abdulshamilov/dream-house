# Generated migration for new fields and models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cards', '0016_alter_aiassistant_api_provider'),
    ]

    operations = [
        # 1. Добавить поле list_curations в Card
        migrations.AddField(
            model_name='card',
            name='list_curations',
            field=models.TextField(
                blank=True,
                default='[]',
                help_text='JSON массив ID карточек для подборок (рекомендации, похожие объекты)'
            ),
        ),
        
        # 2. Создать CardDocumentList модель
        migrations.CreateModel(
            name='CardDocumentList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(
                    help_text='Название подборки',
                    max_length=255
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('card', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='document_lists',
                    to='cards.card'
                )),
            ],
            options={
                'verbose_name': 'Подборка документов',
                'verbose_name_plural': 'Подборки документов',
                'ordering': ['name'],
            },
        ),
        
        # 3. Создать ViewHistory модель
        migrations.CreateModel(
            name='ViewHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('duration_seconds', models.PositiveIntegerField(default=0)),
                ('card', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='viewed_by',
                    to='cards.card'
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='view_history',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'verbose_name': 'История просмотров',
                'verbose_name_plural': 'История просмотров',
                'ordering': ['-viewed_at'],
            },
        ),
        
        # 4. Добавить индексы для ViewHistory
        migrations.AddIndex(
            model_name='viewhistory',
            index=models.Index(fields=['user', '-viewed_at'], name='vh_user_viewed_idx'),
        ),
        migrations.AddIndex(
            model_name='viewhistory',
            index=models.Index(fields=['card', '-viewed_at'], name='vh_card_viewed_idx'),
        ),
    ]
