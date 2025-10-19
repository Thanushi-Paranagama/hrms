# Create this file: employees/context_processors.py
# This makes employee profile available in all templates

def employee_profile(request):
    """Add employee profile to template context"""
    if request.user.is_authenticated and hasattr(request.user, 'employee_profile'):
        return {
            'employee_profile': request.user.employee_profile,
            'is_hr': request.user.employee_profile.role in ['HR', 'ADMIN'],
            'is_admin': request.user.employee_profile.role == 'ADMIN',
        }
    return {
        'employee_profile': None,
        'is_hr': False,
        'is_admin': False,
    }