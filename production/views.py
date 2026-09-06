from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from myfarm.permissions import permission_required
from goats.models import Goat
import pdb
from .models import GoatWeight,GoatMilk,GoatMilkBatch,GoatMilkTest,Product,ProductPrice,Ingredient,IngredientPrice,Recipe,RecipeItem,ProductBatch
from .forms import GoatWeightForm,GoatWeightVoiceForm,GoatMilkForm,GoatMilkVoiceForm,GoatMilkBatchForm,GoatMilkTestForm,ProductForm,ProductPriceForm,IngredientForm,IngredientPriceForm,RecipeForm,RecipeItemForm,ProductBatchForm

# =========================================================
# GOAT WEIGHT
# =========================================================
@permission_required("weight.view")
def goat_weight_list(request):
    business = request.business
    weights = GoatWeight.objects.filter(business=business).select_related("goat","created_by","user")
    return render(request,"production/goat_weight/goat_weight_list.html",{"weights":weights,"business":business})

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
    form.fields["goat"].queryset = Goat.objects.filter(business=business)
    return render(request,"production/goat_weight/goat_weight_form.html",{"form":form,"business":business})

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
    form.fields["goat"].queryset = Goat.objects.filter(business=business)
    return render(request,"production/goat_weight/goat_weight_form.html",{"form":form,"weight":weight,"business":business})

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
    milks = GoatMilk.objects.filter(business=business).select_related("goat","created_by","user")
    return render(request,"production/goat_milk/goat_milk_list.html",{"milks":milks,"business":business})

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
    form.fields["goat"].queryset = Goat.objects.filter(business=business,gender="FEMALE",live=True)
    return render(request,"production/goat_milk/goat_milk_form.html",{"form":form,"business":business})

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
    form.fields["goat"].queryset = Goat.objects.filter(business=business,gender="FEMALE",live=True)
    return render(request,"production/goat_milk/goat_milk_form.html",{"form":form,"milk":milk,"business":business})

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
    if request.method == "POST":
        form = GoatMilkVoiceForm(request.POST,business=business)
        if form.is_valid():
            now = timezone.localtime()
            goat = form.cleaned_data["goat"]
            milk_weight = Decimal(form.cleaned_data["milk_weight"])
            milking_time = GoatMilk.MilkingTime.MORNING if now.hour < 12 else GoatMilk.MilkingTime.EVENING
            milk,created = GoatMilk.objects.update_or_create(business=business,goat=goat,date=now.date(),time=milking_time,defaults={"milk_weight":milk_weight,"user":request.user,"created_by":request.user,"note":""})
            if created:
                messages.success(request,"Goat milk record added successfully.")
            else:
                messages.success(request,"Existing goat milk record updated successfully.")
            return redirect("production:goat_milk_voice_create")
    else:
        form = GoatMilkVoiceForm(business=business)
    return render(request,"production/goat_milk/goat_milk_voice_form.html",{"form":form,"business":business})

# =========================================================
# GOAT WEIGHT VOICE
# =========================================================
@permission_required("weight.create")
def goat_weight_voice_create(request):
    business = request.business
    if request.method == "POST":
        form = GoatWeightVoiceForm(request.POST,business=business)
        if form.is_valid():
            now = timezone.localtime()
            goat = form.cleaned_data["goat"]
            weight = Decimal(form.cleaned_data["weight"])
            weight_record,created = GoatWeight.objects.update_or_create(business=business,goat=goat,date=now.date(),defaults={"weight":weight,"user":request.user,"created_by":request.user,"note":""})
            if created:
                messages.success(request,"Goat weight recorded successfully.")
            else:
                messages.success(request,"Existing goat weight updated successfully.")
            return redirect("production:goat_weight_voice_create")
    else:
        form = GoatWeightVoiceForm(business=business)
    return render(request,"production/goat_weight/goat_weight_voice_form.html",{"form":form,"business":business})

# =========================================================
# HELPER
# =========================================================
def save_created_by(obj,request):
    obj.business = request.business
    obj.created_by = request.business_user.user
    obj.save()

