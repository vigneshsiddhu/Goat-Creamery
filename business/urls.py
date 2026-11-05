from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "business"

urlpatterns = [
    # =====================================================
    # BUSINESS
    # =====================================================
    path("",views.business_list,name="list"),
    path("add/",views.business_create,name="create"),
    path("<uuid:pk>/edit/",views.business_edit,name="update"),
    path("<uuid:pk>/delete/",views.business_delete,name="delete"),
    # =====================================================
    # BUSINESS USERS
    # =====================================================
    path("business-users/",views.business_user_list,name="business_user_list"),
    path("business-users/create/",views.business_user_create,name="business_user_create"),
    path("business-users/<uuid:pk>/edit/",views.business_user_edit,name="business_user_edit"),
    path("business-users/<uuid:pk>/delete/",views.business_user_delete,name="business_user_delete"),
    # =====================================================
    # BUSINESS USERS
    # =====================================================
    path("locations/",views.location_list,name="location_list"),
    path("locations/create/",views.location_create,name="location_create"),
    path("locations/<uuid:pk>/edit/",views.location_edit,name="location_edit"),
    path("locations/<uuid:pk>/delete/",views.location_delete,name="location_delete"),
    path("location", RedirectView.as_view(pattern_name="business:location_list", permanent=False)),
    path("location/", RedirectView.as_view(pattern_name="business:location_list", permanent=False)),
]
