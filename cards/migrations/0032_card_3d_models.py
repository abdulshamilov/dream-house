import django.core.validators
from django.db import migrations, models

import cards.models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0031_remove_card_building_material_card_complex_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='model_3d_glb',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='apartments/3d/glb/%Y/%m/',
                validators=[
                    django.core.validators.FileExtensionValidator(['glb']),
                    cards.models.validate_file_size_10mb,
                ],
                verbose_name='3D модель (.glb)',
            ),
        ),
        migrations.AddField(
            model_name='card',
            name='model_3d_usdz',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='apartments/3d/usdz/%Y/%m/',
                validators=[
                    django.core.validators.FileExtensionValidator(['usdz']),
                ],
                verbose_name='3D модель AR (.usdz)',
            ),
        ),
        migrations.AddField(
            model_name='card',
            name='model_3d_poster',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='apartments/3d/posters/%Y/%m/',
                verbose_name='Постер 3D модели',
            ),
        ),
    ]
