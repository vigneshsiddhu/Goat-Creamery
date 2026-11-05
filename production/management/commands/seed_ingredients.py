import random
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser
from production.models import Ingredient, IngredientPrice


INGREDIENTS = [
    ("Milk 6% Fat", 300),
    ("Sugar Grain", 68),
    ("Liquid Glucose", 130),
    ("SMP", 380),
    ("Celebree Dextrose", 130),
    ("Amul Cream 25% Fat", 230),
    ("Base 50MB", 1890),
    ("Mascarpone cheese", 900),
    ("Espresso coffee concentrate", 4000),
    ("Premium tiramisu paste", 1200),
    ("Madagascar vanilla paste", 5000),
    ("Coffee liqueur flavor (non-alcoholic)", 8000),
    ("100% Sicilian pistachio paste", 9000),
    ("Natural flavour", 9000),
    ("Premium French salted caramel paste", 2500),
    ("Homemade salted caramel sauce", 500),
    ("Fleur de Sel", 4000),
    ("Premium Gianduja paste", 3000),
    ("70% Belgian dark chocolate", 1500),
    ("Hazelnut paste", 2000),
    ("Vanilla paste", 5000),
    ("Cocoa powder", 1000),
    ("Crushed Savoiardi (ladyfinger) biscuits", 900),
    ("Belgian dark chocolate curls", 2400),
    ("Mascarpone cream swirl", 1200),
    ("Chocolate-covered coffee beans", 3000),
    ("Crushed Sicilian roasted pistachio", 8000),
    ("Pistachio cream", 4000),
    ("White chocolate curls", 2000),
    ("Salted caramel drizzle", 700),
    ("Honeycomb (cinder toffee) pieces", 1250),
    ("Belgian milk chocolate curls", 2000),
    ("Candied pecans", 2500),
    ("Roasted Piemonte hazelnuts", 3000),
    ("Belgian chocolate curls", 2000),
    ("Gianduja drizzle", 2000),
    ("Cocoa nibs", 3000),
    ("Peach puree", 200),
    ("Lemon juice", 9000),
    ("Natural peach flavour", 8000),
    ("White chocolate ganache", 900),
    ("Premium honey ribbon", 500),
    ("Vanilla bean cream", 900),
    ("Fresh peach cubes", 200),
    ("Freeze dried peach", 5000),
    ("Edible flower petals", 10000),
    ("Candied almond crunch", 1500),
    ("Madagascar vanilla bean paste", 1000),
    ("Natural vanilla extract", 8000),
    ("Bourbon vanilla caramel ribbon", 650),
    ("Madagascar vanilla bean specks", 10000),
    ("Caramel drizzle", 800),
    ("Gold sugar pearls", 1600),
    ("Strawberry puree", 200),
    ("Natural strawberry flavor", 8000),
    ("Strawberry compote", 500),
    ("Premium strawberry variegato", 700),
    ("Freeze-dried strawberry pieces", 5000),
    ("Fresh strawberry cubes", 250),
    ("Belgian white chocolate curls", 2000),
    ("Strawberry crunch crumble", 1000),
    ("Caramelized almonds crunch", 1500),
]


def unique_ingredients():
    seen = {}
    for name, price_per_kg in INGREDIENTS:
        key = " ".join(name.strip().split()).title()
        if key not in seen:
            seen[key] = Decimal(str(price_per_kg))
    return seen


class Command(BaseCommand):
    help = "Seed unique gelato ingredients with 10–15 kg stock and MRP from per-kg price."

    def add_arguments(self, parser):
        parser.add_argument("--business", type=str, default="Goat Creamery")

    @transaction.atomic
    def handle(self, *args, **options):
        business_name = options["business"].strip()
        business = Business.objects.filter(name__iexact=business_name, status=True).first()
        if not business:
            raise CommandError(f"No active business named '{business_name}'.")

        admin = (
            BusinessUser.objects.filter(business=business, is_active=True, role="SUPER_ADMIN")
            .select_related("user")
            .first()
        )
        user = admin.user if admin else business.created_by
        today = date.today()
        rng = random.Random(42)
        created = 0
        skipped = 0

        for name, price_per_kg in unique_ingredients().items():
            if Ingredient.objects.filter(business=business, name__iexact=name).exists():
                skipped += 1
                continue
            quantity = Decimal(str(rng.randint(10, 15)))
            mrp = (quantity * price_per_kg).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            gst = Decimal("5.00")
            ingredient = Ingredient(
                name=name,
                business=business,
                created_by=user,
            )
            ingredient.save()
            IngredientPrice.objects.create(
                ingredient=ingredient,
                quantity=quantity,
                unit="kg",
                mrp=mrp,
                gst=gst,
                date=today,
                status="active",
                stock=quantity,
                stock_price=mrp,
                business=business,
                created_by=user,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created} ingredients created, {skipped} already existed on {business.name} "
            f"(10–15 kg, MRP = qty × per-kg price, GST 5%, date {today})."
        ))
