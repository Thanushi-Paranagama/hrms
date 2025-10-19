# Create this file: salary/utils.py

from datetime import datetime
import calendar


def calculate_monthly_salary(employee, month, year):
    """
    Calculate monthly salary based on attendance and leaves
    
    Returns: dict with salary breakdown
    """
    from attendance.models import Attendance
    from leave_management.models import LeaveRequest
    from django.db.models import Q
    
    # Get days in month
    days_in_month = calendar.monthrange(year, month)[1]
    
    # Get attendance data
    attendances = Attendance.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    )
    
    days_present = attendances.filter(status='PRESENT').count()
    days_late = attendances.filter(status='LATE').count()
    days_absent = attendances.filter(status='ABSENT').count()
    days_half = attendances.filter(status='HALF_DAY').count()
    
    # Calculate worked days (late days count as present)
    days_worked = days_present + days_late
    
    # Get approved leaves for the month
    leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='APPROVED',
        start_date__month__lte=month,
        start_date__year__lte=year,
        end_date__month__gte=month,
        end_date__year__gte=year
    )
    
    # Calculate leave days in this specific month
    days_leave = 0
    for leave in leaves:
        # Count only days that fall in this month
        leave_start = leave.start_date
        leave_end = leave.end_date
        
        month_start = datetime(year, month, 1).date()
        month_end = datetime(year, month, days_in_month).date()
        
        # Get the overlap
        overlap_start = max(leave_start, month_start)
        overlap_end = min(leave_end, month_end)
        
        if overlap_start <= overlap_end:
            days_leave += (overlap_end - overlap_start).days + 1
    
    # Calculate salary
    base_salary = float(employee.salary_base)
    per_day_salary = base_salary / days_in_month if days_in_month > 0 else 0
    
    # Deductions for absent days and half days
    absent_deduction = per_day_salary * days_absent
    half_day_deduction = (per_day_salary * days_half) / 2
    
    total_deductions = absent_deduction + half_day_deduction
    total_salary = base_salary - total_deductions
    
    return {
        'base_salary': base_salary,
        'days_in_month': days_in_month,
        'days_worked': days_worked,
        'days_present': days_present,
        'days_late': days_late,
        'days_absent': days_absent,
        'days_half': days_half,
        'days_leave': days_leave,
        'per_day_salary': per_day_salary,
        'absent_deduction': absent_deduction,
        'half_day_deduction': half_day_deduction,
        'total_deductions': total_deductions,
        'total_salary': total_salary,
        'bonuses': 0,  # Can be added later
    }


def generate_salary_slip_text(salary_record):
    """Generate a text-based salary slip"""
    employee = salary_record.employee
    
    slip = f"""
=====================================
          SALARY SLIP
=====================================

Employee Details:
-----------------
Name: {employee.user.get_full_name()}
Employee ID: {employee.employee_id}
Department: {employee.department.name if employee.department else 'N/A'}
Month/Year: {salary_record.month}/{salary_record.year}

Attendance Summary:
------------------
Days Worked: {salary_record.days_worked}
Days Absent: {salary_record.days_absent}
Days on Leave: {salary_record.days_leave}

Salary Breakdown:
-----------------
Base Salary:       Rs. {salary_record.base_salary:,.2f}
Bonuses:           Rs. {salary_record.bonuses:,.2f}
Deductions:        Rs. {salary_record.deductions:,.2f}

Total Salary:      Rs. {salary_record.total_salary:,.2f}

Payment Status: {'PAID' if salary_record.is_paid else 'PENDING'}
Payment Date: {salary_record.payment_date if salary_record.payment_date else 'N/A'}

=====================================
This is a system-generated document
=====================================
    """
    
    return slip

