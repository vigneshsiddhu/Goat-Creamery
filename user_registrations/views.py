from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from goats.models import Goat
from reports.pages import milk_report, sales_report, weight_report
from reports.stats import overview_cards

from .forms import LoginForm, SignupForm
from myfarm.permissions import permission_required


# =========================================================
# SIGN UP
# =========================================================

def signup(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("login")

    else:

        form = SignupForm()

    return render(
        request,
        "user_registrations/signup.html",
        {
            "form": form
        }
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        form = LoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            next_url = request.POST.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("dashboard")

    else:

        form = LoginForm()

    return render(
        request,
        "user_registrations/login.html",
        {
            "form": form
        }
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect("login")


# =========================================================
# DASHBOARD
# =========================================================

@permission_required("dashboard.view")
def dashboard(request):
    business = getattr(request, "business", None)
    context = {
        "business": business,
        "business_user": getattr(request, "business_user", None),
    }
    if business:
        today = timezone.localdate()
        pulse = overview_cards(business, today)
        sales = sales_report(business, today)
        milk = milk_report(business, today)
        weight = weight_report(business, today)
        cards = {card["key"]: card for card in pulse["cards"]}
        context.update(
            {
                "period_start": pulse["period_start"],
                "period_end": pulse["period_end"],
                "live_goats": Goat.objects.filter(business=business, live=True).count(),
                "milk_card": cards.get("milk"),
                "sales_card": cards.get("sales"),
                "weight_card": cards.get("weight"),
                "sales_map": sales["map"],
                "milk_tiles": milk["tiles"],
                "weight_tiles": weight["tiles"],
                "mix_charts": {
                    "mix": {
                        "labels": milk["charts"]["daily"]["labels"],
                        "milk": milk["charts"]["daily"]["values"],
                        "sales": sales["charts"]["daily"]["values"],
                    }
                },
            }
        )
    return render(request, "user_registrations/dashboard.html", context)