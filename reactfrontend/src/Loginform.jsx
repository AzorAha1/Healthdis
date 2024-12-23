import React, { useState } from 'react';
import tauraimage from './assets/taura.jpg';
import axios from './api/axios';
import { useNavigate } from 'react-router-dom';
import { use } from 'react';

const LoginForm = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('clinical-services');
    const [errorMessage, setErrorMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);

    

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setErrorMessage('');
    
        // Basic validation
        if (!email || !password) {
            setErrorMessage('Please enter both email and password');
            setLoading(false);
            return;
        }
    
        try {
            const response = await axios.post('/api/login', { 
                email, 
                password, 
                role,
            });
    
            if (response.data.success) {
                // Log the full redirectUrl for debugging
                console.log('Redirect URL:', response.data.redirectUrl);
                
                // Extract the path from the full URL
                const redirectPath = new URL(response.data.redirectUrl, window.location.origin).pathname;
                
                // Log the extracted path for debugging
                console.log('Extracted Path:', redirectPath);
                navigate(redirectPath);
            } else {
                setErrorMessage(response.data.message || 'An unknown error occurred');
            }
        } catch (error) {
            console.error('Login error:', error.response ? error.response.data : error.message);
            setErrorMessage('An error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const roles = [
        { id: 'clinical-services', label: 'Clinical' },
        { id: 'medpay-user', label: 'MedPay' },
        { id: 'admin-user', label: 'Admin' }
    ];

    return (
        <div 
            className="min-h-screen flex justify-center items-center bg-cover bg-center relative p-4" 
            style={{ backgroundImage: `url(${tauraimage})` }}
        >
            <div className="absolute inset-0 bg-black opacity-50"></div>
            <div className="w-full max-w-md p-8 bg-white/90 backdrop-blur-sm rounded-xl shadow-2xl relative z-10">
                <div className="text-center mb-8">
                    <h2 className="text-3xl font-bold text-gray-800 mb-2">FMC Taura</h2>
                    <p className="text-gray-600">Select your role and sign in</p>
                </div>

                {errorMessage && (
                    <div 
                        className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4 animate-pulse"
                        role="alert"
                        aria-live="assertive"
                    >
                        {errorMessage}
                    </div>
                )}

                <div className="flex justify-center space-x-2 mb-6">
                    {roles.map((roleOption) => (
                        <button
                            key={roleOption.id}
                            className={`
                                px-4 py-2 rounded-lg transition duration-300 
                                ${role === roleOption.id 
                                    ? 'bg-blue-500 text-white scale-105 shadow-md' 
                                    : 'bg-gray-200 text-gray-800 hover:bg-gray-300'}
                            `}
                            onClick={() => setRole(roleOption.id)}
                            aria-pressed={role === roleOption.id}
                        >
                            {roleOption.label}
                        </button>
                    ))}
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label 
                            htmlFor="email" 
                            className="block text-gray-700 mb-2"
                        >
                            Email Address
                        </label>
                        <div className="relative">
                            <input
                                id="email"
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                                aria-required="true"
                                placeholder="Enter your email"
                            />
                            <svg 
                                className="absolute left-3 top-3 text-gray-500" 
                                xmlns="http://www.w3.org/2000/svg" 
                                fill="none" 
                                viewBox="0 0 24 24" 
                                stroke="currentColor" 
                                width="20" 
                                height="20"
                            >
                                <path 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round" 
                                    strokeWidth="2" 
                                    d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m9-9a9 9 0 00-9-9v0a9 9 0 00-9 9v0a9 9 0 009 9v0a9 9 0 009-9v0z" 
                                />
                            </svg>
                        </div>
                    </div>

                    <div>
                        <label 
                            htmlFor="password" 
                            className="block text-gray-700 mb-2"
                        >
                            Password
                        </label>
                        <div className="relative">
                            <input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-4 py-2 pl-10 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                required
                                aria-required="true"
                                placeholder="Enter your password"
                            />
                            <svg 
                                className="absolute left-3 top-3 text-gray-500" 
                                xmlns="http://www.w3.org/2000/svg" 
                                fill="none" 
                                viewBox="0 0 24 24" 
                                stroke="currentColor" 
                                width="20" 
                                height="20"
                            >
                                <path 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round" 
                                    strokeWidth="2" 
                                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" 
                                />
                            </svg>
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
                                aria-label={showPassword ? "Hide password" : "Show password"}
                            >
                                <svg 
                                    xmlns="http://www.w3.org/2000/svg" 
                                    fill="none" 
                                    viewBox="0 0 24 24" 
                                    stroke="currentColor" 
                                    width="20" 
                                    height="20"
                                >
                                    {showPassword ? (
                                        <path 
                                            strokeLinecap="round" 
                                            strokeLinejoin="round" 
                                            strokeWidth="2" 
                                            d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" 
                                        />
                                    ) : (
                                        <path 
                                            strokeLinecap="round" 
                                            strokeLinejoin="round" 
                                            strokeWidth="2" 
                                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" 
                                        />
                                    )}
                                </svg>
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center justify-between">
                        <div className="flex items-center">
                            <input
                                id="remember-me"
                                type="checkbox"
                                checked={rememberMe}
                                onChange={() => setRememberMe(!rememberMe)}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <label 
                                htmlFor="remember-me" 
                                className="ml-2 block text-sm text-gray-900"
                            >
                                Remember me
                            </label>
                        </div>
                        <div>
                            <a 
                                href="/forgot-password" 
                                className="text-sm text-blue-600 hover:text-blue-800 hover:underline"
                            >
                                Forgot password?
                            </a>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`
                            w-full py-3 rounded-lg text-white font-semibold transition duration-300
                            ${loading 
                                ? 'bg-blue-400 cursor-wait' 
                                : 'bg-blue-500 hover:bg-blue-600 active:bg-blue-700'}
                        `}
                    >
                        {loading ? 'Signing In...' : 'Sign In'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default LoginForm;