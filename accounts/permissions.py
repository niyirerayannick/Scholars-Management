from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


ADMIN = "Admin"
PROGRAM_MANAGER = "Program Manager"
DATA_OFFICER = "Data Officer"
VIEWER = "Viewer"


def user_role(user):
    if user.is_superuser:
        return ADMIN
    return getattr(getattr(user, "profile", None), "role", VIEWER)


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            role = user_role(request.user)
            if role == ADMIN or role in roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to perform that action.")
            raise PermissionDenied

        return wrapped

    return decorator


def can_edit_scholars(user):
    return user_role(user) in {ADMIN, PROGRAM_MANAGER, DATA_OFFICER}
