from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0008_remove_product_goat_milk_batch"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="recipe",
            name="unique_recipe_per_product_type",
        ),
        migrations.AddConstraint(
            model_name="recipe",
            constraint=models.UniqueConstraint(
                fields=("business", "product"),
                name="unique_recipe_per_product",
            ),
        ),
    ]
