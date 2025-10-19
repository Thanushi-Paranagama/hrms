# Smart HR Management System

A comprehensive Django-based Human Resources Management System with advanced features including face recognition attendance, automated salary processing, recruitment tracking, and workforce calendar management.

## 🚀 Features

### 1. **Employee Management**
- Complete employee profile management
- Department and role assignment
- Face recognition integration for attendance
- User authentication linkage
- Personal and employment information tracking

### 2. **Attendance System**
- Face recognition-based attendance marking
- Manual attendance recording
- Check-in/Check-out tracking
- Hours worked calculation
- Monthly attendance reports
- Status tracking (Present, Absent, Late, Half-Day)

### 3. **Leave Management**
- Multiple leave types (Annual, Sick, Casual, Unpaid)
- Leave request submission
- Approval workflow
- Leave balance tracking
- Calendar integration for conflict checking

### 4. **Recruitment Portal**
- Candidate application tracking
- Resume management
- Interview scheduling
- Multi-stage recruitment pipeline
- Hiring workflow automation
- Candidate status tracking (Applied → Screening → Interview → Offered → Hired)

### 5. **Salary Management**
- Automated salary calculation
- Attendance-based salary adjustment
- Bonus and deduction management
- Monthly payroll generation
- Payment tracking
- Salary reports

### 6. **Workforce Calendar**
- Event management (Meetings, Deadlines, Holidays, Training)
- Department-wide events
- Personal calendar view
- Schedule conflict detection
- Event notifications

## 📋 Technology Stack

- **Backend**: Django 5.2.7
- **Database**: SQLite (Development) / PostgreSQL (Production ready)
- **Frontend**: Bootstrap 5, Font Awesome, Chart.js
- **Authentication**: Django Session-based Auth
- **API**: Django REST Framework
- **Face Recognition**: OpenCV, face_recognition library
- **Additional**: CORS Headers for API support

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Step 1: Clone and Setup Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Database Setup
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### Step 4: Load Sample Data
```bash
# Run the test script to create sample departments and leave types
python test_system.py
```

### Step 5: Run Development Server
```bash
python manage.py runserver
```

Access the application at: **http://localhost:8000/**

## 🔐 Default Access

### Admin Panel
- URL: http://localhost:8000/admin/
- Use the superuser credentials created in Step 3

### Application Login
- URL: http://localhost:8000/login/
- Dashboard: http://localhost:8000/dashboard/

## 📁 Project Structure

```
smart_hr_system/
├── attendance/              # Attendance management module
│   ├── models.py           # Attendance data model
│   ├── views.py            # Attendance views and logic
│   ├── admin.py            # Admin panel configuration
│   └── templates/          # Attendance HTML templates
│
├── employees/              # Employee management module
│   ├── models.py           # Employee and Department models
│   ├── views.py            # Employee CRUD operations
│   ├── face_recognition_utils.py  # Face recognition utilities
│   └── templates/          # Employee HTML templates
│
├── leave_management/       # Leave request module
│   ├── models.py           # Leave types and requests
│   ├── views.py            # Leave approval workflow
│   └── templates/          # Leave management templates
│
├── recruitment/            # Recruitment tracking module
│   ├── models.py           # Candidate and application models
│   ├── views.py            # Recruitment pipeline logic
│   └── templates/          # Recruitment templates
│
├── salary/                 # Payroll management module
│   ├── models.py           # Salary records model
│   ├── views.py            # Salary calculation logic
│   ├── utils.py            # Salary calculation utilities
│   └── templates/          # Salary reports templates
│
├── workforce_calendar/     # Calendar and events module
│   ├── models.py           # Event model
│   ├── views.py            # Calendar views
│   └── templates/          # Calendar templates
│
├── smart_hr_backend/       # Main project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL routing
│   ├── views.py            # Authentication views
│   └── middleware.py       # Custom middleware
│
├── templates/              # Global templates
│   ├── base.html           # Base template with navigation
│   ├── dashboard.html      # Main dashboard
│   └── auth/               # Authentication templates
│
├── media/                  # Uploaded files
│   ├── face_images/        # Face recognition images
│   ├── resumes/            # Candidate resumes
│   └── attendance_images/  # Attendance verification images
│
├── staticfiles/            # Static files (CSS, JS, images)
├── db.sqlite3              # Database file
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── test_system.py          # System test and initialization script
```

## 🎯 Key Models

### Employee Model
- Links to Django User model
- Department assignment
- Role-based access control (Admin, HR, Technician, Employee)
- Face encoding storage
- Personal and contact information

### Attendance Model
- Employee reference
- Date, check-in, check-out times
- Status tracking
- Hours worked calculation
- Optional attendance image

