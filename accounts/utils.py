from .models import Profile

def is_it_admin(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile.role == Profile.Role.IT_ADMIN
    except Exception:
        return False

def is_employee(user):
    if not user or not user.is_authenticated:
        return False
    if is_it_admin(user):
        return False
    try:
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile.role == Profile.Role.EMPLOYEE
    except Exception:
        # Fallback default role is Employee for standard authenticated users
        return True
