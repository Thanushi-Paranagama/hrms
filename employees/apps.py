from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employees'
    
# Import signals in employees/apps.py
# Add this to employees/apps.py:

"""
from django.apps import AppConfig

class EmployeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employees'
    
    def ready(self):
        import employees.signals  # noqa
"""