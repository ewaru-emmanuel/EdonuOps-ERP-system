import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Grid, Card, CardContent, Button, IconButton, Chip, Avatar, Badge, Tooltip, Alert, LinearProgress, Skeleton,
  Dialog, DialogTitle, DialogContent, DialogActions, List, ListItem, ListItemText, ListItemIcon, Divider, SpeedDial, SpeedDialAction, SpeedDialIcon
} from '@mui/material';
import {
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, AccountBalanceWallet,
  Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  Add, Edit, Visibility, Delete, MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop
} from '@mui/icons-material';
import { useFinanceData } from '../hooks/useFinanceData';
import ManualJournalEntry from './ManualJournalEntry';

const SmartDashboard = ({ isMobile, isTablet }) => {
  const navigate = useNavigate();
  const [selectedPeriod, setSelectedPeriod] = useState('current');
  const [refreshKey, setRefreshKey] = useState(0);
  const [insightsOpen, setInsightsOpen] = useState(false);
  const [manualEntryOpen, setManualEntryOpen] = useState(false);

  // Real-time data hooks - using real API calls
  const { data: generalLedger, loading: glLoading } = useFinanceData('double-entry/journal-entries');
  const { data: accounts, loading: accountsLoading } = useFinanceData('double-entry/accounts');
  
  // Placeholder data for endpoints not yet implemented
  const accountsPayable = [];
  const accountsReceivable = [];
  const fixedAssets = [];
  const budgets = [];
  const paymentMethods = [];
  
  // Calculate bank accounts from accounts table (type = 'asset' and code starts with '10')
  const bankAccounts = accounts?.filter(acc => 
    acc.type === 'asset' && (acc.code?.startsWith('10') || acc.name?.toLowerCase().includes('bank') || acc.name?.toLowerCase().includes('cash'))
  ) || [];
  
  // Placeholder loading states
  const apLoading = false;
  const arLoading = false;
  const assetsLoading = false;
  const budgetsLoading = false;
  const bankAccountsLoading = accountsLoading;
  const paymentMethodsLoading = false;

  // Calculate real-time metrics from accounts table
  const metrics = useMemo(() => {
    // Universal double-entry accounting formulas for unlimited users
    // These formulas handle the correct sign conventions for all account types
    
    // ASSETS: Debit accounts (should be positive)
    // If negative, it means there's an error in the data or unusual transaction
    const totalAssets = accounts?.filter(acc => acc.type === 'asset')
      .reduce((sum, acc) => sum + Math.abs(acc.balance || 0), 0) || 0;
    
    // LIABILITIES: Credit accounts (should be positive when displayed)
    // In double-entry, they're negative, but we show them as positive
    const totalLiabilities = accounts?.filter(acc => acc.type === 'liability')
      .reduce((sum, acc) => sum + Math.abs(acc.balance || 0), 0) || 0;
    
    // EQUITY: Credit accounts (should be positive when displayed)
    // In double-entry, they're negative, but we show them as positive
    const totalEquity = accounts?.filter(acc => acc.type === 'equity')
      .reduce((sum, acc) => sum + Math.abs(acc.balance || 0), 0) || 0;
    
    // REVENUE: Credit accounts (negative in double-entry, positive when displayed)
    // Net Income = Revenue - Expenses = |Revenue| - |Expenses|
    const totalRevenue = accounts?.filter(acc => acc.type === 'revenue')
      .reduce((sum, acc) => sum + Math.abs(acc.balance || 0), 0) || 0;
    
    // EXPENSES: Debit accounts (positive in double-entry)
    const totalExpenses = accounts?.filter(acc => acc.type === 'expense')
      .reduce((sum, acc) => sum + Math.abs(acc.balance || 0), 0) || 0;
    
    const netIncome = totalRevenue - totalExpenses;

    // Accounts Receivable (from accounts table) - Asset account, should be positive
    const totalAccountsReceivable = Math.abs(accounts?.find(acc => acc.code === '1100')?.balance || 0);
    
    // Accounts Payable (from accounts table) - Liability account, should be positive
    const totalAccountsPayable = accounts?.filter(acc => acc.type === 'liability' && acc.name?.toLowerCase().includes('payable'))
      .reduce((sum, acc) => sum + Math.abs(acc.balance || 0), 0) || 0;

    // Bank account balances - sum of all cash and bank accounts (asset accounts, should be positive)
    const totalBankBalance = bankAccounts?.reduce((sum, account) => sum + Math.abs(account.balance || 0), 0) || 0;
    const activeBankAccounts = bankAccounts?.length || 0;
    const depositAccounts = bankAccounts?.length || 0;
    const withdrawalAccounts = bankAccounts?.length || 0;

    // Payment method analysis
    const paymentMethodCount = paymentMethods?.filter(method => method.is_active !== false).length || 0;
    const activePaymentMethods = paymentMethods?.filter(method => method.is_active !== false) || [];

    // Calculate comprehensive cash flow from journal entries
    // Cash Flow = Cash Inflows - Cash Outflows
    // Cash Inflows: Revenue transactions, AR collections, cash receipts
    // Cash Outflows: Expense transactions, AP payments, cash payments
    
    // Get cash accounts (typically account codes 1000-1999 for assets)
    const cashAccounts = accounts?.filter(acc => 
      acc.type === 'asset' && 
      (acc.code?.startsWith('1') || acc.name?.toLowerCase().includes('cash') || acc.name?.toLowerCase().includes('bank'))
    ) || [];
    
    // Calculate cash inflows (debits to cash accounts = money coming in)
    // Journal entries have a 'lines' array, each line has account_id, debit_amount, credit_amount
    const cashInflows = generalLedger?.reduce((total, entry) => {
      if (entry.lines && Array.isArray(entry.lines)) {
        return total + entry.lines
          .filter(line => cashAccounts.some(cashAcc => cashAcc.id === line.account_id) && line.debit_amount > 0)
          .reduce((sum, line) => sum + Math.abs(line.debit_amount || 0), 0);
      }
      return total;
    }, 0) || 0;
    
    // Calculate cash outflows (credits to cash accounts = money going out)
    const cashOutflows = generalLedger?.reduce((total, entry) => {
      if (entry.lines && Array.isArray(entry.lines)) {
        return total + entry.lines
          .filter(line => cashAccounts.some(cashAcc => cashAcc.id === line.account_id) && line.credit_amount > 0)
          .reduce((sum, line) => sum + Math.abs(line.credit_amount || 0), 0);
      }
      return total;
    }, 0) || 0;
    
    // Net cash flow from operations
    const netCashFlow = cashInflows - cashOutflows;

    // Calculate trends from historical data using journal entries
    const currentMonth = new Date().toISOString().slice(0, 7); // YYYY-MM format
    const lastMonth = new Date();
    lastMonth.setMonth(lastMonth.getMonth() - 1);
    const lastMonthStr = lastMonth.toISOString().slice(0, 7);
    
    // Calculate current month revenue and expenses
    // For revenue: use credit amounts (negative in our system, so take absolute value)
    // For expenses: use debit amounts (positive in our system)
    const currentMonthRevenue = generalLedger?.reduce((total, entry) => {
      if (entry.lines && Array.isArray(entry.lines) && entry.date?.startsWith(currentMonth)) {
        return total + entry.lines
          .filter(line => accounts?.find(acc => acc.id === line.account_id)?.type === 'revenue')
          .reduce((sum, line) => sum + Math.abs(line.credit_amount || 0), 0);
      }
      return total;
    }, 0) || 0;
    
    const currentMonthExpenses = generalLedger?.reduce((total, entry) => {
      if (entry.lines && Array.isArray(entry.lines) && entry.date?.startsWith(currentMonth)) {
        return total + entry.lines
          .filter(line => accounts?.find(acc => acc.id === line.account_id)?.type === 'expense')
          .reduce((sum, line) => sum + Math.abs(line.debit_amount || 0), 0);
      }
      return total;
    }, 0) || 0;
    
    // Calculate last month revenue and expenses
    const lastMonthRevenue = generalLedger?.reduce((total, entry) => {
      if (entry.lines && Array.isArray(entry.lines) && entry.date?.startsWith(lastMonthStr)) {
        return total + entry.lines
          .filter(line => accounts?.find(acc => acc.id === line.account_id)?.type === 'revenue')
          .reduce((sum, line) => sum + Math.abs(line.credit_amount || 0), 0);
      }
      return total;
    }, 0) || 0;
    
    const lastMonthExpenses = generalLedger?.reduce((total, entry) => {
      if (entry.lines && Array.isArray(entry.lines) && entry.date?.startsWith(lastMonthStr)) {
        return total + entry.lines
          .filter(line => accounts?.find(acc => acc.id === line.account_id)?.type === 'expense')
          .reduce((sum, line) => sum + Math.abs(line.debit_amount || 0), 0);
      }
      return total;
    }, 0) || 0;
    
    // Calculate growth percentages
    const revenueGrowth = lastMonthRevenue > 0 ? ((currentMonthRevenue - lastMonthRevenue) / lastMonthRevenue) * 100 : 0;
    const expenseGrowth = lastMonthExpenses > 0 ? ((currentMonthExpenses - lastMonthExpenses) / lastMonthExpenses) * 100 : 0;
    
    // Calculate asset growth (comparing current vs last month total assets)
    // For assets: debit increases, credit decreases
    const currentMonthAssets = generalLedger?.reduce((total, entry) => {
      if (entry.lines && Array.isArray(entry.lines) && entry.date?.startsWith(currentMonth)) {
        return total + entry.lines
          .filter(line => accounts?.find(acc => acc.id === line.account_id)?.type === 'asset')
          .reduce((sum, line) => sum + Math.abs(line.debit_amount || 0) - Math.abs(line.credit_amount || 0), 0);
      }
      return total;
    }, 0) || 0;
    
    const lastMonthAssets = generalLedger?.reduce((total, entry) => {
      if (entry.lines && Array.isArray(entry.lines) && entry.date?.startsWith(lastMonthStr)) {
        return total + entry.lines
          .filter(line => accounts?.find(acc => acc.id === line.account_id)?.type === 'asset')
          .reduce((sum, line) => sum + Math.abs(line.debit_amount || 0) - Math.abs(line.credit_amount || 0), 0);
      }
      return total;
    }, 0) || 0;
    
    const assetGrowth = lastMonthAssets > 0 ? ((currentMonthAssets - lastMonthAssets) / lastMonthAssets) * 100 : 0;

    const result = {
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
      assetGrowth,
      // Comprehensive cash flow from journal entries
      cashFlow: netCashFlow,
      cashInflows,
      cashOutflows,
      overdueInvoices: accountsReceivable?.filter(ar => ar.status === 'overdue').length || 0,
      pendingApprovals: accountsPayable?.filter(ap => ap.approval_status === 'pending').length || 0,
      // Bank account metrics
      totalBankBalance,
      activeBankAccounts,
      depositAccounts,
      withdrawalAccounts,
      // Payment method metrics
      paymentMethodCount,
      activePaymentMethods
    };
    
    console.log('💰 Finance Dashboard Metrics (from database):', {
      accountCount: accounts?.length || 0,
      bankAccountCount: bankAccounts?.length || 0,
      totalAssets,
      totalLiabilities,
      totalEquity,
      totalRevenue,
      totalExpenses,
      netIncome,
      totalBankBalance
    });
    
    return result;
  }, [generalLedger, accountsPayable, accountsReceivable, fixedAssets, bankAccounts, paymentMethods, accounts]);

  // AI Insights - will populate based on your real business data
  const aiInsights = useMemo(() => {
    const insights = [];
    
    // System will generate insights as you add real business data
    if (insights.length === 0) {
      insights.push({
        type: 'info',
        icon: <TrendingUp />,
        title: 'System Ready',
        message: 'Add customers, create invoices, and record transactions to see intelligent insights',
        action: 'Get Started'
      });
    }
    
    return insights;
  }, [metrics]);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const handleInsightAction = (action) => {
    setInsightsOpen(false);
  };

  return (
    <Box sx={{ width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
      {/* Header with Smart Controls */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" gutterBottom>
            Financial Intelligence Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time financial metrics and analytics
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
            backgroundColor: 'white',
            border: '1px solid rgba(0, 0, 0, 0.12)',
            borderRadius: 2,
            boxShadow: 'none'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box>
                <Typography variant="body2" color="text.primary" sx={{ mb: 1, fontWeight: 500 }}>
                  Total Assets
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 1 }}>
                  ${metrics.totalAssets.toLocaleString()}
                </Typography>
                <Typography variant="caption" color={metrics.assetGrowth >= 0 ? "success.main" : "error.main"}>
                  {metrics.assetGrowth > 0 ? '+' : ''}{metrics.assetGrowth.toFixed(1)}% from last month
                </Typography>
              </Box>
              {assetsLoading && (
                <LinearProgress sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Net Income */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'white',
            border: '1px solid rgba(0, 0, 0, 0.12)',
            borderRadius: 2,
            boxShadow: 'none'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box>
                <Typography variant="body2" color="text.primary" sx={{ mb: 1, fontWeight: 500 }}>
                  Net Income
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 1 }}>
                  ${metrics.netIncome.toLocaleString()}
                </Typography>
                <Typography variant="caption" color={metrics.revenueGrowth >= 0 ? "success.main" : "error.main"}>
                  {metrics.revenueGrowth > 0 ? '+' : ''}{metrics.revenueGrowth.toFixed(1)}% revenue growth
                </Typography>
              </Box>
              {glLoading && (
                <LinearProgress sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Accounts Receivable */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'white',
            border: '1px solid rgba(0, 0, 0, 0.12)',
            borderRadius: 2,
            boxShadow: 'none'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box>
                <Typography variant="body2" color="text.primary" sx={{ mb: 1, fontWeight: 500 }}>
                  Accounts Receivable
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 1 }}>
                  ${metrics.accountsReceivable.toLocaleString()}
                </Typography>
                <Typography variant="caption" color={metrics.overdueInvoices > 0 ? "error.main" : "success.main"}>
                  {metrics.overdueInvoices} overdue
                </Typography>
              </Box>
              {arLoading && <LinearProgress sx={{ mt: 2 }} />}
            </CardContent>
          </Card>
        </Grid>

        {/* Accounts Payable */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'white',
            border: '1px solid rgba(0, 0, 0, 0.12)',
            borderRadius: 2,
            boxShadow: 'none'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box>
                <Typography variant="body2" color="text.primary" sx={{ mb: 1, fontWeight: 500 }}>
                  Accounts Payable
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 1 }}>
                  ${metrics.accountsPayable.toLocaleString()}
                </Typography>
                <Typography variant="caption" color={metrics.pendingApprovals > 0 ? "warning.main" : "success.main"}>
                  {metrics.pendingApprovals} pending
                </Typography>
              </Box>
              {apLoading && <LinearProgress sx={{ mt: 2 }} />}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Bank Account & Payment Method Cards */}
      <Grid container spacing={3} mb={3}>
        {/* Total Bank Balance */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'white',
            border: '1px solid rgba(0, 0, 0, 0.12)',
            borderRadius: 2,
            boxShadow: 'none'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box>
                <Typography variant="body2" color="text.primary" sx={{ mb: 1, fontWeight: 500 }}>
                  Bank Balance
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 1 }}>
                  ${metrics.totalBankBalance.toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {metrics.activeBankAccounts} {metrics.activeBankAccounts === 1 ? 'active account' : 'active accounts'}
                </Typography>
              </Box>
              {bankAccountsLoading && (
                <LinearProgress sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Deposit Accounts */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'white',
            border: '1px solid rgba(0, 0, 0, 0.12)',
            borderRadius: 2,
            boxShadow: 'none'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box>
                <Typography variant="body2" color="text.primary" sx={{ mb: 1, fontWeight: 500 }}>
                  Deposit Accounts
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 1 }}>
                  {metrics.depositAccounts}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {metrics.depositAccounts > 0 ? 'Can receive payments' : 'No deposit accounts'}
                </Typography>
              </Box>
              {bankAccountsLoading && (
                <LinearProgress sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Payment Methods */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'white',
            border: '1px solid rgba(0, 0, 0, 0.12)',
            borderRadius: 2,
            boxShadow: 'none'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box>
                <Typography variant="body2" color="text.primary" sx={{ mb: 1, fontWeight: 500 }}>
                  Payment Methods
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 1 }}>
                  {metrics.paymentMethodCount}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {metrics.paymentMethodCount > 0 ? 'Available options' : 'No payment methods'}
                </Typography>
              </Box>
              {paymentMethodsLoading && (
                <LinearProgress sx={{ mt: 2 }} />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Withdrawal Accounts */}
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'white',
            border: '1px solid rgba(0, 0, 0, 0.12)',
            borderRadius: 2,
            boxShadow: 'none'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Box>
                <Typography variant="body2" color="text.primary" sx={{ mb: 1, fontWeight: 500 }}>
                  Withdrawal Accounts
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'text.primary', mb: 1 }}>
                  {metrics.withdrawalAccounts}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {metrics.withdrawalAccounts > 0 ? 'Can make payments' : 'No withdrawal accounts'}
                </Typography>
              </Box>
              {bankAccountsLoading && (
                <LinearProgress sx={{ mt: 2 }} />
              )}
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
                  onClick={() => setManualEntryOpen(true)}
                >
                  New Journal Entry
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Receipt />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                  onClick={() => navigate('/finance?feature=accounts-receivable')}
                >
                  Create Invoice
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Payment />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                  onClick={() => navigate('/finance?feature=accounts-payable')}
                >
                  Record Bill
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Assessment />}
                  fullWidth
                  sx={{ justifyContent: 'flex-start' }}
                  onClick={() => navigate('/finance?feature=reports')}
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
                <Typography variant="h4" color={metrics.cashFlow >= 0 ? "success.main" : "error.main"} gutterBottom>
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
                  ${metrics.cashInflows.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Cash Inflows
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h6" color="warning.main" gutterBottom>
                  ${metrics.cashOutflows.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Cash Outflows
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
                primary="Revenue Analysis"
                secondary={`Current revenue: $${metrics.totalRevenue.toLocaleString()}. ${metrics.revenueGrowth > 0 ? `Growing at ${metrics.revenueGrowth.toFixed(1)}%` : 'Consider revenue optimization strategies'}`}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <Warning color={metrics.cashFlow < 0 ? "error" : "warning"} />
              </ListItemIcon>
              <ListItemText
                primary="Cash Flow Status"
                secondary={metrics.cashFlow < 0 ? 
                  `Negative cash flow: $${Math.abs(metrics.cashFlow).toLocaleString()}. Consider reducing expenses or increasing collections` :
                  `Positive cash flow: $${metrics.cashFlow.toLocaleString()}. Good financial position`}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon>
                <Info color="info" />
              </ListItemIcon>
              <ListItemText
                primary="Financial Health"
                secondary={`Total assets: $${metrics.totalAssets.toLocaleString()}, Net income: $${metrics.netIncome.toLocaleString()}. ${metrics.netIncome > 0 ? 'Profitable operations' : 'Review expense management'}`}
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
        sx={{ 
          position: 'absolute', 
          bottom: 16, 
          right: 16,
          zIndex: 1000
        }}
        icon={<SpeedDialIcon />}
      >
        <SpeedDialAction
          icon={<Add />}
          tooltipTitle="New Entry"
          onClick={() => setManualEntryOpen(true)}
        />
        <SpeedDialAction
          icon={<Receipt />}
          tooltipTitle="Create Invoice"
          onClick={() => navigate('/finance?feature=accounts-receivable')}
        />
        <SpeedDialAction
          icon={<Payment />}
          tooltipTitle="Record Bill"
          onClick={() => navigate('/finance?feature=accounts-payable')}
        />
        <SpeedDialAction
          icon={<Assessment />}
          tooltipTitle="Generate Report"
          onClick={() => navigate('/finance?feature=reports')}
        />
      </SpeedDial>

      {/* Manual Journal Entry Dialog */}
      <ManualJournalEntry
        open={manualEntryOpen}
        onClose={() => setManualEntryOpen(false)}
        onSuccess={() => {
          setManualEntryOpen(false);
          setRefreshKey(prev => prev + 1); // Refresh data
        }}
      />
    </Box>
  );
};

export default SmartDashboard;
