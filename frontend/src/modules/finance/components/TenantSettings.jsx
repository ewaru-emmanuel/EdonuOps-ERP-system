import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Divider,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Business as BusinessIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Palette as PaletteIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon
} from '@mui/icons-material';
import { useTenant } from '../../../contexts/TenantContext';
import { useTenantApi } from '../../../hooks/useTenantApi';

const TenantSettings = () => {
  const { currentTenant, getTenantInfo, getTenantModules } = useTenant();
  const { get, post, put } = useTenantApi();
  
  const [tenantInfo, setTenantInfo] = useState(null);
  const [modules, setModules] = useState([]);
  const [settings, setSettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingSetting, setEditingSetting] = useState(null);

  useEffect(() => {
    loadTenantData();
  }, [currentTenant]);

  const loadTenantData = async () => {
    if (!currentTenant) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // Load tenant info and modules in parallel
      const [info, moduleData] = await Promise.all([
        getTenantInfo(),
        getTenantModules()
      ]);
      
      setTenantInfo(info);
      setModules(moduleData);
      
      // Load tenant settings
      const settingsData = await get(`/api/tenant/tenants/${currentTenant.tenant_id}/settings`);
      setSettings(settingsData);
      
    } catch (err) {
      console.error('Error loading tenant data:', err);
      setError('Failed to load tenant information');
    } finally {
      setLoading(false);
    }
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSaveSettings = async () => {
    try {
      setSaving(true);
      setError(null);
      
      // Save each setting
      for (const [key, value] of Object.entries(settings)) {
        try {
          await post(`/api/tenant/tenants/${currentTenant.tenant_id}/settings`, {
            setting_key: key,
            setting_value: value,
            setting_type: typeof value === 'boolean' ? 'boolean' : 'string'
          });
        } catch (err) {
          console.error(`Error saving setting ${key}:`, err);
        }
      }
      
      setSuccess('Settings saved successfully');
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      console.error('Error saving settings:', err);
      setError('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleEditSetting = (setting) => {
    setEditingSetting(setting);
    setEditDialogOpen(true);
  };

  const handleUpdateSetting = async (key, value) => {
    try {
      await put(`/api/tenant/tenants/${currentTenant.tenant_id}/settings/${key}`, {
        setting_value: value
      });
      
      setSettings(prev => ({
        ...prev,
        [key]: value
      }));
      
      setEditDialogOpen(false);
      setEditingSetting(null);
      setSuccess('Setting updated successfully');
      setTimeout(() => setSuccess(null), 3000);
      
    } catch (err) {
      console.error('Error updating setting:', err);
      setError('Failed to update setting');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!currentTenant) {
    return (
      <Alert severity="warning">
        No tenant selected. Please select a tenant to view settings.
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Tenant Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage settings and configurations for {currentTenant.tenant_name}
        </Typography>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Tenant Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <BusinessIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Tenant Information
                </Typography>
              </Box>
              
              {tenantInfo && (
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Name:</strong> {tenantInfo.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Domain:</strong> {tenantInfo.domain || 'Not set'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Plan:</strong> 
                    <Chip 
                      label={tenantInfo.subscription_plan} 
                      size="small" 
                      color="primary" 
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Status:</strong> 
                    <Chip 
                      label={tenantInfo.status} 
                      size="small" 
                      color={tenantInfo.status === 'active' ? 'success' : 'warning'}
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Created:</strong> {new Date(tenantInfo.created_at).toLocaleDateString()}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Active Modules */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <SettingsIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Active Modules
                </Typography>
              </Box>
              
              <List>
                {modules.map((module) => (
                  <ListItem key={module.module_name}>
                    <ListItemText
                      primary={module.module_name}
                      secondary={`Activated: ${new Date(module.activated_at).toLocaleDateString()}`}
                    />
                    <ListItemSecondaryAction>
                      <Chip 
                        label={module.enabled ? 'Enabled' : 'Disabled'} 
                        size="small" 
                        color={module.enabled ? 'success' : 'default'}
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* General Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <PaletteIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  General Settings
                </Typography>
              </Box>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.auto_reconciliation || false}
                        onChange={(e) => handleSettingChange('auto_reconciliation', e.target.checked)}
                      />
                    }
                    label="Auto Reconciliation"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.email_notifications || false}
                        onChange={(e) => handleSettingChange('email_notifications', e.target.checked)}
                      />
                    }
                    label="Email Notifications"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Default Currency"
                    value={settings.currency || 'USD'}
                    onChange={(e) => handleSettingChange('currency', e.target.value)}
                    variant="outlined"
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Date Format"
                    value={settings.date_format || 'YYYY-MM-DD'}
                    onChange={(e) => handleSettingChange('date_format', e.target.value)}
                    variant="outlined"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Custom Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <SecurityIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Custom Settings
                </Typography>
              </Box>
              
              <List>
                {Object.entries(settings).map(([key, value]) => (
                  <ListItem key={key}>
                    <ListItemText
                      primary={key.replace(/_/g, ' ').toUpperCase()}
                      secondary={typeof value === 'boolean' ? (value ? 'Enabled' : 'Disabled') : value}
                    />
                    <ListItemSecondaryAction>
                      <IconButton onClick={() => handleEditSetting({ key, value })}>
                        <EditIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Save Button */}
      <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
        
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={loadTenantData}
        >
          Refresh
        </Button>
      </Box>

      {/* Edit Setting Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)}>
        <DialogTitle>Edit Setting</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Value"
            value={editingSetting?.value || ''}
            onChange={(e) => setEditingSetting(prev => ({ ...prev, value: e.target.value }))}
            variant="outlined"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={() => handleUpdateSetting(editingSetting?.key, editingSetting?.value)}
            variant="contained"
          >
            Update
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TenantSettings;












