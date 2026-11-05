from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from farm.models import Land, Water, LandWater, FeedConsumption, FeedStock, FeedStockTransaction
from myfarm.permissions import permission_required
from .forms import LandForm, WaterForm, LandWaterForm, FeedStockForm, FeedStockTransactionForm, FeedConsumptionForm


def land_hub_redirect(tab="land"):
    return redirect(f"{reverse('farm:land_list')}?tab={tab}")


@permission_required("land.view")
def land_list(request):
    business = request.business
    tab = request.GET.get("tab", "land")
    if tab not in {"land", "water", "map"}:
        tab = "land"
    return render(request, "land/land_list.html", {
        "business": business,
        "business_user": request.business_user,
        "active_tab": tab,
        "lands": Land.objects.filter(business=business).select_related("location", "created_by"),
        "waters": Water.objects.filter(business=business).select_related("created_by"),
        "records": LandWater.objects.filter(business=business).select_related("land", "water", "created_by"),
    })


@permission_required("land.create")
def land_create(request):
    business = request.business
    if request.method == "POST":
        form = LandForm(request.POST,business=business)
        if form.is_valid():
            land = form.save(commit=False)
            land.business = business
            land.created_by = request.user
            land.save()
            messages.success(request,f"{land.name} created successfully.")
            return land_hub_redirect("land")
    else:
        form = LandForm(business=business)
    return render(request,"land/land_form.html",{"form":form,"land":None,"business":business})


@permission_required("land.update")
def land_edit(request,pk):
    business = request.business
    land = get_object_or_404(Land,pk=pk,business=business)
    if request.method == "POST":
        form = LandForm(request.POST,instance=land,business=business)
        if form.is_valid():
            updated_land = form.save(commit=False)
            updated_land.business = business
            updated_land.created_by = land.created_by
            updated_land.save()
            messages.success(request,"Land updated successfully.")
            return land_hub_redirect("land")
    else:
        form = LandForm(instance=land,business=business)
    return render(request,"land/land_form.html",{"form":form,"land":land,"business":business})


@permission_required("land.delete")
def land_delete(request,pk):
    business = request.business
    land = get_object_or_404(Land,pk=pk,business=business)
    if request.method == "POST":
        land_name = land.name
        land.delete()
        messages.success(request,f"{land_name} deleted successfully.")
        return land_hub_redirect("land")
    return render(request,"land/land_delete.html",{"land":land,"business":business})


@permission_required("water.view")
def water_list(request):
    return land_hub_redirect("water")


@permission_required("water.create")
def water_create(request):
    business = request.business
    if request.method == "POST":
        form = WaterForm(request.POST)
        if form.is_valid():
            water = form.save(commit=False)
            water.business = business
            water.created_by = request.user
            water.save()
            messages.success(request,f"{water.name} created successfully.")
            return land_hub_redirect("water")
    else:
        form = WaterForm()
    return render(request,"water/water_form.html",{"form":form,"water":None,"business":business})


@permission_required("water.update")
def water_edit(request,pk):
    business = request.business
    water = get_object_or_404(Water,pk=pk,business=business)
    if request.method == "POST":
        form = WaterForm(request.POST,instance=water)
        if form.is_valid():
            updated_water = form.save(commit=False)
            updated_water.business = business
            updated_water.created_by = water.created_by
            updated_water.save()
            messages.success(request,"Water source updated successfully.")
            return land_hub_redirect("water")
    else:
        form = WaterForm(instance=water)
    return render(request,"water/water_form.html",{"form":form,"water":water,"business":business})


@permission_required("water.delete")
def water_delete(request,pk):
    business = request.business
    water = get_object_or_404(Water,pk=pk,business=business)
    if request.method == "POST":
        water_name = water.name
        water.delete()
        messages.success(request,f"{water_name} deleted successfully.")
        return land_hub_redirect("water")
    return render(request,"water/water_delete.html",{"water":water,"business":business})


@permission_required("land_water.view")
def land_water_list(request):
    return land_hub_redirect("map")


@permission_required("land_water.create")
def land_water_create(request):
    business = request.business
    if request.method == "POST":
        form = LandWaterForm(request.POST,business=business)
        if form.is_valid():
            record = form.save(commit=False)
            record.business = business
            record.created_by = request.user
            record.save()
            messages.success(request,"Land water record created successfully.")
            return land_hub_redirect("map")
    else:
        form = LandWaterForm(business=business)
    return render(request,"land_water/land_water_form.html",{"form":form,"record":None,"business":business})


@permission_required("land_water.update")
def land_water_edit(request,pk):
    business = request.business
    record = get_object_or_404(LandWater,pk=pk,business=business)
    if request.method == "POST":
        form = LandWaterForm(request.POST,instance=record,business=business)
        if form.is_valid():
            updated_record = form.save(commit=False)
            updated_record.business = business
            updated_record.created_by = record.created_by
            updated_record.save()
            messages.success(request,"Land water record updated successfully.")
            return land_hub_redirect("map")
    else:
        form = LandWaterForm(instance=record,business=business)
    return render(request,"land_water/land_water_form.html",{"form":form,"record":record,"business":business})


