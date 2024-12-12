import React, { useState } from 'react';
import axios from 'axios';
import tauraimage from './assets/taura.jpg';

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('clinical-services'); // default role
    const [errorMessage, setErrorMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const response = await axios.post('/api/login', { email, password, role });
            if (response.data.success) {
                window.location.href = response.data.redirectUrl;
            } else {
                setErrorMessage('Invalid credentials or role');
            }
        } catch (error) {
            setErrorMessage('An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="h-screen flex justify-center items-center bg-cover bg-center relative" style={{ backgroundImage: `url(${tauraimage})` }}>
            <div className="absolute inset-0 bg-black opacity-50"></div> {/* Dark overlay */}
            <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-lg animate-fadeIn">
                <h2 className="text-2xl font-bold text-center mb-6">FMC Taura Login</h2>
                {errorMessage && (
                    <div className="bg-red-100 text-red-700 px-4 py-2 rounded mb-4">
                        {errorMessage}
                    </div>
                )}
                <div className="flex flex-col sm:flex-row justify-around mb-6">
                    <button
                        className={`px-4 py-2 rounded transition duration-300 ease-in-out transform ${role === 'clinical-services' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}
                        onClick={() => setRole('clinical-services')}
                    >
                        Clinical
                    </button>
                    <button
                        className={`px-4 py-2 rounded transition duration-300 ease-in-out transform ${role === 'medpay-user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}
                        onClick={() => setRole('medpay-user')}
                    >
                        MedPay
                    </button>
                    <button
                        className={`px-4 py-2 rounded transition duration-300 ease-in-out transform ${role === 'admin-user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'}`}
                        onClick={() => setRole('admin-user')}
                    >
                        Admin
                    </button>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-gray-700">Email</label>
                        <div className="relative">
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-2 pl-10 border rounded focus:outline-none focus:ring-4 focus:ring-blue-500"
                                required
                            />
                            <svg className="absolute left-3 top-3 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2a10 10 0 0110 10c0 4.28-2.652 7.918-6.39 9.248A7.99 7.99 0 0012 18a7.99 7.99 0 00-3.61-.752A9.973 9.973 0 012 12a10 10 0 0110-10z" />
                            </svg>
                        </div>
                    </div>
                    <div>
                        <label className="block text-gray-700">Password</label>
                        <div className="relative">
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-2 pl-10 border rounded focus:outline-none focus:ring-4 focus:ring-blue-500"
                                required
                            />
                            <svg className="absolute left-3 top-3 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" width="16" height="16">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 11c1.104 0 2-.896 2-2s-.896-2-2-2-2 .896-2 2 .896 2 2 2z" />
                            </svg>
                        </div>
                    </div>
                    <button
                        type="submit"
                        className={`w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600 transition duration-300 ease-in-out ${loading ? 'cursor-wait' : ''}`}
                    >
                        {loading ? 'Signing In...' : 'Sign In'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default LoginForm;