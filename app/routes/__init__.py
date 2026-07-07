from functools import wraps
from flask import session, redirect, url_for, current_app


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def inject_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import g
        g.user = None
        if "user_id" in session:
            g.user = current_app.auth_service.get_current_user(session["user_id"])
        return f(*args, **kwargs)
    return decorated_function
