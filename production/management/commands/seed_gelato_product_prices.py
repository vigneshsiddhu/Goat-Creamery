from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser
from production.models import Product, ProductPrice


PRICES = [
    ("GEL-002", "premium_pistachio", Decimal("140"), Decimal("80")),
    ("GEL-003", "premium_caramel", Decimal("120"), Decimal("80")),
    ("GEL-004", "premium_chocolate_hazelnut", Decimal("120"), Decimal("80")),
    ("GEL-005", "strawberry", Decimal("100"), Decimal("80")),
    ("GEL-006", "vanilla", Decimal("90"), Decimal("80")),
    ("GEL-007", "peach", Decimal("90"), Decimal("80")),
    ("GEL-001", "premium_tiramisu", Decimal("120"), Decimal("80")),
]


class Command(BaseCommand):
    help = "Create 80 g gelato product prices (MRP) for Goat Creamery flavours."

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
        today = date.today()
        created = 0
        skipped = 0

        for sku, variant, mrp, quantity in PRICES:
            product = Product.objects.filter(
                business=business,
                type="gelato",
                variant=variant,
            ).first()
            if product is None:
                product = Product.objects.filter(business=business, code_sku=sku).first()
            if product is None:
                raise CommandError(f"Product {sku} ({variant}) was not found.")

            already = ProductPrice.objects.filter(
                business=business,
                product=product,
                quantity=quantity,
                unit="gram",
                mrp=mrp,
                status="active",
            ).exists()
            if already:
                skipped += 1
                continue

            ProductPrice.objects.filter(
                business=business,
                product=product,
                status="active",
            ).update(status="inactive")

            ProductPrice.objects.create(
                product=product,
                mrp=mrp,
                gst=Decimal("5.00"),
                date=today,
                quantity=quantity,
                unit="gram",
                status="active",
                business=business,
                created_by=user,
            )
            created += 1
            self.stdout.write(f"{product.code_sku} {variant}: ₹{mrp} / {quantity} g")

        self.stdout.write(self.style.SUCCESS(
            f"{created} product prices created, {skipped} already existed on {business.name}."
        ))
