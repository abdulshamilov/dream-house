# Generated manually to align notifications API with new fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
        ("cards", "0030_promotion_promotionitem"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="title",
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notification",
            name="message",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="type",
            field=models.CharField(choices=[
                ("price_drop", "Price drop"),
                ("sale", "Sale"),
                ("discount", "Discount"),
                ("subscription", "Subscription"),
                ("new", "New"),
                ("system", "System"),
            ], max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="notification",
            name="card",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="notifications",
                to="cards.card",
            ),
        ),
        migrations.AddField(
            model_name="notification",
            name="old_price",
            field=models.DecimalField(
                blank=True,
                null=True,
                max_digits=12,
                decimal_places=2,
                help_text="Previous price before discount",
            ),
        ),
    ]
