# workforce_calendar/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from .models import WorkforceEvent
from employees.models import Employee, Department
import json

@login_required
def calendar_view(request):
    """Display workforce calendar"""
    # Get date range from query params or default to current month
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        # Default to current month
        start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    # Get events
    events = WorkforceEvent.objects.filter(
        start_datetime__gte=start_date,
        start_datetime__lte=end_date
    ).prefetch_related('participants', 'department').select_related('created_by__user')
    
    # Filter by employee if not HR/Admin
    if hasattr(request.user, 'employee_profile'):
        if request.user.employee_profile.role not in ['HR', 'ADMIN']:
            employee = request.user.employee_profile
            events = events.filter(
                Q(participants=employee) | Q(department=employee.department) | Q(created_by=employee)
            ).distinct()
    
    context = {
        'events': events,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'workforce_calendar/calendar.html', context)

@login_required
def event_create(request):
    """Create a new calendar event"""
    if request.method == 'POST':
        try:
            # Parse datetime
            start_datetime = datetime.strptime(
                request.POST.get('start_datetime'), 
                '%Y-%m-%dT%H:%M'
            )
            end_datetime = datetime.strptime(
                request.POST.get('end_datetime'), 
                '%Y-%m-%dT%H:%M'
            )
            
            # Validate dates
            if start_datetime >= end_datetime:
                messages.error(request, 'End time must be after start time')
                return redirect('event_create')
            
            # Create event
            event = WorkforceEvent.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description', ''),
                event_type=request.POST.get('event_type'),
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                all_day=request.POST.get('all_day') == 'on',
                location=request.POST.get('location', ''),
                created_by=request.user.employee_profile
            )
            
            # Add department if specified
            department_id = request.POST.get('department_id')
            if department_id:
                event.department = Department.objects.get(id=department_id)
                event.save()
            
            # Add participants
            participant_ids = request.POST.getlist('participants')
            if participant_ids:
                participants = Employee.objects.filter(id__in=participant_ids)
                event.participants.set(participants)
            
            messages.success(request, 'Event created successfully')
            return redirect('calendar_view')
            
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
    
    employees = Employee.objects.filter(is_active=True).select_related('user')
    departments = Department.objects.all()
    
    context = {
        'employees': employees,
        'departments': departments,
        'event_types': WorkforceEvent.EVENT_TYPE_CHOICES,
    }
    return render(request, 'workforce_calendar/event_create.html', context)

@login_required
def event_detail(request, event_id):
    """Display detailed information about an event"""
    event = get_object_or_404(WorkforceEvent, id=event_id)
    
    # Check if user has access to this event
    if hasattr(request.user, 'employee_profile'):
        employee = request.user.employee_profile
        if employee.role not in ['HR', 'ADMIN']:
            # Check if employee is participant or in same department
            if employee not in event.participants.all() and \
               employee.department != event.department and \
               event.created_by != employee:
                messages.error(request, 'You do not have access to this event')
                return redirect('calendar_view')
    
    context = {'event': event}
    return render(request, 'workforce_calendar/event_detail.html', context)

@login_required
def event_update(request, event_id):
    """Update an existing event"""
    event = get_object_or_404(WorkforceEvent, id=event_id)
    
    # Check permission
    if hasattr(request.user, 'employee_profile'):
        employee = request.user.employee_profile
        if employee.role not in ['HR', 'ADMIN'] and event.created_by != employee:
            messages.error(request, 'You do not have permission to edit this event')
            return redirect('event_detail', event_id=event_id)
    
    if request.method == 'POST':
        try:
            event.title = request.POST.get('title')
            event.description = request.POST.get('description', '')
            event.event_type = request.POST.get('event_type')
            event.location = request.POST.get('location', '')
            event.all_day = request.POST.get('all_day') == 'on'
            
            start_datetime = datetime.strptime(
                request.POST.get('start_datetime'), 
                '%Y-%m-%dT%H:%M'
            )
            end_datetime = datetime.strptime(
                request.POST.get('end_datetime'), 
                '%Y-%m-%dT%H:%M'
            )
            
            if start_datetime >= end_datetime:
                messages.error(request, 'End time must be after start time')
                return redirect('event_update', event_id=event_id)
            
            event.start_datetime = start_datetime
            event.end_datetime = end_datetime
            
            # Update department
            department_id = request.POST.get('department_id')
            if department_id:
                event.department = Department.objects.get(id=department_id)
            else:
                event.department = None
            
            event.save()
            
            # Update participants
            participant_ids = request.POST.getlist('participants')
            if participant_ids:
                participants = Employee.objects.filter(id__in=participant_ids)
                event.participants.set(participants)
            else:
                event.participants.clear()
            
            messages.success(request, 'Event updated successfully')
            return redirect('event_detail', event_id=event_id)
            
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    
    employees = Employee.objects.filter(is_active=True).select_related('user')
    departments = Department.objects.all()
    
    context = {
        'event': event,
        'employees': employees,
        'departments': departments,
        'event_types': WorkforceEvent.EVENT_TYPE_CHOICES,
    }
    return render(request, 'workforce_calendar/event_update.html', context)

@login_required
def event_delete(request, event_id):
    """Delete a calendar event"""
    event = get_object_or_404(WorkforceEvent, id=event_id)
    
    # Check permission
    if hasattr(request.user, 'employee_profile'):
        employee = request.user.employee_profile
        if employee.role not in ['HR', 'ADMIN'] and event.created_by != employee:
            messages.error(request, 'You do not have permission to delete this event')
            return redirect('event_detail', event_id=event_id)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully')
        return redirect('calendar_view')
    
    context = {'event': event}
    return render(request, 'workforce_calendar/event_delete.html', context)

@login_required
def check_schedule_conflict(request):
    """Check if employee has schedule conflicts for leave request (API endpoint)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            employee_id = data.get('employee_id')
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
            
            employee = Employee.objects.get(employee_id=employee_id)
            
            # Check for events during requested period
            conflicts = WorkforceEvent.objects.filter(
                Q(participants=employee) | Q(department=employee.department),
                start_datetime__date__lte=end_date,
                end_datetime__date__gte=start_date
            ).select_related('created_by__user')
            
            has_conflict = conflicts.exists()
            conflict_list = [
                {
                    'title': event.title,
                    'start_date': event.start_datetime.date().isoformat(),
                    'end_date': event.end_datetime.date().isoformat(),
                    'type': event.event_type,
                    'location': event.location
                }
                for event in conflicts
            ]
            
            return JsonResponse({
                'success': True,
                'has_conflict': has_conflict,
                'conflicts': conflict_list,
                'message': f'Found {len(conflict_list)} conflicting events' if has_conflict else 'No conflicts found'
            })
            
        except Employee.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Employee not found'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)

@login_required
def my_calendar(request):
    """Display personal calendar for logged-in employee"""
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'Employee profile not found')
        return redirect('calendar_view')
    
    employee = request.user.employee_profile
    
    # Get events for current month
    start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
    
    # Get employee's events
    events = WorkforceEvent.objects.filter(
        Q(participants=employee) | Q(department=employee.department) | Q(created_by=employee),
        start_datetime__gte=start_date,
        start_datetime__lte=end_date
    ).distinct().order_by('start_datetime')
    
    # Get employee's leave requests
    from leave_management.models import LeaveRequest
    leave_requests = LeaveRequest.objects.filter(
        employee=employee,
        start_date__lte=end_date.date(),
        end_date__gte=start_date.date()
    ).order_by('start_date')
    
    context = {
        'employee': employee,
        'events': events,
        'leave_requests': leave_requests,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'workforce_calendar/my_calendar.html', context)