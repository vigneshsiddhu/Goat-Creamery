from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Avg, Sum

from production.models import GoatMilk, GoatWeight, ProductBatch
from sales.models import Invoice


def previous_calendar_month(today):
    first = today.replace(day=1)
    prev_end = first - timedelta(days=1)
    start = prev_end.replace(day=1)
    return start, prev_end


def month_before(start):
    prev_end = start - timedelta(days=1)
    prev_start = prev_end.replace(day=1)
    return prev_start, prev_end


def _days(start, end):
    days = []
    cursor = start
    while cursor <= end:
        days.append(cursor)
        cursor += timedelta(days=1)
    return days


def _pct(value, maximum):
    if not maximum or maximum <= 0:
        return 0
    height = float(value) / float(maximum) * 100
    if value > 0 and height < 6:
        return 6
    return round(height, 1)


def _change(current, previous):
    current = Decimal(current or 0)
    previous = Decimal(previous or 0)
    if previous == 0:
        if current == 0:
            return Decimal("0"), "flat"
        return Decimal("100"), "up"
    delta = ((current - previous) / previous) * Decimal("100")
    delta = delta.quantize(Decimal("0.1"))
    if delta > 0:
        direction = "up"
    elif delta < 0:
        direction = "down"
    else:
        direction = "flat"
    return delta, direction


def daily_series(day_map, start, end):
    days = _days(start, end)
    values = [Decimal(day_map.get(day, 0) or 0) for day in days]
    maximum = max(values) if values else Decimal("0")
    peak_day = days[values.index(maximum)] if values and maximum > 0 else None
    dip_candidates = [(day, val) for day, val in zip(days, values) if val > 0]
    if dip_candidates:
        dip_day, dip_value = min(dip_candidates, key=lambda row: row[1])
    else:
        dip_day, dip_value = None, Decimal("0")
    if dip_day and (maximum <= 0 or dip_value >= maximum):
        dip_day, dip_value = None, Decimal("0")
    bars = []
    for day, value in zip(days, values):
        kind = ""
        if peak_day and day == peak_day and maximum > 0:
            kind = "peak"
        elif dip_day and day == dip_day and dip_value < maximum:
            kind = "dip"
        bars.append(
            {
                "date": day,
                "value": value,
                "pct": _pct(value, maximum),
                "kind": kind,
            }
        )
    return {
        "bars": bars,
        "peak_day": peak_day,
        "peak_value": maximum,
        "dip_day": dip_day,
        "dip_value": dip_value,
        "total": sum(values, Decimal("0")),
    }


def _sum_by_date(queryset, date_field, value_field, start, end):
    rows = (
        queryset.filter(**{f"{date_field}__range": (start, end)})
        .values(date_field)
        .annotate(total=Sum(value_field))
        .order_by(date_field)
    )
    return {row[date_field]: row["total"] or Decimal("0") for row in rows}


def milk_card(business, start, end, prev_start, prev_end):
    current_map = _sum_by_date(
        GoatMilk.objects.filter(business=business),
        "date",
        "milk_weight",
        start,
        end,
    )
    previous_total = (
        GoatMilk.objects.filter(business=business, date__range=(prev_start, prev_end)).aggregate(
            total=Sum("milk_weight")
        )["total"]
        or Decimal("0")
    )
    series = daily_series(current_map, start, end)
    change, direction = _change(series["total"], previous_total)
    return {
        "key": "milk",
        "title": "Goat milk",
        "icon": "bi-cup-straw",
        "unit": "L",
        "headline": series["total"],
        "change": change,
        "direction": direction,
        **series,
        "previous_total": previous_total,
    }


def production_card(business, start, end, prev_start, prev_end):
    current_map = _sum_by_date(
        ProductBatch.objects.filter(business=business, status="active"),
        "date",
        "quantity",
        start,
        end,
    )
    previous_total = (
        ProductBatch.objects.filter(
            business=business,
            status="active",
            date__range=(prev_start, prev_end),
        ).aggregate(total=Sum("quantity"))["total"]
        or Decimal("0")
    )
    series = daily_series(current_map, start, end)
    change, direction = _change(series["total"], previous_total)
    return {
        "key": "production",
        "title": "Production",
        "icon": "bi-boxes",
        "unit": "g",
        "headline": series["total"],
        "change": change,
        "direction": direction,
        **series,
        "previous_total": previous_total,
    }


def sales_card(business, start, end, prev_start, prev_end):
    invoices = Invoice.objects.filter(business=business).exclude(payment_status="cancelled")
    current_map = _sum_by_date(invoices, "date", "grand_total", start, end)
    previous_total = (
        invoices.filter(date__range=(prev_start, prev_end)).aggregate(total=Sum("grand_total"))["total"]
        or Decimal("0")
    )
    series = daily_series(current_map, start, end)
    change, direction = _change(series["total"], previous_total)
    return {
        "key": "sales",
        "title": "Sales",
        "icon": "bi-receipt",
        "unit": "₹",
        "headline": series["total"],
        "change": change,
        "direction": direction,
        **series,
        "previous_total": previous_total,
    }


def weight_card(business, start, end, prev_start, prev_end):
    current = list(
        GoatWeight.objects.filter(business=business, date__range=(start, end)).select_related("goat")
    )
    previous = list(
        GoatWeight.objects.filter(business=business, date__range=(prev_start, prev_end)).select_related("goat")
    )
    current_avg = (
        GoatWeight.objects.filter(business=business, date__range=(start, end)).aggregate(avg=Avg("weight"))["avg"]
        or Decimal("0")
    )
    previous_avg = (
        GoatWeight.objects.filter(business=business, date__range=(prev_start, prev_end)).aggregate(avg=Avg("weight"))[
            "avg"
        ]
        or Decimal("0")
    )
    prev_by_goat = {}
    for row in sorted(previous, key=lambda item: item.date):
        prev_by_goat[row.goat_id] = row.weight
    latest_prev = prev_by_goat
    latest_curr = {}
    for row in sorted(current, key=lambda item: item.date):
        latest_curr[row.goat_id] = row.weight
    up = down = flat = 0
    for goat_id, weight in latest_curr.items():
        before = latest_prev.get(goat_id)
        if before is None:
            continue
        if weight > before:
            up += 1
        elif weight < before:
            down += 1
        else:
            flat += 1
    counts = (
        GoatWeight.objects.filter(business=business, date__range=(start, end))
        .values("date")
        .annotate(n=Avg("weight"))
    )
    avg_map = {row["date"]: row["n"] or Decimal("0") for row in counts}
    series = daily_series(avg_map, start, end)
    change, direction = _change(current_avg, previous_avg)
    return {
        "key": "weight",
        "title": "Goat weight",
        "icon": "bi-speedometer2",
        "unit": "kg",
        "headline": current_avg,
        "change": change,
        "direction": direction,
        "up_count": up,
        "down_count": down,
        "flat_count": flat,
        "previous_total": previous_avg,
        **series,
        "total": current_avg,
    }


def overview_cards(business, today=None):
    today = today or date.today()
    start, end = previous_calendar_month(today)
    prev_start, prev_end = month_before(start)
    return {
        "period_start": start,
        "period_end": end,
        "prev_start": prev_start,
        "prev_end": prev_end,
        "cards": [
            milk_card(business, start, end, prev_start, prev_end),
            production_card(business, start, end, prev_start, prev_end),
            sales_card(business, start, end, prev_start, prev_end),
            weight_card(business, start, end, prev_start, prev_end),
        ],
    }
