from django.urls import path
from . import views


app_name = "inventory"


urlpatterns = [

    # ========================================================
    # ITEM    
    # # ========================================================
    path("items/",views.item_list,name="item_list"),
    path("items/create/",views.item_create,name="item_create"),
    path("items/<uuid:pk>/edit/",views.item_edit,name="item_edit"),
    path("items/<uuid:pk>/delete/",views.item_delete,name="item_delete"),


    # ========================================================
    # VEHICLE    
    # # ========================================================
    path("vehicles/",views.vehicle_list,name="vehicle_list"),
    path("vehicles/create/",views.vehicle_create,name="vehicle_create"),
    path("vehicles/<uuid:pk>/edit/",views.vehicle_edit,name="vehicle_edit"),
    path("vehicles/<uuid:pk>/delete/",views.vehicle_delete,name="vehicle_delete"),


    # ========================================================
    # VEHICLE LOCATION    
    # # ========================================================
    path("vehicle-locations/",views.vehicle_location_list,name="vehicle_location_list"),
    path("vehicle-locations/create/",views.vehicle_location_create,name="vehicle_location_create"),
    path("vehicle-locations/<uuid:pk>/edit/",views.vehicle_location_edit,name="vehicle_location_edit"),
    path("vehicle-locations/<uuid:pk>/delete/",views.vehicle_location_delete,name="vehicle_location_delete"),


    # ========================================================
    # ITEM LOCATION    
    # # ========================================================
    path("item-locations/",views.item_location_list,name="item_location_list"),
    path("item-locations/create/",views.item_location_create,name="item_location_create"),
    path("item-locations/<uuid:pk>/edit/",views.item_location_edit,name="item_location_edit"),
    path("item-locations/<uuid:pk>/delete/",views.item_location_delete,name="item_location_delete"),
]