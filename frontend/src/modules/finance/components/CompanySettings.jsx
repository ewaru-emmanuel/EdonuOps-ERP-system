import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider,
  Switch,
  FormControlLabel
} from '@mui/material';
import apiClient from '../../../services/apiClient';

const CompanySettings = () => {
  const [settings, setSettings] = useState({
    companyName: '',
    taxId: '',
    address: '',
    city: '',
    state: '',
    zipCode: '',
    country: '',
    phone: '',
    email: '',
    website: '',
    currency: 'USD',
    fiscalYearStart: '',
    autoBackup: false,
    multiCurrency: false
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await apiClient.get('/api/core/settings/company');
      if (response.data) {
        setSettings({ ...settings, ...response.data });
      }
    } catch (error) {
      console.error('Error loading company settings:', error);
    }
  };

  const handleInputChange = (field) => (event) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value;
    setSettings({
      ...settings,
      [field]: value
    });
  };

  const handleSave = async () => {
    setLoading(true);
    setMessage('');

    try {
      await apiClient.put('/api/core/settings/company', settings);
      setMessage('Company settings saved successfully!');
    } catch (error) {
      console.error('Error saving company settings:', error);
      setMessage('Error saving settings. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const currencies = [
    'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'SEK', 'NOK'
  ];

  const countries = [
    'United States', 'Canada', 'United Kingdom', 'Germany', 'France',
    'Japan', 'Australia', 'Switzerland', 'Sweden', 'Norway'
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Company Settings
      </Typography>

      {message && (
        <Alert severity={message.includes('Error') ? 'error' : 'success'} sx={{ mb: 3 }}>
          {message}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Company Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Company Information
              </Typography>
              
              <TextField
                fullWidth
                label="Company Name"
                value={settings.companyName}
                onChange={handleInputChange('companyName')}
                margin="normal"
              />
              
              <TextField
                fullWidth
                label="Tax ID / EIN"
                value={settings.taxId}
                onChange={handleInputChange('taxId')}
                margin="normal"
              />
              
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={settings.email}
                onChange={handleInputChange('email')}
                margin="normal"
              />
              
              <TextField
                fullWidth
                label="Phone"
                value={settings.phone}
                onChange={handleInputChange('phone')}
                margin="normal"
              />
              
              <TextField
                fullWidth
                label="Website"
                value={settings.website}
                onChange={handleInputChange('website')}
                margin="normal"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Address Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Address Information
              </Typography>
              
              <TextField
                fullWidth
                label="Address"
                value={settings.address}
                onChange={handleInputChange('address')}
                margin="normal"
              />
              
              <Grid container spacing={2}>
                <Grid item xs={8}>
                  <TextField
                    fullWidth
                    label="City"
                    value={settings.city}
                    onChange={handleInputChange('city')}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="State"
                    value={settings.state}
                    onChange={handleInputChange('state')}
                    margin="normal"
                  />
                </Grid>
              </Grid>
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="ZIP Code"
                    value={settings.zipCode}
                    onChange={handleInputChange('zipCode')}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Country</InputLabel>
                    <Select
                      value={settings.country}
                      onChange={handleInputChange('country')}
                      label="Country"
                    >
                      {countries.map((country) => (
                        <MenuItem key={country} value={country}>
                          {country}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Financial Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Financial Settings
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Default Currency</InputLabel>
                    <Select
                      value={settings.currency}
                      onChange={handleInputChange('currency')}
                      label="Default Currency"
                    >
                      {currencies.map((currency) => (
                        <MenuItem key={currency} value={currency}>
                          {currency}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={4}>
                  <TextField
                    fullWidth
                    label="Fiscal Year Start"
                    type="date"
                    value={settings.fiscalYearStart}
                    onChange={handleInputChange('fiscalYearStart')}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
              </Grid>
              
              <Divider sx={{ my: 3 }} />
              
              <Box>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.autoBackup}
                      onChange={handleInputChange('autoBackup')}
                    />
                  }
                  label="Enable Automatic Backups"
                />
                
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.multiCurrency}
                      onChange={handleInputChange('multiCurrency')}
                    />
                  }
                  label="Enable Multi-Currency Support"
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Save Button */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleSave}
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Settings'}
            </Button>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CompanySettings;







