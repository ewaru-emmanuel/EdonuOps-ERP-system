import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Avatar, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Autocomplete, SpeedDial, SpeedDialAction, SpeedDialIcon,
  TablePagination, TableSortLabel, InputAdornment, OutlinedInput, FormHelperText, Collapse, List, ListItem, ListItemText, ListItemIcon
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, LocalTaxi, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { getERPApiService } from '../../../services/erpApiService';
import { useCoA } from '../context/CoAContext';

const SmartGeneralLedger = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState('entry_date');
  const [order, setOrder] = useState('desc');
  const [filters, setFilters] = useState({
    period: 'current',
    account: '',
    status: '',
    amount: ''
  });
  const [editingRow, setEditingRow] = useState(null);
  const [editData, setEditData] = useState({});
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [showAiDialog, setShowAiDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // CRUD Dialog States
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [formData, setFormData] = useState({
    account_id: null,
    entry_date: '',
    description: '',
    debit_amount: '',
    credit_amount: '',
    reference: '',
    status: 'posted'
  });

  // Real-time data hooks
  const { data: generalLedger, loading: glLoading, error: glError, create, update, remove, refresh } = useRealTimeData('/api/finance/general-ledger');

  // Debug: Log general ledger data
  console.log('SmartGeneralLedger - General Ledger data:', generalLedger);
  console.log('SmartGeneralLedger - Loading:', glLoading);
  console.log('SmartGeneralLedger - Error:', glError);
  
  // Chart of Accounts context
  const { accounts: chartOfAccounts, loading: coaLoading } = useCoA();
  
  // Debug log for chart of accounts

  // Calculate real-time trial balance
  const trialBalance = useMemo(() => {
    if (!generalLedger) return { debits: 0, credits: 0, balance: 0 };
    
    const debits = generalLedger.reduce((sum, entry) => sum + (entry.debit_amount || 0), 0);
    const credits = generalLedger.reduce((sum, entry) => sum + (entry.credit_amount || 0), 0);
    const balance = debits - credits;
    
    return { debits, credits, balance };
  }, [generalLedger]);

  // Filter and sort data
  const filteredData = useMemo(() => {
    if (!generalLedger) return [];
    
    let filtered = [...generalLedger];
    
    // Apply filters
    if (filters.period !== 'all') {
      const currentDate = new Date();
      const currentMonth = currentDate.getMonth();
      const currentYear = currentDate.getFullYear();
      
      filtered = filtered.filter(entry => {
        const entryDate = new Date(entry.entry_date);
        return entryDate.getMonth() === currentMonth && entryDate.getFullYear() === currentYear;
      });
    }
    
    if (filters.account) {
      filtered = filtered.filter(entry => 
        entry.account_name?.toLowerCase().includes(filters.account.toLowerCase())
      );
    }
    
    if (filters.status) {
      filtered = filtered.filter(entry => entry.status === filters.status);
    }
    
    if (filters.amount) {
      const amount = parseFloat(filters.amount);
      filtered = filtered.filter(entry => 
        (entry.debit_amount || 0) >= amount || (entry.credit_amount || 0) >= amount
      );
    }
    
    // Sort data
    filtered.sort((a, b) => {
      const aValue = a[orderBy];
      const bValue = b[orderBy];
      
      if (order === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    return filtered;
  }, [generalLedger, filters, orderBy, order]);

  // Pagination
  const paginatedData = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return filteredData.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredData, page, rowsPerPage]);

  // AI Suggestions
  const generateAiSuggestions = useCallback(() => {
    const suggestions = [];
    
    // Analyze patterns and suggest optimizations
    if (trialBalance.balance !== 0) {
      suggestions.push({
        type: 'warning',
        icon: <Warning />,
        title: 'Unbalanced Entries',
        message: `Trial balance shows ${Math.abs(trialBalance.balance).toFixed(2)} difference. Review recent entries.`,
        action: 'Review Entries'
      });
    }
    
    // Suggest common journal entries based on patterns
    const commonAccounts = chartOfAccounts?.slice(0, 5) || [];
    suggestions.push({
      type: 'info',
      icon: <Lightbulb />,
      title: 'Common Entries',
      message: `Based on your patterns, you might want to record: ${commonAccounts.map(acc => acc.name).join(', ')}`,
      action: 'Quick Entry'
    });
    
    setAiSuggestions(suggestions);
  }, [trialBalance, chartOfAccounts]);

  useEffect(() => {
    generateAiSuggestions();
  }, [generateAiSuggestions]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.account_id) {
      setSnackbar({ open: true, message: 'Please select an account', severity: 'error' });
      return;
    }
    
    if (!formData.entry_date) {
      setSnackbar({ open: true, message: 'Please select an entry date', severity: 'error' });
      return;
    }
    
    if (!formData.description) {
      setSnackbar({ open: true, message: 'Please enter a description', severity: 'error' });
      return;
    }
    
    // Validate double-entry bookkeeping
    const debitAmount = parseFloat(formData.debit_amount) || 0;
    const creditAmount = parseFloat(formData.credit_amount) || 0;
    
    if (debitAmount > 0 && creditAmount > 0) {
      setSnackbar({ open: true, message: 'Cannot have both debit and credit amounts', severity: 'error' });
      return;
    }
    
    if (debitAmount === 0 && creditAmount === 0) {
      setSnackbar({ open: true, message: 'Must have either debit or credit amount', severity: 'error' });
      return;
    }
    
    try {
      // Ensure account_id is a number
      const submitData = {
        ...formData,
        account_id: parseInt(formData.account_id) || null
      };
      
      
      if (editDialogOpen && selectedEntry) {
        await update(selectedEntry.id, submitData);
        setSnackbar({ open: true, message: 'Journal entry updated successfully!', severity: 'success' });
      } else {
        await create(submitData);
        setSnackbar({ open: true, message: 'Journal entry created successfully!', severity: 'success' });
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Form submission error:', error); // Debug log
      setSnackbar({ open: true, message: 'Error saving journal entry: ' + error.message, severity: 'error' });
    }
  };

  // Handle edit
  const handleEdit = (entry) => {
    setSelectedEntry(entry);
    setFormData({
      account_id: entry.account_id || null,
      entry_date: entry.entry_date ? entry.entry_date.split('T')[0] : '',
      description: entry.description || '',
      debit_amount: entry.debit_amount || '',
      credit_amount: entry.credit_amount || '',
      reference: entry.reference || '',
      status: entry.status || 'posted'
    });
    setEditDialogOpen(true);
  };

  // Handle delete
  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this journal entry?')) {
      try {
        await remove(id);
        setSnackbar({ open: true, message: 'Journal entry deleted successfully!', severity: 'success' });
      } catch (error) {
        setSnackbar({ open: true, message: 'Error deleting journal entry: ' + error.message, severity: 'error' });
      }
    }
  };

  // Handle dialog close
  const handleCloseDialog = () => {
    setAddDialogOpen(false);
    setEditDialogOpen(false);
    setSelectedEntry(null);
    setFormData({
      account_id: null,
      entry_date: '',
      description: '',
      debit_amount: '',
      credit_amount: '',
      reference: '',
      status: 'posted'
    });
  };

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle inline editing save
  const handleSave = async () => {
    try {
      // Validate double-entry bookkeeping
      if (editData.debit_amount > 0 && editData.credit_amount > 0) {
        setSnackbar({ open: true, message: 'Cannot have both debit and credit amounts', severity: 'error' });
        return;
      }
      
      if (editData.debit_amount === 0 && editData.credit_amount === 0) {
        setSnackbar({ open: true, message: 'Must have either debit or credit amount', severity: 'error' });
        return;
      }
      
      // Update the entry
      await update(editingRow, editData);
      setSnackbar({ open: true, message: 'Journal entry updated successfully', severity: 'success' });
      setEditingRow(null);
      setEditData({});
    } catch (error) {
      setSnackbar({ open: true, message: `Error updating entry: ${error.message}`, severity: 'error' });
    }
  };

  // Handle inline editing cancel
  const handleCancel = () => {
    setEditingRow(null);
    setEditData({});
  };

  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleExport = () => {
    // Export functionality
    const csvContent = "data:text/csv;charset=utf-8," + 
      "Date,Reference,Account,Description,Debit,Credit,Status\n" +
      filteredData.map(row => 
        `${row.entry_date},${row.reference},${row.account_name},${row.description},${row.debit_amount},${row.credit_amount},${row.status}`
      ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "general_ledger.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleAiSuggestion = (suggestion) => {
    setShowAiDialog(false);
  };

  return (
    <Box sx={{ width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
      {/* Header with Smart Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>
          Smart General Ledger
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<AutoAwesome />}
            onClick={() => setShowAiDialog(true)}
          >
            AI Insights
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleExport}
          >
            Export GL
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddDialogOpen(true)}
          >
            Add Entry
          </Button>
        </Box>
      </Box>

      {/* Quick Workflow Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Quick Workflow Actions
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Receipt />}
                onClick={() => {}}
              >
                Record Sale
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Payment />}
                onClick={() => {}}
              >
                Record Purchase
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<AccountBalance />}
                onClick={() => {}}
              >
                Bank Reconciliation
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<LocalTaxi />}
                onClick={() => {}}
              >
                Tax Entry
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Real-time Trial Balance */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Real-time Trial Balance
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary.main" gutterBottom>
                  ${trialBalance.debits.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Debits
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h4" color="secondary.main" gutterBottom>
                  ${trialBalance.credits.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Credits
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h4" color={trialBalance.balance === 0 ? 'success.main' : 'error.main'} gutterBottom>
                  ${Math.abs(trialBalance.balance).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {trialBalance.balance === 0 ? 'Balanced' : 'Difference'}
                </Typography>
                {trialBalance.balance !== 0 && (
                  <Chip 
                    label="Unbalanced" 
                    color="error" 
                    size="small" 
                    sx={{ mt: 1 }}
                  />
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Smart Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Smart Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Period</InputLabel>
                <Select
                  value={filters.period}
                  onChange={(e) => setFilters({ ...filters, period: e.target.value })}
                >
                  <MenuItem value="all">All Periods</MenuItem>
                  <MenuItem value="current">Current Month</MenuItem>
                  <MenuItem value="previous">Previous Month</MenuItem>
                  <MenuItem value="quarter">This Quarter</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Autocomplete
                options={chartOfAccounts || []}
                getOptionLabel={(option) => option.name}
                value={filters.account ? chartOfAccounts?.find(acc => acc.name === filters.account) || null : null}
                onChange={(e, value) => setFilters({ ...filters, account: value?.name || '' })}
                renderInput={(params) => (
                  <TextField {...params} label="Account" size="small" />
                )}
                size="small"
                isOptionEqualToValue={(option, value) => option.id === value?.id}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
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
            <Grid item xs={12} sm={6} md={3}>
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

      {/* General Ledger Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Journal Entries ({filteredData.length} entries)
            </Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => {
                  refresh();
                }}
                disabled={glLoading || coaLoading}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          {glLoading && <LinearProgress sx={{ mb: 2 }} />}

          {glError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {glError}
            </Alert>
          )}

          <TableContainer component={Paper} sx={{ width: '100%', overflowX: 'auto' }}>
            <Table sx={{ minWidth: 900 }} stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'entry_date'}
                      direction={orderBy === 'entry_date' ? order : 'asc'}
                      onClick={() => handleSort('entry_date')}
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
                  <TableCell>Account</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">
                    <TableSortLabel
                      active={orderBy === 'debit_amount'}
                      direction={orderBy === 'debit_amount' ? order : 'asc'}
                      onClick={() => handleSort('debit_amount')}
                    >
                      Debit
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="right">
                    <TableSortLabel
                      active={orderBy === 'credit_amount'}
                      direction={orderBy === 'credit_amount' ? order : 'asc'}
                      onClick={() => handleSort('credit_amount')}
                    >
                      Credit
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedData.map((entry, index) => (
                  <TableRow key={entry.id || `entry-${index}`} hover>
                    <TableCell>
                      {entry.entry_date ? new Date(entry.entry_date).toLocaleDateString() : ''}
                    </TableCell>
                    <TableCell>
                      {editingRow === entry.id ? (
                        <TextField
                          value={editData.reference}
                          onChange={(e) => setEditData({ ...editData, reference: e.target.value })}
                          size="small"
                          fullWidth
                        />
                      ) : (
                        entry.reference || ''
                      )}
                    </TableCell>
                    <TableCell>
                      {editingRow === entry.id ? (
                        <Autocomplete
                          options={chartOfAccounts || []}
                          getOptionLabel={(option) => option.name}
                          value={chartOfAccounts?.find(acc => acc.id === editData.account_id) || null}
                          onChange={(e, value) => setEditData({ ...editData, account_id: value?.id || null })}
                          renderInput={(params) => (
                            <TextField {...params} size="small" />
                          )}
                          size="small"
                          isOptionEqualToValue={(option, value) => option.id === value?.id}
                        />
                      ) : (
                        entry.account_name || ''
                      )}
                    </TableCell>
                    <TableCell>
                      {editingRow === entry.id ? (
                        <TextField
                          value={editData.description}
                          onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                          size="small"
                          fullWidth
                        />
                      ) : (
                        entry.description || ''
                      )}
                    </TableCell>
                    <TableCell align="right">
                      {editingRow === entry.id ? (
                        <TextField
                          type="number"
                          value={editData.debit_amount}
                          onChange={(e) => setEditData({ ...editData, debit_amount: parseFloat(e.target.value) || 0 })}
                          size="small"
                          InputProps={{
                            startAdornment: <InputAdornment position="start">$</InputAdornment>,
                          }}
                        />
                      ) : (
                        `$${entry.debit_amount || 0}`
                      )}
                    </TableCell>
                    <TableCell align="right">
                      {editingRow === entry.id ? (
                        <TextField
                          type="number"
                          value={editData.credit_amount}
                          onChange={(e) => setEditData({ ...editData, credit_amount: parseFloat(e.target.value) || 0 })}
                          size="small"
                          InputProps={{
                            startAdornment: <InputAdornment position="start">$</InputAdornment>,
                          }}
                        />
                      ) : (
                        `$${entry.credit_amount || 0}`
                      )}
                    </TableCell>
                    <TableCell>
                      {editingRow === entry.id ? (
                        <FormControl size="small" fullWidth>
                          <Select
                            value={editData.status}
                            onChange={(e) => setEditData({ ...editData, status: e.target.value })}
                          >
                            <MenuItem value="draft">Draft</MenuItem>
                            <MenuItem value="posted">Posted</MenuItem>
                            <MenuItem value="void">Void</MenuItem>
                          </Select>
                        </FormControl>
                      ) : (
                        <Chip
                          label={entry.status || 'draft'}
                          color={entry.status === 'posted' ? 'success' : entry.status === 'void' ? 'error' : 'warning'}
                          size="small"
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      {editingRow === entry.id ? (
                        <Box display="flex" gap={1}>
                          <Tooltip title="Save">
                            <IconButton onClick={handleSave} color="success" size="small">
                              <Save />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Cancel">
                            <IconButton onClick={handleCancel} color="error" size="small">
                              <Cancel />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      ) : (
                        <Box display="flex" gap={1}>
                          <Tooltip title="View Details">
                            <IconButton size="small">
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton onClick={() => handleEdit(entry)} size="small">
                              <Edit />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton color="error" size="small" onClick={() => handleDelete(entry.id)}>
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          <TablePagination
            component="div"
            count={filteredData.length}
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

      {/* AI Insights Dialog */}
      <Dialog
        open={showAiDialog}
        onClose={() => setShowAiDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <Psychology />
            </Avatar>
            <Typography variant="h6">AI-Powered Insights</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Intelligent analysis of your General Ledger patterns:
          </Typography>
          
          <List>
            {aiSuggestions.map((suggestion, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {suggestion.icon}
                </ListItemIcon>
                <ListItemText
                  primary={suggestion.title}
                  secondary={suggestion.message}
                  primaryTypographyProps={{ fontWeight: 'bold' }}
                />
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => handleAiSuggestion(suggestion)}
                >
                  {suggestion.action}
                </Button>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAiDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Add/Edit Journal Entry Dialog */}
      <Dialog 
        open={addDialogOpen || editDialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editDialogOpen ? 'Edit Journal Entry' : 'Add New Journal Entry'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Account</InputLabel>
                  <Select
                    value={formData.account_id || ''}
                    onChange={(e) => handleInputChange('account_id', e.target.value || null)}
                    label="Account"
                    required
                  >
                    {chartOfAccounts?.map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Entry Date"
                  type="date"
                  value={formData.entry_date}
                  onChange={(e) => handleInputChange('entry_date', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  fullWidth
                  margin="normal"
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Reference"
                  value={formData.reference}
                  onChange={(e) => handleInputChange('reference', e.target.value)}
                  fullWidth
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    onChange={(e) => handleInputChange('status', e.target.value)}
                    label="Status"
                  >
                    <MenuItem value="draft">Draft</MenuItem>
                    <MenuItem value="posted">Posted</MenuItem>
                    <MenuItem value="void">Void</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Debit Amount"
                  type="number"
                  value={formData.debit_amount}
                  onChange={(e) => handleInputChange('debit_amount', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Credit Amount"
                  type="number"
                  value={formData.credit_amount}
                  onChange={(e) => handleInputChange('credit_amount', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            {editDialogOpen ? 'Update' : 'Create'} Entry
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

      {/* Floating Action Button */}
      <SpeedDial
        ariaLabel="General Ledger Actions"
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
          onClick={() => setAddDialogOpen(true)}
        />
        <SpeedDialAction
          icon={<AutoAwesome />}
          tooltipTitle="AI Insights"
          onClick={() => setShowAiDialog(true)}
        />
        <SpeedDialAction
          icon={<Download />}
          tooltipTitle="Export"
          onClick={handleExport}
        />
      </SpeedDial>
    </Box>
  );
};

export default SmartGeneralLedger;
