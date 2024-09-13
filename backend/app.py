import uuid
from bson import ObjectId
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/statics')

# MongoDB Configuration
app.config['MONGO_URI'] = "mongodb://localhost:27017/healthdis"
app.config['SECRET_KEY'] = 'dc21a9cb05847ffd9d5a37b67857042b'
mongo = PyMongo(app)

# Helper function for requiring login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function for requiring a specific role
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') != role:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Login route
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
            user = mongo.db.users.find_one({'email': email, 'role': role})

            if user and check_password_hash(user['password'], password):
                session['email'] = email
                session['role'] = role
                
                if role == 'medpay-user':
                    return redirect(url_for('medpay_dashboard'))
                elif role == 'clinical-services':
                    return redirect(url_for('clinical_dashboard'))
            else:
                flash('Invalid credentials or role.', 'danger')
    
    return render_template('login.html', title='Login')
# Add employee route
@app.route('/admin/add_employee', methods=['GET', 'POST'])
@login_required
@role_required('admin-user')
def add_employee():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        department = request.form.get('department')
        position = request.form.get('position')
        phone_number = request.form.get('phone_number')

        # Check if employee already exists
        existing_employee = mongo.db.employees.find_one({'email': email})
        if existing_employee:
            flash('Employee with this email already exists.', 'danger')
            return redirect(url_for('add_employee'))

        new_employee = {
            'name': name,
            'email': email,
            'department': department,
            'position': position,
            'phone_number': phone_number,
        }
        mongo.db.employees.insert_one(new_employee)

        flash('Employee added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_employee.html', title='Add Employee')

# Admin dashboard
@app.route('/admin/')
@app.route('/admin/dashboard')
@login_required
@role_required('admin-user')
def admin_dashboard():
    return render_template('admin_dashboard.html', title='Admin Dashboard')

