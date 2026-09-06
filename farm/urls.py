from django.urls import path
from . import views

app_name = "farm"

urlpatterns = [
    path("land/",views.land_list,name="land_list"),
    path("land/create/",views.land_create,name="land_create"),
    path("land/<uuid:pk>/edit/",views.land_edit,name="land_edit"),
    path("land/<uuid:pk>/delete/",views.land_delete,name="land_delete"),

    path("water/",views.water_list,name="water_list"),
    path("water/create/",views.water_create,name="water_create"),
    path("water/<uuid:pk>/edit/",views.water_edit,name="water_edit"),
    path("water/<uuid:pk>/delete/",views.water_delete,name="water_delete"),

    path("land-water/",views.land_water_list,name="land_water_list"),
    path("land-water/create/",views.land_water_create,name="land_water_create"),
    path("land-water/<uuid:pk>/edit/",views.land_water_edit,name="land_water_edit"),
    path("land-water/<uuid:pk>/delete/",views.land_water_delete,name="land_water_delete"),

    path("feedstock/",views.feedstock_list,name="feedstock_list"),
    path("feedstock/create/",views.feedstock_create,name="feedstock_create"),
    path("feedstock/<uuid:pk>/edit/",views.feedstock_edit,name="feedstock_edit"),
    path("feedstock/<uuid:pk>/delete/",views.feedstock_delete,name="feedstock_delete"),

    path("feedstock-transaction/",views.feedstock_transaction_list,name="feedstock_transaction_list"),
    path("feedstock-transaction/create/",views.feedstock_transaction_create,name="feedstock_transaction_create"),
    path("feedstock-transaction/<uuid:pk>/edit/",views.feedstock_transaction_edit,name="feedstock_transaction_edit"),
    path("feedstock-transaction/<uuid:pk>/delete/",views.feedstock_transaction_delete,name="feedstock_transaction_delete"),

    path("feed-consumption/",views.feed_consumption_list,name="feed_consumption_list"),
    path("feed-consumption/create/",views.feed_consumption_create,name="feed_consumption_create"),
    path("feed-consumption/<uuid:pk>/edit/",views.feed_consumption_edit,name="feed_consumption_edit"),
    path("feed-consumption/<uuid:pk>/delete/",views.feed_consumption_delete,name="feed_consumption_delete"),
]