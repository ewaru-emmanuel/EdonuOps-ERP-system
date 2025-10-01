import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Alert,
  Snackbar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Divider,
  InputAdornment
} from '@mui/material';
import {
  Pending,
  CheckCircle,
  Warning,
  Add as AddIcon,
  Business,
  Description,
  AttachFile,
  Close,
  Save,
  Visibility,
  Edit,
  Delete,
  Refresh,
  Upload,
  BarChart
} from '@mui/icons-material';
// Removed API imports to prevent authentication calls

const ProcurementDashboard = () => {
  // State management
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [loading, setLoading] = useState(false);
  
  // Dialog states
  const [createPODialog, setCreatePODialog] = useState(false);
  const [addVendorDialog, setAddVendorDialog] = useState(false);
  const [uploadDocumentsDialog, setUploadDocumentsDialog] = useState(false);
  const [viewReportsDialog, setViewReportsDialog] = useState(false);
  const [pendingApprovalsDialog, setPendingApprovalsDialog] = useState(false);
  
  // Form states
  const [poForm, setPOForm] = useState({
    vendor_id: '',
    order_date: new Date().toISOString().split('T')[0],
    expected_delivery: '',
    notes: '',
    items: []
  });
  
  const [vendorForm, setVendorForm] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    tax_id: '',
    payment_terms: 'Net 30',
    credit_limit: ''
  });
  
  const [itemForm, setItemForm] = useState({
    description: '',
    quantity: '',
    unit_price: '',
    tax_rate: '0'
  });

  // Data hooks
  // Mock data to prevent API calls
  const purchaseOrders = [];
  const poLoading = false;
  const poError = null;
  const createPO = async (data) => { console.log('Mock create PO:', data); return { id: Date.now(), ...data }; };
  const refreshPOs = () => { console.log('Mock refresh purchase orders'); };
  
  const vendors = [];
  const vendorsLoading = false;
  const vendorsError = null;
  const createVendor = async (data) => { console.log('Mock create vendor:', data); return { id: Date.now(), ...data }; };
  const refreshVendors = () => { console.log('Mock refresh vendors'); };

  // Calculate metrics from real data
  const metrics = useMemo(() => {
    if (!purchaseOrders) return {};
    
    const totalPOs = purchaseOrders.length;
    const pendingPOs = purchaseOrders.filter(po => po.status === 'pending').length;
    const approvedPOs = purchaseOrders.filter(po => po.status === 'approved').length;
    const rejectedPOs = purchaseOrders.filter(po => po.status === 'rejected').length;
    const totalValue = purchaseOrders.reduce((sum, po) => sum + (po.total_amount || 0), 0);
    
    const approvalRate = totalPOs > 0 ? Math.round((approvedPOs / totalPOs) * 100) : 0;
    const costSavings = totalPOs > 0 ? Math.round((rejectedPOs / totalPOs) * 15) : 0; // Simulated
    
    return { 
      totalPOs, 
      pendingPOs, 
      approvedPOs, 
      rejectedPOs, 
      totalValue, 
      approvalRate, 
      costSavings 
    };
  }, [purchaseOrders]);

  // Get recent POs (last 5)
  const recentPOs = useMemo(() => {
    if (!purchaseOrders) return [];
    return purchaseOrders
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 5);
  }, [purchaseOrders]);

  // Get pending approvals
  const pendingApprovals = useMemo(() => {
    if (!purchaseOrders) return [];
    return purchaseOrders.filter(po => po.status === 'pending');
  }, [purchaseOrders]);

  // Helper functions
  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle color="success" />;
      case 'pending': return <Pending color="warning" />;
      case 'rejected': return <Warning color="error" />;
      default: return <Pending />;
    }
  };

  const getVendorName = (vendorId) => {
    const vendor = vendors?.find(v => v.id === vendorId);
    return vendor ? vendor.name : 'Unknown Vendor';
  };

  // Calculate totals for PO items
  const calculateTotals = (items) => {
    const subtotal = items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
    const taxTotal = items.reduce((sum, item) => sum + (item.quantity * item.unit_price * (item.tax_rate / 100)), 0);
    return { subtotal, taxTotal, total: subtotal + taxTotal };
  };

  // Add item to PO
  const addItem = () => {
    if (!itemForm.description || !itemForm.quantity || !itemForm.unit_price) {
      setSnackbar({ 
        open: true, 
        message: 'Please fill in all required item fields', 
        severity: 'error' 
      });
      return;
    }

    const newItem = {
      id: Date.now(),
      description: itemForm.description,
      quantity: parseFloat(itemForm.quantity),
      unit_price: parseFloat(itemForm.unit_price),
      tax_rate: parseFloat(itemForm.tax_rate),
      total_amount: parseFloat(itemForm.quantity) * parseFloat(itemForm.unit_price)
    };

    setPOForm(prev => ({
      ...prev,
      items: [...prev.items, newItem]
    }));

    setItemForm({
      description: '',
      quantity: '',
      unit_price: '',
      tax_rate: '0'
    });
  };

  // Remove item from PO
  const removeItem = (itemId) => {
    setPOForm(prev => ({
      ...prev,
      items: prev.items.filter(item => item.id !== itemId)
    }));
  };

  // Handle PO form submission
  const handlePOSubmit = async () => {
    if (!poForm.vendor_id || !poForm.order_date || poForm.items.length === 0) {
      setSnackbar({ 
        open: true, 
        message: 'Please fill in all required fields and add at least one item', 
        severity: 'error' 
      });
      return;
    }

    setLoading(true);
    try {
      const totals = calculateTotals(poForm.items);
      const poData = {
        ...poForm,
        total_amount: totals.total,
        tax_amount: totals.taxTotal,
        items: poForm.items.map(item => ({
          description: item.description,
          quantity: item.quantity,
          unit_price: item.unit_price,
          tax_rate: item.tax_rate,
          total_amount: item.total_amount
        }))
      };

      await createPO(poData);
      setSnackbar({ 
        open: true, 
        message: 'Purchase Order created successfully!', 
        severity: 'success' 
      });
      setCreatePODialog(false);
      resetPOForm();
      refreshPOs();
    } catch (error) {
      console.error('Error creating purchase order:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error creating purchase order: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle vendor form submission
  const handleVendorSubmit = async () => {
    if (!vendorForm.name || !vendorForm.email) {
      setSnackbar({ 
        open: true, 
        message: 'Please fill in vendor name and email', 
        severity: 'error' 
      });
      return;
    }

    setLoading(true);
    try {
      await createVendor(vendorForm);
      setSnackbar({ 
        open: true, 
        message: 'Vendor created successfully!', 
        severity: 'success' 
      });
      setAddVendorDialog(false);
      resetVendorForm();
      refreshVendors();
    } catch (error) {
      console.error('Error creating vendor:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error creating vendor: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  // Reset forms
  const resetPOForm = () => {
    setPOForm({
      vendor_id: '',
      order_date: new Date().toISOString().split('T')[0],
      expected_delivery: '',
      notes: '',
      items: []
    });
    setItemForm({
      description: '',
      quantity: '',
      unit_price: '',
      tax_rate: '0'
    });
  };

  const resetVendorForm = () => {
    setVendorForm({
      name: '',
      email: '',
      phone: '',
      address: '',
      tax_id: '',
      payment_terms: 'Net 30',
      credit_limit: ''
    });
  };

  // Approve/Reject PO
  const handlePOAction = async (poId, action) => {
    try {
      // Mock API call - no authentication
      console.log('Mock PO action:', action, 'for PO:', poId);
      if (action === 'approve') {
        setSnackbar({ 
          open: true, 
          message: 'Purchase Order approved successfully!', 
          severity: 'success' 
        });
      } else if (action === 'reject') {
        const reason = window.prompt('Please provide a reason for rejection:');
        if (!reason) return;
        
        setSnackbar({ 
          open: true, 
          message: 'Purchase Order rejected successfully!', 
          severity: 'success' 
        });
      }
      refreshPOs();
    } catch (error) {
      console.error(`Error ${action}ing purchase order:`, error);
      setSnackbar({ 
        open: true, 
        message: `Error ${action}ing purchase order: ` + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    }
  };

  return (
    <Grid container spacing={3}>
      {/* Recent Purchase Orders */}
      <Grid item xs={12} lg={8}>
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                Recent Purchase Orders
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                size="small"
                onClick={() => setCreatePODialog(true)}
                sx={{ textTransform: 'none' }}
              >
                New PO
              </Button>
            </Box>
            
            {poLoading ? (
              <Box textAlign="center" py={4}>
                <LinearProgress />
                <Typography sx={{ mt: 2 }}>Loading purchase orders...</Typography>
              </Box>
            ) : poError ? (
              <Alert severity="error" sx={{ mb: 2 }}>
                Error loading purchase orders: {poError.message}
              </Alert>
            ) : (
              <List sx={{ p: 0 }}>
                {recentPOs.map((po) => (
                  <ListItem
                    key={po.id}
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                      '&:last-child': { mb: 0 }
                    }}
                  >
                    <ListItemIcon>
                      {getStatusIcon(po.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>
                            {po.po_number || po.id}
                          </Box>
                          <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>
                            ${(po.total_amount || 0).toLocaleString()}
                          </Box>
                        </Box>
                      }
                      secondary={
                        <Box component="span" sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
                          {getVendorName(po.vendor_id)}
                        </Box>
                      }
                    />
                    <Box sx={{ ml: 2 }}>
                      <Chip
                        label={po.status}
                        size="small"
                        color={getStatusColor(po.status)}
                        sx={{ textTransform: 'capitalize' }}
                      />
                    </Box>
                  </ListItem>
                ))}
              </List>
            )}
            
            {(!recentPOs || recentPOs.length === 0) && !poLoading && (
              <Box textAlign="center" py={4}>
                <Description sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No Purchase Orders Found
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Start by creating your first purchase order
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Pending Approvals */}
      <Grid item xs={12} lg={4}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 3 }}>
              Pending Approvals
            </Typography>
            
            {poLoading ? (
              <Box textAlign="center" py={2}>
                <LinearProgress />
              </Box>
            ) : (
              <>
                <List sx={{ p: 0 }}>
                  {pendingApprovals.slice(0, 3).map((approval) => (
                    <ListItem
                      key={approval.id}
                      sx={{
                        border: '1px solid',
                        borderColor: 'warning.main',
                        borderRadius: 1,
                        mb: 2,
                        bgcolor: 'warning.50'
                      }}
                    >
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>
                              {approval.po_number || approval.id}
                            </Box>
                            <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem', color: 'warning.main' }}>
                              ${(approval.total_amount || 0).toLocaleString()}
                            </Box>
                          </Box>
                        }
                        secondary={
                          <Box component="span" sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
                            {getVendorName(approval.vendor_id)}
                          </Box>
                        }
                      />
                      <Box sx={{ ml: 2, display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                        <Box component="span" sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                          {approval.created_at ? new Date(approval.created_at).toLocaleDateString() : 'Unknown'}
                        </Box>
                      </Box>
                    </ListItem>
                  ))}
                </List>

                {pendingApprovals.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Button
                      variant="contained"
                      color="warning"
                      fullWidth
                      onClick={() => setPendingApprovalsDialog(true)}
                      sx={{ textTransform: 'none' }}
                    >
                      Review All Pending ({pendingApprovals.length})
                    </Button>
                  </Box>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Quick Actions */}
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 3 }}>
              Quick Actions
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  fullWidth
                  onClick={() => setCreatePODialog(true)}
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Create PO
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<Business />}
                  fullWidth
                  onClick={() => setAddVendorDialog(true)}
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Add Vendor
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<BarChart />}
                  fullWidth
                  onClick={() => setViewReportsDialog(true)}
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  View Reports
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<Upload />}
                  fullWidth
                  onClick={() => setUploadDocumentsDialog(true)}
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Upload Documents
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Performance Metrics */}
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 3 }}>
              Performance Metrics
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Approval Rate</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{metrics.approvalRate || 0}%</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={metrics.approvalRate || 0} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Total POs</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{metrics.totalPOs || 0}</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((metrics.totalPOs || 0) * 10, 100)} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Pending Approvals</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>{metrics.pendingPOs || 0}</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((metrics.pendingPOs || 0) * 20, 100)} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Total Value</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>${(metrics.totalValue || 0).toLocaleString()}</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={Math.min((metrics.totalValue || 0) / 1000, 100)} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Create PO Dialog */}
      <Dialog open={createPODialog} onClose={() => setCreatePODialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Create New Purchase Order</Typography>
            <IconButton onClick={() => setCreatePODialog(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Vendor *</InputLabel>
                <Select
                  value={poForm.vendor_id}
                  label="Vendor *"
                  onChange={(e) => setPOForm(prev => ({ ...prev, vendor_id: e.target.value }))}
                  error={!poForm.vendor_id}
                >
                  {vendors?.map((vendor) => (
                    <MenuItem key={vendor.id} value={vendor.id}>
                      {vendor.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Order Date *"
                type="date"
                value={poForm.order_date}
                onChange={(e) => setPOForm(prev => ({ ...prev, order_date: e.target.value }))}
                InputLabelProps={{ shrink: true }}
                error={!poForm.order_date}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Expected Delivery"
                type="date"
                value={poForm.expected_delivery}
                onChange={(e) => setPOForm(prev => ({ ...prev, expected_delivery: e.target.value }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={poForm.notes}
                onChange={(e) => setPOForm(prev => ({ ...prev, notes: e.target.value }))}
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" sx={{ mb: 2 }}>
            Order Items *
          </Typography>

          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Description *"
                value={itemForm.description}
                onChange={(e) => setItemForm(prev => ({ ...prev, description: e.target.value }))}
                size="small"
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                label="Quantity *"
                type="number"
                value={itemForm.quantity}
                onChange={(e) => setItemForm(prev => ({ ...prev, quantity: e.target.value }))}
                size="small"
                InputProps={{
                  startAdornment: <InputAdornment position="start">Qty</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                label="Unit Price *"
                type="number"
                value={itemForm.unit_price}
                onChange={(e) => setItemForm(prev => ({ ...prev, unit_price: e.target.value }))}
                size="small"
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                label="Tax Rate %"
                type="number"
                value={itemForm.tax_rate}
                onChange={(e) => setItemForm(prev => ({ ...prev, tax_rate: e.target.value }))}
                size="small"
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={addItem}
                sx={{ textTransform: 'none', height: '40px' }}
                fullWidth
              >
                Add Item
              </Button>
            </Grid>
          </Grid>

          {/* Items Table */}
          {poForm.items.length > 0 && (
            <TableContainer component={Paper} elevation={0} sx={{ mb: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Description</TableCell>
                    <TableCell align="right">Quantity</TableCell>
                    <TableCell align="right">Unit Price</TableCell>
                    <TableCell align="right">Tax Rate</TableCell>
                    <TableCell align="right">Total</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {poForm.items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.description}</TableCell>
                      <TableCell align="right">{item.quantity}</TableCell>
                      <TableCell align="right">${item.unit_price.toLocaleString()}</TableCell>
                      <TableCell align="right">{item.tax_rate}%</TableCell>
                      <TableCell align="right">${item.total_amount.toLocaleString()}</TableCell>
                      <TableCell align="center">
                        <Tooltip title="Remove Item">
                          <IconButton 
                            size="small" 
                            color="error" 
                            onClick={() => removeItem(item.id)}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Totals */}
          {poForm.items.length > 0 && (
            <Box sx={{ textAlign: 'right', mt: 2 }}>
              <Typography variant="h6">
                Subtotal: ${calculateTotals(poForm.items).subtotal.toLocaleString()}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Tax: ${calculateTotals(poForm.items).taxTotal.toLocaleString()}
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                Total: ${calculateTotals(poForm.items).total.toLocaleString()}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreatePODialog(false)}>Cancel</Button>
          <Button 
            onClick={handlePOSubmit} 
            variant="contained" 
            disabled={loading || poForm.items.length === 0}
            startIcon={loading ? <LinearProgress size={20} /> : <Save />}
          >
            {loading ? 'Creating...' : 'Create Purchase Order'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Vendor Dialog */}
      <Dialog open={addVendorDialog} onClose={() => setAddVendorDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Add New Vendor</Typography>
            <IconButton onClick={() => setAddVendorDialog(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Vendor Name *"
                value={vendorForm.name}
                onChange={(e) => setVendorForm(prev => ({ ...prev, name: e.target.value }))}
                error={!vendorForm.name}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email *"
                type="email"
                value={vendorForm.email}
                onChange={(e) => setVendorForm(prev => ({ ...prev, email: e.target.value }))}
                error={!vendorForm.email}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Phone"
                value={vendorForm.phone}
                onChange={(e) => setVendorForm(prev => ({ ...prev, phone: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tax ID"
                value={vendorForm.tax_id}
                onChange={(e) => setVendorForm(prev => ({ ...prev, tax_id: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Payment Terms</InputLabel>
                <Select
                  value={vendorForm.payment_terms}
                  label="Payment Terms"
                  onChange={(e) => setVendorForm(prev => ({ ...prev, payment_terms: e.target.value }))}
                >
                  <MenuItem value="Net 30">Net 30</MenuItem>
                  <MenuItem value="Net 60">Net 60</MenuItem>
                  <MenuItem value="Net 90">Net 90</MenuItem>
                  <MenuItem value="Immediate">Immediate</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Credit Limit"
                type="number"
                value={vendorForm.credit_limit}
                onChange={(e) => setVendorForm(prev => ({ ...prev, credit_limit: e.target.value }))}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                multiline
                rows={3}
                value={vendorForm.address}
                onChange={(e) => setVendorForm(prev => ({ ...prev, address: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddVendorDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleVendorSubmit} 
            variant="contained" 
            disabled={loading || !vendorForm.name || !vendorForm.email}
            startIcon={loading ? <LinearProgress size={20} /> : <Save />}
          >
            {loading ? 'Creating...' : 'Create Vendor'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Pending Approvals Dialog */}
      <Dialog open={pendingApprovalsDialog} onClose={() => setPendingApprovalsDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Pending Approvals ({pendingApprovals.length})</Typography>
            <IconButton onClick={() => setPendingApprovalsDialog(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>PO Number</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Vendor</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Amount</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Date</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pendingApprovals.map((po) => (
                  <TableRow key={po.id} hover>
                    <TableCell>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                        {po.po_number || po.id}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {getVendorName(po.vendor_id)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        ${(po.total_amount || 0).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {po.created_at ? new Date(po.created_at).toLocaleDateString() : 'Unknown'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Approve">
                          <IconButton 
                            size="small" 
                            color="success" 
                            onClick={() => handlePOAction(po.id, 'approve')}
                          >
                            <CheckCircle />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Reject">
                          <IconButton 
                            size="small" 
                            color="error" 
                            onClick={() => handlePOAction(po.id, 'reject')}
                          >
                            <Warning />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          {pendingApprovals.length === 0 && (
            <Box textAlign="center" py={4}>
              <CheckCircle sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
              <Typography variant="h6" color="success.main" gutterBottom>
                No Pending Approvals
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All purchase orders have been processed
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPendingApprovalsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Upload Documents Dialog */}
      <Dialog open={uploadDocumentsDialog} onClose={() => setUploadDocumentsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Upload Documents</Typography>
            <IconButton onClick={() => setUploadDocumentsDialog(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box textAlign="center" py={4}>
            <Upload sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Document Upload Feature
            </Typography>
            <Typography variant="body2" color="text.secondary">
              This feature will be implemented in the next phase to allow uploading of contracts, invoices, and other procurement documents.
            </Typography>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDocumentsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* View Reports Dialog */}
      <Dialog open={viewReportsDialog} onClose={() => setViewReportsDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Procurement Reports</Typography>
            <IconButton onClick={() => setViewReportsDialog(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Purchase Order Summary
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {metrics.totalPOs || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Purchase Orders
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Total Value
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    ${(metrics.totalValue || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Combined PO Value
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Approval Rate
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {metrics.approvalRate || 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Successfully Approved
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Pending Approvals
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', mb: 1 }}>
                    {metrics.pendingPOs || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Awaiting Decision
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewReportsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Grid>
  );
};

export default ProcurementDashboard;
