"""
URL configuration for smart_hr_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api import views as api_views
from . import views

urlpatterns = [
    # Authentication
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),

    
    # Admin
    path('admin/', admin.site.urls),
    
    # App URLs
    path('employees/', include('employees.urls')),
    path('attendance/', include('attendance.urls')),
    path('leave/', include('leave_management.urls')),
    path('recruitment/', include('recruitment.urls')),
    path('salary/', include('salary.urls')),
    path('calendar/', include('workforce_calendar.urls')),
    # API endpoints
     # API Endpoints for mobile
    path('api/login/', api_views.login_api, name='api_login'),
    path('api/logout/', api_views.logout_api, name='api_logout'),
    path('api/attendance/mark/', api_views.mark_attendance_api, name='api_mark_attendance'),
    path('api/attendance/my/', api_views.my_attendance_api, name='api_my_attendance'),
    path('api/leave/my/', api_views.my_leaves_api, name='api_my_leaves'),
    path('api/leave/create/', api_views.create_leave_api, name='api_create_leave'),
    path('api/leave/types/', api_views.leave_types_api, name='api_leave_types'),
    path('api/salary/my/', api_views.my_salary_api, name='api_my_salary'),
    path('api/calendar/my/', api_views.my_calendar_api, name='api_my_calendar'),  # ← MAKE SURE THIS IS HERE
    path('api/employee/upload-face/', api_views.upload_face_image, name='upload_face'),
    path('api/attendance/mark-with-face/', api_views.mark_attendance_with_face, name='mark_attendance_face'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


