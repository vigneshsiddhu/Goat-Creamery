from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.contrib import messages
from django.db import transaction
from django.db.models import Avg, Count, Max, OuterRef, Prefetch, Subquery, Sum, Value
from django.db.models.functions import Coalesce, Lower
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect,render
from django.urls import reverse
from django.utils import timezone
from myfarm.permissions import permission_required
from myfarm.pagination import paginate
from goats.models import Goat
import pdb
from .models import GoatWeight,GoatMilk,GoatMilkBatch,GoatMilkTest,Product,ProductPrice,Ingredient,IngredientPrice,Recipe,RecipeItem,ProductBatch,ProductBatchMilk,recipe_item_grams
from .forms import GoatWeightForm,GoatWeightVoiceForm,GoatMilkForm,GoatMilkVoiceForm,GoatMilkBatchForm,GoatMilkBatchFarmForm,GoatMilkTestForm,ProductForm,ProductPriceForm,IngredientWithPriceForm,IngredientPriceForm,RecipeForm,RecipeItemForm,RecipeItemFormSet,ProductBatchForm,ProductBatchVoiceForm

# =========================================================
# GOAT WEIGHT
# =========================================================
@permission_required("weight.view")
def goat_weight_list(request):
    business = request.business
    weights = GoatWeight.objects.filter(business=business).select_related("goat", "created_by", "user")
    stats = weights.aggregate(
        total_records=Count("id"),
        average_weight=Avg("weight"),
        heaviest_weight=Max("weight"),
    )
    latest = weights.first()
    heaviest = weights.order_by("-weight", "-date").first()
    token_ids = list(
        weights.values_list("goat__token_no", flat=True).distinct().order_by("goat__token_no")
    )
    selected_token = (request.GET.get("token") or "").strip()
    filtered = weights.filter(goat__token_no=selected_token) if selected_token else weights
    page = paginate(request, filtered)
    return render(
        request,
        "production/goat_weight/goat_weight_list.html",
        {
            "weights": page,
            "page_obj": page,
            "business": business,
            "total_records": stats["total_records"] or 0,
            "average_weight": stats["average_weight"] or 0,
            "latest_weight": latest.weight if latest else 0,
            "latest_goat": latest.goat if latest else None,
            "heaviest_weight": stats["heaviest_weight"] or 0,
            "heaviest_goat": heaviest.goat if heaviest else None,
            "token_ids": token_ids,
            "selected_token": selected_token,
        },
    )

@permission_required("weight.view")
def goat_weight_detail(request, id):
    business = request.business
    weight = get_object_or_404(GoatWeight, id=id, business=business)
    return render(
        request,
        "production/goat_weight/goat_weight_detail.html",
        {"weight": weight, "business": business},
    )

@permission_required("weight.create")
def goat_weight_create(request):
    business = request.business
    if request.method == "POST":
        form = GoatWeightForm(request.POST)
        if form.is_valid():
            goat = form.cleaned_data["goat"]
            weight_value = form.cleaned_data["weight"]
            date = form.cleaned_data["date"]
            note = form.cleaned_data["note"]
            weight,created = GoatWeight.objects.update_or_create(business=business,goat=goat,date=date,defaults={"weight":weight_value,"note":note,"user":request.user,"created_by":request.user})
            if created:
                messages.success(request,"Goat weight recorded successfully.")
            else:
                messages.success(request,"Existing goat weight record updated successfully.")
            return redirect("production:goat_weight_list")
    else:
        form = GoatWeightForm()
    form.fields["goat"].queryset = Goat.objects.filter(business=business).order_by("token_no")
    return render(
        request,
        "production/goat_weight/goat_weight_form.html",
        {"form": form, "business": business, "title": "Add Goat Weight"},
    )

@permission_required("weight.update")
def goat_weight_update(request,id):
    business = request.business
    weight = get_object_or_404(GoatWeight,id=id,business=business)
    if request.method == "POST":
        form = GoatWeightForm(request.POST,instance=weight)
        if form.is_valid():
            updated_weight = form.save(commit=False)
            updated_weight.business = business
            updated_weight.user = weight.user
            updated_weight.created_by = weight.created_by
            updated_weight.save()
            messages.success(request,"Goat weight updated successfully.")
            return redirect("production:goat_weight_list")
    else:
        form = GoatWeightForm(instance=weight)
    form.fields["goat"].queryset = Goat.objects.filter(business=business).order_by("token_no")
    return render(
        request,
        "production/goat_weight/goat_weight_form.html",
        {"form": form, "weight": weight, "business": business, "title": "Edit Goat Weight"},
    )

@permission_required("weight.delete")
def goat_weight_delete(request,id):
    business = request.business
    weight = get_object_or_404(GoatWeight,id=id,business=business)
    if request.method == "POST":
        weight.delete()
        messages.success(request,"Goat weight deleted successfully.")
        return redirect("production:goat_weight_list")
    return render(request,"production/goat_weight/goat_weight_delete.html",{"weight":weight,"business":business})

# =========================================================
# GOAT MILK
# =========================================================
@permission_required("milk.view")
def goat_milk_list(request):
    business = request.business
    milks = GoatMilk.objects.filter(business=business).select_related("goat", "created_by", "user")
    stats = milks.aggregate(
        total_records=Count("id"),
        average_milk=Avg("milk_weight"),
        highest_milk=Max("milk_weight"),
        total_milk=Sum("milk_weight"),
    )
    latest = milks.first()
    highest = milks.order_by("-milk_weight", "-date").first()
    token_ids = list(
        milks.values_list("goat__token_no", flat=True).distinct().order_by("goat__token_no")
    )
    selected_token = (request.GET.get("token") or "").strip()
    filtered = milks.filter(goat__token_no=selected_token) if selected_token else milks
    page = paginate(request, filtered)
    return render(
        request,
        "production/goat_milk/goat_milk_list.html",
        {
            "milks": page,
            "page_obj": page,
            "business": business,
            "total_records": stats["total_records"] or 0,
            "average_milk": stats["average_milk"] or 0,
            "total_milk": stats["total_milk"] or 0,
            "latest_milk": latest.milk_weight if latest else 0,
            "latest_goat": latest.goat if latest else None,
            "highest_milk": stats["highest_milk"] or 0,
            "highest_goat": highest.goat if highest else None,
            "token_ids": token_ids,
            "selected_token": selected_token,
        },
    )

