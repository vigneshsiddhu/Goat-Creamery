from django.urls import path
from . import views

app_name = "goats"
urlpatterns = [
    path("",views.goat_list,name="list"),
    path("create/",views.goat_create,name="create"),
    path("<uuid:id>/edit/",views.goat_update,name="update"),
    path("<uuid:id>/delete/",views.goat_delete,name="delete"),
    path("diseases/",views.disease_list,name="disease_list"),
    path("diseases/create/",views.disease_create,name="disease_create"),
    path("diseases/<uuid:pk>/edit/",views.disease_update,name="disease_update"),
    path("diseases/<uuid:pk>/delete/",views.disease_delete,name="disease_delete"),
    path("death-goats/",views.death_goat_list,name="death_goat_list"),
    path("death-goats/create/",views.death_goat_create,name="death_goat_create"),
    path("death-goats/<uuid:pk>/edit/",views.death_goat_update,name="death_goat_update"),
    path("death-goats/<uuid:pk>/delete/",views.death_goat_delete,name="death_goat_delete"),
    path("health/",views.goat_health_list,name="goat_health_list"),
    path("health/create/",views.goat_health_create,name="goat_health_create"),
    path("health/<uuid:pk>/edit/",views.goat_health_update,name="goat_health_update"),
    path("health/<uuid:pk>/delete/",views.goat_health_delete,name="goat_health_delete"),
]