from django.shortcuts import get_object_or_404,redirect,render
from django.contrib import messages
from django.db.models import Count,Q
from myfarm.permissions import permission_required
from .forms import GoatForm,DiseaseForm,DeathGoatForm,GoatHealthForm
from .models import Goat,Disease,DeathGoat,GoatHealth
import pdb
# =========================================================
# GOAT
# =========================================================
@permission_required("goat.view")
def goat_list(request):
    business = request.business
    goats = Goat.objects.filter(business=business).select_related("business","created_by")
    goat_counts = goats.filter(live=True).aggregate(
        total_live=Count("id"),
        adult_male=Count("id",filter=Q(gender="MALE",maturity="ADULT")),
        adult_female=Count("id",filter=Q(gender="FEMALE",maturity="ADULT")),
        kid_male=Count("id",filter=Q(gender="MALE",maturity="KID")),
        kid_female=Count("id",filter=Q(gender="FEMALE",maturity="KID")),
    )
    return render(request,"goats/goat_list.html",{
        "goats":goats,
        "business":business,
        "total_live":goat_counts["total_live"],
        "adult_male":goat_counts["adult_male"],
        "adult_female":goat_counts["adult_female"],
        "kid_male":goat_counts["kid_male"],
        "kid_female":goat_counts["kid_female"],
    })

# =========================================================
# GOAT CREATE
# =========================================================
@permission_required("goat.create")
def goat_create(request):
    business = request.business
    if request.method == "POST":
        form = GoatForm(request.POST)
        if form.is_valid():
            goat = form.save(commit=False)
            goat.business = business
            goat.created_by = request.user
            goat.save()
            messages.success(request,"Goat created successfully.")
            return redirect("goats:list")
    else:
        form = GoatForm()
    return render(request,"goats/goat_form.html",{"form":form,"goat":None,"business":business})

# =========================================================
# GOAT UPDATE
# =========================================================
@permission_required("goat.update")
def goat_update(request,id):
    business = request.business
    goat = get_object_or_404(Goat,id=id,business=business)
    if request.method == "POST":
        form = GoatForm(request.POST,instance=goat)
        if form.is_valid():
            goat = form.save(commit=False)
            goat.business = business
            goat.save()
            messages.success(request,"Goat updated successfully.")
            return redirect("goats:list")
    else:
        form = GoatForm(instance=goat)
    return render(request,"goats/goat_form.html",{"form":form,"goat":goat,"business":business})

# =========================================================
# GOAT DELETE
# =========================================================
@permission_required("goat.delete")
def goat_delete(request,id):
    business = request.business
    goat = get_object_or_404(Goat,id=id,business=business)
    if request.method == "POST":
        goat.delete()
        messages.success(request,"Goat deleted successfully.")
        return redirect("goats:list")
    return render(request,"goats/goat_delete.html",{"goat":goat,"business":business})

# =========================================================
# DISEASE LIST
# =========================================================
@permission_required("goat_disease.view")
def disease_list(request):
    business = request.business
    diseases = Disease.objects.filter(business=business).select_related("created_by")
    return render(request,"disease/disease_list.html",{"diseases":diseases,"business":business})

# =========================================================
# DISEASE CREATE
# =========================================================
@permission_required("goat_disease.create")
def disease_create(request):
    business = request.business
    if request.method == "POST":
        form = DiseaseForm(request.POST)
        if form.is_valid():
            disease = form.save(commit=False)
            disease.business = business
            disease.created_by = request.user
            disease.save()
            messages.success(request,"Disease created successfully.")
            return redirect("goats:disease_list")
    else:
        form = DiseaseForm()
    return render(request,"disease/disease_form.html",{"form":form,"business":business})

# =========================================================
# DISEASE UPDATE
# =========================================================
@permission_required("goat_disease.update")
def disease_update(request,pk):
    business = request.business
    disease = get_object_or_404(Disease,id=pk,business=business)
    if request.method == "POST":
        form = DiseaseForm(request.POST,instance=disease)
        if form.is_valid():
            disease = form.save(commit=False)
            disease.business = business
            disease.save()
            messages.success(request,"Disease updated successfully.")
            return redirect("goats:disease_list")
    else:
        form = DiseaseForm(instance=disease)
    return render(request,"disease/disease_form.html",{"form":form,"disease":disease,"business":business})

# =========================================================
# DISEASE DELETE
# =========================================================
@permission_required("goat_disease.delete")
def disease_delete(request,pk):
    business = request.business
    disease = get_object_or_404(Disease,id=pk,business=business)
    if request.method == "POST":
        disease.delete()
        messages.success(request,"Disease deleted successfully.")
        return redirect("goats:disease_list")
    return render(request,"disease/disease_delete.html",{"disease":disease,"business":business})

