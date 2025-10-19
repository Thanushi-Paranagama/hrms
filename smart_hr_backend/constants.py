# Create this file: smart_hr_backend/constants.py

# Email Templates
EMAIL_TEMPLATES = {
    'ONBOARDING': 'emails/onboarding.html',
    'BIRTHDAY': 'emails/birthday.html',
    'LEAVE_APPROVAL': 'emails/leave_approval.html',
    'LEAVE_REJECTION': 'emails/leave_rejection.html',
    'SALARY_SLIP': 'emails/salary_slip.html',
}

# Attendance Status
ATTENDANCE_STATUS = {
    'PRESENT': 'Present',
    'ABSENT': 'Absent',
    'LATE': 'Late',
    'HALF_DAY': 'Half Day',
}

# Leave Status
LEAVE_STATUS = {
    'PENDING': 'Pending',
    'APPROVED': 'Approved',
    'REJECTED': 'Rejected',
    'CANCELLED': 'Cancelled',
}

# Employee Roles
EMPLOYEE_ROLES = {
    'ADMIN': 'Administrator',
    'HR': 'HR Team',
    'TECHNICIAN': 'Technician',
    'EMPLOYEE': 'Employee',
}

# Event Types
EVENT_TYPES = {
    'MEETING': 'Meeting',
    'DEADLINE': 'Deadline',
    'EVENT': 'Event',
    'HOLIDAY': 'Holiday',
    'TRAINING': 'Training',
}

# Recruitment Status
RECRUITMENT_STATUS = {
    'APPLIED': 'Application Received',
    'SCREENING': 'Under Screening',
    'INTERVIEW': 'Interview Scheduled',
    'OFFERED': 'Offer Extended',
    'HIRED': 'Hired',
    'REJECTED': 'Rejected',
}

# Salary calculation constants
WORKING_DAYS_PER_MONTH = 22
WORKING_HOURS_PER_DAY = 8

# Face recognition settings
FACE_RECOGNITION_TOLERANCE = 0.6
FACE_MIN_CONFIDENCE = 70.0

# File upload settings
MAX_RESUME_SIZE_MB = 5
MAX_PROFILE_IMAGE_SIZE_MB = 2
ALLOWED_RESUME_FORMATS = ['.pdf', '.doc', '.docx']
ALLOWED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png']