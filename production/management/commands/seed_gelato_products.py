from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser
from production.models import Product


VARIANTS = [
    ("premium_tiramisu", "Premium Tiramisu"),
    ("premium_pistachio", "Premium Pistachio"),
    ("premium_caramel", "Premium Caramel"),
    ("premium_chocolate_hazelnut", "Premium Chocolate Hazelnut"),
    ("strawberry", "Strawberry"),
    ("vanilla", "Vanilla"),
    ("peach", "Peach"),
]


class Command(BaseCommand):
    help = "Create gelato products for the listed flavours."

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

        for slug, label in VARIANTS:
            exists = Product.objects.filter(
                business=business,
                type="gelato",
                variant=slug,
            ).exists()
            if exists:
                skipped += 1
                continue
            Product.objects.create(
                type="gelato",
                variant=slug,
                storage_type="frozen",
                storage_temp_min=Decimal("-18.00"),
                storage_temp_max=Decimal("-12.00"),
                status="active",
                description=f"{label} gelato",
                life_span_value=6,
                life_span_unit="month",
                business=business,
                created_by=user,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created} gelato products created, {skipped} already existed on {business.name}."
        ))