@permission_required("milk.view")
def goat_milk_detail(request, id):
    business = request.business
    milk = get_object_or_404(GoatMilk, id=id, business=business)
    return render(
        request,
        "production/goat_milk/goat_milk_detail.html",
        {"milk": milk, "business": business},
    )

@permission_required("milk.create")
def goat_milk_create(request):
    business = request.business
    if request.method == "POST":
        form = GoatMilkForm(request.POST)
        if form.is_valid():
            goat = form.cleaned_data["goat"]
            milk_weight = form.cleaned_data["milk_weight"]
            date = form.cleaned_data["date"]
            time = form.cleaned_data["time"]
            note = form.cleaned_data["note"]
            milk,created = GoatMilk.objects.update_or_create(business=business,goat=goat,date=date,time=time,defaults={"milk_weight":milk_weight,"note":note,"user":request.user,"created_by":request.user})
            if created:
                messages.success(request,"Goat milk record created successfully.")
            else:
                messages.success(request,"Existing goat milk record updated successfully.")
            return redirect("production:goat_milk_list")
    else:
        form = GoatMilkForm()
    form.fields["goat"].queryset = Goat.objects.filter(business=business, gender="FEMALE", live=True).order_by("token_no")
    return render(
        request,
        "production/goat_milk/goat_milk_form.html",
        {"form": form, "business": business, "title": "Add Goat Milk"},
    )

@permission_required("milk.update")
def goat_milk_update(request,id):
    business = request.business
    milk = get_object_or_404(GoatMilk,id=id,business=business)
    if request.method == "POST":
        form = GoatMilkForm(request.POST,instance=milk)
        if form.is_valid():
            updated_milk = form.save(commit=False)
            updated_milk.business = business
            updated_milk.user = milk.user
            updated_milk.created_by = milk.created_by
            updated_milk.save()
            messages.success(request,"Goat milk record updated successfully.")
            return redirect("production:goat_milk_list")
    else:
        form = GoatMilkForm(instance=milk)
    form.fields["goat"].queryset = Goat.objects.filter(business=business, gender="FEMALE", live=True).order_by("token_no")
    return render(
        request,
        "production/goat_milk/goat_milk_form.html",
        {"form": form, "milk": milk, "business": business, "title": "Edit Goat Milk"},
    )

@permission_required("milk.delete")
def goat_milk_delete(request,id):
    business = request.business
    milk = get_object_or_404(GoatMilk,id=id,business=business)
    if request.method == "POST":
        milk.delete()
        messages.success(request,"Goat milk record deleted successfully.")
        return redirect("production:goat_milk_list")
    return render(request,"production/goat_milk/goat_milk_delete.html",{"milk":milk,"business":business})

# =========================================================
# GOAT MILK VOICE
# =========================================================
@permission_required("milk.create")
def goat_milk_voice_create(request):
    business = request.business
    latest_milk = GoatMilk.objects.filter(
        business=business,
        goat_id=OuterRef("pk"),
    ).order_by("-date", "-created_at")
    goats = (
        Goat.objects.filter(business=business, gender="FEMALE", live=True)
        .order_by("token_no")
        .annotate(last_milk=Subquery(latest_milk.values("milk_weight")[:1]))
    )
    if request.method == "POST":
        form = GoatMilkVoiceForm(request.POST, business=business)
        if form.is_valid():
            now = timezone.localtime()
            goat = form.cleaned_data["goat"]
            milk_weight = form.cleaned_data["milk_weight"]
            milking_time = GoatMilk.MilkingTime.MORNING if now.hour < 12 else GoatMilk.MilkingTime.EVENING
            milk, created = GoatMilk.objects.update_or_create(
                business=business,
                goat=goat,
                date=now.date(),
                time=milking_time,
                defaults={
                    "milk_weight": milk_weight,
                    "user": request.user,
                    "created_by": request.user,
                    "note": "",
                },
            )
            if created:
                messages.success(request, "Goat milk record added successfully.")
            else:
                messages.success(request, "Existing goat milk record updated successfully.")
            return redirect("production:goat_milk_voice_create")
    else:
        form = GoatMilkVoiceForm(business=business)
    form.fields["goat"].queryset = goats
    return render(
        request,
        "production/goat_milk/goat_milk_voice_form.html",
        {"form": form, "goats": goats, "business": business},
    )

# =========================================================
# GOAT WEIGHT VOICE
# =========================================================
@permission_required("weight.create")
def goat_weight_voice_create(request):
    business = request.business
    latest_weight = GoatWeight.objects.filter(
        business=business,
        goat_id=OuterRef("pk"),
    ).order_by("-date", "-created_at")
    goats = (
        Goat.objects.filter(business=business, live=True)
        .order_by("token_no")
        .annotate(last_weight=Subquery(latest_weight.values("weight")[:1]))
    )
    if request.method == "POST":
        form = GoatWeightVoiceForm(request.POST, business=business)
        if form.is_valid():
            now = timezone.localtime()
            goat = form.cleaned_data["goat"]
            weight = form.cleaned_data["weight"]
            weight_record, created = GoatWeight.objects.update_or_create(
                business=business,
                goat=goat,
                date=now.date(),
                defaults={
                    "weight": weight,
                    "user": request.user,
                    "created_by": request.user,
                    "note": "",
                },
            )
            if created:
                messages.success(request, "Goat weight recorded successfully.")
            else:
                messages.success(request, "Existing goat weight updated successfully.")
            return redirect("production:goat_weight_voice_create")
    else:
        form = GoatWeightVoiceForm(business=business)
    form.fields["goat"].queryset = goats
    return render(
        request,
        "production/goat_weight/goat_weight_voice_form.html",
        {"form": form, "goats": goats, "business": business},
    )

# =========================================================
# HELPER
# =========================================================
def save_created_by(obj,request):
    obj.business = request.business
    obj.created_by = request.business_user.user
    obj.save()


