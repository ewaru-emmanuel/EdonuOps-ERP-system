import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Business as BusinessIcon,
  CreditCard as CreditCardIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Upgrade as UpgradeIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { useTenant } from '../../../contexts/TenantContext';
import { useTenantApi } from '../../../hooks/useTenantApi';

const SubscriptionManagement = () => {
  const { currentTenant, hasModuleAccess } = useTenant();
  const { get, post, put, loading } = useTenantApi();
  
  const [subscriptionInfo, setSubscriptionInfo] = useState(null);
  const [availablePlans, setAvailablePlans] = useState({});
  const [usage, setUsage] = useState({});
  const [limitsStatus, setLimitsStatus] = useState({});
  const [recommendations, setRecommendations] = useState([]);
  const [billingInfo, setBillingInfo] = useState({});
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState(null);
  const [upgradeDialogOpen, setUpgradeDialogOpen] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState('');
  const [billingDialogOpen, setBillingDialogOpen] = useState(false);

  useEffect(() => {
    if (currentTenant) {
      loadSubscriptionData();
    }
  }, [currentTenant]);

  const loadSubscriptionData = async () => {
    try {
      setLoadingData(true);
      setError(null);
      
      // Load all subscription data in parallel
      const [
        subscriptionData,
        plansData,
        usageData,
        limitsData,
        recommendationsData,
        billingData
      ] = await Promise.all([
        get('/api/subscription/tenant/info'),
        get('/api/subscription/plans'),
        get('/api/subscription/tenant/usage'),
        get('/api/subscription/tenant/limits'),
        get('/api/subscription/tenant/recommendations'),
        get('/api/subscription/tenant/billing')
      ]);
      
      setSubscriptionInfo(subscriptionData);
      setAvailablePlans(plansData);
      setUsage(usageData);
      setLimitsStatus(limitsData);
      setRecommendations(recommendationsData);
      setBillingInfo(billingData);
      
    } catch (err) {
      console.error('Error loading subscription data:', err);
      setError('Failed to load subscription data');
    } finally {
      setLoadingData(false);
    }
  };

  const handleUpgrade = async () => {
    try {
      setLoadingData(true);
      setError(null);
      
      await post('/api/subscription/tenant/upgrade', {
        plan_id: selectedPlan
      });
      
      setUpgradeDialogOpen(false);
      setSelectedPlan('');
      await loadSubscriptionData(); // Refresh data
      
    } catch (err) {
      console.error('Error upgrading plan:', err);
      setError('Failed to upgrade plan');
    } finally {
      setLoadingData(false);
    }
  };

  const getPlanIcon = (planId) => {
    switch (planId) {
      case 'free':
        return <BusinessIcon color="action" />;
      case 'basic':
        return <TrendingUpIcon color="primary" />;
      case 'premium':
        return <SpeedIcon color="warning" />;
      case 'enterprise':
        return <AssessmentIcon color="success" />;
      default:
        return <BusinessIcon color="action" />;
    }
  };

  const getPlanColor = (planId) => {
    switch (planId) {
      case 'free':
        return 'default';
      case 'basic':
        return 'primary';
      case 'premium':
        return 'warning';
      case 'enterprise':
        return 'success';
      default:
        return 'default';
    }
  };

  const getUsagePercentage = (current, max) => {
    if (max === -1) return 0; // Unlimited
    if (max === 0) return 100;
    return Math.min((current / max) * 100, 100);
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 100) return 'error';
    if (percentage >= 80) return 'warning';
    return 'success';
  };

  if (loadingData) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!subscriptionInfo) {
    return (
      <Alert severity="info">
        No subscription information available.
      </Alert>
    );
  }

  const { current_plan, features, limits, usage: currentUsage, limits_status } = subscriptionInfo;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Subscription Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your subscription and billing for {currentTenant?.tenant_name}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadSubscriptionData}
            disabled={loadingData}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            disabled
          >
            Download Invoice
          </Button>
        </Box>
      </Box>

      {/* Alerts */}
      {limits_status && !limits_status.within_limits && (
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" fontWeight="bold">
            Plan Limits Exceeded
          </Typography>
          <Typography variant="body2">
            {limits_status.blocked.join(', ')}
          </Typography>
        </Alert>
      )}

      {limits_status && limits_status.warnings.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2" fontWeight="bold">
            Approaching Limits
          </Typography>
          <Typography variant="body2">
            {limits_status.warnings.join(', ')}
          </Typography>
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Current Plan */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                {getPlanIcon(current_plan.id)}
                <Typography variant="h6" fontWeight="bold">
                  Current Plan
                </Typography>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="h4" fontWeight="bold" gutterBottom>
                  {current_plan.name}
                </Typography>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  ${current_plan.price}/{current_plan.billing_cycle}
                </Typography>
                <Chip
                  label={current_plan.id}
                  color={getPlanColor(current_plan.id)}
                  size="small"
                />
              </Box>
              
              <Button
                variant="contained"
                startIcon={<UpgradeIcon />}
                onClick={() => setUpgradeDialogOpen(true)}
                fullWidth
              >
                Upgrade Plan
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Usage Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <AssessmentIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Usage Overview
                </Typography>
              </Box>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <BusinessIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Accounts"
                    secondary={`${currentUsage.accounts}/${features.max_accounts === -1 ? '∞' : features.max_accounts}`}
                  />
                  <Box sx={{ width: 100 }}>
                    <LinearProgress
                      variant="determinate"
                      value={getUsagePercentage(currentUsage.accounts, features.max_accounts)}
                      color={getUsageColor(getUsagePercentage(currentUsage.accounts, features.max_accounts))}
                    />
                  </Box>
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <PeopleIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Users"
                    secondary={`${currentUsage.users}/${features.max_users === -1 ? '∞' : features.max_users}`}
                  />
                  <Box sx={{ width: 100 }}>
                    <LinearProgress
                      variant="determinate"
                      value={getUsagePercentage(currentUsage.users, features.max_users)}
                      color={getUsageColor(getUsagePercentage(currentUsage.users, features.max_users))}
                    />
                  </Box>
                </ListItem>
                
                <ListItem>
                  <ListItemIcon>
                    <AssessmentIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="GL Entries"
                    secondary={`${currentUsage.gl_entries}/${features.max_gl_entries === -1 ? '∞' : features.max_gl_entries}`}
                  />
                  <Box sx={{ width: 100 }}>
                    <LinearProgress
                      variant="determinate"
                      value={getUsagePercentage(currentUsage.gl_entries, features.max_gl_entries)}
                      color={getUsageColor(getUsagePercentage(currentUsage.gl_entries, features.max_gl_entries))}
                    />
                  </Box>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Available Plans */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <TrendingUpIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Available Plans
                </Typography>
              </Box>
              
              <Grid container spacing={2}>
                {Object.entries(availablePlans).map(([planId, plan]) => (
                  <Grid item xs={12} key={planId}>
                    <Paper
                      sx={{
                        p: 2,
                        border: planId === current_plan.id ? '2px solid' : '1px solid',
                        borderColor: planId === current_plan.id ? 'primary.main' : 'divider',
                        cursor: 'pointer',
                        '&:hover': {
                          backgroundColor: 'action.hover'
                        }
                      }}
                      onClick={() => {
                        if (planId !== current_plan.id) {
                          setSelectedPlan(planId);
                          setUpgradeDialogOpen(true);
                        }
                      }}
                    >
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="h6" fontWeight="bold">
                            {plan.name}
                          </Typography>
                          <Typography variant="h5" color="primary">
                            ${plan.price}/{plan.billing_cycle}
                          </Typography>
                        </Box>
                        <Box textAlign="right">
                          {planId === current_plan.id ? (
                            <Chip label="Current" color="primary" />
                          ) : (
                            <Button size="small" variant="outlined">
                              Select
                            </Button>
                          )}
                        </Box>
                      </Box>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Billing Information */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <CreditCardIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Billing Information
                </Typography>
                <Box sx={{ flexGrow: 1 }} />
                <IconButton onClick={() => setBillingDialogOpen(true)}>
                  <SettingsIcon />
                </IconButton>
              </Box>
              
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Next Billing Date"
                    secondary={billingInfo.next_billing_date ? new Date(billingInfo.next_billing_date).toLocaleDateString() : 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Payment Method"
                    secondary={billingInfo.payment_method || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Billing Address"
                    secondary={billingInfo.billing_address || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Invoice Email"
                    secondary={billingInfo.invoice_email || 'N/A'}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Upgrade Recommendations */}
        {recommendations.length > 0 && (
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={3}>
                  <NotificationsIcon color="primary" />
                  <Typography variant="h6" fontWeight="bold">
                    Upgrade Recommendations
                  </Typography>
                </Box>
                
                <Grid container spacing={2}>
                  {recommendations.map((rec, index) => (
                    <Grid item xs={12} md={6} key={index}>
                      <Paper sx={{ p: 2, border: '1px solid', borderColor: 'primary.main' }}>
                        <Typography variant="h6" fontWeight="bold" gutterBottom>
                          {rec.plan_name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary" gutterBottom>
                          {rec.reason}
                        </Typography>
                        <Typography variant="h5" color="primary" gutterBottom>
                          ${rec.price}/{current_plan.billing_cycle}
                        </Typography>
                        <List dense>
                          {rec.benefits.map((benefit, idx) => (
                            <ListItem key={idx} sx={{ py: 0 }}>
                              <ListItemIcon>
                                <CheckCircleIcon color="success" fontSize="small" />
                              </ListItemIcon>
                              <ListItemText primary={benefit} />
                            </ListItem>
                          ))}
                        </List>
                        <Button
                          variant="contained"
                          fullWidth
                          onClick={() => {
                            setSelectedPlan(rec.plan_id);
                            setUpgradeDialogOpen(true);
                          }}
                        >
                          Upgrade to {rec.plan_name}
                        </Button>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Upgrade Dialog */}
      <Dialog open={upgradeDialogOpen} onClose={() => setUpgradeDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <UpgradeIcon color="primary" />
            <Typography variant="h6">
              Upgrade Subscription
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" gutterBottom>
            Are you sure you want to upgrade to the {availablePlans[selectedPlan]?.name} plan?
          </Typography>
          <Typography variant="body2" color="text.secondary">
            This will change your billing to ${availablePlans[selectedPlan]?.price}/{availablePlans[selectedPlan]?.billing_cycle}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUpgradeDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleUpgrade}
            disabled={loadingData}
          >
            {loadingData ? 'Upgrading...' : 'Upgrade'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Billing Dialog */}
      <Dialog open={billingDialogOpen} onClose={() => setBillingDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <SettingsIcon color="primary" />
            <Typography variant="h6">
              Billing Settings
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Billing settings would be configured here in a real implementation.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBillingDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SubscriptionManagement;












