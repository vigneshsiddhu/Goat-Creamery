from django.db import migrations, models


def populate_recipe_type_and_dedupe(apps, schema_editor):
    Recipe = apps.get_model("production", "Recipe")
    kept_by_key = {}
    delete_ids = []
    for recipe in Recipe.objects.select_related("product").order_by(
        "business_id", "product__type", "-date", "-created_at"
    ):
        recipe.type = recipe.product.type
        key = (recipe.business_id, recipe.type)
        if key in kept_by_key:
            delete_ids.append(recipe.pk)
        else:
            kept_by_key[key] = recipe.pk
            recipe.save(update_fields=["type"])
    if delete_ids:
        Recipe.objects.filter(pk__in=delete_ids).delete()


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("production", "0005_recipeitem_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="type",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.RunPython(populate_recipe_type_and_dedupe, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="recipe",
            name="type",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="status",
            field=models.CharField(
                choices=[("active", "Active"), ("inactive", "Inactive")],
                default="active",
                max_length=20,
            ),
        ),
        migrations.AddConstraint(
            model_name="recipe",
            constraint=models.UniqueConstraint(
                fields=("business", "type"),
                name="unique_recipe_per_product_type",
            ),
        ),
    ]
