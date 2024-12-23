import LoginForm from './Loginform';
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ClinicalDashboard from './components/clinical/ClinicalDashboard';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginForm />} />
        <Route path="/clinical/dashboard" element={<ClinicalDashboard />} />
        {/* Add a catch-all redirect if needed */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
};

export default App;