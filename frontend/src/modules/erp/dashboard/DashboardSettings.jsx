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
  Alert
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';

const DashboardSettings = () => {
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



