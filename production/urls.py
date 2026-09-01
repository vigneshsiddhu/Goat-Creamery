from django.urls import path

from . import views


app_name = "production"


urlpatterns = [

    # =====================================================
    # GOAT WEIGHT
    # =====================================================

    path(
        "goat-weight/",
        views.goat_weight_list,
        name="goat_weight_list"
    ),

    path(
        "goat-weight/create/",
        views.goat_weight_create,
        name="goat_weight_create"
    ),
    path(
        "goat-weight/voice/create/",
        views.goat_weight_voice_create,
        name="goat_weight_voice_create"
    ),

    path(
        "goat-weight/<uuid:id>/edit/",
        views.goat_weight_update,
        name="goat_weight_update"
    ),

    path(
        "goat-weight/<uuid:id>/delete/",
        views.goat_weight_delete,
        name="goat_weight_delete"
    ),


    # =====================================================
    # GOAT MILK
    # =====================================================

    path(
        "goat-milk/",
        views.goat_milk_list,
        name="goat_milk_list"
    ),

    path(
        "goat-milk/create/",
        views.goat_milk_create,
        name="goat_milk_create"
    ),
    path(
            "goat-milk/voice/create/",
            views.goat_milk_voice_create,
            name="goat_milk_voice_create"
        ),

    path(
        "goat-milk/<uuid:id>/edit/",
        views.goat_milk_update,
        name="goat_milk_update"
    ),

    path(
        "goat-milk/<uuid:id>/delete/",
        views.goat_milk_delete,
        name="goat_milk_delete"
    ),
]