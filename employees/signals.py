# Create this file: employees/signals.py
# Django signals for automatic actions

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Employee
from datetime import date


@receiver(post_save, sender=Employee)
def employee_created(sender, instance, created, **kwargs):
    """Send welcome email when employee is created"""
    if created:
        # You can add automatic actions here
        # For example, send welcome SMS, create initial attendance record, etc.
        pass


@receiver(pre_save, sender=Employee)
def check_birthday(sender, instance, **kwargs):
    """Check if today is employee's birthday"""
    if instance.date_of_birth:
        today = date.today()
        if instance.date_of_birth.month == today.month and \
           instance.date_of_birth.day == today.day:
            # Birthday detected - can trigger email here or log it
            pass

