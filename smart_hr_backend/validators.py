# Create this file: smart_hr_backend/validators.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def validate_phone_number(value):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'  # ADD THE CLOSING QUOTE AND $
    if not re.match(pattern, value):
        raise ValidationError(
            _('%(value)s is not a valid phone number. Use format: +999999999'),
            params={'value': value},
        )


def validate_employee_id(value):
    """Validate employee ID format"""
    pattern = r'^EMP\d{4}$'  # ADD THE CLOSING QUOTE AND $
    if not re.match(pattern, value):
        raise ValidationError(
            _('%(value)s is not a valid employee ID. Use format: EMP0001'),
            params={'value': value},
        )


def validate_future_date(value):
    """Validate that date is not in the past"""
    from datetime import date
    if value < date.today():
        raise ValidationError(
            _('Date cannot be in the past'),
        )


def validate_date_range(start_date, end_date):
    """Validate that end date is after start date"""
    if end_date < start_date:
        raise ValidationError(
            _('End date must be after start date'),
        )