@app.route('/admin/edit_user/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    """Route to edit a user."""
    # Logic to edit the user with the given user_id
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if request.method == 'POST':
        # Handle the form submission to edit the user
        pass
    return render_template('edit_user.html', user=user)
@app.route('/admin/edit_employee/<employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    """Route to edit a user."""
    # Logic to edit the user with the given user_id
    employee = mongo.db.employee.find_one({'_id': ObjectId(employee_id)})
    if request.method == 'POST':
        # Handle the form submission to edit the user
        pass
    return render_template('edit_user.html', employee=employee)


@app.route('/admin/delete_user/<user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    """Route to edit a user."""
    # Logic to edit the user with the given user_id
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    if request.method == 'POST':
        # Handle the form submission to edit the user
        pass
    return render_template('delete_user.html', user=user)
@app.route('/admin/delete_employee/<employee_id>', methods=['GET', 'POST'])
def delete_employee(employee_id):
    """Route to edit a user."""
    # Logic to edit the user with the given user_id
    employee = mongo.db.employees.find_one({'_id': ObjectId(employee_id)})
    if request.method == 'POST':
        # Handle the form submission to edit the user
        pass
    return render_template('edit_user.html', employee=employee)
# Clinical services dashboard
@app.route('/clinical/dashboard')
def clinical_dashboard():
    ward_name = session['ward']['name']
    return render_template('clinical_dashboard.html', ward_name=ward_name, title='Clinical Dashboard')

@app.route('/clinical/patient_list')
def patient_list():
    """this shows the list of patients created"""
    all_patients = mongo.db.patients.find()
    return render_template('patient_list.html', title='Patient List', patients=all_patients)

@app.route('/clinical/update_patient/<hospital_number>', methods=['GET', 'POST'])
def update_patient(hospital_number):
    patient = mongo.db.patients.find_one({'hospital_number': hospital_number})
    timenow = datetime.now()  # Get current date and time
    formatted_time = timenow.strftime('%Y-%m-%d %H:%M:%S %p')
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patient_list'))

    if request.method == 'POST':
        updated_patient = {
            'patient_first_name': request.form.get('patient_first_name'),
            'patient_middle_name': request.form.get('patient_middle_name'),
            'patient_surname_name': request.form.get('patient_surname_name'),
            'dob': request.form.get('dob'),
            'gender': request.form.get('gender'),
            'phone_number': request.form.get('phone_number'),
            'next_of_kin_phone_number': request.form.get('next_of_kin_phone_number'),
            'address': request.form.get('address'),
            'status': request.form.get('status'),
            'updated': str(formatted_time)  # Track when the record was updated
        }

        mongo.db.patients.update_one(
            {'hospital_number': hospital_number},
            {'$set': updated_patient}
        )

        flash('Patient information updated successfully!', 'success')
        return redirect(url_for('patient_list'))

    return render_template('update_patient.html', patient=patient)

@app.route('/clinical/search_patient', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        ehr_number = request.form.get('ehr_number')
        patient = mongo.db.patients.find_one({'ehr_number': ehr_number})
        
        if patient:
            return redirect(url_for('update_patient', hospital_number=patient['hospital_number']))
        else:
            flash('Patient not found.', 'danger')
    
    return render_template('search_patient.html')
@app.route('/clinical/new_patient', methods=['GET', 'POST'])
# @login_required
# @role_required('clinical-services')
def new_patient():
    timenow = datetime.now()  # Get current date and time
    formatted_time = timenow.strftime('%Y-%m-%d %H:%M:%S %p')
    print(formatted_time)
    if request.method == 'POST':
        # Get data from the form
        patient_first_name = request.form.get('patient_first_name')
        patient_middle_name = request.form.get('patient_middle_name')
        patient_surname_name = request.form.get('patient_surname_name')
        dob = request.form.get('age')
        gender = request.form.get('gender')
        phone_number = request.form.get('patient-pno')
        next_of_kin_phone_number = request.form.get('patient-nextofkinpno')
        address = request.form.get('address')

        # Fetch the last EHR number and increment it
        last_patient = mongo.db.patients.find_one(sort=[("ehr_number", -1)])

        if last_patient:
            last_ehr_number = int(last_patient['ehr_number'])
        else:
            # If no patients exist, start with EHR number 1
            last_ehr_number = 0

        # Increment the EHR number
        new_ehr_number = last_ehr_number + 1

        # Format the EHR number as a 6-digit number (e.g., 000001)
        formatted_ehr_number = f'{new_ehr_number:06d}'

        # Generate a unique hospital number (UUID)
        hospital_number = str(uuid.uuid4())

        # Check if the patient already exists
        existing_patient = mongo.db.patients.find_one({'ehr_number': formatted_ehr_number})

        if existing_patient:
            flash(f'Patient with EHR Number {formatted_ehr_number} already exists.', 'warning')
        else:
            # Save patient data to MongoDB
            new_patient = {
                'patient_first_name': patient_first_name,
                'patient_middle_name': patient_middle_name,
                'patient_surname_name': patient_surname_name,
                'dob': dob,
                'gender': gender,
                'phone_number': phone_number,
                'next_of_kin_phone_number': next_of_kin_phone_number,
                'address': address,
                'ehr_number': formatted_ehr_number,
                'created': str(formatted_time),  # Add timestamp
                'registered_by': 'None',    # Dummy data for registered_by
                'status': 'Active',         # New field for user status
                'hospital_number': hospital_number  # New field for unique UUID
            }
            mongo.db.patients.insert_one(new_patient)
            flash(f'Patient enrolled successfully with EHR Number: {formatted_ehr_number} and Hospital Number: {hospital_number}!', 'success')

        return redirect(url_for('clinical_dashboard'))

    return render_template('new_patient.html', title='New Patient Enrollment')
# MedPay dashboard
@app.route('/medpay/dashboard')
@login_required
@role_required('medpay-user')
def medpay_dashboard():
    return render_template('medpay_dashboard.html', title='MedPay Dashboard')

# Add user route
@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
@role_required('admin-user')
def add_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        department = request.form.get('department')
        ehr_number = request.form.get('ehr_number')

        # Check if user already exists
        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            flash('User with this email already exists.', 'danger')
            return redirect(url_for('add_user'))

        # Check if EHR number already exists
        existing_ehr = mongo.db.users.find_one({'ehr_number': ehr_number})
        if existing_ehr:
            flash('User with this EHR number already exists.', 'danger')
            return redirect(url_for('add_user'))

        hashed_password = generate_password_hash(password)

        new_user = {
            'email': email,
            'password': hashed_password,
            'role': role,
            'department': department,
            'ehr_number': ehr_number
        }
        mongo.db.users.insert_one(new_user)

        flash(f'User added successfully with EHR Number: {ehr_number}!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_user.html', title='Add User')
@app.route('/admin/user_list')
def user_list():
    """this shows the list of users created"""
    all_users = mongo.db.users.find()
    return render_template('user_list.html', title='User List', users=all_users)
@app.route('/admin/employee_list')
# @login_required
# @role_required('admin-user')
def employee_list():
    """This shows the list of employees."""
    all_employees = mongo.db.employees.find()
    return render_template('employee_list.html', title='Employee List', employees=all_employees)
@app.route('/admin/add_ehr_fee', methods=['GET', 'POST'])
def add_ehr_fee():
    if request.method == 'POST':
        name = request.form.get('name')
        department = request.form.get('department')
        unit = request.form.get('unit')
        cost = request.form.get('cost')

        # Insert the new fee into the database
        mongo.db.ehr_fees.insert_one({
            'name': name,
            'department': department,
            'unit': unit,
            'cost': cost
        })
        
        return redirect(url_for('manage_ehr_fees'))
    
    return render_template('add_ehr_fee.html')
@app.route('/admin/mange_ehr_fees', methods=['GET', 'POST'])
def manage_ehr_fees():
    """Display the EHR Fees table and handle adding new fees."""
    if request.method == 'POST':
        # Add a new fee
        name = request.form['name']
        department = request.form['department']
        unit = request.form['unit']
        cost = float(request.form['cost'])

        mongo.db.ehr_fees.insert_one({
            'name': name,
            'department': department,
            'unit': unit,
            'cost': cost
        })
        return redirect(url_for('ehr_fees'))

    # Retrieve all EHR fees
    fees = mongo.db.ehr_fees.find()
    return render_template('ehr_fees.html', title='EHR Fees', fees=fees)


@app.route('/admin/manage_ehr_fees/delete/<fee_id>', methods=['POST'])
def delete_ehr_fee(fee_id):
    """Delete an EHR fee."""
    mongo.db.ehr_fees.delete_one({'_id': ObjectId(fee_id)})
    return redirect(url_for('ehr_fees'))


@app.route('/admin/manage_ehr_fees/edit/<fee_id>', methods=['POST'])
def edit_ehr_fee(fee_id):
    """Update the cost of an EHR fee."""
    new_cost = float(request.form['cost'])
    mongo.db.ehr_fees.update_one(
        {'_id': ObjectId(fee_id)},
        {'$set': {'cost': new_cost}}
    )
    return redirect(url_for('ehr_fees'))

@app.route('/admin/list_departments')
def list_departments():
    """Display a list of departments"""
    departments = mongo.db.departments.find()
    return render_template('department_list.html', title='Department List', departments=departments)

@app.route('/admin/add_department', methods=['GET', 'POST'])
def add_department():
    """Add a new department"""
    if request.method == 'POST':
        name = request.form.get('name')
        type_ = request.form.get('type')
        bed_fee = float(request.form.get('bed_fee'))
        
        mongo.db.departments.insert_one({
            'name': name,
            'type': type_,
            'bed_fee': bed_fee
        })
        flash('Department added successfully!', 'success')
        return redirect(url_for('list_departments'))

    return render_template('add_department.html', title='Add Department')

@app.route('/admin/edit_department/<department_id>', methods=['GET', 'POST'])
def edit_department(department_id):
    """Edit an existing department"""
    department = mongo.db.departments.find_one_or_404({'_id': department_id})

    if request.method == 'POST':
        name = request.form.get('name')
        type_ = request.form.get('type')
        bed_fee = int(request.form.get('bed_fee'))
        
        mongo.db.departments.update_one(
            {'_id': department_id},
            {'$set': {'name': name, 'type': type_, 'bed_fee': bed_fee}}
        )
        flash('Department updated successfully!', 'success')
        return redirect(url_for('list_departments'))

    return render_template('edit_department.html', title='Edit Department', department=department)

@app.route('/admin/delete_department/<department_id>')
def delete_department(department_id):
    """Delete a department"""
    mongo.db.departments.delete_one({'_id': department_id})
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('list_departments'))

@app.route('/clinical/ward_login', methods=['GET', 'POST'])
def ward_login():
    departments = mongo.db.departments.find()
    if request.method == 'POST':
        selected_ward_id = request.form.get('ward')
        if selected_ward_id:
            selected_ward = mongo.db.departments.find_one({'_id': ObjectId(selected_ward_id)})
            if selected_ward:
                session['ward'] = {
                    'id': str(selected_ward['_id']),
                    'name': selected_ward['name']
                }
                print(f'Selected Ward: {session["ward"]}')
                return redirect(url_for('clinical_dashboard'))
    return render_template('ward_login.html', title='Ward Login', departments=departments)
@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)