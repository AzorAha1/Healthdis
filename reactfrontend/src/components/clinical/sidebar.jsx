import React, { useState } from 'react'; // Add useState
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faUser, faCog, faArrowLeft, faArrowRight } from '@fortawesome/free-solid-svg-icons';

const Sidebar = () => {
    const [isCollapsed, setIsCollapsed] = useState(false); // State for sidebar collapse

    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    }

    return (
        <aside style={{ backgroundColor: '#1e1e2d' }} 
            className={`h-screen text-white transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-72'}`}
        >
            {/* Header Section */}
            <div style={{ backgroundColor: '#1a1a26' }} className="p-4 flex items-center justify-between">
                {/* Title */}
                {!isCollapsed && (
                    <h1 className="text-2xl font-semibold text-blue-400">HealthDis</h1>
                )}
                
                {/* Back Icon */}
                <button className="text-white hover:text-blue-400" onClick={toggleSidebar}>
                    <FontAwesomeIcon icon={isCollapsed ? faArrowLeft : faArrowRight} className="text-xl" />
                </button>
            </div>
            
            {/* Menu Section */}
            <ul className="p-4 space-y-4">
                {/* Home */}
                <li className="flex items-center space-x-4 p-2 hover:bg-gray-700 rounded">
                    <FontAwesomeIcon icon={faHome} className="text-lg" />
                    {!isCollapsed && (
                        <span>Home</span>
                    )}
                </li>
                {/* Profile */}
                <li className="flex items-center space-x-4 p-2 hover:bg-gray-700 rounded">
                    <FontAwesomeIcon icon={faUser} className="text-lg" />
                    {!isCollapsed && (
                        <span>Profile</span>
                    )}
                </li>
                {/* Settings */}
                <li className="flex items-center space-x-4 p-2 hover:bg-gray-700 rounded">
                    <FontAwesomeIcon icon={faCog} className="text-lg" />
                    {!isCollapsed && (
                        <span>Settings</span>
                    )}
                </li>
            </ul>
        </aside>
    );
};

export default Sidebar;