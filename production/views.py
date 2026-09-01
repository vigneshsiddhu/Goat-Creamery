from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from myfarm.permissions import permission_required
import pdb
from goats.models import Goat

from .forms import (
    GoatWeightForm,
    GoatWeightVoiceForm,
    GoatMilkForm,
    GoatMilkVoiceForm,
)

from .models import (
    GoatWeight,
    GoatMilk,
)


# =========================================================
# GOAT WEIGHT
# =========================================================


@permission_required("weight.view")
def goat_weight_list(request):

    business = request.business

    weights = (
        GoatWeight.objects
        .filter(
            business=business
        )
        .select_related(
            "goat",
            "created_by",
            "user",
        )
    )

    return render(
        request,
        "production/goat_weight/goat_weight_list.html",
        {
            "weights": weights,
            "business": business,
        }
    )


# =========================================================
# GOAT WEIGHT CREATE
# =========================================================


@permission_required("weight.create")
def goat_weight_create(request):

    business = request.business

    if request.method == "POST":

        form = GoatWeightForm(
            request.POST
        )

        if form.is_valid():

            goat = form.cleaned_data["goat"]
            weight_value = form.cleaned_data["weight"]
            date = form.cleaned_data["date"]
            note = form.cleaned_data["note"]

            # -------------------------------------------------
            # CREATE OR UPDATE
            #
            # Same:
            # Business + Goat + Date
            #
            # => update existing record
            # -------------------------------------------------

            weight, created = GoatWeight.objects.update_or_create(

                business=business,

                goat=goat,

                date=date,

                defaults={
                    "weight": weight_value,
                    "note": note,
                    "user": request.user,
                    "created_by": request.user,
                }
            )

            # -------------------------------------------------
            # MESSAGE
            # -------------------------------------------------

            if created:

                messages.success(
                    request,
                    "Goat weight recorded successfully."
                )

            else:

                messages.success(
                    request,
                    "Existing goat weight record updated successfully."
                )

            return redirect(
                "production:goat_weight_list"
            )

    else:

        form = GoatWeightForm()

    # ---------------------------------------------------------
    # Only goats belonging to this business
    # ---------------------------------------------------------

    form.fields["goat"].queryset = Goat.objects.filter(
        business=business
    )

    return render(
        request,
        "production/goat_weight/goat_weight_form.html",
        {
            "form": form,
            "business": business,
        }
    )


# =========================================================
# GOAT WEIGHT UPDATE
# =========================================================


@permission_required("weight.update")
def goat_weight_update(request, id):

    business = request.business

    weight = get_object_or_404(
        GoatWeight,
        id=id,
        business=business
    )

    if request.method == "POST":

        form = GoatWeightForm(
            request.POST,
            instance=weight
        )

        if form.is_valid():

            updated_weight = form.save(
                commit=False
            )

            # -------------------------------------------------
            # Never allow business / ownership to change
            # -------------------------------------------------

            updated_weight.business = business

            updated_weight.user = weight.user

            updated_weight.created_by = weight.created_by

            updated_weight.save()

            messages.success(
                request,
                "Goat weight updated successfully."
            )

            return redirect(
                "production:goat_weight_list"
            )

    else:

        form = GoatWeightForm(
            instance=weight
        )

    # ---------------------------------------------------------
    # Only goats belonging to this business
    # ---------------------------------------------------------

    form.fields["goat"].queryset = Goat.objects.filter(
        business=business
    )

    return render(
        request,
        "production/goat_weight/goat_weight_form.html",
        {
            "form": form,
            "weight": weight,
            "business": business,
        }
    )


# =========================================================
# GOAT WEIGHT DELETE
# =========================================================


@permission_required("weight.delete")
def goat_weight_delete(request, id):

    business = request.business

    weight = get_object_or_404(
        GoatWeight,
        id=id,
        business=business
    )

    if request.method == "POST":

        weight.delete()

        messages.success(
            request,
            "Goat weight deleted successfully."
        )

        return redirect(
            "production:goat_weight_list"
        )

    return render(
        request,
        "production/goat_weight/goat_weight_delete.html",
        {
            "weight": weight,
            "business": business,
        }
    )


# =========================================================
# GOAT MILK
# =========================================================


@permission_required("milk.view")
def goat_milk_list(request):

    business = request.business

    milks = (
        GoatMilk.objects
        .filter(
            business=business
        )
        .select_related(
            "goat",
            "created_by",
            "user",
        )
    )

    return render(
        request,
        "production/goat_milk/goat_milk_list.html",
        {
            "milks": milks,
            "business": business,
        }
    )


# =========================================================
# GOAT MILK CREATE
# =========================================================


@permission_required("milk.create")
def goat_milk_create(request):

    business = request.business

    if request.method == "POST":
        # pdb.set_trace()
        form = GoatMilkForm(
            request.POST
        )

        if form.is_valid():

            goat = form.cleaned_data["goat"]

            milk_weight = form.cleaned_data[
                "milk_weight"
            ]

            date = form.cleaned_data[
                "date"
            ]

            time = form.cleaned_data[
                "time"
            ]

            note = form.cleaned_data[
                "note"
            ]

            # -------------------------------------------------
            # CREATE OR UPDATE
            #
            # Same:
            # Business + Goat + Date + Time
            #
            # => update existing record
            # -------------------------------------------------

            milk, created = GoatMilk.objects.update_or_create(

                business=business,

                goat=goat,

                date=date,

                time=time,

                defaults={
                    "milk_weight": milk_weight,
                    "note": note,
                    "user": request.user,
                    "created_by": request.user,
                }
            )

            # -------------------------------------------------
            # MESSAGE
            # -------------------------------------------------

            if created:

                messages.success(
                    request,
                    "Goat milk record created successfully."
                )

            else:

                messages.success(
                    request,
                    "Existing goat milk record updated successfully."
                )

            return redirect(
                "production:goat_milk_list"
            )

    else:

        form = GoatMilkForm()

    # ---------------------------------------------------------
    # Only goats belonging to this business
    # ---------------------------------------------------------

    form.fields["goat"].queryset = Goat.objects.filter(
        business=business,
        gender="FEMALE",
        live=True,
    )

    return render(
        request,
        "production/goat_milk/goat_milk_form.html",
        {
            "form": form,
            "business": business,
        }
    )


