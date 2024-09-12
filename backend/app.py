from datetime import timedelta, datetime
from functools import wraps
from unittest import result
import bcrypt
from bson import ObjectId
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import DESCENDING, PyMongo
import uuid


app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/statics')
app.secret_key = '2b63a7cd1e7f5941daf586eefe63ba257c7d1c5739db4d072c0e76ed4ba97bc'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/healthdis'
app.permanent_session_lifetime = timedelta(hours=1)
mongo = PyMongo(app)

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
                print('admin logged in')
                flash('Admin User logged in successfully', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                print('admin login wrong')
                flash('Invalid admin credentials.', 'danger')

        elif role == 'medpay-user':
            medpayemail = request.form.get('medpayemail')
            medpaypassword = request.form.get('medpaypassword')
            if medpayemail == 'medpay@email.com' and medpaypassword == '12345':
                session['email'] = medpayemail
                session['role'] = 'medpay-user'
                print('medpay user logged in')
                return redirect(url_for('medpay_dashboard'))
            else:
                print('medpay login wrong')
                flash('Invalid medpay credentials.', 'danger')

        elif role == 'clinical-services':
            clinicalemail = request.form.get('clinicalemail')
            clinicalpassword = request.form.get('clinicalpassword')
            if clinicalemail == 'clinical@email.com' and clinicalpassword == '123456':
                session['email'] = clinicalemail
                session['role'] = 'clinical-services'
                print('clinical services user logged in')
                return redirect(url_for('clinical_dashboard'))
            else:
                print('clinical login wrong')
                flash('Invalid clinical services credentials.', 'danger')

        else:
            flash('Invalid role.', 'danger')
        
        return redirect(url_for('login'))

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
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_collection = mongo.db.user

        user_collection.insert_one({
            'email': email,
            'password': hashed_password,
            'role': role
        })

        flash('User added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_user.html', title='Add User')


@app.route('/logout')
def logout():
    session.pop('email', None)  # Clear session data
    return redirect(url_for('login'))

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)