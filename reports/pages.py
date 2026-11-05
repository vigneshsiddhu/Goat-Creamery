import hashlib
from collections import defaultdict
from decimal import Decimal

from django.db.models import Avg, Sum

from production.models import GoatMilk, GoatWeight
from sales.models import Invoice, InvoiceItem, InvoiceLocation

from .stats import _change, _days, _sum_by_date, previous_calendar_month, month_before, daily_series


CITY_COORDS = {
    "pondi": (11.9416, 79.8083, "Pondicherry"),
    "coimbat": (11.0168, 76.9558, "Coimbatore"),
}


def _period(today):
    start, end = previous_calendar_month(today)
    prev_start, prev_end = month_before(start)
    return start, end, prev_start, prev_end


def _f(value):
    if value is None:
        return 0.0
    return float(Decimal(value))


def _city_key(name):
    text = (name or "").lower()
    if "pondi" in text:
        return "pondi"
    if "coimbat" in text:
        return "coimbat"
    return None


def _jitter(key, lat, lng):
    digest = hashlib.md5(str(key).encode()).hexdigest()
    lat_off = (int(digest[:4], 16) % 90 - 45) / 2500
    lng_off = (int(digest[4:8], 16) % 90 - 45) / 2500
    return round(lat + lat_off, 6), round(lng + lng_off, 6)


def _labels(start, end):
    return [day.strftime("%d %b") for day in _days(start, end)]


def sales_report(business, today):
    start, end, prev_start, prev_end = _period(today)
    invoices = Invoice.objects.filter(business=business).exclude(payment_status="cancelled")
    current = invoices.filter(date__range=(start, end))
    day_map = _sum_by_date(current, "date", "grand_total", start, end)
    series = daily_series(day_map, start, end)
    previous_total = invoices.filter(date__range=(prev_start, prev_end)).aggregate(total=Sum("grand_total"))["total"] or 0
    change, direction = _change(series["total"], previous_total)

    weekday_totals = [0.0] * 7
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for day, value in day_map.items():
        weekday_totals[day.weekday()] += _f(value)

    flavour_map = defaultdict(float)
    lines = (
        InvoiceItem.objects.filter(invoice__in=current)
        .select_related("item__product")
    )
    for line in lines:
        flavour = line.item.product.flavour_display or line.item.product.type or "Other"
        flavour_map[flavour] += _f(line.total)
    flavour_rows = sorted(flavour_map.items(), key=lambda row: row[1], reverse=True)

    payment_map = defaultdict(float)
    for invoice in current:
        method = (invoice.payment_method or "other").replace("_", " ").title()
        payment_map[method] += _f(invoice.grand_total)
    payment_rows = sorted(payment_map.items(), key=lambda row: row[1], reverse=True)

    city_totals = defaultdict(float)
    points = []
    locations = InvoiceLocation.objects.filter(invoice__in=current).select_related("location", "invoice")
    for row in locations:
        amount = _f(row.invoice.grand_total)
        city = _city_key(row.location.name if row.location_id else "")
        if city:
            city_totals[CITY_COORDS[city][2]] += amount
        lat, lng = None, None
        if row.latitude is not None and row.longitude is not None:
            lat, lng = float(row.latitude), float(row.longitude)
        elif city:
            base_lat, base_lng, city_name = CITY_COORDS[city]
            lat, lng = _jitter(row.invoice_id, base_lat, base_lng)
        if lat is None:
            continue
        points.append(
            {
                "lat": lat,
                "lng": lng,
                "amount": amount,
                "label": row.invoice.number,
                "city": CITY_COORDS[city][2] if city else "Sale",
                "date": row.invoice.date.strftime("%d %b"),
            }
        )
    city_rows = sorted(city_totals.items(), key=lambda row: row[1], reverse=True)

    return {
        "page": "sales",
        "title": "Sales report",
        "period_start": start,
        "period_end": end,
        "kpis": [
            {"label": "Revenue", "value": f"₹{series['total']:.0f}", "note": f"{change}% vs prior month", "tone": direction},
            {"label": "Invoices", "value": str(current.count()), "note": "Paid and open bills", "tone": "flat"},
            {"label": "Peak day", "value": series["peak_day"].strftime("%d %b") if series["peak_day"] else "—", "note": f"₹{series['peak_value']:.0f}" if series["peak_day"] else "", "tone": "up"},
            {"label": "Quiet day", "value": series["dip_day"].strftime("%d %b") if series["dip_day"] else "—", "note": f"₹{series['dip_value']:.0f}" if series["dip_day"] else "", "tone": "down"},
        ],
        "charts": {
            "daily": {
                "labels": _labels(start, end),
                "values": [_f(bar["value"]) for bar in series["bars"]],
                "label": "Revenue ₹",
            },
            "weekday": {"labels": weekday_names, "values": weekday_totals, "label": "Revenue ₹"},
            "flavour": {
                "labels": [row[0] for row in flavour_rows],
                "values": [row[1] for row in flavour_rows],
            },
            "payment": {
                "labels": [row[0] for row in payment_rows],
                "values": [row[1] for row in payment_rows],
            },
            "city": {
                "labels": [row[0] for row in city_rows],
                "values": [row[1] for row in city_rows],
            },
        },
        "map": {"points": points, "center": [11.48, 78.38], "zoom": 8},
    }


