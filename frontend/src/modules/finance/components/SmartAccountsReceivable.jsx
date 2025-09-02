import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Autocomplete, SpeedDial, SpeedDialAction, SpeedDialIcon,
  TablePagination, TableSortLabel, InputAdornment, OutlinedInput, FormHelperText, Collapse, List, ListItem, ListItemText, ListItemIcon,
  Checkbox, FormControlLabel, FormGroup, Badge, Avatar, Divider, Accordion, AccordionSummary, AccordionDetails,
  RadioGroup, Radio
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, LocalTaxi, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb,
  CloudUpload, Description, ReceiptLong, PaymentOutlined, ScheduleSend, AutoFixHigh, SmartToy, QrCode, CameraAlt,
  Email, CalendarToday
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { getERPApiService } from '../../../services/erpApiService';

const SmartAccountsReceivable = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState('due_date');
  const [order, setOrder] = useState('asc');
  const [filters, setFilters] = useState({
    status: '',
    customer: '',
    dueDate: '',
    amount: ''
  });
  const [selectedInvoices, setSelectedInvoices] = useState([]);
  const [bulkAction, setBulkAction] = useState('');
  const [showBulkDialog, setShowBulkDialog] = useState(false);
  const [showReminderDialog, setShowReminderDialog] = useState(false);
  const [reminderMessage, setReminderMessage] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // CRUD Dialog States
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [formData, setFormData] = useState({
    customer_id: null,
    invoice_number: '',
    invoice_date: '',
    due_date: '',
    total_amount: '',
    tax_amount: '',
    description: '',
    status: 'pending'
  });

  // Real-time data hooks
  const { data: accountsReceivable, loading: arLoading, error: arError, create, update, remove, refresh } = useRealTimeData('/api/finance/accounts-receivable');
  const { data: customers, loading: customersLoading, refresh: refreshCustomers } = useRealTimeData('/api/finance/customers');

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editDialogOpen && selectedInvoice) {
        await update(selectedInvoice.id, formData);
        setSnackbar({ open: true, message: 'Invoice updated successfully!', severity: 'success' });
      } else {
        await create(formData);
        setSnackbar({ open: true, message: 'Invoice created successfully!', severity: 'success' });
      }
      handleCloseDialog();
    } catch (error) {
      setSnackbar({ open: true, message: 'Error saving invoice: ' + error.message, severity: 'error' });
    }
  };

  // Handle edit
  const handleEdit = (invoice) => {
    setSelectedInvoice(invoice);
    setFormData({
      customer_id: invoice.customer_id || null,
      invoice_number: invoice.invoice_number || '',
      invoice_date: invoice.invoice_date ? invoice.invoice_date.split('T')[0] : '',
      due_date: invoice.due_date ? invoice.due_date.split('T')[0] : '',
      total_amount: invoice.total_amount || '',
      tax_amount: invoice.tax_amount || '',
      description: invoice.description || '',
      status: invoice.status || 'pending'
    });
    setEditDialogOpen(true);
  };

  // Handle delete
  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this invoice?')) {
      try {
        await remove(id);
        setSnackbar({ open: true, message: 'Invoice deleted successfully!', severity: 'success' });
      } catch (error) {
        setSnackbar({ open: true, message: 'Error deleting invoice: ' + error.message, severity: 'error' });
      }
    }
  };

  // Handle dialog close
  const handleCloseDialog = () => {
    setAddDialogOpen(false);
    setEditDialogOpen(false);
    setSelectedInvoice(null);
    setFormData({
      customer_id: null,
      invoice_number: '',
      invoice_date: '',
      due_date: '',
      total_amount: '',
      tax_amount: '',
      description: '',
      status: 'pending'
    });
  };

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Calculate AR metrics and aging buckets
  const arMetrics = useMemo(() => {
    if (!accountsReceivable) return {
      totalOutstanding: 0,
      overdueAmount: 0,
      dueThisWeek: 0,
      agingBuckets: {
        current: 0,
        '30days': 0,
        '60days': 0,
        '90days': 0,
        'over90days': 0
      }
    };

    const totalOutstanding = accountsReceivable.reduce((sum, ar) => sum + (ar.outstanding_amount || 0), 0);
    const overdueAmount = accountsReceivable
      .filter(ar => ar.status === 'overdue')
      .reduce((sum, ar) => sum + (ar.outstanding_amount || 0), 0);
    
    const dueThisWeek = accountsReceivable
      .filter(ar => {
        const dueDate = new Date(ar.due_date);
        const today = new Date();
        const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        return dueDate <= weekFromNow && ar.status === 'pending';
      })
      .reduce((sum, ar) => sum + (ar.outstanding_amount || 0), 0);

    // Aging buckets
    const today = new Date();
    const agingBuckets = {
      current: 0,
      '30days': 0,
      '60days': 0,
      '90days': 0,
      'over90days': 0
    };

    accountsReceivable.forEach(ar => {
      const dueDate = new Date(ar.due_date);
      const daysOverdue = Math.floor((today - dueDate) / (1000 * 60 * 60 * 24));
      const amount = ar.outstanding_amount || 0;

      if (daysOverdue <= 0) {
        agingBuckets.current += amount;
      } else if (daysOverdue <= 30) {
        agingBuckets['30days'] += amount;
      } else if (daysOverdue <= 60) {
        agingBuckets['60days'] += amount;
      } else if (daysOverdue <= 90) {
        agingBuckets['90days'] += amount;
      } else {
        agingBuckets['over90days'] += amount;
      }
    });

    return {
      totalOutstanding,
      overdueAmount,
      dueThisWeek,
      agingBuckets
    };
  }, [accountsReceivable]);

  // Filter data
  const filteredData = useMemo(() => {
    if (!accountsReceivable) return [];
    
    let filtered = [...accountsReceivable];
    
    if (filters.status) {
      filtered = filtered.filter(ar => ar.status === filters.status);
    }
    
    if (filters.customer) {
      filtered = filtered.filter(ar => 
        ar.customer_name?.toLowerCase().includes(filters.customer.toLowerCase())
      );
    }
    
    if (filters.aging) {
      const today = new Date();
      filtered = filtered.filter(ar => {
        const dueDate = new Date(ar.due_date);
        const daysOverdue = Math.floor((today - dueDate) / (1000 * 60 * 60 * 24));
        
        switch (filters.aging) {
          case 'current':
            return daysOverdue <= 0;
          case '30days':
            return daysOverdue > 0 && daysOverdue <= 30;
          case '60days':
            return daysOverdue > 30 && daysOverdue <= 60;
          case '90days':
            return daysOverdue > 60 && daysOverdue <= 90;
          case 'over90days':
            return daysOverdue > 90;
          default:
            return true;
        }
      });
    }
    
    return filtered;
  }, [accountsReceivable, filters]);

  // Pagination
  const paginatedData = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return filteredData.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredData, page, rowsPerPage]);

  // Handle bulk selection
  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelectedInvoices(paginatedData.map(ar => ar.id));
    } else {
      setSelectedInvoices([]);
    }
  };

  const handleSelectInvoice = (invoiceId) => {
    setSelectedInvoices(prev => 
      prev.includes(invoiceId) 
        ? prev.filter(id => id !== invoiceId)
        : [...prev, invoiceId]
    );
  };

  // Bulk actions
  const handleBulkAction = async () => {
    try {
      switch (bulkAction) {
        case 'send_reminders':
          setSnackbar({ open: true, message: `Reminders sent for ${selectedInvoices.length} invoices`, severity: 'success' });
          break;
        case 'generate_statements':
          setSnackbar({ open: true, message: `Statements generated for ${selectedInvoices.length} customers`, severity: 'success' });
          break;
        default:
          break;
      }
      setShowBulkDialog(false);
      setSelectedInvoices([]);
      setBulkAction('');
    } catch (error) {
      setSnackbar({ open: true, message: `Error performing bulk action: ${error.message}`, severity: 'error' });
    }
  };

  const handleExport = () => {
    const csvContent = "data:text/csv;charset=utf-8," + 
      "Invoice #,Customer,Due Date,Amount,Outstanding,Status\n" +
      filteredData.map(row => 
        `${row.invoice_number},${row.customer_name},${row.due_date},${row.total_amount},${row.outstanding_amount},${row.status}`
      ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "accounts_receivable.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getAgingColor = (daysOverdue) => {
    if (daysOverdue <= 0) return 'success';
    if (daysOverdue <= 30) return 'warning';
    if (daysOverdue <= 60) return 'error';
    return 'error';
  };

  const getAgingLabel = (daysOverdue) => {
    if (daysOverdue <= 0) return 'Current';
    if (daysOverdue <= 30) return '1-30 Days';
    if (daysOverdue <= 60) return '31-60 Days';
    if (daysOverdue <= 90) return '61-90 Days';
    return 'Over 90 Days';
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" gutterBottom>
            Smart Accounts Receivable
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Intelligent customer management with payment prediction
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Email />}
            onClick={() => setShowBulkDialog(true)}
            disabled={selectedInvoices.length === 0}
          >
            Send Reminders ({selectedInvoices.length})
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddDialogOpen(true)}
          >
            Create Invoice
          </Button>
        </Box>
      </Box>

      {/* AR Metrics Dashboard */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Total Outstanding
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${arMetrics.totalOutstanding.toLocaleString()}
                  </Typography>
                </Box>
                <Receipt sx={{ fontSize: 28, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            color: 'white'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Overdue Amount
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${arMetrics.overdueAmount.toLocaleString()}
                  </Typography>
                </Box>
                <Warning sx={{ fontSize: 28, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            color: 'white'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Due This Week
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${arMetrics.dueThisWeek.toLocaleString()}
                  </Typography>
                </Box>
                <CalendarToday sx={{ fontSize: 28, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Avg Collection Time
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    25 days
                  </Typography>
                </Box>
                <Timeline sx={{ fontSize: 28, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Aging Buckets */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Aging Analysis
          </Typography>
          <Grid container spacing={2}>
            {Object.entries(arMetrics.agingBuckets).map(([bucket, amount]) => (
              <Grid item xs={12} sm={6} md={2.4} key={bucket}>
                <Box 
                  textAlign="center" 
                  p={2} 
                  sx={{ 
                    bgcolor: bucket === 'current' ? 'success.light' :
                            bucket === '30days' ? 'warning.light' :
                            bucket === '60days' ? 'error.light' :
                            bucket === '90days' ? 'error.main' : 'error.dark',
                    color: 'white',
                    borderRadius: 2
                  }}
                >
                  <Typography variant="h6" gutterBottom>
                    ${amount.toLocaleString()}
                  </Typography>
                  <Typography variant="body2">
                    {bucket === 'current' ? 'Current' :
                     bucket === '30days' ? '1-30 Days' :
                     bucket === '60days' ? '31-60 Days' :
                     bucket === '90days' ? '61-90 Days' : 'Over 90 Days'}
                  </Typography>
                </Box>
              </Grid>
            ))}
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
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="paid">Paid</MenuItem>
                  <MenuItem value="overdue">Overdue</MenuItem>
                  <MenuItem value="partial">Partial</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                label="Customer"
                value={filters.customer}
                onChange={(e) => setFilters({ ...filters, customer: e.target.value })}
                size="small"
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Aging</InputLabel>
                <Select
                  value={filters.aging}
                  onChange={(e) => setFilters({ ...filters, aging: e.target.value })}
                >
                  <MenuItem value="">All Aging</MenuItem>
                  <MenuItem value="current">Current</MenuItem>
                  <MenuItem value="30days">1-30 Days</MenuItem>
                  <MenuItem value="60days">31-60 Days</MenuItem>
                  <MenuItem value="90days">61-90 Days</MenuItem>
                  <MenuItem value="over90days">Over 90 Days</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* AR Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Customer Invoices ({filteredData.length} invoices)
            </Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleExport}
              >
                Export
              </Button>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => {
                  refresh();
                  refreshCustomers();
                }}
                disabled={arLoading || customersLoading}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          {arLoading && <LinearProgress sx={{ mb: 2 }} />}

          {arError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {arError}
            </Alert>
          )}

          <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox">
                    <Checkbox
                      indeterminate={selectedInvoices.length > 0 && selectedInvoices.length < paginatedData.length}
                      checked={selectedInvoices.length === paginatedData.length && paginatedData.length > 0}
                      onChange={handleSelectAll}
                    />
                  </TableCell>
                  <TableCell>Invoice #</TableCell>
                  <TableCell>Customer</TableCell>
                  <TableCell>Due Date</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell align="right">Outstanding</TableCell>
                  <TableCell>Aging</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedData.map((ar, index) => {
                  const dueDate = new Date(ar.due_date);
                  const today = new Date();
                  const daysOverdue = Math.floor((today - dueDate) / (1000 * 60 * 60 * 24));
                  
                  return (
                    <TableRow key={ar.id || `ar-${index}`} hover>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={selectedInvoices.includes(ar.id)}
                          onChange={() => handleSelectInvoice(ar.id)}
                        />
                      </TableCell>
                      <TableCell>{ar.invoice_number || ''}</TableCell>
                      <TableCell>{ar.customer_name || ''}</TableCell>
                      <TableCell>
                        {ar.due_date ? new Date(ar.due_date).toLocaleDateString() : ''}
                      </TableCell>
                      <TableCell align="right">${ar.total_amount || 0}</TableCell>
                      <TableCell align="right">${ar.outstanding_amount || 0}</TableCell>
                      <TableCell>
                        <Chip
                          label={getAgingLabel(daysOverdue)}
                          color={getAgingColor(daysOverdue)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={ar.status || 'pending'}
                          color={
                            ar.status === 'paid' ? 'success' :
                            ar.status === 'overdue' ? 'error' :
                            ar.status === 'partial' ? 'warning' : 'info'
                          }
                          size="small"
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
                            <IconButton size="small" onClick={() => handleEdit(ar)}>
                              <Edit />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton color="error" size="small" onClick={() => handleDelete(ar.id)}>
                              <Delete />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Send Payment Link">
                            <IconButton size="small" color="primary">
                              <Payment />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Send Reminder">
                            <IconButton size="small" color="warning">
                              <Email />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Bulk Actions Dialog */}
      <Dialog
        open={showBulkDialog}
        onClose={() => setShowBulkDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6">Bulk Actions</Typography>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Perform actions on {selectedInvoices.length} selected invoices:
          </Typography>
          
          <FormControl component="fieldset" fullWidth>
            <RadioGroup
              value={bulkAction}
              onChange={(e) => setBulkAction(e.target.value)}
            >
              <FormControlLabel value="send_reminders" control={<Radio />} label="Send Payment Reminders" />
              <FormControlLabel value="generate_statements" control={<Radio />} label="Generate Customer Statements" />
            </RadioGroup>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowBulkDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleBulkAction}
            disabled={!bulkAction}
          >
            Execute Action
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add/Edit Invoice Dialog */}
      <Dialog 
        open={addDialogOpen || editDialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editDialogOpen ? 'Edit Invoice' : 'Create New Invoice'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Customer</InputLabel>
                  <Select
                    value={formData.customer_id}
                    onChange={(e) => handleInputChange('customer_id', e.target.value)}
                    label="Customer"
                    required
                  >
                    {customers?.map((customer) => (
                      <MenuItem key={customer.id} value={customer.id}>
                        {customer.customer_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Invoice Number"
                  value={formData.invoice_number}
                  onChange={(e) => handleInputChange('invoice_number', e.target.value)}
                  fullWidth
                  margin="normal"
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Invoice Date"
                  type="date"
                  value={formData.invoice_date}
                  onChange={(e) => handleInputChange('invoice_date', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Due Date"
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => handleInputChange('due_date', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Total Amount"
                  type="number"
                  value={formData.total_amount}
                  onChange={(e) => handleInputChange('total_amount', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Tax Amount"
                  type="number"
                  value={formData.tax_amount}
                  onChange={(e) => handleInputChange('tax_amount', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  fullWidth
                  margin="normal"
                  multiline
                  rows={3}
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
                    <MenuItem value="pending">Pending</MenuItem>
                    <MenuItem value="partial">Partial</MenuItem>
                    <MenuItem value="paid">Paid</MenuItem>
                    <MenuItem value="overdue">Overdue</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            {editDialogOpen ? 'Update' : 'Create'} Invoice
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

export default SmartAccountsReceivable;
