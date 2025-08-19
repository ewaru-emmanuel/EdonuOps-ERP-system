import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Box,
  Typography,
  Alert,
  CircularProgress
} from '@mui/material';
import { Close as CloseIcon, Save as SaveIcon } from '@mui/icons-material';

// Generic Form Dialog Component
export const FormDialog = ({ 
  open, 
  onClose, 
  title, 
  children, 
  onSave, 
  loading = false,
  maxWidth = 'md'
}) => {
  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth={maxWidth} 
      fullWidth
      aria-labelledby="form-dialog-title"
      aria-describedby="form-dialog-content"
    >
      <DialogTitle id="form-dialog-title">
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">{title}</Typography>
          <Button 
            onClick={onClose} 
            color="inherit"
            aria-label="close dialog"
          >
            <CloseIcon />
          </Button>
        </Box>
      </DialogTitle>
      <DialogContent id="form-dialog-content">
        {children}
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
          onClick={onSave} 
          variant="contained" 
          startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
          disabled={loading}
          aria-label="save form"
        >
          {loading ? 'Saving...' : 'Save'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Finance Forms
export const AccountForm = ({ open, onClose, onSave, editData = null }) => {
  const [formData, setFormData] = useState({
    name: editData?.name || '',
    accountNumber: editData?.accountNumber || '',
    type: editData?.type || 'Asset',
    balance: editData?.balance || '',
    description: editData?.description || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    onSave(formData);
    setLoading(false);
    onClose();
  };

  return (
    <FormDialog 
      open={open} 
      onClose={onClose} 
      title={editData ? 'Edit Account' : 'Add New Account'}
      onSave={handleSave}
      loading={loading}
    >
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Account Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Account Number"
            value={formData.accountNumber}
            onChange={(e) => setFormData({...formData, accountNumber: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Account Type</InputLabel>
            <Select
              value={formData.type}
              onChange={(e) => setFormData({...formData, type: e.target.value})}
              label="Account Type"
            >
              <MenuItem value="Asset">Asset</MenuItem>
              <MenuItem value="Liability">Liability</MenuItem>
              <MenuItem value="Equity">Equity</MenuItem>
              <MenuItem value="Revenue">Revenue</MenuItem>
              <MenuItem value="Expense">Expense</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Balance"
            type="number"
            value={formData.balance}
            onChange={(e) => setFormData({...formData, balance: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
          />
        </Grid>
      </Grid>
    </FormDialog>
  );
};

// Inventory Forms
export const ProductForm = ({ open, onClose, onSave, editData = null }) => {
  const [formData, setFormData] = useState({
    name: editData?.name || '',
    sku: editData?.sku || '',
    category: editData?.category_name || '',
    price: editData?.current_cost || '',
    stock: editData?.current_stock || '',
    description: editData?.description || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    onSave(formData);
    setLoading(false);
    onClose();
  };

  return (
    <FormDialog 
      open={open} 
      onClose={onClose} 
      title={editData ? 'Edit Product' : 'Add New Product'}
      onSave={handleSave}
      loading={loading}
    >
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Product Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="SKU"
            value={formData.sku}
            onChange={(e) => setFormData({...formData, sku: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Category"
            value={formData.category}
            onChange={(e) => setFormData({...formData, category: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Price"
            type="number"
            value={formData.price}
            onChange={(e) => setFormData({...formData, price: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Stock Quantity"
            type="number"
            value={formData.stock}
            onChange={(e) => setFormData({...formData, stock: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
          />
        </Grid>
      </Grid>
    </FormDialog>
  );
};

export const CategoryForm = ({ open, onClose, onSave, editData = null }) => {
  const [formData, setFormData] = useState({
    name: editData?.name || '',
    description: editData?.description || '',
    color: editData?.color || '#1976d2'
  });
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    onSave(formData);
    setLoading(false);
    onClose();
  };

  return (
    <FormDialog 
      open={open} 
      onClose={onClose} 
      title={editData ? 'Edit Category' : 'Add New Category'}
      onSave={handleSave}
      loading={loading}
    >
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Category Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({...formData, description: e.target.value})}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Color"
            type="color"
            value={formData.color}
            onChange={(e) => setFormData({...formData, color: e.target.value})}
            InputLabelProps={{ shrink: true }}
          />
        </Grid>
      </Grid>
    </FormDialog>
  );
};

// CRM Forms
export const CustomerForm = ({ open, onClose, onSave, editData = null }) => {
  const [formData, setFormData] = useState({
    name: editData?.name || '',
    email: editData?.email || '',
    phone: editData?.phone || '',
    company: editData?.company || '',
    status: editData?.status || 'Active',
    type: editData?.type || 'SMB',
    location: editData?.location || '',
    notes: editData?.notes || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    onSave(formData);
    setLoading(false);
    onClose();
  };

  return (
    <FormDialog 
      open={open} 
      onClose={onClose} 
      title={editData ? 'Edit Customer' : 'Add New Customer'}
      onSave={handleSave}
      loading={loading}
    >
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Customer Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Phone"
            value={formData.phone}
            onChange={(e) => setFormData({...formData, phone: e.target.value})}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Company"
            value={formData.company}
            onChange={(e) => setFormData({...formData, company: e.target.value})}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={formData.status}
              onChange={(e) => setFormData({...formData, status: e.target.value})}
              label="Status"
            >
              <MenuItem value="Active">Active</MenuItem>
              <MenuItem value="Inactive">Inactive</MenuItem>
              <MenuItem value="Prospect">Prospect</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Type</InputLabel>
            <Select
              value={formData.type}
              onChange={(e) => setFormData({...formData, type: e.target.value})}
              label="Type"
            >
              <MenuItem value="SMB">SMB</MenuItem>
              <MenuItem value="Enterprise">Enterprise</MenuItem>
              <MenuItem value="Startup">Startup</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Location"
            value={formData.location}
            onChange={(e) => setFormData({...formData, location: e.target.value})}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Notes"
            multiline
            rows={3}
            value={formData.notes}
            onChange={(e) => setFormData({...formData, notes: e.target.value})}
          />
        </Grid>
      </Grid>
    </FormDialog>
  );
};

export const LeadForm = ({ open, onClose, onSave, editData = null }) => {
  const [formData, setFormData] = useState({
    name: editData?.name || '',
    email: editData?.email || '',
    status: editData?.status || 'New',
    source: editData?.source || 'Website',
    value: editData?.value || '',
    notes: editData?.notes || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    onSave(formData);
    setLoading(false);
    onClose();
  };

  return (
    <FormDialog 
      open={open} 
      onClose={onClose} 
      title={editData ? 'Edit Lead' : 'Add New Lead'}
      onSave={handleSave}
      loading={loading}
    >
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Lead Name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={formData.status}
              onChange={(e) => setFormData({...formData, status: e.target.value})}
              label="Status"
            >
              <MenuItem value="New">New</MenuItem>
              <MenuItem value="Qualified">Qualified</MenuItem>
              <MenuItem value="Proposal">Proposal</MenuItem>
              <MenuItem value="Negotiation">Negotiation</MenuItem>
              <MenuItem value="Closed">Closed</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Source</InputLabel>
            <Select
              value={formData.source}
              onChange={(e) => setFormData({...formData, source: e.target.value})}
              label="Source"
            >
              <MenuItem value="Website">Website</MenuItem>
              <MenuItem value="Referral">Referral</MenuItem>
              <MenuItem value="Trade Show">Trade Show</MenuItem>
              <MenuItem value="Social Media">Social Media</MenuItem>
              <MenuItem value="Cold Call">Cold Call</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Value"
            type="number"
            value={formData.value}
            onChange={(e) => setFormData({...formData, value: e.target.value})}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            label="Notes"
            multiline
            rows={3}
            value={formData.notes}
            onChange={(e) => setFormData({...formData, notes: e.target.value})}
          />
        </Grid>
      </Grid>
    </FormDialog>
  );
};

// HCM Forms
export const EmployeeForm = ({ open, onClose, onSave, editData = null }) => {
  const [formData, setFormData] = useState({
    firstName: editData?.firstName || '',
    lastName: editData?.lastName || '',
    email: editData?.email || '',
    phone: editData?.phone || '',
    department: editData?.department || '',
    position: editData?.position || '',
    hireDate: editData?.hireDate || '',
    salary: editData?.salary || ''
  });
  const [loading, setLoading] = useState(false);

  const handleSave = async () => {
    setLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    onSave(formData);
    setLoading(false);
    onClose();
  };

  return (
    <FormDialog 
      open={open} 
      onClose={onClose} 
      title={editData ? 'Edit Employee' : 'Add New Employee'}
      onSave={handleSave}
      loading={loading}
    >
      <Grid container spacing={2} sx={{ mt: 1 }}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="First Name"
            value={formData.firstName}
            onChange={(e) => setFormData({...formData, firstName: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Last Name"
            value={formData.lastName}
            onChange={(e) => setFormData({...formData, lastName: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Phone"
            value={formData.phone}
            onChange={(e) => setFormData({...formData, phone: e.target.value})}
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Department"
            value={formData.department}
            onChange={(e) => setFormData({...formData, department: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Position"
            value={formData.position}
            onChange={(e) => setFormData({...formData, position: e.target.value})}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Hire Date"
            type="date"
            value={formData.hireDate}
            onChange={(e) => setFormData({...formData, hireDate: e.target.value})}
            InputLabelProps={{ shrink: true }}
            required
          />
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Salary"
            type="number"
            value={formData.salary}
            onChange={(e) => setFormData({...formData, salary: e.target.value})}
            required
          />
        </Grid>
      </Grid>
    </FormDialog>
  );
};

// AI Error Component
export const AIErrorDialog = ({ open, onClose, feature }) => {
  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
      aria-labelledby="ai-error-dialog-title"
      aria-describedby="ai-error-dialog-content"
    >
      <DialogTitle id="ai-error-dialog-title">
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" color="error">
            AI Feature Unavailable
          </Typography>
          <Button 
            onClick={onClose} 
            color="inherit"
            aria-label="close dialog"
          >
            <CloseIcon />
          </Button>
        </Box>
      </DialogTitle>
      <DialogContent id="ai-error-dialog-content">
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
            Network Error
          </Typography>
          <Typography variant="body2">
            Unable to connect to AI services. Please check your internet connection and try again.
          </Typography>
        </Alert>
        <Typography variant="body2" color="text.secondary">
          The {feature} feature requires an active internet connection and valid API credentials.
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button 
          onClick={onClose} 
          variant="contained"
          aria-label="close dialog"
        >
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Confirmation Dialog
export const ConfirmationDialog = ({ open, onClose, onConfirm, title, message, loading = false }) => {
  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="sm" 
      fullWidth
      aria-labelledby="confirmation-dialog-title"
      aria-describedby="confirmation-dialog-content"
    >
      <DialogTitle id="confirmation-dialog-title">{title}</DialogTitle>
      <DialogContent id="confirmation-dialog-content">
        <Typography>{message}</Typography>
      </DialogContent>
      <DialogActions>
        <Button 
          onClick={onClose} 
          disabled={loading}
          aria-label="cancel action"
        >
          Cancel
        </Button>
        <Button 
          onClick={onConfirm} 
          variant="contained" 
          color="error"
          startIcon={loading ? <CircularProgress size={20} /> : null}
          disabled={loading}
          aria-label="confirm action"
        >
          {loading ? 'Deleting...' : 'Delete'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
