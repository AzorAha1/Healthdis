import React, { useState } from 'react';
import axios from 'axios';
import tauraimage from './assets/taura.jpg'

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('clinical-services'); // default role
    const [errorMessage, setErrorMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('/api/login', { email, password, role });
            if (response.data.success) {
                window.location.href = response.data.redirectUrl; // Redirect based on response
            } else {
                setErrorMessage('Invalid credentials or role');
            }
        } catch (error) {
            setErrorMessage('An error occurred. Please try again.');
        }
    };

    return (
        <div className="h-screen flex justify-center items-center bg-cover bg-center"  style={{ backgroundImage: `url(${tauraimage})` }}>
            <div className="w-full max-w-md p-8 bg-white rounded shadow-md">
                <h2 className="text-2xl font-bold text-center mb-4">FMC Taura Login</h2>
                {errorMessage && (
                    <div className="bg-red-100 text-red-700 px-4 py-2 rounded mb-4">
                        {errorMessage}
                    </div>
                )}
                <div className="flex justify-around mb-6">
                    <button
                        className={`px-4 py-2 rounded ${
                            role === 'clinical-services'
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-200 text-gray-800'
                        }`}
                        onClick={() => setRole('clinical-services')}
                    >
                        Clinical
                    </button>
                    <button
                        className={`px-4 py-2 rounded ${
                            role === 'medpay-user'
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-200 text-gray-800'
                        }`}
                        onClick={() => setRole('medpay-user')}
                    >
                        MedPay
                    </button>
                    <button
                        className={`px-4 py-2 rounded ${
                            role === 'admin-user'
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-200 text-gray-800'
                        }`}
                        onClick={() => setRole('admin-user')}
                    >
                        Admin
                    </button>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-gray-700">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-gray-700">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
                            required
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
                    >
                        Sign In
                    </button>
                </form>
            </div>
        </div>
    );
};

export default LoginForm;