def apply_goat_milk_batch_checkout(milk_batch, close_batch):
    if not milk_batch:
        return
    milk_batch.status = "closed" if close_batch else "processing"
    milk_batch.save(update_fields=["status", "updated_at"])


def product_batch_continue_milk(request, business):
    add_another = request.GET.get("add_another") == "1" or request.POST.get("add_another") == "1"
    choose_next = request.GET.get("choose") == "1"
    milk_id = request.GET.get("milk") or request.POST.get("milk")
    milk = None
    if milk_id and (add_another or choose_next):
        milk = GoatMilkBatch.objects.filter(pk=milk_id, business=business).first()
        if not milk:
            add_another = False
            choose_next = False
    return add_another, choose_next, milk


def redirect_after_milk_checkout(route_name, milk_batch):
    url = reverse(route_name)
    return redirect(f"{url}?choose=1&milk={milk_batch.pk}")


def redirect_add_another_product_batch(route_name, milk_batch):
    url = reverse(route_name)
    return redirect(f"{url}?add_another=1&milk={milk_batch.pk}")


def redirect_after_product_batch_save(request, obj, close_milk, add_another, milk, create_route):
    if close_milk:
        link = obj.milk_links.select_related("goat_milk_batch").first()
        if link:
            return redirect_add_another_product_batch(create_route, link.goat_milk_batch)
    if add_another and milk:
        return redirect_add_another_product_batch(create_route, milk)
    return redirect("production:product_batch_list")


VOICE_BATCH_UNIT_CHOICES = ProductBatchVoiceForm.UNIT_CHOICES


def empty_product_batch_row(index=0):
    return {
        "index": index,
        "goat_milk_batch": "",
        "product": "",
        "quantity": "",
        "unit": "kg",
        "checkout": False,
        "errors": {},
    }


def parse_voice_batch_rows(post):
    try:
        count = max(1, int(post.get("batch_count", 1) or 1))
    except (TypeError, ValueError):
        count = 1
    rows = []
    for index in range(count):
        rows.append({
            "index": index,
            "goat_milk_batch": (post.get(f"batch-{index}-goat_milk_batch") or "").strip(),
            "product": (post.get(f"batch-{index}-product") or "").strip(),
            "quantity": (post.get(f"batch-{index}-quantity") or "").strip(),
            "unit": (post.get(f"batch-{index}-unit") or "kg").strip(),
            "checkout": post.get(f"batch-{index}-checkout") in ("1", "on", "true"),
            "errors": {},
        })
    return rows


def validate_voice_batch_rows(business, rows):
    validated = []
    row_errors = {}
    for row in rows:
        index = row["index"]
        errors = {}
        milk_batch = None
        if not row["goat_milk_batch"]:
            errors["goat_milk_batch"] = "Select a goat milk batch."
        else:
            milk_batch = GoatMilkBatch.objects.filter(
                pk=row["goat_milk_batch"],
                business=business,
            ).first()
            if not milk_batch:
                errors["goat_milk_batch"] = "Invalid goat milk batch."
        product = None
        if not row["product"]:
            errors["product"] = "Select a product."
        else:
            product = Product.objects.filter(
                pk=row["product"],
                business=business,
                status="active",
            ).first()
            if not product:
                errors["product"] = "Invalid product."
            elif not recipe_for_product(business, product):
                errors["product"] = "No recipe is mapped for this product type."
        quantity = None
        if not row["quantity"]:
            errors["quantity"] = "Enter quantity."
        else:
            try:
                quantity = Decimal(row["quantity"])
                if quantity <= 0:
                    errors["quantity"] = "Quantity must be greater than zero."
            except (ArithmeticError, InvalidOperation, ValueError):
                errors["quantity"] = "Enter a valid quantity."
        if not row["unit"]:
            errors["unit"] = "Select unit."
        if errors:
            row_errors[index] = errors
        else:
            validated.append({
                "goat_milk_batch": milk_batch,
                "product": product,
                "quantity": quantity,
                "unit": row["unit"],
                "checkout": row["checkout"],
            })
    return validated, row_errors


def recipe_production_scale(recipe, quantity, unit):
    recipe_weight = recipe.weight if recipe and recipe.weight else Decimal("0")
    entered_grams = recipe_item_grams(quantity, unit)
    if recipe_weight > 0 and entered_grams > 0:
        return entered_grams / recipe_weight
    return quantity or Decimal("0")


def is_goat_milk_ingredient_name(name):
    return (name or "").strip().lower().replace("_", " ") == "goat milk"


def goat_milk_used_litres(recipe, quantity, unit):
    if not recipe:
        return Decimal("0")
    scale = recipe_production_scale(recipe, quantity, unit)
    used = Decimal("0")
    for recipe_item in recipe.items.filter(status=True).select_related("ingredient"):
        if not is_goat_milk_ingredient_name(recipe_item.ingredient.name):
            continue
        used += recipe_item_grams(recipe_item.quantity, recipe_item.unit) * scale / Decimal("1000")
    return used


def apply_goat_milk_batch_wastage(validated, business):
    usage = {}
    for item in validated:
        milk = item.get("goat_milk_batch")
        if not milk:
            continue
        recipe = recipe_for_product(business, item["product"])
        used = goat_milk_used_litres(recipe, item["quantity"], item["unit"])
        usage[milk.pk] = usage.get(milk.pk, Decimal("0")) + used
    milks = GoatMilkBatch.objects.select_for_update().filter(
        pk__in=list(usage.keys()),
        business=business,
    )
    for milk in milks:
        added = usage.get(milk.pk, Decimal("0"))
        previous = milk.wastage or Decimal("0")
        milk_qty = milk.milk_quantity or Decimal("0")
        appended = previous + added
        remaining = milk_qty - appended
        wastage = Decimal("0") if remaining < 0 else appended
        if wastage < 0:
            wastage = Decimal("0")
        milk.wastage = wastage.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        milk.save(update_fields=["wastage", "updated_at"])
    return usage


