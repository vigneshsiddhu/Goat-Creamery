from django.urls import path
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
]
