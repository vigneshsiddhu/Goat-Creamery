import calendar
import random
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser
from goats.models import Goat
from production.models import GoatMilk


class Command(BaseCommand):
    help = "Seed morning and evening milk for GC-F goats for the previous calendar month."

    def add_arguments(self, parser):
        parser.add_argument("--business", type=str, default="Goat Creamery")
        parser.add_argument("--prefix", type=str, default="GC-F")
        parser.add_argument("--count", type=int, default=25)
        parser.add_argument("--year", type=int, default=2026)
        parser.add_argument(
            "--months",
            type=str,
            default="",
            help="Comma-separated month numbers, e.g. 6,7 for June and July.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        business_name = options["business"].strip()
        prefix = options["prefix"].strip() or "GC-F"
        count = options["count"]

        business = Business.objects.filter(name__iexact=business_name, status=True).first()
        if not business:
            raise CommandError(f"No active business named '{business_name}'.")

        user = (
            BusinessUser.objects.filter(
                business=business,
                is_active=True,
                role="SUPER_ADMIN",
            )
            .select_related("user")
            .first()
        )
        user = user.user if user else business.created_by

        goats = list(
            Goat.objects.filter(
                business=business,
                token_no__in=[f"{prefix}-{i:03d}" for i in range(1, count + 1)],
            ).order_by("token_no")
        )
        if len(goats) != count:
            raise CommandError(
                f"Expected {count} goats with prefix {prefix} on {business.name}, found {len(goats)}."
            )

        today = date.today()
        year = options["year"]
        months_arg = (options["months"] or "").strip()
        if months_arg:
            months = [int(part) for part in months_arg.split(",") if part.strip()]
        else:
            months = [today.month - 1 if today.month > 1 else 12]
            if months[0] == 12:
                year = today.year - 1
        if any(month < 1 or month > 12 for month in months):
            raise CommandError("Months must be between 1 and 12.")

        days = []
        for month in months:
            last_day = calendar.monthrange(year, month)[1]
            days.extend(date(year, month, day) for day in range(1, last_day + 1))

        rng = random.Random(25)
        records = []
        for goat in goats:
            for milk_date in days:
                for session in (GoatMilk.MilkingTime.MORNING, GoatMilk.MilkingTime.EVENING):
                    litres = Decimal(str(rng.uniform(1.0, 2.0))).quantize(
                        Decimal("0.1"),
                        rounding=ROUND_HALF_UP,
                    )
                    if litres < Decimal("1.0"):
                        litres = Decimal("1.0")
                    if litres > Decimal("2.0"):
                        litres = Decimal("2.0")
                    records.append(
                        GoatMilk(
                            goat=goat,
                            user=user,
                            business=business,
                            milk_weight=litres,
                            date=milk_date,
                            time=session,
                            note="seed",
                            created_by=user,
                        )
                    )

        GoatMilk.objects.bulk_create(records, ignore_conflicts=True, batch_size=500)
        saved = GoatMilk.objects.filter(
            business=business,
            goat__in=goats,
            date__range=(days[0], days[-1]),
            note="seed",
        ).count()
        self.stdout.write(self.style.SUCCESS(
            f"{saved} milk records for {len(goats)} goats on {business.name} "
            f"({days[0]} to {days[-1]}, morning + evening, 1.0–2.0 L)."
        ))
