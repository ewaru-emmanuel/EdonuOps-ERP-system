import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  Grid,
  IconButton,
  Tooltip,
  Alert,
  Snackbar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  TrendingUp,
  Person,
  Business,
  AttachMoney,
  Schedule,
  DragIndicator
} from '@mui/icons-material';
import { useCRM } from './context/CRMContext';

const CRMPipeline = () => {
  const { 
    opportunities, 
    contacts, 
    loading, 
    errors, 
    createOpportunity, 
    updateOpportunity, 
    deleteOpportunity, 
    moveOpportunity,
    fetchOpportunities, 
    fetchContacts 
  } = useCRM();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingOpportunity, setEditingOpportunity] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const [formData, setFormData] = useState({
    name: '',
    company: '',
    value: '',
    probability: 50,
    stage: 'prospecting',
    owner: '',
    expected_close_date: '',
    contact_id: '',
    notes: ''
  });

  const stages = [
    { id: 'prospecting', name: 'Prospecting', color: 'default', probability: 10 },
    { id: 'qualification', name: 'Qualification', color: 'info', probability: 25 },
    { id: 'proposal', name: 'Proposal', color: 'warning', probability: 50 },
    { id: 'negotiation', name: 'Negotiation', color: 'error', probability: 75 },
    { id: 'closed_won', name: 'Closed Won', color: 'success', probability: 100 },
    { id: 'closed_lost', name: 'Closed Lost', color: 'error', probability: 0 }
  ];

  useEffect(() => {
    fetchOpportunities();
    fetchContacts();
  }, [fetchOpportunities, fetchContacts]);

  const getOpportunitiesByStage = (stageId) => {
    return (opportunities || []).filter(opp => opp.stage === stageId);
  };

  const getContactName = (contactId) => {
    const contact = (contacts || []).find(c => c.id === contactId);
    return contact ? contact.name : 'Unknown';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const getStageColor = (stage) => {
    const stageConfig = stages.find(s => s.id === stage);
    return stageConfig ? stageConfig.color : 'default';
  };

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
        contact_id: opportunity.contact_id || '',
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
        contact_id: '',
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

  const handleMoveOpportunity = async (opportunityId, newStage) => {
    try {
      await moveOpportunity(opportunityId, newStage);
      setSnackbar({ open: true, message: 'Opportunity moved successfully!', severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  const totalValue = (opportunities || []).reduce((sum, opp) => sum + (opp.value || 0), 0);
  const weightedValue = (opportunities || []).reduce((sum, opp) => sum + ((opp.value || 0) * (opp.probability || 0) / 100), 0);
  const totalOpportunities = (opportunities || []).length;
  const wonOpportunities = (opportunities || []).filter(opp => opp.stage === 'closed_won').length;
  const winRate = totalOpportunities > 0 ? (wonOpportunities / totalOpportunities * 100).toFixed(1) : 0;

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold">
            Sales Pipeline
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Total Value: {formatCurrency(totalValue)} | Weighted Value: {formatCurrency(weightedValue)} | Win Rate: {winRate}%
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

      {/* Pipeline Stages */}
      <Grid container spacing={3}>
        {stages.map((stage) => {
          const stageOpportunities = getOpportunitiesByStage(stage.id);
          const stageValue = stageOpportunities.reduce((sum, opp) => sum + (opp.value || 0), 0);
          const stageCount = stageOpportunities.length;
          
          return (
            <Grid item xs={12} md={4} lg={2} key={stage.id}>
              <Paper sx={{ p: 2, height: '100%', minHeight: 400, display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2, gap: 1, minWidth: 0 }}>
                  <Typography 
                    variant="subtitle1" 
                    fontWeight="medium"
                    sx={{ 
                      flex: 1, 
                      minWidth: 0, 
                      overflow: 'hidden', 
                      textOverflow: 'ellipsis', 
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {stage.name}
                  </Typography>
                  <Chip 
                    label={stageCount} 
                    color={stage.color} 
                    size="small" 
                  />
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2, wordBreak: 'break-word' }}>
                  {formatCurrency(stageValue)}
                </Typography>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, maxHeight: 300, overflowY: 'auto', overflowX: 'hidden', pr: 0.5 }}>
                  {stageOpportunities.map((opportunity) => (
                    <Card key={opportunity.id} sx={{ mb: 1, cursor: 'pointer' }} onClick={() => handleOpenDialog(opportunity)}>
                      <CardContent sx={{ p: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1, gap: 1, minWidth: 0 }}>
                          <Typography 
                            variant="subtitle2" 
                            fontWeight="medium" 
                            sx={{ 
                              flex: 1, 
                              minWidth: 0, 
                              overflow: 'hidden', 
                              textOverflow: 'ellipsis', 
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {opportunity.name}
                          </Typography>
                          <DragIndicator sx={{ fontSize: 16, color: 'text.secondary' }} />
                        </Box>
                        
                        <Typography variant="body2" color="text.secondary" gutterBottom sx={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {opportunity.company}
                        </Typography>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                          <Typography variant="body2" fontWeight="medium" color="primary">
                            {formatCurrency(opportunity.value)}
                          </Typography>
                          <Chip 
                            label={`${opportunity.probability}%`} 
                            size="small" 
                            color={opportunity.probability > 70 ? 'success' : opportunity.probability > 30 ? 'warning' : 'error'}
                          />
                        </Box>
                        
                        {opportunity.contact_id && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center' }}>
                            <Person sx={{ fontSize: 12, mr: 0.5 }} />
                            {getContactName(opportunity.contact_id)}
                          </Typography>
                        )}
                        
                        {opportunity.expected_close_date && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                            <Schedule sx={{ fontSize: 12, mr: 0.5 }} />
                            {new Date(opportunity.expected_close_date).toLocaleDateString()}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                  
                  {stageOpportunities.length === 0 && (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="body2" color="text.secondary">
                        No opportunities
                      </Typography>
                    </Box>
                  )}
                </Box>
              </Paper>
            </Grid>
          );
        })}
      </Grid>

      {/* Pipeline Analytics */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" fontWeight="medium" gutterBottom>
          Pipeline Analytics
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="primary" fontWeight="bold">
                {totalOpportunities}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Opportunities
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="success.main" fontWeight="bold">
                {wonOpportunities}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Won Opportunities
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="warning.main" fontWeight="bold">
                {winRate}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Win Rate
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h4" color="info.main" fontWeight="bold">
                {formatCurrency(weightedValue)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Weighted Value
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>

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
              sx={{ gridColumn: '1 / -1' }}
            />
            <TextField
              label="Company"
              value={formData.company}
              onChange={(e) => handleInputChange('company', e.target.value)}
              fullWidth
            />
            <TextField
              label="Value"
              type="number"
              value={formData.value}
              onChange={(e) => handleInputChange('value', e.target.value)}
              fullWidth
              InputProps={{
                startAdornment: <Typography variant="body2" sx={{ mr: 1 }}>$</Typography>
              }}
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
                {(contacts || []).map((contact) => (
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
            disabled={!formData.name}
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

export default CRMPipeline;

