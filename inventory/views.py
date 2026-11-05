from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404,redirect,render

from myfarm.permissions import permission_required
from myfarm.pagination import paginate

from django.utils import timezone

from production.models import ProductBatch, ProductPrice, Recipe, RecipeItem
from .forms import ItemForm,VehicleForm,VehicleLocationForm,ItemLocationCreateForm
from .models import Item,Vehicle,VehicleLocation,ItemLocation
from .utils import apply_product_batch_item_wastage, assign_item_location, deactivate_previous_item_locations


def build_item_product_maps(business):
    batch_map = {}
    price_map = {}
    for batch in ProductBatch.objects.filter(business=business).order_by("-date", "-created_at"):
        batch_map.setdefault(str(batch.product_id), []).append({
            "id": str(batch.pk),
            "label": f"{batch.batch_number} · {batch.date.strftime('%d %b %Y')}",
        })
    for price in ProductPrice.objects.filter(business=business, status="active").order_by("-date"):
        price_map.setdefault(str(price.product_id), []).append({
            "id": str(price.pk),
            "label": f"₹{price.mrp} · {price.quantity} {price.unit}",
        })
    return batch_map, price_map


# ============================================================
# ITEM
# ============================================================
@permission_required("item.view")
def item_list(request):
    business = request.business
    objects = (
        Item.objects.filter(business=business)
        .select_related("product", "product_batch", "price")
        .prefetch_related(
            Prefetch(
                "vehicle_assignments",
                queryset=ItemLocation.objects.filter(status=True).select_related("location", "vehicle"),
                to_attr="active_locations",
            )
        )
        .order_by("-packed_date", "-created_at")
    )
    page = paginate(request, objects)
    return render(request, "items/item_list.html", {"objects": page, "page_obj": page, "business": business})

@permission_required("item.update")
def item_inactive(request):
    business = request.business
    active_batches = list(
        ProductBatch.objects.filter(business=business, status__iexact="active")
        .select_related("product")
        .order_by("-date", "-created_at")
    )
    error = ""
    if request.method == "POST":
        batch_id = (request.POST.get("product_batch") or "").strip()
        checkout = request.POST.get("checkout") in ("1", "on", "true")
        batch = next((row for row in active_batches if str(row.pk) == batch_id), None)
        if not batch_id:
            error = "Select a production batch."
        elif not batch:
            error = "Select an active production batch."
        elif not checkout:
            error = "Tick checkout to mark the production batch inactive."
        else:
            batch.status = "inactive"
            batch.save(update_fields=["status", "updated_at"])
            messages.success(request, f"Production batch {batch.batch_number} marked inactive.")
            return redirect("inventory:item_inactive")
    return render(
        request,
        "items/item_inactive.html",
        {
            "business": business,
            "active_batches": active_batches,
            "error": error,
            "selected_batch": request.POST.get("product_batch", ""),
            "checkout": request.POST.get("checkout") in ("1", "on", "true"),
        },
    )

@permission_required("item.view")
def item_detail(request, pk):
    business = request.business
    item = get_object_or_404(
        Item.objects.select_related(
            "product",
            "product_batch",
            "price",
        ).prefetch_related(
            "product_batch__milk_links__goat_milk_batch",
            Prefetch(
                "vehicle_assignments",
                queryset=ItemLocation.objects.select_related("vehicle", "location").order_by(
                    "-status", "-loaded_at", "-created_at"
                ),
            ),
        ),
        pk=pk,
        business=business,
    )
    goat_milk_batches = [
        link.goat_milk_batch for link in item.product_batch.milk_links.all()
    ]
    recipe = (
        Recipe.objects.filter(business=business, type=item.product.type, status="active")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=RecipeItem.objects.filter(status=True).select_related("ingredient"),
            )
        )
        .first()
    )
    item_locations = list(item.vehicle_assignments.all())
    active_location = next((loc for loc in item_locations if loc.status), None)
    location_history = [loc for loc in item_locations if not loc.status]
    recipe_ingredients = list(recipe.items.all()) if recipe else []
    return render(
        request,
        "items/item_detail.html",
        {
            "item": item,
            "business": business,
            "goat_milk_batches": goat_milk_batches,
            "recipe_ingredients": recipe_ingredients,
            "active_location": active_location,
            "location_history": location_history,
            "shelf_days_remaining": item.shelf_days_remaining,
        },
    )

@permission_required("item.create")
def item_create(request):
    business = request.business
    if request.method == "POST":
        form = ItemForm(request.POST,business=business)
        if form.is_valid():
            with transaction.atomic():
                item = form.save(commit=False)
                item.business = business
                item.created_by = request.business_user.user
                item.save()
                batch = ProductBatch.objects.select_for_update().get(pk=item.product_batch_id)
                apply_product_batch_item_wastage(batch)
                location = form.cleaned_data.get("location")
                vehicle = form.cleaned_data.get("vehicle")
                if location or vehicle:
                    assign_item_location(
                        item,
                        business,
                        request.business_user.user,
                        location,
                        vehicle,
                    )
            messages.success(request,"Item created successfully.")
            return redirect("inventory:item_list")
    else:
        form = ItemForm(business=business)
    batch_map, price_map = build_item_product_maps(business)
    return render(
        request,
        "items/item_form.html",
        {
            "form": form,
            "title": "Create Item",
            "business": business,
            "product_batch_map": batch_map,
            "product_price_map": price_map,
        },
    )