# =========================================================
# GOAT MILK UPDATE
# =========================================================


@permission_required("milk.update")
def goat_milk_update(request, id):

    business = request.business

    milk = get_object_or_404(
        GoatMilk,
        id=id,
        business=business
    )

    if request.method == "POST":

        form = GoatMilkForm(
            request.POST,
            instance=milk
        )

        if form.is_valid():

            updated_milk = form.save(
                commit=False
            )

            # -------------------------------------------------
            # Preserve business and ownership
            # -------------------------------------------------

            updated_milk.business = business

            updated_milk.user = milk.user

            updated_milk.created_by = milk.created_by

            updated_milk.save()

            messages.success(
                request,
                "Goat milk record updated successfully."
            )

            return redirect(
                "production:goat_milk_list"
            )

    else:

        form = GoatMilkForm(
            instance=milk
        )

    # ---------------------------------------------------------
    # Only goats belonging to this business
    # ---------------------------------------------------------

    form.fields["goat"].queryset = Goat.objects.filter(
        business=business
    )

    return render(
        request,
        "production/goat_milk/goat_milk_form.html",
        {
            "form": form,
            "milk": milk,
            "business": business,
        }
    )


# =========================================================
# GOAT MILK DELETE
# =========================================================


@permission_required("milk.delete")
def goat_milk_delete(request, id):

    business = request.business

    milk = get_object_or_404(
        GoatMilk,
        id=id,
        business=business
    )

    if request.method == "POST":

        milk.delete()

        messages.success(
            request,
            "Goat milk record deleted successfully."
        )

        return redirect(
            "production:goat_milk_list"
        )

    return render(
        request,
        "production/goat_milk/goat_milk_delete.html",
        {
            "milk": milk,
            "business": business,
        }
    )


# =========================================================
# GOAT MILK VOICE CREATE
# =========================================================


@permission_required("milk.create")
def goat_milk_voice_create(request):

    business = request.business

    if request.method == "POST":
        # pdb.set_trace()

        form = GoatMilkVoiceForm(
            request.POST,
            business=business
        )
        # pdb.set_trace()
        if form.is_valid():

            now = timezone.localtime()

            goat = form.cleaned_data[
                "goat"
            ]

            milk_weight = Decimal(
                form.cleaned_data[
                    "milk_weight"
                ]
            )

            # -------------------------------------------------
            # AUTOMATIC MILKING TIME
            # -------------------------------------------------

            if now.hour < 12:

                milking_time = (
                    GoatMilk.MilkingTime.MORNING
                )

            else:

                milking_time = (
                    GoatMilk.MilkingTime.EVENING
                )

            # -------------------------------------------------
            # CREATE OR UPDATE
            #
            # Same:
            # Business + Goat + Date + Time
            #
            # => update old record
            # -------------------------------------------------

            milk, created = (
                GoatMilk.objects.update_or_create(

                    business=business,

                    goat=goat,

                    date=now.date(),

                    time=milking_time,

                    defaults={

                        "milk_weight": milk_weight,

                        "user": request.user,

                        "created_by": request.user,

                        "note": "",
                    }
                )
            )

            # -------------------------------------------------
            # MESSAGE
            # -------------------------------------------------

            if created:

                messages.success(
                    request,
                    "Goat milk record added successfully."
                )

            else:

                messages.success(
                    request,
                    "Existing goat milk record updated successfully."
                )

            return redirect(
                "production:goat_milk_voice_create"
            )

    else:

        form = GoatMilkVoiceForm(
            business=business
        )

    return render(
        request,
        "production/goat_milk/goat_milk_voice_form.html",
        {
            "form": form,
            "business": business,
        }
    )

# =========================================================
# GOAT WEIGHT VOICE CREATE
# =========================================================

@permission_required("weight.create")
def goat_weight_voice_create(request):
    business = request.business
    if request.method == "POST":
        form = GoatWeightVoiceForm(
            request.POST,
            business=business
        )
        if form.is_valid():
            now = timezone.localtime()
            goat = form.cleaned_data["goat"]
            weight = Decimal(
                form.cleaned_data["weight"]
            )
            weight_record, created = GoatWeight.objects.update_or_create(
                business=business,
                goat=goat,
                date=now.date(),
                defaults={
                    "weight": weight,
                    "user": request.user,
                    "created_by": request.user,
                    "note": "",
                }
            )
            if created:
                messages.success(
                    request,
                    "Goat weight recorded successfully."
                )
            else:
                messages.success(
                    request,
                    "Existing goat weight updated successfully."
                )
            return redirect(
                "production:goat_weight_voice_create"
            )
    else:
        form = GoatWeightVoiceForm(
            business=business
        )
    return render(
        request,
        "production/goat_weight/goat_weight_voice_form.html",
        {
            "form": form,
            "business": business,
        }
    )