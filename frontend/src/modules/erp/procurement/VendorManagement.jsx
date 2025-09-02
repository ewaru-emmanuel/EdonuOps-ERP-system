import React, { useState } from 'react';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
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
  Snackbar,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Business,
  Email,
  Phone,
  LocationOn
} from '@mui/icons-material';

const VendorManagement = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [editingVendor, setEditingVendor] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [submitting, setSubmitting] = useState(false);
  
  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    tax_id: '',
    payment_terms: 'Net 30',
    credit_limit: '',
    is_active: true
  });

    // Real-time data hook for vendors
  const { data: vendors, loading: vendorsLoading, error: vendorsError, create, update, remove } = useRealTimeData('/api/procurement/vendors');

  const handleOpenDialog = (vendor = null) => {
    if (vendor) {
      setEditingVendor(vendor);
      setFormData(vendor);
    } else {
      setEditingVendor(null);
      setFormData({
        name: '',
        email: '',
        phone: '',
        address: '',
        tax_id: '',
        payment_terms: 'Net 30',
        credit_limit: '',
        is_active: true
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingVendor(null);
  };

  const handleSubmit = async () => {
    // Form validation
    if (!formData.name?.trim()) {
      showSnackbar('Vendor name is required', 'error');
      return;
    }
    if (!formData.email?.trim()) {
      showSnackbar('Email is required', 'error');
      return;
    }
    if (!formData.phone?.trim()) {
      showSnackbar('Phone is required', 'error');
      return;
    }

    setSubmitting(true);
    try {
      if (editingVendor) {
        await update(editingVendor.id, formData);
        showSnackbar('Vendor updated successfully!');
      } else {
        await create(formData);
        showSnackbar('Vendor created successfully!');
      }
      handleCloseDialog();
    } catch (error) {
      showSnackbar('Error saving vendor: ' + error.message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleDeleteVendor = async (vendorId) => {
    if (window.confirm('Are you sure you want to delete this vendor?')) {
      setSubmitting(true);
      try {
        await remove(vendorId);
        showSnackbar('Vendor deleted successfully!');
      } catch (error) {
        showSnackbar('Error deleting vendor: ' + error.message, 'error');
      } finally {
        setSubmitting(false);
      }
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>
          Vendor Management
        </Typography>
                 <Button
           variant="contained"
           startIcon={vendorsLoading ? <CircularProgress size={20} /> : <AddIcon />}
           onClick={() => handleOpenDialog()}
           disabled={vendorsLoading}
           sx={{ textTransform: 'none' }}
         >
           Add New Vendor
         </Button>
      </Box>

      {/* Vendor Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {vendors?.length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Vendors
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1, color: 'success.main' }}>
                {vendors?.filter(v => v.is_active).length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Vendors
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {vendors?.reduce((sum, v) => sum + (v.total_orders || 0), 0) || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Orders
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                ${(vendors?.reduce((sum, v) => sum + (v.total_spent || 0), 0) || 0).toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Spent
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Vendors Table */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
            Vendor List
          </Typography>
          
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>Vendor</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Contact</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Payment Terms</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Credit Limit</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Orders</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
                             <TableBody>
                 {vendorsLoading ? (
                   <TableRow>
                     <TableCell colSpan={7} align="center">
                       <Typography>Loading vendors...</Typography>
                     </TableCell>
                   </TableRow>
                 ) : vendorsError ? (
                   <TableRow>
                     <TableCell colSpan={7} align="center">
                       <Typography color="error">Error loading vendors: {vendorsError.message}</Typography>
                     </TableCell>
                   </TableRow>
                 ) : !vendors || vendors.length === 0 ? (
                   <TableRow>
                     <TableCell colSpan={7} align="center">
                       <Typography color="text.secondary">No vendors found. Add your first vendor to get started.</Typography>
                     </TableCell>
                   </TableRow>
                 ) : (
                   vendors.map((vendor) => (
                  <TableRow key={vendor.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          <Business />
                        </Avatar>
                        <Box>
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                            {vendor.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {vendor.tax_id}
                          </Typography>
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                          <Email fontSize="small" />
                          {vendor.email}
                        </Typography>
                        <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Phone fontSize="small" />
                          {vendor.phone}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={vendor.payment_terms} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        ${(Number(vendor.credit_limit) || 0).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={vendor.is_active ? 'Active' : 'Inactive'}
                        color={vendor.is_active ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {vendor.total_orders}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          ${(Number(vendor.total_spent) || 0).toLocaleString()}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                                                 <Tooltip title="View Details">
                           <IconButton size="small" color="primary" disabled={submitting} onClick={() => showSnackbar(`Viewing vendor details for ${vendor.name}`)}>
                             <ViewIcon />
                           </IconButton>
                         </Tooltip>
                         <Tooltip title="Edit Vendor">
                           <IconButton size="small" color="primary" disabled={submitting} onClick={() => handleOpenDialog(vendor)}>
                             <EditIcon />
                           </IconButton>
                         </Tooltip>
                         <Tooltip title="Delete Vendor">
                           <IconButton size="small" color="error" disabled={submitting} onClick={() => handleDeleteVendor(vendor.id)}>
                             <DeleteIcon />
                           </IconButton>
                         </Tooltip>
                      </Box>
                                         </TableCell>
                   </TableRow>
                 ))
                 )}
               </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Add/Edit Vendor Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingVendor ? 'Edit Vendor' : 'Add New Vendor'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Vendor Name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Phone"
                value={formData.phone}
                onChange={(e) => handleInputChange('phone', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tax ID"
                value={formData.tax_id}
                onChange={(e) => handleInputChange('tax_id', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Address"
                multiline
                rows={3}
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Payment Terms</InputLabel>
                <Select
                  value={formData.payment_terms}
                  label="Payment Terms"
                  onChange={(e) => handleInputChange('payment_terms', e.target.value)}
                >
                  <MenuItem value="Net 15">Net 15</MenuItem>
                  <MenuItem value="Net 30">Net 30</MenuItem>
                  <MenuItem value="Net 45">Net 45</MenuItem>
                  <MenuItem value="Net 60">Net 60</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Credit Limit"
                type="number"
                value={formData.credit_limit}
                onChange={(e) => handleInputChange('credit_limit', e.target.value)}
              />
            </Grid>
          </Grid>
        </DialogContent>
                 <DialogActions>
           <Button onClick={handleCloseDialog} disabled={submitting}>Cancel</Button>
           <Button 
             onClick={handleSubmit} 
             variant="contained"
             disabled={submitting}
             startIcon={submitting ? <CircularProgress size={20} /> : null}
           >
             {submitting ? 'Saving...' : (editingVendor ? 'Update' : 'Create') + ' Vendor'}
           </Button>
         </DialogActions>
       </Dialog>

       {/* Snackbar for notifications */}
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

export default VendorManagement;
