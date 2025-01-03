import uuid
from flask_smorest import Blueprint
from marshmallow import fields, Schema
import pymongo
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
    session.pop('_flashes', None)
    print(session)
    email_name = session.get('email', 'Guest')
    return render_template('admin_dashboard.html', title='Admin Dashboard', email_name=email_name)

# Add user route
# @login_required
# @role_required('admin-user')
@admin_bp.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """add user"""
    departments = list(mongo.db.departments.find())
    
    if request.method == 'POST':
        # Print all form data for debugging
        print("Form Data:", dict(request.form))
        print("Departments:", departments)
        
        # Gather form data
        firstname = request.form.get('firstname', '').strip()
        middlename = request.form.get('middlename', '').strip()
        lastname = request.form.get('lastname', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        ehr_number = request.form.get('ehr_number', '').strip()
        assigned_departments = request.form.getlist('assigned_departments')
        
        # Debug print specific fields
        print(f"Firstname: {firstname}")
        print(f"Lastname: {lastname}")
        print(f"Email: {email}")
        print(f"Username: {username}")
        print(f"EHR Number: {ehr_number}")
        print(f"Assigned Departments: {assigned_departments}")
        
        # More comprehensive validation
        if not all([firstname, lastname, email, username, ehr_number]):
            print("Validation failed: Missing required fields")
            flash('All required fields must be filled.', 'danger')
            return render_template('add_user.html', title='Add User', departments=departments)
        
        assigned_departments = assigned_departments if assigned_departments else []
        
        try:
            # Comprehensive existence checks
            if mongo.db.users.find_one({'email': email}):
                print(f"User with email {email} already exists")
                flash('User with this email already exists.', 'danger')
                return render_template('add_user.html', title='Add User', departments=departments)
            
            if mongo.db.users.find_one({'username': username}):
                print(f"User with username {username} already exists")
                flash('User with this username already exists.', 'danger')
                return render_template('add_user.html', title='Add User', departments=departments)
            
            if mongo.db.users.find_one({'ehr_number': ehr_number}):
                print(f"User with EHR number {ehr_number} already exists")
                flash('User with this EHR number already exists.', 'danger')
                return render_template('add_user.html', title='Add User', departments=departments)
            
            # Prepare user data
            new_user = {
                'firstname': firstname,
                'middlename': middlename,
                'lastname': lastname,
                'ippisno': request.form.get('ippisno'),
                'staff_id': request.form.get('staff_id'),
                'rank': request.form.get('rank'),
                'username': username,
                'phonenumber': request.form.get('phonenumber'),
                'email': email,
                'department': request.form.get('department'),
                'password': generate_password_hash(request.form.get('password')),
                'role': request.form.get('role'),
                'assigned_departments': assigned_departments,
                'ehr_number': ehr_number,
                'clinical_role': request.form.get('clinical_role')
            }
            
            # Insert user
            print("Attempting to insert user:", new_user)
            result = mongo.db.users.insert_one(new_user)
            
            if result.inserted_id:
                print(f"User successfully added with EHR Number: {ehr_number}")
                flash(f'User added successfully with EHR Number: {ehr_number}!', 'success')
                return redirect(url_for('admin.user_list'))
            else:
                print("Failed to insert user")
                flash('Failed to add user. Please try again.', 'danger')
                return render_template('add_user.html', title='Add User', departments=departments)
        
        except (pymongo.errors.DuplicateKeyError, pymongo.errors.OperationFailure) as e:
            print(f"Unexpected user addition error: {e}")
            flash('An unexpected error occurred.', 'danger')
            return render_template('add_user.html', title='Add User', departments=departments)
    
    return render_template('add_user.html', title='Add User', departments=departments)

# manage rooms
@admin_bp.route('/user_list')
# @login_required
# @role_required('admin-user')
def user_list():
    """this shows the list of users created"""
    show_flash_messages = request.args.get('show_flash_messages', True)
    if not show_flash_messages:
        session.pop('_flashes', None)
    all_users = mongo.db.users.find()
    return render_template('user_list.html', title='User List', users=all_users)

@admin_bp.route('/add_ehr_fee', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def add_ehr_fee():
    """function to add ehr fee"""
    service_code = str(uuid.uuid4().hex)[:8].upper() 
    session.pop('_flashes', None)
    departments = mongo.db.departments.find({}, {'_id': 0, 'department_name': 1})
    if request.method == 'POST':
        name = request.form.get('service_name')
        department = request.form.get('department_name')
        fee = request.form.get('service_fee')

        # Insert the new fee into the database
        mongo.db.ehr_fees.insert_one({
            'service_name': name,
            'department_name': department,
            'service_code': service_code,
            'service_fee': fee
        })
        
        return redirect(url_for('admin.manage_ehr_fees'))
    return render_template('add_ehr_fee.html', departments=departments, service_code=service_code)
@admin_bp.route('/mange_ehr_fees', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def manage_ehr_fees():
    """Display the EHR Fees table and handle adding new fees."""
    session.pop('_flashes', None)
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
# @role_required('admin-user'
def delete_ehr_fee(fee_id):
    """Delete an EHR Fee"""
    session.pop('_flashes', None)
    mongo.db.ehr_fees.delete_one({'_id': ObjectId(fee_id)})
    flash('EHR Fee deleted successfully!', 'success')
    return redirect(url_for('admin.manage_ehr_fees'))


@admin_bp.route('/edit_ehr_fee/<fee_id>', methods=['GET', 'POST'])
@login_required
@role_required('admin-user')
def edit_ehr_fee(fee_id):
    """Edit an existing EHR Fee"""
    session.pop('_flashes', None)
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
    session.pop('_flashes', None)
    departments = mongo.db.departments.find()
    return render_template('department_list.html', title='Department List', departments=departments)



@admin_bp.route('/add_department', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def add_department():
    """Add a new department"""
    session.pop('_flashes', None)
    if request.method == 'POST':
        department_name = request.form.get('department_name')
        department_id = request.form.get('department_id')
        department_typ = request.form.get('department_typ')
        department_abbreviation = request.form.get('department_abbreviation')
        
        # Remove the redundant existing department check
        if create_department(department_id, department_name, department_typ, department_abbreviation):
            flash('Department added successfully!', 'success')
            return redirect(url_for('admin.list_departments'))
        else:
            flash('Error adding department', 'danger')
    
    return render_template('add_department.html', title='Add Department')



@admin_bp.route('/edit_department/<department_id>', methods=['GET', 'POST'])
def edit_department(department_id):
    """Edit an existing department"""
    session.pop('_flashes', None)
    
    try:
        department = mongo.db.departments.find_one_or_404({'_id': ObjectId(department_id)})
    except InvalidId:
        flash('Invalid department ID', 'error')
        return redirect(url_for('admin.list_departments'))
    
    if request.method == 'POST':
        try:
            department_name = request.form.get('department_name')
            department_id_form = request.form.get('department_id')
            department_abbreviation = request.form.get('department_abbreviation')
            department_typ = request.form.get('department_typ')
            
            # Update in database
            result = mongo.db.departments.update_one(
                {'_id': ObjectId(department_id)},
                {'$set': {
                    'department_name': department_name,
                    'department_id': department_id_form,
                    'department_abbreviation': department_abbreviation,
                    'department_typ': department_typ
                }}
            )
            if result.modified_count:
                flash('Department updated successfully!', 'success')
                return redirect(url_for('admin.list_departments'))
            else:
                flash('No changes made to department', 'warning')
        
        except Exception as e:
            print(e)
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
    session.pop('_flashes', None)
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
        return redirect(url_for('admin.user_list'))
    
    return render_template('edit_user.html', user=user, departments=departments)

@admin_bp.route('/delete_user/<user_id>', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def delete_user(user_id):
    """Delete an EHR Fee"""
    session.pop('_flashes', None)
    mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    flash('EHR Fee deleted successfully!', 'success')
    return redirect(url_for('admin.user_list'))


@admin_bp.route('/manage_rooms', methods=['GET', 'POST'])
# @login_required
# @role_required('admin-user')
def manage_rooms():
    """managing rooms"""
    if request.method == 'POST':
        room_number = request.form.get('room_number')
        if room_number:
            room_number = room_number.strip()
        room_type = request.form.get('department')
        room_capacity = request.form.get('room_capacity')

        # Check if room already exists
        existing_room = mongo.db.rooms.find_one({
            'room_number': room_number,
            'room_department': room_type
        })
        if existing_room:
            flash('Room with this name already exists.', 'danger')
            return redirect(url_for('admin.manage_rooms'))

        new_room = {
            'room_number': room_number,
            'room_department': room_type,
            'room_capacity': int(room_capacity) if room_capacity else 0
        }
        mongo.db.rooms.insert_one(new_room)

        flash('Room added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))
    departments = mongo.db.departments.find({}, {'_id': 0, 'department_name': 1})
    return render_template('manage_rooms.html', title='Add Room', departments=departments)
@admin_bp.route('/delete_department/<department_id>')
def delete_department(department_id):
    """Delete a department"""
    session.pop('_flashes', None)
    
    try:
        # Find the department first to get its name
        department = mongo.db.departments.find_one({'_id': ObjectId(department_id)})
        
        if department:
            # Create queue name based on department name
            queue_name = f'{department["department_name"].lower().replace(" ", "_")}_nurses_queue'
            
            # Drop the nurses queue collection
            mongo.db.drop_collection(queue_name)
            
            # Delete the department
            mongo.db.departments.delete_one({'_id': ObjectId(department_id)})
            
            flash('Department deleted successfully!', 'success')
        else:
            flash('Department not found.', 'error')
    
    except Exception as e:
        print(f"Error deleting department: {e}")
        flash('Error deleting department.', 'error')
    
    return redirect(url_for('admin.list_departments'))