import React, { useState } from 'react';
import {
  Box, Container, Typography, Button, Stepper, Step, StepLabel,
  Card, CardContent, Grid, TextField, FormControl, InputLabel,
  Select, MenuItem, Chip, Checkbox, FormGroup, FormControlLabel,
  Alert, LinearProgress, Paper, Stack, useTheme, useMediaQuery
} from '@mui/material';
import {
  AccountBalance, Inventory, People,
  CheckCircle, ArrowForward, ArrowBack, Celebration,
  Store, Business
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useVisitorSession } from '../hooks/useVisitorSession';
import apiClient from '../services/apiClient';

const OnboardingWizard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { visitorId, setVisitorData } = useVisitorSession();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);

  // Form data
  const initialProfile = () => {
    try {
      const raw = localStorage.getItem('edonuops_business_profile');
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  };
  const [businessProfile, setBusinessProfile] = useState(initialProfile() || {
    companyName: '',
    industry: '',
    employeeCount: '',
    annualRevenue: '',
    challenges: []
  });

  const [selectedModules, setSelectedModules] = useState(['financials', 'inventory']);
  const [selectedCoATemplate, setSelectedCoATemplate] = useState('retail');
  
  // Team Setup state
  const [organizationSetup, setOrganizationSetup] = useState({
    organizationType: 'single_owner', // 'single_owner', 'partnership', 'corporation', 'startup'
    departments: ['Management', 'Finance', 'Operations'],
    userPermissions: {
      defaultUserRole: 'admin', // Since owner is setting up
      restrictionLevel: 'flexible',
      allowRoleOverride: true,
      requireApprovalForAdjustments: false
    },
    teamMembers: [
      {
        id: 1,
        name: 'Company Owner',
        email: '',
        role: 'owner',
        department: 'Management',
        permissions: ['all'],
        status: 'active'
      }
    ]
  });

  const steps = [
    'Business Profile',
    'Module Selection',
    'CoA Template',
    'Team Setup',
    'Data Import',
    'Activation'
  ];

  // Persist profile as user types
  const persistProfile = (next) => {
    try { localStorage.setItem('edonuops_business_profile', JSON.stringify(next)); } catch {}
  };

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
        selectedModules: selectedModules.includes('financials') && !selectedModules.includes('procurement')
          ? [...selectedModules, 'procurement']
          : selectedModules,
        businessProfile: businessProfile,
        coaTemplate: selectedCoATemplate,
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
      try { 
        localStorage.setItem('edonuops_business_profile', JSON.stringify(businessProfile)); 
        localStorage.setItem('edonuops_coa_template', selectedCoATemplate);
      } catch {}
      
      // Send preferences to backend (uses configured API base URL)
      try {
        await apiClient.post(`/api/visitors/${visitorId}/preferences`, userPreferences);
      } catch (error) {
        console.error('Could not sync preferences to backend:', error);
      }
      
      // Simulate account activation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Save organization setup to AdminSettings format
      localStorage.setItem('adminSettings_userPermissions', JSON.stringify(organizationSetup.userPermissions));
      localStorage.setItem('edonuops_organization_setup', JSON.stringify(organizationSetup));
      
      // Show success message
      alert('🎉 Welcome to EdonuOps! Your personalized dashboard has been configured with your selected modules and team settings.');
      
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
            onChange={(e) => setBusinessProfile(prev => { const next = { ...prev, companyName: e.target.value }; persistProfile(next); return next; })}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth required>
            <InputLabel>Industry</InputLabel>
            <Select
              value={businessProfile.industry}
              onChange={(e) => setBusinessProfile(prev => { const next = { ...prev, industry: e.target.value }; persistProfile(next); return next; })}
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
              onChange={(e) => setBusinessProfile(prev => { const next = { ...prev, employeeCount: e.target.value }; persistProfile(next); return next; })}
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
              onChange={(e) => setBusinessProfile(prev => { const next = { ...prev, annualRevenue: e.target.value }; persistProfile(next); return next; })}
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
                            setBusinessProfile(prev => { const next = { ...prev, challenges: [...prev.challenges, challenge] }; persistProfile(next); return next; });
                          } else {
                            setBusinessProfile(prev => { const next = { ...prev, challenges: prev.challenges.filter(c => c !== challenge) }; persistProfile(next); return next; });
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

  const renderCoATemplateSelection = () => (
    <Box>
      <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Choose Your Chart of Accounts Template
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Select a template that matches your business type. This will pre-populate your chart of accounts with the most relevant accounts for your industry.
      </Typography>
      
      <Grid container spacing={3}>
        {[
          { id: 'retail', name: 'Retail Business', description: 'Perfect for stores, e-commerce, and retail operations', accounts: 45 },
          { id: 'services', name: 'Services Business', description: 'Ideal for consulting, agencies, and service providers', accounts: 38 },
          { id: 'manufacturing', name: 'Manufacturing', description: 'For production businesses with inventory and equipment', accounts: 52 },
          { id: 'freelancer', name: 'Freelancer/Solo', description: 'Simple setup for individual entrepreneurs', accounts: 25 },
          { id: 'ngo', name: 'Non-Profit', description: 'Specialized accounts for charitable organizations', accounts: 41 }
        ].map((template) => (
          <Grid item xs={12} md={6} key={template.id}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                border: selectedCoATemplate === template.id ? 2 : 1,
                borderColor: selectedCoATemplate === template.id ? 'primary.main' : 'divider',
                '&:hover': { borderColor: 'primary.main' }
              }}
              onClick={() => setSelectedCoATemplate(template.id)}
            >
              <CardContent>
                <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {template.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {template.description}
                </Typography>
                <Chip 
                  label={`${template.accounts} accounts`} 
                  size="small" 
                  color={selectedCoATemplate === template.id ? 'primary' : 'default'}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderTeamSetup = () => (
    <Box>
      <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Organization & Team Setup
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Configure your organization structure and set up user permissions for your team.
      </Typography>

      {/* Organization Type */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Business color="primary" />
            Organization Type
          </Typography>
          
          <Grid container spacing={2}>
            {[
              { value: 'single_owner', label: 'Single Owner', desc: 'Individual business owner with full control' },
              { value: 'partnership', label: 'Partnership', desc: 'Multiple partners sharing ownership and decisions' },
              { value: 'corporation', label: 'Corporation', desc: 'Formal corporate structure with board and shareholders' },
              { value: 'startup', label: 'Startup', desc: 'Growing company with flexible team structure' }
            ].map((type) => (
              <Grid item xs={12} sm={6} key={type.value}>
                <Card 
                  variant={organizationSetup.organizationType === type.value ? "elevation" : "outlined"}
                  sx={{ 
                    cursor: 'pointer',
                    border: organizationSetup.organizationType === type.value ? 2 : 1,
                    borderColor: organizationSetup.organizationType === type.value ? 'primary.main' : 'divider'
                  }}
                  onClick={() => setOrganizationSetup(prev => ({ ...prev, organizationType: type.value }))}
                >
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>{type.label}</Typography>
                    <Typography variant="body2" color="text.secondary">{type.desc}</Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* User Permissions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <People color="primary" />
            Default User Permissions
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Default Role for New Users</InputLabel>
                <Select
                  value={organizationSetup.userPermissions.defaultUserRole}
                  onChange={(e) => setOrganizationSetup(prev => ({
                    ...prev,
                    userPermissions: { ...prev.userPermissions, defaultUserRole: e.target.value }
                  }))}
                  label="Default Role for New Users"
                >
                  <MenuItem value="user">Regular User - Basic access</MenuItem>
                  <MenuItem value="accountant">Accountant - Financial access</MenuItem>
                  <MenuItem value="admin">Admin - Full system access</MenuItem>
                  <MenuItem value="manager">Manager - Department oversight</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Smart Entry Restrictions</InputLabel>
                <Select
                  value={organizationSetup.userPermissions.restrictionLevel}
                  onChange={(e) => setOrganizationSetup(prev => ({
                    ...prev,
                    userPermissions: { ...prev.userPermissions, restrictionLevel: e.target.value }
                  }))}
                  label="Smart Entry Restrictions"
                >
                  <MenuItem value="none">None - Full access for all</MenuItem>
                  <MenuItem value="flexible">Flexible - Smart guidance with overrides</MenuItem>
                  <MenuItem value="strict">Strict - Enforce accounting rules</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Box sx={{ mt: 2 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={organizationSetup.userPermissions.allowRoleOverride}
                  onChange={(e) => setOrganizationSetup(prev => ({
                    ...prev,
                    userPermissions: { ...prev.userPermissions, allowRoleOverride: e.target.checked }
                  }))}
                />
              }
              label="Allow users to temporarily override their permissions"
            />
          </Box>

          <Box sx={{ mt: 1 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={organizationSetup.userPermissions.requireApprovalForAdjustments}
                  onChange={(e) => setOrganizationSetup(prev => ({
                    ...prev,
                    userPermissions: { ...prev.userPermissions, requireApprovalForAdjustments: e.target.checked }
                  }))}
                />
              }
              label="Require approval for adjustment entries and corrections"
            />
          </Box>
        </CardContent>
      </Card>

      {/* Current Setup Summary */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircle color="primary" />
            Setup Summary
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Chip 
                label={`Organization: ${organizationSetup.organizationType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}`}
                color="primary" 
                variant="outlined" 
                sx={{ mb: 1, mr: 1 }}
              />
              <Chip 
                label={`Default Role: ${organizationSetup.userPermissions.defaultUserRole}`}
                color="secondary" 
                variant="outlined" 
                sx={{ mb: 1, mr: 1 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <Chip 
                label={`Restrictions: ${organizationSetup.userPermissions.restrictionLevel}`}
                color={organizationSetup.userPermissions.restrictionLevel === 'none' ? 'success' : 
                       organizationSetup.userPermissions.restrictionLevel === 'strict' ? 'error' : 'warning'} 
                variant="outlined" 
                sx={{ mb: 1, mr: 1 }}
              />
              <Chip 
                label={`Overrides: ${organizationSetup.userPermissions.allowRoleOverride ? 'Allowed' : 'Disabled'}`}
                color={organizationSetup.userPermissions.allowRoleOverride ? 'success' : 'default'} 
                variant="outlined" 
                sx={{ mb: 1 }}
              />
            </Grid>
          </Grid>

          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Note:</strong> You can modify these settings later in Admin Settings → User Permissions. 
              As the owner, you'll have full access regardless of these restrictions.
            </Typography>
          </Alert>
        </CardContent>
      </Card>
    </Box>
  );

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderBusinessProfile();
      case 1:
        return renderModuleSelection();
      case 2:
        return renderCoATemplateSelection();
      case 3:
        return renderTeamSetup();
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
      case 2:
        return selectedCoATemplate !== '';
      case 3:
        return organizationSetup.organizationType && organizationSetup.userPermissions.defaultUserRole;
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
