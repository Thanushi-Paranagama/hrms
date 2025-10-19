# Smart HR System - Quick Start Guide

## 🚀 Getting Started (5 Minutes)

### Step 1: Start the Server
```bash
python manage.py runserver
```
Server will start at: http://127.0.0.1:8000/

### Step 2: Access the System
Open your browser and navigate to:
- **Application**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

### Step 3: Login
Use your superuser credentials:
- Username: admin
- Password: [your password]

---

## 📋 First Time Setup Checklist

- [x] ✅ Migrations applied
- [x] ✅ Superuser created
- [x] ✅ Sample departments created (IT, HR, Finance, Marketing)
- [x] ✅ Sample leave types created (Annual, Sick, Casual, Unpaid)
- [x] ✅ Admin panel configured
- [x] ✅ All models registered
- [x] ✅ Templates created
- [x] ✅ Authentication system configured
- [x] ✅ Server running

---

## 🎯 Common Tasks

### Add a New Employee
1. Go to http://localhost:8000/admin/employees/employee/
2. Click "Add Employee"
3. First create a Django User, then link it to employee
4. Or use: http://localhost:8000/employees/create/

### Create a Department
1. Admin Panel → Employees → Departments → Add Department
2. Enter name and description
3. Save

### Add Leave Type
1. Admin Panel → Leave Management → Leave Types → Add Leave Type
2. Set name, max days, and payment status
3. Save

### Add a Candidate
1. Go to http://localhost:8000/recruitment/create/
2. Fill in candidate details
3. Upload resume (optional)
4. Submit

### Mark Attendance
1. Go to http://localhost:8000/attendance/mark/
2. Select employee
3. Choose status (Present/Absent/Late/Half-Day)
4. Submit

### Generate Salary
1. Go to http://localhost:8000/salary/generate/
2. Select month and year
3. System will calculate based on attendance
4. Review and confirm

---

## 📊 Dashboard Overview

The main dashboard (http://localhost:8000/dashboard/) shows:
- Total employees count
- Today's attendance statistics
- Pending leave requests
- Active recruitment candidates
- Quick action buttons
- Recent activities

---

## 🔐 User Roles

### Admin
- Full system access
- Can manage all modules
- Can approve leaves
- Can generate salary

### HR
- Employee management
- Leave approval
- Recruitment management
- Attendance overview

### Technician
- Limited access
- Can mark own attendance
- Can submit leave requests

### Employee
- View own profile
- Mark attendance
- Submit leave requests
- View personal calendar

---

## 📱 Module Access

| Module | URL | Quick Access |
|--------|-----|--------------|
| Dashboard | /dashboard/ | Main page after login |
| Employees | /employees/ | Sidebar → Employees |
| Attendance | /attendance/ | Sidebar → Attendance |
| Leave | /leave/ | Sidebar → Leave Requests |
| Recruitment | /recruitment/ | Sidebar → Recruitment |
| Salary | /salary/ | Sidebar → Salary |
| Calendar | /calendar/ | Sidebar → Calendar |
| Admin Panel | /admin/ | Top right → Admin Panel |

---

## 🎨 Key Features in Action

### Face Recognition Attendance
1. Upload employee face image in their profile
2. System will encode the face
3. Use face recognition for automatic attendance marking

### Automated Onboarding
- When a recruitment candidate is marked as "Hired"
- System can create employee profile automatically
- Sends welcome email (configure email backend)

### Attendance Reports
- Monthly summary reports
- Export to CSV
- Print-friendly format
- Charts and visualizations

### Leave Approval Workflow
1. Employee submits leave request
2. HR/Admin receives notification
3. Review and approve/reject
4. Employee gets notification

### Salary Calculation
- Automatically calculates based on:
  - Base salary
  - Days worked (from attendance)
  - Days absent
  - Bonuses
  - Deductions

---

## 🛠️ Quick Commands

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Test System
```bash
python test_system.py
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Create Database Backup
```bash
# Copy db.sqlite3 to backup location
copy db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
```

---

## 🐛 Troubleshooting

### Can't Login?
- Verify superuser exists: `python manage.py createsuperuser`
- Check credentials
- Clear browser cache

### Page Not Found?
- Ensure server is running: `python manage.py runserver`
- Check URL spelling
- Verify you're logged in

### Template Not Found?
- Check templates folder structure
- Verify app is in INSTALLED_APPS
- Restart server

### Database Locked?
- Close all connections
- Restart server
- Check file permissions

---

## 📞 Quick Help

### View All Employees
```
http://localhost:8000/admin/employees/employee/
```

### View All Attendance
```
http://localhost:8000/admin/attendance/attendance/
```

### View All Leave Requests
```
http://localhost:8000/admin/leave_management/leaverequest/
```

### View All Candidates
```
http://localhost:8000/admin/recruitment/recruitment/
```

---

## 💡 Tips & Best Practices

1. **Regular Backups**: Backup db.sqlite3 regularly
2. **User Creation**: Create Django User first, then Employee profile
3. **Department Setup**: Set up departments before adding employees
4. **Leave Types**: Configure leave types before employees request leaves
5. **Face Recognition**: Ensure good quality face images for accuracy
6. **Attendance**: Mark attendance daily for accurate salary calculation
7. **Reports**: Generate monthly reports for record keeping

---

## 🎯 Next Steps

1. ✅ System is now fully operational
2. 📝 Add your employees via Admin Panel
3. 👥 Create departments if needed
4. 📅 Start marking attendance
5. 💼 Begin using recruitment module
6. 💰 Generate monthly salary at month-end
7. 📆 Schedule events in calendar

---

## 📚 Additional Resources

- **Full Documentation**: See README.md
- **Django Docs**: https://docs.djangoproject.com/
- **Bootstrap Docs**: https://getbootstrap.com/docs/
- **Test Script**: Run `python test_system.py` for system status

---

## ✅ System Status: OPERATIONAL

**Server**: http://127.0.0.1:8000/  
**Admin**: http://127.0.0.1:8000/admin/  
**Database**: SQLite (db.sqlite3)  
**Status**: ✅ All systems operational

**Date**: October 19, 2025  
**Version**: 1.0.0

---

**Happy HR Management! 🎉**
