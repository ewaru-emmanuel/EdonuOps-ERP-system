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
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb,
  CloudUpload, Description, ReceiptLong, PaymentOutlined, ScheduleSend, AutoFixHigh, SmartToy, QrCode, CameraAlt,
  Email, CalendarToday, PersonAdd
} from '@mui/icons-material';
import { useFinanceData } from '../hooks/useFinanceData';
import PermissionGuard, { PermissionButton } from '../../../components/PermissionGuard';

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
  
  // Payment tracking UI state
  const [showPaymentFields, setShowPaymentFields] = useState(false);
  const [partialPaymentDialogOpen, setPartialPaymentDialogOpen] = useState(false);
  const [exchangeRateLoading, setExchangeRateLoading] = useState(false);
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
    status: 'pending',
    // Multi-currency fields
    currency: 'USD',
    exchange_rate: 1.0,
    base_amount: '',
    // Payment tracking fields
    payment_method_id: '',
    bank_account_id: '',
    payment_reference: '',
    payment_date: '',
    processing_fee: '',
    payment_notes: ''
  });

  // Customer creation dialog states
  const [addCustomerDialogOpen, setAddCustomerDialogOpen] = useState(false);
  const [customerFormData, setCustomerFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    company_name: '',
    tax_id: '',
    credit_limit: '',
    payment_terms: 'Net 30',
    customer_type: 'regular',
    category: '',
    region: ''
  });

  // Real-time data hooks - fetch from database
  const { data: accountsReceivable = [], loading: arLoading, error: arError, refresh: refreshAR } = useFinanceData('accounts-receivable');
  
  // Real CRUD operations using API
  const update = async (id, invoiceData) => {
    try {
      const apiClient = (await import('../../../services/apiClient')).default;
      const response = await apiClient.put(`/finance/accounts-receivable/${id}`, invoiceData);
      console.log('✅ AR Invoice updated:', response);
      await refreshAR(); // Refresh the list
      return response;
    } catch (error) {
      console.error('❌ Error updating AR invoice:', error);
      throw error;
    }
  };
  
  // Mock operations for create/delete (will be implemented later)
  const create = async (data) => { console.log('Mock create AR:', data); return { id: Date.now(), ...data }; };
  const remove = async (id) => { console.log('Mock delete AR:', id); return true; };
  const refresh = refreshAR;
  
  const customersResponse = [];
  const customersLoading = false;
  const refreshCustomers = () => { console.log('Mock refresh customers'); };
  
  const paymentMethods = [];
  const paymentMethodsLoading = false;
  
  const bankAccounts = [];
  const bankAccountsLoading = false;
  
  const supportedCurrencies = [];
  const currenciesLoading = false;
  
  const partialPayments = [];
  const partialPaymentsLoading = false;
  const createPartialPayment = async (data) => { console.log('Mock create partial payment:', data); return { id: Date.now(), ...data }; };
  
  // Extract customers array from response - backend returns direct array
  const customers = Array.isArray(customersResponse) ? customersResponse : (customersResponse?.customers || []);

  // Show payment fields when status is 'paid'
  useEffect(() => {
    setShowPaymentFields(formData.status === 'paid');
  }, [formData.status]);

  // Fetch exchange rate when currency changes
  const fetchExchangeRate = useCallback(async (fromCurrency, toCurrency = 'USD') => {
    if (fromCurrency === toCurrency) {
      setFormData(prev => ({ ...prev, exchange_rate: 1.0 }));
      return;
    }

    setExchangeRateLoading(true);
    try {
      // Mock exchange rate - no API call
      console.log('Mock get exchange rate:', fromCurrency, toCurrency);
      const response = { rate: 1.0 };
      if (response && response.rate) {
        setFormData(prev => ({ ...prev, exchange_rate: response.rate }));
      }
    } catch (error) {
      console.warn('Could not fetch exchange rate:', error);
      // Keep current rate or default to 1.0
      if (!formData.exchange_rate || formData.exchange_rate === 0) {
        setFormData(prev => ({ ...prev, exchange_rate: 1.0 }));
      }
    } finally {
      setExchangeRateLoading(false);
    }
  }, [formData.exchange_rate]);

  // Update exchange rate when currency changes
  useEffect(() => {
    if (formData.currency && formData.currency !== 'USD') {
      fetchExchangeRate(formData.currency, 'USD');
    }
  }, [formData.currency, fetchExchangeRate]);

  // Calculate processing fee when payment method or amount changes
  const calculateProcessingFee = useCallback(async () => {
    if (formData.payment_method_id && formData.total_amount && showPaymentFields) {
      try {
        // Mock processing fee calculation - no API call
        console.log('Mock calculate processing fees:', {
          amount: parseFloat(formData.total_amount),
          payment_method_id: parseInt(formData.payment_method_id)
        });
        
        // Mock response
        const response = { processing_fee: 0 };
        
        if (response && response.processing_fee !== undefined) {
          setFormData(prev => ({
            ...prev,
            processing_fee: response.processing_fee.toString()
          }));
        }
      } catch (error) {
        console.warn('Could not calculate processing fee:', error);
      }
    }
  }, [formData.payment_method_id, formData.total_amount, showPaymentFields]);

  // Auto-calculate processing fee when payment method or amount changes
  useEffect(() => {
    calculateProcessingFee();
  }, [calculateProcessingFee]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Validate required fields
      if (!formData.customer_id) {
        setSnackbar({ open: true, message: 'Customer is required', severity: 'error' });
        return;
      }
      if (!formData.invoice_number) {
        setSnackbar({ open: true, message: 'Invoice number is required', severity: 'error' });
        return;
      }
      if (!formData.invoice_date) {
        setSnackbar({ open: true, message: 'Invoice date is required', severity: 'error' });
        return;
      }
      if (!formData.due_date) {
        setSnackbar({ open: true, message: 'Due date is required', severity: 'error' });
        return;
      }
      if (!formData.total_amount || formData.total_amount <= 0) {
        setSnackbar({ open: true, message: 'Total amount must be greater than 0', severity: 'error' });
        return;
      }
      
      // Additional validation for data types and formats
      if (isNaN(parseFloat(formData.total_amount))) {
        setSnackbar({ open: true, message: 'Total amount must be a valid number', severity: 'error' });
        return;
      }
      if (isNaN(parseInt(formData.customer_id))) {
        setSnackbar({ open: true, message: 'Please select a valid customer', severity: 'error' });
        return;
      }

      // Find customer name from customer_id
      const selectedCustomer = customers.find(c => c.id === parseInt(formData.customer_id));
      
      // Prepare data for API
      const submitData = {
        customer_id: parseInt(formData.customer_id),
        customer_name: selectedCustomer?.customer_name || selectedCustomer?.name || 'Unknown Customer',
        invoice_number: formData.invoice_number,
        invoice_date: formData.invoice_date,
        due_date: formData.due_date,
        total_amount: parseFloat(formData.total_amount),
        tax_amount: parseFloat(formData.tax_amount || 0),
        status: formData.status,
        description: formData.description
      };
      
      console.log('Submitting invoice data:', JSON.stringify(submitData, null, 2));


      if (editDialogOpen && selectedInvoice) {
        await update(selectedInvoice.id, submitData);
        setSnackbar({ open: true, message: 'Invoice updated successfully!', severity: 'success' });
        // Refresh accounts receivable data to show updated invoice immediately
        refresh();
      } else {
        await create(submitData);
        setSnackbar({ open: true, message: 'Invoice created successfully!', severity: 'success' });
        // Refresh accounts receivable data to show new invoice immediately
        refresh();
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving invoice:', error);
      
      // Try to extract the actual error message from the backend
      let errorMessage = 'Error saving invoice';
      
      if (error.response?.data?.error) {
        // Backend returned a specific error message
        errorMessage = error.response.data.error;
      } else if (error.message) {
        // Use the error message from the exception
        errorMessage = error.message;
      }
      
      setSnackbar({ open: true, message: errorMessage, severity: 'error' });
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
      status: invoice.status || 'pending',
      // Payment tracking fields
      payment_method_id: invoice.payment_method_id || '',
      bank_account_id: invoice.bank_account_id || '',
      payment_reference: invoice.payment_reference || '',
      payment_date: invoice.payment_date ? invoice.payment_date.split('T')[0] : '',
      processing_fee: invoice.processing_fee || '',
      payment_notes: invoice.payment_notes || ''
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

  const handleCustomerInputChange = (field, value) => {
    setCustomerFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleCustomerSubmit = async (e) => {
    e.preventDefault();
    try {
      // Validate required fields
      if (!customerFormData.name) {
        setSnackbar({ open: true, message: 'Customer name is required', severity: 'error' });
        return;
      }

      // Prepare customer data - map frontend fields to backend expected fields
      const submitData = {
        customer_code: customerFormData.name.replace(/\s+/g, '_').replace(/[^A-Z0-9_]/g, '').toUpperCase(), // Generate clean code from name
        customer_name: customerFormData.name,
        contact_person: customerFormData.name,
        email: customerFormData.email,
        phone: customerFormData.phone,
        address: customerFormData.address,
        payment_terms: customerFormData.payment_terms || 'Net 30',
        credit_limit: parseFloat(customerFormData.credit_limit || 0),
        status: 'active'
      };

      // Create customer via API call
      // Mock create customer - no API call
      console.log('Mock create customer:', submitData);
      const response = { id: Date.now(), ...submitData };

      if (response) {
        setSnackbar({ open: true, message: 'Customer created successfully!', severity: 'success' });
        
        // Refresh customers list
        refreshCustomers();
        
        // Auto-select the new customer in invoice form
        setFormData(prev => ({ ...prev, customer_id: response.id }));
        
        // Close customer dialog
        handleCloseCustomerDialog();
      }
    } catch (error) {
      console.error('Customer creation error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to create customer';
      setSnackbar({ open: true, message: `Error creating customer: ${errorMessage}`, severity: 'error' });
    }
  };

  const handleCloseCustomerDialog = () => {
    setAddCustomerDialogOpen(false);
    setCustomerFormData({
      name: '',
      email: '',
      phone: '',
      address: '',
      company_name: '',
      tax_id: '',
      credit_limit: '',
      payment_terms: 'Net 30',
      customer_type: 'regular',
      category: '',
      region: ''
    });
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>Accounts Receivable</Typography>
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
            variant="outlined"
            startIcon={<PersonAdd />}
            onClick={() => setAddCustomerDialogOpen(true)}
          >
            Add Customer
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
                  value={filters.status || ''}
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
                  value={filters.aging || ''}
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

          <TableContainer component={Paper} sx={{ width: '100%', overflowX: 'auto' }}>
            <Table sx={{ minWidth: 800 }} stickyHeader>
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
                          {ar.status === 'paid' ? (
                            <span>
                              <Tooltip title="Invoice already paid">
                                <IconButton 
                                  size="small" 
                                  color="primary"
                                  disabled={true}
                                >
                                  <PaymentOutlined />
                                </IconButton>
                              </Tooltip>
                            </span>
                          ) : (
                            <Tooltip title="Add Partial Payment">
                              <IconButton 
                                size="small" 
                                color="primary"
                                onClick={() => {
                                  setSelectedInvoice(ar);
                                  setPartialPaymentDialogOpen(true);
                                }}
                              >
                                <PaymentOutlined />
                              </IconButton>
                            </Tooltip>
                          )}
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
                    value={formData.customer_id || ''}
                    onChange={(e) => handleInputChange('customer_id', e.target.value)}
                    label="Customer"
                    required
                    error={!formData.customer_id}
                  >
                    {customers.length === 0 ? (
                      <MenuItem disabled>
                        <Box display="flex" alignItems="center" gap={1}>
                          <PersonAdd fontSize="small" />
                          <Typography variant="body2" color="text.secondary">
                            No customers available - Click "Add Customer" to create one
                          </Typography>
                        </Box>
                      </MenuItem>
                    ) : (
                      customers.map((customer) => (
                        <MenuItem key={customer.id} value={customer.id}>
                          {customer.customer_name || customer.name} {customer.contact_person && customer.contact_person !== customer.customer_name && `(${customer.contact_person})`}
                        </MenuItem>
                      ))
                    )}
                  </Select>
                  {!formData.customer_id && (
                    <FormHelperText error>
                      {customers.length === 0 
                        ? 'Please add a customer first using the "Add Customer" button'
                        : 'Customer is required'
                      }
                    </FormHelperText>
                  )}
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
                <FormControl fullWidth margin="normal">
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={formData.currency || 'USD'}
                    onChange={(e) => handleInputChange('currency', e.target.value)}
                    label="Currency"
                    disabled={currenciesLoading}
                  >
                    <MenuItem value="USD">USD - US Dollar</MenuItem>
                    <MenuItem value="EUR">EUR - Euro</MenuItem>
                    <MenuItem value="GBP">GBP - British Pound</MenuItem>
                    <MenuItem value="JPY">JPY - Japanese Yen</MenuItem>
                    <MenuItem value="CAD">CAD - Canadian Dollar</MenuItem>
                    <MenuItem value="AUD">AUD - Australian Dollar</MenuItem>
                    <MenuItem value="CHF">CHF - Swiss Franc</MenuItem>
                    <MenuItem value="CNY">CNY - Chinese Yuan</MenuItem>
                    <MenuItem value="INR">INR - Indian Rupee</MenuItem>
                    <MenuItem value="BRL">BRL - Brazilian Real</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              {formData.currency !== 'USD' && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Exchange Rate"
                    type="number"
                    value={formData.exchange_rate}
                    onChange={(e) => handleInputChange('exchange_rate', parseFloat(e.target.value) || 1.0)}
                    fullWidth
                    margin="normal"
                    InputProps={{
                      endAdornment: exchangeRateLoading ? (
                        <InputAdornment position="end">
                          <LinearProgress size={20} />
                        </InputAdornment>
                      ) : (
                        <InputAdornment position="end">
                          <CurrencyExchange />
                        </InputAdornment>
                      ),
                    }}
                    helperText={`1 ${formData.currency} = ${formData.exchange_rate} USD`}
                  />
                </Grid>
              )}
              {formData.currency !== 'USD' && formData.total_amount && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Amount in USD"
                    type="number"
                    value={(parseFloat(formData.total_amount || 0) * parseFloat(formData.exchange_rate || 1)).toFixed(2)}
                    fullWidth
                    margin="normal"
                    InputProps={{
                      startAdornment: <InputAdornment position="start">$</InputAdornment>,
                      readOnly: true
                    }}
                    disabled
                    helperText="Calculated automatically"
                  />
                </Grid>
              )}
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
                    value={formData.status || 'pending'}
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
              
              {/* Payment Tracking Fields - Show only when status is 'paid' */}
              {showPaymentFields && (
                <>
                  <Grid item xs={12}>
                    <Typography variant="h6" sx={{ mt: 2, mb: 1, color: 'primary.main' }}>
                      Payment Information
                    </Typography>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth margin="normal">
                      <InputLabel>Payment Method</InputLabel>
                      <Select
                        value={formData.payment_method_id || ''}
                        onChange={(e) => handleInputChange('payment_method_id', e.target.value)}
                        label="Payment Method"
                        disabled={paymentMethodsLoading}
                      >
                        {paymentMethods && paymentMethods.map((method) => (
                          <MenuItem key={method.id} value={method.id}>
                            {method.name} {method.default_processing_fee_rate > 0 && `(${method.default_processing_fee_rate}% fee)`}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth margin="normal">
                      <InputLabel>Bank Account</InputLabel>
                      <Select
                        value={formData.bank_account_id || ''}
                        onChange={(e) => handleInputChange('bank_account_id', e.target.value)}
                        label="Bank Account"
                        disabled={bankAccountsLoading}
                      >
                        {bankAccounts && bankAccounts.map((account) => (
                          <MenuItem key={account.id} value={account.id}>
                            {account.account_name} ({account.account_type})
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Payment Reference"
                      value={formData.payment_reference}
                      onChange={(e) => handleInputChange('payment_reference', e.target.value)}
                      fullWidth
                      margin="normal"
                      placeholder="Check #, Transaction ID, etc."
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Payment Date"
                      type="date"
                      value={formData.payment_date}
                      onChange={(e) => handleInputChange('payment_date', e.target.value)}
                      fullWidth
                      margin="normal"
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Processing Fee"
                      type="number"
                      value={formData.processing_fee}
                      onChange={(e) => handleInputChange('processing_fee', e.target.value)}
                      fullWidth
                      margin="normal"
                      InputProps={{
                        startAdornment: <InputAdornment position="start">$</InputAdornment>,
                      }}
                      placeholder="Credit card fees, etc."
                    />
                  </Grid>
                  
                  <Grid item xs={12} sm={6}>
                    <TextField
                      label="Net Amount Received"
                      type="number"
                      value={formData.total_amount && formData.processing_fee ? 
                        (parseFloat(formData.total_amount || 0) - parseFloat(formData.processing_fee || 0)).toFixed(2) : 
                        formData.total_amount}
                      fullWidth
                      margin="normal"
                      InputProps={{
                        startAdornment: <InputAdornment position="start">$</InputAdornment>,
                        readOnly: true
                      }}
                      disabled
                      helperText="Total Amount - Processing Fee"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <TextField
                      label="Payment Notes"
                      value={formData.payment_notes}
                      onChange={(e) => handleInputChange('payment_notes', e.target.value)}
                      fullWidth
                      margin="normal"
                      multiline
                      rows={2}
                      placeholder="Additional payment details..."
                    />
                  </Grid>
                </>
              )}
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

      {/* Add Customer Dialog */}
      <Dialog 
        open={addCustomerDialogOpen} 
        onClose={handleCloseCustomerDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Add New Customer</DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleCustomerSubmit} sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  id="customer-name-field"
                  label="Customer Name"
                  value={customerFormData.name}
                  onChange={(e) => handleCustomerInputChange('name', e.target.value)}
                  fullWidth
                  required
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  id="customer-company-field"
                  label="Company Name"
                  value={customerFormData.company_name}
                  onChange={(e) => handleCustomerInputChange('company_name', e.target.value)}
                  fullWidth
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  id="customer-email-field"
                  label="Email"
                  type="email"
                  value={customerFormData.email}
                  onChange={(e) => handleCustomerInputChange('email', e.target.value)}
                  fullWidth
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Phone"
                  value={customerFormData.phone}
                  onChange={(e) => handleCustomerInputChange('phone', e.target.value)}
                  fullWidth
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Address"
                  value={customerFormData.address}
                  onChange={(e) => handleCustomerInputChange('address', e.target.value)}
                  fullWidth
                  margin="normal"
                  multiline
                  rows={2}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Credit Limit"
                  type="number"
                  value={customerFormData.credit_limit}
                  onChange={(e) => handleCustomerInputChange('credit_limit', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputProps={{
                    startAdornment: '$'
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Payment Terms</InputLabel>
                  <Select
                    value={customerFormData.payment_terms}
                    onChange={(e) => handleCustomerInputChange('payment_terms', e.target.value)}
                    label="Payment Terms"
                  >
                    <MenuItem value="Net 15">Net 15 Days</MenuItem>
                    <MenuItem value="Net 30">Net 30 Days</MenuItem>
                    <MenuItem value="Net 45">Net 45 Days</MenuItem>
                    <MenuItem value="Net 60">Net 60 Days</MenuItem>
                    <MenuItem value="Cash on Delivery">Cash on Delivery</MenuItem>
                    <MenuItem value="Prepaid">Prepaid</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Customer Type</InputLabel>
                  <Select
                    value={customerFormData.customer_type}
                    onChange={(e) => handleCustomerInputChange('customer_type', e.target.value)}
                    label="Customer Type"
                  >
                    <MenuItem value="regular">Regular</MenuItem>
                    <MenuItem value="vip">VIP</MenuItem>
                    <MenuItem value="wholesale">Wholesale</MenuItem>
                    <MenuItem value="retail">Retail</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Region"
                  value={customerFormData.region}
                  onChange={(e) => handleCustomerInputChange('region', e.target.value)}
                  fullWidth
                  margin="normal"
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseCustomerDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleCustomerSubmit}>
            Create Customer
          </Button>
        </DialogActions>
      </Dialog>

      {/* Partial Payment Dialog */}
      <Dialog
        open={partialPaymentDialogOpen}
        onClose={() => setPartialPaymentDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Add Partial Payment - Invoice #{selectedInvoice?.invoice_number}
        </DialogTitle>
        <DialogContent>
          {selectedInvoice && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                Invoice Total: ${selectedInvoice.total_amount} | Outstanding: ${selectedInvoice.outstanding_amount || selectedInvoice.total_amount}
              </Alert>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Payment Reference"
                    fullWidth
                    margin="normal"
                    placeholder="Payment ID, Check #, etc."
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Payment Date"
                    type="date"
                    fullWidth
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                    defaultValue={new Date().toISOString().split('T')[0]}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Payment Amount"
                    type="number"
                    fullWidth
                    margin="normal"
                    InputProps={{
                      startAdornment: <InputAdornment position="start">{selectedInvoice.currency || '$'}</InputAdornment>,
                    }}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Payment Method</InputLabel>
                    <Select
                      label="Payment Method"
                      disabled={paymentMethodsLoading}
                    >
                      {paymentMethods && paymentMethods.map((method) => (
                        <MenuItem key={method.id} value={method.id}>
                          {method.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel>Bank Account</InputLabel>
                    <Select
                      label="Bank Account"
                      disabled={bankAccountsLoading}
                    >
                      {bankAccounts && bankAccounts.map((account) => (
                        <MenuItem key={account.id} value={account.id}>
                          {account.account_name} ({account.account_type})
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Reference Number"
                    fullWidth
                    margin="normal"
                    placeholder="Check #, Transaction ID, etc."
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Payment Notes"
                    fullWidth
                    margin="normal"
                    multiline
                    rows={3}
                    placeholder="Additional payment details..."
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPartialPaymentDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="contained" color="primary">
            Add Payment
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
