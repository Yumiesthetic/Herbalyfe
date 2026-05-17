from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name="register"),

    path(
        'register/verify/',
        views.verify_code,
        name="register_verify"
    ),

    path('login/', views.login_view, name="login"),

    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),

    path(
        'delete-account/',
        views.delete_account_view,
        name='delete_account'
    ),

    path(
        'delete-account/final/',
        views.delete_account_final_view,
        name='delete_account_final'
    ),

    path(
        "password-recovery/",
        views.password_recovery,
        name="password_recovery"
    ),

    path(
        "password-recovery/verify/",
        views.verify_code,
        name="verify_code"
    ),

    path(
        "password-recovery/reset/",
        views.reset_password_view,
        name="reset_password"
    ),
    
    path(
        "change-email/verify/",
        views.verify_code,
        name="change_email_verify"
    ),
    
]