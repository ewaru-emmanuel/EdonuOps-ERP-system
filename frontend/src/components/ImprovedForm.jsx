import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Typography,
  Grid,
  FormControlLabel,
  Switch,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Close as CloseIcon,
  Save as SaveIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { getERPApiService } from '../services/erpApiService';

const ImprovedForm = ({
  open,
  onClose,
  onSubmit,
  onSave, // Support both onSubmit and onSave for backward compatibility
  data = null, // null for create, object for edit
  type = 'generic',
  title = 'Form',
  loading = false,
  error = null
}) => {
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [dynamicOptions, setDynamicOptions] = useState({});

  // Initialize form data when component mounts or data changes
  useEffect(() => {
    if (data) {
      // Pre-fill form with existing data for editing
      setFormData({ ...data });
    } else {
      // Reset form for creating new item
      setFormData(getDefaultFormData(type));
    }
    setErrors({});
    
    // Fetch dynamic options for form fields
    fetchDynamicOptions();
  }, [data, type]);

  const fetchDynamicOptions = async () => {
    const fields = getFormFields(type);
    const apiService = getERPApiService();
    
    for (const field of fields) {
      if (field.apiEndpoint) {
        try {
          const response = await apiService.get(field.apiEndpoint);
          setDynamicOptions(prev => ({
            ...prev,
            [field.name]: response.data || response
          }));
        } catch (error) {
          console.error(`Error fetching options for ${field.name}:`, error);
        }
      }
    }
  };

  const getDefaultFormData = (type) => {
    switch (type) {
      case 'employee':
        return {
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          position: '',
          department_id: null,
          salary: '',
          hire_date: '',
          status: 'active'
        };
      case 'product':
        return {
          name: '',
          sku: '',
          description: '',
          category_id: '',
          unit: 'pcs',
          standard_cost: '',
          current_cost: '',
          min_stock: '',
          max_stock: '',
          is_active: true
        };
      case 'category':
        return {
          name: '',
          description: '',
          parent_id: '',
          is_active: true
        };
      case 'warehouse':
        return {
          name: '',
          location: '',
          capacity: '',
          is_active: true
        };
      case 'contact':
        return {
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          company: '',
          type: 'customer',
          status: 'active'
        };
      case 'lead':
        return {
          first_name: '',
          last_name: '',
          email: '',
          phone: '',
          company: '',
          source: 'website',
          status: 'new'
        };
      case 'opportunity':
        return {
          name: '',
          contact_id: '',
          amount: '',
          stage: 'prospecting',
          probability: '',
          expected_close_date: ''
        };
      case 'account':
        return {
          code: '',
          name: '',
          type: 'asset',
          parent_id: '',
          is_active: true
        };
      case 'journal-entry':
        return {
          entry_date: new Date().toISOString().split('T')[0],
          reference: '',
          description: '',
          status: 'draft',
          total_debit: '',
          total_credit: ''
        };
      case 'order':
        return {
          customer_name: '',
          customer_email: '',
          total_amount: '',
          status: 'Pending'
        };
      case 'store_config':
        return {
          store_name: '',
          theme: 'default',
          primary_color: '#1976d2',
          logo_url: '',
          description: ''
        };
      case 'payment_config':
        return {
          payment_gateway: 'stripe',
          api_key: '',
          webhook_url: '',
          currency: 'USD'
        };
      case 'prediction':
        return {
          title: '',
          description: '',
          prediction_type: '',
          accuracy: 0,
          confidence_score: 0,
          status: 'Active'
        };
      case 'insight':
        return {
          title: '',
          description: '',
          insight_type: '',
          impact_score: 0,
          category: '',
          status: 'Active'
        };
      case 'recommendation':
        return {
          title: '',
          description: '',
          recommendation_type: '',
          priority: 'Medium',
          implementation_status: 'Pending'
        };
      case 'environmental':
        return {
          metric_name: '',
          value: 0,
          unit: '',
          category: '',
          reporting_period: '',
          status: 'Active'
        };
      case 'social':
        return {
          metric_name: '',
          value: 0,
          unit: '',
          category: '',
          reporting_period: '',
          status: 'Active'
        };
      case 'governance':
        return {
          metric_name: '',
          value: 0,
          unit: '',
          category: '',
          reporting_period: '',
          status: 'Active'
        };
      case 'report':
        return {
          report_title: '',
          report_type: '',
          reporting_period: '',
          esg_rating: '',
          status: 'Draft'
        };
      default:
        return {};
    }
  };

  const getFormFields = (type) => {
    switch (type) {
      case 'employee':
        return [
          { name: 'first_name', label: 'First Name', type: 'text', required: true },
          { name: 'last_name', label: 'Last Name', type: 'text', required: true },
          { name: 'email', label: 'Email', type: 'email', required: true },
          { name: 'phone', label: 'Phone', type: 'tel' },
          { name: 'position', label: 'Position', type: 'text', required: true },
          { name: 'department_id', label: 'Department', type: 'select', options: [], apiEndpoint: '/api/hcm/departments', optionValue: 'id', optionLabel: 'name' },
          { name: 'salary', label: 'Salary', type: 'number' },
          { name: 'hire_date', label: 'Hire Date', type: 'date' },
          { name: 'status', label: 'Status', type: 'select', options: ['active', 'inactive', 'terminated'] }
        ];
      case 'product':
        return [
          { name: 'name', label: 'Product Name', type: 'text', required: true },
          { name: 'description', label: 'Description', type: 'textarea' },
          { name: 'price', label: 'Price', type: 'number', required: true },
          { name: 'stock_quantity', label: 'Stock Quantity', type: 'number' },
          { name: 'category', label: 'Category', type: 'text' },
          { name: 'status', label: 'Status', type: 'select', options: ['Active', 'Inactive'] }
        ];
      case 'category':
        return [
          { name: 'name', label: 'Category Name', type: 'text', required: true },
          { name: 'description', label: 'Description', type: 'textarea' },
          { name: 'parent_id', label: 'Parent Category', type: 'select', options: [] } // Will be populated from API
        ];
      case 'warehouse':
        return [
          { name: 'name', label: 'Warehouse Name', type: 'text', required: true },
          { name: 'location', label: 'Location', type: 'text' },
          { name: 'capacity', label: 'Capacity', type: 'number' }
        ];
      case 'contact':
        return [
          { name: 'first_name', label: 'First Name', type: 'text', required: true },
          { name: 'last_name', label: 'Last Name', type: 'text', required: true },
          { name: 'email', label: 'Email', type: 'email' },
          { name: 'phone', label: 'Phone', type: 'tel' },
          { name: 'company', label: 'Company', type: 'text' },
          { name: 'type', label: 'Type', type: 'select', options: ['customer', 'vendor', 'partner', 'prospect'] },
          { name: 'status', label: 'Status', type: 'select', options: ['active', 'inactive'] }
        ];
      case 'lead':
        return [
          { name: 'first_name', label: 'First Name', type: 'text', required: true },
          { name: 'last_name', label: 'Last Name', type: 'text', required: true },
          { name: 'email', label: 'Email', type: 'email' },
          { name: 'phone', label: 'Phone', type: 'tel' },
          { name: 'company', label: 'Company', type: 'text' },
          { name: 'source', label: 'Source', type: 'select', options: ['website', 'referral', 'trade_show', 'social_media', 'cold_call'] },
          { name: 'status', label: 'Status', type: 'select', options: ['new', 'qualified', 'proposal', 'negotiation', 'closed'] }
        ];
      case 'opportunity':
        return [
          { name: 'name', label: 'Opportunity Name', type: 'text', required: true },
          { name: 'contact_id', label: 'Contact ID', type: 'number' },
          { name: 'amount', label: 'Amount', type: 'number' },
          { name: 'stage', label: 'Stage', type: 'select', options: ['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost'] },
          { name: 'probability', label: 'Probability (%)', type: 'number' },
          { name: 'expected_close_date', label: 'Expected Close Date', type: 'date' }
        ];
      case 'account':
        return [
          { name: 'code', label: 'Account Code', type: 'text', required: true },
          { name: 'name', label: 'Account Name', type: 'text', required: true },
          { name: 'type', label: 'Account Type', type: 'select', options: ['asset', 'liability', 'equity', 'revenue', 'expense'] },
          { name: 'parent_id', label: 'Parent Account', type: 'select', options: [] } // Will be populated from API
        ];
      case 'journal-entry':
        return [
          { name: 'entry_date', label: 'Entry Date', type: 'date', required: true },
          { name: 'reference', label: 'Reference', type: 'text' },
          { name: 'description', label: 'Description', type: 'textarea' },
          { name: 'status', label: 'Status', type: 'select', options: ['draft', 'posted'] },
          { name: 'total_debit', label: 'Total Debit', type: 'number' },
          { name: 'total_credit', label: 'Total Credit', type: 'number' }
        ];
      case 'order':
        return [
          { name: 'customer_name', label: 'Customer Name', type: 'text', required: true },
          { name: 'customer_email', label: 'Customer Email', type: 'email' },
          { name: 'total_amount', label: 'Total Amount', type: 'number', required: true },
          { name: 'status', label: 'Status', type: 'select', options: ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'] }
        ];
      case 'store_config':
        return [
          { name: 'store_name', label: 'Store Name', type: 'text', required: true },
          { name: 'theme', label: 'Theme', type: 'select', options: ['default', 'modern', 'classic', 'minimal'] },
          { name: 'primary_color', label: 'Primary Color', type: 'text' },
          { name: 'logo_url', label: 'Logo URL', type: 'text' },
          { name: 'description', label: 'Store Description', type: 'textarea' }
        ];
      case 'payment_config':
        return [
          { name: 'payment_gateway', label: 'Payment Gateway', type: 'select', options: ['stripe', 'paypal', 'square', 'authorize_net'] },
          { name: 'api_key', label: 'API Key', type: 'text' },
          { name: 'webhook_url', label: 'Webhook URL', type: 'text' },
          { name: 'currency', label: 'Currency', type: 'select', options: ['USD', 'EUR', 'GBP', 'CAD', 'AUD'] }
        ];
      case 'prediction':
        return [
          { name: 'title', label: 'Title', type: 'text', required: true },
          { name: 'description', label: 'Description', type: 'textarea' },
          { name: 'prediction_type', label: 'Prediction Type', type: 'select', options: ['Sales', 'Inventory', 'Customer', 'Financial', 'Operational'] },
          { name: 'accuracy', label: 'Accuracy (%)', type: 'number' },
          { name: 'confidence_score', label: 'Confidence Score', type: 'number' },
          { name: 'status', label: 'Status', type: 'select', options: ['Active', 'Inactive', 'Archived'] }
        ];
      case 'insight':
        return [
          { name: 'title', label: 'Title', type: 'text', required: true },
          { name: 'description', label: 'Description', type: 'textarea' },
          { name: 'insight_type', label: 'Insight Type', type: 'select', options: ['Trend Analysis', 'Anomaly Detection', 'Risk Analysis', 'Opportunity'] },
          { name: 'impact_score', label: 'Impact Score', type: 'number' },
          { name: 'category', label: 'Category', type: 'select', options: ['Finance', 'Sales', 'Operations', 'Customer', 'Product'] },
          { name: 'status', label: 'Status', type: 'select', options: ['Active', 'Reviewed', 'Implemented'] }
        ];
      case 'recommendation':
        return [
          { name: 'title', label: 'Title', type: 'text', required: true },
          { name: 'description', label: 'Description', type: 'textarea' },
          { name: 'recommendation_type', label: 'Recommendation Type', type: 'select', options: ['Process Improvement', 'Cost Reduction', 'Revenue Growth', 'Risk Mitigation'] },
          { name: 'priority', label: 'Priority', type: 'select', options: ['Low', 'Medium', 'High', 'Critical'] },
          { name: 'implementation_status', label: 'Implementation Status', type: 'select', options: ['Pending', 'In Progress', 'Completed', 'On Hold'] }
        ];
      case 'environmental':
      case 'social':
      case 'governance':
        return [
          { name: 'metric_name', label: 'Metric Name', type: 'text', required: true },
          { name: 'value', label: 'Value', type: 'number', required: true },
          { name: 'unit', label: 'Unit', type: 'text', required: true },
          { name: 'category', label: 'Category', type: 'text' },
          { name: 'reporting_period', label: 'Reporting Period', type: 'text' },
          { name: 'status', label: 'Status', type: 'select', options: ['Active', 'Inactive', 'Archived'] }
        ];
      case 'report':
        return [
          { name: 'report_title', label: 'Report Title', type: 'text', required: true },
          { name: 'report_type', label: 'Report Type', type: 'select', options: ['Annual', 'Quarterly', 'Monthly', 'Special'] },
          { name: 'reporting_period', label: 'Reporting Period', type: 'text' },
          { name: 'esg_rating', label: 'ESG Rating', type: 'select', options: ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D'] },
          { name: 'status', label: 'Status', type: 'select', options: ['Draft', 'In Review', 'Published', 'Archived'] }
        ];
      default:
        return [];
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    const fields = getFormFields(type);
    
    fields.forEach(field => {
      if (field.required && !formData[field.name]) {
        newErrors[field.name] = `${field.label} is required`;
      }
      
      if (field.type === 'email' && formData[field.name]) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData[field.name])) {
          newErrors[field.name] = 'Invalid email format';
        }
      }
      
      if (field.type === 'number' && formData[field.name]) {
        if (isNaN(formData[field.name]) || formData[field.name] < 0) {
          newErrors[field.name] = 'Must be a positive number';
        }
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }
    
    try {
      const submitFunction = onSubmit || onSave; // Use onSubmit if available, otherwise fallback to onSave
      if (submitFunction) {
        await submitFunction(formData);
        onClose();
      } else {
        console.error('No submit function provided');
      }
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  const renderField = (field) => {
    const value = formData[field.name] || '';
    const error = errors[field.name];
    
    switch (field.type) {
      case 'textarea':
        return (
          <TextField
            key={field.name}
            fullWidth
            label={field.label}
            value={value}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            multiline
            rows={3}
            error={!!error}
            helperText={error}
            margin="normal"
          />
        );
      
      case 'select':
        const options = field.apiEndpoint ? (dynamicOptions[field.name] || []) : field.options;
        return (
          <FormControl key={field.name} fullWidth margin="normal" error={!!error}>
            <InputLabel>{field.label}</InputLabel>
            <Select
              value={value}
              label={field.label}
              onChange={(e) => handleInputChange(field.name, e.target.value)}
            >
              {options.map((option) => {
                const optionValue = field.optionValue ? option[field.optionValue] : option;
                const optionLabel = field.optionLabel ? option[field.optionLabel] : option;
                return (
                  <MenuItem key={optionValue} value={optionValue}>
                    {optionLabel}
                  </MenuItem>
                );
              })}
            </Select>
            {error && <Typography color="error" variant="caption">{error}</Typography>}
          </FormControl>
        );
      
      case 'date':
        return (
          <TextField
            key={field.name}
            fullWidth
            label={field.label}
            type="date"
            value={value}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            error={!!error}
            helperText={error}
            margin="normal"
            InputLabelProps={{ shrink: true }}
          />
        );
      
      case 'number':
        return (
          <TextField
            key={field.name}
            fullWidth
            label={field.label}
            type="number"
            value={value}
            onChange={(e) => handleInputChange(field.name, parseFloat(e.target.value) || '')}
            error={!!error}
            helperText={error}
            margin="normal"
          />
        );
      
      default:
        return (
          <TextField
            key={field.name}
            fullWidth
            label={field.label}
            type={field.type}
            value={value}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            error={!!error}
            helperText={error}
            margin="normal"
          />
        );
    }
  };

  const renderSwitchField = (field) => {
    return (
      <FormControlLabel
        key={field.name}
        control={
          <Switch
            checked={formData[field.name] || false}
            onChange={(e) => handleInputChange(field.name, e.target.checked)}
          />
        }
        label={field.label}
        sx={{ mt: 2 }}
      />
    );
  };

  const getSwitchFields = (type) => {
    switch (type) {
      case 'product':
      case 'category':
      case 'warehouse':
        return ['is_active'];
      default:
        return [];
    }
  };

  const handleClose = (event, reason) => {
    // Prevent closing when backdrop is clicked, but allow other close methods
    if (reason === 'backdropClick') {
      return;
    }
    onClose();
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      aria-labelledby="form-dialog-title"
      aria-describedby="form-dialog-description"
      disableEscapeKeyDown={loading}
    >
      <DialogTitle id="form-dialog-title">
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            {data ? `Edit ${title}` : `Add New ${title}`}
          </Typography>
          <IconButton
            onClick={onClose}
            disabled={loading}
            aria-label="close"
            size="small"
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        <Box component="form" id="form-dialog-description" noValidate>
          <Grid container spacing={2}>
            {getFormFields(type).map((field) => (
              <Grid item xs={12} sm={field.gridSize || 6} key={field.name}>
                {field.type === 'switch' ? renderSwitchField(field) : renderField(field)}
              </Grid>
            ))}
          </Grid>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button 
          onClick={onClose} 
          disabled={loading}
          aria-label="cancel form"
        >
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={loading}
          startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
          aria-label="save form"
        >
          {loading ? 'Saving...' : (data ? 'Update' : 'Save')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ImprovedForm;
