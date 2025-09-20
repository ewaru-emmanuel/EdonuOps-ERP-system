import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../services/apiClient';
import { initializeERPApiService } from '../services/erpApiService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    if (initialized) return; // Prevent multiple initializations
    
    // Initialize the ERP API service
    initializeERPApiService(apiClient);
    
    const token = localStorage.getItem('access_token');
    if (token) {
      // Token exists, set authenticated state
      setIsAuthenticated(true);
      // Set a placeholder user (in production, you'd decode the JWT or call /auth/me)
      setUser({ id: 1, username: 'Authenticated User', role: 'admin' });
    } else {
      // No token, ensure user is logged out
      setIsAuthenticated(false);
      setUser(null);
    }
    setLoading(false);
    setInitialized(true);
  }, [initialized]);

  const login = async (email, password) => {
    try {
      const response = await apiClient.login({ email, password });
      const { access_token, user: userData } = response;
      
      localStorage.setItem('access_token', access_token);
      setIsAuthenticated(true);
      setUser({
        id: userData.id || 1,
        username: userData.username,
        email: userData.email,
        role: userData.role
      });
      
      return response;
    } catch (error) {
      console.error("Login failed:", error);
      throw new Error(error.response?.data?.message || 'Login failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setIsAuthenticated(false);
    setUser(null);
    window.location.href = '/login'; // Redirect to login page
  };

  const value = {
    user,
    isAuthenticated,
    login,
    logout,
    loading,
    initialized
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    // Return default values instead of throwing error during initialization
    return {
      user: null,
      isAuthenticated: false,
      loading: true,
      initialized: false,
      login: () => Promise.reject(new Error('Auth not initialized')),
      logout: () => {}
    };
  }
  return context;
};