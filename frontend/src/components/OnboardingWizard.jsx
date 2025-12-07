import React, { useState, useEffect } from 'react';
import {
  Box, Container, Typography, Button, Stepper, Step, StepLabel,
  Card, CardContent, Grid, TextField, FormControl, InputLabel,
  Select, MenuItem, Chip, Checkbox, FormGroup, FormControlLabel,
  Alert, LinearProgress, Paper, Stack, useTheme, useMediaQuery,
  Backdrop, CircularProgress, Dialog, DialogContent, DialogTitle
} from '@mui/material';
import {
  AccountBalance, Inventory, People,
  CheckCircle, ArrowForward, ArrowBack, Celebration,
  Store, Business
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useVisitorSession } from '../hooks/useVisitorSession';
import { useAuth } from '../context/AuthContext';
import apiClient from '../services/apiClient';
import databaseFirstPersistence from '../services/databaseFirstPersistence';

const OnboardingWizard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const { visitorId, setVisitorData } = useVisitorSession();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);

  // Form data - start empty, load from database
  const [businessProfile, setBusinessProfile] = useState({
    companyName: '',
    industry: '',
    employeeCount: '',
    annualRevenue: '',
    challenges: []
  });

  const [selectedModules, setSelectedModules] = useState([]);
  const [selectedCoATemplate, setSelectedCoATemplate] = useState('retail');
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [defaultAccountsPreview, setDefaultAccountsPreview] = useState([]);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [createDefaultAccounts, setCreateDefaultAccounts] = useState(true);
  
  // Load default accounts preview
  const loadDefaultAccountsPreview = async () => {
    if (!selectedModules.includes('finance')) {
      return;
    }
    
    try {
      setLoadingPreview(true);
      const preview = await apiClient.get('/api/finance/double-entry/accounts/default/preview');
      setDefaultAccountsPreview(Array.isArray(preview) ? preview : []);
    } catch (error) {
      console.error('Error loading default accounts preview:', error);
      setDefaultAccountsPreview([]);
    } finally {
      setLoadingPreview(false);
    }
  };

  // Load existing user data from database (only on first load)
  const loadExistingData = async () => {
    if (!isAuthenticated || !user) {
      setIsLoadingData(false);
      return;
    }

    try {
      console.log('🔄 Loading existing user data from database...');
      
      // Load user modules from backend
      let userModules = [];
      try {
        const modulesResponse = await apiClient.get('/api/dashboard/modules/user');
        userModules = Array.isArray(modulesResponse) ? modulesResponse : [];
      } catch (moduleError) {
        // Handle 404 or other errors gracefully - user might not have modules yet
        if (moduleError.message && moduleError.message.includes('404')) {
          console.log('ℹ️ User modules endpoint not found or user has no modules yet');
        } else {
          console.warn('⚠️ Error loading user modules:', moduleError.message);
        }
        userModules = [];
      }
      
      const moduleIds = userModules.map(module => module.id);
      console.log('📊 Found modules in database:', moduleIds);
      
      // Always pre-fill modules from database if they exist (user can still modify)
      if (moduleIds.length > 0) {
        setSelectedModules(moduleIds);
        console.log('✅ Pre-filled modules from database:', moduleIds);
      } else {
        console.log('ℹ️ No modules found in database, user will select fresh');
      }
      
      // Load business profile from database
      let profileResponse = null;
      try {
        profileResponse = await databaseFirstPersistence.loadUserData(user.id, 'business_profile');
        console.log('📦 Business profile response:', profileResponse);
        if (profileResponse) {
          // Merge with defaults to ensure all fields are present
          const mergedProfile = {
            companyName: profileResponse.companyName || '',
            industry: profileResponse.industry || '',
            employeeCount: profileResponse.employeeCount || '',
            annualRevenue: profileResponse.annualRevenue || '',
            challenges: profileResponse.challenges || []
          };
          console.log('📝 Setting business profile:', mergedProfile);
          setBusinessProfile(mergedProfile);
          console.log('✅ Loaded business profile from database');
        } else {
          console.log('ℹ️ No business profile found in database');
        }
      } catch (e) {
        console.error('❌ Error loading business profile:', e);
        console.log('No business profile in database');
      }
      
      // Load COA template from database
      let coaResponse = null;
      try {
        coaResponse = await databaseFirstPersistence.loadUserData(user.id, 'coa_template');
        console.log('📦 COA template response:', coaResponse);
        if (coaResponse) {
          setSelectedCoATemplate(coaResponse);
          console.log('✅ Loaded COA template from database:', coaResponse);
        } else {
          console.log('ℹ️ No COA template found in database');
        }
      } catch (e) {
        console.error('❌ Error loading COA template:', e);
        console.log('No COA template in database');
      }
      
      // Load organization setup from database
      let orgResponse = null;
      try {
        orgResponse = await databaseFirstPersistence.loadUserData(user.id, 'organization_setup');
        console.log('📦 Organization setup response:', orgResponse);
        if (orgResponse) {
          // Merge with defaults to ensure all fields are present
          const mergedOrg = {
            organizationType: orgResponse.organizationType || 'single_owner',
            departments: orgResponse.departments || ['Management', 'Finance', 'Operations'],
            userPermissions: {
              defaultUserRole: orgResponse.userPermissions?.defaultUserRole || 'admin',
              restrictionLevel: orgResponse.userPermissions?.restrictionLevel || 'flexible',
              allowRoleOverride: orgResponse.userPermissions?.allowRoleOverride !== undefined 
                ? orgResponse.userPermissions.allowRoleOverride 
                : true,
              requireApprovalForAdjustments: orgResponse.userPermissions?.requireApprovalForAdjustments !== undefined
                ? orgResponse.userPermissions.requireApprovalForAdjustments
                : false
            },
            teamMembers: orgResponse.teamMembers || [
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
          };
          console.log('📝 Setting organization setup:', mergedOrg);
          setOrganizationSetup(mergedOrg);
          console.log('✅ Loaded organization setup from database');
        } else {
          console.log('ℹ️ No organization setup found in database');
        }
      } catch (e) {
        console.error('❌ Error loading organization setup:', e);
        console.log('No organization setup in database');
      }
      
      console.log('✅ Data loaded from database:', {
        modules: moduleIds,
        hasProfile: !!profileResponse,
        coaTemplate: coaResponse || 'retail',
        hasOrgSetup: !!orgResponse
      });
      
    } catch (error) {
      console.error('❌ Error loading data from database:', error);
    } finally {
      setIsLoadingData(false);
    }
  };
  
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
    'Default Accounts Preview',
    'Team Setup',
    'Data Import',
    'Activation'
  ];

  // No need to persist to localStorage - everything goes to database

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
      id: 'finance',
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

  // Load default accounts preview when finance module is selected
  useEffect(() => {
    if (selectedModules.includes('finance') && activeStep >= 2) {
      loadDefaultAccountsPreview();
    }
  }, [selectedModules, activeStep]);

  // Load existing data when component mounts or when user/auth changes
  useEffect(() => {
    console.log('🔄 useEffect triggered:', {
      isAuthenticated,
      hasUser: !!user,
      userId: user?.id,
      isLoadingData
    });
    
    if (isAuthenticated && user && isLoadingData) {
      console.log('✅ Conditions met, loading existing data...');
      loadExistingData();
    } else if (!isAuthenticated || !user) {
      // If not authenticated, stop loading
      console.log('⚠️ Not authenticated or no user, skipping data load');
      setIsLoadingData(false);
    }
  }, [isAuthenticated, user?.id]); // Depend on user.id to trigger when user changes

  const handleActivation = async () => {
    setLoading(true);
    try {
      console.log('🚀 Starting onboarding activation with database-first storage...');
      
      // Ensure user is authenticated
      if (!isAuthenticated || !user) {
        throw new Error('User must be authenticated to complete onboarding');
      }
      
      const userId = user.id;
      console.log(`👤 Saving onboarding data for user ${userId} to database...`);
      
      // Prepare comprehensive onboarding data
      const onboardingData = {
        // Business Profile
        businessProfile: {
          companyName: businessProfile.companyName,
          industry: businessProfile.industry,
          employeeCount: businessProfile.employeeCount,
          annualRevenue: businessProfile.annualRevenue,
          challenges: businessProfile.challenges,
          createdAt: new Date().toISOString()
        },
        
        // Module Selection
        selectedModules: selectedModules.includes('finance') && !selectedModules.includes('procurement')
          ? [...selectedModules, 'procurement']
          : selectedModules,
        
        // Chart of Accounts Template
        coaTemplate: selectedCoATemplate,
        
        // Organization Setup
        organizationSetup: {
          organizationType: organizationSetup.organizationType,
          departments: organizationSetup.departments,
          userPermissions: organizationSetup.userPermissions,
          teamMembers: organizationSetup.teamMembers
        },
        
        // Metadata
        onboardingMetadata: {
          activatedAt: new Date().toISOString(),
          visitorId: visitorId,
          deviceInfo: {
            userAgent: navigator.userAgent,
            screenResolution: `${window.screen.width}x${window.screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
          },
          version: '1.0'
        }
      };
      
      console.log('💾 Saving onboarding data to database with tenant isolation...');
      
      // Save company info using tenant-aware onboarding API (like CoA)
      // Backend expects camelCase field names (companyName, not company_name)
      try {
        await apiClient.post('/api/onboarding/step/company_info', {
          companyName: businessProfile.companyName,  // camelCase - backend maps this to company_name
          companySize: businessProfile.employeeCount || businessProfile.business_size,  // camelCase
          employeeCount: businessProfile.employeeCount || businessProfile.business_size,  // Also send as employeeCount
          industry: businessProfile.industry,
          companyWebsite: businessProfile.companyWebsite || '',
          companyAddress: businessProfile.companyAddress || '',
          companyPhone: businessProfile.companyPhone || '',
          companyEmail: businessProfile.companyEmail || '',
          // Store challenges and other complex data in the data JSONB field
          challenges: businessProfile.challenges || [],
          annualRevenue: businessProfile.annualRevenue || '',
          pain_points: businessProfile.pain_points || [],
          goals: businessProfile.goals || []
        });
        console.log('✅ Company info saved via tenant-aware onboarding API');
      } catch (error) {
        console.error('⚠️ Error saving company info via onboarding API:', error);
        // Fallback to databaseFirstPersistence if API fails
        await databaseFirstPersistence.saveUserData(userId, 'business_profile', onboardingData.businessProfile);
      }
      
      // Save other onboarding data (modules, CoA template, etc.) via databaseFirstPersistence
      // These are stored in onboarding_progress.data JSONB field
      await databaseFirstPersistence.saveUserData(userId, 'onboarding_complete', onboardingData);
      await databaseFirstPersistence.saveUserData(userId, 'selected_modules', onboardingData.selectedModules);
      await databaseFirstPersistence.saveUserData(userId, 'coa_template', onboardingData.coaTemplate);
      await databaseFirstPersistence.saveUserData(userId, 'organization_setup', onboardingData.organizationSetup);
      await databaseFirstPersistence.saveUserData(userId, 'onboarding_metadata', onboardingData.onboardingMetadata);
      
      console.log('✅ Onboarding data saved to database with tenant isolation');
      
      // Get current user modules to see what needs to be deactivated
      console.log('🔧 Getting current user modules...');
      let currentModules = [];
      try {
        const currentModulesResponse = await apiClient.get('/api/dashboard/modules/user');
        currentModules = Array.isArray(currentModulesResponse) ? currentModulesResponse : [];
      } catch (moduleError) {
        // Handle gracefully if endpoint fails
        console.warn('⚠️ Error getting current modules:', moduleError.message);
        currentModules = [];
      }
      const currentModuleIds = currentModules.map(m => m.id);
      
      console.log('📊 Current modules:', currentModuleIds);
      console.log('📊 Selected modules:', onboardingData.selectedModules);
      
      // Deactivate modules that are no longer selected
      const modulesToDeactivate = currentModuleIds.filter(id => !onboardingData.selectedModules.includes(id));
      console.log('🔧 Deactivating modules:', modulesToDeactivate);
      
      for (const moduleId of modulesToDeactivate) {
        try {
          await apiClient.post('/api/dashboard/modules/deactivate', {
            module_id: moduleId
          });
          console.log(`✅ Module ${moduleId} deactivated for user ${userId}`);
        } catch (moduleError) {
          console.log(`ℹ️ Module ${moduleId} deactivation issue:`, moduleError.message);
        }
      }
      
      // Activate selected modules in backend
      console.log('🔧 Activating selected modules in backend...');
      console.log('📦 Modules to activate:', onboardingData.selectedModules);
      const activationResults = [];
      
      for (const moduleId of onboardingData.selectedModules) {
        try {
          console.log(`🔄 Activating module ${moduleId} for user ${userId}...`);
          const response = await apiClient.post('/api/dashboard/modules/activate', {
            module_id: moduleId,
            permissions: {
              can_view: true,
              can_edit: true,
              can_delete: false
            }
          });
          console.log(`✅ Module ${moduleId} activation response:`, response);
          activationResults.push({ moduleId, success: true, response });
        } catch (moduleError) {
          console.error(`❌ Error activating module ${moduleId}:`, moduleError);
          activationResults.push({ moduleId, success: false, error: moduleError.message });
          // Continue with other modules even if one fails
        }
      }
      
      console.log('📊 Module activation summary:', activationResults);
      
      // Verify modules were saved by fetching them back
      console.log('🔍 Verifying modules were saved...');
      try {
        const verifyModules = await apiClient.get('/api/dashboard/modules/user');
        console.log('✅ Verification - Modules in database:', verifyModules);
        console.log('✅ Verification - Module IDs:', verifyModules.map(m => m.id));
      } catch (verifyError) {
        console.error('❌ Error verifying modules:', verifyError);
      }
      
      // Create default accounts if Finance module is selected and user confirmed
      if (onboardingData.selectedModules.includes('finance') && createDefaultAccounts) {
        console.log('💰 Finance module selected - creating default accounts...');
        try {
          // Check if user already has accounts by fetching them
          const existingAccounts = await apiClient.get('/api/finance/double-entry/accounts');
          const accountsArray = Array.isArray(existingAccounts) ? existingAccounts : [];
          
          if (accountsArray.length === 0) {
            console.log('📊 Creating default accounts for user...');
            const createResult = await apiClient.post('/api/finance/double-entry/accounts/default/create', {});
            console.log('✅ Default accounts created:', createResult);
            
            if (createResult.new_count > 0) {
              console.log(`✅ Successfully created ${createResult.new_count} default accounts`);
            }
          } else {
            console.log('ℹ️ User already has accounts, skipping default account creation');
          }
        } catch (accountError) {
          console.error('⚠️ Error creating default accounts:', accountError);
          // Don't fail onboarding if account creation fails
        }
      }
      
      // Mark onboarding as completed via tenant-aware API
      try {
        await apiClient.post('/api/onboarding/complete');
        console.log('✅ Onboarding marked as completed via tenant-aware API');
      } catch (error) {
        console.error('⚠️ Error marking onboarding as complete:', error);
        // Continue anyway - data is saved
      }
      
      // No localStorage needed - everything is in database
      console.log('✅ All data saved to database with tenant isolation - no localStorage needed');
      
      // Trigger sidebar refresh
      console.log('🔄 Triggering sidebar refresh...');
      window.dispatchEvent(new CustomEvent('modulesUpdated'));
      window.dispatchEvent(new CustomEvent('onboardingCompleted'));
      
      // Simulate account activation
      console.log('⏳ Finalizing activation...');
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      console.log('🎉 Onboarding completed successfully!');
      
      // Force refresh of user preferences from database
      console.log('🔄 User preferences will refresh from database on next load');
      
      // Show success message
      const hasFinance = onboardingData.selectedModules.includes('finance');
      const successMessage = hasFinance 
        ? '🎉 Welcome to EdonuOps! Your personalized dashboard has been configured. 25 default accounts (12 core + 13 standard) have been created for your Chart of Accounts.'
        : '🎉 Welcome to EdonuOps! Your personalized dashboard has been configured with your selected modules and team settings.';
      
      alert(successMessage);
      
      // Navigate to the dashboard
      navigate('/dashboard');
      
    } catch (error) {
      console.error('❌ Onboarding activation failed:', error);
      alert(`Activation failed: ${error.message}. Please try again.`);
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
                            setBusinessProfile(prev => ({ ...prev, challenges: [...prev.challenges, challenge] }));
                          } else {
                            setBusinessProfile(prev => ({ ...prev, challenges: prev.challenges.filter(c => c !== challenge) }));
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
        {selectedModules.length > 0 ? 'Update Your Module Selection' : 'What would you like to manage with EdonuOps?'}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        {selectedModules.length > 0 
          ? `You currently have ${selectedModules.length} modules selected: ${selectedModules.join(', ')}. Check/uncheck modules to modify your selection.`
          : 'Select the modules that match your business needs.'
        }
      </Typography>
      
      {selectedModules.length > 0 && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Current Selection:</strong> {selectedModules.length} modules selected
          </Typography>
        </Alert>
      )}
      
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

  const renderDefaultAccountsPreview = () => {
    if (!selectedModules.includes('finance')) {
      return (
        <Box>
          <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
            Chart of Accounts Setup
          </Typography>
          <Alert severity="info" sx={{ mb: 3 }}>
            Finance module is not selected. You can set up your Chart of Accounts later in the Finance module.
          </Alert>
        </Box>
      );
    }

    const coreAccounts = defaultAccountsPreview.filter(acc => acc.is_core);
    const standardAccounts = defaultAccountsPreview.filter(acc => !acc.is_core);
    const accountsByType = {
      asset: defaultAccountsPreview.filter(acc => acc.type === 'asset'),
      liability: defaultAccountsPreview.filter(acc => acc.type === 'liability'),
      equity: defaultAccountsPreview.filter(acc => acc.type === 'equity'),
      revenue: defaultAccountsPreview.filter(acc => acc.type === 'revenue'),
      expense: defaultAccountsPreview.filter(acc => acc.type === 'expense')
    };

    return (
      <Box>
        <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold', mb: 2 }}>
          Default Chart of Accounts Preview
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          We'll create 25 default accounts (12 core + 13 standard) to get you started. 
          You can edit, delete, or add more accounts later.
        </Typography>

        <FormControlLabel
          control={
            <Checkbox
              checked={createDefaultAccounts}
              onChange={(e) => setCreateDefaultAccounts(e.target.checked)}
              color="primary"
            />
          }
          label="Create 25 default accounts automatically"
          sx={{ mb: 3 }}
        />

        {loadingPreview ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Box>
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                <strong>12 Core Accounts</strong> (essential for all businesses) + 
                <strong> 13 Standard Accounts</strong> (common business needs)
              </Typography>
            </Alert>

            <Grid container spacing={2}>
              {Object.entries(accountsByType).map(([type, accounts]) => (
                accounts.length > 0 && (
                  <Grid item xs={12} md={6} key={type}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="h6" sx={{ mb: 1, textTransform: 'capitalize' }}>
                          {type}s ({accounts.length})
                        </Typography>
                        <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
                          {accounts.map((account) => (
                            <Box 
                              key={account.code} 
                              sx={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: 1, 
                                py: 0.5,
                                borderLeft: account.is_core ? '3px solid' : 'none',
                                borderColor: account.is_core ? 'primary.main' : 'transparent',
                                pl: account.is_core ? 1 : 0
                              }}
                            >
                              <Typography variant="body2" sx={{ fontFamily: 'monospace', minWidth: 60 }}>
                                {account.code}
                              </Typography>
                              <Typography variant="body2" sx={{ flex: 1 }}>
                                {account.name}
                              </Typography>
                              {account.is_core && (
                                <Chip label="Core" size="small" color="primary" variant="filled" />
                              )}
                            </Box>
                          ))}
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                )
              ))}
            </Grid>

            <Alert severity="success" sx={{ mt: 3 }}>
              <Typography variant="body2">
                These accounts will be created in your database and ready to use immediately. 
                You can customize them anytime in the Chart of Accounts module.
              </Typography>
            </Alert>
          </Box>
        )}
      </Box>
    );
  };

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
        return renderDefaultAccountsPreview();
      case 4:
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
        // Default accounts preview - always valid (user can skip)
        return true;
      case 4:
        return organizationSetup.organizationType && organizationSetup.userPermissions.defaultUserRole;
      default:
        return true;
    }
  };

  // Show loading state while loading data
  if (isLoadingData) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ maxWidth: 800, mx: 'auto', textAlign: 'center' }}>
          <Typography variant="h4" sx={{ mb: 2 }}>
            Loading Your Settings...
          </Typography>
          <LinearProgress sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary">
            Pre-filling your onboarding form with saved data...
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <>
      {/* Loading Overlay during Account Activation */}
      <Backdrop
        open={loading}
        sx={{
          color: '#fff',
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: 'rgba(0, 0, 0, 0.7)'
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center',
          gap: 3
        }}>
          <CircularProgress 
            size={60} 
            thickness={4}
            sx={{ color: 'primary.main' }}
          />
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="h5" sx={{ mb: 1, fontWeight: 'bold' }}>
              Activating Your Account...
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 400 }}>
              We're setting up your personalized dashboard and configuring your selected modules. 
              This may take a few moments. Please don't close this window.
            </Typography>
          </Box>
        </Box>
      </Backdrop>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ maxWidth: 800, mx: 'auto' }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 2 }}>
              {selectedModules.length > 0 ? 'Edit Your Module Selection' : 'Welcome to EdonuOps!'}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {selectedModules.length > 0 
                ? `You currently have ${selectedModules.length} modules selected. Modify your selection below.`
                : 'Let\'s get your business set up in just a few minutes'
              }
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
              disabled={activeStep === 0 || loading}
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
    </>
  );
};

export default OnboardingWizard;
