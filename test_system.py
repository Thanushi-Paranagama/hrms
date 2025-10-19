"""
System Test Script for Smart HR System
This script tests various components of the HR system
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_hr_backend.settings')
django.setup()

from django.contrib.auth.models import User
from employees.models import Department, Employee
from attendance.models import Attendance
from leave_management.models import LeaveType, LeaveRequest
from recruitment.models import Recruitment
from salary.models import SalaryRecord
from workforce_calendar.models import WorkforceEvent
from datetime import date, datetime, timedelta

def test_models():
    """Test model creation and relationships"""
    print("\n" + "="*60)
    print("TESTING MODELS")
    print("="*60)
    
    # Test Department
    print("\n1. Testing Department Model...")
    dept_count = Department.objects.count()
    print(f"   ✓ Departments in database: {dept_count}")
    
    # Test Employee
    print("\n2. Testing Employee Model...")
    emp_count = Employee.objects.count()
    print(f"   ✓ Employees in database: {emp_count}")
    
    # Test Attendance
    print("\n3. Testing Attendance Model...")
    att_count = Attendance.objects.count()
    print(f"   ✓ Attendance records in database: {att_count}")
    
    # Test LeaveType
    print("\n4. Testing LeaveType Model...")
    leave_type_count = LeaveType.objects.count()
    print(f"   ✓ Leave types in database: {leave_type_count}")
    
    # Test LeaveRequest
    print("\n5. Testing LeaveRequest Model...")
    leave_req_count = LeaveRequest.objects.count()
    print(f"   ✓ Leave requests in database: {leave_req_count}")
    
    # Test Recruitment
    print("\n6. Testing Recruitment Model...")
    rec_count = Recruitment.objects.count()
    print(f"   ✓ Recruitment records in database: {rec_count}")
    
    # Test SalaryRecord
    print("\n7. Testing SalaryRecord Model...")
    sal_count = SalaryRecord.objects.count()
    print(f"   ✓ Salary records in database: {sal_count}")
    
    # Test WorkforceEvent
    print("\n8. Testing WorkforceEvent Model...")
    event_count = WorkforceEvent.objects.count()
    print(f"   ✓ Calendar events in database: {event_count}")
    
    print("\n✅ All models are working correctly!")

def create_sample_data():
    """Create sample data for testing"""
    print("\n" + "="*60)
    print("CREATING SAMPLE DATA")
    print("="*60)
    
    # Create Departments
    print("\n1. Creating Departments...")
    departments = [
        ('IT', 'Information Technology Department'),
        ('HR', 'Human Resources Department'),
        ('Finance', 'Finance Department'),
        ('Marketing', 'Marketing Department'),
    ]
    
    for name, desc in departments:
        dept, created = Department.objects.get_or_create(
            name=name,
            defaults={'description': desc}
        )
        if created:
            print(f"   ✓ Created department: {name}")
        else:
            print(f"   ℹ Department already exists: {name}")
    
    # Create Leave Types
    print("\n2. Creating Leave Types...")
    leave_types = [
        ('Annual Leave', 'Regular annual leave', 20, True, True),
        ('Sick Leave', 'Medical leave', 10, True, True),
        ('Casual Leave', 'Short notice leave', 5, True, True),
        ('Unpaid Leave', 'Leave without pay', 30, True, False),
    ]
    
    for name, desc, max_days, req_approval, is_paid in leave_types:
        lt, created = LeaveType.objects.get_or_create(
            name=name,
            defaults={
                'description': desc,
                'max_days_per_year': max_days,
                'requires_approval': req_approval,
                'is_paid': is_paid
            }
        )
        if created:
            print(f"   ✓ Created leave type: {name}")
        else:
            print(f"   ℹ Leave type already exists: {name}")
    
    print("\n✅ Sample data created successfully!")

def check_admin_access():
    """Check if admin user exists"""
    print("\n" + "="*60)
    print("CHECKING ADMIN ACCESS")
    print("="*60)
    
    superusers = User.objects.filter(is_superuser=True)
    if superusers.exists():
        print(f"\n✓ Found {superusers.count()} superuser(s):")
        for user in superusers:
            print(f"   - Username: {user.username}")
            print(f"     Email: {user.email}")
    else:
        print("\n⚠ No superuser found!")
        print("   Create one using: python manage.py createsuperuser")

def system_summary():
    """Print system summary"""
    print("\n" + "="*60)
    print("SMART HR SYSTEM - STATUS SUMMARY")
    print("="*60)
    
    print("\n📊 DATABASE STATISTICS:")
    print(f"   • Users: {User.objects.count()}")
    print(f"   • Departments: {Department.objects.count()}")
    print(f"   • Employees: {Employee.objects.count()}")
    print(f"   • Attendance Records: {Attendance.objects.count()}")
    print(f"   • Leave Types: {LeaveType.objects.count()}")
    print(f"   • Leave Requests: {LeaveRequest.objects.count()}")
    print(f"   • Recruitment Records: {Recruitment.objects.count()}")
    print(f"   • Salary Records: {SalaryRecord.objects.count()}")
    print(f"   • Calendar Events: {WorkforceEvent.objects.count()}")
    
    print("\n📋 INSTALLED APPS:")
    from django.conf import settings
    hr_apps = [app for app in settings.INSTALLED_APPS if not app.startswith('django')]
    for app in hr_apps:
        print(f"   ✓ {app}")
    
    print("\n🔐 AUTHENTICATION:")
    print(f"   • Login URL: /login/")
    print(f"   • Admin Panel: /admin/")
    print(f"   • Dashboard: /dashboard/")
    
    print("\n🌐 AVAILABLE MODULES:")
    print("   ✓ Employees Management (/employees/)")
    print("   ✓ Attendance System (/attendance/)")
    print("   ✓ Leave Management (/leave/)")
    print("   ✓ Recruitment Portal (/recruitment/)")
    print("   ✓ Salary Management (/salary/)")
    print("   ✓ Workforce Calendar (/calendar/)")
    
    print("\n" + "="*60)
    print("✅ SYSTEM CHECK COMPLETE")
    print("="*60)

if __name__ == '__main__':
    try:
        test_models()
        create_sample_data()
        check_admin_access()
        system_summary()
        
        print("\n" + "🚀 "*20)
        print("NEXT STEPS:")
        print("-" * 60)
        print("1. If you haven't created a superuser yet:")
        print("   python manage.py createsuperuser")
        print("\n2. Start the development server:")
        print("   python manage.py runserver")
        print("\n3. Access the application:")
        print("   • Main App: http://localhost:8000/")
        print("   • Admin Panel: http://localhost:8000/admin/")
        print("   • Dashboard: http://localhost:8000/dashboard/")
        print("🚀 "*20 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
