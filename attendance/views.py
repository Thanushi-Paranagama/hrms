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

@login_required
def attendance_dashboard(request):
    """Display attendance dashboard with today's statistics"""
    today = timezone.now().date()
    today_attendance = Attendance.objects.filter(date=today).select_related('employee__user', 'employee__department')
    
    # Today's statistics
    total_employees = Employee.objects.filter(is_active=True).count()
    present_today = today_attendance.filter(status='PRESENT').count()
    absent_today = total_employees - today_attendance.count()
    late_today = today_attendance.filter(status='LATE').count()
    half_day_today = today_attendance.filter(status='HALF_DAY').count()
    
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
            employee = get_object_or_404(Employee, employee_id=data['employee_id'])
            today = timezone.now().date()
            current_time = timezone.now().time()
            
            # Check if attendance already exists
            attendance, created = Attendance.objects.get_or_create(
                employee=employee,
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

