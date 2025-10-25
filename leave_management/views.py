# leave_management/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from .models import LeaveRequest, LeaveType
from employees.models import Employee
from django.http import JsonResponse
from django.db.models import Q

@login_required
def leave_request_list(request):
    """Display list of leave requests based on user role"""
    try:
        emp = request.user.employee_profile
    except Exception:
        emp = None

    # Allow filtering by status via ?status= (All/PENDING/APPROVED/REJECTED/CANCELLED)
    status_filter = request.GET.get('status')

    # Allow staff/superuser access even if they don't have an employee_profile
    is_staff_user = request.user.is_staff or request.user.is_superuser

    if emp:
        if emp.role in ['HR', 'ADMIN']:
            # HR and Admin see all leave requests
            qs = LeaveRequest.objects.all().select_related(
                'employee__user', 'leave_type', 'approved_by__user'
            ).order_by('-created_at')
        else:
            # Employees see only their own requests
            qs = LeaveRequest.objects.filter(
                employee=emp
            ).select_related('leave_type', 'approved_by__user').order_by('-created_at')
    else:
        if is_staff_user:
            qs = LeaveRequest.objects.all().select_related(
                'employee__user', 'leave_type', 'approved_by__user'
            ).order_by('-created_at')
        else:
            qs = LeaveRequest.objects.none()

    if status_filter:
        qs = qs.filter(status=status_filter)

    leave_requests = qs

    context = {
        'leave_requests': leave_requests,
        'status': status_filter or '',
        'user_has_profile': bool(emp),
        'user_emp': emp,
        # Treat site staff/superusers as HR for UI actions
        'user_is_hr': bool((emp and emp.role in ['HR', 'ADMIN']) or is_staff_user),
    }
    return render(request, 'leave_management/leave_list.html', context)

@login_required
def leave_request_create(request):
    """Create a new leave request"""
    if request.method == 'POST':
        try:
            # Determine which employee this leave is for.
            # If requester is staff/superuser and provided an employee_pk, allow creating on behalf.
            target_employee = None
            if (request.user.is_staff or request.user.is_superuser) and request.POST.get('employee_pk'):
                try:
                    target_employee = Employee.objects.get(pk=int(request.POST.get('employee_pk')))
                except Exception:
                    messages.error(request, 'Selected employee not found')
                    return redirect('leave_request_create')

            if not target_employee:
                if not hasattr(request.user, 'employee_profile'):
                    messages.error(request, 'No employee profile found for your account. Please contact HR.')
                    return redirect('leave_request_create')
                target_employee = request.user.employee_profile

            leave_type = LeaveType.objects.get(id=request.POST.get('leave_type_id'))

            start_date = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d').date()
            days_requested = (end_date - start_date).days + 1

            # Validate dates
            if start_date > end_date:
                messages.error(request, 'End date must be after start date')
                return redirect('leave_request_create')

            if start_date < timezone.now().date():
                messages.error(request, 'Cannot request leave for past dates')
                return redirect('leave_request_create')

            # Create leave request for target_employee
            leave_request = LeaveRequest.objects.create(
                employee=target_employee,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                days_requested=days_requested,
                reason=request.POST.get('reason', '')
            )

            messages.success(request, 'Leave request submitted successfully')
            return redirect('leave_request_list')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    leave_types = LeaveType.objects.all()
    # Provide today's date for template min attributes
    today = timezone.now().date()
    # Allow staff users to create leave for others
    is_staff_user = request.user.is_staff or request.user.is_superuser
    context = {
        'leave_types': leave_types,
        'today': today,
        'user_has_profile': hasattr(request.user, 'employee_profile'),
        'is_staff_user': is_staff_user,
    }
    return render(request, 'leave_management/leave_create.html', context)


@login_required
def employee_search(request):
    """Return JSON list of employees matching a query. Restricted to staff or HR/ADMIN roles."""
    q = request.GET.get('q', '').strip()
    results = []

    # Basic permission: only staff/superuser or HR/ADMIN employees can search
    try:
        emp = request.user.employee_profile
    except Exception:
        emp = None

    is_staff_user = request.user.is_staff or request.user.is_superuser
    allowed = is_staff_user or (emp and emp.role in ['HR', 'ADMIN'])

    if not allowed:
        return JsonResponse({'results': []})

    if q:
        qs = Employee.objects.select_related('user').filter(
            Q(employee_id__icontains=q) |
            Q(user__username__icontains=q) |
            Q(user__first_name__icontains=q) |
            Q(user__last_name__icontains=q)
        )[:15]

        for e in qs:
            results.append({
                'pk': e.pk,
                'employee_id': e.employee_id,
                'name': e.user.get_full_name() or e.user.username,
            })

    return JsonResponse({'results': results})

@login_required
def leave_request_approve(request, leave_id):
    """Approve or reject a leave request (HR/Admin only)"""
    try:
        emp = request.user.employee_profile
    except Exception:
        emp = None

    # Allow staff/superuser (admin) to approve/reject even if they don't have an employee_profile
    is_staff_user = request.user.is_staff or request.user.is_superuser

    if not ((emp and emp.role in ['HR', 'ADMIN']) or is_staff_user):
        messages.error(request, 'You do not have permission to approve leave requests')
        return redirect('leave_request_list')

    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            leave_request.status = 'APPROVED'
            # If the approver has an Employee profile, link it; otherwise leave null
            leave_request.approved_by = emp if emp else None
            leave_request.approval_date = timezone.now()
            
            # Send approval email
            try:
                send_mail(
                    'Leave Request Approved',
                    f'Your leave request from {leave_request.start_date} to {leave_request.end_date} has been approved.',
                    settings.DEFAULT_FROM_EMAIL,
                    [leave_request.employee.user.email],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, 'Leave request approved successfully')
        
        elif action == 'reject':
            leave_request.status = 'REJECTED'
            leave_request.rejection_reason = request.POST.get('rejection_reason', '')
            # Record who rejected (if available)
            leave_request.approved_by = emp if emp else None
            leave_request.approval_date = timezone.now()
            
            # Send rejection email
            try:
                send_mail(
                    'Leave Request Rejected',
                    f'Your leave request from {leave_request.start_date} to {leave_request.end_date} has been rejected.\nReason: {leave_request.rejection_reason}',
                    settings.DEFAULT_FROM_EMAIL,
                    [leave_request.employee.user.email],
                    fail_silently=True,
                )
            except:
                pass
            
            messages.success(request, 'Leave request rejected')
        
        leave_request.save()
        return redirect('leave_request_list')
    
    context = {'leave_request': leave_request}
    return render(request, 'leave_management/leave_approve.html', context)

@login_required
def leave_request_cancel(request, leave_id):
    """Cancel a leave request (employee can cancel their own pending requests)"""
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    if not hasattr(request.user, 'employee_profile'):
        messages.error(request, 'No employee profile found for your account. Cannot cancel leave.')
        return redirect('leave_request_list')

    # Check if user owns this request
    if leave_request.employee != request.user.employee_profile:
        messages.error(request, 'You can only cancel your own leave requests')
        return redirect('leave_request_list')
    
    # Can only cancel pending requests
    if leave_request.status != 'PENDING':
        messages.error(request, 'You can only cancel pending leave requests')
        return redirect('leave_request_list')
    
    leave_request.status = 'CANCELLED'
    leave_request.save()
    
    messages.success(request, 'Leave request cancelled successfully')
    return redirect('leave_request_list')

