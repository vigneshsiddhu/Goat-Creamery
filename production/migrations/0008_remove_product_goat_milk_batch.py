from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0007_product_unique_type_variant"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="goat_milk_batch",
        ),
    ]
