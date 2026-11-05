from decimal import Decimal, ROUND_HALF_UP

from inventory.models import Item, Vehicle
from inventory.utils import mark_item_unloaded_on_invoice

from .models import InvoiceLocation


def _quantize(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_item_pricing(item, quantity=Decimal("1")):
    """Return invoice line pricing from the inventory item's linked ProductPrice."""
    quantity = Decimal(quantity or 1)
    if quantity <= 0:
        quantity = Decimal("1")

    product_price = item.price
    unit = product_price.unit or "unit"
    price = _quantize(product_price.mrp or 0)
    discount = Decimal("0")
    line_subtotal = _quantize((quantity * price) - discount)
    gst_percent = Decimal(product_price.gst or 0)
    gst_amount = _quantize(line_subtotal * gst_percent / Decimal("100"))
    total = _quantize(line_subtotal + gst_amount)

    return {
        "unit": unit,
        "price": str(price),
        "discount": str(discount),
        "gst": str(gst_amount),
        "gst_percent": str(gst_percent),
        "line_subtotal": str(line_subtotal),
        "total": str(total),
        "product_label": str(item.product),
    }


def apply_item_pricing(invoice_item):
    """Apply product price fields to a saved invoice line item."""
    if not invoice_item.item_id:
        return invoice_item

    inventory_item = (
        Item.objects.select_related("price", "product")
        .filter(pk=invoice_item.item_id)
        .first()
    )
    if not inventory_item:
        return invoice_item

    pricing = get_item_pricing(inventory_item, invoice_item.quantity)
    invoice_item.unit = pricing["unit"]
    invoice_item.price = Decimal(pricing["price"])
    invoice_item.discount = Decimal(pricing["discount"])
    invoice_item.gst = Decimal(pricing["gst"])
    invoice_item.total = Decimal(pricing["total"])
    return invoice_item


def build_item_pricing_map(business):
    """Build a lookup of base pricing for all active inventory items."""
    items = Item.objects.filter(
        business=business,
        status=True,
    ).select_related("price", "product")
    return {
        str(item.pk): get_item_pricing(item, Decimal("1"))
        for item in items
    }


def save_invoice_location(invoice, business, request, vehicle=None, latitude=None, longitude=None):
    """Save optional GPS coordinates and/or vehicle for a new invoice."""
    has_coords = latitude is not None and longitude is not None
    if not vehicle and not has_coords:
        return None

    invoice_location = InvoiceLocation(
        invoice=invoice,
        business=business,
        vehicle=vehicle,
        latitude=latitude,
        longitude=longitude,
    )
    save_created_by(invoice_location, request)
    invoice_location.save()
    return invoice_location


def save_created_by(obj, request):
    if hasattr(obj, "created_by") and request.user.is_authenticated:
        obj.created_by = request.user
    return obj


def calculate_invoice_totals(invoice):
    """Recalculate invoice subtotal, GST, and grand total from line items."""
    items = invoice.items.all()
    sub_total = Decimal("0")
    gst_total = Decimal("0")

    for line in items:
        sub_total += line.total - line.gst
        gst_total += line.gst or Decimal("0")

    invoice.sub_total = _quantize(sub_total)
    invoice.gst = _quantize(gst_total)
    discount = invoice.discount or Decimal("0")
    invoice.grand_total = _quantize(invoice.sub_total - discount + invoice.gst)
    if invoice.grand_total < 0:
        invoice.grand_total = Decimal("0")
    return invoice