def save_product_batch_rows(request, validated, today, production_time):
    created_numbers = []
    with transaction.atomic():
        first = validated[0]
        recipe = recipe_for_product(request.business, first["product"])
        obj = ProductBatch(
            product=first["product"],
            recipe=recipe,
            quantity=first["quantity"],
            unit=first["unit"],
            date=today,
            time=production_time,
            cost=calculate_recipe_production_cost(recipe),
            qc_status="passed",
            status="active",
            wastage=Decimal("0"),
            business=request.business,
        )
        save_created_by(obj, request)
        created_numbers.append(obj.batch_number)
        for item in validated:
            milk = item["goat_milk_batch"]
            ProductBatchMilk.objects.create(product_batch=obj, goat_milk_batch=milk)
            apply_goat_milk_batch_checkout(milk, item["checkout"])
        apply_goat_milk_batch_wastage(validated, request.business)
    return created_numbers


def product_batch_multi_create(request, title):
    business = request.business
    now = timezone.localtime()
    today = now.date()
    production_time = now.time().replace(microsecond=0)
    products = Product.objects.filter(business=business, status="active").order_by("type", "code_sku")
    milk_batches = list(
        GoatMilkBatch.objects.filter(business=business).exclude(
            status__iexact="closed"
        ).order_by("-date", "-created_at")
    )
    for batch in milk_batches:
        remaining = (batch.milk_quantity or Decimal("0")) - (batch.wastage or Decimal("0"))
        batch.remaining = remaining if remaining > 0 else Decimal("0")
    batch_rows = [empty_product_batch_row()]
    form_errors = []

    if request.method == "POST":
        batch_rows = parse_voice_batch_rows(request.POST) or [empty_product_batch_row()]
        validated, row_errors = validate_voice_batch_rows(business, batch_rows)
        for row in batch_rows:
            row["errors"] = row_errors.get(row["index"], {})
        if validated and not row_errors:
            created_numbers = save_product_batch_rows(request, validated, today, production_time)
            if len(created_numbers) == 1:
                messages.success(request, f"Product batch {created_numbers[0]} created.")
            return redirect("production:product_batch_list")

    return render(
        request,
        "product_batch/product_batch_voice_form.html",
        {
            "title": title,
            "business": business,
            "today": today,
            "production_time": production_time,
            "product_recipe_map": build_product_recipe_map(business),
            "products": products,
            "milk_batches": milk_batches,
            "milk_batch_map": {
                str(batch.pk): {
                    "number": batch.batch_number,
                    "milk_quantity": f"{batch.milk_quantity:g}",
                    "wastage": f"{batch.wastage:g}",
                    "remaining": f"{batch.remaining:g}",
                }
                for batch in milk_batches
            },
            "unit_choices": VOICE_BATCH_UNIT_CHOICES,
            "batch_rows": batch_rows,
            "batch_count": len(batch_rows),
            "form_errors": form_errors,
        },
    )

_MASS_TO_GRAM = {"kg": Decimal("1000"), "gram": Decimal("1")}
_VOL_TO_ML = {"litre": Decimal("1000"), "ml": Decimal("1")}


def convert_ingredient_quantity(quantity, from_unit, to_unit):
    from_unit = (from_unit or "").strip().lower()
    to_unit = (to_unit or "").strip().lower()
    if not from_unit or not to_unit or from_unit == to_unit:
        return quantity
    if from_unit in _MASS_TO_GRAM and to_unit in _MASS_TO_GRAM:
        return quantity * _MASS_TO_GRAM[from_unit] / _MASS_TO_GRAM[to_unit]
    if from_unit in _VOL_TO_ML and to_unit in _VOL_TO_ML:
        return quantity * _VOL_TO_ML[from_unit] / _VOL_TO_ML[to_unit]
    return quantity


def latest_ingredient_price(ingredient):
    prices = ingredient.prices.all()
    return prices.filter(status="active").first() or prices.first()


def ingredient_price_per_unit(price):
    if price.quantity and price.quantity > 0:
        return price.mrp / price.quantity
    return Decimal("0")


def calculate_recipe_production_cost(recipe):
    if not recipe:
        return Decimal("0.00")
    recipe.refresh_totals()
    return recipe.cost


def recipe_for_product(business, product):
    qs = Recipe.objects.filter(business=business, product=product).order_by("-date", "-created_at")
    if not qs.exists():
        qs = Recipe.objects.filter(business=business, type=product.type).order_by("-date", "-created_at")
    return qs.filter(status="active").first() or qs.first()


def build_product_recipe_map(business):
    recipes_by_product = {}
    recipes_by_type = {}
    for recipe in Recipe.objects.filter(business=business).order_by("-date", "-created_at"):
        recipes_by_product.setdefault(str(recipe.product_id), recipe)
        recipes_by_type.setdefault(recipe.type, recipe)

    items_by_recipe = {}
    for item in (
        RecipeItem.objects.filter(business=business, status=True)
        .select_related("ingredient")
        .order_by("ingredient__name")
    ):
        items_by_recipe.setdefault(str(item.recipe_id), []).append({
            "name": item.ingredient.name,
            "code": item.ingredient.code or "",
            "quantity": f"{item.quantity:g}",
            "unit": item.unit,
            "grams": f"{recipe_item_grams(item.quantity, item.unit):g}",
            "is_goat_milk": (item.ingredient.name or "").strip().lower().replace("_", " ") == "goat milk",
        })

    recipe_map = {}
    for product in Product.objects.filter(business=business).only("id", "type", "variant", "code_sku"):
        recipe = recipes_by_product.get(str(product.pk)) or recipes_by_type.get(product.type)
        if not recipe:
            continue
        flavour = (product.variant or product.type).replace("_", " ").title()
        recipe_map[str(product.pk)] = {
            "id": str(recipe.pk),
            "label": f"Recipe · {flavour} · {recipe.date.strftime('%d %b %Y')}",
            "product": str(product),
            "type": (recipe.type or "").replace("_", " ").title(),
            "date": recipe.date.strftime("%d %b %Y"),
            "weight": f"{recipe.weight:g}" if recipe.weight else "0",
            "cost": f"{recipe.cost:.2f}" if recipe.cost is not None else "0.00",
            "items": items_by_recipe.get(str(recipe.pk), []),
        }
    return recipe_map

