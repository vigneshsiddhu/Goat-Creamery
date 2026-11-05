import random
from calendar import monthrange
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from business.models import Business, BusinessUser
from inventory.models import Item, ItemLocation
from inventory.utils import mark_item_unloaded_on_invoice
from sales.models import Customer, Invoice, InvoiceItem, InvoiceLocation
from sales.utils import apply_item_pricing, calculate_invoice_totals


WEEKDAY_WEIGHT = {
    0: 10,  # Mon
    1: 11,
    2: 12,
    3: 13,  # Thu
    4: 26,  # Fri
    5: 34,  # Sat
    6: 28,  # Sun
}

CUSTOMERS = [
    ("Priya Kumar", "9876501001", "female", 32),
    ("Arun Raj", "9876501002", "male", 41),
    ("Meena Devi", "9876501003", "female", 28),
    ("Suresh Babu", "9876501004", "male", 36),
    ("Lakshmi N", "9876501005", "female", 45),
]


def allocate_counts(days, total, rng):
    weights = []
    for day in days:
        base = WEEKDAY_WEIGHT[day.weekday()]
        jitter = rng.uniform(0.7, 1.35)
        weights.append(max(1, base * jitter))
    total_weight = sum(weights)
    counts = [max(1, int(round(total * w / total_weight))) for w in weights]
    diff = total - sum(counts)
    weekend_indexes = [i for i, day in enumerate(days) if day.weekday() >= 4]
    cursor = 0
    while diff != 0 and weekend_indexes:
        idx = weekend_indexes[cursor % len(weekend_indexes)]
        if diff > 0:
            counts[idx] += 1
            diff -= 1
        elif counts[idx] > 1:
            counts[idx] -= 1
            diff += 1
        cursor += 1
        if cursor > 200:
            break
    return counts


def split_into_invoices(items, day, rng):
    if not items:
        return []
    weekend = day.weekday() >= 4
    max_groups = min(len(items), rng.randint(5, 9) if weekend else rng.randint(2, 4))
    groups = [[] for _ in range(max_groups)]
    shuffled = list(items)
    rng.shuffle(shuffled)
    for index, item in enumerate(shuffled):
        groups[index % max_groups].append(item)
    return [group for group in groups if group]


class Command(BaseCommand):
    help = "Seed August invoices using 50% of items, with heavier Fri–Sun sales."

    def add_arguments(self, parser):
        parser.add_argument("--business", type=str, default="Goat Creamery")
        parser.add_argument("--year", type=int, default=2026)
        parser.add_argument("--month", type=int, default=8)

    @transaction.atomic
    def handle(self, *args, **options):
        year = options["year"]
        month = options["month"]
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
        rng = random.Random(808)

        last_day = monthrange(year, month)[1]
        days = [date(year, month, day) for day in range(1, last_day + 1)]

        customers = []
        for name, number, gender, age in CUSTOMERS:
            customer, _ = Customer.objects.get_or_create(
                business=business,
                number=number,
                defaults={
                    "name": name,
                    "gender": gender,
                    "age": age,
                    "created_by": user,
                },
            )
            customers.append(customer)

        sold_ids = set(
            InvoiceItem.objects.filter(business=business).values_list("item_id", flat=True)
        )
        items = list(
            Item.objects.filter(business=business, status=True)
            .exclude(pk__in=sold_ids)
            .select_related("product", "price", "product_batch")
            .prefetch_related("vehicle_assignments__location", "vehicle_assignments__vehicle")
        )
        if not items:
            raise CommandError("No unsold items available to invoice.")

        rng.shuffle(items)
        pool = items[: len(items) // 2]
        counts = allocate_counts(days, len(pool), rng)

        remaining = list(pool)
        remaining.sort(key=lambda item: (item.packed_date, item.qr_code or ""))
        day_items = {day: [] for day in days}

        for day, target in zip(days, counts):
            available = [item for item in remaining if item.packed_date <= day]
            take = min(target, len(available))
            chosen = available[:take]
            chosen_ids = {item.pk for item in chosen}
            remaining = [item for item in remaining if item.pk not in chosen_ids]
            day_items[day].extend(chosen)

        leftover = [item for item in remaining if item.packed_date <= days[-1]]
        weekend_days = [day for day in days if day.weekday() >= 4]
        cursor = 0
        for item in leftover:
            eligible = [day for day in weekend_days if item.packed_date <= day] or [
                day for day in days if item.packed_date <= day
            ]
            if not eligible:
                continue
            day = eligible[cursor % len(eligible)]
            day_items[day].append(item)
            cursor += 1

        invoices_created = 0
        lines_created = 0
        methods = ["cash", "cash", "upi", "upi", "card"]

        for day in days:
            groups = split_into_invoices(day_items[day], day, rng)
            for group in groups:
                hour = rng.randint(16, 21) if day.weekday() >= 4 else rng.randint(11, 19)
                minute = rng.choice([0, 10, 15, 30, 45])
                invoice = Invoice(
                    date=day,
                    time=time(hour, minute),
                    customer=rng.choice(customers) if rng.random() < 0.45 else None,
                    payment_status="paid",
                    payment_method=rng.choice(methods),
                    discount=Decimal("0"),
                    notes="August seed sale",
                    business=business,
                    created_by=user,
                )
                invoice.number = Invoice.generate_number(business)
                invoice.save()

                location = None
                vehicle = None
                for stock in group:
                    active = next(
                        (
                            row
                            for row in stock.vehicle_assignments.all()
                            if row.status
                        ),
                        None,
                    )
                    if active:
                        if active.location_id and location is None:
                            location = active.location
                        if active.vehicle_id and vehicle is None:
                            vehicle = active.vehicle
                    line = InvoiceItem(
                        invoice=invoice,
                        item=stock,
                        quantity=Decimal("1"),
                        status="active",
                        business=business,
                        created_by=user,
                    )
                    apply_item_pricing(line)
                    line.save()
                    mark_item_unloaded_on_invoice(line, invoice)
                    stock.status = False
                    stock.save(update_fields=["status", "updated_at"])
                    lines_created += 1

                calculate_invoice_totals(invoice)
                invoice.save(update_fields=["sub_total", "gst", "grand_total", "updated_at"])
                InvoiceLocation.objects.create(
                    invoice=invoice,
                    location=location,
                    vehicle=vehicle,
                    business=business,
                    created_by=user,
                )
                invoices_created += 1

        nonempty = sum(1 for day in days if day_items[day])
        weekend_sold = sum(len(day_items[day]) for day in days if day.weekday() >= 4)
        weekday_sold = lines_created - weekend_sold
        self.stdout.write(self.style.SUCCESS(
            f"{invoices_created} invoices, {lines_created} items sold on {business.name} "
            f"({nonempty} days in {days[0]:%b %Y}; weekday {weekday_sold}, Fri–Sun {weekend_sold})."
        ))
