import React, { useState, useEffect } from 'react';
import { useCurrency } from './GlobalCurrencySettings';
import { useNavigate } from 'react-router-dom';
import { useForm, ValidationError } from '@formspree/react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  LinearProgress,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  useTheme,
  useMediaQuery,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  Switch,
  FormControlLabel,
  Divider,
  TextField,
  Snackbar
} from '@mui/material';
import {
  People as PeopleIcon,
  ShoppingCart as OrdersIcon,
  Inventory as ProductsIcon,
  AccountBalance as FinanceIcon,
  Business as BusinessIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Visibility as ViewIcon,
  PersonAdd as PersonAddIcon,
  Store as StoreIcon,
  Tune as TuneIcon,
  AdminPanelSettings as AdminPanelSettingsIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { useUserPreferences } from '../hooks/useUserPreferences';
import { usePermissions } from '../hooks/usePermissions';
import apiClient from '../services/apiClient';

// Feedback Form Component using Formspree
const FeedbackForm = () => {
  const [state, handleSubmit] = useForm("xqadyknr");
  
  if (state.succeeded) {
    return (
      <Box sx={{ textAlign: 'center', py: 3 }}>
        <Typography variant="h6" color="success.main" sx={{ fontWeight: 'bold' }}>
          ✅ Thank you for your feedback!
        </Typography>
        <Typography variant="body2" color="text.secondary">
          We'll use it to improve EdonuOps for you.
        </Typography>
      </Box>
    );
  }
  
  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ maxWidth: 600, mx: 'auto' }}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Your Email (optional)"
            type="email"
            name="email"
            placeholder="your@email.com"
            variant="outlined"
            size="small"
          />
          <ValidationError prefix="Email" field="email" errors={state.errors} />
        </Grid>
        <Grid item xs={12} sm={6}>
          <TextField
            fullWidth
            label="Message"
            multiline
            rows={2}
            name="message"
            placeholder="Tell us what you think..."
            variant="outlined"
            size="small"
            required
          />
          <ValidationError prefix="Message" field="message" errors={state.errors} />
        </Grid>
        <Grid item xs={12}>
          <Box sx={{ textAlign: 'center' }}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={state.submitting}
              sx={{ px: 4, py: 1.5 }}
            >
              {state.submitting ? 'Sending...' : 'Send Feedback'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  const { formatCurrency: formatGlobalCurrency } = useCurrency();
  const { 
    isModuleEnabled, 
    hasPreferences, 
    isLoading: preferencesLoading, 
    selectedModules, 
    updatePreferences, 
    error: preferencesError,
    refresh: refreshPreferences
  } = useUserPreferences();
  const { hasModuleAccess, loading: permissionsLoading } = usePermissions();
  
  // Calculate actual available modules based on permissions
  const availableModules = ['finance', 'inventory', 'procurement', 'crm', 'general'];
  const actualEnabledModules = availableModules.filter(module => hasModuleAccess(module));
  // Count only business modules (exclude dashboard)
  const businessModules = selectedModules.filter(module => module !== 'dashboard');
  const displayModuleCount = businessModules.length;
  
  console.log('📊 Dashboard Module Count Debug:', {
    selectedModules,
    businessModules,
    displayModuleCount,
    hasPreferences
  });
  // Removed useVisitorSession - now using user-based preferences
  
  // Module definitions for settings
  const allModules = [
    {
      id: 'finance',
      name: 'Financials',
      icon: <FinanceIcon sx={{ fontSize: 20 }} />,
      description: 'Complete financial management suite (auto-enables Procurement)',
      category: 'Core Business'
    },
    {
      id: 'inventory',
      name: 'Inventory Management',
      icon: <ProductsIcon sx={{ fontSize: 20 }} />,
      description: 'Smart inventory and warehouse management',
      category: 'Core Business'
    },
    {
      id: 'crm',
      name: 'Customer Relationship',
      icon: <PeopleIcon sx={{ fontSize: 20 }} />,
      description: 'Complete customer lifecycle management',
      category: 'Customer Management'
    },
    {
      id: 'procurement',
      name: 'Procurement & Purchasing',
      icon: <StoreIcon sx={{ fontSize: 20 }} />,
      description: 'Streamlined procurement processes (auto-enabled with Finance)',
      category: 'Operations'
    },
  ];
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  

  


  const fetchDashboardData = async () => {
    try {
      console.log('📊 Fetching dashboard data...');
      const response = await apiClient.get('/api/dashboard/summary');
      console.log('📊 Dashboard API Response:', response);
      const safe = response?.data || response || {};
      console.log('📊 Processed data:', {
        totalRevenue: safe.totalRevenue || 0,
        totalCustomers: safe.totalCustomers || 0,
        totalLeads: safe.totalLeads || 0,
        totalProducts: safe.totalProducts || 0,
        totalEmployees: safe.totalEmployees || 0
      });
      setDashboardData({
        totalRevenue: safe.totalRevenue || 0,
        totalCustomers: safe.totalCustomers || 0,
        totalLeads: safe.totalLeads || 0,
        totalOpportunities: safe.totalOpportunities || 0,
        totalProducts: safe.totalProducts || 0,
        totalEmployees: safe.totalEmployees || 0,
        recentActivity: safe.recentActivity || [],
        systemStatus: safe.systemStatus || 'operational'
      });
    } catch (error) {
      console.error('❌ Error fetching dashboard data:', error);
      setDashboardData({
        totalRevenue: 0,
        totalCustomers: 0,
        totalLeads: 0,
        totalOpportunities: 0,
        totalProducts: 0,
        totalEmployees: 0,
        recentActivity: [],
        systemStatus: 'operational'
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [apiClient]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
  };

  // Auto-enable procurement when finance is selected
  const handleModuleToggle = async (moduleId, isEnabled) => {
    try {
      let newModules = [...selectedModules];
      
      if (isEnabled) {
        // Adding a module
        if (moduleId === 'finance' && !newModules.includes('procurement')) {
          // Auto-enable procurement when finance is enabled
          newModules = [...newModules, 'finance', 'procurement'];
        } else if (moduleId === 'procurement' && !newModules.includes('finance')) {
          // Auto-enable finance when procurement is enabled
          newModules = [...newModules, 'procurement', 'finance'];
        } else if (!newModules.includes(moduleId)) {
          newModules.push(moduleId);
        }
      } else {
        // Removing a module
        if (moduleId === 'finance' && newModules.includes('procurement')) {
          // Auto-disable procurement when finance is disabled
          newModules = newModules.filter(id => id !== 'finance' && id !== 'procurement');
        } else if (moduleId === 'procurement' && newModules.includes('finance')) {
          // Auto-disable finance when procurement is disabled
          newModules = newModules.filter(id => id !== 'procurement' && id !== 'finance');
        } else {
          newModules = newModules.filter(id => id !== moduleId);
        }
      }
      
      await updatePreferences({ selected_modules: newModules });
    } catch (error) {
      console.error('Error updating modules:', error);
    }
  };

  const handleGettingStarted = (action) => {
    switch (action) {
      case 'customer':
        navigate('/crm');
        break;
      case 'explore':
        navigate('/finance');
        break;
      case 'product':
        navigate('/inventory');
        break;
      default:
        navigate('/crm');
    }
  };

  const handleSessionRefresh = () => {
    // Refresh user preferences from backend
    refreshPreferences();
    // For now, we'll just show an alert
    alert('Session refreshed successfully!');
  };





  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ py: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <Typography variant="h6">Loading dashboard...</Typography>
        </Box>
      </Container>
    );
  }

  const data = dashboardData || {
    totalRevenue: 0,
    totalCustomers: 0,
    totalLeads: 0,
    totalOpportunities: 0,
    totalProducts: 0,
    totalEmployees: 0,
    recentActivity: [],
    systemStatus: 'operational'
  };

  // Define all available modules with their details
  const quickActionModules = [
    { id: 'crm', name: 'Add Customer', icon: <PeopleIcon />, color: 'primary', path: '/crm', module: 'crm' },
    { id: 'finance', name: 'Create Invoice', icon: <FinanceIcon />, color: 'success', path: '/finance', module: 'finance' },
    { id: 'inventory', name: 'Add Product', icon: <ProductsIcon />, color: 'warning', path: '/inventory', module: 'inventory' },
    { id: 'procurement', name: 'Create PO', icon: <StoreIcon />, color: 'warning', path: '/procurement', module: 'procurement' },
  ];

  // Filter quick actions based on user's selected modules and limit to 3
  const quickActions = quickActionModules
    .filter(action => {
      if (!hasPreferences) return true; // Show all if no preferences set
      return isModuleEnabled(action.module);
    })
    .slice(0, 3); // Limit to 3 actions

  const systemStatus = [
    { name: 'Database', status: 'Online', color: 'success' },
    { name: 'API Services', status: 'Online', color: 'success' },
    { name: 'File Storage', status: 'Online', color: 'success' },
    { name: 'Email Service', status: 'Online', color: 'success' }
  ];

  const formatCurrency = (amount) => {
    if (amount === 0) return formatGlobalCurrency(0);
    if (amount >= 1000000) return formatGlobalCurrency(amount / 1000000) + 'M';
    if (amount >= 1000) return formatGlobalCurrency(amount / 1000) + 'K';
    return formatGlobalCurrency(amount);
  };

  return (
    <Box sx={{ 
      width: '100%', 
      height: '100%',
      backgroundColor: '#f8f9fa',
      overflow: 'auto',
      p: 2,
      maxWidth: '100%',
      boxSizing: 'border-box'
    }}>
      {/* Welcome Header */}
      <Box sx={{ mb: { xs: 2, md: 4 } }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box>
            <Typography 
              variant={isMobile ? "h4" : "h3"} 
              component="h1" 
              gutterBottom 
              sx={{ fontWeight: 'bold' }}
            >
              Dashboard
            </Typography>
            <Typography 
              variant={isMobile ? "body1" : "h6"} 
              color="text.secondary" 
              gutterBottom
            >
              {hasPreferences 
                ? `Business overview with ${displayModuleCount} enabled modules`
                : `Complete business management platform with ${displayModuleCount} modules available`
              }
            </Typography>
          </Box>
          
          {/* Settings Button removed: settings migrated to Dashboard Settings page */}
          

        </Box>
        
        <Alert severity="success" sx={{ mt: 2 }}>
          <Typography variant={isMobile ? "body1" : "h6"} sx={{ fontWeight: 'bold' }}>
            ✅ System Ready - {hasPreferences ? `${displayModuleCount} modules enabled` : `${displayModuleCount} modules operational`}
          </Typography>
          <Typography variant="body2">
            {hasPreferences 
              ? `Your selected modules are ready. Start by adding your first data to see it here.`
              : 'Your EdonuOps platform is ready. Start by adding your first data to see it here.'
            }
          </Typography>
        </Alert>
        
        {!hasPreferences && !preferencesLoading && (
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              💡 <strong>Tip:</strong> Customize your dashboard by selecting which modules you want to use. 
              <Button 
                size="small" 
                sx={{ ml: 1 }} 
                onClick={() => navigate('/onboarding')}
              >
                Go to Onboarding
              </Button>
            </Typography>
          </Alert>
        )}
        
        {hasPreferences && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="body2">
              ✅ <strong>Customized:</strong> Your dashboard is configured with {displayModuleCount} modules. 
              <Button 
                size="small" 
                sx={{ ml: 1 }} 
                onClick={() => navigate('/onboarding')}
                variant="outlined"
              >
                Modify Selection
              </Button>
            </Typography>
          </Alert>
        )}
        
        {/* Visitor Privacy Status */}
        <Alert severity="info" sx={{ mt: 2 }}>
          <Typography variant="body2">
            🔒 <strong>Privacy Protected:</strong> Your data is completely isolated and private
            {preferencesError && (
              <Chip 
                label="Preferences Error" 
                size="small" 
                color="warning" 
                sx={{ ml: 1 }}
              />
            )}
          </Typography>
        </Alert>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={2} sx={{ mb: { xs: 2, md: 4 } }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography 
                    variant={isMobile ? "h5" : "h4"} 
                    color="primary" 
                    sx={{ fontWeight: 'bold' }}
                  >
                    {data.totalRevenue > 0 ? formatCurrency(data.totalRevenue) : '0'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Revenue
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main', width: { xs: 40, md: 56 }, height: { xs: 40, md: 56 } }}>
                  <FinanceIcon />
                </Avatar>
              </Box>
              {data.totalRevenue > 0 && (
                <LinearProgress variant="determinate" value={75} sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography 
                    variant={isMobile ? "h5" : "h4"} 
                    color="primary" 
                    sx={{ fontWeight: 'bold' }}
                  >
                    {data.totalCustomers > 0 ? data.totalCustomers : 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Customers
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main', width: { xs: 40, md: 56 }, height: { xs: 40, md: 56 } }}>
                  <PeopleIcon />
                </Avatar>
              </Box>
              {data.totalCustomers > 0 && (
                <LinearProgress variant="determinate" value={85} sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography 
                    variant={isMobile ? "h5" : "h4"} 
                    color="primary" 
                    sx={{ fontWeight: 'bold' }}
                  >
                    {data.totalProducts > 0 ? data.totalProducts : 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Products
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main', width: { xs: 40, md: 56 }, height: { xs: 40, md: 56 } }}>
                  <ProductsIcon />
                </Avatar>
              </Box>
              {data.totalProducts > 0 && (
                <LinearProgress variant="determinate" value={60} sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography 
                    variant={isMobile ? "h5" : "h4"} 
                    color="primary" 
                    sx={{ fontWeight: 'bold' }}
                  >
                    {data.totalEmployees > 0 ? data.totalEmployees : 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Employees
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main', width: { xs: 40, md: 56 }, height: { xs: 40, md: 56 } }}>
                  <PeopleIcon />
                </Avatar>
              </Box>
              {data.totalEmployees > 0 && (
                <LinearProgress variant="determinate" value={90} sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Module Status */}
      {hasPreferences && (
        <Card elevation={2} sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                Your Module Status
              </Typography>
              <Chip 
                label={`${displayModuleCount} of ${allModules.length} enabled`} 
                color="primary" 
                variant="outlined"
              />
            </Box>
            <Grid container spacing={2}>
              {allModules.map((module) => (
                <Grid item xs={12} sm={6} md={4} key={module.id}>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 1,
                    p: 1,
                    borderRadius: 1,
                    backgroundColor: isModuleEnabled(module.id) ? 'success.light' : 'grey.100',
                    border: 1,
                    borderColor: isModuleEnabled(module.id) ? 'success.main' : 'grey.300',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: 2
                    }
                  }}
                  onClick={() => navigate('/onboarding')}
                  >
                    {module.icon}
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {module.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {isModuleEnabled(module.id) ? 'Enabled' : 'Click to enable'}
                      </Typography>
                      {/* Show auto-enable relationship */}
                      {module.id === 'procurement' && isModuleEnabled('finance') && (
                        <Typography variant="caption" color="primary" display="block">
                          Auto-enabled with Finance
                        </Typography>
                      )}
                      {module.id === 'finance' && isModuleEnabled('procurement') && (
                        <Typography variant="caption" color="primary" display="block">
                          Auto-enables Procurement
                        </Typography>
                      )}
                    </Box>
                    <Chip 
                      label={isModuleEnabled(module.id) ? '✓' : '✗'} 
                      size="small" 
                      color={isModuleEnabled(module.id) ? 'success' : 'default'}
                      variant="outlined"
                    />
                  </Box>
                </Grid>
              ))}
            </Grid>
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                💡 Click on any disabled module to enable it through onboarding
              </Typography>
              <Typography variant="caption" color="primary" display="block" sx={{ mt: 1 }}>
                🔗 <strong>Note:</strong> Finance and Procurement are linked - enabling one automatically enables the other
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions & System Status */}
      <Grid container spacing={2} sx={{ mb: { xs: 2, md: 4 } }}>
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Quick Actions
              </Typography>
              {quickActions.length > 0 ? (
                <Grid container spacing={1}>
                  {quickActions.map((action, index) => {
                    const allowedColors = ['primary','secondary','success','warning','info','error'];
                    const safeColor = allowedColors.includes(action.color) ? action.color : 'primary';
                    return (
                      <Grid item xs={12} sm={6} key={index}>
                        <Button
                          variant="outlined"
                          color={safeColor}
                          startIcon={action.icon}
                          fullWidth
                          onClick={() => navigate(action.path)}
                          sx={{ 
                            justifyContent: 'flex-start',
                            fontSize: { xs: '0.8rem', md: '0.9rem' },
                            py: { xs: 1, md: 1.25 }
                          }}
                        >
                          {action.name}
                        </Button>
                      </Grid>
                    );
                  })}
                </Grid>
              ) : (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    No modules enabled. Enable modules in onboarding to see quick actions.
                  </Typography>
                  <Button
                    variant="outlined"
                    size="small"
                    sx={{ mt: 1 }}
                    onClick={() => navigate('/onboarding')}
                  >
                    Go to Onboarding
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                System Status
              </Typography>
              <List dense>
                {systemStatus.map((service, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CheckCircleIcon color="success" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={service.name}
                      secondary={service.status}
                    />
                    <Chip 
                      label={service.status} 
                      color={service.color} 
                      size="small" 
                      variant="outlined"
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={2}>
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Recent Activity
                </Typography>
                <IconButton size="small" onClick={handleRefresh} disabled={refreshing}>
                  <RefreshIcon />
                </IconButton>
              </Box>
              
              <List>
                {(data.recentActivity || []).length > 0 ? (
                  data.recentActivity.map((activity, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <CheckCircleIcon color={activity.type === 'customer' ? 'success' : activity.type === 'finance' ? 'primary' : 'info'} />
                      </ListItemIcon>
                      <ListItemText 
                        primary={activity.message}
                        secondary={activity.time}
                      />
                      <Chip 
                        label={activity.type} 
                        color={activity.type === 'customer' ? 'success' : activity.type === 'finance' ? 'primary' : 'default'} 
                        size="small" 
                      />
                    </ListItem>
                  ))
                ) : (
                  <ListItem>
                    <ListItemText 
                      primary="No recent activity"
                      secondary="Start adding data to see activity here"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
                Getting Started
              </Typography>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="System Setup Complete"
                    secondary={`${displayModuleCount} modules configured`}
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="System Ready"
                    secondary="Start adding your data"
                  />
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <InfoIcon color="info" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Next Steps"
                    secondary={hasPreferences ? "Use your enabled modules" : "Complete onboarding to customize"}
                  />
                </ListItem>
              </List>

              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  startIcon={<PersonAddIcon />}
                  fullWidth
                  sx={{ mb: 1 }}
                  onClick={() => handleGettingStarted('customer')}
                >
                  Add Your First Customer
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<StoreIcon />}
                  fullWidth
                  onClick={() => handleGettingStarted('explore')}
                >
                  Explore Modules
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Feedback Form */}
      <Card elevation={2} sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', textAlign: 'center', mb: 3 }}>
            💬 We'd Love Your Feedback
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', mb: 3 }}>
            Help us improve EdonuOps for your business needs
          </Typography>
          
          <FeedbackForm />
        </CardContent>
      </Card>

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          EdonuOps Enterprise Platform - {displayModuleCount} modules enabled
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="SOC 2 Compliant" size="small" sx={{ mr: 1, mb: 1 }} />
          <Chip label="ISO 27001" size="small" sx={{ mr: 1, mb: 1 }} />
          <Chip label="GDPR Ready" size="small" sx={{ mr: 1, mb: 1 }} />
          <Chip label="Enterprise Grade" size="small" color="primary" />
        </Box>
        

      </Box>

      {/* Settings Dialog removed: migrated to Dashboard Settings page */}





      {/* Success Notifications */}

    </Box>
  );
};

export default Dashboard;
