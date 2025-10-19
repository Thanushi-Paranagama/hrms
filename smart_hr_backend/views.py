# smart_hr_backend/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from employees.models import Employee
from attendance.models import Attendance
from leave_management.models import LeaveRequest
from recruitment.models import Recruitment
from django.db.models import Count, Q


def home(request):
    """Home page - redirects to login or dashboard"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect to next parameter or dashboard
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard(request):
    """Main dashboard view"""
    context = {
        'today': timezone.now().date(),
    }
    
    # Get employee profile if exists
    try:
        employee = request.user.employee_profile
        context['employee'] = employee
    except:
        # User doesn't have employee profile
        if request.user.is_staff or request.user.is_superuser:
            # Admin users without profile can still access dashboard
            employee = None
        else:
            messages.warning(request, 'Your employee profile is not set up. Please contact HR.')
            return redirect('admin:index')
    
    # Get statistics
    today = timezone.now().date()
    current_month = timezone.now().month
    current_year = timezone.now().year
    
    # Total employees
    context['total_employees'] = Employee.objects.filter(is_active=True).count()
    
    # Today's attendance
    today_attendance = Attendance.objects.filter(date=today)
    context['today_present'] = today_attendance.filter(
        Q(status='PRESENT') | Q(status='LATE')
    ).count()
    context['today_absent'] = today_attendance.filter(status='ABSENT').count()
    
    # Pending leave requests
    context['pending_leaves'] = LeaveRequest.objects.filter(status='PENDING').count()
    
    # Active recruitment
    context['active_recruitments'] = Recruitment.objects.exclude(
        status__in=['HIRED', 'REJECTED']
    ).count()
    
    # Recent activities
    context['recent_leaves'] = LeaveRequest.objects.select_related(
        'employee__user', 'leave_type'
    ).order_by('-created_at')[:5]
    
    context['recent_recruitments'] = Recruitment.objects.order_by('-created_at')[:5]
    
    # User role-based data
    if employee:
        # Employee's own data
        context['my_attendance_this_month'] = Attendance.objects.filter(
            employee=employee,
            date__month=current_month,
            date__year=current_year,
            status__in=['PRESENT', 'LATE']
        ).count()
        
        context['my_leaves'] = LeaveRequest.objects.filter(
            employee=employee
        ).order_by('-created_at')[:3]
    
    return render(request, 'dashboard.html', context)


@login_required
def profile_view(request):
    """User profile view"""
    try:
        employee = request.user.employee_profile
        return redirect('employee_detail', employee_id=employee.employee_id)
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('dashboard')
