from django.urls import path
from . import views

app_name = 'illnesses'

urlpatterns = [
    path('', views.illness_list, name="illnesses_list"), # URL for the illness list page
    path('<slug:slug>', views.illness_page, name="illness_page"), # Dynamic URL for individual illness pages
]
