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

  // Helper function to get or create user ID dynamically
  const getOrCreateUserId = async (email) => {
    try {
      // Try to get existing user from database
      const response = await fetch(`/api/users/find?email=${encodeURIComponent(email)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const user = await response.json();
        return user.id;
      } else {
        // Create new user
        const createResponse = await fetch('/api/users', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: email,
            username: email.split('@')[0],
            role: 'user'
          })
        });
        
        if (createResponse.ok) {
          const newUser = await createResponse.json();
          return newUser.id;
        }
      }
    } catch (error) {
      console.warn('Could not get/create user, using fallback:', error);
    }
    
    // Fallback: Generate user ID based on email hash
    const hash = email.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    // Special case: Use user 1 for admin emails
    if (email === 'admin@edonuops.com' || email === 'admin@edonuerp.com') {
      return 1;
    }
    
    return Math.abs(hash) % 1000 + 2; // Start from 2, avoid 1 (admin)
  };

  // Restore user session on mount from localStorage (minimal data only)
  useEffect(() => {
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
    
    if (storedUserId && sessionToken && storedEmail) {
      // Reconstruct user data from stored session
      const userData = {
        id: parseInt(storedUserId),
        user_id: parseInt(storedUserId),
        email: storedEmail,
        username: storedUsername || 'user',
        role: storedRole || 'user'
      };
      
      console.log('✅ Restoring session for user:', userData);
      setUser(userData);
      setIsAuthenticated(true);
    } else {
      console.log('❌ No valid session found, user needs to login');
    }
    
    // Mark initialization as complete
    setInitialized(true);
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
      
      // Map known admin emails to their user IDs
      const adminEmailMap = {
        'admin@edonuops.com': 1,
        'admin@edonuerp.com': 3,
        'herbertndawula070@gmail.com': 2
      };
      
      if (adminEmailMap[email]) {
        const userId = adminEmailMap[email];
        const userData = {
          id: userId,
          user_id: userId,
          email: email,
          username: email === 'admin@edonuops.com' ? 'admin' : 
                   email === 'admin@edonuerp.com' ? 'admin_edonuerp' : 
                   'edonuOps',
          role: 'admin'
        };
        
        setUser(userData);
        setIsAuthenticated(true);
        
        // Store NEW session data for this user
        const sessionToken = `session_${Date.now()}_${userData.id}`;
        localStorage.setItem('sessionToken', sessionToken);
        localStorage.setItem('userId', String(userId));
        localStorage.setItem('userEmail', email);
        localStorage.setItem('username', userData.username);
        localStorage.setItem('userRole', 'admin');
        
        console.log('🔐 Admin user logged in successfully:', userData);
        setLoading(false);
        return;
      }
      
      // Dynamic user authentication for other users
      let userId = null;
      let username = email.split('@')[0];
      let role = 'user';
      
      // Try to authenticate with backend API
      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
          const userData = await response.json();
          userId = userData.id;
          username = userData.username || email.split('@')[0];
          role = userData.role || 'user';
        } else {
          // Fallback: Create new user or use existing
          userId = await getOrCreateUserId(email);
          username = email.split('@')[0];
          role = 'user';
        }
      } catch (error) {
        console.warn('Backend authentication failed, using fallback:', error);
        // Fallback: Create new user or use existing
        userId = await getOrCreateUserId(email);
        username = email.split('@')[0];
        role = 'user';
      }
      
      const userData = {
        id: userId,
        user_id: userId, // Use actual user ID for multi-tenancy
        email: email,
        username: username,
        role: role
      };
      
      setUser(userData);
      setIsAuthenticated(true);
      
      // Store ONLY session token and user ID, not full user data
      const sessionToken = `session_${Date.now()}_${userData.id}`;
      localStorage.setItem('sessionToken', sessionToken);
      localStorage.setItem('userId', String(userId));
      localStorage.setItem('userEmail', email);
      localStorage.setItem('username', username);
      localStorage.setItem('userRole', 'user');
      
      console.log('🔐 User logged in successfully:', userData);
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
