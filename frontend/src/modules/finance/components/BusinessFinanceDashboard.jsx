import React, { useState, useEffect, useMemo } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Avatar, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  SpeedDial, SpeedDialAction, SpeedDialIcon, TablePagination, TableSortLabel, InputAdornment, TextField, FormControl, InputLabel, Select, MenuItem, Divider
} from '@mui/material';
import {
  Add, AttachMoney, AccountBalance, Receipt, Payment, Business, ShoppingCart, 
  TrendingUp, TrendingDown, CheckCircle, Warning, Error, Info, Refresh, Visibility, Edit, Delete,
  Assessment, BarChart, PieChart, ShowChart, Timeline, CurrencyExchange, Audit, Compliance
} from '@mui/icons-material';
import { useCurrency } from '../../../components/GlobalCurrencySettings';
import apiClient from '../../../services/apiClient';
import BusinessTransactionForm from './BusinessTransactionForm';

const BusinessFinanceDashboard = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const { formatCurrency } = useCurrency();
  
  // State management
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Dialog states
  const [transactionFormOpen, setTransactionFormOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  
  // Table states
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState('date');
  const [order, setOrder] = useState('desc');
  const [filters, setFilters] = useState({
    template: '',
    status: '',
    amount: ''
  });

  // Load transactions on component mount
  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get('/api/finance/double-entry/journal-entries');
      if (Array.isArray(response)) {
        setTransactions(response);
      } else {
        setTransactions([]);
      }
    } catch (error) {
      console.error('Error loading transactions:', error);
      setError('Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  const handleTransactionSuccess = (newTransaction) => {
    setSnackbar({
      open: true,
      message: 'Transaction created successfully!',
      severity: 'success'
    });
    loadTransactions(); // Refresh the list
  };

  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleDelete = async (transactionId) => {
    if (window.confirm('Are you sure you want to delete this transaction?')) {
      try {
        await apiClient.delete(`/api/finance/journal-entries/${transactionId}`);
        setSnackbar({
          open: true,
          message: 'Transaction deleted successfully',
          severity: 'success'
        });
        loadTransactions();
      } catch (error) {
        console.error('Error deleting transaction:', error);
        setSnackbar({
          open: true,
          message: 'Failed to delete transaction',
          severity: 'error'
        });
      }
    }
  };

  // Filter and sort transactions
  const filteredTransactions = useMemo(() => {
    let filtered = [...transactions];

    // Apply filters
    if (filters.template) {
      filtered = filtered.filter(t => 
        t.description.toLowerCase().includes(filters.template.toLowerCase())
      );
    }
    
    if (filters.status) {
      filtered = filtered.filter(t => t.status === filters.status);
    }
    
    if (filters.amount) {
      const minAmount = parseFloat(filters.amount);
      filtered = filtered.filter(t => t.total_debits >= minAmount);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue = a[orderBy];
      let bValue = b[orderBy];
      
      if (orderBy === 'date') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      }
      
      if (order === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [transactions, filters, orderBy, order]);

  // Pagination
  const paginatedTransactions = filteredTransactions.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // Calculate summary metrics
  const summaryMetrics = useMemo(() => {
    const totalTransactions = transactions.length;
    const totalAmount = transactions.reduce((sum, t) => sum + t.total_debits, 0);
    const cashTransactions = transactions.filter(t => t.payment_method === 'cash').length;
    const bankTransactions = transactions.filter(t => t.payment_method === 'bank').length;
    
    return {
      totalTransactions,
      totalAmount,
      cashTransactions,
      bankTransactions
    };
  }, [transactions]);

  const getTransactionIcon = (description) => {
    if (description.toLowerCase().includes('cash sales')) return <AttachMoney />;
    if (description.toLowerCase().includes('bank sales')) return <AccountBalance />;
    if (description.toLowerCase().includes('expense')) return <Payment />;
    if (description.toLowerCase().includes('purchase')) return <ShoppingCart />;
    if (description.toLowerCase().includes('loan')) return <Business />;
    return <Receipt />;
  };

  const getTransactionColor = (description) => {
    if (description.toLowerCase().includes('sales')) return 'success';
    if (description.toLowerCase().includes('expense')) return 'warning';
    if (description.toLowerCase().includes('purchase')) return 'info';
    if (description.toLowerCase().includes('loan')) return 'secondary';
    return 'default';
  };

  const speedDialActions = [
    {
      icon: <AttachMoney />,
      name: 'Cash Sale',
      onClick: () => setTransactionFormOpen(true)
    },
    {
      icon: <AccountBalance />,
      name: 'Bank Sale',
      onClick: () => setTransactionFormOpen(true)
    },
    {
      icon: <Payment />,
      name: 'Expense Payment',
      onClick: () => setTransactionFormOpen(true)
    },
    {
      icon: <ShoppingCart />,
      name: 'Purchase',
      onClick: () => setTransactionFormOpen(true)
    },
    {
      icon: <Business />,
      name: 'Loan Receipt',
      onClick: () => setTransactionFormOpen(true)
    }
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Business Finance Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage your business transactions with ease
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setTransactionFormOpen(true)}
          size="large"
        >
          Record Transaction
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total Transactions
                  </Typography>
                  <Typography variant="h4">
                    {summaryMetrics.totalTransactions}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <Receipt />
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
                    Total Amount
                  </Typography>
                  <Typography variant="h4">
                    {formatCurrency(summaryMetrics.totalAmount)}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <AttachMoney />
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
                    Cash Transactions
                  </Typography>
                  <Typography variant="h4">
                    {summaryMetrics.cashTransactions}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <AttachMoney />
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
                    Bank Transactions
                  </Typography>
                  <Typography variant="h4">
                    {summaryMetrics.bankTransactions}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <AccountBalance />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Search Transactions"
                value={filters.template}
                onChange={(e) => setFilters({ ...filters, template: e.target.value })}
                fullWidth
                size="small"
                InputProps={{
                  startAdornment: <InputAdornment position="start">🔍</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="posted">Posted</MenuItem>
                  <MenuItem value="void">Void</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Min Amount"
                type="number"
                value={filters.amount}
                onChange={(e) => setFilters({ ...filters, amount: e.target.value })}
                size="small"
                fullWidth
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Transactions Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Recent Transactions ({filteredTransactions.length} entries)
            </Typography>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadTransactions}
              disabled={loading}
            >
              Refresh
            </Button>
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
                      active={orderBy === 'date'}
                      direction={orderBy === 'date' ? order : 'asc'}
                      onClick={() => handleSort('date')}
                    >
                      Date
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'reference'}
                      direction={orderBy === 'reference' ? order : 'asc'}
                      onClick={() => handleSort('reference')}
                    >
                      Reference
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Transaction</TableCell>
                  <TableCell>Payment Method</TableCell>
                  <TableCell align="right">
                    <TableSortLabel
                      active={orderBy === 'total_debits'}
                      direction={orderBy === 'total_debits' ? order : 'asc'}
                      onClick={() => handleSort('total_debits')}
                    >
                      Amount
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedTransactions.map((transaction) => (
                  <TableRow key={transaction.id} hover>
                    <TableCell>
                      {new Date(transaction.date).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {transaction.reference}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: `${getTransactionColor(transaction.description)}.main` }}>
                          {getTransactionIcon(transaction.description)}
                        </Avatar>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {transaction.description}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {transaction.lines?.length || 0} journal lines
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={transaction.payment_method}
                        size="small"
                        color={transaction.payment_method === 'cash' ? 'success' : 'primary'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="medium">
                        {formatCurrency(transaction.total_debits)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={transaction.status}
                        size="small"
                        color={transaction.status === 'posted' ? 'success' : 'warning'}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Tooltip title="View Details">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit">
                          <IconButton size="small">
                            <Edit />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => handleDelete(transaction.id)}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          <TablePagination
            component="div"
            count={filteredTransactions.length}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </CardContent>
      </Card>

      {/* Speed Dial for Quick Actions */}
      <SpeedDial
        ariaLabel="Quick transaction actions"
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
        icon={<SpeedDialIcon />}
      >
        {speedDialActions.map((action) => (
          <SpeedDialAction
            key={action.name}
            icon={action.icon}
            tooltipTitle={action.name}
            onClick={action.onClick}
          />
        ))}
      </SpeedDial>

      {/* Transaction Form Dialog */}
      <BusinessTransactionForm
        open={transactionFormOpen}
        onClose={() => setTransactionFormOpen(false)}
        onSuccess={handleTransactionSuccess}
      />

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

export default BusinessFinanceDashboard;

