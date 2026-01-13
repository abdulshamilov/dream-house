from django.db import migrations, models
import uuid


def populate_referral_codes(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        if not getattr(user, 'referral_code', None):
            user.referral_code = uuid.uuid4()
            user.save(update_fields=['referral_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_remove_login_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='referral_code',
            field=models.UUIDField(null=True, editable=False, default=None),
        ),
        migrations.RunPython(populate_referral_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='user',
            name='referral_code',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
