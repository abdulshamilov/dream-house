from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0013_remove_user_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=50, blank=True, null=True),
        ),
    ]
