from django.core.management.base import BaseCommand
from leave_management.models import LeaveRequest
from employees.models import Employee
from django.db.models import Count

class Command(BaseCommand):
    help = 'Dump leave request counts and samples'

    def handle(self, *args, **options):
        total = LeaveRequest.objects.count()
        self.stdout.write(f'total_leave_requests={total}')
        self.stdout.write('counts_by_status:')
        self.stdout.write(str(list(LeaveRequest.objects.values('status').annotate(c=Count('id')))))
        self.stdout.write('\nSamples:')
        for lr in LeaveRequest.objects.all()[:20]:
            emp = lr.employee
            uname = emp.user.username if emp and hasattr(emp, 'user') and emp.user else None
            self.stdout.write(f'{lr.id} {lr.status} emp_id={lr.employee_id} username={uname} {lr.start_date} -> {lr.end_date}')

        self.stdout.write('\nEmployees sample:')
        for e in Employee.objects.all()[:20]:
            uname = e.user.username if hasattr(e, 'user') and e.user else None
            self.stdout.write(f'{e.id} {e.employee_id} username={uname}')
