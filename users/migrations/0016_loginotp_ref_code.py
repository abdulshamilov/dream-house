from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_loginotp_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='loginotp',
            name='ref_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
