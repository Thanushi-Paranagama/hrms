# attendance/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_dashboard, name='attendance_dashboard'),
    path('mark/', views.attendance_mark, name='attendance_mark'),
    path('report/<str:employee_id>/', views.attendance_report, name='attendance_report'),
    path('monthly-summary/', views.attendance_monthly_summary, name='attendance_monthly_summary'),
]