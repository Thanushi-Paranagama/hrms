# Create this file: workforce_calendar/utils.py

from datetime import datetime, timedelta
from django.db.models import Q


def check_event_conflicts(employee, start_dt, end_dt, exclude_event_id=None):
    """
    Check if employee has conflicting events in the given time range
    
    Returns: (has_conflict: bool, conflicts: list)
    """
    from workforce_calendar.models import WorkforceEvent

    # Query for overlapping events (employee participates or employees in same department)
    conflicts_query = WorkforceEvent.objects.filter(
        Q(employees=employee) | Q(employees__department=employee.department),
        start_date__lt=end_dt,
        end_date__gt=start_dt
    )
    
    # Exclude specific event if updating
    if exclude_event_id:
        conflicts_query = conflicts_query.exclude(id=exclude_event_id)
    
    conflicts = list(conflicts_query)
    
    return len(conflicts) > 0, conflicts


def check_leave_conflicts(employee, start_date, end_date):
    """
    Check if employee has approved leaves or important events during the date range
    
    Returns: dict with conflict information
    """
    from workforce_calendar.models import WorkforceEvent
    from leave_management.models import LeaveRequest
    
    # Check for approved leaves
    existing_leaves = LeaveRequest.objects.filter(
        employee=employee,
        status='APPROVED',
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    
    # Check for important events
    important_events = WorkforceEvent.objects.filter(
        Q(employees=employee) | Q(employees__department=employee.department),
        start_date__date__lte=end_date,
        end_date__date__gte=start_date,
        event_type__in=['MEETING', 'DEADLINE', 'TRAINING']
    )
    
    return {
        'has_leave_conflict': existing_leaves.exists(),
        'conflicting_leaves': list(existing_leaves),
        'has_event_conflict': important_events.exists(),
        'conflicting_events': list(important_events),
        'total_conflicts': existing_leaves.count() + important_events.count()
    }


def get_upcoming_events(employee, days=7):
    """Get upcoming events for an employee within specified days"""
    from workforce_calendar.models import WorkforceEvent
    from django.utils import timezone
    
    start_date = timezone.now()
    end_date = start_date + timedelta(days=days)
    
    events = WorkforceEvent.objects.filter(
        Q(employees=employee) | Q(employees__department=employee.department) | Q(created_by=employee),
        start_date__gte=start_date,
        start_date__lte=end_date
    ).distinct().order_by('start_date')
    
    return events
