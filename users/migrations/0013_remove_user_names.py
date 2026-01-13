from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0012_user_dad_name_user_first_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='dad_name',
        ),
    ]
