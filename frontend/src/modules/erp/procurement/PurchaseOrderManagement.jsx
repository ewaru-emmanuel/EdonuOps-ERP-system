import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Avatar,
  Tooltip,
  Divider,
  Alert,
  Snackbar,
  LinearProgress,
  InputAdornment,
  IconButton as MuiIconButton
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  CheckCircle,
  Pending,
  Warning,
  Business,
  Description,
  AttachFile,
  Approval,
  Close,
  Save,
  Refresh
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { getERPApiService } from '../../../services/erpApiService';

const PurchaseOrderManagement = () => {
  // State management
  const [openDialog, setOpenDialog] = useState(false);
  const [editingPO, setEditingPO] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [loading, setLoading] = useState(false);
  const [selectedPO, setSelectedPO] = useState(null);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  
  // Form data
  const [formData, setFormData] = useState({
    vendor_id: '',
    order_date: new Date().toISOString().split('T')[0],
    expected_delivery: '',
    notes: '',
    items: []
  });

  // Item form data
  const [itemForm, setItemForm] = useState({
    description: '',
    quantity: '',
    unit_price: '',
    tax_rate: '0'
  });

  // Item editing state
  const [editingItem, setEditingItem] = useState(null);
  const [editingItemIndex, setEditingItemIndex] = useState(-1);

  // Data hooks
  const { 
    data: purchaseOrders, 
    loading: poLoading, 
    error: poError, 
    create: createPO, 
    update: updatePO, 
    remove: deletePO, 
    refresh: refreshPOs 
  } = useRealTimeData('/api/procurement/purchase-orders');

  const { 
    data: vendors, 
    loading: vendorsLoading, 
    error: vendorsError, 
    refresh: refreshVendors 
  } = useRealTimeData('/api/procurement/vendors');

  // Calculate totals
  const calculateTotals = (items) => {
    const subtotal = items.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0);
    const taxTotal = items.reduce((sum, item) => sum + (item.quantity * item.unit_price * (item.tax_rate / 100)), 0);
    return { subtotal, taxTotal, total: subtotal + taxTotal };
  };

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle item form input changes
  const handleItemInputChange = (field, value) => {
    setItemForm(prev => ({
      ...prev,
      [field]: value
    }));
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
      id: Date.now(), // Temporary ID
      description: itemForm.description,
      quantity: parseFloat(itemForm.quantity),
      unit_price: parseFloat(itemForm.unit_price),
      tax_rate: parseFloat(itemForm.tax_rate),
      total_amount: parseFloat(itemForm.quantity) * parseFloat(itemForm.unit_price)
    };

    setFormData(prev => ({
      ...prev,
      items: [...prev.items, newItem]
    }));

    // Reset item form
    setItemForm({
      description: '',
      quantity: '',
      unit_price: '',
      tax_rate: '0'
    });
  };

  // Remove item from PO
  const removeItem = (itemId) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter(item => item.id !== itemId)
    }));
  };

  // Start editing an item
  const startEditItem = (item, index) => {
    setEditingItem({ ...item });
    setEditingItemIndex(index);
    setItemForm({
      description: item.description,
      quantity: item.quantity.toString(),
      unit_price: item.unit_price.toString(),
      tax_rate: item.tax_rate.toString()
    });
  };

  // Save edited item
  const saveEditedItem = () => {
    if (!editingItem.description || !editingItem.quantity || !editingItem.unit_price) {
      setSnackbar({ 
        open: true, 
        message: 'Please fill in all required item fields', 
        severity: 'error' 
      });
      return;
    }

    const updatedItem = {
      ...editingItem,
      description: editingItem.description,
      quantity: parseFloat(editingItem.quantity),
      unit_price: parseFloat(editingItem.unit_price),
      tax_rate: parseFloat(editingItem.tax_rate),
      total_amount: parseFloat(editingItem.quantity) * parseFloat(editingItem.unit_price)
    };

    setFormData(prev => ({
      ...prev,
      items: prev.items.map((item, index) => 
        index === editingItemIndex ? updatedItem : item
      )
    }));

    // Reset editing state
    setEditingItem(null);
    setEditingItemIndex(-1);
    setItemForm({
      description: '',
      quantity: '',
      unit_price: '',
      tax_rate: '0'
    });
  };

  // Cancel editing item
  const cancelEditItem = () => {
    setEditingItem(null);
    setEditingItemIndex(-1);
    setItemForm({
      description: '',
      quantity: '',
      unit_price: '',
      tax_rate: '0'
    });
  };

  // Open dialog for creating/editing PO
  const handleOpenDialog = (po = null) => {
    if (po) {
      setEditingPO(po);
      setFormData({
        vendor_id: po.vendor_id || '',
        order_date: po.order_date || new Date().toISOString().split('T')[0],
        expected_delivery: po.expected_delivery || '',
        notes: po.notes || '',
        items: po.items || []
      });
    } else {
      setEditingPO(null);
      setFormData({
        vendor_id: '',
        order_date: new Date().toISOString().split('T')[0],
        expected_delivery: '',
        notes: '',
        items: []
      });
    }
    setOpenDialog(true);
  };

  // Close dialog
  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingPO(null);
    setFormData({
      vendor_id: '',
      order_date: new Date().toISOString().split('T')[0],
      expected_delivery: '',
      notes: '',
      items: []
    });
    // Reset item editing state
    setEditingItem(null);
    setEditingItemIndex(-1);
    setItemForm({
      description: '',
      quantity: '',
      unit_price: '',
      tax_rate: '0'
    });
  };

  // Submit form
  const handleSubmit = async () => {
    if (!formData.vendor_id || !formData.order_date || formData.items.length === 0) {
      setSnackbar({ 
        open: true, 
        message: 'Please fill in all required fields and add at least one item', 
        severity: 'error' 
      });
      return;
    }

    setLoading(true);
    try {
      const totals = calculateTotals(formData.items);
      const poData = {
        ...formData,
        total_amount: totals.total,
        tax_amount: totals.taxTotal,
        items: formData.items.map(item => ({
          description: item.description,
          quantity: item.quantity,
          unit_price: item.unit_price,
          tax_rate: item.tax_rate,
          total_amount: item.total_amount
        }))
      };

      if (editingPO) {
        await updatePO(editingPO.id, poData);
        setSnackbar({ 
          open: true, 
          message: 'Purchase Order updated successfully!', 
          severity: 'success' 
        });
      } else {
        await createPO(poData);
        setSnackbar({ 
          open: true, 
          message: 'Purchase Order created successfully!', 
          severity: 'success' 
        });
      }

      handleCloseDialog();
      refreshPOs();
    } catch (error) {
      console.error('Error saving purchase order:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error saving purchase order: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    } finally {
      setLoading(false);
    }
  };

  // Delete PO
  const handleDelete = async (poId) => {
    if (!window.confirm('Are you sure you want to delete this purchase order?')) {
      return;
    }

    try {
      const apiService = getERPApiService();
      await apiService.delete(`/api/procurement/purchase-orders/${poId}`);
      
      setSnackbar({ 
        open: true, 
        message: 'Purchase Order deleted successfully!', 
        severity: 'success' 
      });
      refreshPOs();
    } catch (error) {
      console.error('Error deleting purchase order:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error deleting purchase order: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    }
  };

  // Approve PO
  const handleApprove = async (poId) => {
    try {
      const apiService = getERPApiService();
      await apiService.post(`/api/procurement/purchase-orders/${poId}/approve`, {
        approved_by: 1 // TODO: Get actual user ID
      });
      
      setSnackbar({ 
        open: true, 
        message: 'Purchase Order approved successfully!', 
        severity: 'success' 
      });
      refreshPOs();
    } catch (error) {
      console.error('Error approving purchase order:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error approving purchase order: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    }
  };

  // Reject PO
  const handleReject = async (poId) => {
    const reason = window.prompt('Please provide a reason for rejection:');
    if (!reason) return;

    try {
      const apiService = getERPApiService();
      await apiService.post(`/api/procurement/purchase-orders/${poId}/reject`, {
        reason: reason
      });
      
      setSnackbar({ 
        open: true, 
        message: 'Purchase Order rejected successfully!', 
        severity: 'success' 
      });
      refreshPOs();
    } catch (error) {
      console.error('Error rejecting purchase order:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error rejecting purchase order: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    }
  };

  // View PO details
  const handleViewPO = (po) => {
    setSelectedPO(po);
    setViewDialogOpen(true);
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      case 'received': return 'info';
      case 'closed': return 'default';
      default: return 'default';
    }
  };

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle color="success" />;
      case 'pending': return <Pending color="warning" />;
      case 'rejected': return <Warning color="error" />;
      case 'received': return <CheckCircle color="info" />;
      case 'closed': return <CheckCircle color="default" />;
      default: return <Pending />;
    }
  };


  // Get vendor name by ID
  const getVendorName = (vendorId) => {
    const vendor = vendors?.find(v => v.id === vendorId);
    return vendor ? vendor.name : 'Unknown Vendor';
  };

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!purchaseOrders) return {};
    
    const totalPOs = purchaseOrders.length;
    const pendingPOs = purchaseOrders.filter(po => po.status === 'pending').length;
    const approvedPOs = purchaseOrders.filter(po => po.status === 'approved').length;
    const totalValue = purchaseOrders.reduce((sum, po) => sum + (po.total_amount || 0), 0);
    const totalItems = purchaseOrders.reduce((sum, po) => sum + (po.items?.length || 0), 0);

    return { totalPOs, pendingPOs, approvedPOs, totalValue, totalItems };
  }, [purchaseOrders]);

  if (poLoading || vendorsLoading) {
    return (
      <Box>
        <LinearProgress />
        <Box p={3} textAlign="center">
          <Typography>Loading Purchase Orders...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>
          Purchase Order Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => { refreshPOs(); refreshVendors(); }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            sx={{ textTransform: 'none' }}
          >
            Create New PO
          </Button>
        </Box>
      </Box>

      {/* PO Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {metrics.totalPOs || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total POs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1, color: 'warning.main' }}>
                {metrics.pendingPOs || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pending Approval
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1, color: 'success.main' }}>
                ${(metrics.totalValue || 0).toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Value
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {metrics.totalItems || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Items
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Purchase Orders Table */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
            Purchase Orders
          </Typography>
          
          {poError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Error loading purchase orders: {poError.message}
            </Alert>
          )}
          
          <TableContainer component={Paper} elevation={0} sx={{ width: '100%', overflowX: 'auto' }}>
            <Table sx={{ minWidth: 900 }}>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>PO Number</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Vendor</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Order Date</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Expected Delivery</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Total Amount</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Items</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {purchaseOrders?.map((po) => (
                  <TableRow key={po.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <Description />
                        </Avatar>
                        <Box>
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                            {po.po_number || po.id}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            by {po.created_by || 'System'}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {getVendorName(po.vendor_id)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {po.order_date}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {po.expected_delivery || 'Not set'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        ${(po.total_amount || 0).toLocaleString()}
                      </Typography>
                      {po.erp_sync_status && (
                        <Chip size="small" label={`ERP: ${po.erp_sync_status}`} sx={{ ml: 1, textTransform: 'capitalize' }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={po.status}
                        size="small"
                        color={getStatusColor(po.status)}
                        icon={getStatusIcon(po.status)}
                        sx={{ textTransform: 'capitalize' }}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {po.items?.length || 0} items
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Details">
                          <IconButton size="small" color="primary" onClick={() => handleViewPO(po)}>
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit PO">
                          <IconButton size="small" color="primary" onClick={() => handleOpenDialog(po)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        {po.status === 'pending' && (
                          <>
                            <Tooltip title="Approve">
                              <IconButton size="small" color="success" onClick={() => handleApprove(po.id)}>
                                <Approval />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Reject">
                              <IconButton size="small" color="error" onClick={() => handleReject(po.id)}>
                                <Warning />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                        <Tooltip title="Delete PO">
                          <IconButton size="small" color="error" onClick={() => handleDelete(po.id)}>
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          
          {(!purchaseOrders || purchaseOrders.length === 0) && !poLoading && (
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

      {/* Create/Edit PO Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="lg" fullWidth fullScreen={typeof window !== 'undefined' ? window.matchMedia('(max-width:600px)').matches : false}>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              {editingPO ? 'Edit Purchase Order' : 'Create New Purchase Order'}
            </Typography>
            <IconButton onClick={handleCloseDialog}>
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
                  value={formData.vendor_id}
                  label="Vendor *"
                  onChange={(e) => handleInputChange('vendor_id', e.target.value)}
                  error={!formData.vendor_id}
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
                value={formData.order_date}
                onChange={(e) => handleInputChange('order_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                error={!formData.order_date}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Expected Delivery"
                type="date"
                value={formData.expected_delivery}
                onChange={(e) => handleInputChange('expected_delivery', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
              />
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" sx={{ mb: 2 }}>
            Order Items *
          </Typography>

          {/* Add/Edit Item Form */}
          {editingItem && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Editing item: {editingItem.description} - Click Save to confirm changes or Cancel to discard
            </Alert>
          )}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Description *"
                value={editingItem ? editingItem.description : itemForm.description}
                onChange={(e) => {
                  if (editingItem) {
                    setEditingItem(prev => ({ ...prev, description: e.target.value }));
                  } else {
                    handleItemInputChange('description', e.target.value);
                  }
                }}
                size="small"
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                label="Quantity *"
                type="number"
                value={editingItem ? editingItem.quantity : itemForm.quantity}
                onChange={(e) => {
                  if (editingItem) {
                    setEditingItem(prev => ({ ...prev, quantity: e.target.value }));
                  } else {
                    handleItemInputChange('quantity', e.target.value);
                  }
                }}
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
                value={editingItem ? editingItem.unit_price : itemForm.unit_price}
                onChange={(e) => {
                  if (editingItem) {
                    setEditingItem(prev => ({ ...prev, unit_price: e.target.value }));
                  } else {
                    handleItemInputChange('unit_price', e.target.value);
                  }
                }}
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
                value={editingItem ? editingItem.tax_rate : itemForm.tax_rate}
                onChange={(e) => {
                  if (editingItem) {
                    setEditingItem(prev => ({ ...prev, tax_rate: e.target.value }));
                  } else {
                    handleItemInputChange('tax_rate', e.target.value);
                  }
                }}
                size="small"
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              {editingItem ? (
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    startIcon={<Save />}
                    onClick={saveEditedItem}
                    sx={{ textTransform: 'none', height: '40px' }}
                    size="small"
                  >
                    Save
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={cancelEditItem}
                    sx={{ textTransform: 'none', height: '40px' }}
                    size="small"
                  >
                    Cancel
                  </Button>
                </Box>
              ) : (
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={addItem}
                  sx={{ textTransform: 'none', height: '40px' }}
                  fullWidth
                >
                  Add Item
                </Button>
              )}
            </Grid>
          </Grid>

          {/* Items Table */}
          {formData.items.length > 0 && (
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
                  {formData.items.map((item, index) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.description}</TableCell>
                      <TableCell align="right">{item.quantity}</TableCell>
                      <TableCell align="right">${item.unit_price.toLocaleString()}</TableCell>
                      <TableCell align="right">{item.tax_rate}%</TableCell>
                      <TableCell align="right">${item.total_amount.toLocaleString()}</TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="Edit Item">
                            <IconButton 
                              size="small" 
                              color="primary" 
                              onClick={() => startEditItem(item, index)}
                              disabled={editingItem !== null}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Item">
                            <IconButton 
                              size="small" 
                              color="error" 
                              onClick={() => removeItem(item.id)}
                              disabled={editingItem !== null}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {/* Totals */}
          {formData.items.length > 0 && (
            <Box sx={{ textAlign: 'right', mt: 2 }}>
              <Typography variant="h6">
                Subtotal: ${calculateTotals(formData.items).subtotal.toLocaleString()}
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Tax: ${calculateTotals(formData.items).taxTotal.toLocaleString()}
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                Total: ${calculateTotals(formData.items).total.toLocaleString()}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained" 
            disabled={loading || formData.items.length === 0}
            startIcon={loading ? <LinearProgress size={20} /> : <Save />}
          >
            {loading ? 'Saving...' : (editingPO ? 'Update' : 'Create')} Purchase Order
          </Button>
        </DialogActions>
      </Dialog>

      {/* View PO Details Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Purchase Order Details
            </Typography>
            <IconButton onClick={() => setViewDialogOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedPO && (
            <Grid container spacing={3}>
              {/* PO Header Info */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 2, mb: 2 }}>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Purchase Order Information
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">PO Number</Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {selectedPO.po_number || selectedPO.id}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Vendor</Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {getVendorName(selectedPO.vendor_id)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Order Date</Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {selectedPO.order_date}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Expected Delivery</Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {selectedPO.expected_delivery || 'Not set'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Status</Typography>
                      <Chip 
                        label={selectedPO.status} 
                        size="small"
                        color={getStatusColor(selectedPO.status)}
                        icon={getStatusIcon(selectedPO.status)}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Total Amount</Typography>
                      <Typography variant="body1" fontWeight="medium" color="primary">
                        ${(selectedPO.total_amount || 0).toLocaleString()}
                      </Typography>
                    </Grid>
                    {selectedPO.notes && (
                      <Grid item xs={12}>
                        <Typography variant="body2" color="text.secondary">Notes</Typography>
                        <Typography variant="body1" sx={{ mt: 1, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                          {selectedPO.notes}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </Card>
              </Grid>

              {/* PO Items */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Order Items
                  </Typography>
                  <TableContainer component={Paper} elevation={0}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Description</TableCell>
                          <TableCell align="right">Quantity</TableCell>
                          <TableCell align="right">Unit Price</TableCell>
                          <TableCell align="right">Tax Rate</TableCell>
                          <TableCell align="right">Total</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                                                 {selectedPO.items?.map((item, index) => (
                           <TableRow key={`view-${selectedPO.id}-item-${index}`}>
                             <TableCell>{item.description}</TableCell>
                             <TableCell align="right">{item.quantity}</TableCell>
                             <TableCell align="right">${item.unit_price?.toLocaleString()}</TableCell>
                             <TableCell align="right">{item.tax_rate || 0}%</TableCell>
                             <TableCell align="right">${item.total_amount?.toLocaleString()}</TableCell>
                           </TableRow>
                         ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
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
    </Box>
  );
};

export default PurchaseOrderManagement;
