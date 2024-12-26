import LoginForm from './Loginform';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ClinicalDashboard from './components/clinical/ClinicalDashboard';
import NewPatient from './components/clinical/NewPatient';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginForm />} />
        <Route path="/clinical/dashboard" element={<ClinicalDashboard />} />
        {/* Add a catch-all redirect if needed */}
        <Route path="*" element={<Navigate to="/" replace />} />
        <Route path='/clinical/new_patient' element={<NewPatient />}></Route>
      </Routes>
    </Router>
  );
};

export default App;