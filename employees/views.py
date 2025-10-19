# employees/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Employee, Department
import json


@login_required
def employee_list(request):
    """Display list of all active employees"""
    employees = Employee.objects.select_related('user', 'department').filter(is_active=True)
    total_departments = Department.objects.count()
    context = {
        'employees': employees,
        'total_departments': total_departments
    }
    return render(request, 'employees/employee_list.html', context)

@login_required
def employee_detail(request, employee_id):
    """Display detailed information about an employee"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    context = {'employee': employee}
    return render(request, 'employees/employee_detail.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def employee_create(request):
    """Create a new employee"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create User
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            
            # Create Employee
            department = Department.objects.get(id=data['department_id'])
            employee = Employee.objects.create(
                user=user,
                employee_id=data['employee_id'],
                department=department,
                role=data.get('role', 'EMPLOYEE'),
                date_of_birth=data.get('date_of_birth'),
                phone_number=data.get('phone_number', ''),
                address=data.get('address', ''),
                floor_number=data.get('floor_number'),
                cabin_number=data.get('cabin_number', ''),
                salary_base=data.get('salary_base', 0)
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Employee created successfully',
                'employee_id': employee.employee_id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    departments = Department.objects.all()
    context = {'departments': departments}
    return render(request, 'employees/employee_create.html', context)

@login_required
@require_http_methods(["POST"])
def employee_update(request, employee_id):
    """Update employee information"""
    try:
        employee = get_object_or_404(Employee, employee_id=employee_id)
        data = json.loads(request.body)
        
        # Update user info
        if 'first_name' in data:
            employee.user.first_name = data['first_name']
        if 'last_name' in data:
            employee.user.last_name = data['last_name']
        if 'email' in data:
            employee.user.email = data['email']
        employee.user.save()
        
        # Update employee info
        if 'department_id' in data:
            employee.department = Department.objects.get(id=data['department_id'])
        if 'phone_number' in data:
            employee.phone_number = data['phone_number']
        if 'address' in data:
            employee.address = data['address']
        if 'floor_number' in data:
            employee.floor_number = data['floor_number']
        if 'cabin_number' in data:
            employee.cabin_number = data['cabin_number']
        if 'salary_base' in data:
            employee.salary_base = data['salary_base']
        
        employee.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Employee updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