def save_ingredient_price(ingredient, business, request, price_data):
    price = IngredientPrice(
        ingredient=ingredient,
        business=business,
        **price_data,
    )
    if request.user.is_authenticated:
        price.created_by = request.business_user.user
    price.save()
    return price

def get_recipe_item_formset(request, recipe=None):
    business = request.business
    if recipe and recipe.pk:
        return RecipeItemFormSet(
            request.POST if request.method == "POST" else None,
            instance=recipe,
            queryset=recipe.items.filter(status=True).select_related("ingredient").order_by("ingredient__name"),
            form_kwargs={"business": business},
        )
    return RecipeItemFormSet(
        request.POST if request.method == "POST" else None,
        form_kwargs={"business": business},
    )

def get_recipe_item_rows(formset):
    rows = []
    for form in formset.forms:
        if form.errors:
            continue
        cleaned = getattr(form, "cleaned_data", None)
        if not cleaned or cleaned.get("DELETE"):
            continue
        ingredient = cleaned.get("ingredient")
        if not ingredient:
            continue
        rows.append({
            "ingredient": ingredient,
            "unit": cleaned["unit"],
            "quantity": cleaned["quantity"],
        })
    return rows

def create_recipe_item(recipe, business, request, row):
    item = RecipeItem(
        recipe=recipe,
        ingredient=row["ingredient"],
        unit=row["unit"],
        quantity=row["quantity"],
        status=True,
        business=business,
    )
    if request.user.is_authenticated:
        item.created_by = request.business_user.user
    item.save()
    return item

def sync_recipe_items(recipe, business, request, formset, is_create=False):
    rows = get_recipe_item_rows(formset)
    if is_create:
        for row in rows:
            create_recipe_item(recipe, business, request, row)
        recipe.refresh_weight()
        return
    active_items = RecipeItem.objects.filter(recipe=recipe, business=business, status=True)
    active_by_ingredient = {item.ingredient_id: item for item in active_items}
    seen = set()
    for row in rows:
        ing_id = row["ingredient"].pk
        seen.add(ing_id)
        existing = active_by_ingredient.get(ing_id)
        if existing:
            if existing.quantity != row["quantity"] or existing.unit != row["unit"]:
                existing.status = False
                existing.save(update_fields=["status", "updated_at"])
                create_recipe_item(recipe, business, request, row)
        else:
            create_recipe_item(recipe, business, request, row)
    for ing_id, item in active_by_ingredient.items():
        if ing_id not in seen:
            item.status = False
            item.save(update_fields=["status", "updated_at"])
    recipe.refresh_weight()

# =========================================================
# GOAT MILK BATCH
# =========================================================
@permission_required("milk_batch.view")
def goat_milk_batch_list(request):
    business = request.business
    objects = GoatMilkBatch.objects.filter(business=business).order_by("-date", "-created_at")
    page = paginate(request, objects)
    return render(
        request,
        "goat_milk_batches/goat_milk_batch_list.html",
        {"objects": page, "page_obj": page, "business": business},
    )

@permission_required("milk_batch.view")
def goat_milk_batch_detail(request, pk):
    business = request.business
    batch = get_object_or_404(GoatMilkBatch, pk=pk, business=business)
    return render(
        request,
        "goat_milk_batches/goat_milk_batch_detail.html",
        {"batch": batch, "business": business},
    )

@permission_required("milk_batch.create")
def goat_milk_batch_create(request):
    business = request.business
    form = GoatMilkBatchForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        save_created_by(obj,request)
        messages.success(request,"Goat milk batch created successfully.")
        return redirect("production:goat_milk_batch_list")
    return render(
        request,
        "goat_milk_batches/goat_milk_batch_form.html",
        {"form": form, "title": "Create Goat Milk Batch", "business": business},
    )

@permission_required("milk_batch.create")
def goat_milk_batch_farm_create(request):
    business = request.business
    now = timezone.localtime()
    today = now.date()
    milk_time = "morning" if now.hour < 12 else "evening"
    goat_milks = list(
        GoatMilk.objects.filter(
            business=business,
            date=today,
            time=milk_time,
        ).select_related("goat").order_by("goat__token_no")
    )
    goat_milk_total = sum((row.milk_weight for row in goat_milks), Decimal("0"))

    form = GoatMilkBatchFarmForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        milk_quantity = form.cleaned_data["milk_quantity"]
        wastage = goat_milk_total - milk_quantity
        if wastage < 0:
            wastage = Decimal("0")
        wastage = wastage.quantize(Decimal("0.01"))
        obj = GoatMilkBatch(
            date=today,
            milk_time=milk_time,
            status="collected",
            milk_quantity=milk_quantity,
            qr_code=form.cleaned_data.get("qr_code"),
            wastage=wastage,
            business=business,
        )
        save_created_by(obj, request)
        messages.success(
            request,
            f"Farm milk batch {obj.batch_number} created. Goat milk total {goat_milk_total} L, wastage {wastage} L.",
        )
        return redirect("production:goat_milk_batch_list")
    return render(
        request,
        "goat_milk_batches/goat_milk_batch_voice_farm.html",
        {
            "form": form,
            "business": business,
            "today": today,
            "milk_time": milk_time,
            "goat_milks": goat_milks,
            "goat_milk_total": goat_milk_total,
        },
    )

