from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser
from production.models import Ingredient, Product, Recipe, RecipeItem


BASE_MIX = [
    ("Milk 6% Fat", Decimal("600")),
    ("Sugar Grain", Decimal("105")),
    ("Liquid Glucose", Decimal("30")),
    ("SMP", Decimal("25")),
    ("Celebree Dextrose", Decimal("25")),
    ("Amul Cream 25% Fat", Decimal("180")),
    ("Base 50MB", Decimal("35")),
]

RECIPES = {
    "premium_pistachio": [
        ("100% Sicilian pistachio paste", Decimal("45")),
        ("Natural flavour", Decimal("0.8")),
        ("Crushed Sicilian roasted pistachio", Decimal("12")),
        ("Pistachio cream", Decimal("10")),
        ("White chocolate curls", Decimal("3")),
        ("Fleur de Sel", Decimal("0.3")),
        *BASE_MIX,
    ],
    "premium_caramel": [
        ("Premium French salted caramel paste", Decimal("50")),
        ("Homemade salted caramel sauce", Decimal("30")),
        ("Madagascar vanilla paste", Decimal("2")),
        ("Fleur de Sel", Decimal("1.0")),
        ("Salted caramel drizzle", Decimal("15")),
        ("Honeycomb (cinder toffee) pieces", Decimal("15")),
        ("Belgian milk chocolate curls", Decimal("5")),
        ("Candied pecans", Decimal("10")),
        *BASE_MIX,
    ],
    "premium_chocolate_hazelnut": [
        ("Premium Gianduja paste", Decimal("60")),
        ("70% Belgian dark chocolate", Decimal("30")),
        ("Hazelnut paste", Decimal("20")),
        ("Vanilla paste", Decimal("2")),
        ("Roasted Piemonte hazelnuts", Decimal("15")),
        ("Belgian chocolate curls", Decimal("10")),
        ("Gianduja drizzle", Decimal("15")),
        ("Cocoa nibs", Decimal("5")),
        ("Honeycomb (cinder toffee) pieces", Decimal("15")),
        *BASE_MIX,
    ],
    "peach": [
        ("Peach puree", Decimal("180")),
        ("Lemon juice", Decimal("1")),
        ("Natural peach flavour", Decimal("1")),
        ("White chocolate ganache", Decimal("50")),
        ("Premium honey ribbon", Decimal("30")),
        ("Vanilla bean cream", Decimal("20")),
        ("Fresh peach cubes", Decimal("20")),
        ("Freeze dried peach", Decimal("8")),
        ("White chocolate curls", Decimal("8")),
        ("Edible flower petals", Decimal("1")),
        ("Candied almond crunch", Decimal("10")),
        *BASE_MIX,
    ],
    "vanilla": [
        ("Madagascar vanilla bean paste", Decimal("8")),
        ("Natural vanilla extract", Decimal("2")),
        ("Bourbon vanilla caramel ribbon", Decimal("60")),
        ("White chocolate ganache", Decimal("40")),
        ("White chocolate curls", Decimal("8")),
        ("Caramelized almonds crunch", Decimal("12")),
        ("Madagascar vanilla bean specks", Decimal("1")),
        ("Caramel drizzle", Decimal("10")),
        ("Gold sugar pearls", Decimal("5")),
        *BASE_MIX,
    ],
    "strawberry": [
        ("Strawberry puree", Decimal("180")),
        ("Natural strawberry flavor", Decimal("1")),
        ("Lemon juice", Decimal("2")),
        ("Strawberry compote", Decimal("30")),
        ("Premium strawberry variegato", Decimal("80")),
        ("Freeze-dried strawberry pieces", Decimal("8")),
        ("Fresh strawberry cubes", Decimal("20")),
        ("Belgian white chocolate curls", Decimal("8")),
        ("Strawberry crunch crumble", Decimal("10")),
        ("Edible flower petals", Decimal("1")),
        *BASE_MIX,
    ],
}


class Command(BaseCommand):
    help = "Create remaining gelato flavour recipes with gram recipe items."

    def add_arguments(self, parser):
        parser.add_argument("--business", type=str, default="Goat Creamery")

    def _ingredient(self, business, name):
        return Ingredient.objects.filter(business=business, name__iexact=name).first()

    @transaction.atomic
    def handle(self, *args, **options):
        business = Business.objects.filter(
            name__iexact=options["business"].strip(),
            status=True,
        ).first()
        if not business:
            raise CommandError(f"No active business named '{options['business']}'.")

        admin = (
            BusinessUser.objects.filter(business=business, is_active=True, role="SUPER_ADMIN")
            .select_related("user")
            .first()
        )
        user = admin.user if admin else business.created_by
        created_recipes = 0
        skipped = 0

        for variant, items in RECIPES.items():
            product = Product.objects.filter(
                business=business,
                type="gelato",
                variant=variant,
            ).first()
            if not product:
                raise CommandError(f"Gelato product '{variant}' was not found.")

            recipe, was_created = Recipe.objects.get_or_create(
                business=business,
                product=product,
                defaults={
                    "date": date.today(),
                    "status": "active",
                    "procedure": f"{variant.replace('_', ' ').title()} gelato mix. Quantities in grams.",
                    "created_by": user,
                },
            )
            if not was_created:
                skipped += 1
                continue

            missing = []
            for name, grams in items:
                ingredient = self._ingredient(business, name)
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
            if missing:
                raise CommandError(f"{variant} missing ingredients: " + ", ".join(missing))
            recipe.refresh_weight()
            created_recipes += 1
            self.stdout.write(self.style.SUCCESS(
                f"{product.code_sku} {variant}: {len(items)} items"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"{created_recipes} recipes created, {skipped} already existed."
        ))
