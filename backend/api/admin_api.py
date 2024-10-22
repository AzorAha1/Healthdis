from flask_smorest import Blueprint
from marshmallow import fields, Schema
from backend.auth.decorator import login_required, role_required
from backend.helperfuncs.helperfuncs import create_department, update_department
from backend.extensions import mongo
from flask import flash, render_template, request, redirect, url_for, session
from bson import ObjectId
from werkzeug.security import generate_password_hash
from bson.errors import InvalidId

class AdminSchema(Schema):
    """admin schema"""


admin_bp = Blueprint('admin', 'admin', url_prefix='/admin')

# Admin dashboard
@admin_bp.route('/')
@admin_bp.route('/dashboard/')
# @login_required
# @role_required('admin-user')
def admin_dashboard():
    """admin dashboard"""
    print(session)
    email_name = session.get('email', 'Guest')
    return render_template('admin_dashboard.html', title='Admin Dashboard', email_name=email_name)

# Add user route
@admin_bp.route('/add_user', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def add_user():
    """add user"""
    departments = mongo.db.departments.find({}, {'_id': 0, 'department_name': 1})
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
        ehr_number = request.form.get('ehr_number')
        clinical_role = request.form.get('clinical_role', None)

        # Check if user already exists
        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            flash('User with this email already exists.', 'danger')
            return redirect(url_for('admin.add_user'))

        # Check if EHR number already exists
        existing_ehr = mongo.db.users.find_one({'ehr_number': ehr_number})
        if existing_ehr:
            flash('User with this EHR number already exists.', 'danger')
            return redirect(url_for('admin.add_user'))
        #check if username already exists
        existing_username = mongo.db.users.find_one({'username': username})
        if existing_username:
            flash('User with this username already exists.', 'danger')
            return redirect(url_for('admin.add_user'))

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
            'ehr_number': ehr_number,
            'clinical_role': clinical_role
        }
        mongo.db.users.insert_one(new_user)

        flash(f'User added successfully with EHR Number: {ehr_number}!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('add_user.html', title='Add User', departments=departments)

# manage rooms

@admin_bp.route('/user_list')
# @login_required 
# @role_required('admin-user')
def user_list():
    """this shows the list of users created"""
    all_users = mongo.db.users.find()
    return render_template('user_list.html', title='User List', users=all_users)
@admin_bp.route('/admin/employee_list')
@login_required
@role_required('admin-user')
def employee_list():
    """This shows the list of employees."""
    all_employees = mongo.db.employees.find()
    return render_template('employee_list.html', title='Employee List', employees=all_employees)
@admin_bp.route('/add_ehr_fee', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def add_ehr_fee():
    """function to add ehr fee"""
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
        
        return redirect(url_for('admin.manage_ehr_fees'))
    return render_template('add_ehr_fee.html', departments=departments)
@admin_bp.route('/mange_ehr_fees', methods=['GET', 'POST'])
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
        return redirect(url_for('admin.ehr_fees'))

    # Retrieve all EHR fees
    fees = mongo.db.ehr_fees.find()
    return render_template('ehr_fees.html', title='EHR Fees', fees=fees)


@admin_bp.route('/delete_ehr_fee/<fee_id>')
# @login_required
# @role_required('admin-user')
def delete_ehr_fee(fee_id):
    """Delete an EHR Fee"""
    mongo.db.ehr_fees.delete_one({'_id': ObjectId(fee_id)})
    flash('EHR Fee deleted successfully!', 'success')
    return redirect(url_for('admin.manage_ehr_fees'))


@admin_bp.route('/edit_ehr_fee/<fee_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin-user')
def edit_ehr_fee(fee_id):
    """Edit an existing EHR Fee"""
    try:
        fee = mongo.db.ehr_fees.find_one_or_404({'_id': ObjectId(fee_id)})
    except InvalidId:
        flash('Invalid EHR Fee ID', 'error')
        return redirect(url_for('admin.manage_ehr_fees'))

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
        return redirect(url_for('admin.manage_ehr_fees')) 
    return render_template('edit_ehr_fees.html', title='Edit EHR Fee', fee=fee, departments=departments)
@admin_bp.route('/list_departments')
# @login_required
# @role_required('admin-user')
def list_departments():
    """Display a list of departments"""
    departments = mongo.db.departments.find()
    return render_template('department_list.html', title='Department List', departments=departments)



@admin_bp.route('/add_department', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def add_department():
    """Add a new department"""
    if request.method == 'POST':
        department_name = request.form.get('department_name')
        department_id = request.form.get('department_id')
        department_typ = request.form.get('department_typ')
        department_abbreviation = request.form.get('department_abbreviation')
        if create_department(department_id, department_name, department_typ, department_abbreviation):
            flash('Department added successfully!', 'success')
            return redirect(url_for('list_departments'))
        else:
            flash('Error adding department', 'danger')
    
    return render_template('add_department.html', title='Add Department')



@admin_bp.route('/edit_department/<department_id>', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def edit_department(department_id):
    """Edit an existing department"""
    try:
        department = mongo.db.departments.find_one_or_404({'_id': ObjectId(department_id)})
    except InvalidId:
        flash('Invalid department ID', 'error')
        return redirect(url_for('list_departments'))
    
    if request.method == 'POST':
        department_name = request.form.get('department_name')
        department_abbreviation = request.form.get('department_abbreviation')
        department_typ = request.form.get('department_typ')
        
        if update_department(department_id, department_name, department_abbreviation, department_typ):
            flash('Department updated successfully!', 'success')
            return redirect(url_for('admin.list_departments'))
        else:
            flash('Error updating department', 'error')
    
    return render_template('edit_department.html', title='Edit Department', department=department)


@admin_bp.route('/refresh_request', methods=['POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def refresh_request():
    """refresh request for it clears session data"""
    # Clear the 'ward' session data
    session.pop('ward', None)
    session.pop('current_patient', None)
    session.pop('current_request', None)
    # Optionally, flash a message
    flash('Ward session has been cleared. Please select a new ward.', 'info')
    
    # Redirect to the ward login page
    return redirect(url_for('clinical.ward_login'))
@admin_bp.route('/request_dashboard', methods=['POST'])
def request_dashboard():
    """dashboard to make request"""
    return render_template('request_dashboard.html', title='Request Dashboard')
@admin_bp.route('/edit_user/<user_id>', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def edit_user(user_id):
    """edit user"""
    # Fetch user data from MongoDB
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    departments = mongo.db.departments.find({}, {'_id': 0, 'department_name': 1})
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
    
    return render_template('edit_user.html', user=user, departments=departments)

@admin_bp.route('/delete_user/<user_id>')
# @login_required
# @role_required('admin-user')
def delete_user(user_id):
    """Delete an EHR Fee"""
    mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    flash('EHR Fee deleted successfully!', 'success')
    return redirect(url_for('user_list'))
@admin_bp.route('/admin/add_employee', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def add_employee():
    """adding employee"""
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

@admin_bp.route('/manage_rooms', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def manage_rooms():
    """managing rooms"""
    if request.method == 'POST':
        room_number = request.form.get('room_number')
        if room_number:
            room_number.strip()
        room_department = request.form.get('department')
        room_capacity = request.form.get('room_capacity')

        # Check if room already exists
        existing_room = mongo.db.rooms.find_one({
            'room_number': room_number,
            'room_department': room_department
        })
        if existing_room:
            flash('Room with this name already exists.', 'danger')
            return redirect(url_for('admin.manage_rooms'))

        new_room = {
            'room_number': room_number,
            'room_type': room_department,
            'room_capacity': int(room_capacity) if room_capacity else 0
        }
        mongo.db.rooms.insert_one(new_room)

        flash('Room added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    departments = mongo.db.departments.find({}, {'_id': 0, 'department_name': 1})
    return render_template('manage_rooms.html', title='Add Room', departments=departments)
@admin_bp.route('/delete_department/<department_id>')
# @login_required
# @role_required('admin-user')
def delete_department(department_id):
    """Delete a department"""
    mongo.db.departments.delete_one({'_id': ObjectId(department_id)})
    flash('Department deleted successfully!', 'success')
    return redirect(url_for('list_departments'))
