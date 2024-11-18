from datetime import datetime, timedelta
from http.client import InvalidURL
import json
import uuid
import bson
from flask import current_app, request, jsonify
from flask_smorest import Blueprint
from bson import ObjectId
from marshmallow import fields, Schema
import pymongo
import pymongo.errors
from backend.auth.decorator import login_required, admin_or_role_required, nurse_check
from backend.extensions import mongo
from backend.helperfuncs.helperfuncs import get_registration_fee
from flask import flash, render_template, redirect, url_for, session


class ClinicalSchema(Schema):
    pass

clinical_bp = Blueprint('clinical', 'clinical', url_prefix='/clinical')

#setup database index
# Add these indexes to your database setup or initialization code
def setup_database_indexes():
    """Setup necessary database indexes"""
    # Patient records indexes
    mongo.db.patient_records.create_index([
        ('ehr_number', 1),
        ('consultation_date', -1)
    ])
    mongo.db.patient_records.create_index([
        ('type', 1),
        ('ehr_number', 1)
    ])
    
    # Nurses vitals indexes
    mongo.db.nurses_vitals.create_index([
        ('ehr_number', 1),
        ('registration_date', -1)
    ])
    
    # Patient index
    mongo.db.patients.create_index('ehr_number')
@clinical_bp.route('/', methods=['GET'])
@clinical_bp.route('/dashboard/', methods=['GET'])
@login_required
@admin_or_role_required('clinical-services')
def clinical_dashboard():
    """clinical dashboard endpoint"""
    # session.pop('_flashes', None)
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



@clinical_bp.route('/doctor_signin', methods=['GET', 'POST'])
@login_required
def doctor_signin():
    departments = list(mongo.db.departments.find())
    rooms = []
    selected_department = None
    # Get current user's email from session
    current_user_email = session.get('email')
    
    if request.method == 'POST':
        selected_department = request.form.get('department')
        selected_room = request.form.get('room')
        # Store department and room in session with email-specific key
        session[f'doctor_{current_user_email}_department'] = request.form.get('department')
        session[f'doctor_{current_user_email}_room'] = request.form.get('room')
        try:
            rooms = list(mongo.db.rooms.find({'room_department': selected_department}))

            print(f'Successfully selected {selected_department} and room {selected_room}')
            return redirect(url_for('clinical.doctor_dashboard'))
        except pymongo.errors.PyMongoError as e:
            print(f"Error fetching rooms: {e}")
            rooms = []
            
    return render_template('doctor_signin.html', 
                         title='Doctor Sign-In',
                         departments=departments,
                         rooms=rooms,
                         selected_department=selected_department)

@clinical_bp.route('/get_rooms/<department>')
def get_rooms(department):
    try:
        rooms = list(mongo.db.rooms.find({'room_department': department}))
        # Convert ObjectId to string for JSON serialization
        for room in rooms:
            room['_id'] = str(room['_id'])
        return jsonify(rooms)
    except Exception as e:
        print(f"Error fetching rooms: {e}")
        return jsonify([])

@clinical_bp.route('/doctors_dashboard')
# @role_required('doctors')
# @login_required
def doctor_dashboard():

    """this is the doctors dashboard"""
    print(session)
    current_user_email = session.get('email')
    current_department = session.get(f'doctor_{current_user_email}_department')
    current_room = session.get(f'doctor_{current_user_email}_room')



    if not current_user_email:
        return redirect(url_for('auth.login'))
    
    # Add debug logging
    print(f"Current Department: {current_department}")
    print(f"Current Room: {current_room}")
    
    # Query all waiting patients for the current department and room
    query = {
        'department': current_department,
        'room_number': current_room,
        'status': 'Waiting'
    }
    
    # Debug: Print the query
    print("Query:", query)
    
    waiting_patients = list(mongo.db.doctors_queue.find(query).sort('created_at', 1))
    # save ehr in session
    if waiting_patients:
        session['current_patient_ehr'] = waiting_patients[0]['ehr_number']
    # Debug: Print the number of patients found
    print(f"Found {len(waiting_patients)} waiting patients")
    
    return render_template(
        'doctor_dashboard.html',
        title='Doctors Dashboard',
        waiting_patients=waiting_patients,
        current_department=current_department,
        current_room=current_room
    )

