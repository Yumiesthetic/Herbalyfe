from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path(
        '',
        views.report_list,
        name='report_list'
    ),

    path(
        'submit/<int:pin_id>/',
        views.submit_report,
        name='submit_report'
    ),

    path(
        'update/<int:report_id>/<str:status>/',
        views.update_report_status,
        name='update_report_status'
    ),

    path(
        'clear_logs/',
        views.clear_logs,
        name='clear_logs'
    ),
]