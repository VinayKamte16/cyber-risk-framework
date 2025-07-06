import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMockData } from './MockDataContext';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { generate, reset } = useMockData();

  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      // Simulate fetching user info from token
      setUser({ email: 'user' + Math.floor(Math.random() * 1000) + '@example.com' });
      generate();
    } else {
      setUser(null);
      reset();
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      // Simulate authentication and random user data
      localStorage.setItem('auth_token', 'dummy_token');
      setUser({ email: email || 'user' + Math.floor(Math.random() * 1000) + '@example.com' });
      generate();
      navigate('/dashboard');
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    reset();
    navigate('/login');
  };

  const value = {
    user,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 