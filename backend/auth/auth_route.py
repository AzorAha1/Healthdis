from backend.extensions import mongo 
from flask_smorest import Blueprint
from werkzeug.security import check_password_hash
from flask import flash, redirect, render_template, request, session, url_for

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        selected_role = request.form.get('role')
        user = mongo.db.users.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            # Check if user is admin or has matching role
            if user['role'] == 'admin-user' or user['role'] == selected_role:
                session['email'] = email
                session['role'] = user['role']
                # Handle redirects based on role and selection
                if user['role'] == 'admin-user':
                    if selected_role == 'clinical-services':
                        flash('Admin logged in as Clinical Services user successfully', 'success')
                        return redirect(url_for('clinical.clinical_dashboard'))
                    elif selected_role == 'medpay-user':
                        flash('Admin logged in as MedPay user successfully', 'success')
                        return redirect(url_for('medpay.medpay_dashboard'))
                    else:
                        flash('Admin logged in successfully', 'success')
                        return redirect(url_for('admin.admin_dashboard'))
                elif user['role'] == 'clinical-services':
                    flash('Logged in successfully as Clinical Services user', 'success')
                    return redirect(url_for('clinical.clinical_dashboard'))
                elif user['role'] == 'medpay-user':
                    flash('Logged in successfully as MedPay user', 'success')
                    return redirect(url_for('medpay.medpay_dashboard'))
            else:
                flash('Invalid role selected', 'danger')
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html', title='Login')


@auth_bp.route('/logout')
def logout():
    """logout endpoint"""
    session.clear()
    return redirect(url_for('auth.login'))
