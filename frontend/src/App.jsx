import React, { useState, createContext, useContext, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
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
  Chip
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
  Nature as NatureIcon
} from '@mui/icons-material';

// Import components
import Dashboard from './components/Dashboard';
import FinanceModule from './modules/finance/FinanceModule';
import CRMModule from './modules/crm/CRMModule';
import ERPMainModule from './modules/erp/ERPMainModule';
import InventoryModule from './modules/erp/InventoryModule';
import HCMModule from './modules/hcm/HCMModule';
import EcommerceModule from './modules/ecommerce/EcommerceModule';
import AIModule from './modules/ai/AIModule';
import SustainabilityModule from './modules/sustainability/SustainabilityModule';

// Import API service
import { initializeERPApiService } from './services/erpApiService';

// Create Auth Context
const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// API client for making HTTP requests
const apiClient = {
  async get(endpoint) {
    try {
      const response = await fetch(`http://localhost:5000${endpoint}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
      throw error;
    }
  },

  async post(endpoint, data) {
    try {
      const response = await fetch(`http://localhost:5000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error posting to ${endpoint}:`, error);
      throw error;
    }
  },

  async put(endpoint, data) {
    try {
      const response = await fetch(`http://localhost:5000${endpoint}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error putting to ${endpoint}:`, error);
      throw error;
    }
  },

  async delete(endpoint) {
    try {
      const response = await fetch(`http://localhost:5000${endpoint}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error deleting ${endpoint}:`, error);
      throw error;
    }
  }
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

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const { logout } = useAuth();

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: <DashboardIcon /> },
    { name: 'Finance', path: '/finance', icon: <FinanceIcon /> },
    { name: 'CRM', path: '/crm', icon: <CRMIcon /> },
    { name: 'ERP', path: '/erp', icon: <BusinessIcon /> },
    { name: 'HCM', path: '/hcm', icon: <PeopleIcon /> },
    { name: 'E-commerce', path: '/ecommerce', icon: <StoreIcon /> },
    { name: 'AI Intelligence', path: '/ai', icon: <PsychologyIcon /> },
    { name: 'Sustainability', path: '/sustainability', icon: <NatureIcon /> },
    { name: 'Inventory', path: '/inventory', icon: <InventoryIcon /> }
  ];

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
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
            <Chip 
              label="Ready to Use" 
              color="success" 
              size="small" 
              variant="outlined"
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
        <MenuItem>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Settings
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
            top: 64,
            height: 'calc(100% - 64px)',
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
      <AuthProvider>
        <Router>
          <Box sx={{ display: 'flex' }}>
            <Navigation />
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                p: 3,
                mt: 8,
                ml: { xs: 0, md: 0 },
                minHeight: '100vh',
                backgroundColor: 'grey.50'
              }}
            >
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/finance" element={<FinanceModule />} />
                <Route path="/crm" element={<CRMModule />} />
                        <Route path="/erp" element={<ERPMainModule />} />
        <Route path="/inventory" element={<InventoryModule />} />
        <Route path="/hcm" element={<HCMModule />} />
        <Route path="/ecommerce" element={<EcommerceModule />} />
        <Route path="/ai" element={<AIModule />} />
        <Route path="/sustainability" element={<SustainabilityModule />} />
              </Routes>
            </Box>
          </Box>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;
