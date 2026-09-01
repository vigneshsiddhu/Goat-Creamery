from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

from .forms import LoginForm, SignupForm
import pdb
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
    return render(
        request,
        "user_registrations/dashboard.html",
        {
            "business": request.business,
            "business_user": request.business_user,
        }
    )