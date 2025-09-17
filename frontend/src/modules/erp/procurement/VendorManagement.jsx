import React, { useState, useMemo } from 'react';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { getERPApiService } from '../../../services/erpApiService';
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
  CircularProgress,
  FormControlLabel,
  Switch,
  Tabs,
  Tab,
  Divider,
  InputAdornment
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Business,
  Email,
  Phone,
  LocationOn,
  AttachFile,
  Chat
} from '@mui/icons-material';

const VendorManagement = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [editingVendor, setEditingVendor] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [submitting, setSubmitting] = useState(false);
  const [activeFilters, setActiveFilters] = useState({
    q: '',
    category: '',
    risk_level: '',
    region: '',
    is_active: true,
    is_preferred: ''
  });
  const [manageDialog, setManageDialog] = useState({ open: false, vendor: null, tab: 0 });
  const [vendorDocs, setVendorDocs] = useState([]);
  const [docsLoading, setDocsLoading] = useState(false);
  const [docFile, setDocFile] = useState(null);
  const [docMeta, setDocMeta] = useState({ doc_type: '', effective_date: '', expiry_date: '' });
  const [vendorComms, setVendorComms] = useState([]);
  const [commsLoading, setCommsLoading] = useState(false);
  const [newComm, setNewComm] = useState({ channel: 'email', direction: 'out', subject: '', message: '' });
  
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
    is_active: true,
    category: '',
    risk_level: '',
    region: '',
    is_preferred: false
  });

    // Real-time data hook for vendors
  const { data: vendors, loading: vendorsLoading, error: vendorsError, create, update, remove, refresh } = useRealTimeData('/api/procurement/vendors');

  // Debug: Log vendor data
  console.log('VendorManagement - Vendors data:', vendors);
  console.log('VendorManagement - Loading:', vendorsLoading);
  console.log('VendorManagement - Error:', vendorsError);

  const filteredVendors = useMemo(() => {
    const list = vendors || [];
    return list.filter(v => {
      const qOk = !activeFilters.q || (
        (v.name || '').toLowerCase().includes(activeFilters.q.toLowerCase()) ||
        (v.email || '').toLowerCase().includes(activeFilters.q.toLowerCase())
      );
      const catOk = !activeFilters.category || v.category === activeFilters.category;
      const riskOk = !activeFilters.risk_level || v.risk_level === activeFilters.risk_level;
      const regionOk = !activeFilters.region || v.region === activeFilters.region;
      const activeOk = activeFilters.is_active === '' ? true : (!!v.is_active === !!activeFilters.is_active);
      const prefOk = activeFilters.is_preferred === '' ? true : (!!v.is_preferred === !!activeFilters.is_preferred);
      return qOk && catOk && riskOk && regionOk && activeOk && prefOk;
    });
  }, [vendors, activeFilters]);

  const openManageDialog = async (vendor) => {
    setManageDialog({ open: true, vendor, tab: 0 });
    await Promise.all([loadVendorDocs(vendor.id), loadVendorComms(vendor.id)]);
  };

  const loadVendorDocs = async (vendorId) => {
    try {
      setDocsLoading(true);
      const api = getERPApiService();
      const res = await api.get(`/api/procurement/vendors/${vendorId}/documents`);
      setVendorDocs(res.data || res);
    } catch (e) {
      showSnackbar('Failed to load documents', 'error');
    } finally {
      setDocsLoading(false);
    }
  };

  const uploadDocument = async () => {
    if (!docFile) {
      showSnackbar('Select a file to upload', 'error');
      return;
    }
    try {
      const api = getERPApiService();
      const form = new FormData();
      form.append('file', docFile);
      if (docMeta.doc_type) form.append('doc_type', docMeta.doc_type);
      if (docMeta.effective_date) form.append('effective_date', docMeta.effective_date);
      if (docMeta.expiry_date) form.append('expiry_date', docMeta.expiry_date);
      await api.post(`/api/procurement/vendors/${manageDialog.vendor.id}/documents`, form, { headers: { 'Content-Type': 'multipart/form-data' } });
      setDocFile(null);
      setDocMeta({ doc_type: '', effective_date: '', expiry_date: '' });
      await loadVendorDocs(manageDialog.vendor.id);
      showSnackbar('Document uploaded');
    } catch (e) {
      showSnackbar('Upload failed', 'error');
    }
  };

  const deleteDocument = async (docId) => {
    try {
      const api = getERPApiService();
      await api.delete(`/api/procurement/vendors/${manageDialog.vendor.id}/documents/${docId}`);
      await loadVendorDocs(manageDialog.vendor.id);
      showSnackbar('Document deleted');
    } catch (e) {
      showSnackbar('Delete failed', 'error');
    }
  };

  const loadVendorComms = async (vendorId) => {
    try {
      setCommsLoading(true);
      const api = getERPApiService();
      const res = await api.get(`/api/procurement/vendors/${vendorId}/communications`);
      setVendorComms(res.data || res);
    } catch (e) {
      showSnackbar('Failed to load communications', 'error');
    } finally {
      setCommsLoading(false);
    }
  };

  const addCommunication = async () => {
    if (!newComm.subject?.trim() || !newComm.message?.trim()) {
      showSnackbar('Subject and message are required', 'error');
      return;
    }
    try {
      const api = getERPApiService();
      await api.post(`/api/procurement/vendors/${manageDialog.vendor.id}/communications`, newComm);
      setNewComm({ channel: 'email', direction: 'out', subject: '', message: '' });
      await loadVendorComms(manageDialog.vendor.id);
      showSnackbar('Communication logged');
    } catch (e) {
      showSnackbar('Failed to log communication', 'error');
    }
  };

  const handleOpenDialog = (vendor = null) => {
    if (vendor) {
      setEditingVendor(vendor);
      setFormData({
        name: vendor.name || '',
        email: vendor.email || '',
        phone: vendor.phone || '',
        address: vendor.address || '',
        tax_id: vendor.tax_id || '',
        payment_terms: vendor.payment_terms || 'Net 30',
        credit_limit: vendor.credit_limit || '',
        is_active: !!vendor.is_active,
        category: vendor.category || '',
        risk_level: vendor.risk_level || '',
        region: vendor.region || '',
        is_preferred: !!vendor.is_preferred
      });
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
        is_active: true,
        category: '',
        risk_level: '',
        region: '',
        is_preferred: false
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
      // Debug: Log the form data being submitted
      console.log('VendorManagement - Submitting form data:', formData);
      
      if (editingVendor) {
        console.log('VendorManagement - Updating vendor:', editingVendor.id);
        await update(editingVendor.id, formData);
        showSnackbar('Vendor updated successfully!');
      } else {
        console.log('VendorManagement - Creating new vendor');
        const result = await create(formData);
        console.log('VendorManagement - Create result:', result);
        showSnackbar('Vendor created successfully!');
      }
      handleCloseDialog();
    } catch (error) {
      console.error('VendorManagement - Error saving vendor:', error);
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
        refresh();
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
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

      {/* Filters */}
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                label="Search vendors"
                value={activeFilters.q}
                onChange={(e) => setActiveFilters(prev => ({ ...prev, q: e.target.value }))}
                InputProps={{ startAdornment: <InputAdornment position="start">@</InputAdornment> }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                label="Category"
                value={activeFilters.category}
                onChange={(e) => setActiveFilters(prev => ({ ...prev, category: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth>
                <InputLabel>Risk Level</InputLabel>
                <Select
                  label="Risk Level"
                  value={activeFilters.risk_level}
                  onChange={(e) => setActiveFilters(prev => ({ ...prev, risk_level: e.target.value }))}
                >
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                label="Region"
                value={activeFilters.region}
                onChange={(e) => setActiveFilters(prev => ({ ...prev, region: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                <FormControlLabel
                  control={<Switch checked={!!activeFilters.is_active} onChange={(e) => setActiveFilters(prev => ({ ...prev, is_active: e.target.checked }))} />}
                  label="Active Only"
                />
                <FormControlLabel
                  control={<Switch checked={!!activeFilters.is_preferred} onChange={(e) => setActiveFilters(prev => ({ ...prev, is_preferred: e.target.checked }))} />}
                  label="Preferred"
                />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Vendor Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {filteredVendors?.length || 0}
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
                {filteredVendors?.filter(v => v.is_active).length || 0}
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
                {filteredVendors?.reduce((sum, v) => sum + (v.total_orders || 0), 0) || 0}
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
                ${(filteredVendors?.reduce((sum, v) => sum + (v.total_spent || 0), 0) || 0).toLocaleString()}
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
          
          <TableContainer component={Paper} elevation={0} sx={{ width: '100%', overflowX: 'auto' }}>
            <Table sx={{ minWidth: 800 }}>
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
                   filteredVendors.map((vendor) => (
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
                           <IconButton size="small" color="primary" disabled={submitting} onClick={() => openManageDialog(vendor)}>
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
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Category"
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Risk Level</InputLabel>
                <Select
                  value={formData.risk_level}
                  label="Risk Level"
                  onChange={(e) => handleInputChange('risk_level', e.target.value)}
                >
                  <MenuItem value="">Not set</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Region"
                value={formData.region}
                onChange={(e) => handleInputChange('region', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={<Switch checked={!!formData.is_preferred} onChange={(e) => handleInputChange('is_preferred', e.target.checked)} />}
                label="Preferred Vendor"
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

      {/* Manage Vendor Dialog */}
      <Dialog open={manageDialog.open} onClose={() => setManageDialog({ open: false, vendor: null, tab: 0 })} maxWidth="md" fullWidth>
        <DialogTitle>Vendor Details: {manageDialog.vendor?.name}</DialogTitle>
        <DialogContent>
          <Tabs value={manageDialog.tab} onChange={(e, v) => setManageDialog(prev => ({ ...prev, tab: v }))} sx={{ mb: 2 }}>
            <Tab label="Overview" />
            <Tab label="Documents" />
            <Tab label="Communications" />
          </Tabs>
          {manageDialog.tab === 0 && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">Email</Typography>
                  <Typography variant="body1">{manageDialog.vendor?.email}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">Phone</Typography>
                  <Typography variant="body1">{manageDialog.vendor?.phone}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">Category</Typography>
                  <Typography variant="body1">{manageDialog.vendor?.category || '-'}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">Risk Level</Typography>
                  <Typography variant="body1" sx={{ textTransform: 'capitalize' }}>{manageDialog.vendor?.risk_level || '-'}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">Region</Typography>
                  <Typography variant="body1">{manageDialog.vendor?.region || '-'}</Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary">Preferred</Typography>
                  <Typography variant="body1">{manageDialog.vendor?.is_preferred ? 'Yes' : 'No'}</Typography>
                </Grid>
              </Grid>
            </Box>
          )}
          {manageDialog.tab === 1 && (
            <Box>
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
                <TextField label="Document Type" size="small" value={docMeta.doc_type} onChange={(e) => setDocMeta(prev => ({ ...prev, doc_type: e.target.value }))} />
                <TextField label="Effective Date" type="date" size="small" InputLabelProps={{ shrink: true }} value={docMeta.effective_date} onChange={(e) => setDocMeta(prev => ({ ...prev, effective_date: e.target.value }))} />
                <TextField label="Expiry Date" type="date" size="small" InputLabelProps={{ shrink: true }} value={docMeta.expiry_date} onChange={(e) => setDocMeta(prev => ({ ...prev, expiry_date: e.target.value }))} />
                <Button variant="outlined" component="label" startIcon={<AttachFile />}>Select File<input type="file" hidden onChange={(e) => setDocFile(e.target.files?.[0] || null)} /></Button>
                <Button variant="contained" onClick={uploadDocument} disabled={!docFile}>Upload</Button>
              </Box>
              <Divider sx={{ mb: 2 }} />
              {docsLoading ? (
                <Typography>Loading documents...</Typography>
              ) : vendorDocs.length === 0 ? (
                <Typography color="text.secondary">No documents uploaded</Typography>
              ) : (
                <TableContainer component={Paper} elevation={0}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>Filename</TableCell>
                        <TableCell>Effective</TableCell>
                        <TableCell>Expiry</TableCell>
                        <TableCell align="right">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {vendorDocs.map(doc => (
                        <TableRow key={doc.id}>
                          <TableCell>{doc.doc_type || '-'}</TableCell>
                          <TableCell>{doc.filename}</TableCell>
                          <TableCell>{doc.effective_date || '-'}</TableCell>
                          <TableCell>{doc.expiry_date || '-'}</TableCell>
                          <TableCell align="right"><Button color="error" size="small" onClick={() => deleteDocument(doc.id)}>Delete</Button></TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}
          {manageDialog.tab === 2 && (
            <Box>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Channel</InputLabel>
                    <Select label="Channel" value={newComm.channel} onChange={(e) => setNewComm(prev => ({ ...prev, channel: e.target.value }))}>
                      <MenuItem value="email">Email</MenuItem>
                      <MenuItem value="phone">Phone</MenuItem>
                      <MenuItem value="portal">Portal</MenuItem>
                      <MenuItem value="meeting">Meeting</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Direction</InputLabel>
                    <Select label="Direction" value={newComm.direction} onChange={(e) => setNewComm(prev => ({ ...prev, direction: e.target.value }))}>
                      <MenuItem value="out">Outbound</MenuItem>
                      <MenuItem value="in">Inbound</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField fullWidth size="small" label="Subject" value={newComm.subject} onChange={(e) => setNewComm(prev => ({ ...prev, subject: e.target.value }))} />
                </Grid>
                <Grid item xs={12}>
                  <TextField fullWidth multiline rows={3} label="Message" value={newComm.message} onChange={(e) => setNewComm(prev => ({ ...prev, message: e.target.value }))} />
                </Grid>
                <Grid item xs={12}>
                  <Button variant="contained" startIcon={<Chat />} onClick={addCommunication}>Log Communication</Button>
                </Grid>
              </Grid>
              <Divider sx={{ mb: 2 }} />
              {commsLoading ? (
                <Typography>Loading communications...</Typography>
              ) : vendorComms.length === 0 ? (
                <Typography color="text.secondary">No communications yet</Typography>
              ) : (
                <TableContainer component={Paper} elevation={0}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>When</TableCell>
                        <TableCell>Channel</TableCell>
                        <TableCell>Direction</TableCell>
                        <TableCell>Subject</TableCell>
                        <TableCell>Message</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {vendorComms.map(c => (
                        <TableRow key={c.id}>
                          <TableCell>{c.created_at}</TableCell>
                          <TableCell sx={{ textTransform: 'capitalize' }}>{c.channel}</TableCell>
                          <TableCell sx={{ textTransform: 'capitalize' }}>{c.direction}</TableCell>
                          <TableCell>{c.subject}</TableCell>
                          <TableCell>{c.message}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setManageDialog({ open: false, vendor: null, tab: 0 })}>Close</Button>
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
