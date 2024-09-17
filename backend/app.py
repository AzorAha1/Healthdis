import uuid
import json
from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/statics')

# MongoDB Configuration
app.config['MONGO_URI'] = "mongodb://localhost:27017/healthdis"
app.config['SECRET_KEY'] = 'dc21a9cb05847ffd9d5a37b67857042b'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
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

# generate ehr number
def generate_ehr_number():
    last_patient = mongo.db.patients.find_one(sort=[("ehr_number", -1)])
    if last_patient:
        last_ehr_number = int(last_patient['ehr_number'])
    else:
        last_ehr_number = 0
    new_ehr_number = last_ehr_number + 1
    return f'{new_ehr_number:07d}'
# calculate age
def calculate_age(dob):
    today = datetime.today()
    birth_date = datetime.strptime(dob, '%Y-%m-%d')
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# get registeration fee
def get_registration_fee(dob):
    age = calculate_age(dob)
    if age <= 14:
        #filtering with case sensitivity
        # ehr_fee_info =  mongo.db.ehr_fees.find_one({"service_name": "NEW CHILD GOPD REGISTRATION"})
        # filtering without case sensitivity
        ehr_fee_info = mongo.db.ehr_fees.find_one({"service_name": {"$regex": "^NEW CHILD GOPD REGISTRATION$", "$options": "i"}})
    else:
        # filtering with case sensitivity
        # ehr_fee_info = mongo.db.ehr_fees.find_one({"service_name": "NEW ADULT GOPD REGISTRATION"})
        # filtering without case sensitivity
        ehr_fee_info = mongo.db.ehr_fees.find_one({"service_name": {"$regex": "^NEW ADULT GOPD REGISTRATION$", "$options": "i"}})
    return f"{ehr_fee_info['service_name']} - {ehr_fee_info['service_fee']} - {ehr_fee_info['service_code']}"

# helping function for requiring admin or a specific role
def admin_or_role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' in session and (session['role'] == 'admin-user' or session['role'] == required_role):
                return f(*args, **kwargs)
            else:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('login'))
        return decorated_function
    return decorator
# Login route

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        selected_role = request.form.get('role')

        user = mongo.db.users.find_one({'email': email})
        if user:
            if check_password_hash(user['password'], password):
                # Check if user role matches or if the user is an admin
                if user['role'] == 'admin-user' or user['role'] == selected_role:
                    session['email'] = email
                    session['role'] = user['role']

                    # Redirect based on the selected role
                    if user['role'] == 'admin-user':
                        if selected_role == 'clinical-services':
                            flash('Admin logged in as Clinical Services user successfully', 'success')
                            return redirect(url_for('clinical_dashboard'))
                        elif selected_role == 'medpay-user':
                            flash('Admin logged in as MedPay user successfully', 'success')
                            return redirect(url_for('medpay_dashboard'))
                        else:
                            flash('Admin logged in successfully', 'success')
                            return redirect(url_for('admin_dashboard'))
                    elif selected_role == 'clinical-services':
                        flash('Clinical Services user logged in successfully', 'success')
                        return redirect(url_for('clinical_dashboard'))
                    elif selected_role == 'medpay-user':
                        flash('MedPay user logged in successfully', 'success')
                        return redirect(url_for('medpay_dashboard'))
                else:
                    flash('Invalid role', 'danger')
            else:
                flash('Invalid password', 'danger')
        else:
            flash('User not found', 'danger')
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
# # @login_required
# @role_required('admin-user')
def admin_dashboard():
    print(session)
    email_name = session.get('email', 'Guest')
    return render_template('admin_dashboard.html', title='Admin Dashboard', email_name=email_name)



@app.route('/admin/edit_user/<user_id>', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def edit_user(user_id):
    # Fetch user data from MongoDB
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    
    if request.method == 'POST':
        # Get updated values from the form
        firstname = request.form.get('firstname')
        middlename = request.form.get('middlename')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        phonenumber = request.form.get('phonenumber')
        ippisno = request.form.get('ippisno')
        department = request.form.get('department')
        rank = request.form.get('rank')
        username = request.form.get('username')
        role = request.form.get('role')  # New role field
        
        # Update user data in the database
        mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'firstname': firstname,
                'middlename': middlename,
                'lastname': lastname,
                'email': email,
                'phonenumber': phonenumber,
                'ippisno': ippisno,
                'department': department,
                'rank': rank,
                'username': username,
                'role': role
            }}
        )
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('user_list'))
    
    return render_template('edit_user.html', user=user)

