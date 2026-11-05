from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser
from production.models import Ingredient, Product, Recipe, RecipeItem


RECIPE_ITEMS = [
    ("Mascarpone cheese", Decimal("80")),
    ("Espresso coffee concentrate", Decimal("20")),
    ("Premium tiramisu paste", Decimal("40")),
    ("Madagascar vanilla paste", Decimal("2")),
    ("Coffee liqueur flavor (non-alcoholic)", Decimal("1")),
    ("Cocoa powder", Decimal("5")),
    ("Crushed Savoiardi (ladyfinger) biscuits", Decimal("20")),
    ("Belgian dark chocolate curls", Decimal("5")),
    ("Mascarpone cream swirl", Decimal("15")),
    ("Chocolate-covered coffee beans", Decimal("5")),
    ("Milk 6% Fat", Decimal("600")),
    ("Sugar Grain", Decimal("105")),
    ("Liquid Glucose", Decimal("30")),
    ("SMP", Decimal("25")),
    ("Celebree Dextrose", Decimal("25")),
    ("Amul Cream 25% Fat", Decimal("180")),
    ("Base 50MB", Decimal("35")),
]


class Command(BaseCommand):
    help = "Create Premium Tiramisu gelato recipe with gram quantities."

    def add_arguments(self, parser):
        parser.add_argument("--business", type=str, default="Goat Creamery")

    @transaction.atomic
    def handle(self, *args, **options):
        business = Business.objects.filter(
            name__iexact=options["business"].strip(),
            status=True,
        ).first()
        if not business:
            raise CommandError(f"No active business named '{options['business']}'.")

        product = Product.objects.filter(
            business=business,
            type="gelato",
            variant="premium_tiramisu",
        ).first()
        if not product:
            raise CommandError("Gelato product Premium Tiramisu was not found.")

        admin = (
            BusinessUser.objects.filter(business=business, is_active=True, role="SUPER_ADMIN")
            .select_related("user")
            .first()
        )
        user = admin.user if admin else business.created_by

        recipe, created = Recipe.objects.get_or_create(
            business=business,
            product=product,
            defaults={
                "date": date.today(),
                "status": "active",
                "procedure": "Premium Tiramisu gelato mix. Quantities in grams.",
                "created_by": user,
            },
        )
        if not created:
            raise CommandError("A recipe already exists for Premium Tiramisu.")

        missing = []
        created_items = 0
        for name, grams in RECIPE_ITEMS:
            ingredient = Ingredient.objects.filter(business=business, name__iexact=name).first()
            if not ingredient:
                missing.append(name)
                continue
            RecipeItem.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                unit="gram",
                quantity=grams,
                status=True,
                business=business,
                created_by=user,
            )
            created_items += 1

        if missing:
            raise CommandError("Missing ingredients: " + ", ".join(missing))

        recipe.refresh_weight()
        self.stdout.write(self.style.SUCCESS(
            f"Recipe created for {product.code_sku} Premium Tiramisu with {created_items} items, {recipe.weight} g."
        ))
