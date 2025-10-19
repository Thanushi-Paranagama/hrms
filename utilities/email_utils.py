# Create utilities/email_utils.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_onboarding_email(employee, credentials):
    """Send onboarding email to new employee"""
    subject = 'Welcome to Smart HR System'
    message = render_to_string('emails/onboarding.html', {
        'employee': employee,
        'credentials': credentials
    })
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [employee.user.email],
        html_message=message,
        fail_silently=False,
    )

def send_birthday_wishes(employee):
    """Send automated birthday email"""
    subject = '🎉 Happy Birthday!'
    message = f"Happy Birthday {employee.user.first_name}! Have a wonderful day!"
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [employee.user.email],
        fail_silently=True,
    )

def send_leave_approval_email(leave_request):
    """Send leave approval/rejection email"""
    subject = f'Leave Request {leave_request.status}'
    message = f"""
    Your leave request from {leave_request.start_date} to {leave_request.end_date}
    has been {leave_request.status.lower()}.
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [leave_request.employee.user.email],
        fail_silently=True,
    )