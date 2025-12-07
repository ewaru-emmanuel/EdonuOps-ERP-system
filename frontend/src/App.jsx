import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { CurrencyProvider, useCurrency } from './components/GlobalCurrencySettings';
import { TenantProvider } from './contexts/TenantContext';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  useMediaQuery,
  useTheme,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Snackbar,
  Alert,
  Tooltip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountBalance as FinanceIcon,
  People as CRMIcon,
  Inventory as InventoryIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  ShoppingCart,
  AdminPanelSettings as AdminPanelSettingsIcon,
  Email as EmailIcon,
  // Finance module icons
  Assessment as AssessmentIcon,
  Receipt as ReceiptIcon,
  Payment as PaymentIcon,
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  Receipt as TaxIcon,
  AccountBalanceWallet as BankIcon,
  BarChart as BarChartIcon,
  Security as SecurityIcon,
  Edit as EditIcon,
  AccountBalance as BalanceIcon,
  Create as CreateIcon,
  // CRM module icons
  People as PeopleIcon,
  Timeline as TimelineIcon,
  Assignment as AssignmentIcon,
  Support as SupportIcon,
  AutoAwesome as AutoAwesomeIcon,
  School as SchoolIcon,
  DataObject as DataObjectIcon,
  // Procurement module icons
  Description as DescriptionIcon,
  Close as CloseIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon
} from '@mui/icons-material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';
import MailOutlineIcon from '@mui/icons-material/MailOutline';
import AttachmentIcon from '@mui/icons-material/Attachment';

// Import components
import Dashboard from './components/Dashboard';
import LandingPage from './components/LandingPage';
import OnboardingWizard from './components/OnboardingWizard';
import Login from './pages/Login';
import EnhancedRegister from './pages/EnhancedRegister';
import DashboardSettings from './modules/erp/dashboard/DashboardSettings';
import AdminSettings from './modules/erp/admin/AdminSettings';
import NotificationsCenter from './components/NotificationsCenter';
import FinanceModule from './modules/finance/FinanceModule';
import CRMModule from './modules/crm/CRMModule';
import CoreInventoryModule from './modules/inventory/CoreInventoryModule';
import ProcurementModule from './modules/erp/procurement/ProcurementModule';
import BreadcrumbNavigation from './components/BreadcrumbNavigation';
import UserProfile from './pages/UserProfile';
import TopNav from './components/TopNav';

// Import centralized API client
import apiClient from './services/apiClient';

// Import permissions system
import { PermissionsProvider, usePermissions } from './hooks/usePermissions';
import SimpleProtectedRoute from './components/SimpleProtectedRoute';
import InvitationManagementPage from './modules/admin/InvitationManagementPage';
import InvitationRegistration from './pages/InvitationRegistration';
import EmailVerification from './pages/EmailVerification';
import PasswordReset from './pages/PasswordReset';

// Import auth context
import { AuthProvider as SimpleAuthProvider, useAuth } from './context/AuthContext';

// Simple approach - no complex hooks needed
console.log('🔍 Using simple direct API approach for sidebar');

// Add manual refresh function for testing
if (typeof window !== 'undefined') {
  window.refreshSidebar = () => {
    console.log('🔄 Manually refreshing sidebar...');
    window.dispatchEvent(new CustomEvent('modulesUpdated'));
  };
}

