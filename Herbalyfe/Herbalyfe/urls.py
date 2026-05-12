"""
URL configuration for Herbalyfe project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from . import views
from django.conf.urls.static import static # Import static to serve media files during development
from django.conf import settings # Import settings to access MEDIA_URL and MEDIA_ROOT


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_page),
    path('map/', views.map_page),
    path('herbs/', include('app_herbs.urls')), # Added herbs app URLs
    path('illnesses/', include('app_illnesses.urls')), # Added illnesses app URLs
    path('users/', include('app_users.urls')), # Added users app URLs
    path('reports/', include('app_reports.urls')), # Added reports app URLs
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Serving media files during development