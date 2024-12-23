import React from 'react';
import ClinicalSidebar from './sidebar';

const ClinicalDashboard = () => {
    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <ClinicalSidebar />

            {/* Main Content Area */}
            <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
                {/* Dashboard Header */}
                <header className="mb-6 border-b pb-4">
                    <h1 className="text-2xl font-bold text-gray-800">Clinical Dashboard</h1>
                    <p className="text-gray-600 mt-2">Welcome to the clinical management system</p>
                </header>

                {/* Dashboard Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Patient Statistics Card */}
                    <div className="bg-white shadow-md rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-800">Patient Statistics</h2>
                            <i className="fa fa-users text-blue-500"></i>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-gray-600">Total Patients</p>
                                <p className="text-2xl font-bold text-blue-600">1,245</p>
                            </div>
                            <div>
                                <p className="text-gray-600">New This Month</p>
                                <p className="text-2xl font-bold text-green-600">127</p>
                            </div>
                        </div>
                    </div>

                    {/* Appointments Card */}
                    <div className="bg-white shadow-md rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-800">Appointments</h2>
                            <i className="fa fa-calendar text-purple-500"></i>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <p className="text-gray-600">Today</p>
                                <p className="text-2xl font-bold text-purple-600">42</p>
                            </div>
                            <div>
                                <p className="text-gray-600">Upcoming</p>
                                <p className="text-2xl font-bold text-orange-600">78</p>
                            </div>
                        </div>
                    </div>

                    {/* Recent Activities Card */}
                    <div className="bg-white shadow-md rounded-lg p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-800">Recent Activities</h2>
                            <i className="fa fa-bell text-red-500"></i>
                        </div>
                        <ul className="space-y-2">
                            <li className="flex items-center">
                                <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                                <span className="text-sm text-gray-700">New patient enrolled</span>
                            </li>
                            <li className="flex items-center">
                                <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                                <span className="text-sm text-gray-700">Appointment scheduled</span>
                            </li>
                            <li className="flex items-center">
                                <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>
                                <span className="text-sm text-gray-700">Prescription updated</span>
                            </li>
                        </ul>
                    </div>

                    {/* Quick Actions */}
                    <div className="bg-white shadow-md rounded-lg p-6 md:col-span-2 lg:col-span-1">
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">Quick Actions</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <button className="bg-blue-500 text-white py-2 rounded hover:bg-blue-600 transition flex items-center justify-center">
                                <i className="fa fa-plus mr-2"></i> New Patient
                            </button>
                            <button className="bg-green-500 text-white py-2 rounded hover:bg-green-600 transition flex items-center justify-center">
                                <i className="fa fa-calendar-plus-o mr-2"></i> Book Appt
                            </button>
                            <button className="bg-purple-500 text-white py-2 rounded hover:bg-purple-600 transition flex items-center justify-center">
                                <i className="fa fa-file-text-o mr-2"></i> Reports
                            </button>
                            <button className="bg-red-500 text-white py-2 rounded hover:bg-red-600 transition flex items-center justify-center">
                                <i className="fa fa-search mr-2"></i> Search
                            </button>
                        </div>
                    </div>

                    {/* Last Section - Fullwidth */}
                    <div className="bg-white shadow-md rounded-lg p-6 col-span-full">
                        <h2 className="text-lg font-semibold text-gray-800 mb-4">Upcoming Schedules</h2>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left text-gray-600">
                                <thead className="bg-gray-100 text-gray-700">
                                    <tr>
                                        <th className="px-4 py-2">Patient</th>
                                        <th className="px-4 py-2">Doctor</th>
                                        <th className="px-4 py-2">Date</th>
                                        <th className="px-4 py-2">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr className="border-b">
                                        <td className="px-4 py-2">John Doe</td>
                                        <td className="px-4 py-2">Dr. Smith</td>
                                        <td className="px-4 py-2">2024-01-15</td>
                                        <td className="px-4 py-2">
                                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs">Confirmed</span>
                                        </td>
                                    </tr>
                                    <tr className="border-b">
                                        <td className="px-4 py-2">Jane Smith</td>
                                        <td className="px-4 py-2">Dr. Johnson</td>
                                        <td className="px-4 py-2">2024-01-16</td>
                                        <td className="px-4 py-2">
                                            <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">Pending</span>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default ClinicalDashboard;