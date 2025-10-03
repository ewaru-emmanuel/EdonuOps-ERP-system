import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Alert, Snackbar, LinearProgress, Tooltip, Chip, Avatar, Divider,
  TablePagination, TableSortLabel, InputAdornment, TextField, FormControl, InputLabel, Select, MenuItem, IconButton
} from '@mui/material';
import {
  Assessment, TrendingUp, TrendingDown, CheckCircle, Warning, Error, Info, Refresh, Download, Print, 
  AccountBalance, AttachMoney, Business, Receipt, Payment, ShoppingCart
} from '@mui/icons-material';
import { useCurrency } from '../../../components/GlobalCurrencySettings';
import apiClient from '../../../services/apiClient';

const TrialBalance = () => {
  const { formatCurrency } = useCurrency();
  
  const [trialBalance, setTrialBalance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Table states
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [orderBy, setOrderBy] = useState('account_code');
  const [order, setOrder] = useState('asc');
  const [filters, setFilters] = useState({
    accountType: '',
    minBalance: ''
  });

  // Load trial balance on component mount
  useEffect(() => {
    loadTrialBalance();
  }, []);

  const loadTrialBalance = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/finance/double-entry/trial-balance');
      if (response.trial_balance) {
        setTrialBalance(response);
      } else {
        setError('Failed to load trial balance data');
      }
    } catch (error) {
      console.error('Error loading trial balance:', error);
      setError('Failed to load trial balance');
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleExport = () => {
    if (!trialBalance) return;
    
    // Create CSV content
    const headers = ['Account Code', 'Account Name', 'Account Type', 'Debit Balance', 'Credit Balance', 'Normal Side'];
    const rows = filteredAccounts.map(account => [
      account.account_code,
      account.account_name,
      account.account_type,
      account.debit_balance,
      account.credit_balance,
      account.normal_side
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    
    // Download CSV
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `trial-balance-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    setSnackbar({
      open: true,
      message: 'Trial balance exported successfully',
      severity: 'success'
    });
  };

  const handlePrint = () => {
    window.print();
  };

  // Filter and sort accounts
  const filteredAccounts = React.useMemo(() => {
    if (!trialBalance?.trial_balance) return [];
    
    let filtered = [...trialBalance.trial_balance];
    
    // Apply filters
    if (filters.accountType) {
      filtered = filtered.filter(account => account.account_type === filters.accountType);
    }
    
    if (filters.minBalance) {
      const minBalance = parseFloat(filters.minBalance);
      filtered = filtered.filter(account => 
        account.debit_balance >= minBalance || account.credit_balance >= minBalance
      );
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let aValue = a[orderBy];
      let bValue = b[orderBy];
      
      if (orderBy === 'account_code') {
        aValue = a.account_code;
        bValue = b.account_code;
      }
      
      if (order === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    return filtered;
  }, [trialBalance, filters, orderBy, order]);

  // Pagination
  const paginatedAccounts = filteredAccounts.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const getAccountTypeIcon = (type) => {
    const icons = {
      'asset': <AttachMoney />,
      'liability': <AccountBalance />,
      'equity': <Business />,
      'revenue': <TrendingUp />,
      'expense': <TrendingDown />
    };
    return icons[type] || <Receipt />;
  };

  const getAccountTypeColor = (type) => {
    const colors = {
      'asset': 'success',
      'liability': 'warning',
      'equity': 'info',
      'revenue': 'primary',
      'expense': 'error'
    };
    return colors[type] || 'default';
  };

  if (!trialBalance && !loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">
          No trial balance data available. Please create some journal entries first.
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Trial Balance
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Financial position summary as of {new Date().toLocaleDateString()}
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadTrialBalance}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleExport}
            disabled={!trialBalance}
          >
            Export CSV
          </Button>
          <Button
            variant="outlined"
            startIcon={<Print />}
            onClick={handlePrint}
            disabled={!trialBalance}
          >
            Print
          </Button>
        </Box>
      </Box>

      {/* Summary Cards */}
      {trialBalance && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Total Debits
                    </Typography>
                    <Typography variant="h4" color="success.main">
                      {formatCurrency(trialBalance.total_debits)}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'success.main' }}>
                    <TrendingUp />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Total Credits
                    </Typography>
                    <Typography variant="h4" color="error.main">
                      {formatCurrency(trialBalance.total_credits)}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: 'error.main' }}>
                    <TrendingDown />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Balance Status
                    </Typography>
                    <Typography variant="h6">
                      {trialBalance.is_balanced ? '✅ Balanced' : '❌ Unbalanced'}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: trialBalance.is_balanced ? 'success.main' : 'error.main' }}>
                    {trialBalance.is_balanced ? <CheckCircle /> : <Error />}
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      Difference
                    </Typography>
                    <Typography variant="h6" color={trialBalance.difference > 0 ? 'error.main' : 'success.main'}>
                      {formatCurrency(trialBalance.difference)}
                    </Typography>
                  </Box>
                  <Avatar sx={{ bgcolor: trialBalance.difference > 0 ? 'error.main' : 'success.main' }}>
                    <Assessment />
                  </Avatar>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Balance Status Alert */}
      {trialBalance && !trialBalance.is_balanced && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            ⚠️ Trial Balance is Unbalanced!
          </Typography>
          <Typography variant="body2">
            The total debits (${trialBalance.total_debits.toFixed(2)}) do not equal the total credits (${trialBalance.total_credits.toFixed(2)}).
            The difference is ${trialBalance.difference.toFixed(2)}. Please review your journal entries for errors.
          </Typography>
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Account Type</InputLabel>
                <Select
                  value={filters.accountType}
                  onChange={(e) => setFilters({ ...filters, accountType: e.target.value })}
                >
                  <MenuItem value="">All Types</MenuItem>
                  <MenuItem value="asset">Assets</MenuItem>
                  <MenuItem value="liability">Liabilities</MenuItem>
                  <MenuItem value="equity">Equity</MenuItem>
                  <MenuItem value="revenue">Revenue</MenuItem>
                  <MenuItem value="expense">Expenses</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Min Balance"
                type="number"
                value={filters.minBalance}
                onChange={(e) => setFilters({ ...filters, minBalance: e.target.value })}
                size="small"
                fullWidth
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box display="flex" alignItems="center" height="100%">
                <Typography variant="body2" color="text.secondary">
                  Showing {filteredAccounts.length} accounts
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Trial Balance Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Trial Balance Report
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Generated on {new Date().toLocaleDateString()}
            </Typography>
          </Box>

          {loading && <LinearProgress sx={{ mb: 2 }} />}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'account_code'}
                      direction={orderBy === 'account_code' ? order : 'asc'}
                      onClick={() => handleSort('account_code')}
                    >
                      Account Code
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Account Name</TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'account_type'}
                      direction={orderBy === 'account_type' ? order : 'asc'}
                      onClick={() => handleSort('account_type')}
                    >
                      Type
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="right">
                    <TableSortLabel
                      active={orderBy === 'debit_balance'}
                      direction={orderBy === 'debit_balance' ? order : 'asc'}
                      onClick={() => handleSort('debit_balance')}
                    >
                      Debit Balance
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="right">
                    <TableSortLabel
                      active={orderBy === 'credit_balance'}
                      direction={orderBy === 'credit_balance' ? order : 'asc'}
                      onClick={() => handleSort('credit_balance')}
                    >
                      Credit Balance
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Normal Side</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedAccounts.map((account, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace" fontWeight="medium">
                        {account.account_code}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: `${getAccountTypeColor(account.account_type)}.main` }}>
                          {getAccountTypeIcon(account.account_type)}
                        </Avatar>
                        <Typography variant="body2">
                          {account.account_name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={account.account_type.toUpperCase()}
                        size="small"
                        color={getAccountTypeColor(account.account_type)}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {account.debit_balance > 0 && (
                        <Typography variant="body2" color="success.main" fontWeight="medium">
                          {formatCurrency(account.debit_balance)}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="right">
                      {account.credit_balance > 0 && (
                        <Typography variant="body2" color="error.main" fontWeight="medium">
                          {formatCurrency(account.credit_balance)}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={account.normal_side.toUpperCase()}
                        size="small"
                        color={account.normal_side === 'debit' ? 'success' : 'error'}
                        variant="outlined"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          <TablePagination
            component="div"
            count={filteredAccounts.length}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            rowsPerPageOptions={[10, 25, 50, 100]}
          />
        </CardContent>
      </Card>

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

export default TrialBalance;