@permission_required("milk_batch.update")
def goat_milk_batch_edit(request,pk):
    business = request.business
    obj = get_object_or_404(GoatMilkBatch,pk=pk,business=business)
    form = GoatMilkBatchForm(request.POST or None,instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = business
        obj.save()
        messages.success(request,"Goat milk batch updated successfully.")
        return redirect("production:goat_milk_batch_list")
    return render(
        request,
        "goat_milk_batches/goat_milk_batch_form.html",
        {"form": form, "title": "Edit Goat Milk Batch", "business": business, "batch": obj},
    )

@permission_required("milk_batch.delete")
def goat_milk_batch_delete(request,pk):
    obj = get_object_or_404(GoatMilkBatch,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Goat milk batch deleted successfully.")
        return redirect("production:goat_milk_batch_list")
    return render(request,"goat_milk_batches/confirm_delete.html",{"object":obj})


# =========================================================
# GOAT MILK TEST
# =========================================================
@permission_required("milk_test.view")
def goat_milk_test_list(request):
    objects = GoatMilkTest.objects.filter(business=request.business).select_related("goat_milk_batch")
    page = paginate(request, objects)
    return render(request,"production/goat_milk_test_list.html",{"objects":page,"page_obj":page})

@permission_required("milk_test.create")
def goat_milk_test_create(request):
    form = GoatMilkTestForm(request.POST or None,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.created_by = request.business_user.user
        obj.save()
        messages.success(request,"Goat milk test created successfully.")
        return redirect("production:goat_milk_test_list")
    return render(request,"production/goat_milk_test_form.html",{"form":form,"title":"Create Goat Milk Test"})

@permission_required("milk_test.update")
def goat_milk_test_edit(request,pk):
    obj = get_object_or_404(GoatMilkTest,pk=pk,business=request.business)
    form = GoatMilkTestForm(request.POST or None,instance=obj,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.save()
        messages.success(request,"Goat milk test updated successfully.")
        return redirect("production:goat_milk_test_list")
    return render(request,"production/goat_milk_test_form.html",{"form":form,"title":"Edit Goat Milk Test"})

@permission_required("milk_test.delete")
def goat_milk_test_delete(request,pk):
    obj = get_object_or_404(GoatMilkTest,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Goat milk test deleted successfully.")
        return redirect("production:goat_milk_test_list")
    return render(request,"production/confirm_delete.html",{"object":obj})


# =========================================================
# PRODUCT
# =========================================================
@permission_required("product.view")
def product_list(request):
    objects = (
        Product.objects.filter(business=request.business)
        .prefetch_related(
            Prefetch(
                "prices",
                queryset=ProductPrice.objects.order_by("-date", "-created_at"),
            )
        )
        .order_by(
            Lower("type"),
            Lower(Coalesce("variant", Value(""))),
            "code_sku",
        )
    )
    page = paginate(request, objects)
    return render(
        request,
        "product/product_list.html",
        {"objects": page, "page_obj": page, "business": request.business},
    )

@permission_required("product.view")
def product_detail(request, pk):
    business = request.business
    product = get_object_or_404(
        Product.objects.prefetch_related(
            Prefetch(
                "prices",
                queryset=ProductPrice.objects.order_by("-date", "-created_at"),
            )
        ),
        pk=pk,
        business=business,
    )
    latest_price = product.prices.first()
    price_history = product.prices.all()[:20]
    product_recipe = Recipe.objects.filter(business=business, product=product).first() or Recipe.objects.filter(business=business, type=product.type).first()
    return render(
        request,
        "product/product_detail.html",
        {
            "product": product,
            "latest_price": latest_price,
            "price_history": price_history,
            "product_recipe": product_recipe,
            "business": business,
        },
    )

@permission_required("product.create")
def product_create(request):
    business = request.business
    form = ProductForm(request.POST or None, business=business)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.business = business
        product.status = "active"
        save_created_by(product, request)
        messages.success(request, "Product created successfully.")
        return redirect("production:product_list")
    return render(
        request,
        "product/product_form.html",
        {
            "form": form,
            "title": "Create Product",
            "product": None,
            "business": business,
        },
    )

@permission_required("product.update")
def product_edit(request,pk):
    business = request.business
    obj = get_object_or_404(Product, pk=pk, business=business)
    form = ProductForm(request.POST or None, instance=obj, business=business)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.business = business
        product.save()
        messages.success(request, "Product updated successfully.")
        return redirect("production:product_list")
    return render(
        request,
        "product/product_form.html",
        {
            "form": form,
            "title": "Edit Product",
            "product": obj,
            "business": business,
        },
    )

@permission_required("product.delete")
def product_delete(request,pk):
    obj = get_object_or_404(Product,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Product deleted successfully.")
        return redirect("production:product_list")
    return render(request,"product/confirm_delete.html",{"object":obj})


# =========================================================
# PRODUCT PRICE
# =========================================================
@permission_required("product_price.view")
def product_price_list(request):
    objects = (
        ProductPrice.objects.filter(business=request.business)
        .select_related("product")
        .order_by("-date", "-created_at")
    )
    page = paginate(request, objects)
    return render(
        request,
        "product_prices/product_price_list.html",
        {"objects": page, "page_obj": page, "business": request.business},
    )

@permission_required("product_price.create")
def product_price_create(request):
    business = request.business
    initial = {}
    product_id = request.GET.get("product")
    if product_id:
        initial["product"] = product_id
    form = ProductPriceForm(request.POST or None, business=business, initial=initial)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.status = form.cleaned_data.get("status") or "active"
        save_created_by(obj, request)
        messages.success(request, "Product price created successfully.")
        return redirect("production:product_price_list")
    return render(
        request,
        "product_prices/product_price_form.html",
        {
            "form": form,
            "title": "Create Product Price",
            "business": business,
        },
    )

@permission_required("product_price.update")
def product_price_edit(request,pk):
    business = request.business
    obj = get_object_or_404(ProductPrice, pk=pk, business=business)
    form = ProductPriceForm(request.POST or None, instance=obj, business=business)
    if request.method == "POST" and form.is_valid():
        price = form.save(commit=False)
        price.business = business
        price.save()
        messages.success(request, "Product price updated successfully.")
        return redirect("production:product_price_list")
    return render(
        request,
        "product_prices/product_price_form.html",
        {
            "form": form,
            "title": "Edit Product Price",
            "business": business,
            "product_price": obj,
        },
    )

@permission_required("product_price.delete")
def product_price_delete(request,pk):
    obj = get_object_or_404(ProductPrice,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Product price deleted successfully.")
        return redirect("production:product_price_list")
    return render(request,"product_prices/confirm_delete.html",{"object":obj})


# =========================================================
# INGREDIENT
# =========================================================
@permission_required("ingredient.view")
def ingredient_list(request):
    objects = (
        Ingredient.objects.filter(business=request.business)
        .prefetch_related(
            Prefetch(
                "prices",
                queryset=IngredientPrice.objects.order_by("-date", "-created_at"),
            )
        )
        .order_by("name")
    )
    page = paginate(request, objects)
    return render(request,"ingredient/ingredient_list.html",{"objects":page,"page_obj":page,"business":request.business})

@permission_required("ingredient.view")
def ingredient_detail(request, pk):
    business = request.business
    ingredient = get_object_or_404(
        Ingredient.objects.prefetch_related(
            Prefetch(
                "prices",
                queryset=IngredientPrice.objects.order_by("-date", "-created_at"),
            )
        ),
        pk=pk,
        business=business,
    )
    latest_price = ingredient.prices.first()
    price_history = ingredient.prices.all()[:20]
    return render(
        request,
        "ingredient/ingredient_detail.html",
        {
            "ingredient": ingredient,
            "latest_price": latest_price,
            "price_history": price_history,
            "business": business,
        },
    )

@permission_required("ingredient.create")
def ingredient_create(request):
    business = request.business
    form = IngredientWithPriceForm(request.POST or None, business=business)
    if request.method == "POST" and form.is_valid():
        ingredient = Ingredient(
            name=form.cleaned_data["name"],
            details=form.cleaned_data.get("details") or None,
            business=business,
        )
        if request.user.is_authenticated:
            ingredient.created_by = request.business_user.user
        ingredient.save()
        save_ingredient_price(ingredient, business, request, form.get_price_data())
        messages.success(request, "Ingredient and price created successfully.")
        return redirect("production:ingredient_list")
    return render(
        request,
        "ingredient/ingredient_form.html",
        {
            "form": form,
            "title": "Create Ingredient",
            "ingredient": None,
            "business": business,
            "previous_stock": Decimal("0"),
            "previous_stock_price": Decimal("0"),
        },
    )

@permission_required("ingredient.update")
def ingredient_edit(request,pk):
    business = request.business
    obj = get_object_or_404(Ingredient, pk=pk, business=business)
    form = IngredientWithPriceForm(request.POST or None, business=business, ingredient=obj)
    if request.method == "POST" and form.is_valid():
        obj.name = form.cleaned_data["name"]
        obj.details = form.cleaned_data.get("details") or None
        obj.save()
        if form.price_changed_from_latest():
            save_ingredient_price(obj, business, request, form.get_price_data())
            messages.success(request, "Ingredient updated and new price record added.")
        else:
            messages.success(request, "Ingredient updated successfully.")
        return redirect("production:ingredient_list")
    price_history = obj.prices.filter(business=business).order_by("-date", "-created_at")[:10]
    latest_price = form.latest_price
    return render(
        request,
        "ingredient/ingredient_form.html",
        {
            "form": form,
            "title": "Edit Ingredient",
            "ingredient": obj,
            "business": business,
            "price_history": price_history,
            "previous_stock": latest_price.stock if latest_price else Decimal("0"),
            "previous_stock_price": latest_price.stock_price if latest_price else Decimal("0"),
        },
    )

@permission_required("ingredient.delete")
def ingredient_delete(request,pk):
    obj = get_object_or_404(Ingredient,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Ingredient deleted successfully.")
        return redirect("production:ingredient_list")
    return render(request,"ingredient/confirm_delete.html",{"object":obj})


# =========================================================
# INGREDIENT PRICE
# =========================================================
@permission_required("ingredient_price.view")
def ingredient_price_list(request):
    objects = IngredientPrice.objects.filter(business=request.business).select_related("ingredient")
    page = paginate(request, objects)
    return render(request,"ingredient_price/ingredient_price_list.html",{"objects":page,"page_obj":page})

@permission_required("ingredient_price.create")
def ingredient_price_create(request):
    return redirect("production:ingredient_create")

@permission_required("ingredient_price.update")
def ingredient_price_edit(request,pk):
    obj = get_object_or_404(IngredientPrice,pk=pk,business=request.business)
    return redirect("production:ingredient_edit", pk=obj.ingredient_id)

@permission_required("ingredient_price.delete")
def ingredient_price_delete(request,pk):
    obj = get_object_or_404(IngredientPrice,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Ingredient price deleted successfully.")
        return redirect("production:ingredient_price_list")
    return render(request,"ingredient_price/confirm_delete.html",{"object":obj})


# =========================================================
# RECIPE
# =========================================================
@permission_required("recipe.view")
def recipe_list(request):
    business = request.business
    objects = (
        Recipe.objects.filter(business=business)
        .select_related("product")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=RecipeItem.objects.filter(status=True).select_related("ingredient"),
            )
        )
        .order_by(
            Lower("type"),
            Lower(Coalesce("product__variant", Value(""))),
            "product__code_sku",
        )
    )
    page = paginate(request, objects)
    return render(
        request,
        "recipe/recipe_list.html",
        {"objects": page, "page_obj": page, "business": business},
    )

@permission_required("recipe.view")
def recipe_detail(request, pk):
    business = request.business
    recipe = get_object_or_404(
        Recipe.objects.select_related("product").prefetch_related(
            Prefetch(
                "items",
                queryset=RecipeItem.objects.filter(status=True)
                .select_related("ingredient")
                .order_by("ingredient__name"),
            )
        ),
        pk=pk,
        business=business,
    )
    active_items = recipe.items.all()
    item_history = (
        RecipeItem.objects.filter(recipe=recipe, business=business, status=False)
        .select_related("ingredient")
        .order_by("-created_at")[:20]
    )
    return render(
        request,
        "recipe/recipe_detail.html",
        {
            "recipe": recipe,
            "active_items": active_items,
            "item_history": item_history,
            "business": business,
        },
    )

@permission_required("recipe.create")
def recipe_create(request):
    business = request.business
    form = RecipeForm(request.POST or None, business=business)
    formset = get_recipe_item_formset(request)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            recipe = form.save(commit=False)
            recipe.business = business
            recipe.type = form.cleaned_data["product"].type
            recipe.status = "active"
            if request.user.is_authenticated:
                recipe.created_by = request.business_user.user
            recipe.save()
            sync_recipe_items(recipe, business, request, formset, is_create=True)
        messages.success(request, "Recipe and items created successfully.")
        return redirect("production:recipe_list")
    return render(
        request,
        "recipe/recipe_form.html",
        {
            "form": form,
            "formset": formset,
            "title": "Create Recipe",
            "recipe": None,
            "business": business,
        },
    )

@permission_required("recipe.update")
def recipe_edit(request,pk):
    business = request.business
    obj = get_object_or_404(Recipe, pk=pk, business=business)
    form = RecipeForm(request.POST or None, instance=obj, business=business)
    formset = get_recipe_item_formset(request, recipe=obj)
    if request.method == "POST" and form.is_valid() and formset.is_valid():
        with transaction.atomic():
            recipe = form.save(commit=False)
            recipe.business = business
            recipe.type = form.cleaned_data["product"].type
            recipe.save()
            sync_recipe_items(recipe, business, request, formset, is_create=False)
        messages.success(request, "Recipe updated successfully.")
        return redirect("production:recipe_list")
    item_history = (
        obj.items.filter(business=business, status=False)
        .select_related("ingredient")
        .order_by("-created_at")[:20]
    )
    return render(
        request,
        "recipe/recipe_form.html",
        {
            "form": form,
            "formset": formset,
            "title": "Edit Recipe",
            "recipe": obj,
            "business": business,
            "item_history": item_history,
        },
    )

@permission_required("recipe.delete")
def recipe_delete(request,pk):
    obj = get_object_or_404(Recipe,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Recipe deleted successfully.")
        return redirect("production:recipe_list")
    return render(request,"recipe/confirm_delete.html",{"object":obj})


# =========================================================
# RECIPE ITEM
# =========================================================
@permission_required("recipe_item.view")
def recipe_item_list(request):
    objects = (
        RecipeItem.objects.filter(business=request.business)
        .select_related("recipe", "recipe__product", "ingredient")
        .order_by("-created_at")
    )
    page = paginate(request, objects)
    return render(
        request,
        "recipe_item/recipe_item_list.html",
        {"objects": page, "page_obj": page, "business": request.business},
    )

@permission_required("recipe_item.create")
def recipe_item_create(request):
    return redirect("production:recipe_create")

@permission_required("recipe_item.update")
def recipe_item_edit(request,pk):
    obj = get_object_or_404(RecipeItem, pk=pk, business=request.business)
    return redirect("production:recipe_edit", pk=obj.recipe_id)

@permission_required("recipe_item.delete")
def recipe_item_delete(request,pk):
    obj = get_object_or_404(RecipeItem,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Recipe item deleted successfully.")
        return redirect("production:recipe_item_list")
    return render(request,"recipe_item/confirm_delete.html",{"object":obj})


# =========================================================
# PRODUCT BATCH
# =========================================================
@permission_required("product_batch.view")
def product_batch_list(request):
    business = request.business
    objects = (
        ProductBatch.objects.filter(business=business)
        .select_related("product", "recipe")
        .prefetch_related("milk_links__goat_milk_batch")
        .order_by("-date", "-created_at")
    )
    page = paginate(request, objects)
    return render(
        request,
        "product_batch/product_batch_list.html",
        {"objects": page, "page_obj": page, "business": business},
    )

@permission_required("milk_batch.update")
def product_batch_inactive(request):
    business = request.business
    collected_milks = list(
        GoatMilkBatch.objects.filter(business=business, status__iexact="collected").order_by(
            "-date", "-created_at"
        )
    )
    error = ""
    if request.method == "POST":
        milk_id = (request.POST.get("goat_milk_batch") or "").strip()
        checkout = request.POST.get("checkout") in ("1", "on", "true")
        milk = next((row for row in collected_milks if str(row.pk) == milk_id), None)
        if not milk_id:
            error = "Select a milk batch."
        elif not milk:
            error = "Select a collected milk batch."
        elif not checkout:
            error = "Tick checkout to close the milk batch."
        else:
            milk.status = "closed"
            milk.save(update_fields=["status", "updated_at"])
            messages.success(request, f"Milk batch {milk.batch_number} closed.")
            return redirect("production:product_batch_inactive")
    return render(
        request,
        "product_batch/product_batch_inactive.html",
        {
            "business": business,
            "collected_milks": collected_milks,
            "error": error,
            "selected_milk": request.POST.get("goat_milk_batch", ""),
            "checkout": request.POST.get("checkout") in ("1", "on", "true"),
        },
    )

@permission_required("product_batch.view")
def product_batch_detail(request, pk):
    business = request.business
    batch = get_object_or_404(
        ProductBatch.objects.select_related("product", "recipe", "location").prefetch_related(
            "milk_links__goat_milk_batch"
        ),
        pk=pk,
        business=business,
    )
    return render(
        request,
        "product_batch/product_batch_detail.html",
        {"batch": batch, "business": business},
    )

@permission_required("product_batch.create")
def product_batch_create(request):
    return product_batch_multi_create(request, "Create Product Batch")

@permission_required("product_batch.create")
def product_batch_voice_create(request):
    return product_batch_multi_create(request, "Voice Product Batch")

@permission_required("product_batch.update")
def product_batch_edit(request,pk):
    business = request.business
    obj = get_object_or_404(
        ProductBatch.objects.prefetch_related("milk_links__goat_milk_batch"),
        pk=pk,
        business=business,
    )
    form = ProductBatchForm(request.POST or None,instance=obj,business=business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = business
        obj.save()
        messages.success(request,"Product batch updated successfully.")
        return redirect("production:product_batch_list")
    return render(
        request,
        "product_batch/product_batch_form.html",
        {
            "form": form,
            "title": "Edit Product Batch",
            "business": business,
            "product_recipe_map": build_product_recipe_map(business),
        },
    )

@permission_required("product_batch.delete")
def product_batch_delete(request,pk):
    obj = get_object_or_404(ProductBatch,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Product batch deleted successfully.")
        return redirect("production:product_batch_list")
    return render(request,"product_batch/confirm_delete.html",{"object":obj})