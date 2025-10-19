
# ============================================
# recruitment/models.py
# ============================================

from django.db import models

class Recruitment(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('SCREENING', 'Screening'),
        ('INTERVIEW', 'Interview'),
        ('OFFERED', 'Offered'),
        ('HIRED', 'Hired'),
        ('REJECTED', 'Rejected'),
    ]
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=17)
    position_applied = models.CharField(max_length=100)
    department = models.ForeignKey('employees.Department', on_delete=models.SET_NULL, null=True)
    
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    cover_letter = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    interview_date = models.DateTimeField(null=True, blank=True)
    
    # If hired
    employee = models.OneToOneField('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='recruitment_record')
    hired_date = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.position_applied}"

    class Meta:
        ordering = ['-created_at']