// Add simple test function to window
if (typeof window !== 'undefined') {
  window.testSidebarIssue = async () => {
    console.log('🧪 Testing sidebar issue...');
    
    // Test 1: Check if we can call the API directly
    try {
      const response = await fetch('http://localhost:5000/api/dashboard/modules/user', {
        headers: {
          'X-User-ID': '3',
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      console.log('🧪 Direct API test:', data);
    } catch (error) {
      console.error('🧪 Direct API test failed:', error);
    }
    
    // Test 2: Check localStorage
    console.log('🧪 localStorage check:', {
      userId: localStorage.getItem('userId'),
      userEmail: localStorage.getItem('userEmail'),
      userRole: localStorage.getItem('userRole')
    });
    
    // Test 3: Check if hook is available
    console.log('🧪 Hook availability:', typeof useUserPreferences);
    
    // Test 4: Check authentication context
    console.log('🧪 Auth context check:', {
      hasAuthProvider: typeof SimpleAuthProvider !== 'undefined',
      hasUseAuth: typeof useAuth !== 'undefined'
    });
  };
}



// App Content Component (inside Router)
const AppContent = () => {
  console.log('🚨 AppContent component is being rendered!');
  
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [sidebarOpen, setSidebarOpen] = useState(false); // Collapsed by default for hover behavior
  
  // Hide navigation on public pages (landing, login, register)
  // Show navigation only on authenticated pages
  const isPublicPage = location.pathname === '/' || 
                      location.pathname === '/login' || 
                      location.pathname === '/register' ||
                      location.pathname === '/verify-email';
  
  const hideNavigation = isPublicPage;
  
  return (
    <Box>
      <Box
        component="main"
        sx={{
          p: { xs: 2, md: location.pathname.startsWith('/finance') ? 0 : 3 },
          mt: hideNavigation ? 0 : ((location.pathname === '/onboarding' || location.pathname === '/verify-email') ? 0 : { xs: 7, md: 8 }),
          minHeight: '100vh',
          backgroundColor: (location.pathname === '/onboarding' || location.pathname === '/verify-email') ? 'transparent' : '#fafafa',
          width: hideNavigation ? '100%' : { xs: '100%', md: 'calc(100% - 72px)' },
          maxWidth: hideNavigation ? '100%' : { xs: '100%', md: 'calc(100% - 72px)' },
          marginLeft: hideNavigation ? 0 : { xs: 0, md: '72px' },
          marginRight: 0,
          paddingLeft: 0,
          transition: theme.transitions.create(['width', 'margin-left'], {
            easing: theme.transitions.easing.easeInOut,
            duration: theme.transitions.duration.standard,
          }),
        }}
      >
        <Routes>
          {/* Public routes - accessible without login */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<EnhancedRegister />} />
          <Route path="/register/invite" element={<InvitationRegistration />} />
          <Route path="/verify-email" element={<EmailVerification />} />
          <Route path="/reset-password" element={<PasswordReset />} />
          
          {/* All routes - simple lock: if logged in show, if not show login */}
          <Route path="/onboarding" element={<SimpleProtectedRoute><OnboardingWizard /></SimpleProtectedRoute>} />
          <Route path="/admin/invitations" element={<SimpleProtectedRoute><InvitationManagementPage /></SimpleProtectedRoute>} />
          <Route path="/dashboard" element={<SimpleProtectedRoute><Dashboard /></SimpleProtectedRoute>} />
          <Route path="/dashboard/settings" element={<SimpleProtectedRoute><DashboardSettings /></SimpleProtectedRoute>} />
          <Route path="/admin/settings" element={<SimpleProtectedRoute><AdminSettings /></SimpleProtectedRoute>} />
          <Route path="/notifications" element={<SimpleProtectedRoute><NotificationsCenter /></SimpleProtectedRoute>} />
          <Route path="/finance" element={<SimpleProtectedRoute><FinanceModule /></SimpleProtectedRoute>} />
          <Route path="/crm" element={<SimpleProtectedRoute><CRMModule /></SimpleProtectedRoute>} />
          <Route path="/procurement" element={<SimpleProtectedRoute><ProcurementModule /></SimpleProtectedRoute>} />
          <Route path="/inventory" element={<SimpleProtectedRoute><CoreInventoryModule /></SimpleProtectedRoute>} />
          <Route path="/profile" element={<SimpleProtectedRoute><UserProfile /></SimpleProtectedRoute>} />
          
          {/* Catch-all route - redirect to login for any unknown routes */}
          <Route path="*" element={<SimpleProtectedRoute><LandingPage /></SimpleProtectedRoute>} />
        </Routes>
        </Box>
      {!hideNavigation && <Navigation sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />}
      {!hideNavigation && <TopNav variant="authenticated" sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />}
    </Box>
  );
};

// Navigation Component
const Navigation = ({ sidebarOpen, setSidebarOpen }) => {
  console.log('🚨 Navigation component is being rendered!');
  
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  console.log('🚨 Navigation component is rendering...');
  
  const { logout: authLogout, user } = useAuth();
  
  // Simple approach: Get user modules directly from API
  const [userModules, setUserModules] = useState([]);
  const [modulesLoading, setModulesLoading] = useState(true);
  
  // Fetch user modules on component mount and when modules change
  const fetchUserModules = async () => {
    // Only fetch if user is authenticated
    if (!user || !user.id) {
      console.log('⚠️ [SIDEBAR] No user authenticated, skipping module fetch');
      setModulesLoading(false);
      setUserModules([]);
      return;
    }
    
    try {
      console.log('🔍 [SIDEBAR] Fetching user modules for user:', user.id);
      setModulesLoading(true);
      
      // Use apiClient which handles proxy and authentication
      const modules = await apiClient.get('/api/dashboard/modules/user');
      
      console.log('📦 [SIDEBAR] Raw API response:', modules);
      console.log('📦 [SIDEBAR] Response type:', typeof modules);
      console.log('📦 [SIDEBAR] Is array:', Array.isArray(modules));
      console.log('📦 [SIDEBAR] Response length:', Array.isArray(modules) ? modules.length : 'N/A');
      
      if (Array.isArray(modules)) {
        const moduleIds = modules.map(m => m.id || m.module_id).filter(Boolean);
        console.log('✅ [SIDEBAR] User modules fetched successfully:', moduleIds);
        console.log('📊 [SIDEBAR] Module details:', modules.map(m => ({
          id: m.id || m.module_id,
          name: m.name,
          is_active: m.is_active,
          is_enabled: m.is_enabled
        })));
        setUserModules(moduleIds);
      } else {
        console.warn('⚠️ [SIDEBAR] Unexpected response format, expected array:', modules);
        setUserModules([]);
      }
      setModulesLoading(false);
    } catch (error) {
      console.error('❌ [SIDEBAR] Error fetching user modules:', error);
      console.error('❌ [SIDEBAR] Error details:', {
        message: error.message,
        stack: error.stack
      });
      // On error, set empty array so UI doesn't break
      setUserModules([]);
      setModulesLoading(false);
    }
  };

  useEffect(() => {
    // Only fetch modules when user is authenticated
    if (user && user.id) {
      console.log('🔄 [SIDEBAR] User available, fetching modules...', user.id);
      fetchUserModules();
    } else {
      console.log('⚠️ [SIDEBAR] No user available yet');
      setModulesLoading(false);
      setUserModules([]);
    }
  }, [user?.id]); // Depend on user.id specifically

  // Listen for module changes (when user completes onboarding)
  useEffect(() => {
    const handleModuleChange = () => {
      console.log('🔄 [SIDEBAR] Module change event detected, refreshing sidebar...');
      if (user && user.id) {
        fetchUserModules();
      }
    };

    // Listen for custom events
    window.addEventListener('modulesUpdated', handleModuleChange);
    window.addEventListener('onboardingCompleted', handleModuleChange);

    return () => {
      window.removeEventListener('modulesUpdated', handleModuleChange);
      window.removeEventListener('onboardingCompleted', handleModuleChange);
    };
  }, [user?.id]); // Include user.id in dependencies
  
  console.log('🎯 Simple sidebar - user modules:', userModules);
  
  // Use permissions hook
  const { hasModuleAccess, loading: permissionsLoading } = usePermissions();


  // Define all navigation links with their module IDs and required permissions
  const allNavLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: <DashboardIcon />, moduleId: 'dashboard', requiredModule: 'dashboard' },
    { name: 'Finance', path: '/finance', icon: <FinanceIcon />, moduleId: 'finance', requiredModule: 'finance' },
    { name: 'CRM', path: '/crm', icon: <CRMIcon />, moduleId: 'crm', requiredModule: 'crm' },
    { name: 'Procurement', path: '/procurement', icon: <ShoppingCart />, moduleId: 'procurement', requiredModule: 'procurement' },
    { name: ' Inventory', path: '/inventory', icon: <InventoryIcon />, moduleId: 'inventory', requiredModule: 'inventory' },
    { name: 'Invitations', path: '/admin/invitations', icon: <EmailIcon />, moduleId: 'admin', requiredModule: 'admin' }
  ];

  // Define Finance module features
  const financeFeatures = [
    { name: 'Dashboard', path: '/finance?feature=dashboard', icon: <AssessmentIcon />, featureId: 'dashboard' },
    { name: 'General Ledger', path: '/finance?feature=general-ledger', icon: <FinanceIcon />, featureId: 'general-ledger' },
    { name: 'Chart of Accounts', path: '/finance?feature=chart-of-accounts', icon: <BusinessIcon />, featureId: 'chart-of-accounts' },
    { name: 'Accounts Payable', path: '/finance?feature=accounts-payable', icon: <PaymentIcon />, featureId: 'accounts-payable' },
    { name: 'Accounts Receivable', path: '/finance?feature=accounts-receivable', icon: <ReceiptIcon />, featureId: 'accounts-receivable' },
    { name: 'Fixed Assets', path: '/finance?feature=fixed-assets', icon: <BusinessIcon />, featureId: 'fixed-assets' },
    { name: 'Budgeting', path: '/finance?feature=budgeting', icon: <TrendingUpIcon />, featureId: 'budgeting' },
    { name: 'Tax Management', path: '/finance?feature=tax-management', icon: <TaxIcon />, featureId: 'tax-management' },
    { name: 'Bank Reconciliation', path: '/finance?feature=bank-reconciliation', icon: <BankIcon />, featureId: 'bank-reconciliation' },
    { name: 'Financial Reports', path: '/finance?feature=financial-reports', icon: <BarChartIcon />, featureId: 'financial-reports' },
    { name: 'Audit Trail', path: '/finance?feature=audit-trail', icon: <SecurityIcon />, featureId: 'audit-trail' }
  ];

  // Define CRM module features
  const crmFeatures = [
    { name: 'Contacts', path: '/crm?feature=contacts', icon: <PersonIcon />, featureId: 'contacts' },
    { name: 'Leads', path: '/crm?feature=leads', icon: <PeopleIcon />, featureId: 'leads' },
    { name: 'Opportunities', path: '/crm?feature=opportunities', icon: <TrendingUpIcon />, featureId: 'opportunities' },
    { name: 'Pipeline', path: '/crm?feature=pipeline', icon: <TimelineIcon />, featureId: 'pipeline' },
    { name: 'Companies', path: '/crm?feature=companies', icon: <BusinessIcon />, featureId: 'companies' },
    { name: 'Activities', path: '/crm?feature=activities', icon: <AssignmentIcon />, featureId: 'activities' },
    { name: 'Tasks', path: '/crm?feature=tasks', icon: <AssignmentIcon />, featureId: 'tasks' },
    { name: 'Tickets', path: '/crm?feature=tickets', icon: <SupportIcon />, featureId: 'tickets' },
    { name: 'Reports', path: '/crm?feature=reports', icon: <BarChartIcon />, featureId: 'reports' },
    { name: 'Automations', path: '/crm?feature=automations', icon: <AutoAwesomeIcon />, featureId: 'automations' },
    { name: 'Knowledge Base', path: '/crm?feature=knowledge-base', icon: <SchoolIcon />, featureId: 'knowledge-base' },
    { name: 'Data Quality', path: '/crm?feature=data-quality', icon: <DataObjectIcon />, featureId: 'data-quality' }
  ];

  // Define Inventory module features
  const inventoryFeatures = [
    { name: 'Dashboard', path: '/inventory?feature=dashboard', icon: <DashboardIcon />, featureId: 'dashboard' },
    { name: 'Products', path: '/inventory?feature=products', icon: <InventoryIcon />, featureId: 'products' },
    { name: 'Stock Levels', path: '/inventory?feature=stock-levels', icon: <AssessmentIcon />, featureId: 'stock-levels' },
    { name: 'Adjustments', path: '/inventory?feature=adjustments', icon: <SettingsIcon />, featureId: 'adjustments' },
    { name: 'Transfers', path: '/inventory?feature=transfers', icon: <TrendingUpIcon />, featureId: 'transfers' },
    { name: 'Reports', path: '/inventory?feature=reports', icon: <BarChartIcon />, featureId: 'reports' },
    { name: 'Settings', path: '/inventory?feature=settings', icon: <SettingsIcon />, featureId: 'settings' }
  ];

  // Define Procurement module features
  const procurementFeatures = [
    { name: 'Dashboard', path: '/procurement?feature=dashboard', icon: <ShoppingCart />, featureId: 'dashboard' },
    { name: 'Vendors', path: '/procurement?feature=vendors', icon: <BusinessIcon />, featureId: 'vendors' },
    { name: 'Purchase Orders', path: '/procurement?feature=purchase-orders', icon: <DescriptionIcon />, featureId: 'purchase-orders' },
    { name: 'RFQ Management', path: '/procurement?feature=rfq', icon: <BusinessIcon />, featureId: 'rfq' },
    { name: 'Contracts', path: '/procurement?feature=contracts', icon: <BusinessIcon />, featureId: 'contracts' },
    { name: 'Analytics', path: '/procurement?feature=analytics', icon: <BarChartIcon />, featureId: 'analytics' }
  ];

  // Simple approach: Show modules that user has activated
  console.log('🔗 Simple sidebar filtering - user modules:', userModules);
  
  // STRICT FILTERING: Only show modules that user has ACTIVATED in database
  // User isolation is KEY - no fallbacks, no permissions override
  const navLinks = allNavLinks.filter(link => {
    // Always show dashboard (not a module, just navigation)
    if (link.moduleId === 'dashboard') {
      console.log(`🔗 Filter: ${link.moduleId} - SHOW (always visible)`);
      return true;
    }
    
    // STRICT: Only show if module is in user's activated modules list from database
    const isActivated = userModules.includes(link.moduleId);
    
    if (isActivated) {
      console.log(`✅ Filter: ${link.moduleId} - SHOW (activated in database)`);
      return true;
    } else {
      console.log(`❌ Filter: ${link.moduleId} - HIDE (not activated by user)`);
      return false; // STRICT: No fallbacks, no permission overrides
    }
  });
  
  // Debug: Log sidebar rendering
  console.log('🔗 Simple sidebar rendering:', {
    totalLinks: allNavLinks.length,
    filteredLinks: navLinks.length,
    userModules,
    navLinks: navLinks.map(link => link.name)
  });
  
  // Debug: Log allNavLinks array
  console.log('🔗 allNavLinks array:', allNavLinks.map(link => ({ name: link.name, moduleId: link.moduleId, path: link.path })));


  // Determine which navigation items to show based on current path
  const getCurrentNavigationItems = () => {
    // If on a specific module page, show module features
    if (location.pathname.startsWith('/finance')) {
      // Only show finance features if finance module is activated
      if (userModules.includes('finance')) {
        return financeFeatures;
      }
      return navLinks; // Fallback to main nav if module not activated
    }
    if (location.pathname.startsWith('/crm')) {
      if (userModules.includes('crm')) {
        return crmFeatures;
      }
      return navLinks;
    }
    if (location.pathname.startsWith('/inventory')) {
      if (userModules.includes('inventory')) {
        return inventoryFeatures;
      }
      return navLinks;
    }
    if (location.pathname.startsWith('/procurement')) {
      if (userModules.includes('procurement')) {
        return procurementFeatures;
      }
      return navLinks;
    }
    // For dashboard and other pages, show enabled modules (main navigation)
    return navLinks;
  };

  const currentNavItems = getCurrentNavigationItems();
  
  console.log('🎯 [SIDEBAR] Current navigation items:', {
    path: location.pathname,
    navLinksCount: navLinks.length,
    navLinks: navLinks.map(l => l.name),
    currentNavItemsCount: currentNavItems.length,
    currentNavItems: currentNavItems.map(l => l.name || l.title)
  });



  // Auto-close sidebar on mobile when route changes
  useEffect(() => {
    if (isMobile && sidebarOpen) {
      setSidebarOpen(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]); // Only close when route changes

  // Sidebar stays collapsed by default on desktop (hover to expand)
  // No auto-open on desktop - user hovers to expand


  const drawer = (
    <Box sx={{ 
      width: isMobile ? 280 : (sidebarOpen ? 240 : 72),
      display: 'flex',
      flexDirection: 'column',
      height: isMobile ? '100vh' : 'calc(100vh - 64px)',
      backgroundColor: '#ffffff'
    }}>
      
      {/* YouTube-style header - minimal, clean */}
      {(isMobile || sidebarOpen) && (
        <Box sx={{ 
          px: 2.5,
          py: 2,
          borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
          backgroundColor: '#ffffff'
        }}>
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 500,
              color: '#1a1a1a',
              fontSize: '0.875rem',
              letterSpacing: '0.01em',
              lineHeight: 1.4
            }}
          >
            {location.pathname.startsWith('/finance') ? 'Finance' : 'EdonuOps'}
          </Typography>
        </Box>
      )}
      
      {/* Collapsed state - minimal icon */}
      {!sidebarOpen && !isMobile && (
        <Box sx={{ 
          px: 1.5,
          py: 2,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
          minHeight: 56
        }}>
          <Box
            sx={{
              width: 28,
              height: 28,
              borderRadius: '50%',
              backgroundColor: '#1976d2',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              fontWeight: 600,
              fontSize: '0.8125rem',
              boxShadow: '0 1px 3px rgba(0,0,0,0.12)'
            }}
          >
            E
          </Box>
        </Box>
      )}
      
      {/* Mobile close button - only on mobile */}
      {isMobile && (
        <Box sx={{ 
          position: 'absolute', 
          top: 8, 
          right: 8,
          zIndex: 1
        }}>
          <IconButton 
            onClick={() => setSidebarOpen(false)}
            sx={{ 
              color: '#5f6368',
              backgroundColor: 'rgba(0,0,0,0.04)',
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.08)',
              }
            }}
            size="small"
          >
            <CloseIcon />
          </IconButton>
        </Box>
      )}

      {/* Breadcrumb Navigation */}
      <BreadcrumbNavigation sidebarOpen={sidebarOpen} />

      {/* YouTube-style navigation - clean and minimal */}
      <Box sx={{ flexGrow: 1, overflow: 'auto', pt: 0.5, pb: 0.5 }}>
        <List sx={{ px: 0, py: 0.5 }}>
          {currentNavItems.map((link) => {
            const isSelected = link.featureId ? 
              ((location.pathname.startsWith('/finance') && searchParams.get('feature') === link.featureId) ||
               (location.pathname.startsWith('/crm') && searchParams.get('feature') === link.featureId) ||
               (location.pathname.startsWith('/inventory') && searchParams.get('feature') === link.featureId) ||
               (location.pathname.startsWith('/procurement') && searchParams.get('feature') === link.featureId)) :
              (location.pathname === link.path);
            
            return (
              <ListItem key={link.name} disablePadding>
                <Tooltip 
                  title={sidebarOpen ? '' : link.name} 
                  placement="right" 
                  arrow
                  disableHoverListener={sidebarOpen || isMobile}
                >
                  <ListItem
                    component={Link}
                    to={link.path}
                    onClick={() => {
                      if (isMobile && sidebarOpen) {
                        setSidebarOpen(false);
                      }
                    }}
                    selected={isSelected}
                    sx={{
                      minHeight: 44,
                      height: 44,
                      px: sidebarOpen ? 2.5 : 1.5,
                      py: 0,
                      mx: 0.5,
                      my: 0.25,
                      backgroundColor: isSelected ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
                      borderRadius: sidebarOpen ? '8px' : '12px',
                      width: sidebarOpen ? 'calc(100% - 8px)' : 'calc(100% - 12px)',
                      justifyContent: sidebarOpen ? 'flex-start' : 'center',
                      transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                      borderLeft: isSelected && sidebarOpen ? '3px solid #1976d2' : '3px solid transparent',
                      '&.Mui-selected': {
                        backgroundColor: 'rgba(25, 118, 210, 0.08)',
                        '&:hover': {
                          backgroundColor: 'rgba(25, 118, 210, 0.12)',
                        },
                        '& .MuiListItemIcon-root': {
                          color: '#1976d2',
                        },
                        '& .MuiTypography-root': {
                          color: '#1976d2',
                          fontWeight: 500,
                        }
                      },
                      '&:hover': {
                        backgroundColor: sidebarOpen ? 'rgba(0, 0, 0, 0.04)' : 'rgba(0, 0, 0, 0.06)',
                      }
                    }}
                  >
                    <ListItemIcon
                      sx={{
                        minWidth: sidebarOpen ? 28 : 28,
                        color: isSelected ? '#1976d2' : '#5f6368',
                        justifyContent: 'center',
                        transition: 'color 0.2s ease',
                        mr: sidebarOpen ? 1.75 : 0,
                        fontSize: '1.375rem',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      {link.icon}
                    </ListItemIcon>
                    
                    {sidebarOpen && (
                      <ListItemText
                        primary={
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              fontWeight: isSelected ? 500 : 400,
                              color: isSelected ? '#1976d2' : '#3c4043',
                              fontSize: '0.875rem',
                              lineHeight: 1.5,
                              letterSpacing: '0.01em'
                            }}
                          >
                            {link.name}
                          </Typography>
                        }
                      />
                    )}
                  </ListItem>
                </Tooltip>
              </ListItem>
            );
          })}
        </List>
      </Box>

      {/* YouTube-style footer - minimal */}
      {sidebarOpen && !isMobile && (
        <Box sx={{ 
          px: 2.5,
          py: 2, 
          borderTop: '1px solid rgba(0, 0, 0, 0.08)',
          mt: 'auto',
          backgroundColor: '#ffffff'
        }}>
          <Typography 
            variant="caption" 
            sx={{ 
              color: '#5f6368',
              fontSize: '0.75rem',
              fontWeight: 400,
              letterSpacing: '0.01em',
              lineHeight: 1.4
            }}
          >
            Simple ERP Platform
          </Typography>
        </Box>
      )}
    </Box>
  );


  return (
    <>

      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? sidebarOpen : true}
        onClose={() => {
          if (isMobile) {
            setSidebarOpen(false);
          }
        }}
        onMouseEnter={() => {
          if (!isMobile) {
            setSidebarOpen(true);
          }
        }}
        onMouseLeave={() => {
          if (!isMobile) {
            setSidebarOpen(false);
          }
        }}
        anchor="left"
        ModalProps={{
          keepMounted: true,
          disableEnforceFocus: false,
          disableAutoFocus: false,
        }}
        BackdropProps={{
          invisible: false,
        }}
        sx={{
          width: isMobile ? 280 : (sidebarOpen ? 240 : 72),
          flexShrink: 0,
          zIndex: isMobile ? theme.zIndex.modal : (theme.zIndex.drawer - 1),
          '& .MuiDrawer-paper': {
            width: isMobile ? 280 : (sidebarOpen ? 240 : 72),
            boxSizing: 'border-box',
            top: isMobile ? 0 : 64,
            height: isMobile ? '100vh' : 'calc(100vh - 64px)',
            minHeight: isMobile ? '100vh' : 'calc(100vh - 64px)',
            maxHeight: isMobile ? '100vh' : 'calc(100vh - 64px)',
            zIndex: isMobile ? (theme.zIndex.modal + 1) : (theme.zIndex.drawer - 1),
            position: 'fixed',
            left: 0,
            right: 'auto',
            margin: 0,
            padding: 0,
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
            overflowX: 'hidden',
            overflowY: 'auto',
            borderRight: '1px solid rgba(0, 0, 0, 0.08)',
            borderLeft: 'none',
            backgroundColor: '#ffffff',
            boxShadow: isMobile ? theme.shadows[8] : '0 1px 2px rgba(0,0,0,0.04)'
          },
        }}
      >
        {drawer}
      </Drawer>

    </>
  );
};

