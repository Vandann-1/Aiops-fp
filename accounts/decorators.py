from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from functools import wraps
from .utils import is_it_admin, is_employee

def employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if is_employee(request.user):
            return view_func(request, *args, **kwargs)
        elif is_it_admin(request.user):
            return redirect('admin_dashboard')
        else:
            raise PermissionDenied
    return _wrapped_view

def it_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if is_it_admin(request.user):
            return view_func(request, *args, **kwargs)
        elif is_employee(request.user):
            return redirect('employee_dashboard')
        else:
            raise PermissionDenied
    return _wrapped_view
