import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Button,
  IconButton,
  Tooltip,
  Paper,
  Divider
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  AccountBalance as AccountBalanceIcon,
  Business as BusinessIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { useTenant } from '../../../contexts/TenantContext';
import { useTenantApi } from '../../../hooks/useTenantApi';

const TenantDashboard = () => {
  const { currentTenant, hasModuleAccess } = useTenant();
  const { get, loading } = useTenantApi();
  
  const [dashboardData, setDashboardData] = useState(null);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    if (currentTenant) {
      loadDashboardData();
    }
  }, [currentTenant]);

  const loadDashboardData = async () => {
    try {
      setLoadingData(true);
      setError(null);
      
      // Load comprehensive dashboard data
      const [
        tenantInfo,
        modules,
        financeMetrics,
        systemHealth,
        recentActivity,
        alerts
      ] = await Promise.all([
        get('/api/finance/tenant-info'),
        get('/api/finance/tenant-modules'),
        getFinanceMetrics(),
        getSystemHealth(),
        getRecentActivity(),
        getAlerts()
      ]);
      
      setDashboardData({
        tenantInfo,
        modules,
        financeMetrics,
        systemHealth,
        recentActivity,
        alerts,
        lastUpdated: new Date()
      });
      
      setLastUpdated(new Date());
      
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoadingData(false);
    }
  };

  const getFinanceMetrics = async () => {
    try {
      const [accounts, glEntries, bankAccounts, reconciliationSessions] = await Promise.all([
        get('/api/finance/chart-of-accounts'),
        get('/api/finance/general-ledger'),
        get('/api/finance/bank-accounts'),
        get('/api/finance/reconciliation-sessions')
      ]);
      
      return {
        totalAccounts: accounts?.length || 0,
        totalGlEntries: glEntries?.length || 0,
        totalBankAccounts: bankAccounts?.length || 0,
        totalReconciliationSessions: reconciliationSessions?.length || 0,
        pendingReconciliations: reconciliationSessions?.filter(s => s.status === 'pending').length || 0
      };
    } catch (err) {
      console.error('Error loading finance metrics:', err);
      return {};
    }
  };

  const getSystemHealth = async () => {
    try {
      // Simulate system health metrics
      return {
        uptime: '99.9%',
        responseTime: '120ms',
        errorRate: '0.1%',
        activeUsers: Math.floor(Math.random() * 50) + 10,
        dataUsage: '2.3 GB',
        lastBackup: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
      };
    } catch (err) {
      console.error('Error loading system health:', err);
      return {};
    }
  };

  const getRecentActivity = async () => {
    try {
      // Simulate recent activity data
      return [
        {
          id: 1,
          type: 'account_created',
          description: 'New account "Cash Account" created',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          user: 'John Doe'
        },
        {
          id: 2,
          type: 'reconciliation_completed',
          description: 'Bank reconciliation completed for Main Checking',
          timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          user: 'Jane Smith'
        },
        {
          id: 3,
          type: 'gl_entry_created',
          description: 'Journal entry posted for Invoice #1234',
          timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          user: 'Mike Johnson'
        }
      ];
    } catch (err) {
      console.error('Error loading recent activity:', err);
      return [];
    }
  };

  const getAlerts = async () => {
    try {
      // Simulate alerts data
      return [
        {
          id: 1,
          type: 'warning',
          title: 'Pending Reconciliation',
          message: '3 bank accounts have pending reconciliations',
          timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
        },
        {
          id: 2,
          type: 'info',
          title: 'System Update',
          message: 'New features available in Finance module',
          timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
        }
      ];
    } catch (err) {
      console.error('Error loading alerts:', err);
      return [];
    }
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'success':
        return <CheckCircleIcon color="success" />;
      default:
        return <NotificationsIcon color="info" />;
    }
  };

  const getActivityIcon = (type) => {
    switch (type) {
      case 'account_created':
        return <AccountBalanceIcon color="primary" />;
      case 'reconciliation_completed':
        return <CheckCircleIcon color="success" />;
      case 'gl_entry_created':
        return <AssessmentIcon color="info" />;
      default:
        return <NotificationsIcon color="action" />;
    }
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

  if (!dashboardData) {
    return (
      <Alert severity="info">
        No dashboard data available.
      </Alert>
    );
  }

  const { tenantInfo, modules, financeMetrics, systemHealth, recentActivity, alerts } = dashboardData;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Tenant Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Welcome to {tenantInfo?.name || currentTenant?.tenant_name}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadDashboardData}
            disabled={loadingData}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            disabled
          >
            Export Report
          </Button>
        </Box>
      </Box>

      {/* Alerts */}
      {alerts && alerts.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {alerts.map((alert) => (
            <Alert
              key={alert.id}
              severity={alert.type}
              sx={{ mb: 1 }}
              action={
                <IconButton size="small">
                  <SettingsIcon />
                </IconButton>
              }
            >
              <Typography variant="subtitle2" fontWeight="bold">
                {alert.title}
              </Typography>
              <Typography variant="body2">
                {alert.message}
              </Typography>
            </Alert>
          ))}
        </Box>
      )}

      <Grid container spacing={3}>
        {/* Tenant Information */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <BusinessIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Tenant Information
                </Typography>
              </Box>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <BusinessIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Company Name"
                    secondary={tenantInfo?.name || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <AccountBalanceIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Subscription Plan"
                    secondary={
                      <Chip 
                        label={tenantInfo?.subscription_plan || 'N/A'} 
                        size="small" 
                        color="primary" 
                      />
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SecurityIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Status"
                    secondary={
                      <Chip 
                        label={tenantInfo?.status || 'N/A'} 
                        size="small" 
                        color={tenantInfo?.status === 'active' ? 'success' : 'warning'}
                      />
                    }
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <PeopleIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Active Users"
                    secondary={systemHealth?.activeUsers || 'N/A'}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Finance Metrics */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <AssessmentIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                Finance Metrics
                </Typography>
              </Box>
              
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Chart of Accounts"
                    secondary={financeMetrics?.totalAccounts || 0}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="GL Entries"
                    secondary={financeMetrics?.totalGlEntries || 0}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Bank Accounts"
                    secondary={financeMetrics?.totalBankAccounts || 0}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Reconciliation Sessions"
                    secondary={financeMetrics?.totalReconciliationSessions || 0}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Pending Reconciliations"
                    secondary={
                      <Box display="flex" alignItems="center" gap={1}>
                        <Typography variant="body2">
                          {financeMetrics?.pendingReconciliations || 0}
                        </Typography>
                        {financeMetrics?.pendingReconciliations > 0 && (
                          <Chip label="Action Required" size="small" color="warning" />
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* System Health */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <SpeedIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  System Health
                </Typography>
              </Box>
              
              <List dense>
                <ListItem>
                  <ListItemIcon>
                    <TrendingUpIcon color="success" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Uptime"
                    secondary={systemHealth?.uptime || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <SpeedIcon color="info" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Response Time"
                    secondary={systemHealth?.responseTime || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <ErrorIcon color="error" />
                  </ListItemIcon>
                  <ListItemText
                    primary="Error Rate"
                    secondary={systemHealth?.errorRate || 'N/A'}
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <StorageIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary="Data Usage"
                    secondary={systemHealth?.dataUsage || 'N/A'}
                  />
                </ListItem>
              </List>
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
              
              <Grid container spacing={1}>
                {modules?.map((module) => (
                  <Grid item xs={6} sm={4} key={module.module_name}>
                    <Chip
                      label={module.module_name}
                      color={module.enabled ? 'success' : 'default'}
                      size="small"
                      icon={module.enabled ? <CheckCircleIcon /> : <ErrorIcon />}
                      sx={{ width: '100%' }}
                    />
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <NotificationsIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Recent Activity
                </Typography>
              </Box>
              
              <List dense>
                {recentActivity?.slice(0, 5).map((activity) => (
                  <ListItem key={activity.id}>
                    <ListItemIcon>
                      {getActivityIcon(activity.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={activity.description}
                      secondary={`${activity.user} • ${new Date(activity.timestamp).toLocaleString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <TrendingUpIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Performance Overview
                </Typography>
              </Box>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" color="success.main">
                      {systemHealth?.uptime || '99.9%'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      System Uptime
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" color="info.main">
                      {systemHealth?.responseTime || '120ms'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Avg Response Time
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" color="warning.main">
                      {systemHealth?.activeUsers || '25'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active Users
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Box textAlign="center">
                    <Typography variant="h4" fontWeight="bold" color="primary.main">
                      {financeMetrics?.totalAccounts || '0'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Accounts
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Last Updated */}
      {lastUpdated && (
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Last updated: {lastUpdated.toLocaleString()}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default TenantDashboard;












