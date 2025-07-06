import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { MockDataProvider, useMockData } from './contexts/MockDataContext';
import PrivateRoute from './components/PrivateRoute';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import RiskAssessment from './pages/RiskAssessment';
import ThreatIntelligence from './pages/ThreatIntelligence';
import Compliance from './pages/Compliance';
import Settings from './pages/Settings';

const AppLayout = ({ children }) => {
  const { user } = useAuth();
  return (
    <>
      {user && <Sidebar />}
      {user && <Navbar />}
      <div className={user ? 'pl-[256px] min-h-screen bg-gray-100' : ''}>
        <main className={user ? 'p-8' : ''}>{children}</main>
      </div>
    </>
  );
};

const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
    <Route path="/risk-assessment" element={<PrivateRoute><RiskAssessment /></PrivateRoute>} />
    <Route path="/threat-intelligence" element={<PrivateRoute><ThreatIntelligence /></PrivateRoute>} />
    <Route path="/compliance" element={<PrivateRoute><Compliance /></PrivateRoute>} />
    <Route path="/settings" element={<PrivateRoute><Settings /></PrivateRoute>} />
  </Routes>
);

const App = () => {
  return (
    <MockDataProvider>
      <AuthProvider>
        <AppLayout>
          <AppRoutes />
        </AppLayout>
      </AuthProvider>
    </MockDataProvider>
  );
};

export default App; 