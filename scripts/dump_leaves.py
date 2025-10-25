import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','smart_hr_backend.settings')
django.setup()
from leave_management.models import LeaveRequest
from employees.models import Employee
from django.db.models import Count

print('Running leave dump')

total = LeaveRequest.objects.count()
print('total_leave_requests=', total)

print('counts_by_status:')
print(list(LeaveRequest.objects.values('status').annotate(c=Count('id'))))

samples = LeaveRequest.objects.all()[:20]
for lr in samples:
    emp = lr.employee
    username = emp.user.username if emp and hasattr(emp, 'user') and emp.user else None
    print(lr.id, lr.status, lr.employee_id, username, lr.start_date, lr.end_date)

print('\nEmployees sample:')
for e in Employee.objects.all()[:20]:
    uname = e.user.username if hasattr(e, 'user') and e.user else None
    print(e.id, e.employee_id, uname)
