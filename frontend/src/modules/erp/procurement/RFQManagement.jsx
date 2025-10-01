import React, { useEffect, useMemo, useState } from 'react';
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
  Snackbar,
  Alert,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Visibility as ViewIcon,
  People,
  CheckCircle,
  Score as ScoreIcon,
  WorkspacePremium as AwardIcon
} from '@mui/icons-material';
// Removed API imports to prevent authentication calls

const RFQManagement = () => {
  const [createOpen, setCreateOpen] = useState(false);
  const [inviteOpen, setInviteOpen] = useState(false);
  const [viewOpen, setViewOpen] = useState(false);
  const [selectedRFQ, setSelectedRFQ] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Mock data to prevent API calls
  const rfqs = [];
  const loading = false;
  const error = null;
  const refresh = () => { console.log('Mock refresh RFQs'); };
  
  const vendors = [];

  const [rfqForm, setRfqForm] = useState({
    title: '',
    description: '',
    due_date: '',
    criteria: { price: 0.5, delivery: 0.5 },
    items: []
  });
  const [itemForm, setItemForm] = useState({ description: '', quantity: '1', uom: '' });
  const [inviteSelection, setInviteSelection] = useState([]);
  const [rfqDetails, setRfqDetails] = useState(null);

  const showToast = (message, severity = 'success') => setSnackbar({ open: true, message, severity });

  const addItem = () => {
    if (!itemForm.description || !itemForm.quantity) return;
    setRfqForm(prev => ({ ...prev, items: [...prev.items, { ...itemForm, quantity: parseFloat(itemForm.quantity) }] }));
    setItemForm({ description: '', quantity: '1', uom: '' });
  };

  const removeItem = (index) => {
    setRfqForm(prev => ({ ...prev, items: prev.items.filter((_, i) => i !== index) }));
  };

  const createRFQ = async () => {
    if (!rfqForm.title || !rfqForm.due_date || rfqForm.items.length === 0) {
      showToast('Title, due date and at least one item are required', 'error');
      return;
    }
    try {
      // Mock API call - no authentication
      console.log('Mock create RFQ:', rfqForm);
      setCreateOpen(false);
      setRfqForm({ title: '', description: '', due_date: '', criteria: { price: 0.5, delivery: 0.5 }, items: [] });
      refresh();
      showToast('RFQ created');
    } catch (e) {
      showToast('Failed to create RFQ', 'error');
    }
  };

  const openInvite = (rfq) => {
    setSelectedRFQ(rfq);
    setInviteSelection([]);
    setInviteOpen(true);
  };

  const sendInvites = async () => {
    try {
      // Mock API call - no authentication
      console.log('Mock RFQ API call');
      // Mock invite vendors - no API call
      console.log('Mock invite vendors:', inviteSelection, 'for RFQ:', selectedRFQ.id);
      setInviteOpen(false);
      showToast('Invitations sent');
    } catch (e) {
      showToast('Failed to send invitations', 'error');
    }
  };

  const viewDetails = async (rfq) => {
    try {
      // Mock API call - no authentication
      console.log('Mock RFQ API call');
      // Mock get RFQ details - no API call
      console.log('Mock get RFQ details for:', rfq.id);
      const res = { data: null };
      setRfqDetails(res.data || res);
      setSelectedRFQ(rfq);
      setViewOpen(true);
    } catch (e) {
      showToast('Failed to load RFQ', 'error');
    }
  };

  const scoreResponses = async () => {
    try {
      // Mock API call - no authentication
      console.log('Mock RFQ API call');
      // Mock score RFQ - no API call
      console.log('Mock score RFQ:', selectedRFQ.id);
      await viewDetails(selectedRFQ);
      showToast('Responses scored');
    } catch (e) {
      showToast('Failed to score', 'error');
    }
  };

  const awardResponse = async (responseId) => {
    try {
      // Mock API call - no authentication
      console.log('Mock RFQ API call');
      // Mock award RFQ - no API call
      console.log('Mock award RFQ:', selectedRFQ.id, 'to response:', responseId);
      const res = { data: null };
      showToast('Awarded and PO created');
      setViewOpen(false);
    } catch (e) {
      showToast('Failed to award', 'error');
    }
  };

  const statusColor = (status) => {
    switch (status) {
      case 'open': return 'info';
      case 'awarded': return 'success';
      case 'closed': return 'default';
      case 'cancelled': return 'error';
      default: return 'warning';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>RFQ Management</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateOpen(true)} sx={{ textTransform: 'none' }}>Create RFQ</Button>
      </Box>

      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 2 }}>RFQs</Typography>
          {error && <Alert severity="error">{String(error)}</Alert>}
          <TableContainer component={Paper} elevation={0} sx={{ width: '100%', overflowX: 'auto' }}>
            <Table sx={{ minWidth: 700 }}>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>Title</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Due</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Items</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }} align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(rfqs || []).map(r => (
                  <TableRow key={r.id} hover>
                    <TableCell>{r.title}</TableCell>
                    <TableCell>{r.due_date || '-'}</TableCell>
                    <TableCell><Chip size="small" color={statusColor(r.status)} label={r.status} sx={{ textTransform: 'capitalize' }} /></TableCell>
                    <TableCell>{r.items_count || (r.items?.length || 0)}</TableCell>
                    <TableCell align="right">
                      <IconButton color="primary" onClick={() => viewDetails(r)} title="View"><ViewIcon /></IconButton>
                      <IconButton color="info" onClick={() => openInvite(r)} title="Invite Vendors"><People /></IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create RFQ Dialog */}
      <Dialog open={createOpen} onClose={() => setCreateOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create RFQ</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Title" value={rfqForm.title} onChange={(e) => setRfqForm(prev => ({ ...prev, title: e.target.value }))} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth type="date" label="Due Date" value={rfqForm.due_date} onChange={(e) => setRfqForm(prev => ({ ...prev, due_date: e.target.value }))} InputLabelProps={{ shrink: true }} />
            </Grid>
            <Grid item xs={12}>
              <TextField fullWidth multiline rows={3} label="Description" value={rfqForm.description} onChange={(e) => setRfqForm(prev => ({ ...prev, description: e.target.value }))} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth type="number" label="Price Weight (0-1)" value={rfqForm.criteria.price} onChange={(e) => setRfqForm(prev => ({ ...prev, criteria: { ...prev.criteria, price: e.target.value } }))} />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField fullWidth type="number" label="Delivery Weight (0-1)" value={rfqForm.criteria.delivery} onChange={(e) => setRfqForm(prev => ({ ...prev, criteria: { ...prev.criteria, delivery: e.target.value } }))} />
            </Grid>
          </Grid>

          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle1" sx={{ mb: 1 }}>Items</Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField fullWidth label="Description" value={itemForm.description} onChange={(e) => setItemForm(prev => ({ ...prev, description: e.target.value }))} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth type="number" label="Quantity" value={itemForm.quantity} onChange={(e) => setItemForm(prev => ({ ...prev, quantity: e.target.value }))} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth label="UoM" value={itemForm.uom} onChange={(e) => setItemForm(prev => ({ ...prev, uom: e.target.value }))} />
            </Grid>
            <Grid item xs={12}>
              <Button variant="outlined" startIcon={<AddIcon />} onClick={addItem}>Add Item</Button>
            </Grid>
          </Grid>
          {(rfqForm.items.length > 0) && (
            <TableContainer component={Paper} elevation={0} sx={{ mt: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Description</TableCell>
                    <TableCell>Qty</TableCell>
                    <TableCell>UoM</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {rfqForm.items.map((it, idx) => (
                    <TableRow key={idx}>
                      <TableCell>{it.description}</TableCell>
                      <TableCell>{it.quantity}</TableCell>
                      <TableCell>{it.uom}</TableCell>
                      <TableCell align="right"><Button color="error" size="small" onClick={() => removeItem(idx)}>Remove</Button></TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={createRFQ}>Create RFQ</Button>
        </DialogActions>
      </Dialog>

      {/* Invite Vendors Dialog */}
      <Dialog open={inviteOpen} onClose={() => setInviteOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Invite Vendors</DialogTitle>
        <DialogContent>
          <FormControl fullWidth>
            <InputLabel>Vendors</InputLabel>
            <Select multiple label="Vendors" value={inviteSelection} onChange={(e) => setInviteSelection(e.target.value)}>
              {(vendors || []).map(v => (
                <MenuItem key={v.id} value={v.id}>{v.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInviteOpen(false)}>Cancel</Button>
          <Button variant="contained" startIcon={<People />} onClick={sendInvites}>Send Invites</Button>
        </DialogActions>
      </Dialog>

      {/* View RFQ Dialog */}
      <Dialog open={viewOpen} onClose={() => setViewOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>RFQ Details</DialogTitle>
        <DialogContent>
          {rfqDetails ? (
            <Box>
              <Typography variant="h6">{rfqDetails.title}</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>{rfqDetails.description}</Typography>
              <Chip size="small" color={statusColor(rfqDetails.status)} label={rfqDetails.status} sx={{ mb: 2, textTransform: 'capitalize' }} />

              <Typography variant="subtitle1">Items</Typography>
              <TableContainer component={Paper} elevation={0} sx={{ mb: 2 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Description</TableCell>
                      <TableCell>Qty</TableCell>
                      <TableCell>UoM</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(rfqDetails.items || []).map(it => (
                      <TableRow key={it.id}>
                        <TableCell>{it.description}</TableCell>
                        <TableCell>{it.quantity}</TableCell>
                        <TableCell>{it.uom}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              <Typography variant="subtitle1">Responses</Typography>
              <TableContainer component={Paper} elevation={0}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Vendor</TableCell>
                      <TableCell>Total Price</TableCell>
                      <TableCell>Delivery (days)</TableCell>
                      <TableCell>Score</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(rfqDetails.responses || []).map(resp => (
                      <TableRow key={resp.id}>
                        <TableCell>{resp.vendor?.name || resp.vendor_id}</TableCell>
                        <TableCell>${(resp.total_price || 0).toLocaleString()}</TableCell>
                        <TableCell>{resp.delivery_days || '-'}</TableCell>
                        <TableCell>{resp.total_score || '-'}</TableCell>
                        <TableCell align="right">
                          <Button size="small" startIcon={<AwardIcon />} onClick={() => awardResponse(resp.id)}>Award</Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                <Button variant="outlined" startIcon={<ScoreIcon />} onClick={scoreResponses}>Score Responses</Button>
              </Box>
            </Box>
          ) : (
            <Typography>Loading...</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Snackbar open={snackbar.open} autoHideDuration={6000} onClose={() => setSnackbar({ ...snackbar, open: false })}>
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default RFQManagement;


