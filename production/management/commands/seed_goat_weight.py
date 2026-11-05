import calendar
import random
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser
from goats.models import Goat
from production.models import GoatWeight


class Command(BaseCommand):
    help = "Seed one weight record per month for the last 3 months for GC-F goats."

    def add_arguments(self, parser):
        parser.add_argument("--business", type=str, default="Goat Creamery")
        parser.add_argument("--prefix", type=str, default="GC-F")
        parser.add_argument("--count", type=int, default=25)

    @transaction.atomic
    def handle(self, *args, **options):
        business_name = options["business"].strip()
        prefix = options["prefix"].strip() or "GC-F"
        count = options["count"]

        business = Business.objects.filter(name__iexact=business_name, status=True).first()
        if not business:
            raise CommandError(f"No active business named '{business_name}'.")

        admin = (
            BusinessUser.objects.filter(
                business=business,
                is_active=True,
                role="SUPER_ADMIN",
            )
            .select_related("user")
            .first()
        )
        user = admin.user if admin else business.created_by

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
        months = []
        year, month = today.year, today.month
        for _ in range(3):
            month -= 1
            if month == 0:
                month = 12
                year -= 1
            months.append((year, month))
        months.reverse()

        weigh_dates = []
        for year, month in months:
            day = min(15, calendar.monthrange(year, month)[1])
            weigh_dates.append(date(year, month, day))

        rng = random.Random(35)
        records = []
        for goat in goats:
            weight = Decimal("35.0") + Decimal(str(rng.uniform(-1.5, 1.5))).quantize(
                Decimal("0.1"),
                rounding=ROUND_HALF_UP,
            )
            for weigh_date in weigh_dates:
                records.append(
                    GoatWeight(
                        goat=goat,
                        user=user,
                        business=business,
                        weight=weight,
                        date=weigh_date,
                        note="seed",
                        created_by=user,
                    )
                )
                gain = Decimal(str(rng.uniform(3.0, 4.0))).quantize(
                    Decimal("0.1"),
                    rounding=ROUND_HALF_UP,
                )
                weight = (weight + gain).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

        GoatWeight.objects.bulk_create(records, ignore_conflicts=True, batch_size=200)
        saved = GoatWeight.objects.filter(
            business=business,
            goat__in=goats,
            date__in=weigh_dates,
            note="seed",
        ).count()
        labels = ", ".join(d.strftime("%b %Y") for d in weigh_dates)
        self.stdout.write(self.style.SUCCESS(
            f"{saved} weight records for {len(goats)} goats on {business.name} "
            f"(1 per goat per month: {labels}; start ~35 kg, +3–4 kg/month)."
        ))
