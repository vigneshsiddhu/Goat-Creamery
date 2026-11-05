from calendar import monthrange
from datetime import date, time
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser
from production.models import GoatMilkBatch, Product, ProductBatch, ProductBatchMilk, Recipe


AIR_REDUCTION = Decimal("0.80")
SESSION_TIME = {
    "morning": time(8, 0),
    "evening": time(18, 0),
}


class Command(BaseCommand):
    help = "Create gelato product batches from each milk batch using recipe weight and 80% of recipe cost."

    def add_arguments(self, parser):
        parser.add_argument("--business", type=str, default="Goat Creamery")
        parser.add_argument("--year", type=int, default=2026)
        parser.add_argument("--month", type=int, default=8)

    @transaction.atomic
    def handle(self, *args, **options):
        year = options["year"]
        month = options["month"]
        if month < 1 or month > 12:
            raise CommandError("Month must be between 1 and 12.")

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

        last_day = monthrange(year, month)[1]
        start = date(year, month, 1)
        end = date(year, month, last_day)

        recipes = list(
            Recipe.objects.filter(
                business=business,
                status="active",
                product__type="gelato",
                product__status="active",
            ).select_related("product")
        )
        if not recipes:
            raise CommandError(f"No active gelato recipes on {business.name}.")

        milk_batches = list(
            GoatMilkBatch.objects.filter(
                business=business,
                date__range=(start, end),
            ).order_by("date", "milk_time")
        )
        if not milk_batches:
            raise CommandError(f"No goat milk batches for {business.name} in {start:%B %Y}.")

        created = 0
        skipped = 0
        for milk_batch in milk_batches:
            for recipe in recipes:
                product = recipe.product
                if recipe.weight <= 0:
                    skipped += 1
                    continue
                exists = ProductBatchMilk.objects.filter(
                    goat_milk_batch=milk_batch,
                    product_batch__business=business,
                    product_batch__product=product,
                ).exists()
                if exists:
                    skipped += 1
                    continue
                cost = (recipe.cost * AIR_REDUCTION).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )
                batch = ProductBatch.objects.create(
                    product=product,
                    recipe=recipe,
                    quantity=recipe.weight,
                    unit="gram",
                    date=milk_batch.date,
                    time=SESSION_TIME.get(milk_batch.milk_time),
                    cost=cost,
                    qc_status="passed",
                    status="active",
                    wastage=Decimal("0"),
                    notes="Recipe weight; production cost is recipe cost minus 20% for air.",
                    business=business,
                    created_by=user,
                )
                ProductBatchMilk.objects.create(product_batch=batch, goat_milk_batch=milk_batch)
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created} product batches created, {skipped} skipped on {business.name} "
            f"({len(milk_batches)} milk batches × {len(recipes)} products, {start} to {end})."
        ))
