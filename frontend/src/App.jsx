import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { CurrencyProvider, useCurrency } from './components/GlobalCurrencySettings';
import { TenantProvider } from './contexts/TenantContext';
import TenantSwitcher from './components/TenantSwitcher';
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
  Menu as MenuIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  ShoppingCart,
  AdminPanelSettings as AdminPanelSettingsIcon,
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
  // CRM module icons
  People as PeopleIcon,
  Timeline as TimelineIcon,
  Assignment as AssignmentIcon,
  Support as SupportIcon,
  AutoAwesome as AutoAwesomeIcon,
  School as SchoolIcon,
  DataObject as DataObjectIcon,
  // Procurement module icons
  Description as DescriptionIcon
} from '@mui/icons-material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';
import MailOutlineIcon from '@mui/icons-material/MailOutline';
import AttachmentIcon from '@mui/icons-material/Attachment';

// Import components
import Dashboard from './components/Dashboard';
import LandingPage from './components/LandingPage';
import OnboardingWizard from './components/OnboardingWizard';
import SimpleLogin from './components/SimpleLogin';
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

// Import centralized API client
import apiClient from './services/apiClient';

// Import permissions system
import { PermissionsProvider, usePermissions } from './hooks/usePermissions';
import SimpleProtectedRoute from './components/SimpleProtectedRoute';

// Import user preferences hook
import { useUserPreferences } from './hooks/useUserPreferences';
import { AuthProvider as SimpleAuthProvider, useAuth } from './context/AuthContext';



