from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("sales/", views.sales, name="sales"),
    path("goat-milk/", views.milk, name="milk"),
    path("goat-weight/", views.weight, name="weight"),
]
