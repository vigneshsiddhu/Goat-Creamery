from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from myfarm.permissions import (
    permission_required,
    get_business_user,
)

from .models import Business, BusinessUser
from .forms import BusinessForm, BusinessUserForm


# =========================================================
# BUSINESS LIST
# =========================================================

@permission_required("business.view")
def business_list(request):

    business_user = request.business_user
    business = request.business

    businesses = Business.objects.filter(
        id=business.id,
        status=True
    )

    return render(
        request,
        "business/business_list.html",
        {
            "businesses": businesses,
            "business_user": business_user,
            "business": business,
        }
    )


# =========================================================
# BUSINESS CREATE
# =========================================================

@permission_required("business.create")
def business_create(request):

    # -----------------------------------------------------
    # Check whether user already belongs to a business
    # -----------------------------------------------------

    current_business_user = get_business_user(
        request.user
    )

    if current_business_user:

        # Existing business user must have permission
        if current_business_user.role != "SUPER_ADMIN":

            messages.error(
                request,
                "Only a Business Super Admin can create another business."
            )

            return redirect(
                "business:business_list"
            )

    # -----------------------------------------------------
    # CREATE
    # -----------------------------------------------------

    if request.method == "POST":

        form = BusinessForm(
            request.POST
        )

        if form.is_valid():

            business = form.save(
                commit=False
            )

            # Current user creates business
            business.created_by = request.user

            # Current user becomes owner
            business.owner = request.user

            business.save()

            # -------------------------------------------------
            # Automatically assign creator as SUPER_ADMIN
            # -------------------------------------------------

            BusinessUser.objects.create(
                business=business,
                user=request.user,
                role="SUPER_ADMIN",
                is_active=True
            )

            messages.success(
                request,
                f"{business.name} created successfully."
            )

            return redirect(
                "business:business_list"
            )

    else:

        form = BusinessForm()

    return render(
        request,
        "business/business_form.html",
        {
            "form": form,
            "business": None,
        }
    )


# =========================================================
# BUSINESS EDIT
# =========================================================

@permission_required("business.update")
def business_edit(request, pk):

    business_user = request.business_user
    business = request.business

    # -----------------------------------------------------
    # Make sure requested business belongs to current user
    # -----------------------------------------------------

    business = get_object_or_404(
        Business,
        pk=pk,
        id=business.id
    )

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    if request.method == "POST":

        form = BusinessForm(
            request.POST,
            instance=business
        )

        if form.is_valid():

            updated_business = form.save(
                commit=False
            )

            # -------------------------------------------------
            # Never allow these values to change
            # -------------------------------------------------

            updated_business.created_by = (
                business.created_by
            )

            updated_business.owner = (
                business.owner
            )

            updated_business.save()

            messages.success(
                request,
                "Business updated successfully."
            )

            return redirect(
                "business:business_list"
            )

    else:

        form = BusinessForm(
            instance=business
        )

    return render(
        request,
        "business/business_form.html",
        {
            "form": form,
            "business": business,
        }
    )


# =========================================================
# BUSINESS DELETE
# =========================================================

@permission_required("business.delete")
def business_delete(request, pk):

    business = request.business

    business = get_object_or_404(
        Business,
        pk=pk,
        id=business.id
    )

    if request.method == "POST":

        business.delete()

        messages.success(
            request,
            "Business deleted successfully."
        )

        return redirect(
            "business:business_list"
        )

    return render(
        request,
        "business/business_delete.html",
        {
            "business": business,
        }
    )


# =========================================================
# BUSINESS USER LIST
# =========================================================

@permission_required("business_user.view")
def business_user_list(request):

    current_business_user = request.business_user
    business = request.business

    business_users = (
        BusinessUser.objects
        .filter(
            business=business,
            is_active=True
        )
        .select_related(
            "user",
            "business"
        )
    )

    return render(
        request,
        "business_users/business_user_list.html",
        {
            "business_users": business_users,
            "business": business,
            "business_user": current_business_user,
        }
    )


# =========================================================
# BUSINESS USER CREATE
# =========================================================

@permission_required("business_user.create")
def business_user_create(request):

    business = request.business

    if request.method == "POST":

        form = BusinessUserForm(
            request.POST,
            business=business
        )

        if form.is_valid():

            business_user = form.save(
                commit=False
            )

            # -------------------------------------------------
            # NEVER ACCEPT BUSINESS FROM FORM
            # -------------------------------------------------

            business_user.business = business

            business_user.save()

            messages.success(
                request,
                f"{business_user.user.username} "
                f"assigned successfully."
            )

            return redirect(
                "business:business_user_list"
            )

    else:

        form = BusinessUserForm(
            business=business
        )

    return render(
        request,
        "business_users/business_user_form.html",
        {
            "form": form,
            "business_user": None,
            "business": business,
        }
    )


# =========================================================
# BUSINESS USER EDIT
# =========================================================

@permission_required("business_user.update")
def business_user_edit(request, pk):

    business = request.business

    business_user = get_object_or_404(
        BusinessUser,
        pk=pk,
        business=business
    )

    if request.method == "POST":

        form = BusinessUserForm(
            request.POST,
            instance=business_user,
            business=business
        )

        if form.is_valid():

            updated_business_user = form.save(
                commit=False
            )

            # -------------------------------------------------
            # NEVER ALLOW BUSINESS TO CHANGE
            # -------------------------------------------------

            updated_business_user.business = business

            updated_business_user.save()

            messages.success(
                request,
                "Business user updated successfully."
            )

            return redirect(
                "business:business_user_list"
            )

    else:

        form = BusinessUserForm(
            instance=business_user,
            business=business
        )

    return render(
        request,
        "business_users/business_user_form.html",
        {
            "form": form,
            "business_user": business_user,
            "business": business,
        }
    )


# =========================================================
# BUSINESS USER DELETE
# =========================================================

@permission_required("business_user.delete")
def business_user_delete(request, pk):

    business = request.business

    business_user = get_object_or_404(
        BusinessUser,
        pk=pk,
        business=business
    )

    # -----------------------------------------------------
    # Prevent removing yourself
    # -----------------------------------------------------

    if business_user.user == request.user:

        messages.error(
            request,
            "You cannot remove yourself as Super Admin."
        )

        return redirect(
            "business:business_user_list"
        )

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    if request.method == "POST":

        username = business_user.user.username

        business_user.delete()

        messages.success(
            request,
            f"{username} removed from the business."
        )

        return redirect(
            "business:business_user_list"
        )

    return render(
        request,
        "business_users/business_user_delete.html",
        {
            "business_user": business_user,
            "business": business,
        }
    )