from django.shortcuts import render
from django.utils import timezone

from myfarm.permissions import permission_required

from .pages import milk_report, sales_report, weight_report
from .stats import overview_cards


def _page(request, builder, template):
    payload = builder(request.business, timezone.localdate())
    return render(
        request,
        template,
        {
            "business": request.business,
            "report": payload,
            "period_start": payload["period_start"],
            "period_end": payload["period_end"],
            "active_report": payload["page"],
        },
    )


@permission_required("reports.view")
def overview(request):
    data = overview_cards(request.business, timezone.localdate())
    return render(
        request,
        "reports/overview.html",
        {
            "business": request.business,
            "period_start": data["period_start"],
            "period_end": data["period_end"],
            "prev_start": data["prev_start"],
            "prev_end": data["prev_end"],
            "cards": data["cards"],
            "active_report": "overview",
        },
    )


@permission_required("reports.view")
def sales(request):
    return _page(request, sales_report, "reports/sales.html")


@permission_required("reports.view")
def milk(request):
    return _page(request, milk_report, "reports/milk.html")


@permission_required("reports.view")
def weight(request):
    return _page(request, weight_report, "reports/weight.html")
