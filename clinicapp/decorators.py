from functools import wraps
from flask import request, redirect, url_for
from flask_login import current_user


def loggedin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index', next=request.url))

        return f(*args, **kwargs)

    return decorated_function