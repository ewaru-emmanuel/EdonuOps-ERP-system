import React, { useState } from 'react';
import {
  Box, Container, Typography, Button, Grid, Card, CardContent,
  Avatar, Chip, Paper, useTheme, useMediaQuery, AppBar, Toolbar,
  IconButton, Drawer, List, ListItem, ListItemText, ListItemIcon,
  Divider, Stack, Alert, Snackbar
} from '@mui/material';
import {
  Business, AccountBalance, Inventory, People, TrendingUp,
  CheckCircle, Star, Security, Speed, Support, Menu, Close,
  ArrowForward, ArrowDownward, Visibility, VisibilityOff,
  Email, Lock, Person
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import DashboardMockup from './DashboardMockup';

const LandingPage = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [signupData, setSignupData] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [showSignup, setShowSignup] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const modules = [
    {
      id: 'financials',
      name: 'Financials',
      icon: <AccountBalance sx={{ fontSize: 40, color: 'primary.main' }} />,
      description: 'Accounting, Invoicing, Multi-Currency',
      features: ['General Ledger', 'Accounts Payable/Receivable', 'Multi-Currency Support', 'Financial Reporting'],
      color: 'primary'
    },
    {
      id: 'inventory',
      name: 'Inventory',
      icon: <Inventory sx={{ fontSize: 40, color: 'success.main' }} />,
      description: 'Stock Management, Smart Reordering',
      features: ['Stock Management', 'Product Tracking', 'Smart Reordering', 'Real-time Tracking'],
      color: 'success'
    },
    {
      id: 'crm',
      name: 'CRM',
      icon: <People sx={{ fontSize: 40, color: 'info.main' }} />,
      description: 'Leads, Customers, Sales Pipeline',
      features: ['Lead Management', 'Customer Database', 'Sales Pipeline', 'Customer Analytics'],
      color: 'info'
    },
  ];

  const handleModuleClick = (moduleId) => {
    const element = document.getElementById(`module-${moduleId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleStartTrial = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/register');
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Navigation */}
      <AppBar position="fixed" color="transparent" elevation={0} sx={{ bgcolor: 'rgba(255,255,255,0.95)', backdropFilter: 'blur(10px)' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold', color: 'primary.main' }}>
            EdonuOps
          </Typography>
          
          {!isMobile ? (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button color="inherit" onClick={() => handleModuleClick('financials')}>Financials</Button>
              <Button color="inherit" onClick={() => handleModuleClick('inventory')}>Inventory</Button>
              <Button color="inherit" onClick={() => handleModuleClick('crm')}>CRM</Button>
              <Button color="inherit" onClick={() => navigate('/login')}>Login</Button>
              <Button variant="outlined" sx={{ color: 'primary.main', borderColor: 'primary.main' }} onClick={() => navigate('/register')}>Sign Up</Button>
              <Button variant="contained" onClick={handleStartTrial}>Start Free Trial</Button>
            </Box>
          ) : (
            <IconButton onClick={() => setMobileMenuOpen(true)}>
              <Menu />
            </IconButton>
          )}
        </Toolbar>
      </AppBar>

      {/* Hero Section */}
      <Box sx={{ pt: 10, pb: 8, bgcolor: 'primary.main', color: 'white' }}>
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" component="h1" sx={{ fontWeight: 'bold', mb: 2 }}>
                One Platform. Every Business Operation.
              </Typography>
              <Typography variant="h5" sx={{ mb: 3, opacity: 0.9 }}>
                Integrate your finance, inventory, sales, and team management in one place.
              </Typography>
              
              {/* Security Notice */}
              <Alert 
                severity="info" 
                icon={<Security />}
                sx={{ 
                  mb: 3, 
                  bgcolor: 'rgba(255,255,255,0.1)', 
                  color: 'white',
                  '& .MuiAlert-icon': { color: 'white' }
                }}
              >
                <Typography variant="body2">
                  🔒 <strong>Secure Enterprise ERP</strong> - Authentication required for all business operations
                </Typography>
              </Alert>
              
              <Stack direction="row" spacing={2} sx={{ mb: 4 }}>
                <Button
                  variant="contained"
                  size="large"
                  onClick={handleStartTrial}
                  sx={{ 
                    bgcolor: 'white', 
                    color: 'primary.main', 
                    fontWeight: 'bold',
                    '&:hover': { bgcolor: 'grey.100' }
                  }}
                >
                  {isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
                </Button>
                <Button
                  variant="outlined"
                  size="large"
                  sx={{ 
                    borderColor: 'white', 
                    color: 'white',
                    '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' }
                  }}
                >
                  Watch Demo
                </Button>
              </Stack>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="body2">Built for teams of 10 to 10,000
                  +.</Typography>
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star key={star} sx={{ fontSize: 16, color: 'yellow' }} />
                  ))}
                </Box>
              </Box>
            </Grid>
                         <Grid item xs={12} md={6}>
               <Box sx={{ textAlign: 'center' }}>
                 <DashboardMockup />
               </Box>
             </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Module Showcase */}
      <Box sx={{ py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" component="h2" align="center" sx={{ fontWeight: 'bold', mb: 6 }}>
            Everything You Need to Run Your Business
          </Typography>
          
          <Grid container spacing={4}>
            {modules.map((module) => (
              <Grid item xs={12} md={6} lg={3} key={module.id}>
                <Card 
                  id={`module-${module.id}`}
                  sx={{ 
                    height: '100%', 
                    cursor: 'pointer',
                    transition: 'all 0.3s ease',
                    '&:hover': { 
                      transform: 'translateY(-8px)',
                      boxShadow: theme.shadows[8]
                    }
                  }}
                  onClick={() => handleModuleClick(module.id)}
                >
                  <CardContent sx={{ textAlign: 'center', p: 4 }}>
                    <Box sx={{ mb: 2 }}>
                      {module.icon}
                    </Box>
                    <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {module.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                      {module.description}
                    </Typography>
                    <Stack spacing={1}>
                      {module.features.map((feature, index) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <CheckCircle sx={{ fontSize: 16, color: 'success.main' }} />
                          <Typography variant="body2">{feature}</Typography>
                        </Box>
                      ))}
                    </Stack>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box sx={{ py: 8, bgcolor: 'primary.main', color: 'white' }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h3" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
              Ready to Transform Your Business?
            </Typography>
            <Typography variant="h6" sx={{ mb: 4, opacity: 0.9 }}>
              Join thousands of companies that trust EdonuOps to run their operations.
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={handleStartTrial}
              sx={{ 
                bgcolor: 'white', 
                color: 'primary.main', 
                fontWeight: 'bold',
                px: 4,
                py: 1.5,
                '&:hover': { bgcolor: 'grey.100' }
              }}
            >
{isAuthenticated ? 'Go to Dashboard' : 'Get Started'}
            </Button>
            <Typography variant="body2" sx={{ mt: 2, opacity: 0.8 }}>
              No credit card required • 14-day free trial • Cancel anytime
            </Typography>
          </Box>
        </Container>
      </Box>
    </Box>
  );
};

export default LandingPage;

