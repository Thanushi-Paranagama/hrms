# Create this file: smart_hr_backend/middleware.py

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse


class EmployeeProfileMiddleware(MiddlewareMixin):
    """
    Middleware to check if authenticated user has an employee profile
    """
    
    def process_request(self, request):
        # Skip for admin, static files, and media
        if request.path.startswith('/admin/') or \
           request.path.startswith('/static/') or \
           request.path.startswith('/media/'):
            return None
        
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return None
        
        # Check if user has employee profile
        if not hasattr(request.user, 'employee_profile'):
            # Allow access to logout
            if request.path == reverse('logout'):
                return None
            
            # For staff users without profile, allow admin access
            if request.user.is_staff:
                return None
            
            # Otherwise, show error or redirect to create profile
            return redirect('/admin/')  # Redirect to admin to create profile
        
        return None
