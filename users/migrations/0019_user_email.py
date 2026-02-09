# Generated migration for adding email field to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_referral_reward_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='email',
            field=models.EmailField(
                blank=True,
                help_text='Email для уведомлений (опционально)',
                max_length=255,
                null=True,
            ),
        ),
    ]
