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
  Divider
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Save as SaveIcon,
  SmartToy as AIIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

const AISettings = () => {
  const [settings, setSettings] = useState({
    aiEnabled: true,
    autoInsights: true,
    predictiveAnalytics: true,
    learningEnabled: true,
    modelAccuracy: 0.95,
    responseTime: 2.5,
    dataRetention: 90,
    privacyMode: 'standard'
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
      console.log('Saving AI settings:', settings);
      setIsDirty(false);
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        AI System Settings
      </Typography>

      <Grid container spacing={3}>
        {/* AI Configuration */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <AIIcon sx={{ mr: 1 }} />
                AI Configuration
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.aiEnabled}
                        onChange={(e) => handleSettingChange('aiEnabled', e.target.checked)}
                      />
                    }
                    label="Enable AI Co-Pilot"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.autoInsights}
                        onChange={(e) => handleSettingChange('autoInsights', e.target.checked)}
                      />
                    }
                    label="Auto-generate insights"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.predictiveAnalytics}
                        onChange={(e) => handleSettingChange('predictiveAnalytics', e.target.checked)}
                      />
                    }
                    label="Enable predictive analytics"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.learningEnabled}
                        onChange={(e) => handleSettingChange('learningEnabled', e.target.checked)}
                      />
                    }
                    label="Enable machine learning"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Settings */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <SettingsIcon sx={{ mr: 1 }} />
                Performance Settings
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Model Accuracy Threshold"
                    type="number"
                    value={settings.modelAccuracy}
                    onChange={(e) => handleSettingChange('modelAccuracy', parseFloat(e.target.value))}
                    inputProps={{ step: 0.01, min: 0.5, max: 1.0 }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Response Time (seconds)"
                    type="number"
                    value={settings.responseTime}
                    onChange={(e) => handleSettingChange('responseTime', parseFloat(e.target.value))}
                    inputProps={{ step: 0.1, min: 0.5, max: 10.0 }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Data Retention (days)"
                    type="number"
                    value={settings.dataRetention}
                    onChange={(e) => handleSettingChange('dataRetention', parseInt(e.target.value))}
                    inputProps={{ min: 30, max: 365 }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Privacy Settings */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <SecurityIcon sx={{ mr: 1 }} />
                Privacy & Security
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Privacy Mode</InputLabel>
                    <Select
                      value={settings.privacyMode}
                      onChange={(e) => handleSettingChange('privacyMode', e.target.value)}
                      label="Privacy Mode"
                    >
                      <MenuItem value="standard">Standard</MenuItem>
                      <MenuItem value="enhanced">Enhanced</MenuItem>
                      <MenuItem value="strict">Strict</MenuItem>
                    </Select>
                  </FormControl>
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

export default AISettings;