@permission_required("item.update")
def item_edit(request,pk):
    business = request.business
    item = get_object_or_404(Item,pk=pk,business=business)
    if request.method == "POST":
        form = ItemForm(request.POST,instance=item,business=business)
        if form.is_valid():
            form.save()
            location = form.cleaned_data.get("location")
            vehicle = form.cleaned_data.get("vehicle")
            if location or vehicle:
                loc_id = location.id if location else None
                veh_id = vehicle.id if vehicle else None
                active = ItemLocation.objects.filter(item=item, business=business, status=True).first()
                if (
                    not active
                    or active.location_id != loc_id
                    or active.vehicle_id != veh_id
                ):
                    assign_item_location(
                        item,
                        business,
                        request.business_user.user,
                        location,
                        vehicle,
                    )
            messages.success(request,"Item updated successfully.")
            return redirect("inventory:item_list")
    else:
        form = ItemForm(instance=item,business=business)
    batch_map, price_map = build_item_product_maps(business)
    return render(
        request,
        "items/item_form.html",
        {
            "form": form,
            "title": "Edit Item",
            "item": item,
            "business": business,
            "product_batch_map": batch_map,
            "product_price_map": price_map,
        },
    )


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
    objects = Vehicle.objects.filter(business=business).order_by("number")
    page = paginate(request, objects)
    return render(
        request,
        "vehicles/vehicle_list.html",
        {"objects": page, "page_obj": page, "business": business},
    )


@permission_required("vehicle.view")
def vehicle_detail(request, pk):
    business = request.business
    vehicle = get_object_or_404(
        Vehicle.objects.prefetch_related("locations__location"),
        pk=pk,
        business=business,
    )
    return render(
        request,
        "vehicles/vehicle_detail.html",
        {"vehicle": vehicle, "business": business},
    )


@permission_required("vehicle.create")
def vehicle_create(request):
    business = request.business
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.business = business
            vehicle.created_by = request.business_user.user
            vehicle.save()
            messages.success(request, "Vehicle created successfully.")
            return redirect("inventory:vehicle_list")
    else:
        form = VehicleForm()
    return render(
        request,
        "vehicles/vehicle_form.html",
        {"form": form, "title": "Create Vehicle", "business": business},
    )


@permission_required("vehicle.update")
def vehicle_edit(request, pk):
    business = request.business
    vehicle = get_object_or_404(Vehicle, pk=pk, business=business)
    if request.method == "POST":
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated successfully.")
            return redirect("inventory:vehicle_list")
    else:
        form = VehicleForm(instance=vehicle)
    return render(
        request,
        "vehicles/vehicle_form.html",
        {"form": form, "title": "Edit Vehicle", "vehicle": vehicle, "business": business},
    )


@permission_required("vehicle.delete")
def vehicle_delete(request, pk):
    business = request.business
    vehicle = get_object_or_404(Vehicle, pk=pk, business=business)
    if request.method == "POST":
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully.")
        return redirect("inventory:vehicle_list")
    return render(
        request,
        "vehicles/vehicle_confirm_delete.html",
        {"vehicle": vehicle, "business": business},
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
    page = paginate(request, vehicle_locations)
    return render(
        request,
        "vehicle_locations/vehicle_location_list.html",
        {"vehicle_locations": page, "page_obj": page, "business": business},
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
            vehicle_location.created_by = request.business_user.user
            vehicle_location.save()
            messages.success(request,"Vehicle location created successfully.")
            return redirect("inventory:vehicle_location_list")
    else:
        form = VehicleLocationForm(business=business)
    return render(
        request,
        "vehicle_locations/vehicle_location_form.html",
        {"form": form, "business": business},
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
        "vehicle_locations/vehicle_location_form.html",
        {
            "form": form,
            "vehicle_location": vehicle_location,
            "business": business,
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
        "vehicle_locations/vehicle_location_delete.html",
        {"vehicle_location": vehicle_location, "business": business},
    )


# ============================================================
# ITEM LOCATION
# ============================================================
@permission_required("item_location.view")
def item_location_list(request):
    business = request.business
    active_objects = ItemLocation.objects.filter(business=business, status=True).select_related(
        "item__product",
        "item__product_batch",
        "item__price",
        "vehicle",
        "location",
    ).order_by("-loaded_at", "-created_at")
    page = paginate(request, active_objects)
    return render(
        request,
        "item_locations/item_location_list.html",
        {
            "objects": page,
            "page_obj": page,
            "business": business,
        },
    )


@permission_required("item_location.create")
def item_location_create(request):
    business = request.business
    if request.method == "POST":
        form = ItemLocationCreateForm(request.POST, business=business)
        if form.is_valid():
            item = form.cleaned_data["item"]
            deactivate_previous_item_locations(item, business)
            item_location = form.save(commit=False)
            item_location.business = business
            item_location.created_by = request.business_user.user
            now = timezone.localtime()
            item_location.loaded_at = now
            item_location.time = now.time().replace(microsecond=0)
            item_location.status = True
            item_location.unloaded_at = None
            item_location.save()
            messages.success(request, "Item location saved successfully.")
            return redirect("inventory:item_location_list")
    else:
        form = ItemLocationCreateForm(business=business)
    return render(
        request,
        "item_locations/item_location_form.html",
        {
            "form": form,
            "title": "Assign Item Location",
            "business": business,
        },
    )


@permission_required("item_location.update")
def item_location_edit(request, pk):
    messages.info(request, "Item locations cannot be edited. Create a new record instead.")
    return redirect("inventory:item_location_create")


@permission_required("item_location.delete")
def item_location_delete(request, pk):
    messages.info(request, "Item locations cannot be deleted. Create a new record to update location.")
    return redirect("inventory:item_location_list")