#consultation route
@clinical_bp.route('/consultation/<string:consultation_id>', methods=['GET', 'POST'])
# @login_required
# @role_required('doctors')
def consultation(consultation_id):
    """consultation"""
    waiting_patient = mongo.db.doctors_queue.find_one({
        '_id': ObjectId(consultation_id),
        'status': 'Waiting',
    })
    

    thepatient = mongo.db.patients.find_one({'ehr_number': waiting_patient['ehr_number']})
    age = None
    if thepatient and 'dob' in thepatient:
        thepatientage = thepatient['dob']
        
        # Calculate age
        dob = datetime.strptime(thepatientage, '%Y-%m-%d')  # Convert string to datetime
        today = datetime.today()  # Get today's date
        
        # Calculate age
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    if not waiting_patient:
        flash('Patient not found', 'error')
        return redirect(url_for('clinical.doctor_dashboard'))
    return render_template('consultation.html', 
                         thepatient=thepatient, 
                         age=age,
                         consultation_id=consultation_id)

@clinical_bp.route('/save-consultation/<string:consultation_id>', methods=['POST'])
@login_required
def save_consultation(consultation_id):
    """Save consultation data with department and room info."""
    try:
        waiting_patient = mongo.db.doctors_queue.find_one({
            '_id': ObjectId(consultation_id)
        })

        if not waiting_patient:
            flash('Patient not found', 'error')
            return redirect(url_for('clinical.doctor_dashboard'))

        current_user_email = session.get('email')
        department = session.get(f'doctor_{current_user_email}_department')
        room = session.get(f'doctor_{current_user_email}_room')

        consultation_data = {}
        if request.method == 'POST':
            consultation_data = {
                'ehr_number': waiting_patient['ehr_number'],
                'doctor_email': current_user_email,
                'department': department,
                'room': room,
                'consultation_date': datetime.utcnow(),
                'type': 'consultation',
                'chief_complaint': request.form.get('chief_complaint'),
                'present_illness': request.form.get('present_illness'),
                'symptoms_duration': request.form.get('symptoms_duration'),
                'severity': request.form.get('severity'),
                'general_appearance': request.form.get('general_appearance'),
                'systematic_examination': request.form.get('systematic_examination'),
                'local_examination': request.form.get('local_examination'),
                'diagnosis': request.form.get('diagnosis'),
                'differential_diagnosis': request.form.get('differential_diagnosis'),
                'treatment_plan': request.form.get('treatment_plan'),
                'prescriptions': request.form.get('prescriptions'),
                'follow_up_period': request.form.get('follow_up_period'),
                'special_instructions': request.form.get('special_instructions'),
                'lab_tests': request.form.get('lab_tests'),
                'imaging_studies': request.form.get('imaging_studies')
            }

            # Save consultation record
            mongo.db.patient_records.insert_one(consultation_data)

            # Update patient queue status
            mongo.db.doctors_queue.update_one(
                {'_id': ObjectId(consultation_id)},
                {'$set': {'status': 'Completed'}}
            )

            flash('Consultation saved successfully', 'success')
            return redirect(url_for('clinical.doctor_dashboard'))
        
    except pymongo.errors.InvalidURI as e:
        # Log the error for debugging purposes
        current_app.logger.error(f"An error occurred while saving consultation: {e}")
        flash('An error occurred while saving the consultation. Please try again.', 'error')
        return redirect(url_for('clinical.doctor_dashboard'))

@clinical_bp.route('/patient-history/<string:ehr_number>')
@login_required


def patient_history(ehr_number):
    """
    View patient history including vitals and consultations.
    Returns a timeline of patient records sorted by date.
    """
    # Check if patient exists
    patient = mongo.db.patients.find_one({'ehr_number': ehr_number})
    if not patient:
        flash('Patient not found', 'error')
        return redirect(url_for('clinical.doctor_dashboard'))
    
    # Get all records - both current and historical
    current_consultations = list(mongo.db.patient_records.find({'ehr_number': ehr_number, 'type': 'consultation'}))
    current_vitals = list(mongo.db.patient_records.find({'ehr_number': ehr_number, 'type': 'vitals'}))

    historical_vitals = list(mongo.db.nurses_vitals.find({'ehr_number': ehr_number}))

    # Sort records by date
    all_records = current_consultations + current_vitals + historical_vitals
    all_records.sort(key=lambda x: x['registration_date'], reverse=True)
    return render_template('patient_history.html', 
                         title='Patient History', 
                         patient=patient, 
                         all_records=all_records)
    
    

    

