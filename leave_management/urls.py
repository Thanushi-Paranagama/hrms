# leave_management/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.leave_request_list, name='leave_request_list'),
    path('create/', views.leave_request_create, name='leave_request_create'),
    path('employee_search/', views.employee_search, name='employee_search'),
    path('approve/<int:leave_id>/', views.leave_request_approve, name='leave_request_approve'),
    path('cancel/<int:leave_id>/', views.leave_request_cancel, name='leave_request_cancel'),
]