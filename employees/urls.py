# employees/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('<str:employee_id>/', views.employee_detail, name='employee_detail'),
    path('create/', views.employee_create, name='employee_create'),
    path('update/<str:employee_id>/', views.employee_update, name='employee_update'),
]