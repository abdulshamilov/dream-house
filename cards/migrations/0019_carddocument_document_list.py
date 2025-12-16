# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0018_rename_vh_user_viewed_idx_cards_viewh_user_id_1c293f_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='carddocument',
            name='document_list',
            field=models.ForeignKey(blank=True, help_text='Подборка, к которой относится документ', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='cards.carddocumentlist'),
        ),
        migrations.AlterModelOptions(
            name='carddocument',
            options={'ordering': ['uploaded_at']},
        ),
    ]
