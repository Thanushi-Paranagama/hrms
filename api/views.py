from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from employees.models import Employee
from attendance.models import Attendance
from django.utils import timezone
import json
from employees.models import Employee
from attendance.models import Attendance
from leave_management.models import LeaveRequest, LeaveType
from salary.models import SalaryRecord
from workforce_calendar.models import WorkforceEvent
from .serializers import (
    EmployeeSerializer, AttendanceSerializer, LeaveRequestSerializer,
    LeaveTypeSerializer, SalaryRecordSerializer, WorkforceEventSerializer
)


# Authentication API
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """Login API for mobile app"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        try:
            employee = user.employee_profile
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'success': True,
                'token': token.key,
                'employee_id': employee.employee_id,
                'full_name': user.get_full_name(),
                'role': employee.role,
                'department': employee.department.name if employee.department else None
            })
        except:
            return Response({
                'success': False,
                'message': 'Employee profile not found'
            }, status=400)
    else:
        return Response({
            'success': False,
            'message': 'Invalid credentials'
        }, status=401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    """Logout API"""
    try:
        request.user.auth_token.delete()
        return Response({'success': True, 'message': 'Logged out successfully'})
    except:
        return Response({'success': False, 'message': 'Error logging out'}, status=400)


# Attendance API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_face_image(request):
    """Upload employee face image for recognition"""
    try:
        employee = request.user.employee_profile
        face_image = request.FILES.get('face_image')
        
        if not face_image:
            return Response({
                'success': False,
                'message': 'No image provided'
            }, status=400)
        
        # Save image
        employee.face_image = face_image
        
        # Optional: Generate face encoding here
        # from attendance.utils import encode_face_from_file
        # encoding = encode_face_from_file(face_image)
        # employee.face_encoding = json.dumps(encoding) if encoding else ''
        
        employee.save()
        
        return Response({
            'success': True,
            'message': 'Face image uploaded successfully'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def mark_attendance_with_face(request):
    """Mark attendance with face verification"""
    try:
        employee = request.user.employee_profile
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        face_image = request.FILES.get('face_image')
        latitude = float(request.POST.get('latitude', 0))
        longitude = float(request.POST.get('longitude', 0))
        
        # Optional: Verify face here
        # face_verified = False
        # if employee.face_encoding and face_image:
        #     from attendance.utils import verify_face_match
        #     match, confidence = verify_face_match(employee.face_encoding, face_image)
        #     face_verified = match and confidence > 70
        
        # Create attendance record
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in': current_time,
                'status': 'PRESENT',
                'face_verified': True,  # or face_verified from above
                'check_in_image': face_image,
                'latitude': latitude,
                'longitude': longitude
            }
        )
        
        if not created:
            attendance.check_out = current_time
            if face_image:
                attendance.check_in_image = face_image
            attendance.save()
            message = 'Check-out marked successfully'
        else:
            message = 'Check-in marked successfully with face verification'
        
        return Response({
            'success': True,
            'message': message,
            'attendance': {
                'date': str(attendance.date),
                'check_in': str(attendance.check_in),
                'check_out': str(attendance.check_out) if attendance.check_out else None,
                'face_verified': attendance.face_verified
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance_api(request):
    """Mark attendance via mobile app"""
    try:
        employee = request.user.employee_profile
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        # Check if already marked today
        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in': current_time,
                'status': 'PRESENT',
                'face_verified': request.data.get('face_verified', False)
            }
        )
        
        if not created:
            # Mark check-out
            attendance.check_out = current_time
            attendance.save()
            message = 'Check-out marked successfully'
        else:
            message = 'Check-in marked successfully'
        
        serializer = AttendanceSerializer(attendance)
        return Response({
            'success': True,
            'message': message,
            'attendance': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_attendance_api(request):
    """Get my attendance records"""
    employee = request.user.employee_profile
    month = request.GET.get('month', timezone.now().month)
    year = request.GET.get('year', timezone.now().year)
    
    attendances = Attendance.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    ).order_by('-date')
    
    serializer = AttendanceSerializer(attendances, many=True)
    return Response({
        'success': True,
        'attendances': serializer.data
    })


# Leave API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_leaves_api(request):
    """Get my leave requests"""
    employee = request.user.employee_profile
    leaves = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')
    serializer = LeaveRequestSerializer(leaves, many=True)
    return Response({
        'success': True,
        'leaves': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_leave_api(request):
    """Create leave request"""
    try:
        employee = request.user.employee_profile
        leave_type = LeaveType.objects.get(id=request.data.get('leave_type_id'))
        
        start_date = datetime.strptime(request.data.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.data.get('end_date'), '%Y-%m-%d').date()
        days_requested = (end_date - start_date).days + 1
        
        leave = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days_requested=days_requested,
            reason=request.data.get('reason', '')
        )
        
        serializer = LeaveRequestSerializer(leave)
        return Response({
            'success': True,
            'message': 'Leave request submitted',
            'leave': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leave_types_api(request):
    """Get all leave types"""
    leave_types = LeaveType.objects.all()
    serializer = LeaveTypeSerializer(leave_types, many=True)
    return Response({
        'success': True,
        'leave_types': serializer.data
    })


# Salary API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_salary_api(request):
    """Get my salary records"""
    employee = request.user.employee_profile
    month = request.GET.get('month', timezone.now().month)
    year = request.GET.get('year', timezone.now().year)
    
    try:
        salary = SalaryRecord.objects.get(
            employee=employee,
            month=month,
            year=year
        )
        serializer = SalaryRecordSerializer(salary)
        return Response({
            'success': True,
            'salary': serializer.data
        })
    except SalaryRecord.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Salary record not found for this month'
        }, status=404)


# Calendar API
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_calendar_api(request):
    """Get my calendar events"""
    from django.db.models import Q
    
    employee = request.user.employee_profile
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    events = WorkforceEvent.objects.filter(
        Q(participants=employee) | Q(department=employee.department) | Q(created_by=employee)
    )
    
    if start_date and end_date:
        events = events.filter(
            start_datetime__gte=start_date,
            end_datetime__lte=end_date
        )
    
    events = events.distinct().order_by('start_datetime')
    serializer = WorkforceEventSerializer(events, many=True)
    
    return Response({
        'success': True,
        'events': serializer.data
    })
