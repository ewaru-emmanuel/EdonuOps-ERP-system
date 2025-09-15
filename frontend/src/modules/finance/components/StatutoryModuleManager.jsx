import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Button,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  IconButton,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Business as BusinessIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Settings as SettingsIcon,
  Description as FormIcon,
  AccountBalance as AccountIcon,
  Flag as FlagIcon
} from '@mui/icons-material';
import { apiClient } from '../../../utils/apiClient';

const StatutoryModuleManager = ({ country = 'US', onModuleChange }) => {
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCountry, setSelectedCountry] = useState(country);
  const [complianceStatus, setComplianceStatus] = useState(null);
  const [showDetails, setShowDetails] = useState(null);
  const [actionLoading, setActionLoading] = useState({});

  const countries = [
    { code: 'US', name: 'United States', flag: '🇺🇸' },
    { code: 'IN', name: 'India', flag: '🇮🇳' },
    { code: 'GB', name: 'United Kingdom', flag: '🇬🇧' },
    { code: 'KE', name: 'Kenya', flag: '🇰🇪' },
    { code: 'GLOBAL', name: 'Global (Basic)', flag: '🌍' }
  ];

  useEffect(() => {
    loadModules();
    loadComplianceStatus();
  }, [selectedCountry]);

  const loadModules = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/finance/statutory/modules?country=${selectedCountry}`);
      setModules(response.data.modules || []);
      setError(null);
    } catch (err) {
      setError('Failed to load statutory modules');
      console.error('Error loading modules:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadComplianceStatus = async () => {
    try {
      const response = await apiClient.get(`/api/finance/statutory/compliance/status?country=${selectedCountry}`);
      setComplianceStatus(response.data);
    } catch (err) {
      console.error('Error loading compliance status:', err);
    }
  };

  const handleModuleToggle = async (moduleId, isActive) => {
    setActionLoading(prev => ({ ...prev, [moduleId]: true }));
    
    try {
      if (isActive) {
        // Activate module
        const response = await apiClient.post(`/api/finance/statutory/modules/${moduleId}/activate`, {
          country: selectedCountry
        });
        
        if (response.data.success) {
          await loadModules();
          await loadComplianceStatus();
          onModuleChange?.(moduleId, 'activated');
        } else {
          setError(response.data.message);
        }
      } else {
        // Deactivate module
        const response = await apiClient.post(`/api/finance/statutory/modules/${moduleId}/deactivate`, {
          country: selectedCountry,
          force: false
        });
        
        if (response.data.success) {
          await loadModules();
          await loadComplianceStatus();
          onModuleChange?.(moduleId, 'deactivated');
        } else {
          setError(response.data.message);
        }
      }
    } catch (err) {
      setError(`Failed to ${isActive ? 'activate' : 'deactivate'} module`);
      console.error('Error toggling module:', err);
    } finally {
      setActionLoading(prev => ({ ...prev, [moduleId]: false }));
    }
  };

  const handleForceDeactivate = async (moduleId) => {
    if (!window.confirm('Are you sure you want to force deactivate this module? This may cause data integrity issues.')) {
      return;
    }

    setActionLoading(prev => ({ ...prev, [moduleId]: true }));
    
    try {
      const response = await apiClient.post(`/api/finance/statutory/modules/${moduleId}/deactivate`, {
        country: selectedCountry,
        force: true
      });
      
      if (response.data.success) {
        await loadModules();
        await loadComplianceStatus();
        onModuleChange?.(moduleId, 'force_deactivated');
      } else {
        setError(response.data.message);
      }
    } catch (err) {
      setError('Failed to force deactivate module');
      console.error('Error force deactivating module:', err);
    } finally {
      setActionLoading(prev => ({ ...prev, [moduleId]: false }));
    }
  };

  const getModuleStatusColor = (module) => {
    if (module.is_active) return 'success';
    if (module.can_activate) return 'info';
    return 'error';
  };

  const getModuleStatusIcon = (module) => {
    if (module.is_active) return <CheckCircleIcon color="success" />;
    if (module.can_activate) return <InfoIcon color="info" />;
    return <ErrorIcon color="error" />;
  };

  const renderModuleCard = (module) => (
    <Card key={module.id} sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {getModuleStatusIcon(module)}
            <Box>
              <Typography variant="h6" gutterBottom>
                {module.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {module.description}
              </Typography>
            </Box>
          </Box>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={module.is_active ? 'Active' : 'Inactive'}
              color={getModuleStatusColor(module)}
              variant={module.is_active ? 'filled' : 'outlined'}
            />
            <Tooltip title="Module Details">
              <IconButton
                onClick={() => setShowDetails(module)}
                size="small"
              >
                <SettingsIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Module Status */}
        {!module.is_active && !module.can_activate && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2">
              {module.activation_message}
            </Typography>
          </Alert>
        )}

        {module.is_active && !module.can_deactivate && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2">
              Cannot deactivate: {module.deactivation_message}
            </Typography>
            {module.deactivation_issues && module.deactivation_issues.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" display="block">
                  Issues preventing deactivation:
                </Typography>
                {module.deactivation_issues.map((issue, index) => (
                  <Typography key={index} variant="caption" display="block" sx={{ ml: 2 }}>
                    • {issue.message}
                  </Typography>
                ))}
              </Box>
            )}
          </Alert>
        )}

        {/* Module Controls */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={module.is_active}
                  onChange={(e) => handleModuleToggle(module.id, e.target.checked)}
                  disabled={actionLoading[module.id] || (!module.is_active && !module.can_activate)}
                  color="primary"
                />
              }
              label={module.is_active ? 'Deactivate Module' : 'Activate Module'}
            />
            
            {actionLoading[module.id] && (
              <CircularProgress size={20} />
            )}
          </Box>

          {module.is_active && !module.can_deactivate && (
            <Button
              variant="outlined"
              color="error"
              size="small"
              onClick={() => handleForceDeactivate(module.id)}
              disabled={actionLoading[module.id]}
            >
              Force Deactivate
            </Button>
          )}
        </Box>

        {/* Compliance Forms */}
        {module.compliance_forms && module.compliance_forms.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Compliance Forms:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {module.compliance_forms.map(form => (
                <Chip
                  key={form}
                  label={form}
                  size="small"
                  icon={<FormIcon />}
                  variant="outlined"
                />
              ))}
            </Box>
          </Box>
        )}
      </CardContent>
    </Card>
  );

  const renderComplianceStatus = () => {
    if (!complianceStatus) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Compliance Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {complianceStatus.active_modules}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Active Modules
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="text.secondary">
                  {complianceStatus.inactive_modules}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Inactive Modules
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info.main">
                  {complianceStatus.compliance_forms_required.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Required Forms
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success.main">
                  {complianceStatus.total_modules}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Modules
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Statutory Module Manager
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Manage tax and compliance modules for your business. Activate only the modules you need
          to keep your Chart of Accounts clean and compliant.
        </Typography>
      </Box>

      {/* Country Selector */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <FlagIcon color="primary" />
            <Typography variant="h6">Country Configuration</Typography>
          </Box>
          <FormControl fullWidth>
            <InputLabel>Select Country</InputLabel>
            <Select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              label="Select Country"
            >
              {countries.map(country => (
                <MenuItem key={country.code} value={country.code}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <span>{country.flag}</span>
                    {country.name}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Compliance Status */}
      {renderComplianceStatus()}

      {/* Modules List */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Available Modules
        </Typography>
        {modules.map(renderModuleCard)}
      </Box>

      {/* Module Details Dialog */}
      <Dialog
        open={!!showDetails}
        onClose={() => setShowDetails(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {showDetails?.name} - Module Details
        </DialogTitle>
        <DialogContent>
          {showDetails && (
            <Box>
              <Typography variant="body1" paragraph>
                {showDetails.description}
              </Typography>
              
              <Typography variant="h6" gutterBottom>
                Required Accounts
              </Typography>
              <List dense>
                {showDetails.required_accounts.map(accountCode => (
                  <ListItem key={accountCode}>
                    <ListItemIcon>
                      <AccountIcon />
                    </ListItemIcon>
                    <ListItemText primary={accountCode} />
                  </ListItem>
                ))}
              </List>
              
              {showDetails.compliance_forms && showDetails.compliance_forms.length > 0 && (
                <>
                  <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                    Compliance Forms
                  </Typography>
                  <List dense>
                    {showDetails.compliance_forms.map(form => (
                      <ListItem key={form}>
                        <ListItemIcon>
                          <FormIcon />
                        </ListItemIcon>
                        <ListItemText primary={form} />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDetails(null)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StatutoryModuleManager;