@permission_required("land_water.delete")
def land_water_delete(request,pk):
    business = request.business
    record = get_object_or_404(LandWater,pk=pk,business=business)
    if request.method == "POST":
        record.delete()
        messages.success(request,"Land water record deleted successfully.")
        return land_hub_redirect("map")
    return render(request,"land_water/land_water_delete.html",{"record":record,"business":business})


def feed_hub_redirect(tab="daily"):
    return redirect(f"{reverse('farm:feedstock_list')}?tab={tab}")


@permission_required("feedstock.view")
def feedstock_list(request):
    business = request.business
    tab = request.GET.get("tab", "daily")
    if tab == "moves":
        tab = "adjust"
    if tab not in {"daily", "stock", "adjust"}:
        tab = "daily"
    return render(request, "feedstock/feedstock_list.html", {
        "business": business,
        "business_user": request.business_user,
        "active_tab": tab,
        "feedstocks": FeedStock.objects.filter(business=business).select_related("created_by"),
        "transactions": FeedStockTransaction.objects.filter(feed_stock__business=business).select_related("feed_stock", "created_by"),
        "consumptions": FeedConsumption.objects.filter(business=business).select_related("created_by"),
    })


@permission_required("feedstock.create")
def feedstock_create(request):
    business = request.business
    if request.method == "POST":
        form = FeedStockForm(request.POST)
        if form.is_valid():
            feedstock = form.save(commit=False)
            feedstock.business = business
            feedstock.created_by = request.user
            feedstock.total_amount = feedstock.stock_weight * feedstock.rate
            feedstock.current_stock_kg = feedstock.stock_weight
            feedstock.save()
            messages.success(request,f"{feedstock.fodder_variety} stock created successfully.")
            return feed_hub_redirect("stock")
    else:
        form = FeedStockForm()
    return render(request,"feedstock/feedstock_form.html",{"form":form,"feedstock":None,"business":business})


@permission_required("feedstock.update")
def feedstock_edit(request,pk):
    business = request.business
    feedstock = get_object_or_404(FeedStock,pk=pk,business=business)
    if request.method == "POST":
        form = FeedStockForm(request.POST,instance=feedstock)
        if form.is_valid():
            updated_feedstock = form.save(commit=False)
            updated_feedstock.business = business
            updated_feedstock.created_by = feedstock.created_by
            updated_feedstock.total_amount = updated_feedstock.stock_weight * updated_feedstock.rate
            updated_feedstock.save()
            messages.success(request,"Feed stock updated successfully.")
            return feed_hub_redirect("stock")
    else:
        form = FeedStockForm(instance=feedstock)

    return render(request,"feedstock/feedstock_form.html",{"form":form,"feedstock":feedstock,"business":business})


@permission_required("feedstock.delete")
def feedstock_delete(request,pk):
    business = request.business
    feedstock = get_object_or_404(FeedStock,pk=pk,business=business)

    if request.method == "POST":
        feedstock.delete()
        messages.success(request,"Feed stock deleted successfully.")
        return feed_hub_redirect("stock")

    return render(request,"feedstock/feedstock_delete.html",{"feedstock":feedstock,"business":business})


@permission_required("feedstock_transaction.view")
def feedstock_transaction_list(request):
    return feed_hub_redirect("adjust")


@permission_required("feedstock_transaction.create")
def feedstock_transaction_create(request):
    business = request.business

    if request.method == "POST":
        form = FeedStockTransactionForm(request.POST,business=business)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.created_by = request.user
            transaction.save()
            messages.success(request,"Feed stock transaction created successfully.")
            return feed_hub_redirect("adjust")
    else:
        form = FeedStockTransactionForm(business=business)

    return render(request,"feedstock_transaction/feedstock_transaction_form.html",{"form":form,"transaction":None,"business":business})


@permission_required("feedstock_transaction.update")
def feedstock_transaction_edit(request,pk):
    business = request.business
    transaction = get_object_or_404(FeedStockTransaction,pk=pk,feed_stock__business=business)

    if request.method == "POST":
        form = FeedStockTransactionForm(request.POST,instance=transaction,business=business)

        if form.is_valid():
            updated_transaction = form.save(commit=False)
            updated_transaction.created_by = transaction.created_by
            updated_transaction.save()
            messages.success(request,"Feed stock transaction updated successfully.")
            return feed_hub_redirect("adjust")
    else:
        form = FeedStockTransactionForm(instance=transaction,business=business)

    return render(request,"feedstock_transaction/feedstock_transaction_form.html",{"form":form,"transaction":transaction,"business":business})


@permission_required("feedstock_transaction.delete")
def feedstock_transaction_delete(request,pk):
    business = request.business
    transaction = get_object_or_404(FeedStockTransaction,pk=pk,feed_stock__business=business)

    if request.method == "POST":
        transaction.delete()
        messages.success(request,"Feed stock transaction deleted successfully.")
        return feed_hub_redirect("adjust")

    return render(request,"feedstock_transaction/feedstock_transaction_delete.html",{"transaction":transaction,"business":business})