# =========================================================
# DEATH GOAT LIST
# =========================================================
@permission_required("goat_death.view")
def death_goat_list(request):
    business = request.business
    deaths = DeathGoat.objects.filter(business=business).select_related("goat","disease","created_by")
    return render(request,"death_goat/death_goat_list.html",{"deaths":deaths,"business":business})

# =========================================================
# DEATH GOAT CREATE
# =========================================================
@permission_required("goat_death.create")
def death_goat_create(request):
    business = request.business
    if request.method == "POST":
        form = DeathGoatForm(request.POST,business=business)
        if form.is_valid():
            death = form.save(commit=False)
            death.business = business
            death.created_by = request.user
            death.save()
            goat = death.goat
            goat.live = False
            goat.save(update_fields=["live"])
            messages.success(request,"Goat death record created successfully.")
            return redirect("goats:death_goat_list")
    else:
        form = DeathGoatForm(business=business)
    return render(request,"death_goat/death_goat_form.html",{"form":form,"business":business})

# =========================================================
# DEATH GOAT UPDATE
# =========================================================
@permission_required("goat_death.update")
def death_goat_update(request,pk):
    business = request.business
    death = get_object_or_404(DeathGoat,id=pk,business=business)
    if request.method == "POST":
        form = DeathGoatForm(request.POST,instance=death,business=business)
        if form.is_valid():
            death = form.save(commit=False)
            death.business = business
            death.save()
            goat = death.goat
            goat.live = False
            goat.save(update_fields=["live"])
            messages.success(request,"Death record updated successfully.")
            return redirect("goats:death_goat_list")
    else:
        form = DeathGoatForm(instance=death,business=business)
    return render(request,"death_goat/death_goat_form.html",{"form":form,"death":death,"business":business})

# =========================================================
# DEATH GOAT DELETE
# =========================================================
@permission_required("goat_death.delete")
def death_goat_delete(request,pk):
    business = request.business
    death = get_object_or_404(DeathGoat,id=pk,business=business)
    if request.method == "POST":
        goat = death.goat
        goat.live = True
        goat.save(update_fields=["live"])
        death.delete()
        messages.success(request,"Death record deleted successfully.")
        return redirect("goats:death_goat_list")
    return render(request,"death_goat/death_goat_delete.html",{"death":death,"business":business})

# =========================================================
# GOAT HEALTH LIST
# =========================================================
@permission_required("goat_health.view")
def goat_health_list(request):
    business = request.business
    objects = GoatHealth.objects.filter(business=business).select_related("goat","disease","created_by")
    # pdb.set_trace()
    return render(request,"goat_health/goat_health_list.html",{"health_records":objects,"business":business})

# =========================================================
# GOAT HEALTH CREATE
# =========================================================
@permission_required("goat_health.create")
def goat_health_create(request):
    business = request.business
    form = GoatHealthForm(request.POST or None,business=business)
    if request.method == "POST" and form.is_valid():
        pdb.set_trace()
        obj = form.save(commit=False)
        obj.business = business
        obj.created_by = request.business_user.user
        obj.save()
        messages.success(request,"Goat health record created successfully.")
        return redirect("goats:goat_health_list")
    return render(request,"goat_health/goat_health_form.html",{"form":form,"title":"Create Goat Health Record","business":business})

# =========================================================
# GOAT HEALTH UPDATE
# =========================================================
@permission_required("goat_health.update")
def goat_health_update(request,pk):
    business = request.business
    obj = get_object_or_404(GoatHealth,pk=pk,business=business)
    form = GoatHealthForm(request.POST or None,instance=obj,business=business)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.business = business
        obj.save()
        messages.success(request,"Goat health record updated successfully.")
        return redirect("goats:goat_health_list")
    return render(request,"goat_health/goat_health_form.html",{"form":form,"title":"Edit Goat Health Record","business":business,"object":obj})

# =========================================================
# GOAT HEALTH DELETE
# =========================================================
@permission_required("goat_health.delete")
def goat_health_delete(request,pk):
    business = request.business
    obj = get_object_or_404(GoatHealth,pk=pk,business=business)
    # pdb.set_trace()
    if request.method == "POST":
        obj.delete()
        messages.success(request,"Goat health record deleted successfully.")
        return redirect("goats:goat_health_list")
    return render(request,"goat_health/goat_health_delete.html",{"object":obj,"business":business})