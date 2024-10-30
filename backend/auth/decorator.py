# Helper function for requiring login
from functools import wraps

from flask import flash, redirect, session, url_for


def login_required(f):
    """login required"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function for requiring a specific role
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' in session and session['role'] in allowed_roles:
                return f(*args, **kwargs)
            else:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('login'))
        return decorated_function
    return decorator

def admin_or_role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' in session and (session['role'] == 'admin-user' or session['role'] == required_role):
                return f(*args, **kwargs)
            else:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('auth.login'))
        return decorated_function
    return decorator

# function to only allow nurses
def nurse_check(f):
    """nurse check"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('clinical_role') != 'nurse' and session.get('role') != 'admin-user':
            flash('You are not a Nurse', 'danger')
            return redirect(url_for('clinical.clinical_dashboard'))
        else:
            return f(*args, **kwargs)
    return decorated_function

#function that only allow doctors
def doctor_check(f):
    """doctor check"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('clinical_role') != 'doctor' and session.get('role') != 'admin-user':
            flash('You are not a Doctor', 'danger')
            return redirect(url_for('clinical.clinical_dashboard'))
        return f(*args, **kwargs)
    return decorated_function