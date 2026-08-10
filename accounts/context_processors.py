from .utils import is_it_admin, is_employee

def role_context(request):
    if request.user.is_authenticated:
        return {
            'is_it_admin': is_it_admin(request.user),
            'is_employee': is_employee(request.user)
        }
    return {
        'is_it_admin': False,
        'is_employee': False
    }
