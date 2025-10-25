# recruitment/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime
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
from decimal import Decimal, InvalidOperation


@login_required
def recruitment_list(request):
    """Display list of all recruitment records"""
    # avoid selecting related Employee here because Employee has Decimal fields that may be malformed
    # selecting employee would trigger DB converters and can raise Decimal.InvalidOperation
    try:
        recruitments = Recruitment.objects.select_related('department').all().order_by('-created_at')
    except Exception as exc:
        # If a Decimal.InvalidOperation (from sqlite converter) or similar occurs, log and fallback to raw-safe fetch
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error loading recruitments: %s', exc)
        from django.contrib import messages as _messages
        _messages.error(request, 'Some stored data is malformed. Showing a simplified recruitment list.')
        from django.db import connection
        rows = []
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, first_name, last_name, position_applied, department_id, email, phone_number, status, interview_date, created_at FROM recruitment_recruitment ORDER BY created_at DESC")
            rows = cursor.fetchall()
        # build lightweight objects for template
        from types import SimpleNamespace
        recruitments = []
        # fetch department names in a simple map
        dept_map = {d.id: d.name for d in Department.objects.all()}
        for r in rows:
            dept_name = dept_map.get(r[4]) if r[4] else None
            obj = SimpleNamespace(id=r[0], first_name=r[1], last_name=r[2], position_applied=r[3], department=SimpleNamespace(name=dept_name) if dept_name else None, email=r[5], phone_number=r[6], status=r[7], interview_date=r[8], created_at=r[9])
            recruitments.append(obj)

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        # recruitments may be a QuerySet or a fallback list of SimpleNamespace objects
        try:
            recruitments = recruitments.filter(status=status_filter)
        except Exception:
            # fallback to in-memory filter for the lightweight list
            if isinstance(recruitments, list):
                recruitments = [r for r in recruitments if getattr(r, 'status', None) == status_filter]

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

            # Send application confirmation email to candidate (if email provided)
            try:
                if recruitment.email:
                    subject = 'Application Received - Thank you'
                    body = f"""
Dear {recruitment.first_name} {recruitment.last_name},

Thank you for applying for the position of {recruitment.position_applied}.
We have received your application and our recruitment team will review it. If your profile matches our requirements, we will contact you for the next steps.

Regards,
HR Team
"""
                    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recruitment.email], fail_silently=False)
            except Exception as email_err:
                # don't block the flow if email fails; record a warning to the user
                messages.warning(request, f'Record created but confirmation email could not be sent: {str(email_err)}')

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
    try:
        recruitment = Recruitment.objects.select_related('employee', 'department').get(id=recruitment_id)
        context = {'recruitment': recruitment}
    except Exception as exc:
        # If DB conversion (Decimal.InvalidOperation) or similar error occurs when loading related employee,
        # fallback to a lightweight object so the template can still render.
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('Error loading recruitment detail %s: %s', recruitment_id, exc)

        from django.db import connection
        from types import SimpleNamespace
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, first_name, last_name, position_applied, department_id, email, phone_number, status, interview_date, created_at, resume, cover_letter, notes FROM recruitment_recruitment WHERE id = %s", [recruitment_id])
            row = cursor.fetchone()

        if not row:
            return get_object_or_404(Recruitment, id=recruitment_id)

        dept = None
        try:
            from employees.models import Department as DeptModel
            dept_obj = DeptModel.objects.filter(id=row[4]).first()
            if dept_obj:
                dept = SimpleNamespace(name=dept_obj.name)
        except Exception:
            dept = None

        recruitment = SimpleNamespace(
            id=row[0],
            first_name=row[1],
            last_name=row[2],
            position_applied=row[3],
            department=dept,
            email=row[5],
            phone_number=row[6],
            status=row[7],
            interview_date=row[8],
            created_at=row[9],
            resume=row[10],
            cover_letter=row[11],
            notes=row[12]
        )
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
            # coerce salary_base to Decimal safely
            salary_val = request.POST.get('salary_base', 0)
            try:
                if salary_val in (None, ''):
                    salary_val = Decimal('0.00')
                else:
                    salary_val = Decimal(str(salary_val))
            except (InvalidOperation, TypeError, ValueError):
                salary_val = Decimal('0.00')

            employee = Employee.objects.create(
                user=user,
                employee_id=emp_id,
                department=recruitment.department,
                role=request.POST.get('role', 'EMPLOYEE'),
                phone_number=recruitment.phone_number,
                floor_number=request.POST.get('floor_number'),
                cabin_number=request.POST.get('cabin_number', ''),
                salary_base=salary_val
            )

            # Update recruitment record
            recruitment.status = 'HIRED'
            recruitment.employee = employee
            recruitment.hired_date = timezone.now().date()
            recruitment.save()

            # Prepare onboarding email (plaintext + HTML) with credentials and workplace details
            wifi_password = request.POST.get('wifi_password', settings.WIFI_PASSWORD if hasattr(settings, 'WIFI_PASSWORD') else 'Contact IT Department')

            email_subject = 'Welcome to Smart HR System - Your Onboarding Details'
            login_url = request.build_absolute_uri('/')

            plain_body = f"""
Dear {recruitment.first_name} {recruitment.last_name},

Congratulations and welcome to our organization!

ACCOUNT INFORMATION:
- Employee ID: {emp_id}
- Username: {username}
- Temporary Password: {password}
- Email: {recruitment.email}

WORKPLACE DETAILS:
- Department: {recruitment.department.name}
- Position: {recruitment.position_applied}
- Role: {request.POST.get('role', 'EMPLOYEE')}
- Base Salary (Rs.): {employee.salary_base}
- Floor: {employee.floor_number}
- Cabin Number: {employee.cabin_number}

NETWORK ACCESS:
- WiFi Password: {wifi_password}

Please change your password immediately after first login: {login_url}

If you have any questions, please contact the HR department.

Best regards,
HR Team
Smart HR System
"""

            # HTML email for nicer formatting
            html_body = f"""
<html>
  <body>
    <p>Dear {recruitment.first_name} {recruitment.last_name},</p>
    <p>Congratulations and welcome to our organization!</p>
    <h3>Account information</h3>
    <ul>
      <li><strong>Employee ID:</strong> {emp_id}</li>
      <li><strong>Username:</strong> {username}</li>
      <li><strong>Temporary Password:</strong> {password}</li>
      <li><strong>Email:</strong> {recruitment.email}</li>
    </ul>
    <h3>Workplace details</h3>
    <ul>
      <li><strong>Department:</strong> {recruitment.department.name}</li>
      <li><strong>Position:</strong> {recruitment.position_applied}</li>
      <li><strong>Role:</strong> {request.POST.get('role', 'EMPLOYEE')}</li>
      <li><strong>Base Salary (Rs.):</strong> {employee.salary_base}</li>
      <li><strong>Floor:</strong> {employee.floor_number}</li>
      <li><strong>Cabin Number:</strong> {employee.cabin_number}</li>
    </ul>
    <h3>Network access</h3>
    <p><strong>WiFi Password:</strong> {wifi_password}</p>
    <p>Please change your password immediately after first login: <a href="{login_url}">{login_url}</a></p>
    <p>If you have any questions, please contact the HR department.</p>
    <p>Best regards,<br/>HR Team<br/>Smart HR System</p>
  </body>
</html>
"""

            # Send email using EmailMultiAlternatives for plain+html
            try:
                from django.core.mail import EmailMultiAlternatives
                msg = EmailMultiAlternatives(subject=email_subject, body=plain_body, from_email=settings.DEFAULT_FROM_EMAIL, to=[recruitment.email])
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                messages.success(request, f'Successfully hired {recruitment.first_name} {recruitment.last_name}. Onboarding email sent to {recruitment.email}')
            except Exception as email_error:
                messages.warning(request, f'Employee created but onboarding email could not be sent: {str(email_error)}')

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
