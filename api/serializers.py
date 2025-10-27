from rest_framework import serializers
from employees.models import Employee, Department
from attendance.models import Attendance
from leave_management.models import LeaveRequest, LeaveType
from salary.models import SalaryRecord
from workforce_calendar.models import WorkforceEvent


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'full_name', 'email', 'department', 
                  'department_name', 'role', 'phone_number', 'floor_number', 
                  'cabin_number', 'date_of_birth', 'is_active']


class AttendanceSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    location = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_id', 'employee_name', 'date', 
                  'check_in', 'check_out', 'status', 'face_verified', 'notes',
                  'latitude', 'longitude', 'location']
    
    def get_location(self, obj):
        """Return a formatted location string if coordinates exist"""
        if obj.latitude and obj.longitude:
            return f"{obj.latitude:.6f}, {obj.longitude:.6f}"
        return None


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'employee_name', 'leave_type', 'leave_type_name',
                  'start_date', 'end_date', 'days_requested', 'reason', 'status',
                  'rejection_reason', 'created_at']


class SalaryRecordSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    
    class Meta:
        model = SalaryRecord
        fields = ['id', 'employee', 'employee_name', 'month', 'year', 
                  'base_salary', 'bonuses', 'deductions', 'total_salary',
                  'days_worked', 'days_absent', 'days_leave', 'is_paid']


class WorkforceEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    start_datetime = serializers.DateTimeField(source='start_date', format='%Y-%m-%dT%H:%M:%S')
    end_datetime = serializers.DateTimeField(source='end_date', format='%Y-%m-%dT%H:%M:%S')
    all_day = serializers.BooleanField(source='is_all_day')
    
    class Meta:
        model = WorkforceEvent
        fields = ['id', 'title', 'description', 'event_type', 'start_datetime',
                  'end_datetime', 'all_day', 'location', 'created_by_name']
    
    def get_created_by_name(self, obj):
        if obj.created_by and obj.created_by.user:
            return obj.created_by.user.get_full_name()
        return "Unknown"