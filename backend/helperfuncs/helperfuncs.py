from bson import ObjectId
from backend.extensions import mongo
from datetime import datetime
def generate_ehr_number():
    last_patient = mongo.db.patients.find_one(sort=[("ehr_number", -1)])
    if last_patient and 'ehr_number' in last_patient:
        try:
            last_ehr_number = int(last_patient['ehr_number'])
        except ValueError:
            last_ehr_number = 0
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
        ehr_fee_info =  mongo.db.ehr_fees.find_one({"service_name": "NEW CHILD GOPD REGISTRATION"})
    else:
        ehr_fee_info = mongo.db.ehr_fees.find_one({"service_name": "NEW ADULT GOPD REGISTRATION"})
    return f"{ehr_fee_info['service_name']} - {ehr_fee_info['service_fee']} - {ehr_fee_info['service_code']}"

# function to create department
def create_department(department_id, department_name, department_typ, department_abbreviation):
    try:
        department_name_clean = department_name.strip()
        mongo.db.departments.insert_one({
            'department_id': department_id,
            'department_name': department_name_clean,
            'department_typ': department_typ,
            'department_abbreviation': department_abbreviation
        })
        queue_name = f'{department_name_clean.lower().replace(" ", "_")}_nurses_queue'
        mongo.db.create_collection(queue_name)
        return True
    except Exception as e:
        print(e)
        return False

# function to update department 
def update_department(old_department_id, new_department_name, new_department_abbreviation, new_department_typ):
    try:
        old_department = mongo.db.departments.find_one({'_id': ObjectId(old_department_id)})
        if not old_department:
            return False
        
        result = mongo.db.departments.update_one(
            {'_id': ObjectId(old_department_id)},
            {'$set': {
                'department_name': new_department_name.strip(),
                'department_abbreviation': new_department_abbreviation,
                'department_typ': new_department_typ
            }}
        )
        
        if result.modified_count > 0:
            old_queue_name = f'{old_department["department_name"].lower().replace(" ", "_")}_nurses_queue'
            new_queue_name = f'{new_department_name.lower().replace(" ", "_")}_nurses_queue'
            
            if old_queue_name != new_queue_name and old_queue_name in mongo.db.list_collection_names():
                mongo.db[old_queue_name].rename(new_queue_name)
            return True
        return False
    except Exception as e:
        print(e)
        return False
