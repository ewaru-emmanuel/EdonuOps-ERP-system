import React, { useState } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  Alert,
  Snackbar
} from '@mui/material';
import { 
  Settings, 
  Security, 
  Notifications, 
  Palette,
  Business,
  People,
  Timeline,
  IntegrationInstructions
} from '@mui/icons-material';

const CRMSettings = () => {
  const [openDialog, setOpenDialog] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Settings state
  const [generalSettings, setGeneralSettings] = useState({
    companyName: 'EdonuOps',
    timezone: 'UTC',
    currency: 'USD',
    dateFormat: 'MM/DD/YYYY',
    language: 'en'
  });

  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: false,
    sessionTimeout: 30,
    passwordPolicy: 'strong',
    ipWhitelist: []
  });

  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    taskReminders: true,
    opportunityAlerts: true,
    weeklyReports: false
  });

  const [pipelineSettings, setPipelineSettings] = useState({
    defaultStages: ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won'],
    autoAssignTasks: true,
    stageChecklists: true,
    dealScoring: true
  });
  const handleOpenDialog = (dialogType) => {
    setOpenDialog(dialogType);
  };

  const handleCloseDialog = () => {
    setOpenDialog(null);
  };

  const handleSaveSettings = (settingsType, newSettings) => {
    try {
      // Here you would typically save to backend
      switch (settingsType) {
        case 'general':
          setGeneralSettings(newSettings);
          break;
        case 'security':
          setSecuritySettings(newSettings);
          break;
        case 'notifications':
          setNotificationSettings(newSettings);
          break;
        case 'pipeline':
          setPipelineSettings(newSettings);
          break;
      }
      setSnackbar({ open: true, message: 'Settings saved successfully!', severity: 'success' });
      handleCloseDialog();
    } catch (error) {
      setSnackbar({ open: true, message: 'Error saving settings', severity: 'error' });
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>
        CRM Settings
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Settings sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="medium">
                  General Settings
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Company info, timezone, currency, and language preferences
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip label={generalSettings.currency} size="small" sx={{ mr: 1 }} />
                <Chip label={generalSettings.timezone} size="small" />
              </Box>
              <Button 
                variant="outlined" 
                size="small"
                onClick={() => handleOpenDialog('general')}
              >
                Configure
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Security sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="medium">
                  Security
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Authentication, permissions, and access control
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={securitySettings.twoFactorAuth ? '2FA Enabled' : '2FA Disabled'} 
                  color={securitySettings.twoFactorAuth ? 'success' : 'default'}
                  size="small" 
                />
              </Box>
              <Button 
                variant="outlined" 
                size="small"
                onClick={() => handleOpenDialog('security')}
              >
                Configure
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Notifications sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="medium">
                  Notifications
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Email, push notifications, and alerts preferences
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={notificationSettings.emailNotifications ? 'Email On' : 'Email Off'} 
                  color={notificationSettings.emailNotifications ? 'success' : 'default'}
                  size="small" 
                  sx={{ mr: 1 }}
                />
                <Chip 
                  label={notificationSettings.pushNotifications ? 'Push On' : 'Push Off'} 
                  color={notificationSettings.pushNotifications ? 'success' : 'default'}
                  size="small" 
                />
              </Box>
              <Button 
                variant="outlined" 
                size="small"
                onClick={() => handleOpenDialog('notifications')}
              >
                Configure
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Timeline sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6" fontWeight="medium">
                  Pipeline
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Sales pipeline stages and automation settings
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Chip 
                  label={`${pipelineSettings.defaultStages.length} Stages`} 
                  size="small" 
                  sx={{ mr: 1 }}
                />
                <Chip 
                  label={pipelineSettings.autoAssignTasks ? 'Auto Tasks' : 'Manual Tasks'} 
                  color={pipelineSettings.autoAssignTasks ? 'success' : 'default'}
                  size="small" 
                />
              </Box>
              <Button 
                variant="outlined" 
                size="small"
                onClick={() => handleOpenDialog('pipeline')}
              >
                Configure
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Settings Dialogs */}
      {openDialog === 'general' && (
        <Dialog open={true} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>General Settings</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
              <TextField
                label="Company Name"
                value={generalSettings.companyName}
                onChange={(e) => setGeneralSettings(prev => ({ ...prev, companyName: e.target.value }))}
                fullWidth
              />
              <FormControl fullWidth>
                <InputLabel>Currency</InputLabel>
                <Select
                  value={generalSettings.currency}
                  label="Currency"
                  onChange={(e) => setGeneralSettings(prev => ({ ...prev, currency: e.target.value }))}
                >
                  <MenuItem value="USD">USD</MenuItem>
                  <MenuItem value="EUR">EUR</MenuItem>
                  <MenuItem value="GBP">GBP</MenuItem>
                  <MenuItem value="JPY">JPY</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Timezone</InputLabel>
                <Select
                  value={generalSettings.timezone}
                  label="Timezone"
                  onChange={(e) => setGeneralSettings(prev => ({ ...prev, timezone: e.target.value }))}
                >
                  <MenuItem value="UTC">UTC</MenuItem>
                  <MenuItem value="EST">EST</MenuItem>
                  <MenuItem value="PST">PST</MenuItem>
                  <MenuItem value="GMT">GMT</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Date Format</InputLabel>
                <Select
                  value={generalSettings.dateFormat}
                  label="Date Format"
                  onChange={(e) => setGeneralSettings(prev => ({ ...prev, dateFormat: e.target.value }))}
                >
                  <MenuItem value="MM/DD/YYYY">MM/DD/YYYY</MenuItem>
                  <MenuItem value="DD/MM/YYYY">DD/MM/YYYY</MenuItem>
                  <MenuItem value="YYYY-MM-DD">YYYY-MM-DD</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={() => handleSaveSettings('general', generalSettings)} 
              variant="contained"
            >
              Save
            </Button>
          </DialogActions>
        </Dialog>
      )}

      {openDialog === 'security' && (
        <Dialog open={true} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>Security Settings</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={securitySettings.twoFactorAuth}
                    onChange={(e) => setSecuritySettings(prev => ({ ...prev, twoFactorAuth: e.target.checked }))}
                  />
                }
                label="Two-Factor Authentication"
              />
              <FormControl fullWidth>
                <InputLabel>Session Timeout (minutes)</InputLabel>
                <Select
                  value={securitySettings.sessionTimeout}
                  label="Session Timeout (minutes)"
                  onChange={(e) => setSecuritySettings(prev => ({ ...prev, sessionTimeout: e.target.value }))}
                >
                  <MenuItem value={15}>15 minutes</MenuItem>
                  <MenuItem value={30}>30 minutes</MenuItem>
                  <MenuItem value={60}>1 hour</MenuItem>
                  <MenuItem value={120}>2 hours</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Password Policy</InputLabel>
                <Select
                  value={securitySettings.passwordPolicy}
                  label="Password Policy"
                  onChange={(e) => setSecuritySettings(prev => ({ ...prev, passwordPolicy: e.target.value }))}
                >
                  <MenuItem value="basic">Basic</MenuItem>
                  <MenuItem value="strong">Strong</MenuItem>
                  <MenuItem value="very-strong">Very Strong</MenuItem>
                </Select>
              </FormControl>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={() => handleSaveSettings('security', securitySettings)} 
              variant="contained"
            >
              Save
            </Button>
          </DialogActions>
        </Dialog>
      )}

      {openDialog === 'notifications' && (
        <Dialog open={true} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>Notification Settings</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.emailNotifications}
                    onChange={(e) => setNotificationSettings(prev => ({ ...prev, emailNotifications: e.target.checked }))}
                  />
                }
                label="Email Notifications"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.pushNotifications}
                    onChange={(e) => setNotificationSettings(prev => ({ ...prev, pushNotifications: e.target.checked }))}
                  />
                }
                label="Push Notifications"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.taskReminders}
                    onChange={(e) => setNotificationSettings(prev => ({ ...prev, taskReminders: e.target.checked }))}
                  />
                }
                label="Task Reminders"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.opportunityAlerts}
                    onChange={(e) => setNotificationSettings(prev => ({ ...prev, opportunityAlerts: e.target.checked }))}
                  />
                }
                label="Opportunity Alerts"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notificationSettings.weeklyReports}
                    onChange={(e) => setNotificationSettings(prev => ({ ...prev, weeklyReports: e.target.checked }))}
                  />
                }
                label="Weekly Reports"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={() => handleSaveSettings('notifications', notificationSettings)} 
              variant="contained"
            >
              Save
            </Button>
          </DialogActions>
        </Dialog>
      )}

      {openDialog === 'pipeline' && (
        <Dialog open={true} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>Pipeline Settings</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={pipelineSettings.autoAssignTasks}
                    onChange={(e) => setPipelineSettings(prev => ({ ...prev, autoAssignTasks: e.target.checked }))}
                  />
                }
                label="Auto-assign Tasks"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={pipelineSettings.stageChecklists}
                    onChange={(e) => setPipelineSettings(prev => ({ ...prev, stageChecklists: e.target.checked }))}
                  />
                }
                label="Stage Checklists"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={pipelineSettings.dealScoring}
                    onChange={(e) => setPipelineSettings(prev => ({ ...prev, dealScoring: e.target.checked }))}
                  />
                }
                label="Deal Scoring"
              />
              <Typography variant="subtitle2" sx={{ mt: 2 }}>
                Default Pipeline Stages:
              </Typography>
              <List dense>
                {pipelineSettings.defaultStages.map((stage, index) => (
                  <ListItem key={index}>
                    <ListItemText primary={stage} />
                    <Chip label={`Stage ${index + 1}`} size="small" />
                  </ListItem>
                ))}
              </List>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button 
              onClick={() => handleSaveSettings('pipeline', pipelineSettings)} 
              variant="contained"
            >
              Save
            </Button>
          </DialogActions>
        </Dialog>
      )}

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CRMSettings;