@permission_required("feed_consumption.view")
def feed_consumption_list(request):
    return feed_hub_redirect("daily")


@permission_required("feed_consumption.create")
def feed_consumption_create(request):
    business = request.business

    if request.method == "POST":
        form = FeedConsumptionForm(request.POST)

        if form.is_valid():
            consumption = form.save(commit=False)
            consumption.business = business
            consumption.created_by = request.user
            consumption.save()
            messages.success(request,"Feed consumption created successfully.")
            return feed_hub_redirect("daily")
    else:
        form = FeedConsumptionForm()

    return render(request,"feeds_consumption/feed_consumption_form.html",{"form":form,"consumption":None,"business":business})


@permission_required("feed_consumption.update")
def feed_consumption_edit(request,pk):
    business = request.business
    consumption = get_object_or_404(FeedConsumption,pk=pk,business=business)

    if request.method == "POST":
        form = FeedConsumptionForm(request.POST,instance=consumption)

        if form.is_valid():
            updated_consumption = form.save(commit=False)
            updated_consumption.business = business
            updated_consumption.created_by = consumption.created_by
            updated_consumption.save()
            messages.success(request,"Feed consumption updated successfully.")
            return feed_hub_redirect("daily")
    else:
        form = FeedConsumptionForm(instance=consumption)

    return render(request,"feeds_consumption/feed_consumption_form.html",{"form":form,"consumption":consumption,"business":business})


@permission_required("feed_consumption.delete")
def feed_consumption_delete(request,pk):
    business = request.business
    consumption = get_object_or_404(FeedConsumption,pk=pk,business=business)

    if request.method == "POST":
        consumption.delete()
        messages.success(request,"Feed consumption deleted successfully.")
        return feed_hub_redirect("daily")

    return render(request,"feeds_consumption/feed_consumption_delete.html",{"consumption":consumption,"business":business})


# Create your views here.

# # =========================================================
# # FEED STOCK LIST
# # =========================================================

# @permission_required("stock.view")
# def feedstock_list(request):

#     business = request.business

#     stocks = (
#         FeedStock.objects
#         .filter(
#             business=business
#         )
#         .select_related(
#             "created_by"
#         )
#     )

#     return render(
#         request,
#         "feed_stock/feedstock_list.html",
#         {
#             "stocks": stocks,
#             "business": business,
#         }
#     )


# # =========================================================
# # FEED STOCK CREATE
# # =========================================================

# @permission_required("stock.create")
# def feedstock_create(request):

#     business = request.business

#     if request.method == "POST":

#         form = FeedStockForm(
#             request.POST
#         )

#         if form.is_valid():

#             feedstock = form.save(
#                 commit=False
#             )

#             # Never accept business from form
#             feedstock.business = business

#             # Record who created it
#             feedstock.created_by = request.user

#             feedstock.save()

#             messages.success(
#                 request,
#                 "Feed stock created successfully."
#             )

#             return redirect(
#                 "inventory:feedstock_list"
#             )

#     else:

#         form = FeedStockForm()

#     return render(
#         request,
#         "feed_stock/feedstock_form.html",
#         {
#             "form": form,
#             "business": business,
#             "feedstock": None,
#         }
#     )


# # =========================================================
# # FEED STOCK UPDATE
# # =========================================================

# @permission_required("stock.update")
# def feedstock_update(request, pk):

#     business = request.business

#     feedstock = get_object_or_404(
#         FeedStock,
#         id=pk,
#         business=business
#     )

#     if request.method == "POST":

#         form = FeedStockForm(
#             request.POST,
#             instance=feedstock
#         )

#         if form.is_valid():

#             feedstock = form.save(
#                 commit=False
#             )

#             # Never allow business to change
#             feedstock.business = business

#             feedstock.save()

#             messages.success(
#                 request,
#                 "Feed stock updated successfully."
#             )

#             return redirect(
#                 "inventory:feedstock_list"
#             )

#     else:

#         form = FeedStockForm(
#             instance=feedstock
#         )

#     return render(
#         request,
#         "feed_stock/feedstock_form.html",
#         {
#             "form": form,
#             "feedstock": feedstock,
#             "business": business,
#         }
#     )


# # =========================================================
# # FEED STOCK DELETE
# # =========================================================

# @permission_required("stock.delete")
# def feedstock_delete(request, pk):

#     business = request.business

#     feedstock = get_object_or_404(
#         FeedStock,
#         id=pk,
#         business=business
#     )

#     if request.method == "POST":

#         feedstock.delete()

#         messages.success(
#             request,
#             "Feed stock deleted successfully."
#         )

#         return redirect(
#             "inventory:feedstock_list"
#         )

#     return render(
#         request,
#         "feed_stock/feedstock_delete.html",
#         {
#             "feedstock": feedstock,
#             "business": business,
#         }
#     )