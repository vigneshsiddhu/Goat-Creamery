from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0013_remove_productbatch_goat_milk_batch"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="productbatchmilk",
            name="unique_milk_batch_per_product_batch",
        ),
    ]
