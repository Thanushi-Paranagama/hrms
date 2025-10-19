# salary/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.salary_dashboard, name='salary_dashboard'),
    path('generate/', views.salary_generate, name='salary_generate'),
    path('report/<str:employee_id>/', views.salary_report, name='salary_report'),
    path('mark-paid/<int:salary_id>/', views.salary_mark_paid, name='salary_mark_paid'),
]
