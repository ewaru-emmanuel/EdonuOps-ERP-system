import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip, LinearProgress,
  IconButton, Tooltip, Alert, List, ListItem, ListItemIcon, ListItemText,
  Divider, Button, Dialog, DialogTitle, DialogContent, DialogActions
} from '@mui/material';
import {
  AccountBalance, TrendingUp, TrendingDown, Lock, LockOpen, 
  Schedule, CheckCircle, Warning, Error, Info, Timeline,
  AutoAwesome, Psychology, Lightbulb, Refresh, History
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const DailyCycleWidgets = () => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [cycleStatus, setCycleStatus] = useState(null);
  const [dailyBalances, setDailyBalances] = useState([]);
  const [auditTrail, setAuditTrail] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [auditDialog, setAuditDialog] = useState({ open: false, data: [] });

  // Real-time data hooks
  const { data: latestStatus, refresh: refreshLatest } = useRealTimeData('/api/finance/daily-cycle/latest-status');

  useEffect(() => {
    loadCycleStatus();
    loadDailyBalances();
    loadAuditTrail();
    loadTrendData();
  }, [selectedDate]);

  const loadCycleStatus = async () => {
    try {
      const response = await fetch(`/api/finance/daily-cycle/status/${selectedDate}`);
      const result = await response.json();
      if (result.success) {
        setCycleStatus(result.data);
      }
    } catch (error) {
      console.error('Error loading cycle status:', error);
    }
  };

  const loadDailyBalances = async () => {
    try {
      const response = await fetch(`/api/finance/daily-cycle/balances/${selectedDate}`);
      const result = await response.json();
      if (result.success) {
        setDailyBalances(result.data.balances || []);
      }
    } catch (error) {
      console.error('Error loading daily balances:', error);
    }
  };

  const loadAuditTrail = async () => {
    try {
      const response = await fetch(`/api/finance/daily-cycle/audit-trail/${selectedDate}`);
      const result = await response.json();
      if (result.success) {
        setAuditTrail(result.data.audit_trail || []);
      }
    } catch (error) {
      console.error('Error loading audit trail:', error);
    }
  };

  const loadTrendData = async () => {
    try {
      // Get last 30 days of closing balances
      const endDate = new Date(selectedDate);
      const startDate = new Date(endDate);
      startDate.setDate(startDate.getDate() - 30);
      
      const response = await fetch(`/api/finance/daily-cycle/trend-data?start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}`);
      const result = await response.json();
      if (result.success) {
        setTrendData(result.data || []);
      }
    } catch (error) {
      console.error('Error loading trend data:', error);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'failed': return 'error';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle />;
      case 'in_progress': return <Schedule />;
      case 'failed': return <Error />;
      case 'pending': return <Warning />;
      default: return <Info />;
    }
  };

  const calculateExpectedClosing = () => {
    if (!dailyBalances.length) return 0;
    
    return dailyBalances.reduce((total, balance) => {
      return total + (balance.opening_balance + balance.daily_net_movement);
    }, 0);
  };

  const calculateActualClosing = () => {
    if (!dailyBalances.length) return 0;
    
    return dailyBalances.reduce((total, balance) => {
      return total + balance.closing_balance;
    }, 0);
  };

  const getLockedAccountsCount = () => {
    return dailyBalances.filter(balance => balance.is_locked).length;
  };

  const getGracePeriodStatus = () => {
    const now = new Date();
    const gracePeriodEnds = dailyBalances.find(balance => balance.grace_period_ends)?.grace_period_ends;
    
    if (!gracePeriodEnds) return null;
    
    const graceEnd = new Date(gracePeriodEnds);
    const timeLeft = graceEnd - now;
    
    if (timeLeft <= 0) return { status: 'expired', message: 'Grace period expired' };
    if (timeLeft < 30 * 60 * 1000) return { status: 'warning', message: 'Grace period ending soon' };
    return { status: 'active', message: 'Grace period active' };
  };

  const refreshAll = () => {
    setLoading(true);
    loadCycleStatus();
    loadDailyBalances();
    loadAuditTrail();
    loadTrendData();
    refreshLatest();
    setTimeout(() => setLoading(false), 1000);
  };

  return (
    <Box sx={{ p: 2 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          Daily Cycle Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refreshAll}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Today's Opening Balance Widget */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AccountBalance color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Today's Opening Balance
                </Typography>
              </Box>
              <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                {formatCurrency(cycleStatus?.total_opening_balance || 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {cycleStatus?.accounts_processed || 0} accounts processed
              </Typography>
              <Chip
                icon={getStatusIcon(cycleStatus?.opening_status)}
                label={`Opening: ${cycleStatus?.opening_status || 'Unknown'}`}
                color={getStatusColor(cycleStatus?.opening_status)}
                size="small"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Expected Closing Widget */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp color="success" sx={{ mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Expected Closing (Live)
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold' }}>
                {formatCurrency(calculateExpectedClosing())}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Opening + Daily Movements
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary">
                  Opening: {formatCurrency(cycleStatus?.total_opening_balance || 0)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Movement: {formatCurrency(cycleStatus?.total_daily_movement || 0)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Actual Closing Widget */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <CheckCircle color="info" sx={{ mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Actual Closing Balance
                </Typography>
              </Box>
              <Typography variant="h4" color="info.main" sx={{ fontWeight: 'bold' }}>
                {formatCurrency(calculateActualClosing())}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {cycleStatus?.accounts_processed || 0} accounts closed
              </Typography>
              <Chip
                icon={getStatusIcon(cycleStatus?.closing_status)}
                label={`Closing: ${cycleStatus?.closing_status || 'Unknown'}`}
                color={getStatusColor(cycleStatus?.closing_status)}
                size="small"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Lock Status Widget */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Lock color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Lock Status
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h4" sx={{ fontWeight: 'bold', mr: 2 }}>
                  {getLockedAccountsCount()}
                </Typography>
                <Typography variant="body1" color="text.secondary">
                  of {dailyBalances.length} accounts locked
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={(getLockedAccountsCount() / Math.max(dailyBalances.length, 1)) * 100}
                sx={{ mb: 1 }}
              />
              {getGracePeriodStatus() && (
                <Alert 
                  severity={getGracePeriodStatus().status === 'expired' ? 'error' : 
                           getGracePeriodStatus().status === 'warning' ? 'warning' : 'info'}
                  sx={{ mt: 1 }}
                >
                  {getGracePeriodStatus().message}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Trend Chart Widget */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingUp color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Closing Balances Trend (30 Days)
                </Typography>
              </Box>
              {trendData.length > 0 ? (
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {formatCurrency(trendData[trendData.length - 1]?.closing_balance || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Latest closing balance
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Trend: {trendData.length > 1 ? 
                        (trendData[trendData.length - 1]?.closing_balance > trendData[trendData.length - 2]?.closing_balance ? 
                          '↗️ Rising' : '↘️ Falling') : 'No trend data'}
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No trend data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity Widget */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Timeline color="primary" sx={{ mr: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    Recent Activity
                  </Typography>
                </Box>
                <Button
                  size="small"
                  startIcon={<History />}
                  onClick={() => setAuditDialog({ open: true, data: auditTrail })}
                >
                  View Full History
                </Button>
              </Box>
              <List dense>
                {auditTrail.slice(0, 5).map((activity, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon>
                      {getStatusIcon(activity.action)}
                    </ListItemIcon>
                    <ListItemText
                      primary={activity.action.replace('_', ' ').toUpperCase()}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            by {activity.user_name || activity.user_id} • {formatTime(activity.timestamp)}
                          </Typography>
                          {activity.action_details && (
                            <Typography variant="caption" color="text.secondary">
                              {activity.affected_accounts} accounts • {formatCurrency(activity.total_amount)}
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
                {auditTrail.length === 0 && (
                  <ListItem sx={{ px: 0 }}>
                    <ListItemText
                      primary="No recent activity"
                      secondary="Activity will appear here as operations are performed"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Audit Trail Dialog */}
      <Dialog
        open={auditDialog.open}
        onClose={() => setAuditDialog({ open: false, data: [] })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Complete Audit Trail - {formatDate(selectedDate)}
        </DialogTitle>
        <DialogContent>
          <List>
            {auditDialog.data.map((activity, index) => (
              <React.Fragment key={index}>
                <ListItem>
                  <ListItemIcon>
                    {getStatusIcon(activity.action)}
                  </ListItemIcon>
                  <ListItemText
                    primary={activity.action.replace('_', ' ').toUpperCase()}
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary">
                          User: {activity.user_name || activity.user_id} ({activity.user_role || 'Unknown Role'})
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Time: {formatTime(activity.timestamp)} • IP: {activity.ip_address || 'Unknown'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Accounts: {activity.affected_accounts} • Amount: {formatCurrency(activity.total_amount)}
                        </Typography>
                        {activity.action_details && (
                          <Typography variant="caption" color="text.secondary">
                            Details: {JSON.stringify(activity.action_details, null, 2)}
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
                {index < auditDialog.data.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAuditDialog({ open: false, data: [] })}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DailyCycleWidgets;
