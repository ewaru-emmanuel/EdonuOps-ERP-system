import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Divider,
  Alert,
  Tabs,
  Tab,
  Chip
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';
import SettingsIcon from '@mui/icons-material/Settings';
import PeopleIcon from '@mui/icons-material/People';
import StoreIcon from '@mui/icons-material/Store';
import Inventory2Icon from '@mui/icons-material/Inventory2';
import WorkIcon from '@mui/icons-material/Work';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import PsychologyIcon from '@mui/icons-material/Psychology';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { useUserPreferences } from '../../../hooks/useUserPreferences';
import { useVisitorSession } from '../../../hooks/useVisitorSession';

const DashboardSettings = () => {
  // New: Bring over gear-modal content into this page
  const { selectedModules, updatePreferences, isModuleEnabled } = useUserPreferences();
  const { visitorId, sessionId, isSessionValid } = useVisitorSession();
  const [activeTab, setActiveTab] = useState(0);

  const allModules = [
    { id: 'crm', name: 'Customer Relationship Management', icon: <PeopleIcon sx={{ fontSize: 20 }} />, description: 'Leads, opportunities, contacts', category: 'Sales' },
    { id: 'financials', name: 'Financial Management', icon: <WorkIcon sx={{ fontSize: 20 }} />, description: 'Invoices, payments, GL', category: 'Finance' },
    { id: 'inventory', name: 'Inventory Management', icon: <Inventory2Icon sx={{ fontSize: 20 }} />, description: 'Products, stock, warehouses', category: 'Operations' },
    { id: 'procurement', name: 'Procurement & Purchasing', icon: <StoreIcon sx={{ fontSize: 20 }} />, description: 'Purchase orders and vendors', category: 'Operations' },
    { id: 'ecommerce', name: 'E-commerce', icon: <ShoppingCartIcon sx={{ fontSize: 20 }} />, description: 'Orders and catalog', category: 'Sales' },
    { id: 'ai', name: 'AI & Analytics', icon: <PsychologyIcon sx={{ fontSize: 20 }} />, description: 'AI-powered insights', category: 'Intelligence' },
    { id: 'sustainability', name: 'Sustainability', icon: <TrendingUpIcon sx={{ fontSize: 20 }} />, description: 'ESG metrics & reports', category: 'Compliance' },
  ];

  const handleModuleToggle = (moduleId, isEnabled) => {
    let newModules = [...selectedModules];
    if (isEnabled) {
      if (moduleId === 'financials' && !newModules.includes('procurement')) {
        newModules = [...newModules, 'financials', 'procurement'];
      } else if (moduleId === 'procurement' && !newModules.includes('financials')) {
        newModules = [...newModules, 'procurement', 'financials'];
      } else if (!newModules.includes(moduleId)) {
        newModules.push(moduleId);
      }
    } else {
      if (moduleId === 'financials' && newModules.includes('procurement')) {
        newModules = newModules.filter(id => id !== 'financials' && id !== 'procurement');
      } else if (moduleId === 'procurement' && newModules.includes('financials')) {
        newModules = newModules.filter(id => id !== 'procurement' && id !== 'financials');
      } else {
        newModules = newModules.filter(id => id !== moduleId);
      }
    }
    updatePreferences({ selectedModules: newModules });
  };

  const [settings, setSettings] = useState({
    autoRefresh: true,
    refreshInterval: 30,
    enableNotifications: true,
    defaultTheme: 'light',
    maxWidgets: 20,
    enableSharing: true,
    enableExport: true,
    dataRetention: 90,
    enableAnalytics: true,
    performanceMode: false
  });

  const [showSuccess, setShowSuccess] = useState(false);

  const handleSettingChange = (setting, value) => {
    setSettings(prev => ({
      ...prev,
      [setting]: value
    }));
  };

  const handleSaveSettings = () => {
    // Mock save functionality
    console.log('Saving settings:', settings);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Dashboard Settings</Typography>

      {/* New: Migrated dashboard gear settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <SettingsIcon color="primary" />
            <Typography variant="h6">Dashboard Configuration</Typography>
          </Box>

          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tab label="Module Management" />
            <Tab label="System Preferences" />
            <Tab label="Visitor Settings" />
          </Tabs>

          {activeTab === 0 && (
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Enable the modules you want visible across the app.
              </Typography>
              <Grid container spacing={2}>
                {allModules.map((module) => (
                  <Grid item xs={12} md={6} key={module.id}>
                    <Card sx={{ p: 2, border: isModuleEnabled(module.id) ? 2 : 1, borderColor: isModuleEnabled(module.id) ? 'primary.main' : 'grey.300' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                        {module.icon}
                        <Box sx={{ flex: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{module.name}</Typography>
                          <Typography variant="caption" color="text.secondary">{module.category}</Typography>
                        </Box>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={isModuleEnabled(module.id)}
                              onChange={(e) => handleModuleToggle(module.id, e.target.checked)}
                              color="primary"
                            />
                          }
                          label=""
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">{module.description}</Typography>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {activeTab === 1 && (
            <Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>Display Settings</Typography>
                    <FormControlLabel control={<Switch defaultChecked />} label="Show module status indicators" />
                    <FormControlLabel control={<Switch defaultChecked />} label="Enable quick action shortcuts" />
                    <FormControlLabel control={<Switch />} label="Show visitor privacy info" />
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>Notification Settings</Typography>
                    <FormControlLabel control={<Switch defaultChecked />} label="Session expiry warnings" />
                    <FormControlLabel control={<Switch defaultChecked />} label="Module update notifications" />
                    <FormControlLabel control={<Switch />} label="System status alerts" />
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>Session Details</Typography>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">Visitor ID: <strong>{visitorId || '—'}</strong></Typography>
                    </Box>
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">Session ID: <strong>{sessionId || '—'}</strong></Typography>
                    </Box>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Status:
                        <Chip label={isSessionValid ? 'Active' : 'Expired'} color={isSessionValid ? 'success' : 'warning'} size="small" sx={{ ml: 1 }} />
                      </Typography>
                    </Box>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card sx={{ p: 3 }}>
                    <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>Privacy Information</Typography>
                    <Typography variant="body2" color="text.secondary">Your data is isolated from other visitors. Sessions expire on a schedule for security.</Typography>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
      
      {showSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>General Settings</Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoRefresh}
                    onChange={(e) => handleSettingChange('autoRefresh', e.target.checked)}
                  />
                }
                label="Auto Refresh"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Refresh Interval (seconds)"
                type="number"
                value={settings.refreshInterval}
                onChange={(e) => handleSettingChange('refreshInterval', parseInt(e.target.value))}
                disabled={!settings.autoRefresh}
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableNotifications}
                    onChange={(e) => handleSettingChange('enableNotifications', e.target.checked)}
                  />
                }
                label="Enable Notifications"
                sx={{ mb: 2 }}
              />
              
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Default Theme</InputLabel>
                <Select
                  value={settings.defaultTheme}
                  onChange={(e) => handleSettingChange('defaultTheme', e.target.value)}
                  label="Default Theme"
                >
                  <MenuItem value="light">Light</MenuItem>
                  <MenuItem value="dark">Dark</MenuItem>
                  <MenuItem value="auto">Auto</MenuItem>
                </Select>
              </FormControl>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Performance Settings</Typography>
              
              <TextField
                fullWidth
                label="Maximum Widgets per Dashboard"
                type="number"
                value={settings.maxWidgets}
                onChange={(e) => handleSettingChange('maxWidgets', parseInt(e.target.value))}
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.performanceMode}
                    onChange={(e) => handleSettingChange('performanceMode', e.target.checked)}
                  />
                }
                label="Performance Mode"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Data Retention (days)"
                type="number"
                value={settings.dataRetention}
                onChange={(e) => handleSettingChange('dataRetention', parseInt(e.target.value))}
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableAnalytics}
                    onChange={(e) => handleSettingChange('enableAnalytics', e.target.checked)}
                  />
                }
                label="Enable Analytics"
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Sharing & Export Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Sharing & Export</Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableSharing}
                    onChange={(e) => handleSettingChange('enableSharing', e.target.checked)}
                  />
                }
                label="Enable Dashboard Sharing"
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableExport}
                    onChange={(e) => handleSettingChange('enableExport', e.target.checked)}
                  />
                }
                label="Enable Export Functionality"
                sx={{ mb: 2 }}
              />
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Export Formats Available:
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • PDF (when enabled)
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Excel (when enabled)
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Image (PNG/JPG)
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Advanced Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Advanced Settings</Typography>
              
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Cache Settings:
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Dashboard data is cached for 5 minutes by default
              </Typography>
              
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Widget Limits:
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                Maximum {settings.maxWidgets} widgets per dashboard
              </Typography>
              
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Data Sources:
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Real-time data (when available)
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Cached data (for performance)
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Historical data (up to {settings.dataRetention} days)
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Save Button */}
      <Box display="flex" justifyContent="flex-end" mt={3}>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
          size="large"
        >
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default DashboardSettings;



