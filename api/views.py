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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from leave_management.models import LeaveType, LeaveRequest
from .serializers import LeaveTypeSerializer, LeaveRequestSerializer
import json
from employees.models import Employee
from attendance.models import Attendance
from leave_management.models import LeaveRequest, LeaveType
from salary.models import SalaryRecord
from workforce_calendar.models import WorkforceEvent
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Q
from workforce_calendar.models import WorkforceEvent
from .serializers import WorkforceEventSerializer
from .serializers import (
    EmployeeSerializer, AttendanceSerializer, LeaveRequestSerializer,
    LeaveTypeSerializer, SalaryRecordSerializer, WorkforceEventSerializer
)
import logging
logger = logging.getLogger(__name__)


# Authentication API
@api_view(['POST'])
@permission_classes([AllowAny])
def login_api(request):
    """Login API for mobile app"""
    print("[DEBUG] Login attempt - Headers:", dict(request.headers))
    print("[DEBUG] Login attempt - Data:", request.data)
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        try:
            employee = user.employee_profile
            token, _ = Token.objects.get_or_create(user=user)
            
            # Check if face is registered
            # Face is considered registered if face_encoding field exists and is not empty
            face_registered = bool(employee.face_encoding and employee.face_encoding.strip())
            
            # Debug logging
            print(f"[DEBUG] Employee: {employee.employee_id}")
            print(f"[DEBUG] Face encoding exists: {bool(employee.face_encoding)}")
            print(f"[DEBUG] Face registered: {face_registered}")
            
            return Response({
                'success': True,
                'token': token.key,
                'employee_id': employee.employee_id,
                'full_name': user.get_full_name(),
                'role': employee.role,
                'department': employee.department.name if employee.department else None,
                'is_face_registered': face_registered  # ← ADDED: This matches Android's @SerializedName
            })
        except Exception as e:
            print(f"[DEBUG] Error getting employee profile: {str(e)}")
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
from .decorators import api_view_with_file_upload

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_face_image(request):
    """Upload employee face image for recognition"""
    # Enhanced debug logging
    logger.info("Upload attempt - Headers: %s", dict(request.headers))
    logger.info("Upload attempt - Auth: %s", request.META.get('HTTP_AUTHORIZATION', 'No Auth header'))
    logger.info("Upload attempt - User: %s, Authenticated: %s", request.user, request.user.is_authenticated)
    
    # Check authentication first
    if not request.user.is_authenticated:
        return Response({
            'error': 'Authentication credentials were not provided.',
            'detail': 'You must provide a valid token in the Authorization header'
        }, status=401)
        
    logger.info("Upload attempt - Files: %s", request.FILES)
    logger.info("Upload attempt - Data: %s", request.POST)
    try:
        try:
            employee = request.user.employee_profile
        except Exception:
            return Response({'success': False, 'message': 'Employee profile not found'}, status=400)
        face_image = request.FILES.get('face_image')
        
        if not face_image:
            return Response({
                'success': False,
                'message': 'No image provided'
            }, status=400)
        
        # Save image
        employee.face_image = face_image
        employee.save()
        
        # Generate face encoding
        from employees.face_recognition_utils import encode_face
        encoding = encode_face(employee.face_image.path)
        
        if not encoding:
            return Response({
                'success': False,
                'message': 'No face detected in the image. Please upload a clear photo of your face.'
            }, status=400)
            
        # Store the encoding
        employee.face_encoding = json.dumps(encoding)
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
        try:
            employee = request.user.employee_profile
        except Exception:
            return Response({'success': False, 'message': 'Employee profile not found'}, status=400)
        today = timezone.now().date()
        current_time = timezone.now().time()
        
        face_image = request.FILES.get('face_image')

        # Parse and validate coordinates
        try:
            latitude = float(request.POST.get('latitude', '6.82114889822254'))
            longitude = float(request.POST.get('longitude', '79.8806658352055'))
            if not (5.0 <= latitude <= 10.0 and 79.0 <= longitude <= 82.0):
                return Response({'success': False, 'message': 'Location coordinates must be within Sri Lanka'}, status=400)
        except (ValueError, TypeError):
            return Response({'success': False, 'message': 'Invalid latitude or longitude values'}, status=400)

        # Require that the authenticated user has registered face encoding
        if not (employee.face_encoding and employee.face_encoding.strip()):
            return Response({'success': False, 'message': 'Face not registered for this account. Please upload your face image first.'}, status=400)

        # Verify the uploaded face matches the registered encoding
        if not face_image:
            return Response({'success': False, 'message': 'No face image provided for verification'}, status=400)

        import tempfile, os
        from employees.face_recognition_utils import verify_face

        tmp_path = None
        try:
            # Save uploaded file to a temporary file for face_recognition library
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                for chunk in face_image.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            # Load stored encoding
            try:
                known_encoding = json.loads(employee.face_encoding)
            except Exception:
                return Response({'success': False, 'message': 'Stored face encoding is invalid'}, status=500)

            match = verify_face(known_encoding, tmp_path)
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

        if not match:
            return Response({'success': False, 'message': 'Face does not match the registered user'}, status=401)

        # Face verified — proceed to create/update attendance
        face_verified = True

        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={
                'check_in': current_time,
                'status': 'PRESENT',
                'face_verified': face_verified,
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
        try:
            employee = request.user.employee_profile
        except Exception:
            return Response({'success': False, 'message': 'Employee profile not found'}, status=400)
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
    try:
        employee = request.user.employee_profile
    except Exception:
        return Response({'success': False, 'message': 'Employee profile not found'}, status=400)
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
def leave_types_api(request):
    """
    Get all available leave types
    """
    try:
        leave_types = LeaveType.objects.all()
        serializer = LeaveTypeSerializer(leave_types, many=True)
        
        return Response({
            'success': True,
            'leave_types': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_leave_api(request):
    """
    Create a new leave request
    """
    try:
        # Check if user has employee profile
        if not hasattr(request.user, 'employee_profile'):
            return Response({
                'success': False,
                'message': 'Employee profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        employee = request.user.employee_profile
        
        # Get data from request
        leave_type_id = request.data.get('leave_type_id')
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        reason = request.data.get('reason', '')
        
        # Validate required fields
        if not all([leave_type_id, start_date_str, end_date_str]):
            return Response({
                'success': False,
                'message': 'Missing required fields'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get leave type
        try:
            leave_type = LeaveType.objects.get(id=leave_type_id)
        except LeaveType.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Leave type not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Parse dates
        from datetime import datetime
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate dates
        if start_date > end_date:
            return Response({
                'success': False,
                'message': 'End date must be after start date'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from django.utils import timezone as tz
        if start_date < tz.now().date():
            return Response({
                'success': False,
                'message': 'Cannot request leave for past dates'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate days
        days_requested = (end_date - start_date).days + 1
        
        # Create leave request
        leave_request = LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            days_requested=days_requested,
            reason=reason,
            status='PENDING'
        )
        
        return Response({
            'success': True,
            'message': 'Leave request submitted successfully',
            'leave_id': leave_request.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error creating leave request: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_leaves_api(request):
    """
    Get leave requests for the authenticated employee
    """
    try:
        # Check if user has employee profile
        if not hasattr(request.user, 'employee_profile'):
            return Response({
                'success': False,
                'message': 'Employee profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        employee = request.user.employee_profile
        
        # Get employee's leave requests
        leaves = LeaveRequest.objects.filter(
            employee=employee
        ).select_related('leave_type', 'approved_by__user').order_by('-created_at')
        
        serializer = LeaveRequestSerializer(leaves, many=True)
        
        return Response({
            'success': True,
            'leaves': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_leaves_api(request):
    """Get my leave requests"""
    try:
        employee = request.user.employee_profile
    except Exception:
        return Response({'success': False, 'message': 'Employee profile not found'}, status=400)
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
        try:
            employee = request.user.employee_profile
        except Exception:
            return Response({'success': False, 'message': 'Employee profile not found'}, status=400)
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
    try:
        employee = request.user.employee_profile
    except Exception:
        return Response({'success': False, 'message': 'Employee profile not found'}, status=400)
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
    """
    API endpoint to get calendar events for the authenticated employee
    Query params: start_date, end_date (optional, format: YYYY-MM-DD)
    """
    try:
        # Check if user has employee profile
        if not hasattr(request.user, 'employee_profile'):
            return Response({
                'success': False,
                'error': 'Employee profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        employee = request.user.employee_profile
        
        # Get date range from query params
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                # Set end_date to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return Response({
                    'success': False,
                    'error': 'Invalid date format. Use YYYY-MM-DD'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Default to current month
            start_date = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        # Make dates timezone-aware if needed
        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)
        if timezone.is_naive(end_date):
            end_date = timezone.make_aware(end_date)
        
        # Get employee's events (where they are participant, or in same department, or creator)
        events = WorkforceEvent.objects.filter(
            Q(employees=employee) | 
            Q(employees__department=employee.department) | 
            Q(created_by=employee),
            start_date__lte=end_date,
            end_date__gte=start_date
        ).distinct().order_by('start_date').select_related('created_by__user')
        
        # Serialize events
        serializer = WorkforceEventSerializer(events, many=True)
        
        return Response({
            'success': True,
            'events': serializer.data,
            'count': events.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_calendar_api(request):
    """Get my calendar events"""
    from django.db.models import Q
    try:
        employee = request.user.employee_profile
    except Exception:
        return Response({'success': False, 'message': 'Employee profile not found'}, status=400)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    events = WorkforceEvent.objects.filter(
        Q(employees=employee) | Q(employees__department=employee.department) | Q(created_by=employee)
    )
    
    if start_date and end_date:
        events = events.filter(
            start_date__gte=start_date,
            end_date__lte=end_date
        )
    
    events = events.distinct().order_by('start_date')
    serializer = WorkforceEventSerializer(events, many=True)
    
    return Response({
        'success': True,
        'events': serializer.data
    })
