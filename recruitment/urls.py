# recruitment/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.recruitment_list, name='recruitment_list'),
    path('create/', views.recruitment_create, name='recruitment_create'),
    path('detail/<int:recruitment_id>/', views.recruitment_detail, name='recruitment_detail'),
    path('update-status/<int:recruitment_id>/', views.recruitment_update_status, name='recruitment_update_status'),
    path('hire/<int:recruitment_id>/', views.recruitment_hire, name='recruitment_hire'),
]