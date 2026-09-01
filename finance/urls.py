from django.urls import path

from . import views


app_name = "finance"


urlpatterns = [

    path(
        "farm_expenses/",
        views.farm_expense_list,
        name="farm_expense_list"
    ),

    path(
        "farm_expenses/create/",
        views.farm_expense_create,
        name="farm_expense_create"
    ),

    path(
        "farm_expenses/<uuid:pk>/edit/",
        views.farm_expense_update,
        name="farm_expense_update"
    ),

    path(
        "farm_expenses/<uuid:pk>/delete/",
        views.farm_expense_delete,
        name="farm_expense_delete"
    ),

]