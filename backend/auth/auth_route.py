from flask import flash, redirect, render_template, request, session, url_for
from backend.extensions import mongo 
from flask_smorest import Blueprint
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/', methods=['GET', 'POST'])
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        selected_role = request.form.get('role')

        user = mongo.db.users.find_one({'email': email})
        if user:
            if check_password_hash(user['password'], password):
                # Validate if the user role matches the selected role
                if user['role'] == selected_role or user['role'] == 'admin-user':
                    session['email'] = email
                    session['role'] = user['role']
                    
                    # Redirect based on the role
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
                else:
                    flash('Invalid role selected', 'danger')
            else:
                flash('Invalid password', 'danger')
        else:
            flash('User not found', 'danger')
    
    return render_template('login.html', title='Login')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))