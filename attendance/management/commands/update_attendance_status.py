from django.core.management.base import BaseCommand
from attendance.models import Attendance
from datetime import datetime, time

class Command(BaseCommand):
    help = 'Recalculate and update attendance statuses'

    def handle(self, *args, **options):
        attendances = Attendance.objects.all()
        updated = 0

        for attendance in attendances:
            old_status = attendance.status
            attendance.update_status()
            if old_status != attendance.status:
                attendance.save()
                hours = attendance.get_hours_worked()
                hours_str = f"{hours:.2f}" if hours is not None else "N/A"
                self.stdout.write(
                    f"Updated {attendance.employee.employee_id} on {attendance.date}:\n"
                    f"Check-in: {attendance.check_in}, Check-out: {attendance.check_out}\n"
                    f"Hours: {hours_str}\n"
                    f"Old status: {old_status}, New status: {attendance.status}\n"
                )
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f'Updated {updated} attendance records'
        ))