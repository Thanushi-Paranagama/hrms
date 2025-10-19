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

@login_required
def leave_request_list(request):
    """Display list of leave requests based on user role"""
    if hasattr(request.user, 'employee_profile'):
        if request.user.employee_profile.role in ['HR', 'ADMIN']:
            # HR and Admin see all leave requests
            leave_requests = LeaveRequest.objects.all().select_related(
                'employee__user', 'leave_type', 'approved_by__user'
            ).order_by('-created_at')
        else:
            # Employees see only their own requests
            leave_requests = LeaveRequest.objects.filter(
                employee=request.user.employee_profile
            ).select_related('leave_type', 'approved_by__user').order_by('-created_at')
    else:
        leave_requests = []
    
    context = {'leave_requests': leave_requests}
    return render(request, 'leave_management/leave_list.html', context)

@login_required
def leave_request_create(request):
    """Create a new leave request"""
    if request.method == 'POST':
        try:
            employee = request.user.employee_profile
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
            
            # Create leave request
            leave_request = LeaveRequest.objects.create(
                employee=employee,
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
    context = {'leave_types': leave_types}
    return render(request, 'leave_management/leave_create.html', context)

@login_required
def leave_request_approve(request, leave_id):
    """Approve or reject a leave request (HR/Admin only)"""
    if not hasattr(request.user, 'employee_profile') or \
       request.user.employee_profile.role not in ['HR', 'ADMIN']:
        messages.error(request, 'You do not have permission to approve leave requests')
        return redirect('leave_request_list')
    
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            leave_request.status = 'APPROVED'
            leave_request.approved_by = request.user.employee_profile
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
            leave_request.approved_by = request.user.employee_profile
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

