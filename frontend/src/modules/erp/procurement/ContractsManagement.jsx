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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Snackbar,
  Alert,
  Divider
} from '@mui/material';
import { Add as AddIcon, AttachFile } from '@mui/icons-material';
// Removed API imports to prevent authentication calls

const ContractsManagement = () => {
  // Mock data to prevent API calls
  const contracts = [];
  const refreshContracts = () => { console.log('Mock refresh contracts'); };
  
  const vendors = [];
  const [createOpen, setCreateOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [docDialog, setDocDialog] = useState({ open: false, contract: null });
  const [docFile, setDocFile] = useState(null);
  const [docType, setDocType] = useState('');

  const [form, setForm] = useState({
    title: '',
    vendor_id: '',
    status: 'active',
    start_date: '',
    end_date: '',
    renewal_notice_days: 60,
    auto_renew: false,
    contract_value: '',
    terms_summary: ''
  });

  const showToast = (message, severity = 'success') => setSnackbar({ open: true, message, severity });

  const createContract = async () => {
    if (!form.title || !form.vendor_id) {
      showToast('Title and vendor are required', 'error');
      return;
    }
    try {
      // Mock API call - no authentication
      console.log('Mock create contract:', form);
      setCreateOpen(false);
      setForm({ title: '', vendor_id: '', status: 'active', start_date: '', end_date: '', renewal_notice_days: 60, auto_renew: false, contract_value: '', terms_summary: '' });
      refreshContracts();
      showToast('Contract created');
    } catch (e) {
      showToast('Failed to create contract', 'error');
    }
  };

  const openUploadDoc = (contract) => {
    setDocDialog({ open: true, contract });
    setDocFile(null);
    setDocType('');
  };

  const uploadDoc = async () => {
    if (!docFile) {
      showToast('Select a file first', 'error');
      return;
    }
    try {
      // Mock API call - no authentication
      console.log('Mock upload contract document');
      // Mock document upload - no API call
      console.log('Mock upload document:', docFile.name, 'for contract:', docDialog.contract.id);
      setDocDialog({ open: false, contract: null });
      showToast('Document uploaded');
    } catch (e) {
      showToast('Upload failed', 'error');
    }
  };

  const getVendorName = (vendorId) => {
    const v = vendors?.find(v => v.id === vendorId);
    return v ? v.name : 'Unknown';
  };

  const statusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'draft': return 'default';
      case 'expired': return 'warning';
      case 'terminated': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>Contracts Management</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateOpen(true)} sx={{ textTransform: 'none' }}>New Contract</Button>
      </Box>

      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 2 }}>Contracts</Typography>
          <TableContainer component={Paper} elevation={0} sx={{ width: '100%', overflowX: 'auto' }}>
            <Table sx={{ minWidth: 800 }}>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>Title</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Vendor</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Start</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>End</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Value</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(contracts || []).map(c => (
                  <TableRow key={c.id} hover>
                    <TableCell>{c.title}</TableCell>
                    <TableCell>{getVendorName(c.vendor_id)}</TableCell>
                    <TableCell>{c.start_date || '-'}</TableCell>
                    <TableCell>{c.end_date || '-'}</TableCell>
                    <TableCell>${(c.contract_value || 0).toLocaleString()}</TableCell>
                    <TableCell><Chip size="small" color={statusColor(c.status)} label={c.status} sx={{ textTransform: 'capitalize' }} /></TableCell>
                    <TableCell align="right">
                      <Button size="small" variant="outlined" startIcon={<AttachFile />} onClick={() => openUploadDoc(c)}>Upload Doc</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create Contract */}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Contract</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Title" value={form.title} onChange={(e) => setForm(prev => ({ ...prev, title: e.target.value }))} />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Vendor</InputLabel>
                <Select label="Vendor" value={form.vendor_id} onChange={(e) => setForm(prev => ({ ...prev, vendor_id: e.target.value }))}>
                  {(vendors || []).map(v => (<MenuItem key={v.id} value={v.id}>{v.name}</MenuItem>))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth type="date" label="Start Date" value={form.start_date} onChange={(e) => setForm(prev => ({ ...prev, start_date: e.target.value }))} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth type="date" label="End Date" value={form.end_date} onChange={(e) => setForm(prev => ({ ...prev, end_date: e.target.value }))} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth type="number" label="Contract Value" value={form.contract_value} onChange={(e) => setForm(prev => ({ ...prev, contract_value: e.target.value }))} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="Terms Summary" value={form.terms_summary} onChange={(e) => setForm(prev => ({ ...prev, terms_summary: e.target.value }))} />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={createContract}>Create Contract</Button>
        </DialogActions>
      </Dialog>

      {/* Upload Document */}
      <Dialog open={docDialog.open} onClose={() => setDocDialog({ open: false, contract: null })} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Contract Document</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Document Type" value={docType} onChange={(e) => setDocType(e.target.value)} sx={{ mb: 2 }} />
          <Button variant="outlined" component="label" startIcon={<AttachFile />}>Select File<input type="file" hidden onChange={(e) => setDocFile(e.target.files?.[0] || null)} /></Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDocDialog({ open: false, contract: null })}>Cancel</Button>
          <Button variant="contained" onClick={uploadDoc} disabled={!docFile}>Upload</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default ContractsManagement;


