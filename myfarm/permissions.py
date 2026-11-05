# myfarm/permissions.py
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from business.models import Business, BusinessUser


SUPER_ADMIN_ROLES = {"SUPER_ADMIN", "SUPERADMIN", "SUPER_USER"}


def normalize_role(role):
    return str(role or "").strip().upper().replace(" ", "_").replace("-", "_")


def is_full_access(user=None, business_user=None):
    if user is not None and getattr(user, "is_superuser", False):
        return True
    if business_user is None:
        return False
    if normalize_role(business_user.role) in SUPER_ADMIN_ROLES:
        return True
    related_user = getattr(business_user, "user", None)
    return bool(related_user and getattr(related_user, "is_superuser", False))


# =========================================================
# ROLE PERMISSIONS
# =========================================================

ROLE_PERMISSIONS = {
    # =====================================================
    # SUPER ADMIN
    # =====================================================

    "SUPER_ADMIN": {"*"},


    # =====================================================
    # ADMIN
    # =====================================================

    "ADMIN": {

        # Dashboard
        "dashboard.view",

        # Business
        "business.view",
        "business.update",

        # Business Users
        "business_user.view",
        "business_user.create",
        "business_user.update",

        # Goat
        "goat.view",
        "goat.create",
        "goat.update",
        "goat.delete",

        # Goat Disease
        "goat_disease.view",
        "goat_disease.create",
        "goat_disease.update",
        "goat_disease.delete",

        # Goat Death
        "goat_death.view",
        "goat_death.create",
        "goat_death.update",

        # Weight
        "weight.view",
        "weight.create",
        "weight.update",

        # Milk
        "milk.view",
        "milk.create",
        "milk.update",

        # Mating
        "mating.view",
        "mating.create",
        "mating.update",

        # Expense
        "expense.view",
        "expense.create",
        "expense.update",

        "farm_expense.view",
        "farm_expense.create",
        "farm_expense.update",
        "farm_expense.delete",

        # Sales
        "sales.view",
        "sales.create",
        "sales.update",

        # Stock
        "stock.view",
        "stock.create",
        "stock.update",

        # Reports
        "reports.view",
        "reports.export",

        
    },


    # =====================================================
    # FARM MANAGER
    # =====================================================

    "FARM_MANAGER": {

        # Dashboard
        "dashboard.view",

        # Goat
        "goat.view",
        "goat.create",
        "goat.update",

        # Goat Disease
        "goat_disease.view",
        "goat_disease.create",
        "goat_disease.update",

        # Goat Death
        "goat_death.view",
        "goat_death.create",

        # Weight
        "weight.view",
        "weight.create",
        "weight.update",

        # Milk
        "milk.view",
        "milk.create",
        "milk.update",

        # Mating
        "mating.view",
        "mating.create",
        "mating.update",

        # Stock
        "stock.view",
        "stock.create",
        "stock.update",

        # Reports
        "reports.view",
    },


    # =====================================================
    # SALES PERSON
    # =====================================================

    "SALES_PERSON": {

        # Dashboard
        "dashboard.view",

        # Goat
        "goat.view",

        # Milk
        "milk.view",

        # Sales
        "sales.view",
        "sales.create",
        "sales.update",

        # Stock
        "stock.view",

        # Reports
        "reports.view",
    },
}


# =========================================================
# GET BUSINESS USER
# =========================================================

def get_business_user(user):
    """
    Return the active BusinessUser for the logged-in user.
    Prefer a SUPER_ADMIN assignment when the user has more than one.
    """
    assignments = list(
        BusinessUser.objects
        .select_related("business", "user")
        .filter(
            user=user,
            is_active=True,
            business__status=True,
        )
    )
    for assignment in assignments:
        if normalize_role(assignment.role) in SUPER_ADMIN_ROLES:
            return assignment
    return assignments[0] if assignments else None


def get_fallback_business(user):
    owned = (
        Business.objects.filter(status=True, owner=user).order_by("name").first()
        or Business.objects.filter(status=True, created_by=user).order_by("name").first()
    )
    if owned:
        return owned
    return Business.objects.filter(status=True).order_by("name").first()


# =========================================================
# CHECK PERMISSION
# =========================================================

def has_permission(business_user, permission):
    """
    Check whether the BusinessUser has a specific permission.
    """

    if not business_user:
        return False

    if not business_user.is_active:
        return False

    if is_full_access(getattr(business_user, "user", None), business_user):
        return True

    role_permissions = ROLE_PERMISSIONS.get(
        normalize_role(business_user.role),
        set()
    )

    if "*" in role_permissions:
        return True

    return permission in role_permissions


# =========================================================
# CHECK ROLE
# =========================================================

def has_role(business_user, role):
    """
    Check whether the BusinessUser has the specified role.
    """

    if not business_user:
        return False

    if not business_user.is_active:
        return False

    return normalize_role(business_user.role) == normalize_role(role)


# =========================================================
# CHECK ANY ROLE
# =========================================================

def has_any_role(business_user, roles):
    """
    Check whether the BusinessUser has one of the
    supplied roles.
    """

    if not business_user:
        return False

    if not business_user.is_active:
        return False

    return normalize_role(business_user.role) in {normalize_role(role) for role in roles}


# =========================================================
# PERMISSION DECORATOR
# =========================================================

def permission_required(permission):
    """
    Central permission decorator.

    Example:

        @permission_required("goat.create")
        def goat_create(request):
            ...
    """

    def decorator(view_func):

        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):

            # -------------------------------------------------
            # Get BusinessUser
            # -------------------------------------------------

            business_user = get_business_user(request.user)

            if is_full_access(request.user, business_user):
                request.business_user = business_user
                request.business = (
                    business_user.business if business_user else get_fallback_business(request.user)
                )
                if request.business is None and permission != "dashboard.view":
                    messages.error(
                        request,
                        "No active business is available yet. Create a business first.",
                    )
                    return redirect("dashboard")
                return view_func(request, *args, **kwargs)

            if not business_user:
                if permission == "dashboard.view":
                    request.business_user = None
                    request.business = None
                    return view_func(request, *args, **kwargs)

                messages.error(
                    request,
                    "You are not assigned to an active business yet. Please contact your administrator.",
                )
                return redirect("dashboard")

            if not has_permission(business_user, permission):
                messages.error(request, "You do not have permission to access this page.")
                return redirect("dashboard")

            request.business_user = business_user
            request.business = business_user.business

            # -------------------------------------------------
            # Execute original view
            # -------------------------------------------------

            return view_func(
                request,
                *args,
                **kwargs
            )

        return wrapper

    return decorator