def milk_report(business, today):
    start, end, prev_start, prev_end = _period(today)
    milks = GoatMilk.objects.filter(business=business, date__range=(start, end)).select_related("goat")
    day_map = _sum_by_date(GoatMilk.objects.filter(business=business), "date", "milk_weight", start, end)
    series = daily_series(day_map, start, end)
    previous_total = GoatMilk.objects.filter(business=business, date__range=(prev_start, prev_end)).aggregate(total=Sum("milk_weight"))["total"] or 0
    change, direction = _change(series["total"], previous_total)

    morning = GoatMilk.objects.filter(business=business, date__range=(start, end), time="morning").aggregate(total=Sum("milk_weight"))["total"] or 0
    evening = GoatMilk.objects.filter(business=business, date__range=(start, end), time="evening").aggregate(total=Sum("milk_weight"))["total"] or 0

    session_rows = (
        GoatMilk.objects.filter(business=business, date__range=(start, end))
        .values("date", "time")
        .annotate(total=Sum("milk_weight"))
    )
    session_lookup = {(row["date"], row["time"]): _f(row["total"]) for row in session_rows}
    session_morning = []
    session_evening = []
    for day in _days(start, end):
        session_morning.append(session_lookup.get((day, "morning"), 0.0))
        session_evening.append(session_lookup.get((day, "evening"), 0.0))

    goat_rows = list(
        milks.values("goat__token_no")
        .annotate(total=Sum("milk_weight"))
        .order_by("-total")
    )
    goat_max = _f(goat_rows[0]["total"]) if goat_rows else 1
    tiles = []
    for row in goat_rows:
        value = _f(row["total"])
        ratio = value / goat_max if goat_max else 0
        if ratio >= 0.8:
            tone = "high"
        elif ratio <= 0.45:
            tone = "low"
        else:
            tone = "mid"
        tiles.append(
            {
                "token": row["goat__token_no"],
                "value": f"{value:.1f} L",
                "tone": tone,
            }
        )

    return {
        "page": "milk",
        "title": "Goat milk report",
        "period_start": start,
        "period_end": end,
        "kpis": [
            {"label": "Total milk", "value": f"{series['total']:.1f} L", "note": f"{change}% vs prior month", "tone": direction},
            {"label": "Morning", "value": f"{_f(morning):.1f} L", "note": "All morning sessions", "tone": "flat"},
            {"label": "Evening", "value": f"{_f(evening):.1f} L", "note": "All evening sessions", "tone": "flat"},
            {"label": "Peak day", "value": series["peak_day"].strftime("%d %b") if series["peak_day"] else "—", "note": f"{series['peak_value']:.1f} L" if series["peak_day"] else "", "tone": "up"},
        ],
        "charts": {
            "daily": {
                "labels": _labels(start, end),
                "values": [_f(bar["value"]) for bar in series["bars"]],
                "label": "Litres",
            },
            "session": {
                "labels": _labels(start, end),
                "morning": session_morning,
                "evening": session_evening,
            },
            "goats": {
                "labels": [row["goat__token_no"] for row in goat_rows[:12]],
                "values": [_f(row["total"]) for row in goat_rows[:12]],
            },
        },
        "tiles": tiles,
        "map": None,
    }


