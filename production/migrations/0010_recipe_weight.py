from decimal import Decimal, ROUND_HALF_UP

from django.db import migrations, models


def recipe_item_grams(quantity, unit):
    qty = Decimal(quantity or 0)
    unit = (unit or "").strip().lower()
    if unit in ("kg", "litre"):
        return qty * Decimal("1000")
    if unit in ("gram", "ml"):
        return qty
    return Decimal("0")


def fill_recipe_weights(apps, schema_editor):
    Recipe = apps.get_model("production", "Recipe")
    RecipeItem = apps.get_model("production", "RecipeItem")
    items_by_recipe = {}
    for item in RecipeItem.objects.filter(status=True).only("recipe_id", "quantity", "unit"):
        items_by_recipe.setdefault(item.recipe_id, []).append(item)
    for recipe in Recipe.objects.all():
        total = Decimal("0")
        for item in items_by_recipe.get(recipe.pk, []):
            total += recipe_item_grams(item.quantity, item.unit)
        recipe.weight = total.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        recipe.save(update_fields=["weight"])


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0009_recipe_unique_per_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="weight",
            field=models.DecimalField(
                decimal_places=3,
                default=0,
                help_text="Total recipe weight in grams",
                max_digits=12,
            ),
        ),
        migrations.RunPython(fill_recipe_weights, migrations.RunPython.noop),
    ]
