
# ============================================
# attendance/models.py
# ============================================

from django.db import models
from django.utils import timezone
from datetime import datetime, time, timedelta

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HALF_DAY', 'Half Day'),
    ]
    
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABSENT')
    
    # Face Recognition Data
    face_verified = models.BooleanField(default=False)
    check_in_image = models.ImageField(upload_to='attendance_images/', null=True, blank=True)
    
    # Location (optional)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_hours_worked(self):
        """Calculate hours worked between check-in and check-out"""
        if not self.check_in:
            return None

        # Get current time in the correct timezone
        now = timezone.localtime()
        
        # Create datetime objects for today's date
        check_in_dt = timezone.make_aware(
            datetime.combine(self.date, self.check_in)
        )
        
        if self.check_out:
            check_out_dt = timezone.make_aware(
                datetime.combine(self.date, self.check_out)
            )
        else:
            # If no check-out, use current time for ongoing work duration
            if self.date == now.date():  # Only if it's today
                check_out_dt = now
            else:
                return None
            
        # Handle case where check-out is before check-in (overnight shift)
        if check_out_dt < check_in_dt:
            check_out_dt = timezone.make_aware(
                datetime.combine(self.date + timedelta(days=1), self.check_out)
            )
        
        duration = check_out_dt - check_in_dt
        return round(duration.total_seconds() / 3600, 2)  # Convert to hours and round to 2 decimals

    def update_status(self):
        """Update status based on check-in time and hours worked"""
        if not self.check_in:
            self.status = 'ABSENT'
            return

        # Standard work day settings (can be moved to settings.py)
        WORK_START_HOUR = 9  # 9:00 AM
        WORK_START_MIN = 0   # 9:00 AM
        LATE_THRESHOLD = 30  # 30 minutes grace period
        HALF_DAY_HOURS = 4.0 # Less than 4 hours is half day
        FULL_DAY_HOURS = 8.0 # Standard 8-hour workday

        # Get current time in the correct timezone
        now = timezone.localtime()
        
        # Create the standard start time for today
        standard_start = time(WORK_START_HOUR, 0)  # 9:00 AM
        late_start = (datetime.combine(self.date, standard_start) + 
                     timedelta(minutes=LATE_THRESHOLD)).time()

        # Get hours worked
        hours = self.get_hours_worked()

        # For today's records
        if self.date == now.date():
            # If it's before work hours, mark as present but hours will show as 0
            if now.time() < standard_start:
                self.status = 'PRESENT'
                return
        
        # Determine status based on hours and check-in time
        if hours is not None:
            if hours < HALF_DAY_HOURS:
                self.status = 'HALF_DAY'
            elif self.check_in > late_start:
                self.status = 'LATE'
            else:
                self.status = 'PRESENT'
        else:  # No check-out yet
            if self.check_in > late_start:
                self.status = 'LATE'
            else:
                self.status = 'PRESENT'

    def save(self, *args, **kwargs):
        """Override save to update status automatically"""
        self.update_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} - {self.status}"

    class Meta:
        ordering = ['-date', '-check_in']
        unique_together = ['employee', 'date']



