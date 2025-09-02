import React, { useState } from 'react';
import {
  Box, Container, Typography, Button, Stepper, Step, StepLabel,
  Card, CardContent, Grid, TextField, FormControl, InputLabel,
  Select, MenuItem, Chip, Checkbox, FormGroup, FormControlLabel,
  Alert, LinearProgress, Paper, Stack, useTheme, useMediaQuery
} from '@mui/material';
import {
  Business, AccountBalance, Inventory, People, TrendingUp,
  CheckCircle, ArrowForward, ArrowBack, Celebration,
  ShoppingCart, Settings, Psychology, Store, Work, AdminPanelSettings
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useVisitorSession } from '../hooks/useVisitorSession';

const OnboardingWizard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { visitorId, setVisitorData } = useVisitorSession();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);

  // Form data
  const [businessProfile, setBusinessProfile] = useState({
    companyName: '',
    industry: '',
    employeeCount: '',
    annualRevenue: '',
    challenges: []
  });

  const [selectedModules, setSelectedModules] = useState(['financials', 'inventory', 'coresetup']);

  const steps = [
    'Business Profile',
    'Module Selection',
    'Team Setup',
    'Data Import',
    'Activation'
  ];

  const industries = [
    'Technology', 'Manufacturing', 'Retail', 'Healthcare', 'Finance',
    'Education', 'Real Estate', 'Transportation', 'Food & Beverage', 'Other'
  ];

  const employeeRanges = [
    '1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'
  ];

  const revenueRanges = [
    'Under $100K', '$100K - $500K', '$500K - $1M', '$1M - $5M', '$5M - $10M', '$10M+'
  ];

  const challenges = [
    'Manual processes taking too much time',
    'Difficulty tracking inventory',
    'Cash flow management',
    'Customer relationship management',
    'Team collaboration',
    'Financial reporting',
    'Compliance and regulations',
    'Scaling operations'
  ];

  const modules = [
    {
      id: 'financials',
      name: 'Financials',
      icon: <AccountBalance sx={{ fontSize: 40, color: 'primary.main' }} />,
      description: 'Complete financial management suite',
      features: [
        'General Ledger & Chart of Accounts',
        'Accounts Payable & Receivable',
        'Multi-Currency Support',
        'Financial Reporting & Analytics'
      ],
      recommended: true
    },
    {
      id: 'inventory',
      name: 'Inventory Management',
      icon: <Inventory sx={{ fontSize: 40, color: 'success.main' }} />,
      description: 'Smart inventory and warehouse management',
      features: [
        'Stock Level Tracking',
        'Warehouse Management',
        'Smart Reordering',
        'Real-time Analytics'
      ],
      recommended: true
    },
    {
      id: 'crm',
      name: 'Customer Relationship',
      icon: <People sx={{ fontSize: 40, color: 'info.main' }} />,
      description: 'Complete customer lifecycle management',
      features: [
        'Lead Management',
        'Customer Database',
        'Sales Pipeline',
        'Customer Analytics'
      ],
      recommended: false
    },
    {
      id: 'hcm',
      name: 'Human Capital Management',
      icon: <Business sx={{ fontSize: 40, color: 'warning.main' }} />,
      description: 'Comprehensive HR and team management',
      features: [
        'Employee Management',
        'Payroll Processing',
        'Time & Attendance',
        'Performance Reviews'
      ],
      recommended: false
    },
    {
      id: 'sustainability',
      name: 'Sustainability & ESG',
      icon: <TrendingUp sx={{ fontSize: 40, color: 'success.main' }} />,
      description: 'Environmental, Social & Governance tracking',
      features: [
        'Carbon Footprint Monitoring',
        'ESG Compliance Reporting',
        'Sustainability Metrics',
        'Green Initiative Tracking'
      ],
      recommended: false
    },
    {
      id: 'ai',
      name: 'AI & Analytics',
      icon: <Psychology sx={{ fontSize: 40, color: 'purple.main' }} />,
      description: 'AI-powered insights and automation',
      features: [
        'Predictive Analytics',
        'Smart Recommendations',
        'Automated Workflows',
        'Business Intelligence'
      ],
      recommended: false
    },
    {
      id: 'ecommerce',
      name: 'E-commerce Operations',
      icon: <ShoppingCart sx={{ fontSize: 40, color: 'orange.main' }} />,
      description: 'Complete e-commerce management',
      features: [
        'Order Management',
        'Product Catalog',
        'Customer Portal',
        'Payment Processing'
      ],
      recommended: false
    },
    {
      id: 'erp',
      name: 'Enterprise Resource Planning',
      icon: <Work sx={{ fontSize: 40, color: 'indigo.main' }} />,
      description: 'Integrated business processes',
      features: [
        'Process Automation',
        'Cross-module Integration',
        'Workflow Management',
        'Business Intelligence'
      ],
      recommended: false
    },
    {
      id: 'procurement',
      name: 'Procurement & Purchasing',
      icon: <Store sx={{ fontSize: 40, color: 'teal.main' }} />,
      description: 'Streamlined procurement processes',
      features: [
        'Vendor Management',
        'Purchase Orders',
        'Contract Management',
        'Spend Analytics'
      ],
      recommended: false
    },
    {
      id: 'inventorywms',
      name: 'Advanced Warehouse Management',
      icon: <Inventory sx={{ fontSize: 40, color: 'deepPurple.main' }} />,
      description: 'Professional warehouse operations',
      features: [
        'Multi-location Support',
        'Advanced Picking',
        'Route Optimization',
        '3PL Integration'
      ],
      recommended: false
    },
    {
      id: 'adminsettings',
      name: 'Administrative Settings',
      icon: <AdminPanelSettings sx={{ fontSize: 40, color: 'grey.main' }} />,
      description: 'System configuration and control',
      features: [
        'User Management',
        'Role Permissions',
        'System Settings',
        'Audit Logs'
      ],
      recommended: false
    },
    {
      id: 'dashboardai',
      name: 'AI Dashboard Copilot',
      icon: <Psychology sx={{ fontSize: 40, color: 'pink.main' }} />,
      description: 'AI-powered dashboard assistance',
      features: [
        'Smart Insights',
        'Natural Language Queries',
        'Automated Reporting',
        'Predictive Alerts'
      ],
      recommended: false
    },
    {
      id: 'coresetup',
      name: 'Core System Setup',
      icon: <Settings sx={{ fontSize: 40, color: 'brown.main' }} />,
      description: 'Essential system configuration',
      features: [
        'Company Profile',
        'Basic Settings',
        'Data Import',
        'System Integration'
      ],
      recommended: true
    }
  ];

  const handleNext = () => {
    if (activeStep === steps.length - 1) {
      handleActivation();
    } else {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleModuleToggle = (moduleId) => {
    setSelectedModules(prev => 
      prev.includes(moduleId) 
        ? prev.filter(id => id !== moduleId)
        : [...prev, moduleId]
    );
  };

  const handleActivation = async () => {
    setLoading(true);
    try {
      // Save user preferences to visitor-specific storage
      const userPreferences = {
        selectedModules: selectedModules,
        businessProfile: businessProfile,
        activatedAt: new Date().toISOString(),
        visitorId: visitorId,
        deviceInfo: {
          userAgent: navigator.userAgent,
          screenResolution: `${window.screen.width}x${window.screen.height}`,
          timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
        }
      };
      
      // Store in visitor-specific storage
      setVisitorData('user_preferences', userPreferences);
      
      // Send preferences to backend
      try {
        await fetch(`/api/visitors/${visitorId}/preferences`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userPreferences)
        });
      } catch (error) {
        console.error('Could not sync preferences to backend:', error);
      }
      
      // Simulate account activation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Show success message
      alert('🎉 Welcome to EdonuOps! Your personalized dashboard has been configured with your selected modules.');
      
      // Navigate to the dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Activation failed:', error);
      alert('Activation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderBusinessProfile = () => (
    <Box>
      <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Tell us about your company
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        This helps us customize EdonuOps for your specific needs and industry.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Company Name"
            value={businessProfile.companyName}
            onChange={(e) => setBusinessProfile(prev => ({ ...prev, companyName: e.target.value }))}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth required>
            <InputLabel>Industry</InputLabel>
            <Select
              value={businessProfile.industry}
              onChange={(e) => setBusinessProfile(prev => ({ ...prev, industry: e.target.value }))}
              label="Industry"
            >
              {industries.map((industry) => (
                <MenuItem key={industry} value={industry}>{industry}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth required>
            <InputLabel>Number of Employees</InputLabel>
            <Select
              value={businessProfile.employeeCount}
              onChange={(e) => setBusinessProfile(prev => ({ ...prev, employeeCount: e.target.value }))}
              label="Number of Employees"
            >
              {employeeRanges.map((range) => (
                <MenuItem key={range} value={range}>{range}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Annual Revenue</InputLabel>
            <Select
              value={businessProfile.annualRevenue}
              onChange={(e) => setBusinessProfile(prev => ({ ...prev, annualRevenue: e.target.value }))}
              label="Annual Revenue"
            >
              {revenueRanges.map((range) => (
                <MenuItem key={range} value={range}>{range}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Current Challenges (Select all that apply)
          </Typography>
          <FormGroup>
            <Grid container spacing={2}>
              {challenges.map((challenge) => (
                <Grid item xs={12} md={6} key={challenge}>
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={businessProfile.challenges.includes(challenge)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setBusinessProfile(prev => ({
                              ...prev,
                              challenges: [...prev.challenges, challenge]
                            }));
                          } else {
                            setBusinessProfile(prev => ({
                              ...prev,
                              challenges: prev.challenges.filter(c => c !== challenge)
                            }));
                          }
                        }}
                      />
                    }
                    label={challenge}
                  />
                </Grid>
              ))}
            </Grid>
          </FormGroup>
        </Grid>
      </Grid>
    </Box>
  );

  const renderModuleSelection = () => (
    <Box>
      <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        What would you like to manage with EdonuOps?
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Select the modules that match your business needs.
      </Typography>
      
      <Grid container spacing={3}>
        {modules.map((module) => (
          <Grid item xs={12} md={6} key={module.id}>
            <Card 
              sx={{ 
                height: '100%',
                cursor: 'pointer',
                border: selectedModules.includes(module.id) ? 2 : 1,
                borderColor: selectedModules.includes(module.id) ? 'primary.main' : 'grey.300',
                transition: 'all 0.3s ease',
                '&:hover': { 
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[4]
                }
              }}
              onClick={() => handleModuleToggle(module.id)}
            >
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  {module.icon}
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                      {module.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {module.description}
                    </Typography>
                  </Box>
                  <Checkbox
                    checked={selectedModules.includes(module.id)}
                    color="primary"
                  />
                </Box>
                
                {module.recommended && (
                  <Chip 
                    label="Recommended" 
                    color="success" 
                    size="small" 
                    sx={{ mb: 2 }}
                  />
                )}
                
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
    </Box>
  );

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderBusinessProfile();
      case 1:
        return renderModuleSelection();
      default:
        return (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h4">Coming Soon...</Typography>
          </Box>
        );
    }
  };

  const canProceed = () => {
    switch (activeStep) {
      case 0:
        return businessProfile.companyName && businessProfile.industry && businessProfile.employeeCount;
      case 1:
        return selectedModules.length > 0;
      default:
        return true;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ maxWidth: 800, mx: 'auto' }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 2 }}>
            Welcome to EdonuOps!
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Let's get your business set up in just a few minutes
          </Typography>
        </Box>

        {/* Stepper */}
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {/* Step Content */}
        <Paper sx={{ p: 4, mb: 4 }}>
          {renderStepContent()}
        </Paper>

        {/* Navigation */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
            startIcon={<ArrowBack />}
          >
            Back
          </Button>
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={!canProceed() || loading}
            endIcon={activeStep === steps.length - 1 ? <Celebration /> : <ArrowForward />}
          >
            {activeStep === steps.length - 1 ? 'Activate Account' : 'Continue'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default OnboardingWizard;
