import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Avatar,
  Divider,
  Alert,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  useTheme,
  CircularProgress
} from '@mui/material';
import {
  Person as PersonIcon,
  Email as EmailIcon,
  Business as BusinessIcon,
  Settings as SettingsIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Palette as PaletteIcon,
  Language as LanguageIcon,
  AccountBalance as AccountBalanceIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import { useUserPreferences } from '../hooks/useUserPreferences';
import databaseFirstPersistence from '../services/databaseFirstPersistence';
import apiClient from '../services/apiClient';

const UserProfile = () => {
  const theme = useTheme();
  const { user, isAuthenticated } = useAuth();
  const { userPreferences, updatePreferences, isLoading, error } = useUserPreferences();
  
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    company_name: '',
    industry: '',
    business_size: '',
    employee_count: '',
    annual_revenue: '',
    challenges: [],
    theme: 'light',
    language: 'en',
    default_currency: 'USD',
    timezone: 'UTC',
    date_format: 'YYYY-MM-DD',
    notifications_enabled: true
  });
  const [loading, setLoading] = useState(false);
  const [dataLoading, setDataLoading] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [changePasswordOpen, setChangePasswordOpen] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [onboardingData, setOnboardingData] = useState(null);
  const [businessProfile, setBusinessProfile] = useState(null);

  // Load user data from database when component mounts
  useEffect(() => {
    const loadUserData = async () => {
      if (!user || !isAuthenticated) {
        setDataLoading(false);
        return;
      }

      try {
        setDataLoading(true);
        console.log('🔄 Loading user profile data from database...');

        // Load onboarding data from database
        const onboardingData = await databaseFirstPersistence.loadUserData(user.id, 'onboarding_complete');
        const businessProfile = await databaseFirstPersistence.loadUserData(user.id, 'business_profile');
        const selectedModules = await databaseFirstPersistence.loadUserData(user.id, 'selected_modules');
        const organizationSetup = await databaseFirstPersistence.loadUserData(user.id, 'organization_setup');

        console.log('📊 Loaded user data:', {
          onboardingData: !!onboardingData,
          businessProfile: !!businessProfile,
          selectedModules: !!selectedModules,
          organizationSetup: !!organizationSetup
        });

        // Set state
        setOnboardingData(onboardingData);
        setBusinessProfile(businessProfile);

        // Populate form data with database values
        const profileData = {
          username: user.username || '',
          email: user.email || '',
          company_name: businessProfile?.companyName || onboardingData?.businessProfile?.companyName || '',
          industry: businessProfile?.industry || onboardingData?.businessProfile?.industry || '',
          business_size: businessProfile?.employeeCount || onboardingData?.businessProfile?.employeeCount || '',
          employee_count: businessProfile?.employeeCount || onboardingData?.businessProfile?.employeeCount || '',
          annual_revenue: businessProfile?.annualRevenue || onboardingData?.businessProfile?.annualRevenue || '',
          challenges: businessProfile?.challenges || onboardingData?.businessProfile?.challenges || [],
          theme: userPreferences?.theme || 'light',
          language: userPreferences?.language || 'en',
          default_currency: userPreferences?.default_currency || 'USD',
          timezone: userPreferences?.timezone || 'UTC',
          date_format: userPreferences?.date_format || 'YYYY-MM-DD',
          notifications_enabled: userPreferences?.notifications_enabled !== false
        };

        setFormData(profileData);
        console.log('✅ Profile data populated:', profileData);

      } catch (error) {
        console.error('❌ Error loading user profile data:', error);
        
        // Fallback to basic user data
        setFormData({
          username: user.username || '',
          email: user.email || '',
          company_name: '',
          industry: '',
          business_size: '',
          employee_count: '',
          annual_revenue: '',
          challenges: [],
          theme: userPreferences?.theme || 'light',
          language: userPreferences?.language || 'en',
          default_currency: userPreferences?.default_currency || 'USD',
          timezone: userPreferences?.timezone || 'UTC',
          date_format: userPreferences?.date_format || 'YYYY-MM-DD',
          notifications_enabled: userPreferences?.notifications_enabled !== false
        });
      } finally {
        setDataLoading(false);
      }
    };

    loadUserData();
  }, [user, isAuthenticated, userPreferences]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      console.log('💾 Saving profile data to database...');
      
      // Save updated business profile to database
      const updatedBusinessProfile = {
        companyName: formData.company_name,
        industry: formData.industry,
        employeeCount: formData.employee_count,
        annualRevenue: formData.annual_revenue,
        challenges: formData.challenges,
        updatedAt: new Date().toISOString()
      };

      await databaseFirstPersistence.saveUserData(user.id, 'business_profile', updatedBusinessProfile);
      
      // Update user preferences in backend
      await updatePreferences(formData);
      
      // Update local state
      setBusinessProfile(updatedBusinessProfile);
      
      setEditMode(false);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      
      console.log('✅ Profile data saved successfully');
    } catch (error) {
      console.error('❌ Error saving profile:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    // Reset form data to original values from database
    if (businessProfile) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        company_name: businessProfile.companyName || '',
        industry: businessProfile.industry || '',
        business_size: businessProfile.employeeCount || '',
        employee_count: businessProfile.employeeCount || '',
        annual_revenue: businessProfile.annualRevenue || '',
        challenges: businessProfile.challenges || [],
        theme: userPreferences?.theme || 'light',
        language: userPreferences?.language || 'en',
        default_currency: userPreferences?.default_currency || 'USD',
        timezone: userPreferences?.timezone || 'UTC',
        date_format: userPreferences?.date_format || 'YYYY-MM-DD',
        notifications_enabled: userPreferences?.notifications_enabled !== false
      });
    }
    setEditMode(false);
  };

  const handleChangePassword = async () => {
    // TODO: Implement password change functionality
    console.log('Change password:', passwordData);
    setChangePasswordOpen(false);
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error">
          Please log in to view your profile.
        </Alert>
      </Container>
    );
  }

  if (isLoading || dataLoading) {
    return (
      <Container maxWidth="md" sx={{ mt: 4, textAlign: 'center' }}>
        <CircularProgress sx={{ mb: 2 }} />
        <Typography>Loading profile data from database...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          User Profile
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage your account settings and preferences
        </Typography>
      </Box>

      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Profile updated successfully!
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Profile Overview */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar
                sx={{
                  width: 80,
                  height: 80,
                  mx: 'auto',
                  mb: 2,
                  bgcolor: theme.palette.primary.main
                }}
              >
                <PersonIcon sx={{ fontSize: 40 }} />
              </Avatar>
              <Typography variant="h6" gutterBottom>
                {user?.username || 'User'}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {user?.email || 'No email'}
              </Typography>
              <Chip
                label={`ID: ${user?.id || 'Unknown'}`}
                size="small"
                variant="outlined"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Profile Details */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">Profile Information</Typography>
                {!editMode ? (
                  <Button
                    startIcon={<EditIcon />}
                    onClick={() => setEditMode(true)}
                    variant="outlined"
                  >
                    Edit
                  </Button>
                ) : (
                  <Box>
                    <Button
                      startIcon={<SaveIcon />}
                      onClick={handleSave}
                      variant="contained"
                      disabled={loading}
                      sx={{ mr: 1 }}
                    >
                      Save
                    </Button>
                    <Button
                      startIcon={<CancelIcon />}
                      onClick={handleCancel}
                      variant="outlined"
                    >
                      Cancel
                    </Button>
                  </Box>
                )}
              </Box>

              <Grid container spacing={3}>
                {/* Basic Information */}
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <PersonIcon sx={{ mr: 1, fontSize: 20 }} />
                    Basic Information
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Username"
                    value={formData.username}
                    onChange={(e) => handleInputChange('username', e.target.value)}
                    disabled={!editMode}
                    variant={editMode ? 'outlined' : 'filled'}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Email"
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    disabled={!editMode}
                    variant={editMode ? 'outlined' : 'filled'}
                  />
                </Grid>

                {/* Business Information */}
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                    <BusinessIcon sx={{ mr: 1, fontSize: 20 }} />
                    Business Information
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Company Name"
                    value={formData.company_name}
                    onChange={(e) => handleInputChange('company_name', e.target.value)}
                    disabled={!editMode}
                    variant={editMode ? 'outlined' : 'filled'}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Industry"
                    value={formData.industry}
                    onChange={(e) => handleInputChange('industry', e.target.value)}
                    disabled={!editMode}
                    variant={editMode ? 'outlined' : 'filled'}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Employee Count"
                    value={formData.employee_count}
                    onChange={(e) => handleInputChange('employee_count', e.target.value)}
                    disabled={!editMode}
                    variant={editMode ? 'outlined' : 'filled'}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Annual Revenue"
                    value={formData.annual_revenue}
                    onChange={(e) => handleInputChange('annual_revenue', e.target.value)}
                    disabled={!editMode}
                    variant={editMode ? 'outlined' : 'filled'}
                  />
                </Grid>

                {formData.challenges && formData.challenges.length > 0 && (
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Business Challenges"
                      value={formData.challenges.join(', ')}
                      disabled={true}
                      variant="filled"
                      multiline
                      rows={2}
                    />
                  </Grid>
                )}

                {/* Preferences */}
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
                    <SettingsIcon sx={{ mr: 1, fontSize: 20 }} />
                    Preferences
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Default Currency"
                    value={formData.default_currency}
                    onChange={(e) => handleInputChange('default_currency', e.target.value)}
                    disabled={!editMode}
                    variant={editMode ? 'outlined' : 'filled'}
                  />
                </Grid>

                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Timezone"
                    value={formData.timezone}
                    onChange={(e) => handleInputChange('timezone', e.target.value)}
                    disabled={!editMode}
                    variant={editMode ? 'outlined' : 'filled'}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Onboarding Status */}
        {onboardingData && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <BusinessIcon sx={{ mr: 1, fontSize: 20 }} />
                  Onboarding Status
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Onboarding Completed
                    </Typography>
                    <Typography variant="body1" fontWeight="medium">
                      {onboardingData.onboardingMetadata?.activatedAt ? 
                        new Date(onboardingData.onboardingMetadata.activatedAt).toLocaleDateString() : 
                        'Unknown'
                      }
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Selected Modules
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                      {onboardingData.selectedModules?.map((module, index) => (
                        <Chip
                          key={index}
                          label={module}
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <List>
                <ListItem
                  button
                  onClick={() => setChangePasswordOpen(true)}
                  sx={{ borderRadius: 1 }}
                >
                  <ListItemIcon>
                    <SecurityIcon />
                  </ListItemIcon>
                  <ListItemText primary="Change Password" secondary="Update your account password" />
                </ListItem>
                <ListItem
                  button
                  onClick={() => window.location.href = '/onboarding'}
                  sx={{ borderRadius: 1 }}
                >
                  <ListItemIcon>
                    <SettingsIcon />
                  </ListItemIcon>
                  <ListItemText primary="Reconfigure Modules" secondary="Update your module preferences" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Change Password Dialog */}
      <Dialog open={changePasswordOpen} onClose={() => setChangePasswordOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Change Password</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Current Password"
            type="password"
            value={passwordData.currentPassword}
            onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
            margin="normal"
          />
          <TextField
            fullWidth
            label="New Password"
            type="password"
            value={passwordData.newPassword}
            onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Confirm New Password"
            type="password"
            value={passwordData.confirmPassword}
            onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setChangePasswordOpen(false)}>Cancel</Button>
          <Button onClick={handleChangePassword} variant="contained">Change Password</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default UserProfile;