# =========================================================
# GOAT MILK BATCH
# =========================================================
@permission_required("milk_batch.view")
def goat_milk_batch_list(request):
    objects = GoatMilkBatch.objects.filter(business=request.business)
    return render(request,"goat_milk_batches/goat_milk_batch_list.html",{"objects":objects})

@permission_required("milk_batch.create")
def goat_milk_batch_create(request):
    form = GoatMilkBatchForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        save_created_by(obj,request)
        messages.success(request,"Goat milk batch created successfully.")
        return redirect("production:goat_milk_batch_list")
    return render(request,"goat_milk_batches/goat_milk_batch_form.html",{"form":form,"title":"Create Goat Milk Batch"})

@permission_required("milk_batch.update")
def goat_milk_batch_edit(request,pk):
    obj = get_object_or_404(GoatMilkBatch,pk=pk,business=request.business)
    form = GoatMilkBatchForm(request.POST or None,instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.save()
        messages.success(request,"Goat milk batch updated successfully.")
        return redirect("production:goat_milk_batch_list")
    return render(request,"goat_milk_batches/goat_milk_batch_form.html",{"form":form,"title":"Edit Goat Milk Batch"})

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
    return render(request,"production/goat_milk_test_list.html",{"objects":objects})

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
    objects = Product.objects.filter(business=request.business)
    return render(request,"product/product_list.html",{"objects":objects})

@permission_required("product.create")
def product_create(request):
    form = ProductForm(request.POST or None,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        save_created_by(obj,request)
        messages.success(request,"Product created successfully.")
        return redirect("production:product_list")
    return render(request,"product/product_form.html",{"form":form,"title":"Create Product"})

@permission_required("product.update")
def product_edit(request,pk):
    obj = get_object_or_404(Product,pk=pk,business=request.business)
    form = ProductForm(request.POST or None,instance=obj,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.save()
        messages.success(request,"Product updated successfully.")
        return redirect("production:product_list")
    return render(request,"product/product_form.html",{"form":form,"title":"Edit Product"})

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
    objects = ProductPrice.objects.filter(business=request.business).select_related("product")
    return render(request,"product_prices/product_price_list.html",{"objects":objects})

@permission_required("product_price.create")
def product_price_create(request):
    form = ProductPriceForm(request.POST or None,business=request.business)
    # pdb.set_trace()
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        save_created_by(obj,request)
        messages.success(request,"Product price created successfully.")
        return redirect("production:product_price_list")
    return render(request,"product_prices/product_price_form.html",{"form":form,"title":"Create Product Price"})

@permission_required("product_price.update")
def product_price_edit(request,pk):
    obj = get_object_or_404(ProductPrice,pk=pk,business=request.business)
    form = ProductPriceForm(request.POST or None,instance=obj,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.save()
        messages.success(request,"Product price updated successfully.")
        return redirect("production:product_price_list")
    return render(request,"product_prices/product_price_form.html",{"form":form,"title":"Edit Product Price"})

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
    objects = Ingredient.objects.filter(business=request.business)
    return render(request,"ingredient/ingredient_list.html",{"objects":objects})

@permission_required("ingredient.create")
def ingredient_create(request):
    form = IngredientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        save_created_by(obj,request)
        messages.success(request,"Ingredient created successfully.")
        return redirect("production:ingredient_list")
    return render(request,"ingredient/ingredient_form.html",{"form":form,"title":"Create Ingredient"})

@permission_required("ingredient.update")
def ingredient_edit(request,pk):
    obj = get_object_or_404(Ingredient,pk=pk,business=request.business)
    form = IngredientForm(request.POST or None,instance=obj)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.save()
        messages.success(request,"Ingredient updated successfully.")
        return redirect("production:ingredient_list")
    return render(request,"ingredient/ingredient_form.html",{"form":form,"title":"Edit Ingredient"})

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
    return render(request,"ingredient_price/ingredient_price_list.html",{"objects":objects})

@permission_required("ingredient_price.create")
def ingredient_price_create(request):
    form = IngredientPriceForm(request.POST or None,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        save_created_by(obj,request)
        messages.success(request,"Ingredient price created successfully.")
        return redirect("production:ingredient_price_list")
    return render(request,"ingredient_price/ingredient_price_form.html",{"form":form,"title":"Create Ingredient Price"})

@permission_required("ingredient_price.update")
def ingredient_price_edit(request,pk):
    obj = get_object_or_404(IngredientPrice,pk=pk,business=request.business)
    form = IngredientPriceForm(request.POST or None,instance=obj,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.save()
        messages.success(request,"Ingredient price updated successfully.")
        return redirect("production:ingredient_price_list")
    return render(request,"ingredient_price/ingredient_price_form.html",{"form":form,"title":"Edit Ingredient Price"})

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
    objects = Recipe.objects.filter(business=request.business).select_related("product")
    return render(request,"recipe/recipe_list.html",{"objects":objects})

@permission_required("recipe.create")
def recipe_create(request):
    form = RecipeForm(request.POST or None,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        save_created_by(obj,request)
        messages.success(request,"Recipe created successfully.")
        return redirect("production:recipe_list")
    return render(request,"recipe/recipe_form.html",{"form":form,"title":"Create Recipe"})

@permission_required("recipe.update")
def recipe_edit(request,pk):
    obj = get_object_or_404(Recipe,pk=pk,business=request.business)
    form = RecipeForm(request.POST or None,instance=obj,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.save()
        messages.success(request,"Recipe updated successfully.")
        return redirect("production:recipe_list")
    return render(request,"recipe/recipe_form.html",{"form":form,"title":"Edit Recipe"})

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
    objects = RecipeItem.objects.filter(business=request.business).select_related("recipe","ingredient")
    return render(request,"recipe_item/recipe_item_list.html",{"objects":objects})

@permission_required("recipe_item.create")
def recipe_item_create(request):
    form = RecipeItemForm(request.POST or None,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        save_created_by(obj,request)
        messages.success(request,"Recipe item created successfully.")
        return redirect("production:recipe_item_list")
    return render(request,"recipe_item/recipe_item_form.html",{"form":form,"title":"Create Recipe Item"})

@permission_required("recipe_item.update")
def recipe_item_edit(request,pk):
    obj = get_object_or_404(RecipeItem,pk=pk,business=request.business)
    form = RecipeItemForm(request.POST or None,instance=obj,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.save()
        messages.success(request,"Recipe item updated successfully.")
        return redirect("production:recipe_item_list")
    return render(request,"recipe_item/recipe_item_form.html",{"form":form,"title":"Edit Recipe Item"})

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
    objects = ProductBatch.objects.filter(business=request.business).select_related("product","recipe","location","goat_milk_batch")
    return render(request,"product_batch/product_batch_list.html",{"objects":objects})

@permission_required("product_batch.create")
def product_batch_create(request):
    form = ProductBatchForm(request.POST or None,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        save_created_by(obj,request)
        messages.success(request,"Product batch created successfully.")
        return redirect("production:product_batch_list")
    return render(request,"product_batch/product_batch_form.html",{"form":form,"title":"Create Product Batch"})

@permission_required("product_batch.update")
def product_batch_edit(request,pk):
    obj = get_object_or_404(ProductBatch,pk=pk,business=request.business)
    form = ProductBatchForm(request.POST or None,instance=obj,business=request.business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = request.business
        obj.save()
        messages.success(request,"Product batch updated successfully.")
        return redirect("production:product_batch_list")
    return render(request,"product_batch/product_batch_form.html",{"form":form,"title":"Edit Product Batch"})

@permission_required("product_batch.delete")
def product_batch_delete(request,pk):
    obj = get_object_or_404(ProductBatch,pk=pk,business=request.business)
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Product batch deleted successfully.")
        return redirect("production:product_batch_list")
    return render(request,"product_batch/confirm_delete.html",{"object":obj})