from datetime import date, time
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser, Location
from inventory.models import Vehicle, VehicleLocation


VEHICLES = [
    {
        "match": "pondi",
        "number": "PY 01 GC 1001",
        "name": "Pondicherry Van",
        "comment": "Based in Pondicherry",
    },
    {
        "match": "coimbat",
        "number": "TN 37 GC 2001",
        "name": "Coimbatore Van",
        "comment": "Based in Coimbatore",
    },
]


class Command(BaseCommand):
    help = "Create one delivery van for Pondicherry and one for Coimbatore."

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
        created = 0
        skipped = 0

        for spec in VEHICLES:
            location = Location.objects.filter(business=business, name__icontains=spec["match"]).first()
            if not location:
                raise CommandError(f"No location matching '{spec['match']}' on {business.name}.")
            if Vehicle.objects.filter(business=business, number=spec["number"]).exists():
                skipped += 1
                continue
            vehicle = Vehicle.objects.create(
                number=spec["number"],
                name=spec["name"],
                vehicle_type="van",
                unit="kg",
                capacity=Decimal("500.00"),
                status="active",
                business=business,
                created_by=user,
            )
            VehicleLocation.objects.create(
                vehicle=vehicle,
                location=location,
                date=date(2026, 8, 1),
                time=time(8, 0),
                status=True,
                comment=spec["comment"],
                business=business,
                created_by=user,
            )
            created += 1
            self.stdout.write(f"{vehicle.number} → {location.name}")

        self.stdout.write(self.style.SUCCESS(
            f"{created} vehicles created, {skipped} already existed on {business.name}."
        ))
