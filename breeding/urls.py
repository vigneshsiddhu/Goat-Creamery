from django.urls import path
from . import views

app_name = "breeding"

urlpatterns = [

    # Mating
    path(
        "mating/",
        views.mating_list,
        name="mating_list"
    ),

    path(
        "mating/create/",
        views.mating_create,
        name="mating_create"
    ),

    path(
        "mating/<uuid:id>/edit/",
        views.mating_update,
        name="mating_update"
    ),

    path(
        "mating/<uuid:id>/delete/",
        views.mating_delete,
        name="mating_delete"
    ),

    # Parent Mapping
    path(
        "parent-mapping/",
        views.parent_mapping_list,
        name="parent_mapping_list"
    ),

    path(
        "parent-mapping/create/",
        views.parent_mapping_create,
        name="parent_mapping_create"
    ),

    path(
        "parent-mapping/<uuid:id>/edit/",
        views.parent_mapping_update,
        name="parent_mapping_update"
    ),

    path(
        "parent-mapping/<uuid:id>/delete/",
        views.parent_mapping_delete,
        name="parent_mapping_delete"
    ),
]