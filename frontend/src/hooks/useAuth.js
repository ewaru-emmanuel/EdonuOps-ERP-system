import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../services/apiClient';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      // In a real-world scenario, you would decode the token to get user info
      // For this project, we'll assume the token is valid for now.
      setIsAuthenticated(true);
      // You could also make an API call to get user details based on the token
      // e.g., apiClient.get('/auth/me')
      // For now, we'll set a placeholder user
      setUser({ id: 1, username: 'Authenticated User', role: 'admin' });
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const response = await apiClient.post('/auth/login', { email, password });
      const { access_token } = response.data;
      
      localStorage.setItem('access_token', access_token);
      setIsAuthenticated(true);
      
      // Fetch user data after successful login.
      // This is a simplified example; a real app might decode the token
      // or hit a /profile endpoint.
      const userResponse = await apiClient.get('/auth/protected');
      setUser({ 
        username: userResponse.data.logged_in_as, 
        role: 'admin' // Assuming a default role for this example
      });
      
      return response.data;
    } catch (error) {
      console.error("Login failed:", error);
      throw new Error('Login failed');
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
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  return useContext(AuthContext);
};