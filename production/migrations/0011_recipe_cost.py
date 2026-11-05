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


def quantity_in_unit(quantity, from_unit, to_unit):
    source_grams = recipe_item_grams(quantity, from_unit)
    target_grams = recipe_item_grams(Decimal("1"), to_unit)
    if target_grams <= 0:
        return Decimal("0")
    return source_grams / target_grams


def fill_recipe_costs(apps, schema_editor):
    Recipe = apps.get_model("production", "Recipe")
    RecipeItem = apps.get_model("production", "RecipeItem")
    IngredientPrice = apps.get_model("production", "IngredientPrice")

    prices_by_ingredient = {}
    for price in IngredientPrice.objects.order_by("-date", "-created_at"):
        prices_by_ingredient.setdefault(price.ingredient_id, []).append(price)

    items_by_recipe = {}
    for item in RecipeItem.objects.filter(status=True).only(
        "recipe_id", "ingredient_id", "quantity", "unit"
    ):
        items_by_recipe.setdefault(item.recipe_id, []).append(item)

    for recipe in Recipe.objects.all():
        cost = Decimal("0")
        for item in items_by_recipe.get(recipe.pk, []):
            prices = prices_by_ingredient.get(item.ingredient_id, [])
            price = next((row for row in prices if row.status == "active"), None)
            if price is None and prices:
                price = prices[0]
            if not price or not price.quantity or price.quantity <= 0:
                continue
            qty = quantity_in_unit(item.quantity, item.unit, price.unit)
            cost += qty * (price.mrp / price.quantity)
        recipe.cost = cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        recipe.save(update_fields=["cost"])


class Migration(migrations.Migration):

    dependencies = [
        ("production", "0010_recipe_weight"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="cost",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Total recipe cost from ingredient prices",
                max_digits=14,
            ),
        ),
        migrations.RunPython(fill_recipe_costs, migrations.RunPython.noop),
    ]
