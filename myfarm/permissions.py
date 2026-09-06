# myfarm/permissions.py
from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import pdb
from business.models import BusinessUser


# =========================================================
# ROLE PERMISSIONS
# =========================================================

ROLE_PERMISSIONS = {
    # =====================================================
    # SUPER ADMIN
    # =====================================================

    # =========================================================
# SUPER ADMIN
# =========================================================
    "SUPER_ADMIN": {
        # =====================================================
        # DASHBOARD
        # =====================================================
        "dashboard.view",
        # =====================================================
        # BUSINESS
        # =====================================================
        "business.view",
        "business.create",
        "business.update",
        "business.delete",
        # =====================================================
        # BUSINESS USERS
        # =====================================================
        "business_user.view",
        "business_user.create",
        "business_user.update",
        "business_user.delete",
        # =====================================================
        # LOCATION
        # =====================================================
        "location.view",
        "location.create",
        "location.update",
        "location.delete",
        # =====================================================
        # GOAT
        # =====================================================
        "goat.view",
        "goat.create",
        "goat.update",
        "goat.delete",
        # =====================================================
        # GOAT DISEASE
        # =====================================================
        "goat_disease.view",
        "goat_disease.create",
        "goat_disease.update",
        "goat_disease.delete",
        # =====================================================
        # GOAT HEALTH
        # =====================================================
        "goat_health.view",
        "goat_health.create",
        "goat_health.update",
        "goat_health.delete",
        # =====================================================
        # GOAT DEATH
        # =====================================================
        "goat_death.view",
        "goat_death.create",
        "goat_death.update",
        "goat_death.delete",
        # =====================================================
        # GOAT WEIGHT
        # =====================================================
        "weight.view",
        "weight.create",
        "weight.update",
        "weight.delete",
        # =====================================================
        # GOAT MILK
        # =====================================================
        "milk.view",
        "milk.create",
        "milk.update",
        "milk.delete",
        # =====================================================
        # MILK BATCH
        # =====================================================
        "milk_batch.view",
        "milk_batch.create",
        "milk_batch.update",
        "milk_batch.delete",
        # =====================================================
        # MILK TEST
        # =====================================================
        "milk_test.view",
        "milk_test.create",
        "milk_test.update",
        "milk_test.delete",
        # =====================================================
        # BREEDING / MATING
        # =====================================================
        "mating.view",
        "mating.create",
        "mating.update",
        "mating.delete",
        # =====================================================
        # PARENT MAPPING
        # =====================================================
        "parent_mapping.view",
        "parent_mapping.create",
        "parent_mapping.update",
        "parent_mapping.delete",
        # =====================================================
        # PRODUCTION - PRODUCTS
        # =====================================================
        "product.view",
        "product.create",
        "product.update",
        "product.delete",
        # =====================================================
        # PRODUCTION - PRODUCT PRICE
        # =====================================================
        "product_price.view",
        "product_price.create",
        "product_price.update",
        "product_price.delete",
        # =====================================================
        # PRODUCTION - INGREDIENT
        # =====================================================
        "ingredient.view",
        "ingredient.create",
        "ingredient.update",
        "ingredient.delete",
        # =====================================================
        # PRODUCTION - INGREDIENT PRICE
        # =====================================================
        "ingredient_price.view",
        "ingredient_price.create",
        "ingredient_price.update",
        "ingredient_price.delete",
        # =====================================================
        # PRODUCTION - RECIPE
        # =====================================================
        "recipe.view",
        "recipe.create",
        "recipe.update",
        "recipe.delete",
        # =====================================================
        # PRODUCTION - RECIPE ITEM
        # =====================================================
        "recipe_item.view",
        "recipe_item.create",
        "recipe_item.update",
        "recipe_item.delete",
        # =====================================================
        # PRODUCTION - PRODUCT BATCH
        # =====================================================
        "product_batch.view",
        "product_batch.create",
        "product_batch.update",
        "product_batch.delete",
        # =====================================================
        # INVENTORY - ITEM
        # =====================================================
        "item.view",
        "item.create",
        "item.update",
        "item.delete",
        # =====================================================
        # INVENTORY - VEHICLE
        # =====================================================
        "vehicle.view",
        "vehicle.create",
        "vehicle.update",
        "vehicle.delete",
        # =====================================================
        # INVENTORY - VEHICLE LOCATION
        # =====================================================
        "vehicle_location.view",
        "vehicle_location.create",
        "vehicle_location.update",
        "vehicle_location.delete",
       
        # =====================================================
        # FINANCE - EMPLOYEE
        # =====================================================
        "employee.view",
        "employee.create",
        "employee.update",
        "employee.delete",
        # =====================================================
        # FINANCE - EMPLOYEE SALARY
        # =====================================================
        "employee_salary.view",
        "employee_salary.create",
        "employee_salary.update",
        "employee_salary.delete",
        # =====================================================
        # FINANCE - FARM SPEND BOOK
        # =====================================================
        "farm_spend_book.view",
        "farm_spend_book.create",
        "farm_spend_book.update",
        "farm_spend_book.delete",
        # =====================================================
        # FINANCE - FARM EXPENSE
        # =====================================================
        "farm_expense.view",
        "farm_expense.create",
        "farm_expense.update",
        "farm_expense.delete",
        # =====================================================
        # FINANCE - BUSINESS SPEND BOOK
        # =====================================================
        "business_spend_book.view",
        "business_spend_book.create",
        "business_spend_book.update",
        "business_spend_book.delete",
        # =====================================================
        # FINANCE - BUSINESS EXPENSE
        # =====================================================
        "business_expense.view",
        "business_expense.create",
        "business_expense.update",
        "business_expense.delete",
        # =====================================================
        # SALES - CUSTOMER
        # =====================================================
        "customer.view",
        "customer.create",
        "customer.update",
        "customer.delete",
        # =====================================================
        # SALES - INVOICE
        # =====================================================
        "invoice.view",
        "invoice.create",
        "invoice.update",
        "invoice.delete",
        # =====================================================
        # SALES - INVOICE ITEM
        # =====================================================
        "invoice_item.view",
        "invoice_item.create",
        "invoice_item.update",
        "invoice_item.delete",
        # =====================================================
        # SALES - INVOICE LOCATION
        # =====================================================
        "invoice_location.view",
        "invoice_location.create",
        "invoice_location.update",
        "invoice_location.delete",
        # =====================================================
        # REPORTS
        # =====================================================
        "reports.view",
        "reports.export",
        # =====================================================
        # SETTINGS
        # =====================================================
        "settings.view",
        "settings.update",
    },


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

    Also loads the related business in the same query.
    """

    return (
        BusinessUser.objects
        .select_related("business")
        .filter(
            user=user,
            is_active=True,
            business__status=True,
        )
        .first()
    )


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

    role_permissions = ROLE_PERMISSIONS.get(
        business_user.role,
        set()
    )

    # Optional wildcard support
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

    return business_user.role == role


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

    return business_user.role in roles


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

            business_user = get_business_user(
                request.user
            )

            # -------------------------------------------------
            # No active business assignment
            # -------------------------------------------------

            if not business_user:

                # Dashboard is accessible even without

                # business assignment.

                if permission == "dashboard.view":
                    request.business_user = None
                    request.business = None
                    return view_func(request,*args,**kwargs)

                messages.error(request,"You are not assigned to an active business yet. ""Please contact your administrator.")
                return redirect("dashboard")

            # -------------------------------------------------
            # Check permission
            # -------------------------------------------------

            if not has_permission(
                business_user,
                permission
            ):

                messages.error(
                    request,
                    "You do not have permission to access this page."
                )

                return redirect("dashboard")

            # -------------------------------------------------
            # Attach business information to request
            # -------------------------------------------------

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