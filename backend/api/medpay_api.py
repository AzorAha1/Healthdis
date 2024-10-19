from datetime import datetime
import uuid
from flask import request
from flask_smorest import Blueprint
from marshmallow import fields, Schema
from backend.auth.decorator import admin_or_role_required, login_required
from backend.helperfuncs.helperfuncs import calculate_age, generate_ehr_number, get_registration_fee
from backend.extensions import mongo
from flask import flash, render_template, request, redirect, url_for, session
from bson import ObjectId


class MedpayApi(Schema):
    dob = fields.Date(required=True)
    patient_id = fields.String(required=True)
    service_name = fields.String(required=True)
    service_fee = fields.String(required=True)
    service_code = fields.String(required=True)
    patient_name = fields.String(required=True)
    patient_phone = fields.String(required=True)
    patient_email = fields.String(required=True)
    patient_address = fields.String(required=True)

medpay_bp = Blueprint('medpay', 'medpay', url_prefix='/medpay')

@medpay_bp.route('/')
@medpay_bp.route('/dashboard')
# @login_required
# @admin_or_role_required('medpay-user')
def medpay_dashboard():
    print(session)
    return render_template('medpay_dashboard.html', title='MedPay Dashboard')

@medpay_bp.route('/make_payment', methods=['GET', 'POST'])
def make_payment():
    if request.method == 'POST':
        request_id = request.form.get('request_id')
        is_new_patient =  False
        if not request_id:
            flash('No request ID provided', 'error')
            return redirect(url_for('medpay.pos_terminal'))
        
        try:
            request_details = mongo.db.requests.find_one({'_id': ObjectId(request_id)})
            print(f'request details: {request_details}')
        except:
            flash('Invalid request ID', 'error')
            return redirect(url_for('medpay.pos_terminal'))
        
        if not request_details:
            flash('Request not found', 'error')
            return redirect(url_for('medpay.pos_terminal'))
        
        # Use ehr_number or temp_ehr_number to find the patient
        ehr_number = request_details.get('ehr_number')
        patient_data = mongo.db.patients.find_one({
            '$or': [
                {'ehr_number': ehr_number},
                {'temp_ehr_number': ehr_number}
            ]
        })
        
        if not patient_data:
            flash('Patient not found', 'error')
            return redirect(url_for('medpay.pos_terminal'))
        
        patient_hospital_number = patient_data.get('hospital_number')
        dob = patient_data.get('dob')
        
        # Check if this is a new patient (has temp_ehr_number but no ehr_number)
        if 'temp_ehr_number' in patient_data and 'ehr_number' not in patient_data:
            new_ehr_number = generate_ehr_number()
            mongo.db.patients.update_one(
                {'hospital_number': patient_hospital_number},
                {'$set': {'ehr_number': new_ehr_number},
                '$unset': {'temp_ehr_number': 1}}
            )
            is_new_patient = True
        else:
            new_ehr_number = patient_data.get('ehr_number')
            is_new_patient = False
        patient_Number = request_details.get('patient_Number')
        requested_by = session.get('email', 'Unknown')
        service_name = request_details.get('Service_Name')
        service_code = request_details.get('Service_Code')
        cost = request_details.get('Cost')
        department = request_details.get('Department')
        invoice_date = request_details.get('Invoice Date')
        
        payments = {
            'patient_Number': patient_Number,
            'ehr_number': new_ehr_number,
            'requested_by': requested_by,
            'service_name': service_name,
            'service_code': service_code,
            'cost': cost,
            'department': department,
            'invoice_date': invoice_date,
            'payment_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'Status': 'Paid'
        }
        
        try:
            # Insert the payment record
            mongo.db.payments.insert_one(payments)
            
            # Remove the request from the requests collection
            mongo.db.requests.delete_one({'_id': ObjectId(request_id)})
            
            # Calculate age and determine queue
            if dob:
                patient_age = calculate_age(dob)
                if patient_age > 14 and is_new_patient:  # Adult
                    mongo.db.hims_queue.insert_one({
                        'ehr_number': new_ehr_number,
                        'patient_name': patient_Number,
                        'registration_date': datetime.now(),
                        'status': 'Pending'
                    })
                    flash(f'Payment processed for {service_name} ({service_code}). Patient added to HIMS queue.', 'success')
                else:  # Child
                    mongo.db.pediatric_queue.insert_one({
                        'ehr_number': new_ehr_number,
                        'patient_name': patient_Number,
                        'registration_date': datetime.now(),
                        'status': 'Pending'
                    })
                    flash(f'Payment processed for {service_name} ({service_code}). Check Paediatric to find Patient', 'success')
            else:
                flash(f'Payment processed for {service_name} ({service_code}). Unable to determine queue due to missing DOB.', 'warning')
            
            return render_template('make_payment.html', userinfos=request_details, payments=payments, title='Payment Successful')
        except Exception as e:
            flash(f'Error processing payment: {str(e)}', 'error')
            return redirect(url_for('medpay.pos_terminal'))
    
    # Handle GET requests
    return redirect(url_for('pos_terminal'))

@medpay_bp.route('/pos_terminal/', methods=['GET', 'POST'])
@login_required
@admin_or_role_required('medpay-user')
def pos_terminal():
    # Initialize `requests` as an empty list by default
    requests = []

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
            # Handle the case where the search term is missing
            flash('Please provide a valid EHR number or Service Code', 'error')
    else:
        # In case of a GET request, show all requests
        requests = mongo.db.requests.find() 

    return render_template('pos_terminal.html', requests=requests, title='POS Terminal')

