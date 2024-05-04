from functools import wraps
from flask import request, redirect, url_for, abort
from flask_login import current_user


def loggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index', next=request.url))

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
