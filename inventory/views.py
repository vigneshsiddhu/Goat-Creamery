from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render

from myfarm.permissions import permission_required

from .forms import ItemForm,VehicleForm,VehicleLocationForm,ItemLocationForm
from .models import Item,Vehicle,VehicleLocation,ItemLocation



# ============================================================
# ITEM
# ============================================================
@permission_required("item.view")
def item_list(request):
    business = request.business
    items = Item.objects.filter(business=business).select_related("product","product_batch","price").order_by("-packed_date","-created_at")
    return render(request,"items/item_list.html",{"objects":items})

@permission_required("item.create")
def item_create(request):
    business = request.business
    if request.method == "POST":
        form = ItemForm(request.POST,business=business)
        if form.is_valid():
            item = form.save(commit=False)
            item.business = business
            item.created_by = request.business_user.user
            item.save()
            messages.success(request,"Item created successfully.")
            return redirect("inventory:item_list")
    else:
        form = ItemForm(business=business)
    return render(request,"items/item_form.html",{"form":form,"title":"Create Item"})

@permission_required("item.update")
def item_edit(request,pk):
    business = request.business
    item = get_object_or_404(Item,pk=pk,business=business)
    if request.method == "POST":
        form = ItemForm(request.POST,instance=item,business=business)
        if form.is_valid():
            form.save()
            messages.success(request,"Item updated successfully.")
            return redirect("inventory:item_list")
    else:
        form = ItemForm(instance=item,business=business)
    return render(request,"items/item_form.html",{"form":form,"title":"Edit Item","item":item})


@permission_required("item.delete")
def item_delete(request,pk):
    business = request.business
    item = get_object_or_404(Item,pk=pk,business=business)
    if request.method == "POST":
        item.delete()
        messages.success(request,"Item deleted successfully.")
        return redirect("inventory:item_list")
    return render(request,"items/item_confirm_delete.html",{"item":item})


# ============================================================
# VEHICLE
# ============================================================
@permission_required("vehicle.view")
def vehicle_list(request):
    business = request.business
    vehicles = Vehicle.objects.filter(
        business=business
    ).order_by("number")
    return render(
        request,
        "inventory/vehicle_list.html",
        {"vehicles":vehicles}
    )


@permission_required("vehicle.create")
def vehicle_create(request):
    business = request.business
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.business = business
            vehicle.created_by = request.business_user
            vehicle.save()
            messages.success(request,"Vehicle created successfully.")
            return redirect("inventory:vehicle_list")
    else:
        form = VehicleForm()
    return render(
        request,
        "inventory/vehicle_form.html",
        {"form":form,"title":"Create Vehicle"}
    )


@permission_required("vehicle.update")
def vehicle_edit(request,pk):
    business = request.business
    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
        business=business
    )
    if request.method == "POST":
        form = VehicleForm(
            request.POST,
            instance=vehicle
        )
        if form.is_valid():
            form.save()
            messages.success(request,"Vehicle updated successfully.")
            return redirect("inventory:vehicle_list")
    else:
        form = VehicleForm(instance=vehicle)
    return render(
        request,
        "inventory/vehicle_form.html",
        {"form":form,"title":"Edit Vehicle","vehicle":vehicle}
    )


@permission_required("vehicle.delete")
def vehicle_delete(request,pk):
    business = request.business
    vehicle = get_object_or_404(
        Vehicle,
        pk=pk,
        business=business
    )
    if request.method == "POST":
        vehicle.delete()
        messages.success(request,"Vehicle deleted successfully.")
        return redirect("inventory:vehicle_list")
    return render(
        request,
        "inventory/vehicle_confirm_delete.html",
        {"vehicle":vehicle}
    )


# ============================================================
# VEHICLE LOCATION
# ============================================================
@permission_required("vehicle_location.view")
def vehicle_location_list(request):
    business = request.business
    vehicle_locations = VehicleLocation.objects.filter(
        business=business
    ).select_related(
        "vehicle",
        "location"
    ).order_by("-date","-time")
    return render(
        request,
        "inventory/vehicle_location_list.html",
        {"vehicle_locations":vehicle_locations}
    )