// Main App Component
const App = () => {
  const [mode, setMode] = useState('light');
  const toggleMode = () => setMode(prev => (prev === 'light' ? 'dark' : 'light'));
  const [viewportSize, setViewportSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768
  });
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const onResize = () => setViewportSize({ width: window.innerWidth, height: window.innerHeight });
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);
  const tooSmall = viewportSize.width < 280 || viewportSize.height < 300;
  const theme = createTheme({
    palette: {
      mode,
      primary: { main: '#1976d2' },
      secondary: { main: '#dc004e' },
    },
    components: {
      MuiModal: {
        styleOverrides: {
          root: {
            '& .MuiBackdrop-root': {
              // Remove aria-hidden from backdrop to fix accessibility issue
              ariaHidden: 'false',
            },
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          root: {
            '& .MuiBackdrop-root': {
              // Remove aria-hidden from backdrop to fix accessibility issue
              ariaHidden: 'false',
            },
          },
        },
      },
      MuiDialog: {
        styleOverrides: {
          root: {
            '& .MuiBackdrop-root': {
              // Ensure backdrop doesn't interfere with focus
              ariaHidden: 'false',
            },
            // Prevent focus trapping issues
            '& .MuiDialog-container': {
              '& .MuiPaper-root': {
                // Ensure dialog content is properly accessible
                ariaModal: 'true',
              },
            },
          },
        },
        defaultProps: {
          // Use keepMounted to prevent focus issues
          keepMounted: false,
        },
      },
    },
  });

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {tooSmall ? (
        <Box sx={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center', p: 3, textAlign: 'center' }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 1 }}>
              Screen too small
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Please use a device with a minimum display size of 280 × 300 pixels to access EdonuOps.
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              For the best experience, use a tablet, laptop, or desktop.
            </Typography>
          </Box>
        </Box>
      ) : (
        <CurrencyProvider>
          <TenantProvider>
            <SimpleAuthProvider>
              <PermissionsProvider>
                <Router>
                  <AppContent mode={mode} toggleMode={toggleMode} />
                </Router>
              </PermissionsProvider>
            </SimpleAuthProvider>
          </TenantProvider>
        </CurrencyProvider>
      )}
    </ThemeProvider>
  );
};

export default App;
