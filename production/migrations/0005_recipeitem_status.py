from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0004_ingredient_unique_name_per_business"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipeitem",
            name="status",
            field=models.BooleanField(default=True),
        ),
    ]
