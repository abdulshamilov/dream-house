# Generated placeholder to match production
from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_alter_notification_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('push_enabled', models.BooleanField(default=True)),
                ('email_enabled', models.BooleanField(default=False)),
                ('new_cards', models.BooleanField(default=True)),
                ('price_changes', models.BooleanField(default=True)),
                ('subscription_updates', models.BooleanField(default=True)),
                ('promotions', models.BooleanField(default=True)),
                ('user', models.OneToOneField(on_delete=models.deletion.CASCADE, related_name='notification_settings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Настройки уведомлений',
                'verbose_name_plural': 'Настройки уведомлений',
            },
        ),
    ]
