import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import ScanUpload from './pages/ScanUpload';
import Vulnerabilities from './pages/Vulnerabilities';
import Settings from './pages/Settings';
import Reports from './pages/Reports';
import Login from './pages/Login';
import Signup from './pages/Signup';

const App: React.FC = () => {
  const isAuthenticated = true; // Mock auth for demo

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        <Route path="/" element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}>
          <Route index element={<Dashboard />} />
          <Route path="scans" element={<ScanUpload />} />
          <Route path="vulnerabilities" element={<Vulnerabilities />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />
          {/* Fallback routes */}
          <Route path="*" element={<Navigate to="/" />} />
        </Route>
      </Routes>
    </Router>
  );
};

export default App;