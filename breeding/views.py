from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from myfarm.permissions import permission_required

from .models import Mating, ParentMapping
from .forms import MatingForm, ParentMappingForm


# =========================================================
# MATING LIST
# =========================================================

@permission_required("mating.view")
def mating_list(request):

    business = request.business

    matings = (
        Mating.objects
        .filter(
            male__business=business,
            female__business=business,
        )
        .select_related(
            "male",
            "female",
            "created_by",
        )
    )

    return render(
        request,
        "mating/mating_list.html",
        {
            "matings": matings,
            "business": business,
        },
    )


# =========================================================
# MATING CREATE
# =========================================================

@permission_required("mating.create")
def mating_create(request):

    business = request.business

    if request.method == "POST":

        form = MatingForm(
            request.POST,
            business=business,
        )

        if form.is_valid():

            mating = form.save(
                commit=False
            )

            # -------------------------------------------------
            # Always use logged-in user
            # -------------------------------------------------

            mating.created_by = request.user

            mating.save()

            messages.success(
                request,
                "Mating record created successfully."
            )

            return redirect(
                "breeding:mating_list"
            )

    else:

        form = MatingForm(
            business=business,
        )

    return render(
        request,
        "mating/mating_form.html",
        {
            "form": form,
            "business": business,
        },
    )


# =========================================================
# MATING UPDATE
# =========================================================

@permission_required("mating.update")
def mating_update(request, id):

    business = request.business

    # -----------------------------------------------------
    # Only allow mating records belonging to this business
    # -----------------------------------------------------

    mating = get_object_or_404(
        Mating,
        id=id,
        male__business=business,
        female__business=business,
    )

    if request.method == "POST":

        form = MatingForm(
            request.POST,
            instance=mating,
            business=business,
        )

        if form.is_valid():

            updated_mating = form.save(
                commit=False
            )

            # -------------------------------------------------
            # Preserve business-related relationships
            # -------------------------------------------------

            updated_mating.save()

            messages.success(
                request,
                "Mating record updated successfully."
            )

            return redirect(
                "breeding:mating_list"
            )

    else:

        form = MatingForm(
            instance=mating,
            business=business,
        )

    return render(
        request,
        "mating/mating_form.html",
        {
            "form": form,
            "mating": mating,
            "business": business,
        },
    )


# =========================================================
# MATING DELETE
# =========================================================

@permission_required("mating.delete")
def mating_delete(request, id):

    business = request.business

    mating = get_object_or_404(
        Mating,
        id=id,
        male__business=business,
        female__business=business,
    )

    if request.method == "POST":

        mating.delete()

        messages.success(
            request,
            "Mating record deleted successfully."
        )

        return redirect(
            "breeding:mating_list"
        )

    return render(
        request,
        "mating/mating_delete.html",
        {
            "mating": mating,
            "business": business,
        },
    )


# =========================================================
# PARENT MAPPING LIST
# =========================================================

@permission_required("parent_mapping.view")
def parent_mapping_list(request):

    business = request.business

    mappings = (
        ParentMapping.objects
        .filter(
            child__business=business,
            parent__business=business,
        )
        .select_related(
            "child",
            "parent",
            "created_by",
        )
    )

    return render(
        request,
        "parent_mapping/parent_mapping_list.html",
        {
            "mappings": mappings,
            "business": business,
        },
    )


# =========================================================
# PARENT MAPPING CREATE
# =========================================================

@permission_required("parent_mapping.create")
def parent_mapping_create(request):

    business = request.business

    if request.method == "POST":

        form = ParentMappingForm(
            request.POST,
            business=business,
        )

        if form.is_valid():

            mapping = form.save(
                commit=False
            )

            # -------------------------------------------------
            # Current logged-in user
            # -------------------------------------------------

            mapping.created_by = request.user

            mapping.save()

            messages.success(
                request,
                "Parent mapping created successfully."
            )

            return redirect(
                "breeding:parent_mapping_list"
            )

    else:

        form = ParentMappingForm(
            business=business,
        )

    return render(
        request,
        "parent_mapping/parent_mapping_form.html",
        {
            "form": form,
            "business": business,
        },
    )


# =========================================================
# PARENT MAPPING UPDATE
# =========================================================

@permission_required("parent_mapping.update")
def parent_mapping_update(request, id):

    business = request.business

    mapping = get_object_or_404(
        ParentMapping,
        id=id,
        child__business=business,
        parent__business=business,
    )

    if request.method == "POST":

        form = ParentMappingForm(
            request.POST,
            instance=mapping,
            business=business,
        )

        if form.is_valid():

            updated_mapping = form.save(
                commit=False
            )

            # -------------------------------------------------
            # Preserve created_by
            # -------------------------------------------------

            updated_mapping.created_by = (
                mapping.created_by
            )

            updated_mapping.save()

            messages.success(
                request,
                "Parent mapping updated successfully."
            )

            return redirect(
                "breeding:parent_mapping_list"
            )

    else:

        form = ParentMappingForm(
            instance=mapping,
            business=business,
        )

    return render(
        request,
        "parent_mapping/parent_mapping_form.html",
        {
            "form": form,
            "mapping": mapping,
            "business": business,
        },
    )


# =========================================================
# PARENT MAPPING DELETE
# =========================================================

@permission_required("parent_mapping.delete")
def parent_mapping_delete(request, id):

    business = request.business

    mapping = get_object_or_404(
        ParentMapping,
        id=id,
        child__business=business,
        parent__business=business,
    )

    if request.method == "POST":

        mapping.delete()

        messages.success(
            request,
            "Parent mapping deleted successfully."
        )

        return redirect(
            "breeding:parent_mapping_list"
        )

    return render(
        request,
        "parent_mapping/parent_mapping_delete.html",
        {
            "mapping": mapping,
            "business": business,
        },
    )