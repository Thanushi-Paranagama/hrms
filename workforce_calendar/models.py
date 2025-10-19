# ============================================
# workforce_calendar/models.py
# ============================================

from django.db import models

class WorkforceEvent(models.Model):
    EVENT_TYPE_CHOICES = [
        ('MEETING', 'Meeting'),
        ('DEADLINE', 'Deadline'),
        ('EVENT', 'Event'),
        ('HOLIDAY', 'Holiday'),
        ('TRAINING', 'Training'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    
    # Participants
    employees = models.ManyToManyField('employees.Employee', blank=True, related_name='calendar_events')
    
    location = models.CharField(max_length=200, blank=True)
    
    created_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, related_name='created_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.start_date.date()}"

    class Meta:
        ordering = ['start_date']