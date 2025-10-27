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
from decimal import Decimal, InvalidOperation
import logging
from types import SimpleNamespace
from django.db import connection

logger = logging.getLogger(__name__)


@login_required
def employee_list(request):
    """Display list of all active employees"""
    try:
        qs = Employee.objects.select_related('user', 'department').filter(is_active=True)
        # materialize queryset and ensure salary_base is a valid Decimal
        employees = list(qs)
        for e in employees:
            try:
                if e.salary_base in (None, ''):
                    e.salary_base = Decimal('0.00')
                else:
                    e.salary_base = Decimal(str(e.salary_base))
            except (InvalidOperation, TypeError, ValueError):
                e.salary_base = Decimal('0.00')
    except InvalidOperation as exc:
        # Occurs when DB contains malformed decimal values that sqlite3 converter cannot parse
        logger.exception('Decimal conversion error when loading employees: %s', exc)
        from django.contrib import messages as _messages
        _messages.error(request, 'Some stored salary values are malformed. Showing a simplified list; please run data cleanup.')

        # Fallback: fetch minimal safe data via raw SQL (avoids Django field converters)
        employees = []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT e.id, e.employee_id, u.first_name, u.last_name, u.email, e.phone_number, d.name as dept_name, e.role
                FROM employees_employee e
                LEFT JOIN auth_user u ON u.id = e.user_id
                LEFT JOIN employees_department d ON d.id = e.department_id
                WHERE e.is_active = 1
            """)
            rows = cursor.fetchall()
            for r in rows:
                # build lightweight object similar to Employee used in templates
                user_ns = SimpleNamespace(first_name=r[2] or '', last_name=r[3] or '', email=r[4] or '',
                                          get_full_name=lambda fn=r[2] or '', ln=r[3] or '': f"{fn} {ln}".strip())
                dept_ns = SimpleNamespace(name=r[6]) if r[6] else None
                emp_ns = SimpleNamespace(employee_id=r[1], user=user_ns, department=dept_ns, phone_number=r[5] or '', role=r[7])
                employees.append(emp_ns)
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
    try:
        employee = get_object_or_404(Employee, employee_id=employee_id)
    except InvalidOperation as exc:
        # Handle malformed Decimal values in the DB that sqlite3 converter chokes on
        logger.exception('Decimal conversion error when loading employee %s: %s', employee_id, exc)
        from django.contrib import messages as _messages
        _messages.error(request, 'Some numeric fields for this employee are malformed. Showing a simplified view; please run data cleanup.')

        # Fallback: fetch minimal safe data via raw SQL (avoids Django field converters)
        with connection.cursor() as cursor:
            cursor.execute(r"""
                SELECT e.id, e.employee_id, e.phone_number, e.role, e.date_of_birth, e.emergency_contact,
                       e.address, e.floor_number, e.cabin_number, e.salary_base,
                       e.face_encoding, e.created_at, e.updated_at,
                       u.id as user_id, u.username, u.first_name, u.last_name, u.email,
                       d.name as dept_name
                FROM employees_employee e
                LEFT JOIN auth_user u ON u.id = e.user_id
                LEFT JOIN employees_department d ON d.id = e.department_id
                WHERE e.employee_id = %s
            """, [employee_id])
            row = cursor.fetchone()

        if not row:
            # If nothing found, raise 404 as usual
            from django.http import Http404
            raise Http404('Employee not found')

        # Build lightweight namespaces to mimic model attributes used by templates
        (eid, empid, phone, role, dob, emergency, address, floor, cabin, salary_base,
         face_encoding, created_at, updated_at, user_id, username, first_name, last_name, email, dept_name) = row

        def _get_full_name(fn=first_name or '', ln=last_name or ''):
            return f"{(fn or '').strip()} {(ln or '').strip()}".strip()

        user_ns = SimpleNamespace(id=user_id, username=username or '', first_name=first_name or '', last_name=last_name or '', email=email or '', get_full_name=_get_full_name)
        dept_ns = SimpleNamespace(name=dept_name) if dept_name else None
        # coerce salary safely
        try:
            salary_val = Decimal(str(salary_base)) if salary_base not in (None, '') else Decimal('0.00')
        except (InvalidOperation, TypeError, ValueError):
            salary_val = Decimal('0.00')

        employee = SimpleNamespace(
            id=eid,
            employee_id=empid,
            user=user_ns,
            phone_number=phone or '',
            role=role,
            date_of_birth=dob,
            emergency_contact=emergency or '',
            address=address or '',
            floor_number=floor,
            cabin_number=cabin or '',
            salary_base=salary_val,
            face_encoding=face_encoding,
            face_image=None,
            created_at=created_at,
            updated_at=updated_at,
            department=dept_ns
        )

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

                # prepare salary value safely
                salary_val = form.cleaned_data.get('salary_base')
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
                    department=department,
                    role=form.cleaned_data['role'],
                    date_of_birth=form.cleaned_data.get('date_of_birth'),
                    phone_number=form.cleaned_data.get('phone_number', ''),
                    emergency_contact=form.cleaned_data.get('emergency_contact', ''),
                    address=form.cleaned_data.get('address', ''),
                    floor_number=form.cleaned_data.get('floor_number'),
                    cabin_number=form.cleaned_data.get('cabin_number', ''),
                    salary_base=salary_val
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
def upload_face_image(request, employee_id):
    """Upload and process face image for recognition"""
    try:
        employee = get_object_or_404(Employee, employee_id=employee_id)
        
        if 'face_image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided'
            }, status=400)
            
        image = request.FILES['face_image']
        employee.face_image = image
        employee.save()
        
        # Generate face encoding
        from .face_recognition_utils import encode_face
        face_encoding = encode_face(employee.face_image.path)
        
        if face_encoding is None:
            return JsonResponse({
                'success': False,
                'error': 'No face detected in the image'
            }, status=400)
            
        # Store the encoding
        employee.face_encoding = json.dumps(face_encoding)
        employee.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Face image uploaded and processed successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

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
            # coerce salary to Decimal safely
            try:
                if data['salary_base'] in (None, ''):
                    employee.salary_base = Decimal('0.00')
                else:
                    employee.salary_base = Decimal(str(data['salary_base']))
            except (InvalidOperation, TypeError, ValueError):
                return JsonResponse({'success': False, 'error': 'Invalid salary value'}, status=400)
        
        employee.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Employee updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

