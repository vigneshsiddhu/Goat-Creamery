import calendar
import random
from datetime import date, datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from business.models import Business, BusinessUser, Location
from inventory.models import Item, ItemLocation
from production.models import ProductBatch, ProductPrice


def add_months(value, months):
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


class Command(BaseCommand):
    help = "Create inventory items for every product batch, split between Pondicherry and Coimbatore."

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

        admin = (
            BusinessUser.objects.filter(business=business, is_active=True, role="SUPER_ADMIN")
            .select_related("user")
            .first()
        )
        user = admin.user if admin else business.created_by

        pondy = Location.objects.filter(business=business, name__icontains="pondi").first()
        coimbatore = Location.objects.filter(business=business, name__icontains="coimbat").first()
        if not pondy or not coimbatore:
            raise CommandError(
                "Need Pondicherry and Coimbatore locations. "
                f"Found: {[loc.name for loc in Location.objects.filter(business=business)]}"
            )

        prices = {}
        for price in ProductPrice.objects.filter(business=business, status="active").order_by("-date", "-created_at"):
            prices.setdefault(price.product_id, price)
        if not prices:
            raise CommandError("No active product prices found.")

        batches = list(
            ProductBatch.objects.filter(business=business)
            .select_related("product")
            .order_by("date", "batch_number")
        )
        if not batches:
            raise CommandError("No product batches found.")

        existing = set(
            Item.objects.filter(business=business).values_list("product_batch_id", flat=True)
        )
        pending = [batch for batch in batches if batch.pk not in existing]
        if not pending:
            self.stdout.write(self.style.WARNING("All product batches already have items."))
            return

        rng = random.Random(8)
        rng.shuffle(pending)
        split_at = len(pending) // 2

        created = 0
        skipped = 0
        pondy_count = 0
        coimbatore_count = 0
        tz = timezone.get_current_timezone()

        for index, batch in enumerate(pending):
            price = prices.get(batch.product_id)
            if not price:
                skipped += 1
                continue
            location = pondy if index < split_at else coimbatore
            packed = batch.date
            expiry = add_months(packed, 6) + timedelta(days=rng.randint(-10, 15))
            if expiry <= packed:
                expiry = add_months(packed, 6)
            packed_time = batch.time
            loaded_at = datetime.combine(packed, packed_time or datetime.min.time())
            loaded_at = timezone.make_aware(loaded_at, tz)
            item = Item.objects.create(
                qr_code=f"ITM-{batch.batch_number}",
                product=batch.product,
                product_batch=batch,
                price=price,
                status=True,
                time=packed_time,
                packed_date=packed,
                exp_date=expiry,
                business=business,
                created_by=user,
            )
            ItemLocation.objects.create(
                item=item,
                location=location,
                vehicle=None,
                loaded_at=loaded_at,
                time=packed_time,
                status=True,
                business=business,
                created_by=user,
            )
            created += 1
            if location == pondy:
                pondy_count += 1
            else:
                coimbatore_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created} items created, {skipped} skipped on {business.name} "
            f"(Pondicherry {pondy_count}, Coimbatore {coimbatore_count})."
        ))
