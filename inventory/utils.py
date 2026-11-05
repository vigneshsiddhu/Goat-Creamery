from datetime import datetime, time as time_cls

from django.utils import timezone

from .models import Item, ItemLocation, Vehicle


def build_vehicle_map_data(business):
    vehicles = Vehicle.objects.filter(business=business, status="active").order_by("number")
    payload = []
    for vehicle in vehicles:
        latest = (
            vehicle.locations.select_related("location")
            .order_by("-date", "-time", "-created_at")
            .first()
        )
        lat = lng = None
        location_label = ""
        if latest and latest.location:
            if latest.location.latitude is not None and latest.location.longitude is not None:
                lat = float(latest.location.latitude)
                lng = float(latest.location.longitude)
            location_label = str(latest.location)
        payload.append(
            {
                "id": str(vehicle.pk),
                "number": vehicle.number,
                "name": vehicle.name or "",
                "type": vehicle.vehicle_type,
                "capacity": str(vehicle.capacity) if vehicle.capacity is not None else "",
                "unit": vehicle.unit,
                "lat": lat,
                "lng": lng,
                "location_label": location_label,
            }
        )
    return payload


def invoice_unloaded_datetime(invoice):
    if invoice.date and invoice.time:
        dt = datetime.combine(invoice.date, invoice.time)
    elif invoice.date:
        dt = datetime.combine(invoice.date, time_cls.min)
    else:
        return timezone.localtime()
    current_tz = timezone.get_current_timezone()
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, current_tz)
    return dt


def deactivate_previous_item_locations(item, business):
    ItemLocation.objects.filter(
        item=item,
        business=business,
        status=True,
    ).update(status=False)


def assign_item_location(item, business, user, location, vehicle):
    deactivate_previous_item_locations(item, business)
    now = timezone.localtime()
    return ItemLocation.objects.create(
        item=item,
        location=location,
        vehicle=vehicle,
        loaded_at=now,
        time=now.time().replace(microsecond=0),
        status=True,
        business=business,
        created_by=user,
    )


def city_locations_for_business(business):
    from business.models import Location

    return Location.objects.filter(
        business=business,
        status=True,
        type__in=["district", "area", "other"],
    ).order_by("name")


def active_vehicles_for_business(business):
    return Vehicle.objects.filter(business=business, status="active").order_by("number")


def mark_item_unloaded_on_invoice(invoice_item, invoice):
    if not invoice_item.item_id:
        return None

    item_location = (
        ItemLocation.objects.filter(
            item_id=invoice_item.item_id,
            business_id=invoice.business_id,
            status=True,
            unloaded_at__isnull=True,
        )
        .order_by("-loaded_at", "-created_at")
        .first()
    )
    if not item_location:
        return None

    item_location.unloaded_at = invoice_unloaded_datetime(invoice)
    item_location.status = False
    item_location.save(update_fields=["unloaded_at", "status", "updated_at"])
    return item_location


def items_for_location(business):
    return (
        Item.objects.filter(business=business, status=True)
        .select_related("product", "product_batch", "price")
        .order_by("-packed_date", "-created_at")
    )


COUNT_UNITS = {
    "piece",
    "pack",
    "pocket",
    "box",
    "bottle",
    "cup",
    "container",
    "unit",
}


def packed_quantity_in_batch_unit(pack_qty, pack_unit, batch_unit):
    from decimal import Decimal

    from production.models import quantity_in_unit

    pack_qty = Decimal(pack_qty or 0)
    pack_unit = (pack_unit or "").strip().lower()
    batch_unit = (batch_unit or "").strip().lower()
    if pack_unit == batch_unit:
        return pack_qty
    converted = quantity_in_unit(pack_qty, pack_unit, batch_unit)
    if converted > 0:
        return converted
    if pack_unit in COUNT_UNITS and batch_unit in COUNT_UNITS:
        return pack_qty
    return Decimal("0")


def apply_product_batch_item_wastage(batch):
    from decimal import Decimal, ROUND_HALF_UP

    packed = Decimal("0")
    for item in batch.items.select_related("price"):
        price = item.price
        if not price:
            continue
        packed += packed_quantity_in_batch_unit(price.quantity, price.unit, batch.unit)
    remaining = (batch.quantity or Decimal("0")) - packed
    if remaining < 0:
        remaining = Decimal("0")
    batch.wastage = remaining.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    batch.save(update_fields=["wastage", "updated_at"])
    return batch.wastage

