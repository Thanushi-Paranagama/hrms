# Create this file: smart_hr_backend/tasks.py
# This is for Celery background tasks (optional, but recommended)

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import date, timedelta


@shared_task
def send_birthday_emails_task():
    """Celery task to send birthday emails automatically"""
    from employees.utils import check_birthdays_today
    
    count = check_birthdays_today()
    return f"Sent birthday wishes to {count} employees"


@shared_task
def generate_monthly_salaries_task(month, year):
    """Celery task to generate monthly salaries"""
    from employees.models import Employee
    from salary.utils import calculate_monthly_salary
    from salary.models import SalaryRecord
    
    employees = Employee.objects.filter(is_active=True)
    count = 0
    
    for employee in employees:
        salary_data = calculate_monthly_salary(employee, month, year)
        
        SalaryRecord.objects.update_or_create(
            employee=employee,
            month=month,
            year=year,
            defaults={
                'base_salary': salary_data['base_salary'],
                'deductions': salary_data['total_deductions'],
                'bonuses': salary_data['bonuses'],
                'days_worked': salary_data['days_worked'],
                'days_absent': salary_data['days_absent'],
                'days_leave': salary_data['days_leave'],
                'total_salary': salary_data['total_salary']
            }
        )
        count += 1
    
    return f"Generated salary for {count} employees"


@shared_task
def send_leave_reminder_task():
    """Celery task to send reminders for pending leave requests"""
    from leave_management.models import LeaveRequest
    from django.utils import timezone
    
    # Get pending leaves older than 3 days
    three_days_ago = timezone.now() - timedelta(days=3)
    
    pending_leaves = LeaveRequest.objects.filter(
        status='PENDING',
        created_at__lte=three_days_ago
    ).select_related('employee__user')
    
    count = 0
    for leave in pending_leaves:
        try:
            send_mail(
                'Leave Request Pending Approval',
                f'Your leave request from {leave.start_date} to {leave.end_date} is still pending approval.',
                settings.DEFAULT_FROM_EMAIL,
                [leave.employee.user.email],
                fail_silently=True,
            )
            count += 1
        except:
            pass
    
    return f"Sent reminders for {count} pending leave requests"
