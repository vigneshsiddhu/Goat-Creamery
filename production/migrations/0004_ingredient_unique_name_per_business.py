from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0003_productbatch_unit_alter_ingredientprice_unit_and_more"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="ingredient",
            constraint=models.UniqueConstraint(
                fields=["business", "name"],
                name="unique_ingredient_name_per_business",
            ),
        ),
    ]
