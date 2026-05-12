from django.urls import path
from . import views

app_name = 'herbs'

urlpatterns = [
    path('', views.herb_list, name="herbs_list"), # URL for the herb list page
    path('<slug:slug>', views.herb_page, name="herb_page"), # Dynamic URL for individual herb pages
    path('pin/', views.pin_herb, name='pin_herb'),
    path('coords/', views.herb_coords, name='herb_coords'),
    path('list_json/', views.herb_list_json, name='herb_list_json'),
    path('pins/', views.herb_pins_json, name='herb_pins_json'), # URL for fetching herb pins in JSON format
    path('pin/<int:pin_id>/delete/', views.delete_herb_pin, name='delete_herb_pin'), # URL for deleting a specific herb pin
    path('pin_users/', views.pin_users, name='pin_users'), # URL for fetching users who have pinned herbs
    path('favorite_pins_json/', views.favorite_pins_json, name='favorite_pins_json'), # URL for fetching favorite herb pins in JSON format
    path('toggle_favorite/<int:pin_id>/', views.toggle_favorite, name='toggle_favorite'), # URL for toggling favorite status of a herb pin
]
