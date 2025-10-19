# workforce_calendar/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar_view'),
    path('my-calendar/', views.my_calendar, name='my_calendar'),
    path('event/create/', views.event_create, name='event_create'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/update/<int:event_id>/', views.event_update, name='event_update'),
    path('event/delete/<int:event_id>/', views.event_delete, name='event_delete'),
    path('check-conflict/', views.check_schedule_conflict, name='check_schedule_conflict'),
]