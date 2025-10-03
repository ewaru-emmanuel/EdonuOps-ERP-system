import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, FormControl, InputLabel, Select, MenuItem, Alert, Snackbar, Chip, Avatar, Divider,
  Stepper, Step, StepLabel, StepContent, Paper, List, ListItem, ListItemText, ListItemIcon,
  IconButton, Tooltip, CircularProgress
} from '@mui/material';
import {
  Add, AttachMoney, AccountBalance, Receipt, Payment, Business, ShoppingCart, 
  TrendingUp, TrendingDown, CheckCircle, Warning, Error, Info, Close
} from '@mui/icons-material';
import apiClient from '../../../services/apiClient';

const BusinessTransactionForm = ({ open, onClose, onSuccess }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [validation, setValidation] = useState({ valid: false, preview: null });

  // Load templates on component mount
  useEffect(() => {
    if (open) {
      loadTemplates();
    }
  }, [open]);

  const loadTemplates = async () => {
    try {
      const response = await apiClient.get('/api/finance/transactions/templates');
      if (response.success) {
        setTemplates(response.templates);
      }
    } catch (error) {
      console.error('Error loading templates:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load transaction templates',
        severity: 'error'
      });
    }
  };

  const handleTemplateSelect = (templateId) => {
    const template = templates[templateId];
    setSelectedTemplate(template);
    setFormData({ template_id: templateId });
    setActiveStep(1);
  };

  const handleInputChange = (field, value) => {
    const newFormData = { ...formData, [field]: value };
    setFormData(newFormData);
    
    // Auto-validate when all required fields are filled
    if (selectedTemplate) {
      const requiredFields = selectedTemplate.required_fields;
      const hasAllFields = requiredFields.every(field => newFormData[field] !== undefined && newFormData[field] !== '');
      
      if (hasAllFields) {
        validateTransaction(newFormData);
      } else {
        setValidation({ valid: false, preview: null });
      }
    }
  };

  const validateTransaction = async (data) => {
    try {
      const response = await apiClient.post('/api/finance/transactions/validate', data);
      if (response.success) {
        setValidation({
          valid: response.valid,
          preview: response.preview
        });
      }
    } catch (error) {
      console.error('Error validating transaction:', error);
      setValidation({ valid: false, preview: null });
    }
  };

  const handleSubmit = async () => {
    if (!validation.valid) {
      setSnackbar({
        open: true,
        message: 'Please fix validation errors before submitting',
        severity: 'error'
      });
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/api/finance/transactions/create', formData);
      if (response.success) {
        setSnackbar({
          open: true,
          message: response.message,
          severity: 'success'
        });
        onSuccess && onSuccess(response.transaction);
        handleClose();
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Failed to create transaction',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error creating transaction:', error);
      setSnackbar({
        open: true,
        message: 'Failed to create transaction',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setActiveStep(0);
    setSelectedTemplate(null);
    setFormData({});
    setValidation({ valid: false, preview: null });
    onClose();
  };

  const getTemplateIcon = (templateId) => {
    const icons = {
      'cash_sales': <AttachMoney />,
      'bank_sales': <AccountBalance />,
      'expense_payment': <Payment />,
      'purchase': <ShoppingCart />,
      'loan_receipt': <Business />
    };
    return icons[templateId] || <Receipt />;
  };

  const getTemplateColor = (templateId) => {
    const colors = {
      'cash_sales': 'success',
      'bank_sales': 'primary',
      'expense_payment': 'warning',
      'purchase': 'info',
      'loan_receipt': 'secondary'
    };
    return colors[templateId] || 'default';
  };

  const renderTemplateSelection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Choose Transaction Type
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Select the type of business transaction you want to record
      </Typography>
      
      <Grid container spacing={2}>
        {Object.entries(templates).map(([templateId, template]) => (
          <Grid item xs={12} sm={6} md={4} key={templateId}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': { 
                  transform: 'translateY(-2px)',
                  boxShadow: 3
                }
              }}
              onClick={() => handleTemplateSelect(templateId)}
            >
              <CardContent sx={{ textAlign: 'center', p: 3 }}>
                <Avatar 
                  sx={{ 
                    bgcolor: `${getTemplateColor(templateId)}.main`,
                    width: 56,
                    height: 56,
                    mx: 'auto',
                    mb: 2
                  }}
                >
                  {getTemplateIcon(templateId)}
                </Avatar>
                <Typography variant="h6" gutterBottom>
                  {template.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {template.description}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Chip 
                    label={`${template.required_fields.length} fields`}
                    size="small"
                    color={getTemplateColor(templateId)}
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderTransactionForm = () => {
    if (!selectedTemplate) return null;

    const requiredFields = selectedTemplate.required_fields;
    
    return (
      <Box>
        <Box display="flex" alignItems="center" gap={2} mb={3}>
          <Avatar sx={{ bgcolor: `${getTemplateColor(selectedTemplate.id)}.main` }}>
            {getTemplateIcon(selectedTemplate.id)}
          </Avatar>
          <Box>
            <Typography variant="h6">
              {selectedTemplate.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {selectedTemplate.description}
            </Typography>
          </Box>
        </Box>

        <Grid container spacing={2}>
          {requiredFields.map((field) => {
            if (field === 'amount') {
              return (
                <Grid item xs={12} sm={6} key={field}>
                  <TextField
                    label="Amount"
                    type="number"
                    value={formData[field] || ''}
                    onChange={(e) => handleInputChange(field, parseFloat(e.target.value) || 0)}
                    fullWidth
                    required
                    InputProps={{
                      startAdornment: <AttachMoney />
                    }}
                    helperText="Enter the transaction amount"
                  />
                </Grid>
              );
            }
            
            if (field === 'description') {
              return (
                <Grid item xs={12} key={field}>
                  <TextField
                    label="Description"
                    value={formData[field] || ''}
                    onChange={(e) => handleInputChange(field, e.target.value)}
                    fullWidth
                    required
                    multiline
                    rows={2}
                    helperText="Describe what this transaction is for"
                  />
                </Grid>
              );
            }
            
            if (field === 'payment_method') {
              return (
                <Grid item xs={12} sm={6} key={field}>
                  <FormControl fullWidth required>
                    <InputLabel>Payment Method</InputLabel>
                    <Select
                      value={formData[field] || ''}
                      onChange={(e) => handleInputChange(field, e.target.value)}
                      label="Payment Method"
                    >
                      <MenuItem value="cash">💵 Cash</MenuItem>
                      <MenuItem value="bank">🏦 Bank Transfer</MenuItem>
                      <MenuItem value="wire">🌐 Wire Transfer</MenuItem>
                      <MenuItem value="credit_card">💳 Credit Card</MenuItem>
                      <MenuItem value="check">📝 Check</MenuItem>
                      <MenuItem value="digital">📱 Digital Payment</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              );
            }
            
            if (field === 'purchase_type') {
              return (
                <Grid item xs={12} sm={6} key={field}>
                  <FormControl fullWidth required>
                    <InputLabel>Purchase Type</InputLabel>
                    <Select
                      value={formData[field] || ''}
                      onChange={(e) => handleInputChange(field, e.target.value)}
                      label="Purchase Type"
                    >
                      <MenuItem value="inventory">📦 Inventory</MenuItem>
                      <MenuItem value="expense">💼 Operating Expense</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              );
            }
            
            return null;
          })}
        </Grid>

        {/* Validation Preview */}
        {validation.preview && (
          <Paper sx={{ mt: 3, p: 2, bgcolor: validation.valid ? 'success.light' : 'error.light' }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              {validation.valid ? <CheckCircle color="success" /> : <Error color="error" />}
              <Typography variant="h6">
                {validation.valid ? 'Transaction Preview' : 'Validation Error'}
              </Typography>
            </Box>
            
            {validation.valid ? (
              <Box>
                <Typography variant="body1" gutterBottom>
                  <strong>Description:</strong> {validation.preview.description}
                </Typography>
                <Typography variant="body1" gutterBottom>
                  <strong>Payment Method:</strong> {validation.preview.payment_method}
                </Typography>
                <Typography variant="body1" gutterBottom>
                  <strong>Total Amount:</strong> ${validation.preview.total_debits}
                </Typography>
                <Typography variant="body1" gutterBottom>
                  <strong>Balanced:</strong> {validation.preview.is_balanced ? '✅ Yes' : '❌ No'}
                </Typography>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="h6" gutterBottom>
                  Journal Lines:
                </Typography>
                <List dense>
                  {validation.preview.lines.map((line, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        {line.debit_amount > 0 ? 
                          <TrendingUp color="success" /> : 
                          <TrendingDown color="error" />
                        }
                      </ListItemIcon>
                      <ListItemText
                        primary={line.account_name}
                        secondary={`${line.debit_amount > 0 ? 'Debit' : 'Credit'}: $${line.debit_amount || line.credit_amount}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            ) : (
              <Typography variant="body1">
                Please fill in all required fields correctly.
              </Typography>
            )}
          </Paper>
        )}
      </Box>
    );
  };

  const steps = [
    {
      label: 'Select Transaction Type',
      content: renderTemplateSelection()
    },
    {
      label: 'Enter Details',
      content: renderTransactionForm()
    }
  ];

  return (
    <>
      <Dialog 
        open={open} 
        onClose={handleClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h5">
              Record Business Transaction
            </Typography>
            <IconButton onClick={handleClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Stepper activeStep={activeStep} orientation="vertical">
            {steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel>{step.label}</StepLabel>
                <StepContent>
                  {step.content}
                  <Box sx={{ mb: 2, mt: 2 }}>
                    <div>
                      {index === 0 && (
                        <Button
                          variant="contained"
                          onClick={() => setActiveStep(1)}
                          sx={{ mt: 1, mr: 1 }}
                          disabled={!selectedTemplate}
                        >
                          Continue
                        </Button>
                      )}
                      {index === 1 && (
                        <Box>
                          <Button
                            variant="contained"
                            onClick={handleSubmit}
                            disabled={!validation.valid || loading}
                            sx={{ mt: 1, mr: 1 }}
                          >
                            {loading ? <CircularProgress size={20} /> : 'Create Transaction'}
                          </Button>
                          <Button
                            onClick={() => setActiveStep(0)}
                            sx={{ mt: 1, mr: 1 }}
                          >
                            Back
                          </Button>
                        </Box>
                      )}
                    </div>
                  </Box>
                </StepContent>
              </Step>
            ))}
          </Stepper>
        </DialogContent>
      </Dialog>

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
    </>
  );
};

export default BusinessTransactionForm;