def weight_report(business, today):
    start, end, prev_start, prev_end = _period(today)
    current = list(
        GoatWeight.objects.filter(business=business, date__range=(start, end)).select_related("goat")
    )
    previous = list(
        GoatWeight.objects.filter(business=business, date__range=(prev_start, prev_end)).select_related("goat")
    )
    current_avg = GoatWeight.objects.filter(business=business, date__range=(start, end)).aggregate(avg=Avg("weight"))["avg"] or 0
    previous_avg = GoatWeight.objects.filter(business=business, date__range=(prev_start, prev_end)).aggregate(avg=Avg("weight"))["avg"] or 0
    change, direction = _change(current_avg, previous_avg)

    prev_by_goat = {}
    for row in sorted(previous, key=lambda item: (item.date, item.created_at)):
        prev_by_goat[row.goat_id] = row
    curr_by_goat = {}
    for row in sorted(current, key=lambda item: (item.date, item.created_at)):
        curr_by_goat[row.goat_id] = row

    movers = []
    tiles = []
    up = down = 0
    for goat_id, row in curr_by_goat.items():
        before = prev_by_goat.get(goat_id)
        prev_w = _f(before.weight) if before else None
        curr_w = _f(row.weight)
        delta = curr_w - prev_w if prev_w is not None else 0
        if delta > 0:
            up += 1
            tone = "up"
        elif delta < 0:
            down += 1
            tone = "down"
        else:
            tone = "mid"
        token = row.goat.token_no
        movers.append({"token": token, "previous": prev_w or 0, "current": curr_w, "delta": delta})
        tiles.append(
            {
                "token": token,
                "value": f"{curr_w:.1f} kg" + (f" ({delta:+.1f})" if prev_w is not None else ""),
                "tone": tone,
            }
        )
    movers.sort(key=lambda row: row["delta"], reverse=True)

    avg_rows = (
        GoatWeight.objects.filter(business=business, date__range=(start, end))
        .values("date")
        .annotate(avg=Avg("weight"))
        .order_by("date")
    )

    return {
        "page": "weight",
        "title": "Goat weight report",
        "period_start": start,
        "period_end": end,
        "kpis": [
            {"label": "Herd average", "value": f"{_f(current_avg):.1f} kg", "note": f"{change}% vs prior month", "tone": direction},
            {"label": "Goats up", "value": str(up), "note": "Gained vs prior month", "tone": "up"},
            {"label": "Goats down", "value": str(down), "note": "Lost vs prior month", "tone": "down"},
            {"label": "Records", "value": str(len(current)), "note": "Weigh-ins this month", "tone": "flat"},
        ],
        "charts": {
            "daily": {
                "labels": [row["date"].strftime("%d %b") for row in avg_rows],
                "values": [_f(row["avg"]) for row in avg_rows],
                "label": "Average kg",
            },
            "movers": {
                "labels": [row["token"] for row in movers],
                "values": [row["delta"] for row in movers],
            },
            "current": {
                "labels": [row["token"] for row in movers],
                "values": [row["current"] for row in movers],
            },
        },
        "tiles": tiles,
        "map": None,
    }