// App Content Component (inside Router)
const AppContent = () => {
  const location = useLocation();
  const theme = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // Hide navigation on public pages (landing, login, register)
  // Show navigation only on authenticated pages
  const isPublicPage = location.pathname === '/' || 
                      location.pathname === '/login' || 
                      location.pathname === '/register';
  
  const hideNavigation = isPublicPage;
  
  return (
    <Box>
      <Box
        component="main"
        sx={{
          p: { xs: 1, md: location.pathname.startsWith('/finance') ? 0 : 2 },
          mt: hideNavigation ? 0 : (location.pathname === '/onboarding' ? 0 : { xs: 7, md: 8 }),
          minHeight: '100vh',
          backgroundColor: location.pathname === '/onboarding' ? 'transparent' : '#f8f9fa',
          width: hideNavigation ? '100%' : { xs: '100%', md: `calc(100% - ${sidebarOpen ? 200 : 60}px)` },
          maxWidth: hideNavigation ? '100%' : { xs: '100%', md: `calc(100% - ${sidebarOpen ? 200 : 60}px)` },
          marginLeft: hideNavigation ? 0 : { xs: 0, md: `${sidebarOpen ? 200 : 60}px` },
          marginRight: 0,
          paddingLeft: 0,
          transition: theme.transitions.create(['width', 'marginLeft'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        }}
      >
        <Routes>
          {/* Public routes - accessible without login */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<SimpleLogin />} />
          <Route path="/register" element={<EnhancedRegister />} />
          
          {/* All routes - simple lock: if logged in show, if not show login */}
          <Route path="/onboarding" element={<SimpleProtectedRoute><OnboardingWizard /></SimpleProtectedRoute>} />
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
    </Box>
  );
};

// Navigation Component
const Navigation = ({ sidebarOpen, setSidebarOpen }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [waitingListOpen, setWaitingListOpen] = useState(false);
  const [waitingListEmail, setWaitingListEmail] = useState('');
  const [waitingListLoading, setWaitingListLoading] = useState(false);
  const [waitingListSuccess, setWaitingListSuccess] = useState(false);
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [readIds, setReadIds] = useState(() => {
    try {
      const raw = localStorage.getItem('edonuops.notifications.readIds');
      return new Set(raw ? JSON.parse(raw) : []);
    } catch {
      return new Set();
    }
  });
  const { hasPreferences, selectedModules } = useUserPreferences();
  const { logout: authLogout } = useAuth();
  
  // Use permissions hook
  const { hasModuleAccess, loading: permissionsLoading } = usePermissions();


  // Define all navigation links with their module IDs and required permissions
  const allNavLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: <DashboardIcon />, moduleId: 'dashboard', requiredModule: 'dashboard' },
    { name: 'Finance', path: '/finance', icon: <FinanceIcon />, moduleId: 'finance', requiredModule: 'finance' },
    { name: 'CRM', path: '/crm', icon: <CRMIcon />, moduleId: 'crm', requiredModule: 'crm' },
    { name: 'Procurement', path: '/procurement', icon: <ShoppingCart />, moduleId: 'procurement', requiredModule: 'procurement' },
    { name: ' Inventory', path: '/inventory', icon: <InventoryIcon />, moduleId: 'inventory', requiredModule: 'inventory' }
  ];

  // Define Finance module features
  const financeFeatures = [
    { name: 'Dashboard', path: '/finance?feature=dashboard', icon: <AssessmentIcon />, featureId: 'dashboard' },
    { name: 'Business Transactions', path: '/finance?feature=business-transactions', icon: <ReceiptIcon />, featureId: 'business-transactions' },
    { name: 'Manual Journal Entry', path: '/finance?feature=manual-journal', icon: <EditIcon />, featureId: 'manual-journal' },
    { name: 'Trial Balance', path: '/finance?feature=trial-balance', icon: <BalanceIcon />, featureId: 'trial-balance' },
    { name: 'Advanced Reports', path: '/finance?feature=advanced-reports', icon: <BarChartIcon />, featureId: 'advanced-reports' },
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

  // Fallback: Check localStorage directly if hook data is not available
  const getFallbackSelectedModules = () => {
    try {
      // Try to get from visitor session data first
      const visitorData = localStorage.getItem('edonuops_visitor_data');
      if (visitorData) {
        const parsed = JSON.parse(visitorData);
        const preferences = parsed.user_preferences;
        if (preferences && preferences.selectedModules) {
          return preferences.selectedModules;
        }
      }
      
      // Fallback: If we have business profile, assume basic modules are enabled
      const businessProfile = localStorage.getItem('edonuops_business_profile');
      if (businessProfile) {
        return ['financials', 'inventory'];
      }
    } catch (error) {
      console.error('Error reading localStorage:', error);
    }
    return [];
  };

  // Use ONLY hook data from backend - no localStorage fallback
  // This ensures sidebar matches dashboard exactly
  const effectiveSelectedModules = selectedModules; // Only use backend data
  const effectiveHasPreferences = hasPreferences; // Only use backend data
  

  // Filter navigation links based on permissions and user's selected modules
  const navLinks = allNavLinks.filter(link => {
    // Always show dashboard (not a module, just navigation)
    if (link.moduleId === 'dashboard') return true;
    
    // Check permissions first (most important)
    if (!hasModuleAccess(link.requiredModule)) {
      return false;
    }
    
    // ALWAYS show modules if user has access (don't hide based on preferences loading state)
    // The preferences are just for customization, not for hiding modules
    return true;
  });


  // Determine which navigation items to show based on current path
  const getCurrentNavigationItems = () => {
    if (location.pathname.startsWith('/finance')) {
      return financeFeatures;
    }
    if (location.pathname.startsWith('/crm')) {
      return crmFeatures;
    }
    if (location.pathname.startsWith('/inventory')) {
      return inventoryFeatures;
    }
    if (location.pathname.startsWith('/procurement')) {
      return procurementFeatures;
    }
    // For dashboard and other pages, show enabled modules
    return navLinks;
  };

  const currentNavItems = getCurrentNavigationItems();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Gmail-style sidebar toggle
  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  // Notifications: fetch integration gaps and surface as alerts
  const loadNotifications = async () => {
    try {
      const gapsResp = await apiClient.get('/api/procurement/integration/gaps');
      const gapItems = (gapsResp?.gaps || []).map(g => ({
        id: `gap-${g.po_number}-${g.item_id}`,
        type: 'integration_gap',
        message: `PO ${g.po_number} · Item ${g.item_id} missing product mapping`,
        href: '/inventory'
      }));
      
      // CRM ticket SLA alerts
      let ticketItems = [];
      try {
        const ticketsResp = await apiClient.get('/api/crm/tickets');
        const now = new Date();
        ticketItems = (ticketsResp || []).filter(t => {
          const isOpen = !['resolved', 'closed'].includes((t.status || '').toLowerCase());
          const breachedFlag = (t.sla_status || '').toLowerCase() === 'breached';
          const overdue = t.due_at ? (new Date(t.due_at) < now) : false;
          return isOpen && (breachedFlag || overdue);
        }).map(t => ({
          id: `ticket-${t.id}`,
          type: 'ticket_sla',
          message: `Ticket #${t.id || ''} ${t.subject ? '· ' + t.subject : ''} SLA at risk/overdue`,
          href: '/crm'
        }));
      } catch (_) {
        // ignore ticket errors to avoid blocking other alerts
      }
      
      // Daily cycle notifications (temporarily disabled until backend restart)
      let dailyCycleItems = [];
      let criticalDailyCycleItems = [];
      
      // Check if daily cycle endpoints are available
      const enableDailyCycleNotifications = false; // Set to true after backend restart
      
      if (enableDailyCycleNotifications) {
        try {
          const dailyCycleResp = await apiClient.get('/api/finance/daily-cycle/notifications/recent?hours_back=24&limit=10');
          if (dailyCycleResp?.success && dailyCycleResp.notifications) {
            dailyCycleItems = dailyCycleResp.notifications.map(notification => ({
              id: notification.id,
              type: notification.type,
              message: notification.message,
              href: notification.href || '/finance?feature=daily-cycle'
            }));
          }
        } catch (_) {
          // ignore daily cycle notification errors
        }
        
        // Critical daily cycle notifications
        try {
          const criticalResp = await apiClient.get('/api/finance/daily-cycle/notifications/critical');
          if (criticalResp?.success && criticalResp.critical_notifications) {
            criticalDailyCycleItems = criticalResp.critical_notifications.map(notification => ({
              id: notification.id,
              type: notification.type,
              message: notification.message,
              href: notification.href || '/finance?feature=daily-cycle'
            }));
          }
        } catch (_) {
          // ignore critical notification errors
        }
      }
      
      // CSV import errors (disabled when endpoint is unavailable)
      let importErrorItems = [];
      // Knowledge Base attachment safety flags (disabled when endpoint is unavailable)
      let kbFlagItems = [];
      
      setNotifications([...gapItems, ...ticketItems, ...dailyCycleItems, ...criticalDailyCycleItems, ...importErrorItems, ...kbFlagItems]);
    } catch (e) {
      // ignore
    }
  };

  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, 60000);
    return () => clearInterval(interval);
  }, []);

  const openNotifications = (e) => setNotificationsAnchor(e.currentTarget);
  const closeNotifications = () => setNotificationsAnchor(null);

  const persistReadIds = (ids) => {
    try { localStorage.setItem('edonuops.notifications.readIds', JSON.stringify(Array.from(ids))); } catch {}
  };
  const markRead = (id) => {
    setReadIds(prev => {
      const next = new Set(prev);
      next.add(id);
      persistReadIds(next);
      return next;
    });
  };
  const markAllRead = () => {
    setReadIds(prev => {
      const next = new Set(prev);
      notifications.forEach(n => next.add(n.id));
      persistReadIds(next);
      return next;
    });
  };
  const unreadCount = notifications.filter(n => !readIds.has(n.id)).length;
  const getIconForType = (type) => {
    switch (type) {
      case 'integration_gap':
        return <ReportProblemIcon fontSize="small" color="warning" />;
      case 'ticket_sla':
        return <WarningAmberIcon fontSize="small" color="error" />;
      case 'csv_import':
        return <MailOutlineIcon fontSize="small" color="info" />;
      case 'kb_attachment':
        return <AttachmentIcon fontSize="small" color="primary" />;
      // Daily cycle notification types
      case 'daily_cycle_opening':
        return <NotificationsIcon fontSize="small" color="info" />;
      case 'daily_cycle_closing':
        return <NotificationsIcon fontSize="small" color="success" />;
      case 'daily_cycle_locked':
        return <WarningAmberIcon fontSize="small" color="warning" />;
      case 'daily_cycle_unlocked':
        return <NotificationsIcon fontSize="small" color="info" />;
      case 'daily_cycle_failed':
        return <ReportProblemIcon fontSize="small" color="error" />;
      case 'adjustment_created':
        return <MailOutlineIcon fontSize="small" color="info" />;
      case 'adjustment_applied':
        return <NotificationsIcon fontSize="small" color="success" />;
      case 'adjustment_pending':
        return <WarningAmberIcon fontSize="small" color="warning" />;
      case 'grace_period_expired':
        return <ReportProblemIcon fontSize="small" color="warning" />;
      default:
        return <NotificationsIcon fontSize="small" />;
    }
  };

  const handleWaitingListSubmit = async (e) => {
    e.preventDefault();
    setWaitingListLoading(true);
    
    try {
      const response = await fetch('https://formspree.io/f/xqadyknr', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: waitingListEmail,
          type: 'Waiting List Signup',
          visitorId: 'navigation-user'
        }),
      });
      
      if (response.ok) {
        setWaitingListSuccess(true);
        setWaitingListEmail('');
        setWaitingListOpen(false);
      } else {
        throw new Error('Failed to join waiting list');
      }
    } catch (error) {
      console.error('Error joining waiting list:', error);
    } finally {
      setWaitingListLoading(false);
    }
  };

  const handleLogout = () => {
    
    // Use the auth hook logout function
    authLogout();
    
    // Clear additional session data
    localStorage.removeItem('currentTenant');
    localStorage.removeItem('user_logged_in');
    localStorage.removeItem('edonuops_visitor_id');
    localStorage.removeItem('edonuops_session_id');
    localStorage.removeItem('edonuops_session_expiry');
    
    
    // Close menu and redirect
    handleUserMenuClose();
    
    // Force page reload to reset all state
    window.location.href = '/login';
  };

  // Auto-close sidebar on mobile when route changes
  useEffect(() => {
    if (isMobile) {
      setMobileOpen(false);
    }
  }, [location.pathname, isMobile]);

  // Adjust sidebar state based on screen size
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    } else {
      setSidebarOpen(true);
    }
  }, [isMobile, setSidebarOpen]);


  const drawer = (
    <Box sx={{ width: sidebarOpen ? 200 : 60 }}>
      
      {/* Gmail-style header */}
      <Box sx={{ 
        p: 2, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: sidebarOpen ? 'space-between' : 'center',
        minHeight: 64,
        borderBottom: '1px solid #e0e0e0'
      }}>
        {sidebarOpen && (
          <Typography 
            variant="h6" 
            sx={{ 
              fontWeight: 400,
              color: '#5f6368',
              fontSize: '1.375rem'
            }}
          >
            {location.pathname.startsWith('/finance') ? 'Finance' : 'EdonuOps'}
          </Typography>
        )}
        
        <IconButton 
          onClick={handleSidebarToggle}
          sx={{ 
            color: '#5f6368',
            '&:hover': {
              backgroundColor: 'rgba(95, 99, 104, 0.08)'
            }
          }}
        >
          <MenuIcon />
        </IconButton>
      </Box>

      {/* Breadcrumb Navigation */}
      <BreadcrumbNavigation sidebarOpen={sidebarOpen} />

      {/* Gmail-style navigation */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List sx={{ px: 1, py: 1 }}>
          {currentNavItems.map((link) => (
            <ListItem key={link.name} disablePadding>
              <Tooltip 
                title={sidebarOpen ? '' : link.name} 
                placement="right" 
                arrow
                disableHoverListener={sidebarOpen}
              >
                <ListItem
                  component={Link}
                  to={link.path}
                  selected={link.featureId ? 
                    ((location.pathname.startsWith('/finance') && searchParams.get('feature') === link.featureId) ||
                     (location.pathname.startsWith('/crm') && searchParams.get('feature') === link.featureId) ||
                     (location.pathname.startsWith('/inventory') && searchParams.get('feature') === link.featureId) ||
                     (location.pathname.startsWith('/procurement') && searchParams.get('feature') === link.featureId)) :
                    (location.pathname === link.path)
                  }
                  sx={{
                    minHeight: 48,
                    px: sidebarOpen ? 2 : 1.5,
                    backgroundColor: (link.featureId ? 
                      ((location.pathname.startsWith('/finance') && searchParams.get('feature') === link.featureId) ||
                       (location.pathname.startsWith('/crm') && searchParams.get('feature') === link.featureId) ||
                       (location.pathname.startsWith('/inventory') && searchParams.get('feature') === link.featureId) ||
                       (location.pathname.startsWith('/procurement') && searchParams.get('feature') === link.featureId)) :
                      (location.pathname === link.path)
                    ) ? 'rgba(25, 118, 210, 0.08)' : 'transparent',
                    borderRadius: sidebarOpen ? '0 25px 25px 0' : '0 20px 20px 0',
                    margin: '0 8px',
                    width: 'auto',
                    '&.Mui-selected': {
                      backgroundColor: 'rgba(25, 118, 210, 0.08)',
                      '&:hover': {
                        backgroundColor: 'rgba(25, 118, 210, 0.12)',
                      },
                    },
                    '&:hover': {
                      backgroundColor: (link.featureId ? 
                        ((location.pathname.startsWith('/finance') && searchParams.get('feature') === link.featureId) ||
                         (location.pathname.startsWith('/crm') && searchParams.get('feature') === link.featureId) ||
                         (location.pathname.startsWith('/inventory') && searchParams.get('feature') === link.featureId) ||
                         (location.pathname.startsWith('/procurement') && searchParams.get('feature') === link.featureId)) :
                        (location.pathname === link.path)
                      ) ? 'rgba(25, 118, 210, 0.12)' : 'rgba(95, 99, 104, 0.08)'
                    }
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: sidebarOpen ? 40 : 'auto',
                      color: (link.featureId ? 
                        ((location.pathname.startsWith('/finance') && searchParams.get('feature') === link.featureId) ||
                         (location.pathname.startsWith('/crm') && searchParams.get('feature') === link.featureId) ||
                         (location.pathname.startsWith('/inventory') && searchParams.get('feature') === link.featureId) ||
                         (location.pathname.startsWith('/procurement') && searchParams.get('feature') === link.featureId)) :
                        (location.pathname === link.path)
                      ) ? '#1976d2' : '#5f6368',
                      justifyContent: 'center'
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
                            fontWeight: (link.featureId ? 
                              ((location.pathname.startsWith('/finance') && searchParams.get('feature') === link.featureId) ||
                               (location.pathname.startsWith('/crm') && searchParams.get('feature') === link.featureId) ||
                               (location.pathname.startsWith('/inventory') && searchParams.get('feature') === link.featureId) ||
                               (location.pathname.startsWith('/procurement') && searchParams.get('feature') === link.featureId)) :
                              (location.pathname === link.path)
                            ) ? 500 : 400,
                            color: (link.featureId ? 
                              ((location.pathname.startsWith('/finance') && searchParams.get('feature') === link.featureId) ||
                               (location.pathname.startsWith('/crm') && searchParams.get('feature') === link.featureId) ||
                               (location.pathname.startsWith('/inventory') && searchParams.get('feature') === link.featureId) ||
                               (location.pathname.startsWith('/procurement') && searchParams.get('feature') === link.featureId)) :
                              (location.pathname === link.path)
                            ) ? '#1976d2' : '#202124',
                            fontSize: '0.875rem'
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
          ))}
        </List>
      </Box>

      {/* Gmail-style footer */}
      {sidebarOpen && (
        <Box sx={{ p: 2, borderTop: '1px solid #e0e0e0' }}>
          <Typography variant="caption" color="#5f6368">
            Simple ERP Platform
          </Typography>
        </Box>
      )}
    </Box>
  );


  return (
    <>
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: theme.zIndex.drawer + 1,
          backgroundColor: '#ffffff',
          color: '#202124',
          borderBottom: '1px solid #e0e0e0',
          boxShadow: 'none'
        }}
      >
        <Toolbar sx={{ minHeight: 64 }}>
          {/* Gmail-style hamburger menu for desktop */}
          {!isMobile && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleSidebarToggle}
              sx={{ 
                mr: 2,
                color: '#5f6368',
                '&:hover': {
                  backgroundColor: 'rgba(95, 99, 104, 0.08)'
                }
              }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          {isMobile && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ 
                mr: 2,
                color: '#5f6368',
                '&:hover': {
                  backgroundColor: 'rgba(95, 99, 104, 0.08)'
                }
              }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Typography 
            variant="h6" 
            component="div" 
            sx={{ 
              flexGrow: 1, 
              fontWeight: 400,
              color: '#202124',
              fontSize: '1.375rem'
            }}
          >
            EdonuOps Enterprise
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <TenantSwitcher />
            <IconButton color="inherit" onClick={openNotifications} title="Notifications">
              <Badge badgeContent={unreadCount} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            <Button
              variant="contained"
              onClick={() => setWaitingListOpen(true)}
              sx={{
                bgcolor: '#FFD700',
                color: '#8B4513',
                '&:hover': {
                  bgcolor: '#FFA500',
                },
                px: 2,
                py: 0.5,
                fontWeight: 'bold',
                fontSize: '0.75rem',
                boxShadow: 1,
                height: 32
              }}
              title="Join our exclusive waiting list"
            >
              Join Waiting List
            </Button>
            <IconButton color="inherit" onClick={handleUserMenuOpen}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                <PersonIcon />
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={handleUserMenuClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={() => {
          handleUserMenuClose();
          navigate('/profile');
        }}>
          <ListItemIcon>
            <PersonIcon fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem onClick={() => {
          handleUserMenuClose();
          navigate('/dashboard/settings');
        }}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Dashboard Settings
        </MenuItem>
        <MenuItem onClick={() => {
          handleUserMenuClose();
          navigate('/admin/settings');
        }}>
          <ListItemIcon>
            <AdminPanelSettingsIcon fontSize="small" />
          </ListItemIcon>
          Administrative Settings
        </MenuItem>
        <Divider />
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>

      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationsAnchor}
        open={Boolean(notificationsAnchor)}
        onClose={closeNotifications}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <MenuItem onClick={() => { closeNotifications(); navigate('/notifications'); }} sx={{ fontWeight: 600 }}>
          View all
        </MenuItem>
        {notifications.length > 0 && <MenuItem onClick={markAllRead} disabled={unreadCount === 0}>Mark all as read</MenuItem>}
        {notifications.length > 0 && <Divider />}
        {notifications.length === 0 && (
          <MenuItem disabled>No notifications</MenuItem>
        )}
        {notifications.map((n) => (
          <MenuItem
            key={n.id}
            onClick={() => { markRead(n.id); closeNotifications(); navigate(n.href); }}
            sx={{ opacity: readIds.has(n.id) ? 0.6 : 1 }}
          >
            <ListItemIcon>
              {getIconForType(n.type)}
            </ListItemIcon>
            <ListItemText
              primary={n.message}
              secondary={n.type === 'integration_gap' ? 'Action needed' : (readIds.has(n.id) ? 'Read' : undefined)}
            />
          </MenuItem>
        ))}
      </Menu>

      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? mobileOpen : true}
        onClose={handleDrawerToggle}
        anchor="left"
        sx={{
          width: sidebarOpen ? 200 : 60,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: sidebarOpen ? 200 : 60,
            boxSizing: 'border-box',
            top: { xs: 56, md: 64 },
            height: { xs: 'calc(100% - 56px)', md: 'calc(100% - 64px)' },
            zIndex: theme.zIndex.drawer,
            position: 'fixed',
            left: 0,
            right: 'auto',
            transition: theme.transitions.create('width', {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
            overflowX: 'hidden',
            borderRight: '1px solid #e0e0e0',
            borderLeft: 'none',
            backgroundColor: '#ffffff'
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Waiting List Dialog */}
      <Dialog 
        open={waitingListOpen} 
        onClose={() => setWaitingListOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          🚀 Join Our Exclusive Waiting List
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Be among the first to experience the next generation of EdonuOps features and get early access to premium modules.
          </Typography>
          
          <Box component="form" onSubmit={handleWaitingListSubmit}>
            <TextField
              fullWidth
              label="Your Email Address"
              type="email"
              value={waitingListEmail}
              onChange={(e) => setWaitingListEmail(e.target.value)}
              placeholder="your@email.com"
              variant="outlined"
              required
              sx={{ mb: 2 }}
            />
            
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2 }}>
              We'll notify you about new features, updates, and exclusive offers.
            </Typography>
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setWaitingListOpen(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleWaitingListSubmit}
            disabled={waitingListLoading || !waitingListEmail.trim()}
          >
            {waitingListLoading ? 'Joining...' : 'Join Waiting List'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Notifications */}
      <Snackbar
        open={waitingListSuccess}
        autoHideDuration={6000}
        onClose={() => setWaitingListSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setWaitingListSuccess(false)} severity="success" sx={{ width: '100%' }}>
          🎉 Welcome to the waiting list! We'll keep you updated on new features.
        </Alert>
      </Snackbar>
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
