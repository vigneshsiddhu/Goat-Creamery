from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum
from myfarm.permissions import permission_required
from django.utils import timezone
from .forms import FarmExpenseForm
from .models import FarmExpense
from business.models import Business


# =========================================================
# FARM EXPENSE LIST
# =========================================================

@permission_required("expense.view")
def farm_expense_list(request):
    business = request.business
    if not business:
        messages.error(
            request,
            "Please select a business first."
        )
        return redirect("business:list")
    # =====================================================
    # ALL EXPENSES
    # =====================================================
    expenses = FarmExpense.objects.filter(
        business=business
    ).select_related(
        "created_by"
    )
    # =====================================================
    # CURRENT DATE
    # =====================================================
    today = timezone.localdate()
    current_year = today.year
    current_month = today.month
    # =====================================================
    # CURRENT MONTH
    # =====================================================
    current_month_expenses = expenses.filter(
        date__year=current_year,
        date__month=current_month
    )
    current_month_total = (
        current_month_expenses.aggregate(
            total=Sum("amount")
        )["total"] or 0
    )
    # =====================================================
    # TODAY
    # =====================================================
    today_total = (
        expenses.filter(
            date=today
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0
    )
    # =====================================================
    # LAST MONTH
    # =====================================================
    if current_month == 1:
        last_month = 12
        last_month_year = current_year - 1
    else:
        last_month = current_month - 1
        last_month_year = current_year
    last_month_expenses = expenses.filter(
        date__year=last_month_year,
        date__month=last_month
    )
    last_month_total = (
        last_month_expenses.aggregate(
            total=Sum("amount")
        )["total"] or 0
    )
    # =====================================================
    # LAST MONTH CATEGORY SPENDING
    # =====================================================
    category_expenses = (
        last_month_expenses
        .values("category")
        .annotate(
            total=Sum("amount")
        )
        .order_by("-total")
    )
    return render(
        request,
        "farm_expenses/farm_expense_list.html",
        {
            "expenses": expenses,
            "business": business,
            # Summary
            "last_month_total": last_month_total,
            "current_month_total": current_month_total,
            "today_total": today_total,
            # Category
            "category_expenses": category_expenses,
            # Month names
            "last_month_name": (
                timezone.datetime(
                    last_month_year,
                    last_month,
                    1
                ).strftime("%B")
            ),
            "current_month_name": today.strftime("%B"),
        }
    )


# =========================================================
# FARM EXPENSE CREATE
# =========================================================

@permission_required("expense.create")
def farm_expense_create(request):

    business = request.business

    if request.method == "POST":

        form = FarmExpenseForm(
            request.POST
        )

        if form.is_valid():

            expense = form.save(
                commit=False
            )

            # -------------------------------------------------
            # Business comes from logged-in user's business
            # -------------------------------------------------

            expense.business = business

            # -------------------------------------------------
            # Created by current logged-in user
            # -------------------------------------------------

            expense.created_by = request.user

            expense.save()

            messages.success(
                request,
                "Farm expense created successfully."
            )

            return redirect(
                "finance:farm_expense_list"
            )

    else:

        form = FarmExpenseForm()

    return render(
        request,
        "farm_expenses/farm_expense_form.html",
        {
            "form": form,
            "business": business,
            "expense": None,
        }
    )


# =========================================================
# FARM EXPENSE UPDATE
# =========================================================

@permission_required("expense.update")
def farm_expense_update(request, pk):

    business = request.business

    # -----------------------------------------------------
    # Only allow expense belonging to current business
    # -----------------------------------------------------

    expense = get_object_or_404(
        FarmExpense,
        id=pk,
        business=business
    )

    if request.method == "POST":

        form = FarmExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():

            updated_expense = form.save(
                commit=False
            )

            # -------------------------------------------------
            # Never allow business to change
            # -------------------------------------------------

            updated_expense.business = business

            # -------------------------------------------------
            # Never change created_by
            # -------------------------------------------------

            updated_expense.created_by = (
                expense.created_by
            )

            updated_expense.save()

            messages.success(
                request,
                "Farm expense updated successfully."
            )

            return redirect(
                "finance:farm_expense_list"
            )

    else:

        form = FarmExpenseForm(
            instance=expense
        )

    return render(
        request,
        "farm_expenses/farm_expense_form.html",
        {
            "form": form,
            "business": business,
            "expense": expense,
        }
    )


# =========================================================
# FARM EXPENSE DELETE
# =========================================================

@permission_required("expense.delete")
def farm_expense_delete(request, pk):

    business = request.business

    # -----------------------------------------------------
    # Only allow expense belonging to current business
    # -----------------------------------------------------

    expense = get_object_or_404(
        FarmExpense,
        id=pk,
        business=business
    )

    if request.method == "POST":

        expense.delete()

        messages.success(
            request,
            "Farm expense deleted successfully."
        )

        return redirect(
            "finance:farm_expense_list"
        )

    return render(
        request,
        "farm_expenses/farm_expense_delete.html",
        {
            "expense": expense,
            "business": business,
        }
    )