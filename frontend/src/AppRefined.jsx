import React, { useState, createContext, useContext, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { CurrencyProvider, useCurrency } from './components/GlobalCurrencySettings';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box
} from '@mui/material';

// Import refined components
import RefinedLayout from './components/RefinedLayout';

// Import page components
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import DashboardSettings from './modules/erp/dashboard/DashboardSettings';
import AdminSettings from './modules/erp/admin/AdminSettings';
import NotificationsCenter from './components/NotificationsCenter';
import FinanceModule from './modules/finance/FinanceModule';
import CRMModule from './modules/crm/CRMModule';
import { CRMProvider } from './modules/crm/context/CRMContext';
import CoreInventoryModule from './modules/inventory/CoreInventoryModule';
import ProcurementModule from './modules/erp/procurement/ProcurementModule';
import OnboardingWizard from './components/OnboardingWizard';

// Import API service
import { initializeERPApiService } from './services/erpApiService';
import apiClient from './services/apiClient';
import { useUserPreferences } from './hooks/useUserPreferences';

// Create Auth Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user] = useState({
    id: 1,
    name: 'John Doe',
    email: 'admin@edonuops.com',
    role: 'Administrator',
    avatar: null
  });

  const [isAuthenticated, setIsAuthenticated] = useState(true);

  // Initialize the ERP API service with the apiClient
  useEffect(() => {
    initializeERPApiService(apiClient);
  }, []);

  const login = (email, password) => {
    // Simple authentication logic
    if (email && password) {
      setIsAuthenticated(true);
      return true;
    }
    return false;
  };

  const logout = () => {
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

// Main App Content Component
const AppContent = () => {
  const { user, logout } = useAuth();
  const { selectedModules } = useUserPreferences();
  const navigate = useNavigate();

  // Check if user has completed onboarding
  const hasCompletedOnboarding = selectedModules && selectedModules.length > 0;

  // If user hasn't completed onboarding, show the wizard
  if (!hasCompletedOnboarding) {
    return <OnboardingWizard />;
  }

  return (
    <RefinedLayout user={user} onLogout={logout}>
      <Routes>
        {/* Landing Page */}
        <Route path="/" element={<LandingPage />} />
        
        {/* Dashboard */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/dashboard/settings" element={<DashboardSettings />} />
        
        {/* Admin Settings */}
        <Route path="/admin/settings" element={<AdminSettings />} />
        
        {/* Notifications */}
        <Route path="/notifications" element={<NotificationsCenter />} />
        
        {/* CRM Module */}
        <Route 
          path="/crm/*" 
          element={
            <CRMProvider>
              <CRMModule />
            </CRMProvider>
          } 
        />
        
        {/* Finance Module */}
        <Route path="/finance/*" element={<FinanceModule />} />
        
        {/* Inventory Module */}
        <Route path="/inventory/*" element={<CoreInventoryModule />} />
        
        {/* Procurement Module */}
        <Route path="/procurement/*" element={<ProcurementModule />} />
        
        {/* Fallback to Dashboard */}
        <Route path="*" element={<Dashboard />} />
      </Routes>
    </RefinedLayout>
  );
};

// Main App Component
const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <CurrencyProvider>
        <AuthProvider>
          <Router>
            <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
              <AppContent />
            </Box>
          </Router>
        </AuthProvider>
      </CurrencyProvider>
    </ThemeProvider>
  );
};

export default App;




