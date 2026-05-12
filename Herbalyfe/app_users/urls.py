from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),  # URL for user registration
    path('login/', views.login_view, name="login"),  # URL for user login
    path('logout/', views.logout_view, name='logout'),  # URL for user logout
    path('profile/', views.profile_view, name='profile'),  # URL for user profile
    path("password-recovery/", views.password_recovery, name="password_recovery"), # URL for password recovery
    path("password-recovery/verify/", views.verify_code, name="verify_code"), # URL for verifying recovery code
    path("password-recovery/reset/", views.reset_password_view, name="reset_password"), # URL for resetting password after verification
]
