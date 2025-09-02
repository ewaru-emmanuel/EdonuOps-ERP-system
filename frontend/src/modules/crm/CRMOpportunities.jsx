import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Snackbar,
  Tooltip,
  LinearProgress
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Search,
  Refresh,
  TrendingUp
} from '@mui/icons-material';
import { useCRM } from './context/CRMContext';

const CRMOpportunities = () => {
  const { opportunities, contacts, loading, errors, createOpportunity, updateOpportunity, deleteOpportunity, fetchOpportunities, fetchContacts } = useCRM();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingOpportunity, setEditingOpportunity] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [stageFilter, setStageFilter] = useState('all');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const [formData, setFormData] = useState({
    name: '',
    company: '',
    value: '',
    probability: 50,
    stage: 'prospecting',
    owner: '',
    expected_close_date: '',
    contact_id: null,
    notes: ''
  });

  useEffect(() => {
    fetchOpportunities();
    fetchContacts();
  }, [fetchOpportunities, fetchContacts]);
  
  // Add safety check for loading state - moved after all hooks
  if (!opportunities && loading.opportunities) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6">Loading opportunities...</Typography>
      </Box>
    );
  }

  const handleOpenDialog = (opportunity = null) => {
    if (opportunity) {
      setEditingOpportunity(opportunity);
      setFormData({
        name: opportunity.name || '',
        company: opportunity.company || '',
        value: opportunity.value || '',
        probability: opportunity.probability || 50,
        stage: opportunity.stage || 'prospecting',
        owner: opportunity.owner || '',
        expected_close_date: opportunity.expected_close_date || '',
        contact_id: opportunity.contact_id || null,
        notes: opportunity.notes || ''
      });
    } else {
      setEditingOpportunity(null);
      setFormData({
        name: '',
        company: '',
        value: '',
        probability: 50,
        stage: 'prospecting',
        owner: '',
        expected_close_date: '',
        contact_id: null,
        notes: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingOpportunity(null);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      const submitData = {
        ...formData,
        value: parseFloat(formData.value) || 0,
        probability: parseInt(formData.probability) || 50
      };

      if (editingOpportunity) {
        await updateOpportunity(editingOpportunity.id, submitData);
        setSnackbar({ open: true, message: 'Opportunity updated successfully!', severity: 'success' });
      } else {
        await createOpportunity(submitData);
        setSnackbar({ open: true, message: 'Opportunity created successfully!', severity: 'success' });
      }
      handleCloseDialog();
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  const handleDelete = async (opportunityId) => {
    if (window.confirm('Are you sure you want to delete this opportunity?')) {
      try {
        await deleteOpportunity(opportunityId);
        setSnackbar({ open: true, message: 'Opportunity deleted successfully!', severity: 'success' });
      } catch (error) {
        setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
      }
    }
  };

  const filteredOpportunities = (opportunities || []).filter(opportunity => {
    const matchesSearch = opportunity.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         opportunity.company?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStage = stageFilter === 'all' || opportunity.stage === stageFilter;
    return matchesSearch && matchesStage;
  });

  const getStageColor = (stage) => {
    switch (stage) {
      case 'prospecting': return 'default';
      case 'qualification': return 'info';
      case 'proposal': return 'warning';
      case 'negotiation': return 'error';
      case 'closed_won': return 'success';
      case 'closed_lost': return 'error';
      default: return 'default';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const getContactName = (contactId) => {
    const contact = (contacts || []).find(c => c.id === contactId);
    return contact ? contact.name : 'Unknown';
  };

  const totalValue = (opportunities || []).reduce((sum, opp) => sum + (opp.value || 0), 0);
  const weightedValue = (opportunities || []).reduce((sum, opp) => sum + ((opp.value || 0) * (opp.probability || 0) / 100), 0);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold">
            Opportunities
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Total Value: {formatCurrency(totalValue)} | Weighted Value: {formatCurrency(weightedValue)}
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
          sx={{ borderRadius: 2 }}
        >
          Add Opportunity
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            placeholder="Search opportunities..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
            }}
            sx={{ minWidth: 300 }}
          />
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Stage</InputLabel>
            <Select
              value={stageFilter}
              label="Stage"
              onChange={(e) => setStageFilter(e.target.value)}
            >
              <MenuItem value="all">All Stages</MenuItem>
              <MenuItem value="prospecting">Prospecting</MenuItem>
              <MenuItem value="qualification">Qualification</MenuItem>
              <MenuItem value="proposal">Proposal</MenuItem>
              <MenuItem value="negotiation">Negotiation</MenuItem>
              <MenuItem value="closed_won">Closed Won</MenuItem>
              <MenuItem value="closed_lost">Closed Lost</MenuItem>
            </Select>
          </FormControl>
          <IconButton onClick={fetchOpportunities} disabled={loading.opportunities}>
            <Refresh />
          </IconButton>
        </Box>
      </Paper>

      {/* Opportunities Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Opportunity</TableCell>
              <TableCell>Company</TableCell>
              <TableCell>Value</TableCell>
              <TableCell>Probability</TableCell>
              <TableCell>Stage</TableCell>
              <TableCell>Owner</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Expected Close</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredOpportunities.map((opportunity) => (
              <TableRow key={opportunity.id} hover>
                <TableCell>
                  <Typography variant="subtitle2" fontWeight="medium">
                    {opportunity.name}
                  </Typography>
                </TableCell>
                <TableCell>{opportunity.company}</TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {formatCurrency(opportunity.value)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={opportunity.probability || 0}
                      sx={{ width: 60, height: 6, borderRadius: 3 }}
                    />
                    <Typography variant="body2">
                      {opportunity.probability}%
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Chip
                    label={opportunity.stage}
                    color={getStageColor(opportunity.stage)}
                    size="small"
                  />
                </TableCell>
                <TableCell>{opportunity.owner}</TableCell>
                <TableCell>{getContactName(opportunity.contact_id)}</TableCell>
                <TableCell>
                  {opportunity.expected_close_date ? 
                    new Date(opportunity.expected_close_date).toLocaleDateString() : 
                    '-'
                  }
                </TableCell>
                <TableCell align="right">
                  <Tooltip title="Edit">
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(opportunity)}
                      color="primary"
                    >
                      <Edit />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(opportunity.id)}
                      color="error"
                    >
                      <Delete />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {filteredOpportunities.length === 0 && (
              <TableRow>
                <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    {searchTerm || stageFilter !== 'all' 
                      ? 'No opportunities match your filters' 
                      : 'No opportunities found. Add your first opportunity!'}
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingOpportunity ? 'Edit Opportunity' : 'Add New Opportunity'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <TextField
              label="Opportunity Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              fullWidth
              required
            />
            <TextField
              label="Company"
              value={formData.company}
              onChange={(e) => handleInputChange('company', e.target.value)}
              fullWidth
              required
            />
            <TextField
              label="Value ($)"
              type="number"
              value={formData.value}
              onChange={(e) => handleInputChange('value', e.target.value)}
              fullWidth
              required
            />
            <TextField
              label="Probability (%)"
              type="number"
              value={formData.probability}
              onChange={(e) => handleInputChange('probability', e.target.value)}
              fullWidth
              inputProps={{ min: 0, max: 100 }}
            />
            <FormControl fullWidth>
              <InputLabel>Stage</InputLabel>
              <Select
                value={formData.stage}
                label="Stage"
                onChange={(e) => handleInputChange('stage', e.target.value)}
              >
                <MenuItem value="prospecting">Prospecting</MenuItem>
                <MenuItem value="qualification">Qualification</MenuItem>
                <MenuItem value="proposal">Proposal</MenuItem>
                <MenuItem value="negotiation">Negotiation</MenuItem>
                <MenuItem value="closed_won">Closed Won</MenuItem>
                <MenuItem value="closed_lost">Closed Lost</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Owner"
              value={formData.owner}
              onChange={(e) => handleInputChange('owner', e.target.value)}
              fullWidth
            />
            <TextField
              label="Expected Close Date"
              type="date"
              value={formData.expected_close_date}
              onChange={(e) => handleInputChange('expected_close_date', e.target.value)}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <FormControl fullWidth>
              <InputLabel>Contact</InputLabel>
              <Select
                value={formData.contact_id}
                label="Contact"
                onChange={(e) => handleInputChange('contact_id', e.target.value)}
              >
                <MenuItem value="">No Contact</MenuItem>
                {(contacts || []).map(contact => (
                  <MenuItem key={contact.id} value={contact.id}>
                    {contact.name} - {contact.company}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="Notes"
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              fullWidth
              multiline
              rows={3}
              sx={{ gridColumn: '1 / -1' }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.name || !formData.company}
          >
            {editingOpportunity ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
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
    </Box>
  );
};

export default CRMOpportunities;
