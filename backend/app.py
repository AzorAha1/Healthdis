from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from config import Config
from models import db, User, bcrypt
from functools import wraps

def create_app():
    app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/statics')
    app.config.from_object(Config)

    # Initialize SQLAlchemy and Bcrypt
    db.init_app(app)
    bcrypt.init_app(app)

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'email' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    def role_required(role):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if session.get('role') != role:
                    return redirect(url_for('login'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    @app.route('/', methods=['GET', 'POST'])
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            role = request.form.get('role')

            if role == 'admin-user':
                adminemail = request.form.get('adminemail')
                adminpassword = request.form.get('adminpassword')
                if adminemail == 'admin@email.com' and adminpassword == '123456':
                    session['email'] = adminemail
                    session['role'] = 'admin-user'
                    flash('Admin User logged in successfully', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash('Invalid admin credentials.', 'danger')
            else:
                email = request.form.get('email')
                password = request.form.get('password')
                user = User.query.filter_by(email=email, role=role).first()

                if user and user.check_password(password):
                    session['email'] = email
                    session['role'] = role
                    
                    if role == 'medpay-user':
                        return redirect(url_for('medpay_dashboard'))
                    elif role == 'clinical-services':
                        return redirect(url_for('clinical_dashboard'))
                else:
                    flash('Invalid credentials or role.', 'danger')
        
        return render_template('login.html', title='Login')

    @app.route('/admin/dashboard')
    @login_required
    @role_required('admin-user')
    def admin_dashboard():
        return render_template('admin_dashboard.html', title='Admin Dashboard')

    @app.route('/clinical/dashboard')
    # @login_required
    # @role_required('clinical-services')
    def clinical_dashboard():
        return render_template('clinical_dashboard.html', title='Clinical Dashboard')

    @app.route('/medpay/dashboard')
    @login_required
    @role_required('medpay-user')
    def medpay_dashboard():
        return render_template('medpay/medpay_dashboard.html', title='MedPay Dashboard')

    @app.route('/admin/add_user', methods=['GET', 'POST'])
    @login_required
    @role_required('admin-user')
    def add_user():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role')
            
            new_user = User(email=email, password=password, role=role)
            db.session.add(new_user)
            db.session.commit()

            flash('User added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

        return render_template('add_user.html', title='Add User')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)