### LeaveRequest Model
- Employee reference
- Leave type and duration
- Approval workflow
- Status tracking (Pending, Approved, Rejected, Cancelled)

### Recruitment Model
- Candidate information
- Resume storage
- Interview scheduling
- Status pipeline
- Hiring conversion

### SalaryRecord Model
- Monthly salary records
- Attendance-based calculations
- Bonus and deduction tracking
- Payment status

### WorkforceEvent Model
- Calendar events
- Employee participants
- Event types (Meeting, Deadline, Event, Holiday, Training)
- All-day event support

## 🔧 Configuration

### Settings (smart_hr_backend/settings.py)

```python
# Authentication
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'
SESSION_COOKIE_AGE = 86400  # 24 hours

# Email Configuration (Development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# For Production, configure PostgreSQL:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'hr_system_db',
#         'USER': 'your_user',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }
```

## 📊 Admin Panel Features

All models are registered in the Django admin panel with:
- Custom list displays
- Search functionality
- Filtering options
- Organized fieldsets
- Readonly fields for metadata
- Date hierarchies

### Access Admin Panel
1. Navigate to http://localhost:8000/admin/
2. Login with superuser credentials
3. Manage all data from centralized interface

## 🌐 URL Structure

| Module | URL Pattern | Description |
|--------|-------------|-------------|
| **Main** | `/` | Home (redirects to login/dashboard) |
| | `/login/` | User login page |
| | `/logout/` | Logout handler |
| | `/dashboard/` | Main dashboard |
| | `/admin/` | Django admin panel |
| **Employees** | `/employees/` | Employee list |
| | `/employees/<id>/` | Employee detail |
| | `/employees/create/` | Create new employee |
| **Attendance** | `/attendance/` | Attendance dashboard |
| | `/attendance/mark/` | Mark attendance |
| | `/attendance/report/` | Attendance reports |
| **Leave** | `/leave/` | Leave requests list |
| | `/leave/create/` | Submit leave request |
| | `/leave/approve/<id>/` | Approve/reject leave |
| **Recruitment** | `/recruitment/` | Candidate list |
| | `/recruitment/<id>/` | Candidate details |
| | `/recruitment/create/` | Add new candidate |
| **Salary** | `/salary/` | Salary dashboard |
| | `/salary/generate/` | Generate payroll |
| | `/salary/report/` | Salary reports |
| **Calendar** | `/calendar/` | Workforce calendar |
| | `/calendar/event/create/` | Create event |
| | `/calendar/my-calendar/` | Personal calendar |

## 🎨 UI Features

### Responsive Design
- Mobile-friendly Bootstrap 5 interface
- Collapsible sidebar navigation
- Responsive tables and cards
- Modal dialogs for forms

### Visual Elements
- Color-coded status badges
- Font Awesome icons
- Chart.js visualizations
- Print-friendly layouts

### User Experience
- Search and filter functionality
- Pagination for large datasets
- Form validation
- Success/error messages
- Quick action buttons

## 🔒 Security Features

- CSRF protection on all forms
- Session-based authentication
- Password hashing
- Role-based access control
- SQL injection prevention (Django ORM)
- XSS protection

## 📝 Sample Data

The system includes a test script that creates:
- 4 Departments (IT, HR, Finance, Marketing)
- 4 Leave Types (Annual, Sick, Casual, Unpaid)

Run: `python test_system.py`

## 🚀 Deployment Considerations

### For Production:

1. **Database**: Switch to PostgreSQL
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           ...
       }
   }
   ```

2. **Static Files**: Configure for production
   ```bash
   python manage.py collectstatic
   ```

3. **Security Settings**:
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   SECRET_KEY = 'your-secure-secret-key'
   ```

4. **HTTPS**: Use SSL/TLS certificates

5. **Server**: Deploy with Gunicorn/uWSGI + Nginx

6. **Environment Variables**: Use python-decouple for sensitive data

## 📚 API Endpoints (DRF)

The system includes REST API support:
- Employee API endpoints
- Authentication via session/token
- CORS enabled for frontend integration

## 🐛 Troubleshooting

### Migration Issues
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### Database Reset (Development Only)
```bash
# Backup your data first!
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
python test_system.py
```

## 📧 Support & Contact

For issues or questions:
- Email: projectmad25@gmail.com
- Review the code comments in each module
- Check Django documentation: https://docs.djangoproject.com/

## 📄 License

This project is developed for educational and business purposes.

## 🎉 Credits

Built with Django, Bootstrap, and modern web technologies.

---

**Version**: 1.0.0  
**Last Updated**: October 19, 2025  
**Status**: ✅ Fully Operational
