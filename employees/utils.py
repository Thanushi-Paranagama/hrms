# Create this file: employees/utils.py

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import date, datetime
import random
import string


def generate_random_password(length=12):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choices(characters, k=length))
    return password


def generate_employee_id():
    """Generate unique employee ID"""
    from employees.models import Employee
    
    latest_emp = Employee.objects.order_by('-id').first()
    if latest_emp:
        last_id = int(latest_emp.employee_id.replace('EMP', ''))
        emp_id = f"EMP{str(last_id + 1).zfill(4)}"
    else:
        emp_id = "EMP0001"
    return emp_id


def send_onboarding_email(employee, username, password, wifi_password='Contact IT'):
    """Send onboarding email to new employee"""
    subject = 'Welcome to Smart HR System - Your Onboarding Details'
    
    message = f"""
Dear {employee.user.first_name} {employee.user.last_name},

Congratulations! Welcome to our organization.

Here are your onboarding details:

ACCOUNT INFORMATION:
- Employee ID: {employee.employee_id}
- Username: {username}
- Temporary Password: {password}
- Email: {employee.user.email}

WORKPLACE DETAILS:
- Department: {employee.department.name if employee.department else 'N/A'}
- Floor: {employee.floor_number}
- Cabin Number: {employee.cabin_number}

NETWORK ACCESS:
- WiFi Password: {wifi_password}

IMPORTANT NOTES:
1. Please change your password immediately after first login
2. Download the Smart HR mobile app for attendance marking
3. Access the web portal for leave requests and other HR services

If you have any questions, please contact the HR department.

Welcome aboard!

Best regards,
HR Team
Smart HR System
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [employee.user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_birthday_wishes(employee):
    """Send automated birthday email"""
    subject = f'🎉 Happy Birthday {employee.user.first_name}!'
    
    message = f"""
Dear {employee.user.first_name},

Happy Birthday! 🎂🎉

On behalf of the entire team, we wish you a wonderful day filled with joy and happiness.

Thank you for being a valuable member of our organization.

Warm wishes,
HR Team
Smart HR System
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [employee.user.email],
            fail_silently=True,
        )
        return True
    except:
        return False


def send_leave_notification(leave_request, is_approved=True):
    """Send leave approval/rejection notification"""
    status = 'Approved' if is_approved else 'Rejected'
    subject = f'Leave Request {status}'
    
    message = f"""
Dear {leave_request.employee.user.first_name},

Your leave request has been {status.lower()}.

LEAVE DETAILS:
- Leave Type: {leave_request.leave_type.name}
- Start Date: {leave_request.start_date}
- End Date: {leave_request.end_date}
- Days: {leave_request.days_requested}
- Status: {status}
"""
    
    if not is_approved and leave_request.rejection_reason:
        message += f"\nReason for Rejection: {leave_request.rejection_reason}\n"
    
    message += """
If you have any questions, please contact HR.

Best regards,
HR Team
Smart HR System
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [leave_request.employee.user.email],
            fail_silently=True,
        )
        return True
    except:
        return False


def check_birthdays_today():
    """Check for birthdays today and send wishes"""
    from employees.models import Employee
    
    today = date.today()
    employees = Employee.objects.filter(
        is_active=True,
        date_of_birth__month=today.month,
        date_of_birth__day=today.day
    )
    
    count = 0
    for employee in employees:
        if send_birthday_wishes(employee):
            count += 1
    
    return count


def calculate_working_days(start_date, end_date):
    """Calculate working days between two dates (excluding weekends)"""
    days = 0
    current_date = start_date
    
    while current_date <= end_date:
        # Check if it's a weekday (0-4 are Monday-Friday)
        if current_date.weekday() < 5:
            days += 1
        current_date += timedelta(days=1)
    
    return days
