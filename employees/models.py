
# ============================================
# employees/models.py
# ============================================

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Employee(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('HR', 'HR Team'),
        ('TECHNICIAN', 'Technician'),
        ('EMPLOYEE', 'Employee'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=17, blank=True)
    
    # Work Information
    floor_number = models.IntegerField(null=True, blank=True)
    cabin_number = models.CharField(max_length=20, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    salary_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Face Recognition
    face_encoding = models.TextField(blank=True, help_text="Stored face encoding for recognition")
    face_image = models.ImageField(upload_to='face_images/', null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"

    class Meta:
        ordering = ['-created_at']


