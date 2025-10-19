# salary/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from .models import SalaryRecord
from employees.models import Employee
from attendance.models import Attendance
from leave_management.models import LeaveRequest
import calendar

@login_required
def salary_dashboard(request):
    """Display salary dashboard with current month statistics"""
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    salary_records = SalaryRecord.objects.filter(
        month=current_month,
        year=current_year
    ).select_related('employee__user', 'employee__department')
    
    total_payroll = salary_records.aggregate(Sum('total_salary'))['total_salary__sum'] or 0
    total_deductions = salary_records.aggregate(Sum('deductions'))['deductions__sum'] or 0
    
    context = {
        'salary_records': salary_records,
        'month': current_month,
        'year': current_year,
        'total_payroll': total_payroll,
        'total_deductions': total_deductions,
        'total_employees': salary_records.count(),
    }
    return render(request, 'salary/dashboard.html', context)

@login_required
def salary_generate(request):
    """Generate monthly salary for all employees"""
    if request.method == 'POST':
        try:
            month = int(request.POST.get('month'))
            year = int(request.POST.get('year'))
            
            # Validate month and year
            if month < 1 or month > 12:
                messages.error(request, 'Invalid month')
                return redirect('salary_generate')
            
            employees = Employee.objects.filter(is_active=True)
            generated_count = 0
            
            for employee in employees:
                # Calculate days in month
                days_in_month = calendar.monthrange(year, month)[1]
                
                # Get attendance data
                attendances = Attendance.objects.filter(
                    employee=employee,
                    date__month=month,
                    date__year=year
                )
                
                days_worked = attendances.filter(
                    Q(status='PRESENT') | Q(status='LATE')
                ).count()
                
                days_absent = attendances.filter(status='ABSENT').count()
                
                # Get approved leaves
                leaves = LeaveRequest.objects.filter(
                    employee=employee,
                    status='APPROVED',
                    start_date__month__lte=month,
                    start_date__year__lte=year,
                    end_date__month__gte=month,
                    end_date__year__gte=year
                )
                
                days_leave = sum(leave.days_requested for leave in leaves)
                
                # Calculate salary
                base_salary = employee.salary_base
                per_day_salary = base_salary / days_in_month if days_in_month > 0 else 0
                
                # Deduct for absent days (leaves are paid)
                deductions = per_day_salary * days_absent
                total_salary = base_salary - deductions
                
                # Create or update salary record
                salary_record, created = SalaryRecord.objects.update_or_create(
                    employee=employee,
                    month=month,
                    year=year,
                    defaults={
                        'base_salary': base_salary,
                        'deductions': deductions,
                        'days_worked': days_worked,
                        'days_absent': days_absent,
                        'days_leave': days_leave,
                        'total_salary': total_salary
                    }
                )
                generated_count += 1
            
            messages.success(request, f'Salary generated for {generated_count} employees for {month}/{year}')
            return redirect('salary_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error generating salary: {str(e)}')
    
    # For GET request, show the form
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    context = {
        'current_month': current_month,
        'current_year': current_year,
        'months': range(1, 13),
        'years': range(current_year - 2, current_year + 2),
    }
    return render(request, 'salary/generate.html', context)

@login_required
def salary_report(request, employee_id):
    """Generate salary report for a specific employee"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    # Check permission: employees can only view their own reports
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Access denied')
        return redirect('salary_dashboard')
    
    if request.user.employee_profile.role not in ['HR', 'ADMIN'] and \
       request.user.employee_profile != employee:
        messages.error(request, 'You can only view your own salary report')
        return redirect('salary_dashboard')
    
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    
    try:
        salary_record = SalaryRecord.objects.get(
            employee=employee,
            month=month,
            year=year
        )
    except SalaryRecord.DoesNotExist:
        salary_record = None
        messages.info(request, f'No salary record found for {month}/{year}')
    
    # Get attendance details for the month
    attendances = Attendance.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    ).order_by('date')
    
    context = {
        'employee': employee,
        'salary_record': salary_record,
        'attendances': attendances,
        'month': month,
        'year': year,
    }
    return render(request, 'salary/report.html', context)

@login_required
def salary_mark_paid(request, salary_id):
    """Mark a salary record as paid (HR/Admin only)"""
    if not hasattr(request.user, 'employee_profile') or \
       request.user.employee_profile.role not in ['HR', 'ADMIN']:
        messages.error(request, 'Access denied')
        return redirect('salary_dashboard')
    
    salary_record = get_object_or_404(SalaryRecord, id=salary_id)
    salary_record.is_paid = True
    salary_record.payment_date = timezone.now().date()
    salary_record.save()
    
    messages.success(request, f'Salary marked as paid for {salary_record.employee.user.get_full_name()}')
    return redirect('salary_dashboard')