@app.route('/admin/edit_employee/<employee_id>', methods=['GET', 'POST'])
# @role_required('admin-user')
# @login_required
def edit_employee(employee_id):
    """Route to edit a user."""
    # Logic to edit the user with the given user_id
    employee = mongo.db.employee.find_one({'_id': ObjectId(employee_id)})
    if request.method == 'POST':
        # Handle the form submission to edit the user
        pass
    return render_template('edit_user.html', employee=employee)


@app.route('/admin/delete_user/<user_id>', methods=['POST'])
# @login_required
# @role_required('admin-user')
def delete_user(user_id):
    mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    flash('User deleted successfully!', 'danger')
    return redirect(url_for('user_list'))
@app.route('/admin/delete_employee/<employee_id>', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def delete_employee(employee_id):
    """Route to edit a user."""
    # Logic to edit the user with the given user_id
    employee = mongo.db.employees.find_one({'_id': ObjectId(employee_id)})
    if request.method == 'POST':
        # Handle the form submission to edit the user
        pass
    return render_template('edit_user.html', employee=employee)
# Clinical services dashboard

@app.route('/clinical/')
@app.route('/clinical/dashboard')
@login_required
@role_required('clinical-services', 'admin-user')
def clinical_dashboard():
    print("Dashboard Session:", session)
    current_patient = session.get('current_patient', {})
    ward_name = session.get('ward', {}).get('name', 'Not Assigned')
    
    if ward_name != 'Not Assigned':
        services_cursor = mongo.db.ehr_fees.find({'department_name': ward_name})
        services_list = list(services_cursor)
        for service in services_list:
            service['_id'] = str(service['_id'])
    else:
        services_list = []
    
    print(services_list)
    email_name = session.get('email', 'Guest')
    
    return render_template('clinical_dashboard.html', 
                           title='Clinical Dashboard', 
                           email_name=email_name,
                           current_patient=current_patient, 
                           ward_name=ward_name, 
                           services=services_list)
@app.route('/clinical/patient_list')
@login_required
@admin_or_role_required('clinical-services')
def patient_list():
    """this shows the list of patients created"""
    all_patients = mongo.db.patients.find()
    print(session)
    return render_template('patient_list.html', title='Patient List', patients=all_patients)

@app.route('/clinical/update_patient/<hospital_number>', methods=['GET', 'POST'])
@login_required
@admin_or_role_required('clinical-services')
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
@login_required
@admin_or_role_required('clinical-services')
def search_patient():
    if request.method == 'POST':
        ehr_number = request.form.get('ehr_number')
        patient = mongo.db.patients.find_one({'ehr_number': ehr_number})
        
        if patient:
            return redirect(url_for('update_patient', hospital_number=patient['hospital_number']))
        else:
            flash('Patient not found.', 'danger')
    
    return render_template('search_patient.html')

@app.route('/clinical/new_request', methods=['GET', 'POST'])
@login_required
@admin_or_role_required('clinical-services')
def new_request():
    """Route to create a new request."""
    if request.method == 'POST':
       ehr_number = request.form.get('ehr_number')
       patient = mongo.db.patients.find_one({'ehr_number': ehr_number})
       if patient:
           session['current_patient'] = {'patient_name': f"{patient['patient_first_name']} {patient['patient_middle_name']} {patient['patient_surname_name']}",
                                            'ehr_number': patient['ehr_number'],
                                            'hospital_number': patient['hospital_number']}
           
           return redirect(url_for('clinical_dashboard'))
       else:
           flash('Patient not found.', 'danger')
    return render_template('new_request.html')

@app.route('/admin/refresh_request', methods=['POST'])
@login_required
@admin_or_role_required('clinical-services')
def refresh_request():
    # Clear the 'ward' session data
    session.pop('ward', None)
    session.pop('current_patient', None)
    session.pop('current_request', None)
    # Optionally, flash a message
    flash('Ward session has been cleared. Please select a new ward.', 'info')
    
    # Redirect to the ward login page
    return redirect(url_for('ward_login'))
@app.route('/admin/request_dashboard', methods=['POST'])
def request_dashboard():
    """dashboard to make request"""
    return render_template('request_dashboard.html', title='Request Dashboard')

@app.route('/clinical/new_patient', methods=['GET', 'POST'])
@login_required
@admin_or_role_required('clinical-services')
def new_patient():
    timenow = datetime.now()
    formatted_time = timenow.strftime('%Y-%m-%d %H:%M:%S %p')
    
    # Generate enrollment code (which will also be the temp_ehr_number)
    enrollment_code = str(uuid.uuid4().hex)[:8].upper()  # 8-character uppercase code
    
    if request.method == 'POST':
        # Get data from the form
        patient_type = request.form.get('patient_type')
        patient_first_name = request.form.get('patient_first_name')
        patient_middle_name = request.form.get('patient_middle_name')
        patient_surname_name = request.form.get('patient_surname_name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        tribe = request.form.get('tribe')
        marital_status = request.form.get('marital_status')
        occupation = request.form.get('occupation')
        phone_number = request.form.get('phone_number')
        address = request.form.get('address')
        place_of_origin = request.form.get('place_of_origin')
        city = request.form.get('city')
        state = request.form.get('state')
        country = request.form.get('country')
        next_of_kin = request.form.get('next_of_kin')
        next_of_kin_relation = request.form.get('next_of_kin_relation')
        next_of_kin_phone_number = request.form.get('next_of_kin_phone_number')
        next_of_kin_address = request.form.get('next_of_kin_address')

        # Generate a unique hospital number (UUID)
        hospital_number = str(uuid.uuid4())

        registration_fee_info = get_registration_fee(dob)
        service_name, service_fee, service_code = registration_fee_info.split(' - ')
        # Check if the patient already exists
        existing_patient = mongo.db.patients.find_one({'hospital_number': hospital_number})
        if existing_patient:
            flash(f'Patient with Hospital Number {hospital_number} already exists.', 'warning')
        else:
            # Save patient data to MongoDB
            new_patient = {
                'enrollment_code': enrollment_code,
                'temp_ehr_number': enrollment_code,
                'patient_type': patient_type,
                'patient_first_name': patient_first_name,
                'patient_middle_name': patient_middle_name,
                'patient_surname_name': patient_surname_name,
                'dob': dob,
                'gender': gender,
                'tribe': tribe,
                'marital_status': marital_status,
                'occupation': occupation,
                'phone_number': phone_number,
                'address': address,
                'place_of_origin': place_of_origin,
                'city': city,
                'state': state,
                'country': country,
                'next_of_kin': next_of_kin,
                'next_of_kin_relation': next_of_kin_relation,
                'next_of_kin_phone_number': next_of_kin_phone_number,
                'next_of_kin_address': next_of_kin_address,
                'created': str(formatted_time),
                'registered_by': session.get('email', 'Unknown'),
                'status': 'Active',
                'hospital_number': hospital_number
            }
            mongo.db.patients.insert_one(new_patient)
            requests = {
                'patient_Number': f'{patient_first_name} {patient_middle_name} {patient_surname_name} - {enrollment_code}',
                'Department': 'HIMS',
                'Service_Code': service_code,
                'Service_Name': service_name,
                'Cost': service_fee,
                'Status': 'Pending',
                'ehr_number': enrollment_code,
                'Invoice Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            mongo.db.requests.insert_one(requests)
            flash(f'Patient enrolled successfully with Enrollment Code: {enrollment_code} and Hospital Number: {hospital_number}!', 'success')

        return redirect(url_for('clinical_dashboard'))

    return render_template('new_patient.html', title='New Patient Enrollment', enrollment_code=enrollment_code)

@app.route('/medpay/make_payment', methods=['GET', 'POST'])
def make_payment():
    if request.method == 'POST':
        pass
        
    return render_template('make_payment.html', title='Make Payment')
# MedPay dashboard
@app.route('/medpay/')
@app.route('/medpay/dashboard')
@login_required
@admin_or_role_required('medpay-user')
def medpay_dashboard():
    print(session)
    return render_template('medpay_dashboard.html', title='MedPay Dashboard')
@app.route('/medpay/pos_terminal/', methods=['GET', 'POST'])
@login_required
@admin_or_role_required('medpay-user')
def pos_terminal():
    if request.method == 'POST':
        search_term = request.form.get('ehr_number')  # This can be EHR number or enrollment code
        if search_term: 
            # Search for requests matching the search term
            requests = mongo.db.requests.find({
                '$or': [
                    {'ehr_number': search_term},
                    {'Service_Code': search_term},  # Assuming Service_Code is used for enrollment_code
                ]
            })
    else:
        requests = mongo.db.requests.find() 
    return render_template('pos_terminal.html', requests=requests, title='POS Terminal')

@login_required
@admin_or_role_required('clinical-services')
@app.route('/clinical/follow_up', methods=['GET', 'POST'])  
def follow_up():
    return render_template('follow_up.html', title='Follow-Up Visit')
# Add user route
@app.route('/admin/add_user', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def add_user():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        middlename = request.form.get('middlename')
        lastname = request.form.get('lastname')
        ippisno = request.form.get('ippisno')
        staff_id = request.form.get('staff_id')
        rank = request.form.get('rank')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        department = request.form.get('department')
        phonenumber = request.form.get('phonenumber')

        # Check if user already exists
        # existing_user = mongo.db.users.find_one({'email': email})
        # if existing_user:
        #     flash('User with this email already exists.', 'danger')
        #     return redirect(url_for('add_user'))

        # Check if EHR number already exists
        # existing_ehr = mongo.db.users.find_one({'ehr_number': ehr_number})
        # if existing_ehr:
        #     flash('User with this EHR number already exists.', 'danger')
        #     return redirect(url_for('add_user'))

        hashed_password = generate_password_hash(password)

        new_user = {
            'firstname': firstname,
            'middlename': middlename,
            'lastname': lastname,
            'ippisno': ippisno,
            'staff_id': staff_id,
            'rank': rank,
            'username': username,
            'phonenumber': phonenumber,
            'email': email,
            'password': hashed_password,
            'role': role,
            'department': department,
        }
        # mongo.db.users.insert_one(new_user)

        # flash(f'User added successfully with EHR Number: {ehr_number}!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_user.html', title='Add User')
@app.route('/admin/user_list')
# @login_required 
# @role_required('admin-user')
def user_list():
    """this shows the list of users created"""
    all_users = mongo.db.users.find()
    return render_template('user_list.html', title='User List', users=all_users)
@app.route('/admin/employee_list')
@login_required
@role_required('admin-user')
def employee_list():
    """This shows the list of employees."""
    all_employees = mongo.db.employees.find()
    return render_template('employee_list.html', title='Employee List', employees=all_employees)
@app.route('/admin/add_ehr_fee', methods=['GET', 'POST'])
@login_required
@role_required('admin-user')
def add_ehr_fee():
    departments = mongo.db.departments.find({}, {'_id': 0, 'department_name': 1})
    if request.method == 'POST':
        name = request.form.get('service_name')
        department = request.form.get('department_name')
        code = request.form.get('service_code')
        fee = request.form.get('service_fee')

        # Insert the new fee into the database
        mongo.db.ehr_fees.insert_one({
            'service_name': name,
            'department_name': department,
            'service_code': code,
            'service_fee': fee
        })
        
        return redirect(url_for('manage_ehr_fees'))
    return render_template('add_ehr_fee.html', departments=departments)
@app.route('/admin/mange_ehr_fees', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
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
    return render_template('ehr_fees.html', title='EHR Fees', kfees=fees
     )


@app.route('/admin/delete_ehr_fee/<fee_id>')
@login_required
@role_required('admin-user')
def delete_ehr_fee(fee_id):
    """Delete an EHR Fee"""
    mongo.db.ehr_fees.delete_one({'_id': ObjectId(fee_id)})
    flash('EHR Fee deleted successfully!', 'success')
    return redirect(url_for('manage_ehr_fees'))


@app.route('/admin/edit_ehr_fee/<fee_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin-user')
def edit_ehr_fee(fee_id):
    """Edit an existing EHR Fee"""
    try:
        fee = mongo.db.ehr_fees.find_one_or_404({'_id': ObjectId(fee_id)})
    except InvalidId:
        flash('Invalid EHR Fee ID', 'error')
        return redirect(url_for('manage_ehr_fees'))

    departments = mongo.db.departments.find({}, {'_id': 0, 'department_name': 1})
    
    if request.method == 'POST':
        department_name = request.form.get('department_name')
        service_name = request.form.get('service_name')
        service_code = request.form.get('service_code')
        service_fee = request.form.get('service_fee')

        mongo.db.ehr_fees.update_one(
            {'_id': ObjectId(fee_id)},
            {'$set': {
                'department_name': department_name,
                'service_name': service_name,
                'service_code': service_code,
                'service_fee': service_fee
            }}
        )
        flash('EHR Fee updated successfully!', 'success')
        return redirect(url_for('manage_ehr_fees'))
    
    return render_template('edit_ehr_fees.html', title='Edit EHR Fee', fee=fee, departments=departments)

@app.route('/admin/list_departments')
@login_required
@role_required('admin-user')
def list_departments():
    """Display a list of departments"""
    departments = mongo.db.departments.find()
    return render_template('department_list.html', title='Department List', departments=departments)

@app.route('/admin/add_department', methods=['GET', 'POST'])
@login_required
@role_required('admin-user')
@role_required('admin-user')
def add_department():
    """Add a new department"""
    if request.method == 'POST':
        department_name = request.form.get('department_name')
        department_id = request.form.get('department_id')
        department_typ = request.form.get('department_typ')
        department_abbreviation = request.form.get('department_abbreviation')
        
        # Insert the new department into the database
        mongo.db.departments.insert_one({
            'department_name': department_name,
            'department_id': department_id,
            'department_typ': department_typ,
            'department_abbreviation': department_abbreviation
        })
        
        flash('Department added successfully!', 'success')
        return redirect(url_for('list_departments'))

    return render_template('add_department.html', title='Add Department')
@app.route('/admin/edit_department/<department_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin-user')
def edit_department(department_id):
    """Edit an existing department"""
    try:
        department = mongo.db.departments.find_one_or_404({'_id': ObjectId(department_id)})
    except InvalidId:
        flash('Invalid department ID', 'error')
        return redirect(url_for('list_departments'))

    if request.method == 'POST':
        department_name = request.form.get('department_name')
        new_department_id = request.form.get('department_id')
        department_abbreviation = request.form.get('department_abbreviation')
        department_typ = request.form.get('department_typ')
        
        mongo.db.departments.update_one(
            {'_id': ObjectId(department_id)},
            {'$set': {
                'department_name': department_name,
                'department_id': new_department_id,
                'department_abbreviation': department_abbreviation,
                'department_typ': department_typ
            }}
        )
        flash('Department updated successfully!', 'success')
        return redirect(url_for('list_departments'))
    
    return render_template('edit_department.html', title='Edit Department', department=department)

@app.route('/admin/delete_department/<department_id>')
@login_required
@role_required('admin-user')
def delete_department(department_id):
    """Delete a department"""
    mongo.db.departments.delete_one({'_id': ObjectId(department_id)})
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('list_departments'))

@app.route('/clinical/ward_login', methods=['GET', 'POST'])
@login_required
@admin_or_role_required('clinical-services')
def ward_login():
    # Fetch departments with department_typ 'ward'
    wards = mongo.db.departments.find({'department_typ': 'ward'})
    #find departments with department_type 'ward' but not case sensitive
    # wards = mongo.db.departments.find({'department_typ': {'$regex': '^ward$', '$options': 'i'}})
    print(session)
    if request.method == 'POST':
        selected_ward_id = request.form.get('ward')
        if selected_ward_id:
            selected_ward = mongo.db.departments.find_one({'_id': ObjectId(selected_ward_id)})
            if selected_ward:
                session['ward'] = {
                    'id': str(selected_ward['_id']),
                    'name': selected_ward['department_name']
                }
                return redirect(url_for('clinical_dashboard'))
    
    return render_template('ward_login.html', title='Ward Login', wards=wards)

@app.route('/clinical/dashboard/make_request', methods=['GET', 'POST'])
@login_required
@admin_or_role_required('clinical-services')
def in_patient_request():
    """This makes request for in-patient"""
    if request.method == 'POST':
        # Get the selected service data from the form
        selected_service = request.form.get('selected_service')
        print("Raw selected_service:", selected_service)
        
        if selected_service:
            try:
                # Parse the selected service (assumes it's in JSON format)
                service = json.loads(selected_service)
                print("Parsed service:", service)
                
                current_patient = session.get('current_patient', {})
                # Create the request information to store in the session
                current_request = {
                    'service_name': service['service_name'],
                    'service_code': service['service_code'],
                    'service_fee': service['service_fee'],
                    'department_name': service['department_name']
                }
                requests = {
                    'patient_Number': f"{current_patient.get('patient_name', 'Unknown')} - {current_patient.get('ehr_number', 'Unknown')}",
                    'Department': service['department_name'],
                    'Service_Code': service['service_code'],
                    'Service_Name': service['service_name'],
                    'Cost': service['service_fee'],
                    'Status': 'Pending',
                    'ehr_number': current_patient.get('ehr_number', 'Unknown'),
                    'Invoice Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'Requested_by': session.get('email', 'Unknown'),
                    'Ward': session.get('ward', {}).get('name', 'Not Assigned')
                }
                mongo.db.requests.insert_one(requests)
                # Save the request information in the session
                session['current_request'] = current_request
                
                # Flash a success message
                flash(f'Request created successfully for {current_patient.get('patient_name', 'Unknown')}', 'success')
                
                # Render a page that shows the request details
                return redirect(url_for('clinical_dashboard'))
            
            # Handle potential JSON decoding errors
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")  # Debug print for error tracking
                flash('Error processing service information', 'error')
        else:
            flash('No service selected', 'error')
    
    # Redirect to the dashboard if no POST request or in case of errors
    return 'Error'
@app.route('/logout')
def logout():
    # session.pop('email', None)
    # session.pop('role', None)
    # session.pop('ward', None)
    session.clear() 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)