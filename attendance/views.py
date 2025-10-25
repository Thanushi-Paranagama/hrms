# attendance/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q, Count
from datetime import datetime, timedelta
from .models import Attendance
from employees.models import Employee
import json
from types import SimpleNamespace
from django.db import connection
from decimal import InvalidOperation

@login_required
def attendance_dashboard(request):
    """Display attendance dashboard with today's statistics"""
    today = timezone.now().date()
    try:
        # Primary attempt: use ORM (fast, convenient)
        today_qs = Attendance.objects.filter(date=today).select_related('employee__user', 'employee__department')

        # Force evaluation now so any DB conversion errors are raised inside this try block
        today_attendance = list(today_qs)

        # Today's statistics (compute from the in-memory list)
        total_employees = Employee.objects.filter(is_active=True).count()
        present_today = sum(1 for r in today_attendance if getattr(r, 'status', None) == 'PRESENT')
        absent_today = total_employees - len(today_attendance)
        late_today = sum(1 for r in today_attendance if getattr(r, 'status', None) == 'LATE')
        half_day_today = sum(1 for r in today_attendance if getattr(r, 'status', None) == 'HALF_DAY')
    except Exception as exc:
        # Defensive fallback: if DB converters (e.g. Decimal.InvalidOperation) raise while ORM hydrates rows,
        # build a lightweight, safe structure using raw SQL and avoid Django field converters.
        import logging
        logger = logging.getLogger(__name__)
        logger.exception('ORM attendance load failed; using raw fallback: %s', exc)

        # Raw fetch attendance rows joined to employee and department names
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.id, a.employee_id, e.employee_id as emp_code, u.first_name, u.last_name,
                       d.name as dept_name, a.check_in, a.check_out, a.status
                FROM attendance_attendance a
                LEFT JOIN employees_employee e ON e.id = a.employee_id
                LEFT JOIN auth_user u ON u.id = e.user_id
                LEFT JOIN employees_department d ON d.id = e.department_id
                WHERE a.date = %s
                ORDER BY a.check_in DESC
            """, [today])
            rows = cursor.fetchall()

        today_attendance = []
        present_today = 0
        late_today = 0
        half_day_today = 0

        for r in rows:
            aid, emp_fk, emp_code, first_name, last_name, dept_name, check_in, check_out, status = r

            # Build nested employee.user.get_full_name callable for template compatibility
            full_name = ' '.join(filter(None, [first_name, last_name])) if first_name or last_name else emp_code or ''
            user_obj = SimpleNamespace(**{
                'get_full_name': (lambda name=full_name: (lambda: name))()
            })

            employee_obj = SimpleNamespace(**{
                'employee_id': emp_code,
                'user': user_obj,
                'department': SimpleNamespace(name=dept_name) if dept_name else None
            })

            # compute hours worked (float hours) if both times present
            hours = None
            try:
                if check_in and check_out:
                    # cursor returns strings for time columns; parse as HH:MM[:SS]
                    fmt = '%H:%M:%S' if len(str(check_in)) > 5 else '%H:%M'
                    try:
                        cin = datetime.strptime(str(check_in), '%H:%M:%S').time()
                        cout = datetime.strptime(str(check_out), '%H:%M:%S').time()
                    except Exception:
                        try:
                            cin = datetime.strptime(str(check_in), '%H:%M').time()
                            cout = datetime.strptime(str(check_out), '%H:%M').time()
                        except Exception:
                            cin = None
                            cout = None

                    if cin and cout:
                        dt_in = datetime.combine(today, cin)
                        dt_out = datetime.combine(today, cout)
                        delta = dt_out - dt_in
                        hours = delta.total_seconds() / 3600.0
            except Exception:
                hours = None

            record = SimpleNamespace(**{
                'id': aid,
                'employee': employee_obj,
                'check_in': check_in,
                'check_out': check_out,
                'status': status,
                'get_hours_worked': hours
            })

            today_attendance.append(record)

            if status == 'PRESENT':
                present_today += 1
            if status == 'LATE':
                late_today += 1
            if status == 'HALF_DAY':
                half_day_today += 1

        # total_employees should avoid hydrating Employee objects; use count() only
        try:
            total_employees = Employee.objects.filter(is_active=True).count()
        except Exception:
            total_employees = 0
        absent_today = total_employees - len(today_attendance)
    
    # Weekly data for charts (last 7 days)
    week_labels = []
    week_present = []
    week_absent = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        week_labels.append(day.strftime('%a'))
        daily_attendance = Attendance.objects.filter(date=day)
        week_present.append(daily_attendance.filter(status='PRESENT').count())
        week_absent.append(daily_attendance.filter(status='ABSENT').count())
    
    context = {
        'today_attendance': today_attendance,
        'current_date': today,
        'total_employees': total_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'late_today': late_today,
        'half_day_today': half_day_today,
        'week_labels': json.dumps(week_labels),
        'week_present': json.dumps(week_present),
        'week_absent': json.dumps(week_absent),
    }
    return render(request, 'attendance/dashboard.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def attendance_mark(request):
    """Mark attendance for an employee"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            emp_identifier = data.get('employee_id')
            # Avoid loading full Employee object which may trigger sqlite3 Decimal converter errors.
            emp_pk = Employee.objects.filter(employee_id=emp_identifier).values_list('id', flat=True).first()
            if not emp_pk:
                return JsonResponse({'success': False, 'error': 'Employee not found'}, status=404)
            today = timezone.now().date()
            current_time = timezone.now().time()
            
            # Check if attendance already exists
            attendance, created = Attendance.objects.get_or_create(
                employee_id=emp_pk,
                date=today,
                defaults={
                    'check_in': current_time,
                    'status': 'PRESENT',
                    'face_verified': data.get('face_verified', False)
                }
            )
            
            if not created:
                # Update check-out time
                attendance.check_out = current_time
                attendance.save()
                message = 'Check-out recorded successfully'
            else:
                message = 'Check-in recorded successfully'
            
            return JsonResponse({
                'success': True,
                'message': message,
                'check_in': str(attendance.check_in),
                'check_out': str(attendance.check_out) if attendance.check_out else None
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return render(request, 'attendance/mark.html')

@login_required
def attendance_report(request, employee_id):
    """Generate attendance report for an employee"""
    employee = get_object_or_404(Employee, employee_id=employee_id)
    
    # Get month and year from query params or default to current
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    
    attendances = Attendance.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    ).order_by('date')
    
    # Calculate statistics
    total_present = attendances.filter(status='PRESENT').count()
    total_absent = attendances.filter(status='ABSENT').count()
    total_late = attendances.filter(status='LATE').count()
    total_half_day = attendances.filter(status='HALF_DAY').count()
    
    context = {
        'employee': employee,
        'attendances': attendances,
        'month': month,
        'year': year,
        'years': [2023, 2024, 2025, 2026],
        'total_present': total_present,
        'total_absent': total_absent,
        'total_late': total_late,
        'total_half_day': total_half_day,
    }
    return render(request, 'attendance/report.html', context)

@login_required
def attendance_monthly_summary(request):
    """Display monthly attendance summary for all employees"""
    month = int(request.GET.get('month', timezone.now().month))
    year = int(request.GET.get('year', timezone.now().year))
    
    employees = Employee.objects.filter(is_active=True).select_related('user', 'department')
    
    summary_data = []
    for employee in employees:
        attendances = Attendance.objects.filter(
            employee=employee,
            date__month=month,
            date__year=year
        )
        
        summary_data.append({
            'employee': employee,
            'present': attendances.filter(status='PRESENT').count(),
            'absent': attendances.filter(status='ABSENT').count(),
            'late': attendances.filter(status='LATE').count(),
        })
    
    context = {
        'summary_data': summary_data,
        'month': month,
        'year': year,
    }
    return render(request, 'attendance/monthly_summary.html', context)

