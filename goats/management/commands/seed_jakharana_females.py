from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business
from goats.models import Goat


class Command(BaseCommand):
    help = "Create dummy live Jakharana female goats for flow testing."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=25)
        parser.add_argument(
            "--business",
            type=str,
            default="",
            help="Business name. Defaults to the first active business.",
        )
        parser.add_argument(
            "--prefix",
            type=str,
            default="JK-F",
            help="Token number prefix, e.g. JK-F-001",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        prefix = options["prefix"].strip() or "JK-F"
        if count < 1:
            raise CommandError("Count must be at least 1.")

        business = self._get_business(options["business"])
        user = business.created_by
        created = 0
        updated = 0
        today = date.today()

        for i in range(1, count + 1):
            is_kid = i > count - 3
            if is_kid:
                age_years = 0
                dob = today - timedelta(days=90 + (i * 7) % 240)
                maturity = "KID"
            else:
                age_years = 1 + ((i - 1) % 5)
                dob = today - timedelta(days=age_years * 365 + (i * 11) % 60)
                maturity = "ADULT"

            goat, was_created = Goat.objects.update_or_create(
                token_no=f"{prefix}-{i:03d}",
                defaults={
                    "rfid": f"RFID-{prefix}-{i:03d}",
                    "breed_variety": "Jakharana",
                    "dob": dob,
                    "age": age_years,
                    "live": True,
                    "gender": "FEMALE",
                    "maturity": maturity,
                    "created_by": user,
                    "business": business,
                },
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created} created, {updated} updated for {business.name} "
            f"({count} Jakharana females, tokens {prefix}-001 to {prefix}-{count:03d})."
        ))

    def _get_business(self, name):
        qs = Business.objects.filter(status=True).order_by("created_at")
        if name:
            business = qs.filter(name__iexact=name.strip()).first()
            if not business:
                raise CommandError(f"No active business named '{name}'.")
            return business
        business = qs.first()
        if not business:
            raise CommandError("No active business found. Create a business first.")
        return business
