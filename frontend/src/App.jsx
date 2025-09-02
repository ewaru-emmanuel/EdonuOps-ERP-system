import React, { useState, createContext, useContext, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { CurrencyProvider, useCurrency } from './components/GlobalCurrencySettings';
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
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Snackbar,
  Alert
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
  Business as BusinessIcon,
  Settings as SettingsIcon,
  People as PeopleIcon,
  Store as StoreIcon,
  Psychology as PsychologyIcon,
  Nature as NatureIcon,
  CurrencyExchange as CurrencyIcon,
  ShoppingCart,
  AdminPanelSettings as AdminPanelSettingsIcon
} from '@mui/icons-material';

// Import components
import Dashboard from './components/Dashboard';
import FinanceModule from './modules/finance/FinanceModule';
import CRMModule from './modules/crm/CRMModule';
import ERPMainModule from './modules/erp/ERPMainModule';
import InventoryModule from './modules/erp/InventoryModule';
import CoreInventoryModule from './modules/inventory/CoreInventoryModule';
import WarehouseManagementModule from './modules/inventory/WarehouseManagementModule';
import HCMModule from './modules/hcm/HCMModule';
import EcommerceModule from './modules/ecommerce/EcommerceModule';
import AIModule from './modules/ai/AIModule';
import SustainabilityModule from './modules/sustainability/SustainabilityModule';
import ProcurementModule from './modules/erp/procurement/ProcurementModule';
import OnboardingWizard from './components/OnboardingWizard';

// Import API service
import { initializeERPApiService } from './services/erpApiService';

// Import centralized API client
import apiClient from './services/apiClient';

// Import user preferences hook
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

  const login = async (email, password) => {
    // Simulate login
    await new Promise(resolve => setTimeout(resolve, 500));
    setIsAuthenticated(true);
    return { success: true };
  };

  const logout = () => {
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout, apiClient }}>
      {children}
    </AuthContext.Provider>
  );
};

// App Content Component (inside Router)
const AppContent = () => {
  const location = useLocation();
  
  return (
    <Box sx={{ display: 'flex' }}>
      <Navigation />
              <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: { xs: 2, md: 3 },
            mt: location.pathname === '/onboarding' ? 0 : { xs: 7, md: 8 },
            minHeight: '100vh',
            backgroundColor: location.pathname === '/onboarding' ? 'transparent' : 'grey.50'
          }}
        >
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/onboarding" element={<OnboardingWizard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/finance" element={<FinanceModule />} />
          <Route path="/crm" element={<CRMModule />} />
          <Route path="/procurement" element={<ProcurementModule />} />
          <Route path="/erp" element={<ERPMainModule />} />
          <Route path="/inventory" element={<CoreInventoryModule />} />
          <Route path="/warehouse" element={<WarehouseManagementModule />} />
          <Route path="/hcm" element={<HCMModule />} />
          <Route path="/ecommerce" element={<EcommerceModule />} />
          <Route path="/ai" element={<AIModule />} />
          <Route path="/sustainability" element={<SustainabilityModule />} />
          {/* Catch-all route for direct URL access */}
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </Box>
    </Box>
  );
};

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [waitingListOpen, setWaitingListOpen] = useState(false);
  const [waitingListEmail, setWaitingListEmail] = useState('');
  const [waitingListLoading, setWaitingListLoading] = useState(false);
  const [waitingListSuccess, setWaitingListSuccess] = useState(false);
  const { logout } = useAuth();
  const { baseCurrency, setShowChangeDialog } = useCurrency();
  const { isModuleEnabled, hasPreferences } = useUserPreferences();

  // Hide navigation only on onboarding
  const hideNavigation = location.pathname === '/onboarding';

  // Define all navigation links with their module IDs
  const allNavLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: <DashboardIcon />, moduleId: 'dashboard' },
    { name: 'Finance', path: '/finance', icon: <FinanceIcon />, moduleId: 'financials' },
    { name: 'CRM', path: '/crm', icon: <CRMIcon />, moduleId: 'crm' },
    { name: 'Procurement', path: '/procurement', icon: <ShoppingCart />, moduleId: 'procurement' },
    { name: 'ERP', path: '/erp', icon: <BusinessIcon />, moduleId: 'erp' },
    { name: 'HCM', path: '/hcm', icon: <PeopleIcon />, moduleId: 'hcm' },
    { name: 'E-commerce', path: '/ecommerce', icon: <StoreIcon />, moduleId: 'ecommerce' },
    { name: 'AI Intelligence', path: '/ai', icon: <PsychologyIcon />, moduleId: 'ai' },
    { name: 'Sustainability', path: '/sustainability', icon: <NatureIcon />, moduleId: 'sustainability' },
    { name: ' Inventory', path: '/inventory', icon: <InventoryIcon />, moduleId: 'inventory' },
    { name: '🏭 Warehouse', path: '/warehouse', icon: <InventoryIcon />, moduleId: 'inventorywms' }
  ];

  // Filter navigation links based on user's selected modules
  const navLinks = allNavLinks.filter(link => {
    if (!hasPreferences) return true; // Show all if no preferences set
    if (link.moduleId === 'dashboard') return true; // Always show dashboard
    return isModuleEnabled(link.moduleId);
  });

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
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
    logout();
    handleUserMenuClose();
  };

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
          EdonuOps
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Enterprise SaaS Platform
        </Typography>
        {hasPreferences && (
          <Chip 
            label={`${navLinks.length - 1} modules enabled`} 
            size="small" 
            color="primary" 
            variant="outlined"
            sx={{ mt: 1 }}
          />
        )}
      </Box>
      <List>
        {navLinks.map((link) => (
          <ListItem
            key={link.name}
            component={Link}
            to={link.path}
            selected={location.pathname === link.path}
            sx={{
              '&.Mui-selected': {
                backgroundColor: 'primary.light',
                '&:hover': {
                  backgroundColor: 'primary.light',
                },
              },
            }}
          >
            <ListItemIcon sx={{ color: location.pathname === link.path ? 'primary.main' : 'inherit' }}>
              {link.icon}
            </ListItemIcon>
            <ListItemText primary={link.name} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  // Don't render navigation on landing page or onboarding
  if (hideNavigation) {
    return null;
  }

  return (
    <>
      <AppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
            EdonuOps Enterprise
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
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
            <Chip
              label={baseCurrency}
              color="primary"
              variant="outlined"
              size="small"
              onClick={() => setShowChangeDialog(true)}
              clickable
              icon={<CurrencyIcon />}
            />
            <IconButton color="inherit">
              <NotificationsIcon />
            </IconButton>
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
        <MenuItem>
          <ListItemIcon>
            <PersonIcon fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <MenuItem onClick={() => {
          handleUserMenuClose();
          navigate('/dashboard');
        }}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Dashboard Settings
        </MenuItem>
        <MenuItem onClick={() => {
          handleUserMenuClose();
          navigate('/dashboard');
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

      <Drawer
        variant={isMobile ? 'temporary' : 'permanent'}
        open={isMobile ? mobileOpen : true}
        onClose={handleDrawerToggle}
        sx={{
          width: 250,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: 250,
            boxSizing: 'border-box',
            top: { xs: 56, md: 64 },
            height: { xs: 'calc(100% - 56px)', md: 'calc(100% - 64px)' },
            zIndex: theme.zIndex.drawer,
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
  const theme = createTheme({
    palette: {
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
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
      <CurrencyProvider>
        <AuthProvider>
          <Router>
            <AppContent />
          </Router>
        </AuthProvider>
      </CurrencyProvider>
    </ThemeProvider>
  );
};

export default App;
