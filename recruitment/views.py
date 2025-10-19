# recruitment/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
from .models import Recruitment
from employees.models import Employee, Department
import random
import string

@login_required
def recruitment_list(request):
    """Display list of all recruitment records"""
    recruitments = Recruitment.objects.select_related('department', 'employee').all().order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        recruitments = recruitments.filter(status=status_filter)
    
    context = {
        'recruitments': recruitments,
        'status_choices': Recruitment.STATUS_CHOICES,
    }
    return render(request, 'recruitment/recruitment_list.html', context)

@login_required
def recruitment_create(request):
    """Create a new recruitment record"""
    if request.method == 'POST':
        try:
            department = Department.objects.get(id=request.POST.get('department_id'))
            
            recruitment = Recruitment.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                email=request.POST.get('email'),
                phone_number=request.POST.get('phone_number'),
                position_applied=request.POST.get('position_applied'),
                department=department,
                cover_letter=request.POST.get('cover_letter', ''),
                notes=request.POST.get('notes', '')
            )
            
            # Handle resume upload if provided
            if 'resume' in request.FILES:
                recruitment.resume = request.FILES['resume']
                recruitment.save()
            
            messages.success(request, 'Recruitment record created successfully')
            return redirect('recruitment_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    departments = Department.objects.all()
    context = {'departments': departments}
    return render(request, 'recruitment/recruitment_create.html', context)

@login_required
def recruitment_detail(request, recruitment_id):
    """Display detailed information about a recruitment record"""
    recruitment = get_object_or_404(Recruitment, id=recruitment_id)
    context = {'recruitment': recruitment}
    return render(request, 'recruitment/recruitment_detail.html', context)

@login_required
def recruitment_update_status(request, recruitment_id):
    """Update recruitment status"""
    if request.method == 'POST':
        recruitment = get_object_or_404(Recruitment, id=recruitment_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Recruitment.STATUS_CHOICES):
            recruitment.status = new_status
            
            # Set interview date if status is INTERVIEW
            if new_status == 'INTERVIEW' and request.POST.get('interview_date'):
                interview_datetime = datetime.strptime(
                    request.POST.get('interview_date'), 
                    '%Y-%m-%dT%H:%M'
                )
                recruitment.interview_date = interview_datetime
            
            recruitment.save()
            messages.success(request, 'Status updated successfully')
        else:
            messages.error(request, 'Invalid status')
        
        return redirect('recruitment_detail', recruitment_id=recruitment_id)
    
    return redirect('recruitment_list')

@login_required
def recruitment_hire(request, recruitment_id):
    """Hire a candidate and create employee account with automated onboarding email"""
    recruitment = get_object_or_404(Recruitment, id=recruitment_id)
    
    # Check if already hired
    if recruitment.status == 'HIRED':
        messages.warning(request, 'This candidate has already been hired')
        return redirect('recruitment_detail', recruitment_id=recruitment_id)
    
    if request.method == 'POST':
        try:
            # Generate random password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
            # Create username from name
            base_username = f"{recruitment.first_name.lower()}.{recruitment.last_name.lower()}"
            username = base_username
            counter = 1
            
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=recruitment.email,
                password=password,
                first_name=recruitment.first_name,
                last_name=recruitment.last_name
            )
            
            # Generate employee ID
            latest_emp = Employee.objects.order_by('-id').first()
            if latest_emp:
                last_id = int(latest_emp.employee_id.replace('EMP', ''))
                emp_id = f"EMP{str(last_id + 1).zfill(4)}"
            else:
                emp_id = "EMP0001"
            
            # Create employee
            employee = Employee.objects.create(
                user=user,
                employee_id=emp_id,
                department=recruitment.department,
                role=request.POST.get('role', 'EMPLOYEE'),
                phone_number=recruitment.phone_number,
                floor_number=request.POST.get('floor_number'),
                cabin_number=request.POST.get('cabin_number', ''),
                salary_base=request.POST.get('salary_base', 0)
            )
            
            # Update recruitment record
            recruitment.status = 'HIRED'
            recruitment.employee = employee
            recruitment.hired_date = timezone.now().date()
            recruitment.save()
            
            # Prepare onboarding email
            wifi_password = request.POST.get('wifi_password', settings.WIFI_PASSWORD if hasattr(settings, 'WIFI_PASSWORD') else 'Contact IT Department')
            
            email_subject = 'Welcome to Smart HR System - Your Onboarding Details'
            email_body = f"""
Dear {recruitment.first_name} {recruitment.last_name},

Congratulations! Welcome to our organization.

Here are your onboarding details:

ACCOUNT INFORMATION:
- Employee ID: {emp_id}
- Username: {username}
- Temporary Password: {password}
- Email: {recruitment.email}

WORKPLACE DETAILS:
- Department: {recruitment.department.name}
- Position: {recruitment.position_applied}
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
            
            # Send onboarding email
            try:
                send_mail(
                    email_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [recruitment.email],
                    fail_silently=False,
                )
                messages.success(request, f'Successfully hired {recruitment.first_name} {recruitment.last_name}. Onboarding email sent to {recruitment.email}')
            except Exception as email_error:
                messages.warning(request, f'Employee created but email could not be sent: {str(email_error)}')
            
            return redirect('employee_detail', employee_id=emp_id)
            
        except Exception as e:
            messages.error(request, f'Error hiring candidate: {str(e)}')
            return redirect('recruitment_detail', recruitment_id=recruitment_id)
    
    departments = Department.objects.all()
    context = {
        'recruitment': recruitment,
        'departments': departments,
        'role_choices': Employee.ROLE_CHOICES,
    }
    return render(request, 'recruitment/recruitment_hire.html', context)
