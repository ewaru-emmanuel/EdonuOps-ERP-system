import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Alert
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Save as SaveIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

const TaxSettings = () => {
  const [settings, setSettings] = useState({
    autoCalculation: true,
    complianceAlerts: true,
    taxRateUpdates: true,
    filingReminders: true,
    defaultTaxType: 'sales',
    roundingMethod: 'nearest',
    decimalPlaces: 2,
    fiscalYearStart: '01-01',
    timezone: 'UTC',
    language: 'en'
  });

  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    // Mock settings data
    // In real app, this would fetch from API
  };

  const handleSettingChange = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
    setIsDirty(true);
  };

  const handleSave = async () => {
    try {
      // TODO: Save settings to API
      console.log('Saving settings:', settings);
      setIsDirty(false);
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Tax System Settings
      </Typography>

      <Grid container spacing={3}>
        {/* General Settings */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <SettingsIcon sx={{ mr: 1 }} />
                General Settings
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.autoCalculation}
                        onChange={(e) => handleSettingChange('autoCalculation', e.target.checked)}
                      />
                    }
                    label="Auto-calculate tax on transactions"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.complianceAlerts}
                        onChange={(e) => handleSettingChange('complianceAlerts', e.target.checked)}
                      />
                    }
                    label="Enable compliance alerts"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.taxRateUpdates}
                        onChange={(e) => handleSettingChange('taxRateUpdates', e.target.checked)}
                      />
                    }
                    label="Auto-update tax rates"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.filingReminders}
                        onChange={(e) => handleSettingChange('filingReminders', e.target.checked)}
                      />
                    }
                    label="Filing deadline reminders"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Calculation Settings */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <SettingsIcon sx={{ mr: 1 }} />
                Calculation Settings
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Default Tax Type</InputLabel>
                    <Select
                      value={settings.defaultTaxType}
                      onChange={(e) => handleSettingChange('defaultTaxType', e.target.value)}
                      label="Default Tax Type"
                    >
                      <MenuItem value="sales">Sales Tax</MenuItem>
                      <MenuItem value="vat">VAT</MenuItem>
                      <MenuItem value="gst">GST</MenuItem>
                      <MenuItem value="corporate">Corporate Tax</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Rounding Method</InputLabel>
                    <Select
                      value={settings.roundingMethod}
                      onChange={(e) => handleSettingChange('roundingMethod', e.target.value)}
                      label="Rounding Method"
                    >
                      <MenuItem value="nearest">Nearest</MenuItem>
                      <MenuItem value="up">Round Up</MenuItem>
                      <MenuItem value="down">Round Down</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Decimal Places"
                    type="number"
                    value={settings.decimalPlaces}
                    onChange={(e) => handleSettingChange('decimalPlaces', parseInt(e.target.value))}
                    inputProps={{ min: 0, max: 4 }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* System Settings */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <SecurityIcon sx={{ mr: 1 }} />
                System Settings
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Fiscal Year Start"
                    value={settings.fiscalYearStart}
                    onChange={(e) => handleSettingChange('fiscalYearStart', e.target.value)}
                    placeholder="MM-DD"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Timezone</InputLabel>
                    <Select
                      value={settings.timezone}
                      onChange={(e) => handleSettingChange('timezone', e.target.value)}
                      label="Timezone"
                    >
                      <MenuItem value="UTC">UTC</MenuItem>
                      <MenuItem value="EST">Eastern Time</MenuItem>
                      <MenuItem value="PST">Pacific Time</MenuItem>
                      <MenuItem value="GMT">GMT</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Language</InputLabel>
                    <Select
                      value={settings.language}
                      onChange={(e) => handleSettingChange('language', e.target.value)}
                      label="Language"
                    >
                      <MenuItem value="en">English</MenuItem>
                      <MenuItem value="es">Spanish</MenuItem>
                      <MenuItem value="fr">French</MenuItem>
                      <MenuItem value="de">German</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Notification Settings */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <NotificationsIcon sx={{ mr: 1 }} />
                Notification Settings
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.complianceAlerts}
                        onChange={(e) => handleSettingChange('complianceAlerts', e.target.checked)}
                      />
                    }
                    label="Compliance alerts"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.filingReminders}
                        onChange={(e) => handleSettingChange('filingReminders', e.target.checked)}
                      />
                    }
                    label="Filing reminders"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.taxRateUpdates}
                        onChange={(e) => handleSettingChange('taxRateUpdates', e.target.checked)}
                      />
                    }
                    label="Tax rate update notifications"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Save Button */}
      {isDirty && (
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            size="large"
            sx={{ px: 4 }}
          >
            Save Settings
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default TaxSettings;




