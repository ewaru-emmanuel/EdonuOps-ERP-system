import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Autocomplete, SpeedDial, SpeedDialAction, SpeedDialIcon,
  TablePagination, TableSortLabel, InputAdornment, OutlinedInput, FormHelperText, Collapse, List, ListItem, ListItemText, ListItemIcon,
  Checkbox, FormControlLabel, FormGroup, Badge, Avatar, Divider, Accordion, AccordionSummary, AccordionDetails, Radio, RadioGroup
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, LocalTaxi, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb,
  CloudUpload, Description, ReceiptLong, PaymentOutlined, ScheduleSend, AutoFixHigh, SmartToy, QrCode, CameraAlt
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { getERPApiService } from '../../../services/erpApiService';

const SmartAccountsPayable = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState('due_date');
  const [order, setOrder] = useState('asc');
  const [filters, setFilters] = useState({
    status: '',
    vendor: '',
    dueDate: '',
    amount: ''
  });
  const [selectedInvoices, setSelectedInvoices] = useState([]);
  const [bulkAction, setBulkAction] = useState('');
  const [showBulkDialog, setShowBulkDialog] = useState(false);
  const [showOcrDialog, setShowOcrDialog] = useState(false);
  const [ocrFile, setOcrFile] = useState(null);
  const [ocrResults, setOcrResults] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // CRUD Dialog States
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [formData, setFormData] = useState({
    vendor_id: null,
    invoice_number: '',
    invoice_date: '',
    due_date: '',
    total_amount: '',
    tax_amount: '',
    description: '',
    status: 'pending'
  });

  // Real-time data hooks
  const { data: accountsPayable, loading: apLoading, error: apError, create, update, remove, refresh } = useRealTimeData('/api/finance/accounts-payable');
  const { data: vendors, loading: vendorsLoading, refresh: refreshVendors } = useRealTimeData('/api/procurement/vendors');

  // Resolve vendor name by id from procurement list
  const getVendorName = (vendorId) => {
    if (!vendorId || !Array.isArray(vendors)) return '';
    const v = vendors.find(v => v.id === vendorId);
    return v?.name || '';
  };

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
      vendor_id: invoice.vendor_id || null,
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
      vendor_id: null,
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

  // Calculate AP metrics
  const apMetrics = useMemo(() => {
    if (!accountsPayable) return {
      totalOutstanding: 0,
      overdueAmount: 0,
      dueThisWeek: 0,
      averagePaymentTime: 0,
      topVendors: []
    };

    const totalOutstanding = accountsPayable.reduce((sum, ap) => sum + (ap.outstanding_amount || 0), 0);
    const overdueAmount = accountsPayable
      .filter(ap => ap.status === 'overdue')
      .reduce((sum, ap) => sum + (ap.outstanding_amount || 0), 0);
    
    const dueThisWeek = accountsPayable
      .filter(ap => {
        const dueDate = new Date(ap.due_date);
        const today = new Date();
        const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
        return dueDate <= weekFromNow && ap.status === 'pending';
      })
      .reduce((sum, ap) => sum + (ap.outstanding_amount || 0), 0);

    // Calculate average payment time (mock data)
    const averagePaymentTime = 15; // days

    // Top vendors by outstanding amount
    const vendorTotals = accountsPayable.reduce((acc, ap) => {
      const name = ap.vendor_name || getVendorName(ap.vendor_id);
      acc[name] = (acc[name] || 0) + (ap.outstanding_amount || 0);
      return acc;
    }, {});
    
    const topVendors = Object.entries(vendorTotals)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .map(([name, amount]) => ({ name, amount }));

    return {
      totalOutstanding,
      overdueAmount,
      dueThisWeek,
      averagePaymentTime,
      topVendors
    };
  }, [accountsPayable, vendors]);

  // Filter and sort data
  const filteredData = useMemo(() => {
    if (!accountsPayable) return [];
    
    let filtered = [...accountsPayable];
    
    // Apply filters
    if (filters.status) {
      filtered = filtered.filter(ap => ap.status === filters.status);
    }
    
    if (filters.vendor) {
      filtered = filtered.filter(ap => {
        const name = (ap.vendor_name || getVendorName(ap.vendor_id) || '').toLowerCase();
        return name.includes(filters.vendor.toLowerCase());
      });
    }
    
    if (filters.dueDate) {
      const dueDate = new Date(filters.dueDate);
      filtered = filtered.filter(ap => {
        const apDueDate = new Date(ap.due_date);
        return apDueDate.toDateString() === dueDate.toDateString();
      });
    }
    
    if (filters.amount) {
      const amount = parseFloat(filters.amount);
      filtered = filtered.filter(ap => (ap.total_amount || 0) >= amount);
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
  }, [accountsPayable, filters, orderBy, order]);

  // Pagination
  const paginatedData = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return filteredData.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredData, page, rowsPerPage]);

  // Handle bulk selection
  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelectedInvoices(paginatedData.map(ap => ap.id));
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
        case 'approve':
          // Approve selected invoices
          setSnackbar({ open: true, message: `${selectedInvoices.length} invoices approved`, severity: 'success' });
          break;
        case 'schedule':
          // Schedule payments for selected invoices
          setSnackbar({ open: true, message: `Payment scheduled for ${selectedInvoices.length} invoices`, severity: 'success' });
          break;
        case 'reject':
          // Reject selected invoices
          setSnackbar({ open: true, message: `${selectedInvoices.length} invoices rejected`, severity: 'warning' });
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

  // OCR Processing
  const handleOcrUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setOcrFile(file);
      // Simulate OCR processing
      setTimeout(() => {
        setOcrResults({
          vendor: 'Sample Vendor',
          invoiceNumber: 'INV-2024-001',
          amount: 1500.00,
          dueDate: '2024-02-15',
          lineItems: [
            { description: 'Office Supplies', amount: 500.00 },
            { description: 'Software License', amount: 1000.00 }
          ]
        });
      }, 2000);
    }
  };

  const handleOcrConfirm = () => {
    // Create invoice from OCR results
    setSnackbar({ open: true, message: 'Invoice created from OCR successfully', severity: 'success' });
    setShowOcrDialog(false);
    setOcrFile(null);
    setOcrResults(null);
  };

  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleExport = () => {
    const csvContent = "data:text/csv;charset=utf-8," + 
      "Invoice #,Vendor,Due Date,Amount,Outstanding,Status\n" +
      filteredData.map(row => 
        `${row.invoice_number},${row.vendor_name || getVendorName(row.vendor_id)},${row.due_date},${row.total_amount},${row.outstanding_amount},${row.status}`
      ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "accounts_payable.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Box>
      {/* Header with Smart Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>Accounts Payable</Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<CameraAlt />}
            onClick={() => setShowOcrDialog(true)}
          >
            OCR Upload
          </Button>
          <Button
            variant="outlined"
            startIcon={<Schedule />}
            onClick={() => setShowBulkDialog(true)}
            disabled={selectedInvoices.length === 0}
          >
            Bulk Actions ({selectedInvoices.length})
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setAddDialogOpen(true)}
          >
            Add Invoice
          </Button>
        </Box>
      </Box>

      {/* AP Metrics Dashboard */}
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
                    ${apMetrics.totalOutstanding.toLocaleString()}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  <Payment sx={{ fontSize: 28 }} />
                </Avatar>
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
                    ${apMetrics.overdueAmount.toLocaleString()}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  <Warning sx={{ fontSize: 28 }} />
                </Avatar>
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
                    ${apMetrics.dueThisWeek.toLocaleString()}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56 }}>
                  <Schedule sx={{ fontSize: 28 }} />
                </Avatar>
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
                    Avg Payment Time
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    {apMetrics.averagePaymentTime} days
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
                  <Timeline sx={{ fontSize: 28 }} />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Top Vendors */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Top Vendors by Outstanding Amount
          </Typography>
          <Grid container spacing={2}>
            {apMetrics.topVendors.map((vendor, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Box display="flex" alignItems="center" justifyContent="space-between" p={2} sx={{ bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {vendor.name}
                    </Typography>
                    <Typography variant="h6" color="primary">
                      ${vendor.amount.toLocaleString()}
                    </Typography>
                  </Box>
                  <Chip label={`#${index + 1}`} color="primary" size="small" />
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
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="approved">Approved</MenuItem>
                  <MenuItem value="paid">Paid</MenuItem>
                  <MenuItem value="overdue">Overdue</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                label="Vendor"
                value={filters.vendor}
                onChange={(e) => setFilters({ ...filters, vendor: e.target.value })}
                size="small"
                fullWidth
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                label="Due Date"
                type="date"
                value={filters.dueDate}
                onChange={(e) => setFilters({ ...filters, dueDate: e.target.value })}
                size="small"
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
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

      {/* AP Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Vendor Invoices ({filteredData.length} invoices)
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
                  refreshVendors();
                }}
                disabled={apLoading || vendorsLoading}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          {apLoading && <LinearProgress sx={{ mb: 2 }} />}

          {apError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {apError}
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
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'invoice_number'}
                      direction={orderBy === 'invoice_number' ? order : 'asc'}
                      onClick={() => handleSort('invoice_number')}
                    >
                      Invoice #
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Vendor</TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'due_date'}
                      direction={orderBy === 'due_date' ? order : 'asc'}
                      onClick={() => handleSort('due_date')}
                    >
                      Due Date
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="right">
                    <TableSortLabel
                      active={orderBy === 'total_amount'}
                      direction={orderBy === 'total_amount' ? order : 'asc'}
                      onClick={() => handleSort('total_amount')}
                    >
                      Amount
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="right">Outstanding</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedData.map((ap, index) => (
                  <TableRow key={ap.id || `ap-${index}`} hover>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedInvoices.includes(ap.id)}
                        onChange={() => handleSelectInvoice(ap.id)}
                      />
                    </TableCell>
                    <TableCell>{ap.invoice_number || ''}</TableCell>
                    <TableCell>{ap.vendor_name || getVendorName(ap.vendor_id) || ''}</TableCell>
                    <TableCell>
                      {ap.due_date ? new Date(ap.due_date).toLocaleDateString() : ''}
                    </TableCell>
                    <TableCell align="right">${ap.total_amount || 0}</TableCell>
                    <TableCell align="right">${ap.outstanding_amount || 0}</TableCell>
                    <TableCell>
                      <Chip
                        label={ap.status || 'pending'}
                        color={
                          ap.status === 'paid' ? 'success' :
                          ap.status === 'overdue' ? 'error' :
                          ap.status === 'approved' ? 'info' : 'warning'
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
                          <IconButton size="small" onClick={() => handleEdit(ap)}>
                            <Edit />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton color="error" size="small" onClick={() => handleDelete(ap.id)}>
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

      {/* Bulk Actions Dialog */}
      <Dialog
        open={showBulkDialog}
        onClose={() => setShowBulkDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <AutoFixHigh />
            </Avatar>
            <Typography variant="h6">Bulk Actions</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Perform actions on {selectedInvoices.length} selected invoices:
          </Typography>
          
          <FormControl component="fieldset" fullWidth>
            <FormGroup>
              <FormControlLabel
                control={
                  <RadioGroup
                    value={bulkAction}
                    onChange={(e) => setBulkAction(e.target.value)}
                  >
                    <FormControlLabel value="approve" control={<Radio />} label="Approve Invoices" />
                    <FormControlLabel value="schedule" control={<Radio />} label="Schedule Payments" />
                    <FormControlLabel value="reject" control={<Radio />} label="Reject Invoices" />
                  </RadioGroup>
                }
              />
            </FormGroup>
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

      {/* OCR Upload Dialog */}
      <Dialog
        open={showOcrDialog}
        onClose={() => setShowOcrDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <CameraAlt />
            </Avatar>
            <Typography variant="h6">OCR Invoice Processing</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {!ocrResults ? (
            <Box textAlign="center" py={4}>
              <input
                accept="image/*,.pdf"
                style={{ display: 'none' }}
                id="ocr-file-input"
                type="file"
                onChange={handleOcrUpload}
              />
              <label htmlFor="ocr-file-input">
                <Button
                  variant="outlined"
                  component="span"
                  startIcon={<CloudUpload />}
                  size="large"
                >
                  Upload Invoice
                </Button>
              </label>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                Drag and drop or click to upload invoice image/PDF
              </Typography>
            </Box>
          ) : (
            <Box>
              <Typography variant="h6" gutterBottom>
                OCR Results
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Vendor"
                    value={ocrResults.vendor}
                    fullWidth
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Invoice Number"
                    value={ocrResults.invoiceNumber}
                    fullWidth
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Amount"
                    value={ocrResults.amount}
                    fullWidth
                    margin="normal"
                    InputProps={{
                      startAdornment: <InputAdornment position="start">$</InputAdornment>,
                    }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Due Date"
                    type="date"
                    value={ocrResults.dueDate}
                    fullWidth
                    margin="normal"
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Line Items
                  </Typography>
                  {ocrResults.lineItems.map((item, index) => (
                    <Box key={index} display="flex" justifyContent="space-between" p={1} sx={{ bgcolor: 'grey.50', mb: 1, borderRadius: 1 }}>
                      <Typography>{item.description}</Typography>
                      <Typography>${item.amount}</Typography>
                    </Box>
                  ))}
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowOcrDialog(false)}>Cancel</Button>
          {ocrResults && (
            <Button variant="contained" onClick={handleOcrConfirm}>
              Create Invoice
            </Button>
          )}
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
          {editDialogOpen ? 'Edit Invoice' : 'Add New Invoice'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Vendor</InputLabel>
                  <Select
                    value={formData.vendor_id}
                    onChange={(e) => handleInputChange('vendor_id', e.target.value)}
                    label="Vendor"
                    required
                  >
                    {vendors?.map((vendor) => (
                      <MenuItem key={vendor.id} value={vendor.id}>
                        {vendor.name}
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
                    <MenuItem value="approved">Approved</MenuItem>
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

      {/* Floating Action Button */}
      <SpeedDial
        ariaLabel="AP Actions"
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
          tooltipTitle="Add Invoice"
          onClick={() => setAddDialogOpen(true)}
        />
        <SpeedDialAction
          icon={<CameraAlt />}
          tooltipTitle="OCR Upload"
          onClick={() => setShowOcrDialog(true)}
        />
        <SpeedDialAction
          icon={<AutoFixHigh />}
          tooltipTitle="Bulk Actions"
          onClick={() => setShowBulkDialog(true)}
        />
      </SpeedDial>
    </Box>
  );
};

export default SmartAccountsPayable;
