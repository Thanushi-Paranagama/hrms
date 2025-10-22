from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.login_api, name='api_login'),
    path('logout/', views.logout_api, name='api_logout'),
    
    # Attendance
    path('attendance/mark/', views.mark_attendance_api, name='api_mark_attendance'),
    path('attendance/my/', views.my_attendance_api, name='api_my_attendance'),
    
    # Leave
    path('leave/my/', views.my_leaves_api, name='api_my_leaves'),
    path('leave/create/', views.create_leave_api, name='api_create_leave'),
    path('leave/types/', views.leave_types_api, name='api_leave_types'),
    
    # Salary
    path('salary/my/', views.my_salary_api, name='api_my_salary'),
    
    # Calendar
    path('calendar/my/', views.my_calendar_api, name='api_my_calendar'),

    # Face registration
    path('employee/upload-face/', views.upload_face_image, name='upload_face'),

    # Attendance with face
    path('attendance/mark-with-face/', views.mark_attendance_with_face, name='mark_attendance_face'),

]

