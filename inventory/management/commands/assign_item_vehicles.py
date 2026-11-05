import random

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, Location
from inventory.models import ItemLocation, Vehicle


PAIRS = [
    ("pondi", "PY 01 GC 1001"),
    ("coimbat", "TN 37 GC 2001"),
]


class Command(BaseCommand):
    help = "Assign each city van to 50% of item locations in that city."

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

        rng = random.Random(50)
        updated = 0

        for loc_match, number in PAIRS:
            location = Location.objects.filter(business=business, name__icontains=loc_match).first()
            vehicle = Vehicle.objects.filter(business=business, number=number).first()
            if not location or not vehicle:
                raise CommandError(f"Missing location or vehicle for {loc_match} / {number}.")

            rows = list(
                ItemLocation.objects.filter(
                    business=business,
                    status=True,
                    location=location,
                )
            )
            rng.shuffle(rows)
            take = len(rows) // 2
            for row in rows[:take]:
                row.vehicle = vehicle
                row.save(update_fields=["vehicle", "updated_at"])
                updated += 1
            self.stdout.write(f"{location.name}: {take}/{len(rows)} items → {vehicle.number}")

        self.stdout.write(self.style.SUCCESS(
            f"{updated} item locations mapped to vehicles on {business.name}."
        ))
