import React, { createContext, useContext, useState, useEffect } from 'react';
import databaseFirstPersistence from '../services/databaseFirstPersistence';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // Initialize state with localStorage values immediately
  // Don't initialize from localStorage - always start fresh
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const [loading, setLoading] = useState(false);
  const [initialized, setInitialized] = useState(false); // Start as false, set to true after session check

  // SECURITY: Removed getOrCreateUserId function - authentication must be STRICT
  // No fallbacks, no automatic user creation, no "in-between" states
  // Either user is authenticated or they are not - PERIOD

  // Restore user session on mount from localStorage - with backend validation
  useEffect(() => {
    const restoreSession = async () => {
      const storedUserId = localStorage.getItem('userId');
      const sessionToken = localStorage.getItem('sessionToken');
      const storedEmail = localStorage.getItem('userEmail');
      const storedUsername = localStorage.getItem('username');
      const storedRole = localStorage.getItem('userRole');
      
      console.log('🔍 Session check:', {
        hasUserId: !!storedUserId,
        hasToken: !!sessionToken,
        hasEmail: !!storedEmail,
        storedUserId,
        storedEmail
      });
      
      // Only restore session if we have ALL required data AND a valid token
      if (storedUserId && sessionToken && storedEmail) {
        // Validate token format (basic check - JWT tokens have 3 parts separated by dots)
        const tokenParts = sessionToken.split('.');
        if (tokenParts.length === 3) {
          // SECURITY: Always validate token format and expiration before trusting it
          try {
            // First check token expiration client-side
            const payload = JSON.parse(atob(tokenParts[1]));
            const now = Math.floor(Date.now() / 1000);
            
            if (payload.exp && payload.exp < now) {
              console.log('❌ Token expired, clearing session');
              localStorage.removeItem('sessionToken');
              localStorage.removeItem('userId');
              localStorage.removeItem('userEmail');
              localStorage.removeItem('username');
              localStorage.removeItem('userRole');
              setUser(null);
              setIsAuthenticated(false);
              setInitialized(true);
              return;
            }
            
            // Token format valid and not expired - validate with backend
            // But if backend rejects it (user deleted, etc.), we'll clear it
            const response = await fetch('/api/auth/verify-token', {
              method: 'GET',
              headers: {
                'Authorization': `Bearer ${sessionToken}`,
                'Content-Type': 'application/json'
              }
            });
            
            if (response.ok) {
              const userData = await response.json();
              // Backend validated the token and returned user data
              if (userData.valid && userData.user) {
                const user = {
                  id: userData.user.id || parseInt(storedUserId),
                  user_id: userData.user.id || parseInt(storedUserId),
                  email: userData.user.email || storedEmail,
                  username: userData.user.username || storedUsername || 'user',
                  role: userData.user.role || storedRole || 'user'
                };
                
                console.log('✅ Session restored and validated with backend:', user);
                setUser(user);
                setIsAuthenticated(true);
              } else {
                throw new Error('Invalid token validation response');
              }
            } else {
              // Backend rejected the token - user deleted or token invalid
              console.log('❌ Backend rejected token (user deleted or invalid), clearing session');
              localStorage.removeItem('sessionToken');
              localStorage.removeItem('userId');
              localStorage.removeItem('userEmail');
              localStorage.removeItem('username');
              localStorage.removeItem('userRole');
              setUser(null);
              setIsAuthenticated(false);
            }
          } catch (error) {
            // Any error means token is invalid - clear session
            console.log('❌ Token validation failed, clearing stale session:', error);
            localStorage.removeItem('sessionToken');
            localStorage.removeItem('userId');
            localStorage.removeItem('userEmail');
            localStorage.removeItem('username');
            localStorage.removeItem('userRole');
            setUser(null);
            setIsAuthenticated(false);
          }
        } else {
          // Invalid token format - clear session
          console.log('❌ Invalid token format, clearing session');
          localStorage.removeItem('sessionToken');
          localStorage.removeItem('userId');
          localStorage.removeItem('userEmail');
          localStorage.removeItem('username');
          localStorage.removeItem('userRole');
          setUser(null);
          setIsAuthenticated(false);
        }
      } else {
        console.log('❌ No valid session found, user needs to login');
        setUser(null);
        setIsAuthenticated(false);
      }
      
      // Mark initialization as complete
      setInitialized(true);
    };
    
    restoreSession();
    
    // Listen for logout events from apiClient
    const handleLogout = () => {
      console.log('🔐 Logout event received, clearing session');
      setUser(null);
      setIsAuthenticated(false);
      setInitialized(true);
    };
    
    // Listen for login events (e.g., from email verification auto-login)
    const handleLogin = (event) => {
      console.log('🔐 Login event received, updating session');
      const userData = event.detail;
      if (userData) {
        setUser({
          id: userData.id,
          user_id: userData.id,
          email: userData.email,
          username: userData.username || 'user',
          role: userData.role || 'user'
        });
        setIsAuthenticated(true);
        setInitialized(true);
      }
    };
    
    window.addEventListener('auth:logout', handleLogout);
    window.addEventListener('auth:login', handleLogin);
    
    return () => {
      window.removeEventListener('auth:logout', handleLogout);
      window.removeEventListener('auth:login', handleLogin);
    };
  }, []);

  const login = async (email, password) => {
    try {
      setLoading(true);
      
      // IMPORTANT: Clear any previous session data first
      localStorage.removeItem('sessionToken');
      localStorage.removeItem('userId');
      localStorage.removeItem('userEmail');
      localStorage.removeItem('username');
      localStorage.removeItem('userRole');
      
      // SECURITY: Only authenticate through backend API - NO fallbacks
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
      });
      
      if (!response.ok) {
        // Authentication failed - do not create user or allow access
        throw new Error('Invalid credentials');
      }
      
      const userData = await response.json();
      
      // Only proceed if we have valid user data from backend
      if (!userData.user || !userData.access_token) {
        throw new Error('Invalid response from server');
      }
      
      const user = {
        id: userData.user.id || userData.user_id,
        user_id: userData.user.id || userData.user_id,
        email: userData.user.email,
        username: userData.user.username,
        role: userData.user.role || 'user'
      };
      
      setUser(user);
      setIsAuthenticated(true);
      
      // Store session token and user data
      localStorage.setItem('sessionToken', userData.access_token);
      localStorage.setItem('userId', String(user.id));
      localStorage.setItem('userEmail', user.email);
      localStorage.setItem('username', user.username);
      localStorage.setItem('userRole', user.role);
      
      // Verify token was stored
      const storedToken = localStorage.getItem('sessionToken');
      console.log('🔐 User logged in successfully:', user);
      console.log('🔐 Token stored:', storedToken ? 'YES' : 'NO', storedToken ? `(${storedToken.substring(0, 20)}...)` : '');
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    // Save all user data to database before logout
    if (user) {
      console.log('💾 Saving all user data to database before logout...');
      
      try {
        // Save current preferences to database
        const currentPreferences = localStorage.getItem('edonuops_user_preferences');
        if (currentPreferences) {
          await databaseFirstPersistence.saveUserPreferences(user.id, JSON.parse(currentPreferences));
        }
        
        // Save current modules to database
        const currentModules = localStorage.getItem('edonuops_user_modules');
        if (currentModules) {
          await databaseFirstPersistence.saveUserModules(user.id, JSON.parse(currentModules));
        }
        
        // Save any other user-specific data to database
        const allKeys = Object.keys(localStorage);
        for (const key of allKeys) {
          if (key.startsWith('edonuops_') && !key.includes('user_') && !key.includes('visitor_') && !key.includes('session_') && !key.includes('cache_')) {
            try {
              const data = localStorage.getItem(key);
              if (data) {
                const dataType = key.replace('edonuops_', '');
                await databaseFirstPersistence.saveUserData(user.id, dataType, JSON.parse(data));
              }
            } catch (error) {
              console.warn(`Could not save data for key ${key}:`, error);
            }
          }
        }
        
        console.log('✅ All user data saved to database before logout');
      } catch (error) {
        console.error('❌ Error saving data to database:', error);
      }
    }
    
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('user');
    
    console.log('🔐 User logged out');
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      loading,
      initialized,
      login,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
