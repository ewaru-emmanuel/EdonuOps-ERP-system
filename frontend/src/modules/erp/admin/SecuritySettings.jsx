import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Button, TextField, Switch,
  FormControl, InputLabel, Select, MenuItem, Alert, Divider, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Dialog, DialogTitle, DialogContent, DialogActions, Tab, Tabs, IconButton,
  Tooltip, LinearProgress
} from '@mui/material';
import {
  Security, Password, Storage, History, Lock,
  Refresh, Save, Edit, Delete, Visibility, VisibilityOff, QrCode,
  Smartphone, Email, Phone, Warning, CheckCircle, Cancel
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';
import PermissionGuard from '../../../components/PermissionGuard';

const SecuritySettings = () => {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  
  // Password Policy State
  const [passwordPolicy, setPasswordPolicy] = useState({
    min_length: 8,
    max_length: 128,
    require_uppercase: true,
    require_lowercase: true,
    require_numbers: true,
    require_special_chars: true,
    special_chars: '!@#$%^&*()_+-=[]{}|;:,.<>?',
    prevent_common_passwords: true,
    prevent_username_in_password: true,
    prevent_recent_passwords: true,
    recent_password_count: 5,
    password_expiry_days: 90,
    warn_before_expiry_days: 7
  });
  
  // Session Policy State
  const [sessionPolicy, setSessionPolicy] = useState({
    session_timeout_minutes: 30,
    max_concurrent_sessions: 3,
    inactive_timeout_minutes: 15,
    extend_on_activity: true,
    require_reauth_for_sensitive: true
  });
  
  // Login Policy State
  const [loginPolicy, setLoginPolicy] = useState({
    max_failed_attempts: 5,
    lockout_duration_minutes: 30,
    permanent_lockout_after: 10,
    track_suspicious_activity: true,
    require_email_verification: true
  });
  
  // 2FA State
  const [twoFactorStatus, setTwoFactorStatus] = useState(null);
  const [twoFactorSetup, setTwoFactorSetup] = useState({
    secret_key: '',
    qr_uri: '',
    token: '',
    backup_codes: []
  });
  const [showSecret, setShowSecret] = useState(false);
  
  // Security Events State
  const [securityEvents, setSecurityEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  
  // Fetch current policies
  const { data: policiesData, loading: policiesLoading } = useRealTimeData(
    '/security/policies',
    'security-policies'
  );
  
  // Fetch 2FA status
  const { data: twoFactorData, loading: twoFactorLoading } = useRealTimeData(
    '/security/2fa/status',
    'two-factor-status'
  );
  
  // Fetch security events
  const { data: eventsData, loading: eventsLoading } = useRealTimeData(
    '/security/events?limit=50',
    'security-events'
  );
  
  useEffect(() => {
    if (policiesData) {
      // Load policies into state
      const passwordPolicyData = policiesData.find(p => p.policy_name === 'password_policy');
      const sessionPolicyData = policiesData.find(p => p.policy_name === 'session_policy');
      const loginPolicyData = policiesData.find(p => p.policy_name === 'login_policy');
      
      if (passwordPolicyData) {
        setPasswordPolicy(prev => ({ ...prev, ...passwordPolicyData.configuration }));
      }
      if (sessionPolicyData) {
        setSessionPolicy(prev => ({ ...prev, ...sessionPolicyData.configuration }));
      }
      if (loginPolicyData) {
        setLoginPolicy(prev => ({ ...prev, ...loginPolicyData.configuration }));
      }
    }
  }, [policiesData]);
  
  useEffect(() => {
    if (twoFactorData) {
      setTwoFactorStatus(twoFactorData);
    }
  }, [twoFactorData]);
  
  useEffect(() => {
    if (eventsData) {
      // Handle both array format and object format with data field
      if (Array.isArray(eventsData)) {
        setSecurityEvents(eventsData);
      } else if (eventsData.data && Array.isArray(eventsData.data)) {
        setSecurityEvents(eventsData.data);
      } else if (eventsData.success && eventsData.data && Array.isArray(eventsData.data)) {
        setSecurityEvents(eventsData.data);
      } else {
        setSecurityEvents([]);
      }
    } else {
      setSecurityEvents([]);
    }
  }, [eventsData]);
  
  const handlePolicyChange = (policyType, field, value) => {
    switch (policyType) {
      case 'password':
        setPasswordPolicy(prev => ({ ...prev, [field]: value }));
        break;
      case 'session':
        setSessionPolicy(prev => ({ ...prev, [field]: value }));
        break;
      case 'login':
        setLoginPolicy(prev => ({ ...prev, [field]: value }));
        break;
      default:
        console.warn(`Unknown policy type: ${policyType}`);
        break;
    }
  };
  
  const savePolicy = async (policyType) => {
    setSaving(true);
    try {
      let policyName, configuration;
      
      switch (policyType) {
        case 'password':
          policyName = 'password_policy';
          configuration = passwordPolicy;
          break;
        case 'session':
          policyName = 'session_policy';
          configuration = sessionPolicy;
          break;
        case 'login':
          policyName = 'login_policy';
          configuration = loginPolicy;
          break;
        default:
          console.error(`Unknown policy type: ${policyType}`);
          return;
      }
      
      const response = await apiClient.post('/security/policies', {
        policy_name: policyName,
        policy_type: policyType.toUpperCase(),
        configuration: configuration,
        is_enabled: true
      });
      
      if (response.success) {
        // Show success message
        console.log(`${policyType} policy saved successfully`);
      }
    } catch (error) {
      console.error('Error saving policy:', error);
    } finally {
      setSaving(false);
    }
  };
  
  const setupTwoFactor = async () => {
    try {
      const response = await apiClient.post('/security/2fa/setup');
      if (response.success) {
        setTwoFactorSetup({
          secret_key: response.data.secret_key,
          qr_uri: response.data.qr_uri,
          token: '',
          backup_codes: []
        });
      }
    } catch (error) {
      console.error('Error setting up 2FA:', error);
    }
  };
  
  const verifyTwoFactor = async () => {
    try {
      const response = await apiClient.post('/security/2fa/verify', {
        token: twoFactorSetup.token
      });
      
      if (response.success) {
        setTwoFactorSetup(prev => ({ ...prev, token: '' }));
        // Refresh 2FA status
        window.location.reload();
      }
    } catch (error) {
      console.error('Error verifying 2FA:', error);
    }
  };
  
  const disableTwoFactor = async () => {
    const password = prompt('Enter your password to disable 2FA:');
    if (!password) return;
    
    try {
      const response = await apiClient.post('/security/2fa/disable', {
        password: password
      });
      
      if (response.success) {
        // Refresh 2FA status
        window.location.reload();
      }
    } catch (error) {
      console.error('Error disabling 2FA:', error);
    }
  };
  
  const getSeverityColor = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return 'error';
      case 'ERROR': return 'error';
      case 'WARNING': return 'warning';
      case 'INFO': return 'info';
      default: return 'default';
    }
  };
  
  const getSeverityIcon = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
      case 'ERROR': return <Cancel color="error" />;
      case 'WARNING': return <Warning color="warning" />;
      case 'INFO': return <CheckCircle color="info" />;
      default: return <Security />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Security color="primary" />
        Security Settings
      </Typography>

      <Tabs value={tab} onChange={(e, v) => setTab(v)} sx={{ mb: 3 }}>
        <Tab 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Password />
              Password Policy
            </Box>
          } 
        />
        <Tab 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Storage />
              Session Management
            </Box>
          } 
        />
        <Tab 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Lock />
              Two-Factor Auth
            </Box>
          } 
        />
        <Tab 
          label={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <History />
              Security Events
            </Box>
          } 
        />
      </Tabs>

      {/* Password Policy Tab */}
      {tab === 0 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Password Security Policy</Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>Password Requirements</Typography>
                
                <Box sx={{ mb: 2 }}>
                  <TextField
                    fullWidth
                    label="Minimum Length"
                    type="number"
                    value={passwordPolicy.min_length}
                    onChange={(e) => handlePolicyChange('password', 'min_length', parseInt(e.target.value))}
                    inputProps={{ min: 4, max: 50 }}
                  />
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <TextField
                    fullWidth
                    label="Maximum Length"
                    type="number"
                    value={passwordPolicy.max_length}
                    onChange={(e) => handlePolicyChange('password', 'max_length', parseInt(e.target.value))}
                    inputProps={{ min: 8, max: 128 }}
                  />
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <TextField
                    fullWidth
                    label="Special Characters"
                    value={passwordPolicy.special_chars}
                    onChange={(e) => handlePolicyChange('password', 'special_chars', e.target.value)}
                  />
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>Character Requirements</Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Switch
                    checked={passwordPolicy.require_uppercase}
                    onChange={(e) => handlePolicyChange('password', 'require_uppercase', e.target.checked)}
                  />
                  <Typography>Require uppercase letters (A-Z)</Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Switch
                    checked={passwordPolicy.require_lowercase}
                    onChange={(e) => handlePolicyChange('password', 'require_lowercase', e.target.checked)}
                  />
                  <Typography>Require lowercase letters (a-z)</Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Switch
                    checked={passwordPolicy.require_numbers}
                    onChange={(e) => handlePolicyChange('password', 'require_numbers', e.target.checked)}
                  />
                  <Typography>Require numbers (0-9)</Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Switch
                    checked={passwordPolicy.require_special_chars}
                    onChange={(e) => handlePolicyChange('password', 'require_special_chars', e.target.checked)}
                  />
                  <Typography>Require special characters</Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>Security Restrictions</Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Switch
                    checked={passwordPolicy.prevent_common_passwords}
                    onChange={(e) => handlePolicyChange('password', 'prevent_common_passwords', e.target.checked)}
                  />
                  <Typography>Prevent common passwords</Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Switch
                    checked={passwordPolicy.prevent_username_in_password}
                    onChange={(e) => handlePolicyChange('password', 'prevent_username_in_password', e.target.checked)}
                  />
                  <Typography>Prevent username in password</Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Switch
                    checked={passwordPolicy.prevent_recent_passwords}
                    onChange={(e) => handlePolicyChange('password', 'prevent_recent_passwords', e.target.checked)}
                  />
                  <Typography>Prevent recent password reuse</Typography>
                </Box>
                
                <TextField
                  fullWidth
                  label="Recent Password Count"
                  type="number"
                  value={passwordPolicy.recent_password_count}
                  onChange={(e) => handlePolicyChange('password', 'recent_password_count', parseInt(e.target.value))}
                  disabled={!passwordPolicy.prevent_recent_passwords}
                  inputProps={{ min: 1, max: 10 }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" gutterBottom>Password Expiry</Typography>
                
                <TextField
                  fullWidth
                  label="Password Expiry (days)"
                  type="number"
                  value={passwordPolicy.password_expiry_days}
                  onChange={(e) => handlePolicyChange('password', 'password_expiry_days', parseInt(e.target.value))}
                  inputProps={{ min: 0, max: 365 }}
                  sx={{ mb: 2 }}
                />
                
                <TextField
                  fullWidth
                  label="Warning Before Expiry (days)"
                  type="number"
                  value={passwordPolicy.warn_before_expiry_days}
                  onChange={(e) => handlePolicyChange('password', 'warn_before_expiry_days', parseInt(e.target.value))}
                  inputProps={{ min: 1, max: 30 }}
                />
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 3 }} />
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={() => savePolicy('password')}
                disabled={saving}
              >
                Save Password Policy
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Session Management Tab */}
      {tab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Session Management Policy</Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Session Timeout (minutes)"
                  type="number"
                  value={sessionPolicy.session_timeout_minutes}
                  onChange={(e) => handlePolicyChange('session', 'session_timeout_minutes', parseInt(e.target.value))}
                  inputProps={{ min: 5, max: 480 }}
                  sx={{ mb: 2 }}
                />
                
                <TextField
                  fullWidth
                  label="Max Concurrent Sessions"
                  type="number"
                  value={sessionPolicy.max_concurrent_sessions}
                  onChange={(e) => handlePolicyChange('session', 'max_concurrent_sessions', parseInt(e.target.value))}
                  inputProps={{ min: 1, max: 10 }}
                  sx={{ mb: 2 }}
                />
                
                <TextField
                  fullWidth
                  label="Inactive Timeout (minutes)"
                  type="number"
                  value={sessionPolicy.inactive_timeout_minutes}
                  onChange={(e) => handlePolicyChange('session', 'inactive_timeout_minutes', parseInt(e.target.value))}
                  inputProps={{ min: 5, max: 120 }}
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Switch
                    checked={sessionPolicy.extend_on_activity}
                    onChange={(e) => handlePolicyChange('session', 'extend_on_activity', e.target.checked)}
                  />
                  <Typography>Extend session on activity</Typography>
                </Box>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Switch
                    checked={sessionPolicy.require_reauth_for_sensitive}
                    onChange={(e) => handlePolicyChange('session', 'require_reauth_for_sensitive', e.target.checked)}
                  />
                  <Typography>Require re-authentication for sensitive operations</Typography>
                </Box>
              </Grid>
            </Grid>
            
            <Divider sx={{ my: 3 }} />
            
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={() => savePolicy('session')}
                disabled={saving}
              >
                Save Session Policy
              </Button>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Two-Factor Authentication Tab */}
      {tab === 2 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Two-Factor Authentication</Typography>
            
            {twoFactorLoading ? (
              <LinearProgress />
            ) : (
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>Current Status</Typography>
                      
                      {twoFactorStatus?.is_enabled ? (
                        <Alert severity="success" icon={<CheckCircle />}>
                          2FA is enabled and active
                        </Alert>
                      ) : twoFactorStatus?.is_setup ? (
                        <Alert severity="warning" icon={<Warning />}>
                          2FA is set up but not enabled
                        </Alert>
                      ) : (
                        <Alert severity="info" icon={<Security />}>
                          2FA is not set up
                        </Alert>
                      )}
                      
                      {twoFactorStatus?.is_setup && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            Created: {new Date(twoFactorStatus.created_at).toLocaleString()}
                          </Typography>
                          {twoFactorStatus.last_used && (
                            <Typography variant="body2" color="text.secondary">
                              Last used: {new Date(twoFactorStatus.last_used).toLocaleString()}
                            </Typography>
                          )}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>Actions</Typography>
                      
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {!twoFactorStatus?.is_setup && (
                          <Button
                            variant="contained"
                            startIcon={<QrCode />}
                            onClick={setupTwoFactor}
                            fullWidth
                          >
                            Setup 2FA
                          </Button>
                        )}
                        
                        {twoFactorStatus?.is_setup && !twoFactorStatus?.is_enabled && (
                          <Button
                            variant="contained"
                            startIcon={<CheckCircle />}
                            onClick={() => setTab(2)}
                            fullWidth
                          >
                            Complete 2FA Setup
                          </Button>
                        )}
                        
                        {twoFactorStatus?.is_enabled && (
                          <Button
                            variant="outlined"
                            color="error"
                            startIcon={<Cancel />}
                            onClick={disableTwoFactor}
                            fullWidth
                          >
                            Disable 2FA
                          </Button>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                
                {/* 2FA Setup Form */}
                {twoFactorSetup.secret_key && (
                  <Grid item xs={12}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle1" gutterBottom>Complete 2FA Setup</Typography>
                        
                        <Alert severity="info" sx={{ mb: 2 }}>
                          Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
                        </Alert>
                        
                        <Grid container spacing={2}>
                          <Grid item xs={12} md={6}>
                            <Typography variant="body2" gutterBottom>Secret Key:</Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <TextField
                                value={showSecret ? twoFactorSetup.secret_key : '••••••••••••••••'}
                                InputProps={{ readOnly: true }}
                                size="small"
                                fullWidth
                              />
                              <IconButton onClick={() => setShowSecret(!showSecret)}>
                                {showSecret ? <VisibilityOff /> : <Visibility />}
                              </IconButton>
                            </Box>
                          </Grid>
                          
                          <Grid item xs={12} md={6}>
                            <Typography variant="body2" gutterBottom>Verification Code:</Typography>
                            <Box sx={{ display: 'flex', gap: 1 }}>
                              <TextField
                                placeholder="Enter 6-digit code"
                                value={twoFactorSetup.token}
                                onChange={(e) => setTwoFactorSetup(prev => ({ ...prev, token: e.target.value }))}
                                inputProps={{ maxLength: 6 }}
                                size="small"
                                fullWidth
                              />
                              <Button
                                variant="contained"
                                onClick={verifyTwoFactor}
                                disabled={twoFactorSetup.token.length !== 6}
                              >
                                Verify
                              </Button>
                            </Box>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
              </Grid>
            )}
          </CardContent>
        </Card>
      )}

      {/* Security Events Tab */}
      {tab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>Recent Security Events</Typography>
            
            {eventsLoading ? (
              <LinearProgress />
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Timestamp</TableCell>
                      <TableCell>Event Type</TableCell>
                      <TableCell>Severity</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>User</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {securityEvents.map((event, index) => (
                      <TableRow key={event.id || `event-${index}`}>
                        <TableCell>
                          {new Date(event.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell>{event.event_type}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getSeverityIcon(event.severity)}
                            <Chip 
                              label={event.severity} 
                              size="small" 
                              color={getSeverityColor(event.severity)}
                            />
                          </Box>
                        </TableCell>
                        <TableCell>{event.description}</TableCell>
                        <TableCell>{event.user_id || 'System'}</TableCell>
                        <TableCell>
                          {event.resolved ? (
                            <Chip label="Resolved" size="small" color="success" />
                          ) : (
                            <Chip label="Open" size="small" color="warning" />
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default SecuritySettings;
