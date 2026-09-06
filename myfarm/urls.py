"""
URL configuration for myfarm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views
from user_registrations import views as user_views

urlpatterns = [
    #Added for PWA
    path(
        'service-worker.js',
        views.service_worker,
        name='service_worker'
    ),  
    path('admin/', admin.site.urls),
    path('users/', include('user_registrations.urls')),
    path('', user_views.dashboard, name='dashboard'),
    # path('', user_views.dashboard, name='home'),
    path("goats/",include("goats.urls")),
    path('business/', include('business.urls')),
    path('breeding/', include('breeding.urls')),    
    path('production/', include('production.urls')),
    path('inventory/', include('inventory.urls')),
    path('finance/', include('finance.urls')),
    path('reports/', include('reports.urls')),
    path('farm/', include('farm.urls')),
    path('sales/', include('sales.urls')),
]

