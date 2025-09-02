import React, { useState, useEffect, useMemo } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, IconButton, Chip, Avatar, Badge, Tooltip, Alert, LinearProgress, Skeleton,
  Dialog, DialogTitle, DialogContent, DialogActions, List, ListItem, ListItemText, ListItemIcon, Divider, SpeedDial, SpeedDialAction, SpeedDialIcon
} from '@mui/material';
import {
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, LocalTaxi, AccountBalanceWallet,
  Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  Add, Edit, Visibility, Delete, MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const SmartDashboard = ({ isMobile, isTablet }) => {
  const [selectedPeriod, setSelectedPeriod] = useState('current');
  const [refreshKey, setRefreshKey] = useState(0);
  const [insightsOpen, setInsightsOpen] = useState(false);

  // Real-time data hooks
  const { data: generalLedger, loading: glLoading } = useRealTimeData('/api/finance/general-ledger');
  const { data: accountsPayable, loading: apLoading } = useRealTimeData('/api/finance/accounts-payable');
  const { data: accountsReceivable, loading: arLoading } = useRealTimeData('/api/finance/accounts-receivable');
  const { data: fixedAssets, loading: assetsLoading } = useRealTimeData('/api/finance/fixed-assets');
  const { data: budgets, loading: budgetsLoading } = useRealTimeData('/api/finance/budgets');

  // Calculate real-time metrics
  const metrics = useMemo(() => {
    const totalAssets = fixedAssets?.reduce((sum, asset) => sum + (asset.current_value || 0), 0) || 0;
    const totalLiabilities = accountsPayable?.reduce((sum, ap) => sum + (ap.outstanding_amount || 0), 0) || 0;
    const totalEquity = totalAssets - totalLiabilities;
    
    const totalRevenue = generalLedger?.filter(entry => entry.account_type === 'Revenue')
      .reduce((sum, entry) => sum + (entry.credit_amount || 0), 0) || 0;
    const totalExpenses = generalLedger?.filter(entry => entry.account_type === 'Expense')
      .reduce((sum, entry) => sum + (entry.debit_amount || 0), 0) || 0;
    const netIncome = totalRevenue - totalExpenses;

    const totalAccountsReceivable = accountsReceivable?.reduce((sum, ar) => sum + (ar.outstanding_amount || 0), 0) || 0;
    const totalAccountsPayable = accountsPayable?.reduce((sum, ap) => sum + (ap.outstanding_amount || 0), 0) || 0;

    // Calculate trends (mock data for now)
    const previousRevenue = totalRevenue * 0.95; // 5% growth
    const previousExpenses = totalExpenses * 0.98; // 2% growth
    const revenueGrowth = ((totalRevenue - previousRevenue) / previousRevenue) * 100;
    const expenseGrowth = ((totalExpenses - previousExpenses) / previousExpenses) * 100;

    return {
      totalAssets,
      totalLiabilities,
      totalEquity,
      totalRevenue,
      totalExpenses,
      netIncome,
      accountsReceivable: totalAccountsReceivable,
      accountsPayable: totalAccountsPayable,
      revenueGrowth,
      expenseGrowth,
      cashFlow: totalAccountsReceivable - totalAccountsPayable,
      overdueInvoices: accountsReceivable?.filter(ar => ar.status === 'overdue').length || 0,
      pendingApprovals: accountsPayable?.filter(ap => ap.approval_status === 'pending').length || 0
    };
  }, [generalLedger, accountsPayable, accountsReceivable, fixedAssets]);

  // AI Insights (mock data)
  const aiInsights = useMemo(() => {
    const insights = [];
    
    if (metrics.revenueGrowth > 10) {
      insights.push({
        type: 'success',
        icon: <TrendingUp />,
        title: 'Strong Revenue Growth',
        message: `Revenue increased by ${metrics.revenueGrowth.toFixed(1)}% this period`,
        action: 'View Revenue Analysis'
      });
    }

    if (metrics.expenseGrowth > 15) {
      insights.push({
        type: 'warning',
        icon: <TrendingDown />,
        title: 'Expense Increase Alert',
        message: `Expenses grew by ${metrics.expenseGrowth.toFixed(1)}% - review spending patterns`,
        action: 'Review Expenses'
      });
    }

    if (metrics.overdueInvoices > 5) {
      insights.push({
        type: 'error',
        icon: <Warning />,
        title: 'Overdue Invoices',
        message: `${metrics.overdueInvoices} invoices are overdue - consider sending reminders`,
        action: 'Send Reminders'
      });
    }

    if (metrics.pendingApprovals > 10) {
      insights.push({
        type: 'info',
        icon: <Schedule />,
        title: 'Pending Approvals',
        message: `${metrics.pendingApprovals} invoices await approval - review queue`,
        action: 'Review Queue'
      });
    }

    return insights;
  }, [metrics]);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleInsightAction = (action) => {
    console.log('AI Insight Action:', action);
    setInsightsOpen(false);
  };

  return (
    <Box>
      {/* Header with Smart Controls */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" gutterBottom>
            Financial Intelligence Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time insights powered by AI • Last updated: {new Date().toLocaleTimeString()}
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={glLoading || apLoading || arLoading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<BarChart />}
            onClick={() => setInsightsOpen(true)}
          >
            AI Insights
          </Button>
        </Box>
      </Box>

      {/* Real-time KPI Cards */}
      <Grid container spacing={3} mb={3}>
        {/* Total Assets */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Total Assets
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${metrics.totalAssets.toLocaleString()}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>
                    +2.5% from last month
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  <AccountBalance sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
              {assetsLoading && (
                <LinearProgress sx={{ mt: 2, bgcolor: 'rgba(255,255,255,0.2)', '& .MuiLinearProgress-bar': { bgcolor: 'white' } }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Net Income */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: metrics.netIncome >= 0 
              ? 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
              : 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            color: 'white',
            position: 'relative'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Net Income
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${metrics.netIncome.toLocaleString()}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>
                    {metrics.revenueGrowth > 0 ? '+' : ''}{metrics.revenueGrowth.toFixed(1)}% revenue growth
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  {metrics.netIncome >= 0 ? <TrendingUp sx={{ fontSize: 28 }} /> : <TrendingDown sx={{ fontSize: 28 }} />}
                </Avatar>
              </Box>
              {glLoading && (
                <LinearProgress sx={{ mt: 2, bgcolor: 'rgba(255,255,255,0.2)', '& .MuiLinearProgress-bar': { bgcolor: 'white' } }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Accounts Receivable */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            position: 'relative'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Accounts Receivable
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${metrics.accountsReceivable.toLocaleString()}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip 
                      label={`${metrics.overdueInvoices} overdue`} 
                      size="small" 
                      color={metrics.overdueInvoices > 0 ? 'error' : 'success'}
                    />
                  </Box>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
                  <Receipt sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
              {arLoading && <LinearProgress sx={{ mt: 2 }} />}
            </CardContent>
          </Card>
        </Grid>

        {/* Accounts Payable */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
            position: 'relative'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Accounts Payable
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${metrics.accountsPayable.toLocaleString()}
                  </Typography>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip 
                      label={`${metrics.pendingApprovals} pending`} 
                      size="small" 
                      color={metrics.pendingApprovals > 0 ? 'warning' : 'success'}
                    />
                  </Box>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main', width: 56, height: 56 }}>
                  <Payment sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
              {apLoading && <LinearProgress sx={{ mt: 2 }} />}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Smart Alerts & Insights */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Smart Alerts & Recommendations
              </Typography>
              <List>
                {aiInsights.map((insight, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Avatar sx={{ 
                        bgcolor: insight.type === 'success' ? 'success.main' : 
                                insight.type === 'warning' ? 'warning.main' :
                                insight.type === 'error' ? 'error.main' : 'info.main',
                        width: 40, height: 40
                      }}>
                        {insight.icon}
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={insight.title}
                      secondary={insight.message}
                      primaryTypographyProps={{ fontWeight: 'bold' }}
                    />
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleInsightAction(insight.action)}
                    >
                      {insight.action}
                    </Button>
                  </ListItem>
                ))}
                {aiInsights.length === 0 && (
                  <ListItem>
                    <ListItemIcon>
                      <Avatar sx={{ bgcolor: 'success.main', width: 40, height: 40 }}>
                        <CheckCircle />
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary="All Systems Normal"
                      secondary="No critical alerts at this time"
                      primaryTypographyProps={{ fontWeight: 'bold' }}
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  New Journal Entry
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Receipt />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Create Invoice
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Payment />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Record Bill
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Assessment />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                >
                  Generate Report
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Cash Flow Summary */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Cash Flow Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h4" color="success.main" gutterBottom>
                  ${metrics.cashFlow.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Net Cash Flow
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h6" color="info.main" gutterBottom>
                  ${metrics.accountsReceivable.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Cash In (AR)
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h6" color="warning.main" gutterBottom>
                  ${metrics.accountsPayable.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Cash Out (AP)
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* AI Insights Dialog */}
      <Dialog
        open={insightsOpen}
        onClose={() => setInsightsOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <BarChart />
            </Avatar>
            <Typography variant="h6">AI-Powered Financial Insights</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Based on your financial data patterns, here are intelligent recommendations:
          </Typography>
          
          <List>
            <ListItem>
              <ListItemIcon>
                <TrendingUp color="success" />
              </ListItemIcon>
              <ListItemText
                primary="Revenue Optimization Opportunity"
                secondary="Your Q4 revenue shows 15% growth potential based on historical patterns"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <Warning color="warning" />
              </ListItemIcon>
              <ListItemText
                primary="Cash Flow Alert"
                secondary="Consider delaying AP payments by 15 days to improve cash position"
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <Info color="info" />
              </ListItemIcon>
              <ListItemText
                primary="Budget Variance"
                secondary="Marketing spend is 12% under budget - opportunity for Q4 campaigns"
              />
            </ListItem>
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInsightsOpen(false)}>Close</Button>
          <Button variant="contained" onClick={() => setInsightsOpen(false)}>
            Apply Recommendations
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button for Quick Actions */}
      <SpeedDial
        ariaLabel="Quick Actions"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        <SpeedDialAction
          icon={<Add />}
          tooltipTitle="New Entry"
          onClick={() => console.log('New Entry')}
        />
        <SpeedDialAction
          icon={<Receipt />}
          tooltipTitle="Create Invoice"
          onClick={() => console.log('Create Invoice')}
        />
        <SpeedDialAction
          icon={<Payment />}
          tooltipTitle="Record Bill"
          onClick={() => console.log('Record Bill')}
        />
        <SpeedDialAction
          icon={<Assessment />}
          tooltipTitle="Generate Report"
          onClick={() => console.log('Generate Report')}
        />
      </SpeedDial>
    </Box>
  );
};

export default SmartDashboard;
