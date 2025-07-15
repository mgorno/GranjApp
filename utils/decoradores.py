# decorators.py
from functools import wraps
from flask import session, redirect, url_for, flash

def login_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Tenés que iniciar sesión", "warning")
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper

def rol_requerido(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "rol" not in session or session["rol"] not in roles:
                flash("Acceso denegado", "danger")
                return redirect(url_for("auth.login"))
            return func(*args, **kwargs)
        return wrapper
    return decorator
