from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('detect/', views.detect_violation, name='detect_violation'),
    path('logs/', views.violation_logs, name='violation_logs'),
    path('repeat-offenders/', views.repeat_offenders, name='repeat_offenders'),
    path('delete-violation/<int:violation_id>/', views.delete_violation, name='delete_violation'),
    path('delete-offender/<str:plate_number>/', views.delete_offender, name='delete_offender'),
    path('delete-all/', views.delete_all_violations, name='delete_all_violations'),
    path('offender-logs/<str:plate_number>/', views.offender_logs, name='offender_logs'),
]
