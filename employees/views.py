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
from django.db import transaction
from .forms import EmployeeCreateForm
from .utils import generate_employee_id


@login_required
def employee_list(request):
    """Display list of all active employees"""
    employees = Employee.objects.select_related('user', 'department').filter(is_active=True)
    total_departments = Department.objects.count()
    departments = Department.objects.all()
    context = {
        'employees': employees,
        'total_departments': total_departments,
        'departments': departments,
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
        # Support both JSON and form-encoded submissions
        if request.content_type == 'application/json':
            try:
                payload = json.loads(request.body)
            except Exception:
                return JsonResponse({'success': False, 'error': 'Invalid JSON payload'}, status=400)
        else:
            payload = request.POST.dict()

        form = EmployeeCreateForm(payload)
        if not form.is_valid():
            # Return structured errors for frontend display
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        # All validation passed — create records atomically
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name']
                )

                department = Department.objects.get(id=form.cleaned_data['department_id'])

                # generate employee id if not provided
                emp_id = form.cleaned_data.get('employee_id') or generate_employee_id()

                employee = Employee.objects.create(
                    user=user,
                    employee_id=emp_id,
                    department=department,
                    role=form.cleaned_data['role'],
                    date_of_birth=form.cleaned_data.get('date_of_birth'),
                    phone_number=form.cleaned_data.get('phone_number', ''),
                    emergency_contact=form.cleaned_data.get('emergency_contact', ''),
                    address=form.cleaned_data.get('address', ''),
                    floor_number=form.cleaned_data.get('floor_number'),
                    cabin_number=form.cleaned_data.get('cabin_number', ''),
                    salary_base=form.cleaned_data.get('salary_base') or 0
                )

            return JsonResponse({
                'success': True,
                'message': 'Employee created successfully',
                'employee_id': employee.employee_id
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

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

