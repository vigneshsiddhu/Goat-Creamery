from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("employees/",views.employee_list,name="employee_list"),
    path("employees/create/",views.employee_create,name="employee_create"),
    path("employees/<uuid:pk>/edit/",views.employee_edit,name="employee_edit"),
    path("employees/<uuid:pk>/delete/",views.employee_delete,name="employee_delete"),

    path("employee-salaries/",views.employee_salary_list,name="employee_salary_list"),
    path("employee-salaries/create/",views.employee_salary_create,name="employee_salary_create"),
    path("employee-salaries/<uuid:pk>/edit/",views.employee_salary_edit,name="employee_salary_edit"),
    path("employee-salaries/<uuid:pk>/delete/",views.employee_salary_delete,name="employee_salary_delete"),

    path("farm-spend-books/",views.farm_spend_book_list,name="farm_spend_book_list"),
    path("farm-spend-books/create/",views.farm_spend_book_create,name="farm_spend_book_create"),
    path("farm-spend-books/<uuid:pk>/edit/",views.farm_spend_book_edit,name="farm_spend_book_edit"),
    path("farm-spend-books/<uuid:pk>/delete/",views.farm_spend_book_delete,name="farm_spend_book_delete"),

    path("farm-spend-items/",views.farm_spend_item_list,name="farm_spend_item_list"),
    path("farm-spend-items/create/",views.farm_spend_item_create,name="farm_spend_item_create"),
    path("farm-spend-items/<uuid:pk>/edit/",views.farm_spend_item_edit,name="farm_spend_item_edit"),
    path("farm-spend-items/<uuid:pk>/delete/",views.farm_spend_item_delete,name="farm_spend_item_delete"),

    path("farm-expenses/",views.farm_expense_list,name="farm_expense_list"),
    path("farm-expenses/create/",views.farm_expense_create,name="farm_expense_create"),
    path("farm-expenses/<uuid:pk>/edit/",views.farm_expense_edit,name="farm_expense_edit"),
    path("farm-expenses/<uuid:pk>/delete/",views.farm_expense_delete,name="farm_expense_delete"),

    path("business-spend-books/",views.business_spend_book_list,name="business_spend_book_list"),
    path("business-spend-books/create/",views.business_spend_book_create,name="business_spend_book_create"),
    path("business-spend-books/<uuid:pk>/edit/",views.business_spend_book_edit,name="business_spend_book_edit"),
    path("business-spend-books/<uuid:pk>/delete/",views.business_spend_book_delete,name="business_spend_book_delete"),

    path("business-spend-items/",views.business_spend_item_list,name="business_spend_item_list"),
    path("business-spend-items/create/",views.business_spend_item_create,name="business_spend_item_create"),
    path("business-spend-items/<uuid:pk>/edit/",views.business_spend_item_edit,name="business_spend_item_edit"),
    path("business-spend-items/<uuid:pk>/delete/",views.business_spend_item_delete,name="business_spend_item_delete"),

    path("business-expenses/",views.business_expense_list,name="business_expense_list"),
    path("business-expenses/create/",views.business_expense_create,name="business_expense_create"),
    path("business-expenses/<uuid:pk>/edit/",views.business_expense_edit,name="business_expense_edit"),
    path("business-expenses/<uuid:pk>/delete/",views.business_expense_delete,name="business_expense_delete"),
]