@permission_required("vehicle_location.create")
def vehicle_location_create(request):
    business = request.business
    if request.method == "POST":
        form = VehicleLocationForm(
            request.POST,
            business=business
        )
        if form.is_valid():
            vehicle_location = form.save(commit=False)
            vehicle_location.business = business
            vehicle_location.created_by = request.business_user
            vehicle_location.save()
            messages.success(request,"Vehicle location created successfully.")
            return redirect("inventory:vehicle_location_list")
    else:
        form = VehicleLocationForm(business=business)
    return render(
        request,
        "inventory/vehicle_location_form.html",
        {"form":form,"title":"Create Vehicle Location"}
    )


@permission_required("vehicle_location.update")
def vehicle_location_edit(request,pk):
    business = request.business
    vehicle_location = get_object_or_404(
        VehicleLocation,
        pk=pk,
        business=business
    )
    if request.method == "POST":
        form = VehicleLocationForm(
            request.POST,
            instance=vehicle_location,
            business=business
        )
        if form.is_valid():
            form.save()
            messages.success(request,"Vehicle location updated successfully.")
            return redirect("inventory:vehicle_location_list")
    else:
        form = VehicleLocationForm(
            instance=vehicle_location,
            business=business
        )

    return render(
        request,
        "inventory/vehicle_location_form.html",
        {
            "form":form,
            "title":"Edit Vehicle Location",
            "vehicle_location":vehicle_location
        }
    )


@permission_required("vehicle_location.delete")
def vehicle_location_delete(request,pk):
    business = request.business
    vehicle_location = get_object_or_404(
        VehicleLocation,
        pk=pk,
        business=business
    )
    if request.method == "POST":
        vehicle_location.delete()
        messages.success(request,"Vehicle location deleted successfully.")
        return redirect("inventory:vehicle_location_list")
    return render(
        request,
        "inventory/vehicle_location_confirm_delete.html",
        {"vehicle_location":vehicle_location}
    )


# ============================================================
# ITEM LOCATION
# ============================================================
@permission_required("item_location.view")
def item_location_list(request):
    business = request.business
    item_locations = ItemLocation.objects.filter(
        business=business
    ).select_related(
        "item",
        "vehicle",
        "location"
    ).order_by("-created_at")
    return render(
        request,
        "inventory/item_location_list.html",
        {"item_locations":item_locations}
    )


@permission_required("item_location.create")
def item_location_create(request):
    business = request.business
    if request.method == "POST":
        form = ItemLocationForm(
            request.POST,
            business=business
        )
        if form.is_valid():
            item_location = form.save(commit=False)
            item_location.business = business
            item_location.created_by = request.business_user
            item_location.save()
            messages.success(request,"Item location created successfully.")
            return redirect("inventory:item_location_list")
    else:
        form = ItemLocationForm(business=business)
    return render(
        request,
        "inventory/item_location_form.html",
        {"form":form,"title":"Create Item Location"}
    )


@permission_required("item_location.update")
def item_location_edit(request,pk):
    business = request.business
    item_location = get_object_or_404(
        ItemLocation,
        pk=pk,
        business=business
    )
    if request.method == "POST":
        form = ItemLocationForm(
            request.POST,
            instance=item_location,
            business=business
        )
        if form.is_valid():
            form.save()
            messages.success(request,"Item location updated successfully.")
            return redirect("inventory:item_location_list")
    else:
        form = ItemLocationForm(
            instance=item_location,
            business=business
        )
    return render(
        request,
        "inventory/item_location_form.html",
        {
            "form":form,
            "title":"Edit Item Location",
            "item_location":item_location
        }
    )


@permission_required("item_location.delete")
def item_location_delete(request,pk):
    business = request.business
    item_location = get_object_or_404(
        ItemLocation,
        pk=pk,
        business=business
    )
    if request.method == "POST":
        item_location.delete()
        messages.success(request,"Item location deleted successfully.")
        return redirect("inventory:item_location_list")
    return render(
        request,
        "inventory/item_location_confirm_delete.html",
        {"item_location":item_location}
    )