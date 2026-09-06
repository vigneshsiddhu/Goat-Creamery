from django.urls import path
from . import views


app_name = "sales"


urlpatterns = [

    # ========================================================
    # CUSTOMER
    # ========================================================

    path("customers/",views.customer_list,name="customer_list"),
    path("customers/create/",views.customer_create,name="customer_create"),
    path("customers/<uuid:pk>/edit/",views.customer_edit,name="customer_edit"),
    path("customers/<uuid:pk>/delete/",views.customer_delete,name="customer_delete"),


    # ========================================================
    # INVOICE
    # ========================================================

    path("invoices/",views.invoice_list,name="invoice_list"),
    path("invoices/create/",views.invoice_create,name="invoice_create"),
    path("invoices/<uuid:pk>/edit/",views.invoice_edit,name="invoice_edit"),
    path("invoices/<uuid:pk>/delete/",views.invoice_delete,name="invoice_delete"),


   
    # ========================================================
    # INVOICE LOCATION
    # ========================================================

    path("invoice-locations/",views.invoice_location_list,name="invoice_location_list"),
    path("invoice-locations/create/",views.invoice_location_create,name="invoice_location_create"),
    path("invoice-locations/<uuid:pk>/edit/",views.invoice_location_edit,name="invoice_location_edit"),
    path("invoice-locations/<uuid:pk>/delete/",views.invoice_location_delete,name="invoice_location_delete"),
]