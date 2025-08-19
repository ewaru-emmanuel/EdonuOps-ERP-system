import React, { useState } from 'react';
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
  Stepper,
  Step,
  StepLabel,
  Divider
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
  Approval
} from '@mui/icons-material';

const PurchaseOrderManagement = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [editingPO, setEditingPO] = useState(null);
  
  const showSnackbar = (message, severity = 'success') => {
    // For now, just log to console. In a real app, this would show a snackbar
    console.log(`${severity.toUpperCase()}: ${message}`);
  };
  const [formData, setFormData] = useState({
    vendor_id: '',
    order_date: '',
    expected_delivery: '',
    items: [],
    notes: ''
  });

  const purchaseOrders = [
    {
      id: 'PO-001',
      vendor: 'Tech Supplies Co.',
      order_date: '2024-01-15',
      expected_delivery: '2024-01-25',
      total_amount: 12500,
      status: 'pending',
      items_count: 5,
      created_by: 'John Smith'
    },
    {
      id: 'PO-002',
      vendor: 'Office Solutions',
      order_date: '2024-01-14',
      expected_delivery: '2024-01-24',
      total_amount: 8500,
      status: 'approved',
      items_count: 3,
      created_by: 'Sarah Johnson'
    },
    {
      id: 'PO-003',
      vendor: 'Industrial Parts Ltd.',
      order_date: '2024-01-13',
      expected_delivery: '2024-01-23',
      total_amount: 22000,
      status: 'rejected',
      items_count: 8,
      created_by: 'Mike Wilson'
    },
    {
      id: 'PO-004',
      vendor: 'Global Electronics',
      order_date: '2024-01-12',
      expected_delivery: '2024-01-22',
      total_amount: 15600,
      status: 'pending',
      items_count: 6,
      created_by: 'Lisa Brown'
    }
  ];

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

  const handleOpenDialog = (po = null) => {
    if (po) {
      setEditingPO(po);
      setFormData(po);
    } else {
      setEditingPO(null);
      setFormData({
        vendor_id: '',
        order_date: '',
        expected_delivery: '',
        items: [],
        notes: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingPO(null);
  };

  const handleSubmit = () => {
    // TODO: Implement API call to save PO
    console.log('Saving PO:', formData);
    handleCloseDialog();
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>
          Purchase Order Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ textTransform: 'none' }}
        >
          Create New PO
        </Button>
      </Box>

      {/* PO Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {purchaseOrders.length}
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
                {purchaseOrders.filter(po => po.status === 'pending').length}
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
                ${purchaseOrders.reduce((sum, po) => sum + po.total_amount, 0).toLocaleString()}
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
                {purchaseOrders.reduce((sum, po) => sum + po.items_count, 0)}
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
          
          <TableContainer component={Paper} elevation={0}>
            <Table>
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
                {purchaseOrders.map((po) => (
                  <TableRow key={po.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <Description />
                        </Avatar>
                        <Box>
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                            {po.id}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            by {po.created_by}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {po.vendor}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {po.order_date}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {po.expected_delivery}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        ${po.total_amount.toLocaleString()}
                      </Typography>
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
                        {po.items_count} items
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="View Details">
                          <IconButton size="small" color="primary" onClick={() => showSnackbar(`Viewing purchase order details for ${po.po_number}`)}>
                            <ViewIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit PO">
                          <IconButton size="small" color="primary" onClick={() => handleOpenDialog(po)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        {po.status === 'pending' && (
                          <Tooltip title="Approve">
                            <IconButton size="small" color="success" onClick={() => showSnackbar(`Purchase order ${po.po_number} approved successfully`)}>
                              <Approval />
                            </IconButton>
                          </Tooltip>
                        )}
                        <Tooltip title="Delete PO">
                          <IconButton size="small" color="error" onClick={() => showSnackbar(`Delete purchase order ${po.po_number} would open confirmation dialog`)}>
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
        </CardContent>
      </Card>

      {/* Create/Edit PO Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="lg" fullWidth>
        <DialogTitle>
          {editingPO ? 'Edit Purchase Order' : 'Create New Purchase Order'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Vendor</InputLabel>
                <Select
                  value={formData.vendor_id}
                  label="Vendor"
                  onChange={(e) => handleInputChange('vendor_id', e.target.value)}
                >
                  <MenuItem value="1">Tech Supplies Co.</MenuItem>
                  <MenuItem value="2">Office Solutions</MenuItem>
                  <MenuItem value="3">Industrial Parts Ltd.</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Order Date"
                type="date"
                value={formData.order_date}
                onChange={(e) => handleInputChange('order_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
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
            Order Items
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              size="small"
              sx={{ textTransform: 'none' }}
            >
              Add Item
            </Button>
          </Box>

          <TableContainer component={Paper} elevation={0}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Item</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Quantity</TableCell>
                  <TableCell>Unit Price</TableCell>
                  <TableCell>Total</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography variant="body2" color="text.secondary">
                      No items added yet
                    </Typography>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingPO ? 'Update' : 'Create'} Purchase Order
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PurchaseOrderManagement;