@clinical_bp.route('/nurses_desk/', methods=['GET', 'POST'])
@login_required
@nurse_check
def nurses_desk():
    """Nurses desk view for managing department access"""
    # session.pop('_flashes', None)
    
    # Get current user info from session email
    current_user = mongo.db.users.find_one({'email': session.get('email')})
    
    if not current_user:
        session.clear()
        flash('Session expired. Please login again.', 'warning')
        return redirect(url_for('auth.login'))

    try:
        # Get departments based on user role and assignments
        if current_user.get('role') == 'admin-user':
            departments = list(mongo.db.departments.find())
        else:
            assigned_departments = current_user.get('assigned_departments', [])
            if not assigned_departments:
                flash('You have no assigned departments.', 'warning')
                departments = []
            else:
                departments = list(mongo.db.departments.find({
                    'department_name': {'$in': assigned_departments}
                }))

        if request.method == 'POST':
            department_id = request.form.get('nurse_department')
            
            if not department_id:
                flash('Please select a department.', 'danger')
                return redirect(url_for('clinical.nurses_desk'))

            try:
                department = mongo.db.departments.find_one({'_id': ObjectId(department_id)})
                
                if not department:
                    flash('Department not found.', 'danger')
                    return redirect(url_for('clinical.nurses_desk'))
                
                department_name = department['department_name']
                
                # Check if non-admin user has access to this department
                if (current_user.get('role') != 'admin-user' and 
                    department_name not in current_user.get('assigned_departments', []) and
                    current_user.get('clinical_role' != 'nurse')
                    ):
                    flash('You do not have access to this department.', 'danger')
                    return redirect(url_for('clinical.nurses_desk'))
                # Store department name in session
                session['department_name'] = department_name
                return redirect(url_for('clinical.nurses_desk_queue', department_name=department_name))
            except InvalidURL:
                flash('Invalid department ID.', 'danger')
                return redirect(url_for('clinical.nurses_desk'))   
        return render_template('nurses_desk.html',
                             title='Nurses Desk',
                             departments=departments,
                             current_user=current_user,
                             )                        
    except (pymongo.errors.PyMongoError, ValueError, KeyError):
        flash('An unexpected error occurred. Please try again.', 'danger')
        return redirect(url_for('clinical.nurses_desk'))

@clinical_bp.route('/take_vitals/', methods=['GET', 'POST'])
@login_required
@admin_or_role_required('clinical-services')
def take_vitals():
    """Take vitals for a patient"""
    session.pop('_flashes', None)
    ehr_number = session.get('current_patient_ehr')
    department_name = session.get('department_name')  # Make sure this is set
    
    if not ehr_number:
        flash('No patient selected', 'error')
        return redirect(url_for('clinical.nurses_desk_queue', department_name=department_name))

    patient = mongo.db.patients.find_one({'ehr_number': ehr_number})
    if not patient:
        flash('Patient not found', 'error')
        return redirect(url_for('clinical.nurses_desk_queue', department_name=department_name))

    department_rooms = list(mongo.db.rooms.find({'room_department': department_name}))

    if request.method == 'POST':
        vitals_data = {
            'ehr_number': ehr_number,
            'temperature': request.form.get('temperature'),
            'pulse_rate': request.form.get('pulse_rate'),\
            'type': 'vitals',
            'respiratory_rate': request.form.get('respiratory_rate'),
            'blood_pressure_systolic': request.form.get('blood_pressure_systolic'),
            'blood_pressure_diastolic': request.form.get('blood_pressure_diastolic'),
            'weight': request.form.get('weight'),
            'height': request.form.get('height'),
            'muac': request.form.get('muac'),
            'registration_date': datetime.now(),
            'additional_notes': request.form.get('additional_notes'),
            'room_number': request.form.get('room_number'),
            'department': department_name,
            'nurse': session.get('email', 'Unknown')
        }
        
        collection_name = department_name.lower().replace(' ', '_') + '_nurses_queue'
        if request.form.get('action') == 'send_to_doctor':
            # Update the patient's status in the queue
            mongo.db[collection_name].update_one(
                {'ehr_number': ehr_number}, 
                {
                    '$set': {
                        'status': 'Processed',
                        'processed_at': datetime.now(),
                        'processed_by': session.get('email'),
                        'vitals_taken': True
                    }
                }
            )
            
            # Store vitals first
            mongo.db.nurses_vitals.insert_one(vitals_data)
            mongo.db.patient_records.insert_one(vitals_data)
            
            # Redirect to send_to_doctor with department parameter
            return redirect(url_for('clinical.send_to_doctor', department_name=department_name))
        
        mongo.db.nurses_vitals.insert_one(vitals_data)
        flash('Vitals recorded successfully', 'success')
        session.pop('current_patient_ehr', None)
        return redirect(url_for('clinical.nurses_desk_queue', department_name=department_name))

    return render_template('take_vitals.html', 
                         title='Take Vitals', 
                         patient=patient, 
                         department_rooms=department_rooms,
                         department_name=department_name)
