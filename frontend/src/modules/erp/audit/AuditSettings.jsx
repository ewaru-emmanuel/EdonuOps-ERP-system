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
  Button,
  Divider,
  Alert
} from '@mui/material';
import { Save as SaveIcon } from '@mui/icons-material';

const AuditSettings = () => {
  const [settings, setSettings] = useState({
    enableAuditLogging: true,
    logRetentionDays: 365,
    enableRealTimeMonitoring: true,
    alertOnCriticalEvents: true,
    alertOnFailedLogins: true,
    alertOnDataExports: false,
    enableComplianceReporting: true,
    autoArchiveLogs: true,
    archiveAfterDays: 90,
    enableAuditTrail: true,
    logUserActions: true,
    logSystemEvents: true,
    logDataChanges: true,
    enableIPFiltering: false,
    allowedIPRanges: '',
    enableSessionTracking: true,
    sessionTimeoutMinutes: 30
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
    console.log('Saving audit settings:', settings);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Audit Settings</Typography>
      
      {showSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Audit settings saved successfully!
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
                    checked={settings.enableAuditLogging}
                    onChange={(e) => handleSettingChange('enableAuditLogging', e.target.checked)}
                  />
                }
                label="Enable Audit Logging"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Log Retention (days)"
                type="number"
                value={settings.logRetentionDays}
                onChange={(e) => handleSettingChange('logRetentionDays', parseInt(e.target.value))}
                disabled={!settings.enableAuditLogging}
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableRealTimeMonitoring}
                    onChange={(e) => handleSettingChange('enableRealTimeMonitoring', e.target.checked)}
                  />
                }
                label="Enable Real-time Monitoring"
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableComplianceReporting}
                    onChange={(e) => handleSettingChange('enableComplianceReporting', e.target.checked)}
                  />
                }
                label="Enable Compliance Reporting"
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Alert Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Alert Settings</Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.alertOnCriticalEvents}
                    onChange={(e) => handleSettingChange('alertOnCriticalEvents', e.target.checked)}
                  />
                }
                label="Alert on Critical Events"
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.alertOnFailedLogins}
                    onChange={(e) => handleSettingChange('alertOnFailedLogins', e.target.checked)}
                  />
                }
                label="Alert on Failed Logins"
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.alertOnDataExports}
                    onChange={(e) => handleSettingChange('alertOnDataExports', e.target.checked)}
                  />
                }
                label="Alert on Data Exports"
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableSessionTracking}
                    onChange={(e) => handleSettingChange('enableSessionTracking', e.target.checked)}
                  />
                }
                label="Enable Session Tracking"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Session Timeout (minutes)"
                type="number"
                value={settings.sessionTimeoutMinutes}
                onChange={(e) => handleSettingChange('sessionTimeoutMinutes', parseInt(e.target.value))}
                disabled={!settings.enableSessionTracking}
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Logging Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Logging Settings</Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.logUserActions}
                    onChange={(e) => handleSettingChange('logUserActions', e.target.checked)}
                  />
                }
                label="Log User Actions"
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.logSystemEvents}
                    onChange={(e) => handleSettingChange('logSystemEvents', e.target.checked)}
                  />
                }
                label="Log System Events"
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.logDataChanges}
                    onChange={(e) => handleSettingChange('logDataChanges', e.target.checked)}
                  />
                }
                label="Log Data Changes"
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableAuditTrail}
                    onChange={(e) => handleSettingChange('enableAuditTrail', e.target.checked)}
                  />
                }
                label="Enable Audit Trail"
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Archive Settings */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Archive Settings</Typography>
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.autoArchiveLogs}
                    onChange={(e) => handleSettingChange('autoArchiveLogs', e.target.checked)}
                  />
                }
                label="Auto-archive Logs"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Archive After (days)"
                type="number"
                value={settings.archiveAfterDays}
                onChange={(e) => handleSettingChange('archiveAfterDays', parseInt(e.target.value))}
                disabled={!settings.autoArchiveLogs}
                sx={{ mb: 2 }}
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.enableIPFiltering}
                    onChange={(e) => handleSettingChange('enableIPFiltering', e.target.checked)}
                  />
                }
                label="Enable IP Filtering"
                sx={{ mb: 2 }}
              />
              
              <TextField
                fullWidth
                label="Allowed IP Ranges"
                value={settings.allowedIPRanges}
                onChange={(e) => handleSettingChange('allowedIPRanges', e.target.value)}
                disabled={!settings.enableIPFiltering}
                placeholder="192.168.1.0/24, 10.0.0.0/8"
                sx={{ mb: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Compliance Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Compliance Settings</Typography>
              
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Data Retention Policy:
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                • Audit logs are retained for {settings.logRetentionDays} days
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                • Archived logs are stored for compliance purposes
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                • All data access is logged and monitored
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="body2" color="textSecondary" gutterBottom>
                Security Features:
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Real-time monitoring: {settings.enableRealTimeMonitoring ? 'Enabled' : 'Disabled'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Critical event alerts: {settings.alertOnCriticalEvents ? 'Enabled' : 'Disabled'}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                • Session tracking: {settings.enableSessionTracking ? 'Enabled' : 'Disabled'}
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

export default AuditSettings;



