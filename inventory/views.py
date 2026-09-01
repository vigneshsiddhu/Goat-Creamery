from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from myfarm.permissions import permission_required

from .forms import FeedStockForm
from .models import FeedStock


# =========================================================
# FEED STOCK LIST
# =========================================================

@permission_required("stock.view")
def feedstock_list(request):

    business = request.business

    stocks = (
        FeedStock.objects
        .filter(
            business=business
        )
        .select_related(
            "created_by"
        )
    )

    return render(
        request,
        "feed_stock/feedstock_list.html",
        {
            "stocks": stocks,
            "business": business,
        }
    )


# =========================================================
# FEED STOCK CREATE
# =========================================================

@permission_required("stock.create")
def feedstock_create(request):

    business = request.business

    if request.method == "POST":

        form = FeedStockForm(
            request.POST
        )

        if form.is_valid():

            feedstock = form.save(
                commit=False
            )

            # Never accept business from form
            feedstock.business = business

            # Record who created it
            feedstock.created_by = request.user

            feedstock.save()

            messages.success(
                request,
                "Feed stock created successfully."
            )

            return redirect(
                "inventory:feedstock_list"
            )

    else:

        form = FeedStockForm()

    return render(
        request,
        "feed_stock/feedstock_form.html",
        {
            "form": form,
            "business": business,
            "feedstock": None,
        }
    )


# =========================================================
# FEED STOCK UPDATE
# =========================================================

@permission_required("stock.update")
def feedstock_update(request, pk):

    business = request.business

    feedstock = get_object_or_404(
        FeedStock,
        id=pk,
        business=business
    )

    if request.method == "POST":

        form = FeedStockForm(
            request.POST,
            instance=feedstock
        )

        if form.is_valid():

            feedstock = form.save(
                commit=False
            )

            # Never allow business to change
            feedstock.business = business

            feedstock.save()

            messages.success(
                request,
                "Feed stock updated successfully."
            )

            return redirect(
                "inventory:feedstock_list"
            )

    else:

        form = FeedStockForm(
            instance=feedstock
        )

    return render(
        request,
        "feed_stock/feedstock_form.html",
        {
            "form": form,
            "feedstock": feedstock,
            "business": business,
        }
    )


# =========================================================
# FEED STOCK DELETE
# =========================================================

@permission_required("stock.delete")
def feedstock_delete(request, pk):

    business = request.business

    feedstock = get_object_or_404(
        FeedStock,
        id=pk,
        business=business
    )

    if request.method == "POST":

        feedstock.delete()

        messages.success(
            request,
            "Feed stock deleted successfully."
        )

        return redirect(
            "inventory:feedstock_list"
        )

    return render(
        request,
        "feed_stock/feedstock_delete.html",
        {
            "feedstock": feedstock,
            "business": business,
        }
    )