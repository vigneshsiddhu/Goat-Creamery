from django.urls import path

from . import views


app_name = "inventory"


urlpatterns = [

    path(
        "feedstock/",
        views.feedstock_list,
        name="feedstock_list"
    ),

    path(
        "feedstock/create/",
        views.feedstock_create,
        name="feedstock_create"
    ),

    path(
        "feedstock/<uuid:pk>/edit/",
        views.feedstock_update,
        name="feedstock_update"
    ),

    path(
        "feedstock/<uuid:pk>/delete/",
        views.feedstock_delete,
        name="feedstock_delete"
    ),

]