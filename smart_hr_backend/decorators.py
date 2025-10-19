# Create this file: smart_hr_backend/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def hr_or_admin_required(view_func):
    """Decorator to restrict access to HR and Admin users only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'employee_profile'):
            messages.error(request, 'Access denied: Employee profile not found')
            return redirect('employee_list')
        
        if request.user.employee_profile.role not in ['HR', 'ADMIN']:
            messages.error(request, 'Access denied: HR or Admin role required')
            return redirect('employee_list')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def admin_required(view_func):
    """Decorator to restrict access to Admin users only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'employee_profile'):
            messages.error(request, 'Access denied: Employee profile not found')
            return redirect('employee_list')
        
        if request.user.employee_profile.role != 'ADMIN':
            messages.error(request, 'Access denied: Admin role required')
            return redirect('employee_list')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def employee_or_owner_required(view_func):
    """Decorator to allow access to own data or HR/Admin"""
    @wraps(view_func)
    def wrapper(request, employee_id=None, *args, **kwargs):
        if not hasattr(request.user, 'employee_profile'):
            messages.error(request, 'Access denied: Employee profile not found')
            return redirect('employee_list')
        
        employee = request.user.employee_profile
        
        # Allow if HR/Admin or viewing own data
        if employee.role in ['HR', 'ADMIN']:
            return view_func(request, employee_id, *args, **kwargs)
        
        if employee_id and employee.employee_id == employee_id:
            return view_func(request, employee_id, *args, **kwargs)
        
        messages.error(request, 'Access denied: You can only view your own data')
        return redirect('employee_detail', employee_id=employee.employee_id)
    
    return wrapper
