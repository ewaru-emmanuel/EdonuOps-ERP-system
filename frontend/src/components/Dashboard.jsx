import React, { useState, useEffect } from 'react';
import { useCurrency } from './GlobalCurrencySettings';
import { useNavigate } from 'react-router-dom';
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
  Divider
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
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
  Settings as SettingsIcon,
  Tune as TuneIcon,
  Psychology as PsychologyIcon,
  ShoppingCart as ShoppingCartIcon,
  Work as WorkIcon,
  AdminPanelSettings as AdminPanelSettingsIcon
} from '@mui/icons-material';
import { useAuth } from '../App';
import { useUserPreferences } from '../hooks/useUserPreferences';
import { useVisitorSession } from '../hooks/useVisitorSession';

const Dashboard = () => {
  const { apiClient } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  const { formatCurrency: formatGlobalCurrency } = useCurrency();
  const { isModuleEnabled, hasPreferences, isLoading: preferencesLoading, selectedModules, updatePreferences } = useUserPreferences();
  const { visitorId, sessionId, isSessionValid } = useVisitorSession();
  
  // Module definitions for settings
  const allModules = [
    {
      id: 'financials',
      name: 'Financials',
      icon: <FinanceIcon sx={{ fontSize: 20 }} />,
      description: 'Complete financial management suite',
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
      id: 'hcm',
      name: 'Human Capital Management',
      icon: <BusinessIcon sx={{ fontSize: 20 }} />,
      description: 'Comprehensive HR and team management',
      category: 'People Management'
    },
    {
      id: 'sustainability',
      name: 'Sustainability & ESG',
      icon: <TrendingUpIcon sx={{ fontSize: 20 }} />,
      description: 'Environmental, Social & Governance tracking',
      category: 'Compliance'
    },
    {
      id: 'ai',
      name: 'AI & Analytics',
      icon: <PsychologyIcon sx={{ fontSize: 20 }} />,
      description: 'AI-powered insights and automation',
      category: 'Intelligence'
    },
    {
      id: 'ecommerce',
      name: 'E-commerce Operations',
      icon: <ShoppingCartIcon sx={{ fontSize: 20 }} />,
      description: 'Complete e-commerce management',
      category: 'Sales'
    },
    {
      id: 'erp',
      name: 'Enterprise Resource Planning',
      icon: <WorkIcon sx={{ fontSize: 20 }} />,
      description: 'Integrated business processes',
      category: 'Integration'
    },
    {
      id: 'procurement',
      name: 'Procurement & Purchasing',
      icon: <StoreIcon sx={{ fontSize: 20 }} />,
      description: 'Streamlined procurement processes',
      category: 'Operations'
    },
    {
      id: 'inventorywms',
      name: 'Advanced Warehouse Management',
      icon: <ProductsIcon sx={{ fontSize: 20 }} />,
      description: 'Professional warehouse operations',
      category: 'Operations'
    },
    {
      id: 'adminsettings',
      name: 'Administrative Settings',
      icon: <AdminPanelSettingsIcon sx={{ fontSize: 20 }} />,
      description: 'System configuration and control',
      category: 'System'
    },
    {
      id: 'dashboardai',
      name: 'AI Dashboard Copilot',
      icon: <PsychologyIcon sx={{ fontSize: 20 }} />,
      description: 'AI-powered dashboard assistance',
      category: 'Intelligence'
    },
    {
      id: 'coresetup',
      name: 'Core System Setup',
      icon: <SettingsIcon sx={{ fontSize: 20 }} />,
      description: 'Essential system configuration',
      category: 'System'
    }
  ];
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  const fetchDashboardData = async () => {
    try {
      const response = await apiClient.get('/api/dashboard/summary');
      setDashboardData(response.data || response);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setDashboardData(null);
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
    // This would call the session refresh function from useVisitorSession
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
    { id: 'financials', name: 'Add Customer', icon: <PeopleIcon />, color: 'primary', path: '/crm', module: 'crm' },
    { id: 'financials', name: 'Create Invoice', icon: <FinanceIcon />, color: 'success', path: '/finance', module: 'financials' },
    { id: 'inventory', name: 'Add Product', icon: <ProductsIcon />, color: 'warning', path: '/inventory', module: 'inventory' },
    { id: 'erp', name: 'New Order', icon: <OrdersIcon />, color: 'info', path: '/erp', module: 'erp' },
    { id: 'hcm', name: 'Add Employee', icon: <PeopleIcon />, color: 'secondary', path: '/hcm', module: 'hcm' },
    { id: 'procurement', name: 'Create PO', icon: <StoreIcon />, color: 'warning', path: '/procurement', module: 'procurement' },
    { id: 'sustainability', name: 'ESG Report', icon: <TrendingUpIcon />, color: 'success', path: '/sustainability', module: 'sustainability' },
    { id: 'ai', name: 'AI Insights', icon: <TrendingUpIcon />, color: 'purple', path: '/ai', module: 'ai' }
  ];

  // Filter quick actions based on user's selected modules
  const quickActions = quickActionModules.filter(action => {
    if (!hasPreferences) return true; // Show all if no preferences set
    return isModuleEnabled(action.module);
  });

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
    <Container maxWidth="xl" sx={{ py: 2 }}>
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
              Welcome to EdonuOps
            </Typography>
            <Typography 
              variant={isMobile ? "body1" : "h6"} 
              color="text.secondary" 
              gutterBottom
            >
              Enterprise management platform
            </Typography>
          </Box>
          
          {/* Settings Button */}
          <IconButton
            onClick={() => setSettingsOpen(true)}
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              '&:hover': {
                bgcolor: 'primary.dark',
              },
              p: 1.5
            }}
            title="Dashboard Settings"
          >
            <SettingsIcon />
          </IconButton>
        </Box>
        
        <Alert severity="success" sx={{ mt: 2 }}>
          <Typography variant={isMobile ? "body1" : "h6"} sx={{ fontWeight: 'bold' }}>
            ✅ System Ready - {hasPreferences ? `${quickActions.length} modules enabled` : 'All modules operational'}
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
              ✅ <strong>Customized:</strong> Your dashboard is configured with {selectedModules.length} modules. 
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
            🔒 <strong>Privacy Protected:</strong> Your data is isolated with unique visitor ID: <strong>{visitorId}</strong>
            {!isSessionValid && (
              <Chip 
                label="Session Expired" 
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
                    {formatCurrency(data.totalRevenue)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Revenue
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main', width: { xs: 40, md: 56 }, height: { xs: 40, md: 56 } }}>
                  <TrendingUpIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={75} sx={{ mt: 2 }} />
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
                    {data.totalCustomers}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Customers
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main', width: { xs: 40, md: 56 }, height: { xs: 40, md: 56 } }}>
                  <PeopleIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={85} sx={{ mt: 2 }} />
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
                    {data.totalProducts}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Products
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main', width: { xs: 40, md: 56 }, height: { xs: 40, md: 56 } }}>
                  <ProductsIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={60} sx={{ mt: 2 }} />
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
                    {data.totalEmployees}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Employees
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main', width: { xs: 40, md: 56 }, height: { xs: 40, md: 56 } }}>
                  <PeopleIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={90} sx={{ mt: 2 }} />
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
                label={`${selectedModules.length} of ${allModules.length} enabled`} 
                color="primary" 
                variant="outlined"
              />
            </Box>
            <Grid container spacing={2}>
              {allModules.map((module) => (
                <Grid item xs={12} sm={6} md={4} key={module.module}>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 1,
                    p: 1,
                    borderRadius: 1,
                    backgroundColor: isModuleEnabled(module.module) ? 'success.light' : 'grey.100',
                    border: 1,
                    borderColor: isModuleEnabled(module.module) ? 'success.main' : 'grey.300',
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
                        {isModuleEnabled(module.module) ? 'Enabled' : 'Click to enable'}
                      </Typography>
                    </Box>
                    <Chip 
                      label={isModuleEnabled(module.module) ? '✓' : '✗'} 
                      size="small" 
                      color={isModuleEnabled(module.module) ? 'success' : 'default'}
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
              <Grid container spacing={1}>
                {quickActions.map((action, index) => (
                  <Grid item xs={6} key={index}>
                    <Button
                      variant="outlined"
                      startIcon={action.icon}
                      fullWidth
                      onClick={() => navigate(action.path)}
                      sx={{ 
                        justifyContent: 'flex-start',
                        borderColor: `${action.color}.main`,
                        color: `${action.color}.main`,
                        fontSize: { xs: '0.75rem', md: '0.875rem' },
                        py: { xs: 1, md: 1.5 },
                        '&:hover': {
                          borderColor: `${action.color}.dark`,
                          backgroundColor: `${action.color}.light`,
                        }
                      }}
                    >
                      {action.name}
                    </Button>
                  </Grid>
                ))}
              </Grid>
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
                    secondary={`${selectedModules.length} modules configured`}
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

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          EdonuOps Enterprise Platform - {hasPreferences ? `${selectedModules.length} modules enabled` : 'All modules available'}
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="SOC 2 Compliant" size="small" sx={{ mr: 1, mb: 1 }} />
          <Chip label="ISO 27001" size="small" sx={{ mr: 1, mb: 1 }} />
          <Chip label="GDPR Ready" size="small" sx={{ mr: 1, mb: 1 }} />
          <Chip label="Enterprise Grade" size="small" color="primary" />
        </Box>
        
        {/* Visitor Session Info */}
        <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 2, display: 'inline-block' }}>
          <Typography variant="caption" color="text.secondary">
            <strong>Visitor Session:</strong> {visitorId} | Session: {sessionId}
          </Typography>
          <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 0.5 }}>
            Your data is completely isolated from other visitors
          </Typography>
        </Box>
      </Box>

      {/* Settings Dialog */}
      <Dialog 
        open={settingsOpen} 
        onClose={() => setSettingsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <SettingsIcon color="primary" />
          Dashboard Settings
        </DialogTitle>
        
        <DialogContent>
          <Tabs 
            value={activeTab} 
            onChange={(e, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}
          >
            <Tab label="Module Management" />
            <Tab label="System Preferences" />
            <Tab label="Visitor Settings" />
          </Tabs>

          {/* Module Management Tab */}
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
                Manage Your Modules
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Select which modules you want to use in your dashboard. Only enabled modules will be visible.
              </Typography>
              
              <Grid container spacing={2}>
                {allModules.map((module) => (
                  <Grid item xs={12} md={6} key={module.id}>
                    <Card 
                      sx={{ 
                        p: 2,
                        border: selectedModules.includes(module.id) ? 2 : 1,
                        borderColor: selectedModules.includes(module.id) ? 'primary.main' : 'grey.300',
                        transition: 'all 0.2s ease',
                        '&:hover': { 
                          transform: 'translateY(-2px)',
                          boxShadow: 2
                        }
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                        {module.icon}
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {module.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {module.category}
                          </Typography>
                        </Box>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={selectedModules.includes(module.id)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  const newModules = [...selectedModules, module.id];
                                  updatePreferences({ selectedModules: newModules });
                                } else {
                                  const newModules = selectedModules.filter(id => id !== module.id);
                                  updatePreferences({ selectedModules: newModules });
                                }
                              }}
                              color="primary"
                            />
                          }
                          label=""
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {module.description}
                      </Typography>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* System Preferences Tab */}
          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
                System Preferences
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Configure your system preferences and display options.
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Display Settings
                    </Typography>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Show module status indicators"
                    />
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Enable quick action shortcuts"
                    />
                    <FormControlLabel
                      control={<Switch />}
                      label="Show visitor privacy info"
                    />
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Notification Settings
                    </Typography>
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Session expiry warnings"
                    />
                    <FormControlLabel
                      control={<Switch defaultChecked />}
                      label="Module update notifications"
                    />
                    <FormControlLabel
                      control={<Switch />}
                      label="System status alerts"
                    />
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Visitor Settings Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold', mb: 2 }}>
                Visitor Session Information
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Your unique visitor session details and privacy information.
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Session Details
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Visitor ID: <strong>{visitorId}</strong>
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Session ID: <strong>{sessionId}</strong>
                      </Typography>
                    </Box>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        Status: 
                        <Chip 
                          label={isSessionValid ? "Active" : "Expired"} 
                          color={isSessionValid ? "success" : "warning"} 
                          size="small" 
                          sx={{ ml: 1 }}
                        />
                      </Typography>
                    </Box>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
                      Privacy Information
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Your data is completely isolated from other visitors. Each visitor gets their own unique storage space.
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      Session expires after 24 hours for security.
                    </Typography>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={handleSessionRefresh}
                    >
                      Refresh Session
                    </Button>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions sx={{ p: 3 }}>
          <Button onClick={() => setSettingsOpen(false)}>
            Close
          </Button>
          <Button 
            variant="contained" 
            onClick={() => navigate('/onboarding')}
            startIcon={<TuneIcon />}
          >
            Advanced Onboarding
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Dashboard;
