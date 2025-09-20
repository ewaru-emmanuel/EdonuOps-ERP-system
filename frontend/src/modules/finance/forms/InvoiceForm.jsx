import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Grid,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Autocomplete,
  Alert,
  Chip,
  Divider
} from '@mui/material';
import {
  Add,
  Delete,
  Save,
  Cancel,
  Person,
  Receipt
} from '@mui/icons-material';
import { useAuth } from '../../../hooks/useAuth';

const InvoiceForm = ({ open, onClose, invoice = null, onSave }) => {
  const { user } = useAuth();
  
  const [formData, setFormData] = useState({
    customer_name: '',
    customer_email: '',
    customer_address: '',
    invoice_number: '',
    invoice_date: new Date().toISOString().slice(0, 10),
    due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10), // 30 days from now
    payment_terms: '30',
    currency: 'USD',
    tax_rate: 8.5, // Default tax rate
    notes: '',
    line_items: [
      { description: '', quantity: 1, unit_price: '', amount: 0 }
    ]
  });

  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  // Customers loaded from API - will be empty until you add customers
  const customers = [];

  // Populate form when editing
  useEffect(() => {
    if (invoice) {
      setFormData({
        customer_name: invoice.customer_name || '',
        customer_email: invoice.customer_email || '',
        customer_address: invoice.customer_address || '',
        invoice_number: invoice.invoice_number || '',
        invoice_date: invoice.invoice_date || new Date().toISOString().slice(0, 10),
        due_date: invoice.due_date || new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10),
        payment_terms: invoice.payment_terms || '30',
        currency: invoice.currency || 'USD',
        tax_rate: invoice.tax_rate || 8.5,
        notes: invoice.notes || '',
        line_items: invoice.line_items?.length > 0 ? invoice.line_items : [
          { description: '', quantity: 1, unit_price: '', amount: 0 }
        ]
      });
    } else {
      // Generate invoice number for new invoices
      const invoiceNum = `INV-${new Date().getFullYear()}-${String(Date.now()).slice(-6)}`;
      setFormData(prev => ({ ...prev, invoice_number: invoiceNum }));
    }
  }, [invoice]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const handleCustomerSelect = (customer) => {
    if (customer) {
      setFormData(prev => ({
        ...prev,
        customer_name: customer.name,
        customer_email: customer.email,
        customer_address: customer.address
      }));
    }
  };

  const handleLineItemChange = (index, field, value) => {
    const newItems = [...formData.line_items];
    newItems[index] = { ...newItems[index], [field]: value };
    
    // Calculate amount when quantity or unit_price changes
    if (field === 'quantity' || field === 'unit_price') {
      const quantity = parseFloat(field === 'quantity' ? value : newItems[index].quantity) || 0;
      const unitPrice = parseFloat(field === 'unit_price' ? value : newItems[index].unit_price) || 0;
      newItems[index].amount = quantity * unitPrice;
    }
    
    setFormData(prev => ({ ...prev, line_items: newItems }));
  };

  const addLineItem = () => {
    setFormData(prev => ({
      ...prev,
      line_items: [...prev.line_items, { description: '', quantity: 1, unit_price: '', amount: 0 }]
    }));
  };

  const removeLineItem = (index) => {
    if (formData.line_items.length > 1) {
      const newItems = formData.line_items.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, line_items: newItems }));
    }
  };

  const calculateTotals = () => {
    const subtotal = formData.line_items.reduce((sum, item) => sum + (item.amount || 0), 0);
    const taxAmount = subtotal * (formData.tax_rate / 100);
    const total = subtotal + taxAmount;
    
    return { subtotal, taxAmount, total };
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Customer validation
    if (!formData.customer_name.trim()) newErrors.customer_name = 'Customer name is required';
    if (!formData.customer_email.trim()) newErrors.customer_email = 'Customer email is required';
    if (!formData.invoice_number.trim()) newErrors.invoice_number = 'Invoice number is required';
    if (!formData.invoice_date) newErrors.invoice_date = 'Invoice date is required';
    if (!formData.due_date) newErrors.due_date = 'Due date is required';
    
    // Line items validation
    formData.line_items.forEach((item, index) => {
      if (!item.description.trim()) {
        newErrors[`line_${index}_description`] = 'Description is required';
      }
      if (!item.quantity || item.quantity <= 0) {
        newErrors[`line_${index}_quantity`] = 'Quantity must be greater than 0';
      }
      if (!item.unit_price || item.unit_price <= 0) {
        newErrors[`line_${index}_unit_price`] = 'Unit price must be greater than 0';
      }
    });
    
    // Check if at least one line item has valid data
    const hasValidItems = formData.line_items.some(item => 
      item.description.trim() && item.quantity > 0 && item.unit_price > 0
    );
    
    if (!hasValidItems) {
      newErrors.line_items = 'At least one valid line item is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }
    
    setSaving(true);
    try {
      const { subtotal, taxAmount, total } = calculateTotals();
      
      const invoiceData = {
        ...formData,
        subtotal,
        tax_amount: taxAmount,
        total_amount: total,
        amount: total, // For compatibility with existing structure
        status: 'pending',
        created_by: user?.id || 'current_user',
        created_at: new Date().toISOString()
      };

      
      // Simulate API call - replace with actual API when ready
      setTimeout(() => {
        onSave(invoiceData);
        onClose();
        setSaving(false);
      }, 1000);
      
    } catch (error) {
      console.error('❌ Error saving invoice:', error);
      setErrors({ submit: error.message || 'Failed to save invoice' });
      setSaving(false);
    }
  };

  const { subtotal, taxAmount, total } = calculateTotals();

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      fullScreen={typeof window !== 'undefined' ? window.matchMedia('(max-width:600px)').matches : false}
      PaperProps={{ sx: { minHeight: '80vh' } }}
      aria-labelledby="invoice-dialog-title"
      aria-describedby="invoice-dialog-content"
    >
      <DialogTitle 
        id="invoice-dialog-title"
        sx={{ display: 'flex', alignItems: 'center', gap: 2 }}
      >
        <Receipt />
        <Typography variant="h6">
          {invoice ? 'Edit Invoice' : 'Create New Invoice'}
        </Typography>
        <Chip
          label={`Total: $${total.toFixed(2)}`}
          color="primary"
          variant="outlined"
        />
      </DialogTitle>

      <DialogContent id="invoice-dialog-content">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Customer Information */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Person />
              Customer Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <Autocomplete
                  options={customers}
                  getOptionLabel={(option) => option.name}
                  onChange={(e, newValue) => handleCustomerSelect(newValue)}
                  isOptionEqualToValue={(option, value) => option.id === value?.id}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Customer Name"
                      value={formData.customer_name}
                      onChange={(e) => handleInputChange('customer_name', e.target.value)}
                      error={!!errors.customer_name}
                      helperText={errors.customer_name}
                      placeholder="Start typing to search or enter new customer..."
                    />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Customer Email"
                  type="email"
                  value={formData.customer_email}
                  onChange={(e) => handleInputChange('customer_email', e.target.value)}
                  fullWidth
                  error={!!errors.customer_email}
                  helperText={errors.customer_email}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Customer Address"
                  value={formData.customer_address}
                  onChange={(e) => handleInputChange('customer_address', e.target.value)}
                  fullWidth
                  multiline
                  rows={1}
                />
              </Grid>
            </Grid>
          </Paper>

          {/* Invoice Details */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Invoice Details
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  label="Invoice Number"
                  value={formData.invoice_number}
                  onChange={(e) => handleInputChange('invoice_number', e.target.value)}
                  fullWidth
                  error={!!errors.invoice_number}
                  helperText={errors.invoice_number}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  label="Invoice Date"
                  type="date"
                  value={formData.invoice_date}
                  onChange={(e) => handleInputChange('invoice_date', e.target.value)}
                  fullWidth
                  error={!!errors.invoice_date}
                  helperText={errors.invoice_date}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  label="Due Date"
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => handleInputChange('due_date', e.target.value)}
                  fullWidth
                  error={!!errors.due_date}
                  helperText={errors.due_date}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  select
                  label="Payment Terms"
                  value={formData.payment_terms}
                  onChange={(e) => handleInputChange('payment_terms', e.target.value)}
                  fullWidth
                >
                  <MenuItem value="15">Net 15</MenuItem>
                  <MenuItem value="30">Net 30</MenuItem>
                  <MenuItem value="45">Net 45</MenuItem>
                  <MenuItem value="60">Net 60</MenuItem>
                  <MenuItem value="0">Due on Receipt</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  select
                  label="Currency"
                  value={formData.currency}
                  onChange={(e) => handleInputChange('currency', e.target.value)}
                  fullWidth
                >
                  <MenuItem value="USD">USD - US Dollar</MenuItem>
                  <MenuItem value="EUR">EUR - Euro</MenuItem>
                  <MenuItem value="GBP">GBP - British Pound</MenuItem>
                  <MenuItem value="CAD">CAD - Canadian Dollar</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="Tax Rate (%)"
                  type="number"
                  value={formData.tax_rate}
                  onChange={(e) => handleInputChange('tax_rate', parseFloat(e.target.value) || 0)}
                  fullWidth
                  inputProps={{ min: 0, max: 100, step: 0.1 }}
                />
              </Grid>
            </Grid>
          </Paper>

          {/* Line Items */}
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Line Items
              </Typography>
              <Button
                startIcon={<Add />}
                onClick={addLineItem}
                variant="outlined"
                size="small"
              >
                Add Item
              </Button>
            </Box>

            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Description</TableCell>
                    <TableCell align="center">Qty</TableCell>
                    <TableCell align="right">Unit Price</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {formData.line_items.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <TextField
                          value={item.description}
                          onChange={(e) => handleLineItemChange(index, 'description', e.target.value)}
                          placeholder="Item description..."
                          size="small"
                          fullWidth
                          error={!!errors[`line_${index}_description`]}
                          helperText={errors[`line_${index}_description`]}
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          type="number"
                          value={item.quantity}
                          onChange={(e) => handleLineItemChange(index, 'quantity', e.target.value)}
                          size="small"
                          sx={{ width: 80 }}
                          inputProps={{ min: 0, step: 1 }}
                          error={!!errors[`line_${index}_quantity`]}
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          type="number"
                          value={item.unit_price}
                          onChange={(e) => handleLineItemChange(index, 'unit_price', e.target.value)}
                          size="small"
                          sx={{ width: 100 }}
                          inputProps={{ min: 0, step: 0.01 }}
                          InputProps={{
                            startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
                          }}
                          error={!!errors[`line_${index}_unit_price`]}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          ${(item.amount || 0).toFixed(2)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          onClick={() => removeLineItem(index)}
                          disabled={formData.line_items.length <= 1}
                          size="small"
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {errors.line_items && (
              <Alert severity="error" sx={{ mt: 1 }}>
                {errors.line_items}
              </Alert>
            )}
          </Paper>

          {/* Totals */}
          <Paper sx={{ p: 2, bgcolor: 'primary.50' }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={8}>
                <TextField
                  label="Notes"
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  fullWidth
                  multiline
                  rows={3}
                  placeholder="Additional notes or payment instructions..."
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography>Subtotal:</Typography>
                    <Typography fontWeight="medium">${subtotal.toFixed(2)}</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography>Tax ({formData.tax_rate}%):</Typography>
                    <Typography fontWeight="medium">${taxAmount.toFixed(2)}</Typography>
                  </Box>
                  <Divider />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="h6">Total:</Typography>
                    <Typography variant="h6" color="primary.main">
                      ${total.toFixed(2)}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* General Errors */}
          {errors.submit && (
            <Alert severity="error">
              {errors.submit}
            </Alert>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button
          onClick={onClose}
          startIcon={<Cancel />}
          disabled={saving}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          startIcon={<Save />}
          disabled={saving}
          sx={{ minWidth: 120 }}
        >
          {saving ? 'Saving...' : 'Save Invoice'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default InvoiceForm;
