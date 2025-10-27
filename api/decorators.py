from functools import wraps
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, parser_classes

def api_view_with_file_upload(*args, **kwargs):
    """
    Combines api_view with csrf_exempt for file upload endpoints that use token auth.
    """
    def decorator(func):
        return csrf_exempt(api_view(*args, **kwargs)(func))
    return decorator