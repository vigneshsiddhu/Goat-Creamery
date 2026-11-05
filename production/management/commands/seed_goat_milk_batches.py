from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Count, Sum

from business.models import Business, BusinessUser
from production.models import GoatMilk, GoatMilkBatch


class Command(BaseCommand):
    help = "Create morning and evening goat milk batches from daily goat milk totals."

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

        totals = (
            GoatMilk.objects.filter(business=business, date__range=(start, end))
            .values("date", "time")
            .annotate(total=Sum("milk_weight"), goat_count=Count("goat", distinct=True))
            .order_by("date", "time")
        )
        if not totals:
            raise CommandError(
                f"No goat milk records for {business.name} in {start:%B %Y}."
            )

        created = 0
        skipped = 0
        for row in totals:
            milk_date = row["date"]
            milk_time = row["time"]
            quantity = (row["total"] or Decimal("0")).quantize(
                Decimal("0.01"),
                rounding=ROUND_HALF_UP,
            )
            if quantity <= 0:
                skipped += 1
                continue
            exists = GoatMilkBatch.objects.filter(
                business=business,
                date=milk_date,
                milk_time=milk_time,
            ).exists()
            if exists:
                skipped += 1
                continue
            GoatMilkBatch.objects.create(
                date=milk_date,
                milk_time=milk_time,
                milk_quantity=quantity,
                wastage=Decimal("0.00"),
                status="collected",
                business=business,
                created_by=user,
            )
            created += 1
            self.stdout.write(
                f"{milk_date} {milk_time}: {quantity} L from {row['goat_count']} goats"
            )

        self.stdout.write(self.style.SUCCESS(
            f"{created} milk batches created, {skipped} skipped on {business.name} "
            f"({start} to {end})."
        ))
