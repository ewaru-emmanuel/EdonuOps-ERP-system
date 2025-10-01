import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Alert, Snackbar,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Chip, LinearProgress, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, FormControl, InputLabel, Select, MenuItem, IconButton,
  Tooltip, Divider, List, ListItem, ListItemIcon, ListItemText, InputAdornment
} from '@mui/material';
import {
  PlayArrow, Pause, Refresh, CheckCircle, Warning, Error, Info,
  Schedule, AccountBalance, TrendingUp, TrendingDown, Timeline,
  AutoAwesome, Psychology, Lightbulb, CalendarToday, Assessment
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const DailyCycleManager = () => {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [cycleStatus, setCycleStatus] = useState(null);
  const [dailyBalances, setDailyBalances] = useState([]);
  const [transactionSummary, setTransactionSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [detailsDialog, setDetailsDialog] = useState({ open: false, data: null });
  const [cashReconciliationDialog, setCashReconciliationDialog] = useState(false);
  const [cashReconciliation, setCashReconciliation] = useState({
    cash_on_hand: '',
    cash_receipts: '',
    cash_payments: '',
    bank_deposits: '',
    variance: 0,
    notes: ''
  });

  // Real-time data hooks
  const { data: pendingCycles, loading: pendingLoading, refresh: refreshPending } = useRealTimeData('/api/finance/daily-cycle/pending-cycles');
  const { data: latestStatus, loading: latestLoading, refresh: refreshLatest } = useRealTimeData('/api/finance/daily-cycle/latest-status');
  const { data: paymentMethods, loading: paymentMethodsLoading } = useRealTimeData('/api/finance/payment-methods');
  const { data: bankAccounts, loading: bankAccountsLoading } = useRealTimeData('/api/finance/bank-accounts');
  const { data: dailyCashFlow, loading: cashFlowLoading } = useRealTimeData(`/api/finance/daily-cash-flow?date=${selectedDate}`);

  useEffect(() => {
    loadCycleStatus();
    loadDailyBalances();
    loadTransactionSummary();
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

  const loadTransactionSummary = async () => {
    try {
      const response = await fetch(`/api/finance/daily-cycle/transaction-summary/${selectedDate}`);
      const result = await response.json();
      if (result.success) {
        setTransactionSummary(result.data);
      }
    } catch (error) {
      console.error('Error loading transaction summary:', error);
    }
  };

  const executeOperation = async (operation) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/finance/daily-cycle/${operation}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ cycle_date: selectedDate })
      });
      
      const result = await response.json();
      if (result.success) {
        setSnackbar({
          open: true,
          message: result.data.message,
          severity: 'success'
        });
        // Refresh all data
        loadCycleStatus();
        loadDailyBalances();
        loadTransactionSummary();
        refreshPending();
        refreshLatest();
      } else {
        setSnackbar({
          open: true,
          message: result.error || 'Operation failed',
          severity: 'error'
        });
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Network error occurred',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
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
      case 'pending': return <Pause />;
      default: return <Info />;
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

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold' }}>
          Daily Cycle Manager
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage daily opening and closing balances for all financial accounts
        </Typography>
      </Box>

      {/* Date Selection and Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Cycle Date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={9}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={() => executeOperation('capture-opening')}
                  disabled={loading || cycleStatus?.opening_status === 'completed'}
                  color="primary"
                >
                  Capture Opening Balances
                </Button>
                <Button
                  variant="contained"
                  startIcon={<CheckCircle />}
                  onClick={() => executeOperation('calculate-closing')}
                  disabled={loading || cycleStatus?.closing_status === 'completed'}
                  color="secondary"
                >
                  Calculate Closing Balances
                </Button>
                <Button
                  variant="contained"
                  startIcon={<AutoAwesome />}
                  onClick={() => executeOperation('execute-full-cycle')}
                  disabled={loading}
                  color="success"
                >
                  Execute Full Cycle
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<AccountBalance />}
                  onClick={() => setCashReconciliationDialog(true)}
                  disabled={loading}
                  color="primary"
                >
                  Cash Reconciliation
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={() => {
                    loadCycleStatus();
                    loadDailyBalances();
                    loadTransactionSummary();
                  }}
                  disabled={loading}
                >
                  Refresh
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Cycle Status */}
      {cycleStatus && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              Cycle Status - {formatDate(cycleStatus.cycle_date)}
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Chip
                    icon={getStatusIcon(cycleStatus.opening_status)}
                    label={`Opening: ${cycleStatus.opening_status}`}
                    color={getStatusColor(cycleStatus.opening_status)}
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {cycleStatus.accounts_processed} / {cycleStatus.total_accounts} accounts
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Chip
                    icon={getStatusIcon(cycleStatus.closing_status)}
                    label={`Closing: ${cycleStatus.closing_status}`}
                    color={getStatusColor(cycleStatus.closing_status)}
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {formatCurrency(cycleStatus.total_daily_movement)} movement
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <Chip
                    icon={getStatusIcon(cycleStatus.overall_status)}
                    label={`Overall: ${cycleStatus.overall_status}`}
                    color={getStatusColor(cycleStatus.overall_status)}
                    sx={{ mb: 1 }}
                  />
                  <Typography variant="body2" color="text.secondary">
                    {formatCurrency(cycleStatus.total_closing_balance)} total
                  </Typography>
                </Box>
              </Grid>
            </Grid>
            {cycleStatus.error_message && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {cycleStatus.error_message}
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Transaction Summary */}
      {transactionSummary && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
              Daily Transaction Summary
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {transactionSummary.total_transactions}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Transactions
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="success">
                    {formatCurrency(transactionSummary.total_debits)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Debits
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="error">
                    {formatCurrency(transactionSummary.total_credits)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Credits
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color={transactionSummary.net_movement >= 0 ? 'success' : 'error'}>
                    {formatCurrency(transactionSummary.net_movement)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Net Movement
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Daily Balances Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
            Daily Balances - {formatDate(selectedDate)}
          </Typography>
          <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Account</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Opening Balance</TableCell>
                  <TableCell align="right">Daily Debit</TableCell>
                  <TableCell align="right">Daily Credit</TableCell>
                  <TableCell align="right">Net Movement</TableCell>
                  <TableCell align="right">Closing Balance</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {dailyBalances.map((balance) => (
                  <TableRow key={balance.id}>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                        {balance.account_name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={balance.account_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(balance.opening_balance)}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(balance.daily_debit)}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(balance.daily_credit)}
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        variant="body2"
                        color={balance.daily_net_movement >= 0 ? 'success.main' : 'error.main'}
                      >
                        {formatCurrency(balance.daily_net_movement)}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                        {formatCurrency(balance.closing_balance)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getStatusIcon(balance.cycle_status)}
                        label={balance.cycle_status}
                        size="small"
                        color={getStatusColor(balance.cycle_status)}
                      />
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton
                          size="small"
                          onClick={() => setDetailsDialog({ open: true, data: balance })}
                        >
                          <Info />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Details Dialog */}
      <Dialog
        open={detailsDialog.open}
        onClose={() => setDetailsDialog({ open: false, data: null })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Account Balance Details
        </DialogTitle>
        <DialogContent>
          {detailsDialog.data && (
            <Box>
              <Typography variant="h6" gutterBottom>
                {detailsDialog.data.account_name}
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Opening Balance
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(detailsDialog.data.opening_balance)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Closing Balance
                  </Typography>
                  <Typography variant="h6">
                    {formatCurrency(detailsDialog.data.closing_balance)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Daily Debit
                  </Typography>
                  <Typography variant="body1" color="success.main">
                    {formatCurrency(detailsDialog.data.daily_debit)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Daily Credit
                  </Typography>
                  <Typography variant="body1" color="error.main">
                    {formatCurrency(detailsDialog.data.daily_credit)}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialog({ open: false, data: null })}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Cash Reconciliation Dialog */}
      <Dialog
        open={cashReconciliationDialog}
        onClose={() => setCashReconciliationDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Daily Cash Reconciliation - {new Date(selectedDate).toLocaleDateString()}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Reconcile cash transactions by payment method for accurate daily closing
            </Alert>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Cash on Hand (Opening)"
                  type="number"
                  fullWidth
                  value={cashReconciliation.cash_on_hand}
                  onChange={(e) => setCashReconciliation({...cashReconciliation, cash_on_hand: e.target.value})}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Cash Receipts (Today)"
                  type="number"
                  fullWidth
                  value={cashReconciliation.cash_receipts}
                  onChange={(e) => setCashReconciliation({...cashReconciliation, cash_receipts: e.target.value})}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Cash Payments (Today)"
                  type="number"
                  fullWidth
                  value={cashReconciliation.cash_payments}
                  onChange={(e) => setCashReconciliation({...cashReconciliation, cash_payments: e.target.value})}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Bank Deposits (Today)"
                  type="number"
                  fullWidth
                  value={cashReconciliation.bank_deposits}
                  onChange={(e) => setCashReconciliation({...cashReconciliation, bank_deposits: e.target.value})}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              
              {/* Calculated Fields */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                  Reconciliation Summary
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Expected Cash Balance"
                  type="number"
                  fullWidth
                  value={
                    (parseFloat(cashReconciliation.cash_on_hand || 0) + 
                     parseFloat(cashReconciliation.cash_receipts || 0) - 
                     parseFloat(cashReconciliation.cash_payments || 0) - 
                     parseFloat(cashReconciliation.bank_deposits || 0)).toFixed(2)
                  }
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                    readOnly: true
                  }}
                  disabled
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Variance"
                  type="number"
                  fullWidth
                  value={cashReconciliation.variance}
                  onChange={(e) => setCashReconciliation({...cashReconciliation, variance: parseFloat(e.target.value) || 0})}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                  color={Math.abs(cashReconciliation.variance) > 5 ? 'error' : 'success'}
                  helperText={Math.abs(cashReconciliation.variance) > 5 ? 'Large variance - investigate' : 'Variance within tolerance'}
                />
              </Grid>
              
              {/* Payment Method Breakdown */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                  Payment Method Breakdown
                </Typography>
              </Grid>
              {paymentMethods && paymentMethods.map((method) => (
                <Grid item xs={12} sm={6} md={4} key={method.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        {method.name}
                      </Typography>
                      <TextField
                        label="Amount"
                        type="number"
                        size="small"
                        fullWidth
                        InputProps={{
                          startAdornment: <InputAdornment position="start">$</InputAdornment>,
                        }}
                        placeholder="Daily total"
                      />
                    </CardContent>
                  </Card>
                </Grid>
              ))}
              
              <Grid item xs={12}>
                <TextField
                  label="Reconciliation Notes"
                  fullWidth
                  multiline
                  rows={3}
                  value={cashReconciliation.notes}
                  onChange={(e) => setCashReconciliation({...cashReconciliation, notes: e.target.value})}
                  placeholder="Notes about variances, adjustments, or issues..."
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCashReconciliationDialog(false)}>
            Cancel
          </Button>
          <Button variant="contained" color="primary">
            Complete Reconciliation
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DailyCycleManager;
