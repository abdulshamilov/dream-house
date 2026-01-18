from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_add_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='loginotp',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
