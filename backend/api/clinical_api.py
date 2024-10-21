from datetime import datetime, timedelta
import json
import uuid
import bson
from flask import request
from flask_smorest import Blueprint
from marshmallow import fields, Schema
from backend.helperfuncs.helperfuncs import get_registration_fee
from backend.extensions import mongo
from flask import flash, render_template, request, redirect, url_for, session
from bson import ObjectId

class ClinicalSchema(Schema):
    pass

clinical_bp = Blueprint('clinical', 'clinical', url_prefix='/clinical')


@clinical_bp.route('/', methods=['GET'])
@clinical_bp.route('/dashboard/', methods=['GET'])
# @login_required
# @role_required('clinical-services', 'admin-user')
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

@clinical_bp.route('/doctors_dashboard')
# @role_required('doctors')
# @login_required
def doctors_dashboard():
    """this is the doctors dashboard"""
    return render_template('doctors_dashboard.html', title='Doctors Dashboard')

@clinical_bp.route('/nurses_desk/', methods=['GET', 'POST'])
def nurses_desk():
    """nurses desk"""
    departments = mongo.db.departments.find()
    if request.method == 'POST':
        department_id = request.form.get('nurse_department')
        try:
            department = mongo.db.departments.find_one({'_id': ObjectId(department_id)})
            
            if department:
                department_name = department['department_name']
                # nurses_queue_name = f"{department_name.lower().replace(' ', '_')}_nurses_queue"
                #store department name in session
                session['department_name'] = department_name
               
                return redirect(url_for('clinical.nurses_desk_queue', department_name=department_name))
            else:
                flash('Department not found', 'danger')
        except bson.errors.InvalidId:
            flash('Invalid department ID', 'danger')
        
        # If there's any error, redirect back to nurses_desk
        return redirect(url_for('clinical.nurses_desk'))
    
    return render_template('nurses_desk.html', title='Nurses Desk', departments=departments)

@clinical_bp.route('/take_vitals/', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def take_vitals():
    """Take vitals for a patient"""
    ehr_number = session.get('current_patient_ehr')
    if not ehr_number:
        flash('No patient selected', 'error')
        return redirect(url_for('clinical.nurses_desk_queue'))
    
    patient = mongo.db.patients.find_one({'ehr_number': ehr_number})
    if not patient:
        flash('Patient not found', 'error')
        return redirect(url_for('clinical.nurses_desk_queue'))
    
    if request.method == 'POST':
        # Get the vitals data from the form
        vitals_data = {
            'ehr_number': ehr_number,  # Use the ehr_number from the session
            'temperature': request.form.get('temperature'),
            'pulse_rate': request.form.get('pulse_rate'),
            'respiratory_rate': request.form.get('respiratory_rate'),
            'blood_pressure': request.form.get('blood_pressure'),
            'weight': request.form.get('weight'),
            'height': request.form.get('height'),
            'bmi': request.form.get('bmi'),
            'muac': request.form.get('muac'),
            'oxygen_saturation': request.form.get('oxygen_saturation'),
            'registration_date': datetime.now(),
            'additional_notes': request.form.get('additional_notes'),
            'nurse': session.get('email', 'Unknown')
        }
        
        mongo.db.nurses_vitals.insert_one(vitals_data)
        
        # Flash a success message
        flash('Vitals recorded successfully', 'success')
        
        # Clear the session after successfully recording vitals
        session.pop('current_patient_ehr', None)
        
        return redirect(url_for('clinical.nurses_desk_queue', department_name=session.get('department_name')))
    
    return render_template('take_vitals.html', title='Take Vitals', patient=patient)

@clinical_bp.route('/set_current_patient', methods=['POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def set_current_patient():
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
# @clinical_bp.route('/nurses_desk_queue/<department_name>')
# @login_required
# @admin_or_role_required('clinical-services')
# def nurses_desk_queue(department_name):
#     """Display the queue for a specific department"""
#     # get the date filter from te h query parameters, default to today
#     date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

#     try:
#         filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
#     except ValueError:
#         flash('Invalid date format. Showing today\'s records.', 'warning')
#         filter_date = datetime.now()
#     # set the date range from the filter (entire day)
#     start_of_day = filter_date.replace(hour=0, minute=0, second=0, microsecond=0)
#     end_of_day = start_of_day + timedelta(days=1)
    
#     # query for records with the date range
#     date_query = {
#         'registration_date': {
#             '$gte': start_of_day,
#             '$lt': end_of_day
#         }
#     }
#     pending_queue = list(mongo.db[department_name.lower().replace(' ', '_') + '_nurses_queue'].find({**date_query, 'status': 'Pending'}))
#     processed_queue = list(mongo.db[department_name.lower().replace(' ', '_') + '_nurses_queue'].find({**date_query, 'status': {'$ne': 'Pending'}}))
#     return render_template('nurses_desk_queue.html', title='Nurses Desk Queue', department_name=department_name, pending_queue=pending_queue, processed_queue=processed_queue, current_date=filter_date.strftime('%m-%d-%Y'))
@clinical_bp.route('/nurses_desk_queue/<department_name>', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def nurses_desk_queue(department_name):
    """Display the queue for a specific department"""
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
    return render_template('follow_up.html', title='Follow-Up Visit')

@clinical_bp.route('/ward_login', methods=['GET', 'POST'])
# @login_required
# @admin_or_role_required('clinical-services')
def ward_login():
    # Fetch departments with department_typ 'ward'
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