@clinical_bp.route('/set_current_patient', methods=['POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def set_current_patient():
    session.pop('_flashes', None)
    ehr_number = request.form.get('ehr_number')
    action = request.form.get('action')
    session['current_patient_ehr'] = ehr_number 
    
    if action == 'view_record':
        return redirect(url_for('clinical.view_patient_record'))
    elif action == 'take_vitals':
        return redirect(url_for('clinical.take_vitals'))
    else:
        flash('Invalid action', 'error')
        return redirect(url_for('clinical.nurses_desk_queue'))

@clinical_bp.route('/hims_dashboard')
# @login_required
# @admin_or_role_required('clinical-services')
def hims_dashboard():
    """HIMS dashboard with date filtering"""
    session.pop('_flashes', None)
    # Get the date filter from the query parameters, default to today
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
    except ValueError:
        flash('Invalid date format. Showing today\'s records.', 'warning')
        filter_date = datetime.now()
    
    # Set the date range for the filter (entire day)
    start_of_day = filter_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # Query for records within the date range
    date_query = {
        'registration_date': {
            '$gte': start_of_day,
            '$lt': end_of_day
        }
    }
    
    pending_queue = list(mongo.db.hims_queue.find({**date_query, 'status': 'Pending'}))
    processed_queue = list(mongo.db.hims_queue.find({**date_query, 'status': {'$ne': 'Pending'}}))
    
    return render_template('hims_dashboard.html', 
                        title='HIMS Dashboard', 
                        pending_queue=pending_queue, 
                        processed_queue=processed_queue,
                        current_date=filter_date.strftime('%m-%d-%Y'))

@clinical_bp.route('/send_to_nurse/<ehr_number>', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def send_to_nurse(ehr_number):
    """send to nurse function"""
    session.pop('_flashes', None)
    patient = mongo.db.hims_queue.find_one({'ehr_number': ehr_number})
    clinics = mongo.db.departments.find({'department_typ': 'clinic'})
    if not patient:
        flash('Patient not found in the HIMS queue', 'danger')
        return redirect(url_for('hims_dashboard'))
    if request.method == 'POST':
        selected_clinic_id = request.form.get('clinic')
        if selected_clinic_id:
            # Update patient's status or move them to the selected clinic
            try:
                selected_clinic_id = ObjectId(selected_clinic_id)
            except bson.errors.InvalidId:
                flash('Invalid clinic ID', 'warning')
                return redirect(url_for('clinical.send_to_nurse', ehr_number=ehr_number))
            selected_clinic = mongo.db.departments.find_one({'_id': selected_clinic_id})
            if selected_clinic:
                mongo.db.hims_queue.update_one(
                    {'ehr_number': ehr_number},
                    {'$set': {
                        'status': 'In Clinic',
                        'clinic': selected_clinic['department_name']
                    }}
                )
                mongo.db[selected_clinic['department_name'].lower().replace(' ', '_') + '_nurses_queue'].insert_one({
                    'ehr_number': ehr_number,
                    'patient_name': patient['patient_name'],
                    'registration_date': datetime.now(),
                    'department_name': selected_clinic['department_name'],
                    'status': 'Pending'
                })
                flash(f'Patient sent to {selected_clinic["department_name"]} successfully!', 'success')
                return redirect(url_for('clinical.hims_dashboard'))
        else:
            flash('Please select a clinic', 'warning')
            return redirect(url_for('clinical.send_to_nurse', ehr_number=ehr_number))
    
    return render_template('send_to_nurse.html', title='Send to Nurse', patient=patient, clinics=clinics)

@clinical_bp.route('/nurses_desk_queue/<department_name>', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def nurses_desk_queue(department_name):
    """Display the queue for a specific department"""
    session.pop('_flashes', None)
    # Get the date filter from the query parameters, default to today
    # date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    date_filter = request.form.get('date') or request.args.get('date') or datetime.now().strftime('%Y-%m-%d')
    

    # Get the EHR number from the query parameters
    ehr_number = request.args.get('ehr_number')

    try:
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
    except ValueError:
        flash('Invalid date format. Showing today\'s records.', 'warning')
        filter_date = datetime.now()

    # Set the date range from the filter (entire day)
    start_of_day = filter_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    # Create the base date query
    date_query = {
        'registration_date': {
            '$gte': start_of_day,
            '$lt': end_of_day
        }
    }

    # If EHR number is provided, add it to the date query
    if ehr_number:
        date_query['ehr_number'] = ehr_number

    collection_name = department_name.lower().replace(' ', '_') + '_nurses_queue'

    # Debug: Print collection name and queries
    print(f"Collection name: {collection_name}")
    print(f"Date query: {date_query}")

    pending_query = {**date_query, 'status': 'Pending'}
    processed_query = {**date_query, 'status': {'$ne': 'Pending'}}

    print(f"Pending query: {pending_query}")
    print(f"Processed query: {processed_query}")

    pending_queue = list(mongo.db[collection_name].find(pending_query))
    processed_queue = list(mongo.db[collection_name].find(processed_query))

    # Debug: Print queue lengths
    print(f"Pending queue length: {len(pending_queue)}")
    print(f"Processed queue length: {len(processed_queue)}")

    return render_template('nurses_desk_queue.html',
                           title='Nurses Desk Queue',
                           department_name=department_name,
                           pending_queue=pending_queue,
                           processed_queue=processed_queue,
                           current_date=filter_date.strftime('%m-%d-%Y'))
@clinical_bp.route('/patient_list')
# @login_required
# @admin_or_role_required('clinical-services')
def patient_list():
    """this shows the list of patients created"""
    all_patients = mongo.db.patients.find()
    print(session)
    return render_template('patient_list.html', title='Patient List', patients=all_patients)

@clinical_bp.route('/update_patient/<hospital_number>', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def update_patient(hospital_number):
    session.pop('_flashes', None)
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
        return redirect(url_for('clinical.patient_list'))

    return render_template('update_patient.html', patient=patient)

@clinical_bp.route('/search_patient', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def search_patient():
    session.pop('_flashes', None)
    if request.method == 'POST':
        ehr_number = request.form.get('ehr_number')
        patient = mongo.db.patients.find_one({'ehr_number': ehr_number})
        
        if patient:
            return redirect(url_for('clinical.update_patient', hospital_number=patient['hospital_number']))
        else:
            flash('Patient not found.', 'danger')
    
    return render_template('search_patient.html')

@clinical_bp.route('/new_request', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
@clinical_bp.route('/new_request', methods=['GET', 'POST'])
def new_request():
    """Route to create a new request."""
    session.pop('_flashes', None)
    if request.method == 'POST':
        ehr_number = request.form.get('ehr_number')
        patient = mongo.db.patients.find_one({'ehr_number': ehr_number})
        
        if patient:
            # Store patient info in session and redirect to the dashboard
            session['current_patient'] = {
                'patient_name': f"{patient['patient_first_name']} {patient['patient_middle_name']} {patient['patient_surname_name']}",
                'ehr_number': patient['ehr_number'],
                'hospital_number': patient['hospital_number']
            }
            return redirect(url_for('clinical.clinical_dashboard'))
        else:
            # Flash error message and stay on the new_request page
            print("Patient not found")
            flash('Patient not found. Try Again 🙂', 'danger')
            return redirect(url_for('clinical.new_request'))  # Stay on the same page
    
    return render_template('new_request.html')
@clinical_bp.route('/new_patient', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def new_patient():
    session.pop('_flashes', None)
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
        religion = request.form.get('religion')
        next_of_kin = request.form.get('next_of_kin')
        next_of_kin_relation = request.form.get('next_of_kin_relation')
        next_of_kin_phone_number = request.form.get('next_of_kin_phone_number')
        next_of_kin_address = request.form.get('next_of_kin_address')

        # Generate a unique hospital number (UUID)
        hospital_number = str(uuid.uuid4())

        registration_fee_info = get_registration_fee(dob)
        if registration_fee_info == None:
            flash('registration fee not found', 'danger')
            return redirect(url_for('clinical.new_patient'))
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
                'patient_first_name': patient_first_name.strip(),
                'patient_middle_name': patient_middle_name.strip(),
                'patient_surname_name': patient_surname_name.strip(),
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
                'religion': religion,
                'hospital_number': hospital_number
            }
            mongo.db.patients.insert_one(new_patient)
            requests = {
                'patient_hospital_number': hospital_number,
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

        return redirect(url_for('clinical.clinical_dashboard'))

    return render_template('new_patient.html', title='New Patient Enrollment', enrollment_code=enrollment_code)

# @login_required
# @admin_or_role_required('clinical-services')
@clinical_bp.route('/follow_up', methods=['GET', 'POST'])  
def follow_up():
    session.pop('_flashes', None)
    return render_template('follow_up.html', title='Follow-Up Visit')

@clinical_bp.route('/ward_login', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def ward_login():
    # Fetch departments with department_typ 'ward'
    session.pop('_flashes', None)
    wards = mongo.db.departments.find({'department_typ': 'ward'})
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
                return redirect(url_for('clinical.clinical_dashboard'))
    
    return render_template('ward_login.html', title='Ward Login', wards=wards)

@clinical_bp.route('/dashboard/make_request', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def in_patient_request():
    """This makes request for in-patient"""
    session.pop('_flashes', None)
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
                flash('Request created successfully', 'success')
                
                # Render a page that shows the request details
                return render_template('request_details.html', request_details=current_request)
            
            # Handle potential JSON decoding errors
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")  # Debug print for error tracking
                flash('Error processing service information', 'error')
        else:
            flash('No service selected', 'error')
    
    # Redirect to the dashboard if no POST request or in case of errors
    return redirect(url_for('clinical.clinical_dashboard'))

# send to doctor
@clinical_bp.route('/send_to_doctor/', methods=['GET', 'POST'])
@login_required
@admin_or_role_required('clinical-services')
def send_to_doctor():
    """Send patient to doctor's queue"""
    ehr_number = session.get('current_patient_ehr')
    department_name = request.args.get('department_name') or session.get('department_name')
    
    if not department_name:
        flash('Department not specified', 'error')
        return redirect(url_for('clinical.hims_dashboard'))
    
    if not ehr_number:
        flash('No patient selected', 'error')
        return redirect(url_for('clinical.nurses_desk_queue', department_name=department_name))
    
    # Get patient details
    patient = mongo.db.patients.find_one({'ehr_number': ehr_number})
    if not patient:
        flash('Patient not found', 'error')
        return redirect(url_for('clinical.nurses_desk_queue', department_name=department_name))
    
    # Get latest vitals
    latest_vitals = mongo.db.nurses_vitals.find_one(
        {'ehr_number': ehr_number},
        sort=[('registration_date', -1)]
    )
    
    if not latest_vitals:
        flash('No vitals found for this patient', 'error')
        return redirect(url_for('clinical.nurses_desk_queue', department_name=department_name))
    
    if request.method == 'POST':
        # Create doctors queue entry
        doctors_queue_data = {
            'ehr_number': ehr_number,
            'patient_name': f"{patient.get('patient_first_name', '')} {patient.get('patient_last_name', '')}",
            'department': department_name,
            'room_number': latest_vitals['room_number'],
            'status': 'Waiting',
            'assigned_doctor': None,
            'assigned_at': None,
            'completed_at': None,
            'vitals': {
                'temperature': latest_vitals['temperature'],
                'pulse_rate': latest_vitals['pulse_rate'],
                'respiratory_rate': latest_vitals['respiratory_rate'],
                'blood_pressure_systolic': latest_vitals['blood_pressure_systolic'],
                'blood_pressure_diastolic': latest_vitals['blood_pressure_diastolic'],
                'weight': latest_vitals['weight'],
                'height': latest_vitals['height'],
                'muac': latest_vitals['muac'],
                'additional_notes': latest_vitals['additional_notes']
            },
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Insert into doctors queue
        mongo.db.doctors_queue.insert_one(doctors_queue_data)
        
        # Clear the current patient from session
        session.pop('current_patient_ehr', None)
        
        flash('Patient successfully added to doctor\'s queue', 'success')
        return redirect(url_for('clinical.nurses_desk_queue', department_name=department_name))
    
    return render_template(
        'send_to_doctor.html',
        patient=patient,
        vitals=latest_vitals,
        department=department_name
    )