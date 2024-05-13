from functools import wraps
from flask import request, redirect, url_for, abort
from flask_login import current_user

from clinicapp.models import UserRole


def loggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


def cashiernotloggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.CASHIER:
            return redirect(url_for('login_my_user', next=request.url))

        return f(*args, **kwargs)

    return decorated_function


def adminloggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.role == UserRole.ADMIN:
            return redirect('/admin')

        return f(*args, **kwargs)

    return decorated_function


def roles_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.role in roles:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def resources_owner(resource_user_id_param='user_id', allowed_roles=None):
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            resource_user_id = kwargs.get(resource_user_id_param)

            if allowed_roles and current_user.role not in allowed_roles:
                abort(403)

            if current_user.role == UserRole.PATIENT:
                if current_user.id != resource_user_id:
                    abort(403)

            return func(*args, **kwargs)

        return decorated

    return decorator
