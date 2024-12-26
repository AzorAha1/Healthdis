import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '../../api/axios';
import ClinicalSidebar from './sidebar';

const NewPatientEnrollment = () => {
    const [enrollmentCode, setEnrollmentCode] = useState('');
    const [isLoading, setIsLoading] = useState(false); 
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const getEnrollmentCode = async () => {
            try {
                setIsLoading(true);
                setError('');
                console.log('Fetching enrollment code...');
                const response = await axios.get('/clinical/api/new_patient');
                console.log('Response:', response);
                
                if (response.data && response.data.enrollment_code) {
                    setEnrollmentCode(response.data.enrollment_code);
                    console.log('Enrollment code set:', response.data.enrollment_code);
                } else {
                    console.log('No enrollment code in response:', response.data);
                    setError('No enrollment code received from server');
                }
            } catch (error) {
                console.log('Full error:', error);
                let errorMessage = 'Error fetching enrollment code';
                
                if (error.response) {
                    errorMessage = `Server Error: ${error.response.status} - ${error.response.data?.message || 'Unknown error'}`;
                } else if (error.request) {
                    errorMessage = 'No response received from server. Please check your connection.';
                } else {
                    errorMessage = error.message;
                }
                
                setError(errorMessage);
                console.error('Error details:', errorMessage);
            } finally {
                setIsLoading(false);
            }
        };
        
        getEnrollmentCode();
    }, []);
    const [formData, setFormData] = useState({
        patient_type: 'Regular',
        patient_first_name: '',
        patient_middle_name: '',
        patient_surname_name: '',
        dob: '',
        gender: '',
        tribe: '',
        marital_status: '',
        occupation: '',
        phone_number: '',
        address: '',
        place_of_origin: '',
        city: '',
        state: '',
        country: '',
        religion: '',
        next_of_kin: '',
        next_of_kin_relation: '',
        next_of_kin_phone_number: '',
        next_of_kin_address: ''
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            setError('');
            const submissionData = {
                ...formData,
                enrollment_code: enrollmentCode
            };
            const response = await axios.post('/clinical/api/new_patient', submissionData);
            if (response.data.status === 'success') {
                navigate('/clinical/dashboard');
            } else {
                setError(response.data.message || 'Error submitting form');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            setError(error.response?.data?.message || 'Error submitting form');
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <div className="flex h-screen bg-gray-100">
            <ClinicalSidebar />
            <main className="flex-1 overflow-y-auto p-6">
                <div className="max-w-4xl mx-auto">
                    <header className="mb-6">
                        <h1 className="text-3xl font-bold text-gray-800">New Patient Enrollment</h1>
                        <p className="text-gray-600 mt-2">Enter patient information to create a new record</p>
                    </header>

                    <div className='bg-blue-50 p-5 mb-4'>
                        <div className="flex flex-col">
                            <label htmlFor="enrollment_code" className='mb-2 font-medium text-gray-700'>Enrollment Code</label>
                            {isLoading ? (
                                <div className="w-full p-2 border rounded-md bg-gray-100">
                                    Loading...
                                </div>
                            ) : (
                                <input 
                                    type="text" 
                                    id="enrollment_code"
                                    value={enrollmentCode}
                                    readOnly
                                    className="w-full p-2 border rounded-md bg-gray-100 font-mono text-lg"
                                />
                            )}
                            {error && (
                                <div className="mt-2 p-2 bg-red-100 border border-red-400 text-red-700 rounded">
                                    {error}
                                </div>
                            )}
                        </div>
                    </div>

                    <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6 space-y-6">
                        {/* Patient Type Selection */}
                        <div className="bg-blue-50 p-4 rounded-md mb-6">
                            <label className="block text-sm font-medium text-gray-700 mb-2">Patient Type</label>
                            <select
                                name="patient_type"
                                value={formData.patient_type}
                                onChange={handleChange}
                                className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                            >
                                <option value="Regular">Regular</option>
                                <option value="NHIS">NHIS</option>
                            </select>
                        </div>

                        {/* Personal Information Section */}
                        <div className="border-b pb-6">
                            <h2 className="text-xl font-semibold text-gray-800 mb-4">Personal Information</h2>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                                    <input
                                        type="text"
                                        name="patient_first_name"
                                        value={formData.patient_first_name}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Middle Name</label>
                                    <input
                                        type="text"
                                        name="patient_middle_name"
                                        value={formData.patient_middle_name}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Surname</label>
                                    <input
                                        type="text"
                                        name="patient_surname_name"
                                        value={formData.patient_surname_name}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Date of Birth</label>
                                    <input
                                        type="date"
                                        name="dob"
                                        value={formData.dob}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                                    <select
                                        name="gender"
                                        value={formData.gender}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    >
                                        <option value="">Select Gender</option>
                                        <option value="Male">Male</option>
                                        <option value="Female">Female</option>
                                        <option value="Other">Other</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Marital Status</label>
                                    <select
                                        name="marital_status"
                                        value={formData.marital_status}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    >
                                        <option value="">Select Status</option>
                                        <option value="Single">Single</option>
                                        <option value="Married">Married</option>
                                        <option value="Divorced">Divorced</option>
                                        <option value="Widowed">Widowed</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        {/* Contact Information Section */}
                        <div className="border-b pb-6">
                            <h2 className="text-xl font-semibold text-gray-800 mb-4">Contact Information</h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                                    <input
                                        type="tel"
                                        name="phone_number"
                                        value={formData.phone_number}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
                                    <input
                                        type="text"
                                        name="address"
                                        value={formData.address}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
                                    <input
                                        type="text"
                                        name="city"
                                        value={formData.city}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">State</label>
                                    <input
                                        type="text"
                                        name="state"
                                        value={formData.state}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
                                    <input
                                        type="text"
                                        name="country"
                                        value={formData.country}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Next of Kin Information */}
                        <div className="border-b pb-6">
                            <h2 className="text-xl font-semibold text-gray-800 mb-4">Next of Kin Information</h2>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Next of Kin Name</label>
                                    <input
                                        type="text"
                                        name="next_of_kin"
                                        value={formData.next_of_kin}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Relation</label>
                                    <input
                                        type="text"
                                        name="next_of_kin_relation"
                                        value={formData.next_of_kin_relation}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                                    <input
                                        type="tel"
                                        name="next_of_kin_phone_number"
                                        value={formData.next_of_kin_phone_number}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="mt-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Next of Kin Address</label>
                                    <input
                                        type="text"
                                        name="next_of_kin_address"
                                        value={formData.next_of_kin_address}
                                        onChange={handleChange}
                                        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Submit and Cancel Buttons */}
                        <div className="flex justify-end mt-6">
                            <button
                                type="button"
                                onClick={() => navigate('/clinical/dashboard')}
                                className="px-6 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 mr-4"
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                            >
                                Enroll
                            </button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    );
};

export default NewPatientEnrollment;