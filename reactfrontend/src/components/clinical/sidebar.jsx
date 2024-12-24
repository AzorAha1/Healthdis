import React, { useState } from 'react'; // Add useState
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome, faTachometerAlt, faFileInvoiceDollar, faStethoscope, faClinicMedical, faBed, faPaperPlane, faArrowLeft, faArrowRight, faArrowDown, faArrowRightRotate, faUserAlt } from '@fortawesome/free-solid-svg-icons';
import { faEarlybirds } from '@fortawesome/free-brands-svg-icons';
import { faHospitalAlt } from '@fortawesome/free-regular-svg-icons/faHospitalAlt';

const Sidebar = () => {
    const [isCollapsed, setIsCollapsed] = useState(false); // State for sidebar collapse

    // States to control the visibility of each submenu
    const [isHimUnitOpen, setIsHimUnitOpen] = useState(false);
    const [isOutPatientOpen, setIsOutPatientOpen] = useState(false);
    const [isInPatientOpen, setIsInPatientOpen] = useState(false);
    const [isDirectRequestOpen, setIsDirectRequestOpen] = useState(false);


    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    };

    const collapsediteminmenu = (title, icon) => {
        return (
            <li className="flex items-center space-x-4 p-2 hover:bg-gray-700 rounded">
                <div className="flex items-center space-x-4">
                    <FontAwesomeIcon icon={icon} className="text-lg" />
                    {!isCollapsed && <span>{title}</span>}
                </div>
            </li>
        );
    };

    return (
        <aside
            style={{ backgroundColor: '#1e1e2d' }}
            className={`h-screen text-white transition-all duration-300 ${isCollapsed ? 'w-20' : 'w-72'}`}
        >
            {/* Header Section */}
            <div style={{ backgroundColor: '#1a1a26' }} className="p-4 flex items-center justify-between">
                {/* Title */}
                {!isCollapsed && (
                    <h1 className="text-2xl font-semibold text-blue-400">HealthDis</h1>
                )}

                {/* Back Icon */}
                <button
                    className={`text-white hover:text-blue-400 cursor-pointer transition-transform duration-300 ease-in-out ${
                        isCollapsed ? 'rotate-0' : 'rotate-180'
                    }`}
                    onClick={toggleSidebar}
                >
                    <FontAwesomeIcon icon={faArrowRight} className="text-xl" />
                </button>
            </div>

            {/* Menu Section */}
            <ul className="p-4 space-y-4">
                {/* Dashboard */}
                <li className="flex items-center space-x-4 p-2 hover:bg-gray-700 rounded">
                    <FontAwesomeIcon icon={faTachometerAlt} className="text-lg" />
                    {!isCollapsed && <span>Dashboard</span>}
                </li>
                {/* Billing */}
                <li className="flex items-center space-x-4 p-2 hover:bg-gray-700 rounded">
                    <FontAwesomeIcon icon={faFileInvoiceDollar} className="text-lg" />
                    {!isCollapsed && <span>Billing</span>}
                </li>
                {/* Home */}
                <li className="flex items-center space-x-4 p-2 hover:bg-gray-700 rounded">
                    <FontAwesomeIcon icon={faHome} className="text-lg" />
                    {!isCollapsed && <span>Home</span>}
                </li>
                {/* HIM Unit */}
                <li
                    className="flex items-center justify-between p-2 hover:bg-gray-700 rounded cursor-pointer"
                    onClick={() => setIsHimUnitOpen(!isHimUnitOpen)} // Toggle submenu
                >
                    <div className="flex items-center space-x-4">
                        <FontAwesomeIcon icon={faStethoscope} className="text-lg" />
                        {!isCollapsed && <span>HIM Unit</span>}
                    </div>
                    {!isCollapsed && (
                        <FontAwesomeIcon
                            icon={faArrowDown}
                            className={`text-sm transform transition-transform ${isHimUnitOpen ? 'rotate-180' : ''}`}
                        />
                    )}
                </li>
                {isHimUnitOpen && !isCollapsed && (
                    <ul className="pl-8 space-y-2">
                        {collapsediteminmenu('HIM Dashboard', faTachometerAlt)}
                        {collapsediteminmenu('Update Patient Record', faArrowRightRotate)}
                        {collapsediteminmenu('New Patient Registered', faUserAlt)}
                        {collapsediteminmenu('Follow-up Visit', faHospitalAlt)}
                        {collapsediteminmenu('Out-Patient Clinic', faClinicMedical)}
                        {collapsediteminmenu('In-Patient/Wards', faBed)}
                        {collapsediteminmenu('Direct Request', faPaperPlane)}
                    </ul>
                )}
                <li className="flex items-center justify-between p-2 hover:bg-gray-700 rounded cursor-pointer"
                    onClick={() => setIsOutPatientOpen(!isOutPatientOpen)} // Toggle submenu

                >
                    <div className="flex items-center space-x-4">
                        <FontAwesomeIcon icon={faClinicMedical} className="text-lg" />
                        {!isCollapsed && <span>Out-Patient Clinic</span>}
                    </div>
                    {!isCollapsed && (
                        <FontAwesomeIcon
                            icon={faArrowDown}
                            className={`text-sm transform transition-transform ${isOutPatientOpen ? 'rotate-180' : ''}`}
                        />
                    )}

                </li>
                {isOutPatientOpen && !isCollapsed && (
                    <ul className="pl-8 space-y-2">
                        {collapsediteminmenu('Out-Patient Clinic', faClinicMedical)}
                        {collapsediteminmenu('New Patient Registered', faUserAlt)}
                        {collapsediteminmenu('Follow-up Visit', faHospitalAlt)}
                        {collapsediteminmenu('Direct Request', faPaperPlane)}
                    </ul>
                )}
                <li className="flex items-center justify-between p-2 hover:bg-gray-700 rounded cursor-pointer"
                    onClick={() => setIsInPatientOpen(!isInPatientOpen)} // Toggle submen
                >
                    <div className="flex items-center space-x-4">
                        <FontAwesomeIcon icon={faBed} className="text-lg" />
                        {!isCollapsed && <span>In-Patient/Wards</span>}
                    </div>
                    {!isCollapsed && (
                        <FontAwesomeIcon
                            icon={faArrowDown}
                            className={`text-sm transform transition-transform ${isInPatientOpen ? 'rotate-180' : ''}`}
                        />
                    )}
                </li>
                {isInPatientOpen && !isCollapsed && (
                    <ul className="pl-8 space-y-2">
                        {collapsediteminmenu('In-Patient/Wards', faBed)}
                        {collapsediteminmenu('New Patient Registered', faUserAlt)}
                        {collapsediteminmenu('Follow-up Visit', faHospitalAlt)}
                        {collapsediteminmenu('Direct Request', faPaperPlane)}
                    </ul>
                )}
                <li className="flex items-center justify-between p-2 hover:bg-gray-700 rounded cursor-pointer"
                    onClick={() => setIsDirectRequestOpen(!isDirectRequestOpen)} // Toggle submenu
                >
                    <div className="flex items-center space-x-4">
                        <FontAwesomeIcon icon={faPaperPlane} className="text-lg" />
                        {!isCollapsed && <span>Direct Request</span>}
                    </div>
                    {!isCollapsed && (
                        <FontAwesomeIcon
                            icon={faArrowDown}
                            className={`text-sm transform transition-transform ${isDirectRequestOpen ? 'rotate-180' : ''}`}
                        />
                    )}
                </li>
                {isDirectRequestOpen && !isCollapsed && (
                    <ul className="pl-8 space-y-2">
                        {collapsediteminmenu('Direct Request', faPaperPlane)}
                        {collapsediteminmenu('New Patient Registered', faUserAlt)}
                        {collapsediteminmenu('Follow-up Visit', faHospitalAlt)}
                    </ul>
                )}
            </ul>
        </aside>
    );
};

export default Sidebar;