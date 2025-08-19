import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Phone,
  Email,
  Message,
  Note,
  VideoCall,
  Add,
  Edit,
  Delete,
  Schedule,
  Person,
  Business,
  TrendingUp
} from '@mui/icons-material';
import { useCRM } from './context/CRMContext';

const CRMCommunicationHistory = () => {
  const { communications, contacts, leads, opportunities, createCommunication } = useCRM();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCommunication, setEditingCommunication] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [filterType, setFilterType] = useState('all');
  const [filterEntity, setFilterEntity] = useState('all');

  const [formData, setFormData] = useState({
    contact_id: '',
    lead_id: '',
    opportunity_id: '',
    type: 'call',
    direction: 'outbound',
    subject: '',
    content: '',
    duration: '',
    status: 'completed',
    scheduled_for: ''
  });

  const communicationTypes = [
    { value: 'call', label: 'Phone Call', icon: <Phone />, color: 'primary' },
    { value: 'email', label: 'Email', icon: <Email />, color: 'info' },
    { value: 'sms', label: 'SMS', icon: <Message />, color: 'success' },
    { value: 'note', label: 'Note', icon: <Note />, color: 'warning' },
    { value: 'meeting', label: 'Meeting', icon: <VideoCall />, color: 'secondary' }
  ];

  const getCommunicationIcon = (type) => {
    const commType = communicationTypes.find(t => t.value === type);
    return commType ? commType.icon : <Note />;
  };

  const getCommunicationColor = (type) => {
    const commType = communicationTypes.find(t => t.value === type);
    return commType ? commType.color : 'default';
  };

  const getEntityName = (type, id) => {
    if (!id) return 'N/A';
    
    switch (type) {
      case 'contact':
        const contact = contacts?.find(c => c.id === id);
        return contact ? contact.name : 'Unknown Contact';
      case 'lead':
        const lead = leads?.find(l => l.id === id);
        return lead ? lead.name : 'Unknown Lead';
      case 'opportunity':
        const opportunity = opportunities?.find(o => o.id === id);
        return opportunity ? opportunity.name : 'Unknown Opportunity';
      default:
        return 'N/A';
    }
  };

  const handleOpenDialog = (communication = null) => {
    if (communication) {
      setEditingCommunication(communication);
      setFormData({
        contact_id: communication.contact_id || '',
        lead_id: communication.lead_id || '',
        opportunity_id: communication.opportunity_id || '',
        type: communication.type || 'call',
        direction: communication.direction || 'outbound',
        subject: communication.subject || '',
        content: communication.content || '',
        duration: communication.duration || '',
        status: communication.status || 'completed',
        scheduled_for: communication.scheduled_for || ''
      });
    } else {
      setEditingCommunication(null);
      setFormData({
        contact_id: '',
        lead_id: '',
        opportunity_id: '',
        type: 'call',
        direction: 'outbound',
        subject: '',
        content: '',
        duration: '',
        status: 'completed',
        scheduled_for: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingCommunication(null);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      await createCommunication(formData);
      setSnackbar({ open: true, message: 'Communication logged successfully!', severity: 'success' });
      handleCloseDialog();
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  const filteredCommunications = communications?.filter(comm => {
    if (filterType !== 'all' && comm.type !== filterType) return false;
    if (filterEntity !== 'all') {
      if (filterEntity === 'contacts' && !comm.contact_id) return false;
      if (filterEntity === 'leads' && !comm.lead_id) return false;
      if (filterEntity === 'opportunities' && !comm.opportunity_id) return false;
    }
    return true;
  }) || [];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" color="primary">
            Communication History
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Track all interactions with contacts, leads, and opportunities
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
          sx={{ borderRadius: 2 }}
        >
          Log Communication
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Communication Type</InputLabel>
              <Select
                value={filterType}
                label="Communication Type"
                onChange={(e) => setFilterType(e.target.value)}
              >
                <MenuItem value="all">All Types</MenuItem>
                {communicationTypes.map(type => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Entity Type</InputLabel>
              <Select
                value={filterEntity}
                label="Entity Type"
                onChange={(e) => setFilterEntity(e.target.value)}
              >
                <MenuItem value="all">All Entities</MenuItem>
                <MenuItem value="contacts">Contacts Only</MenuItem>
                <MenuItem value="leads">Leads Only</MenuItem>
                <MenuItem value="opportunities">Opportunities Only</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">
              {filteredCommunications.length} communications found
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Communication List */}
      <Grid container spacing={2}>
        {filteredCommunications.map((communication) => (
          <Grid item xs={12} key={communication.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {getCommunicationIcon(communication.type)}
                    <Typography variant="h6" fontWeight="medium">
                      {communication.subject || `${communication.type.charAt(0).toUpperCase() + communication.type.slice(1)} with ${getEntityName('contact', communication.contact_id) || getEntityName('lead', communication.lead_id) || getEntityName('opportunity', communication.opportunity_id)}`}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip 
                      label={communication.type} 
                      color={getCommunicationColor(communication.type)}
                      size="small"
                    />
                    <Chip 
                      label={communication.direction} 
                      variant="outlined"
                      size="small"
                    />
                    {communication.duration && (
                      <Chip 
                        label={`${Math.floor(communication.duration / 60)}:${(communication.duration % 60).toString().padStart(2, '0')}`}
                        size="small"
                      />
                    )}
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {communication.content}
                </Typography>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    {communication.contact_id && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Person sx={{ fontSize: 16 }} />
                        <Typography variant="caption">
                          {getEntityName('contact', communication.contact_id)}
                        </Typography>
                      </Box>
                    )}
                    {communication.lead_id && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Business sx={{ fontSize: 16 }} />
                        <Typography variant="caption">
                          {getEntityName('lead', communication.lead_id)}
                        </Typography>
                      </Box>
                    )}
                    {communication.opportunity_id && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <TrendingUp sx={{ fontSize: 16 }} />
                        <Typography variant="caption">
                          {getEntityName('opportunity', communication.opportunity_id)}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(communication.created_at).toLocaleString()}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredCommunications.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No communications found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Start logging communications to track your interactions
          </Typography>
        </Box>
      )}

      {/* Add/Edit Communication Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingCommunication ? 'Edit Communication' : 'Log New Communication'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Entity Type</InputLabel>
              <Select
                value={formData.contact_id ? 'contact' : formData.lead_id ? 'lead' : formData.opportunity_id ? 'opportunity' : ''}
                label="Entity Type"
                onChange={(e) => {
                  // Clear all entity IDs when changing type
                  setFormData(prev => ({
                    ...prev,
                    contact_id: '',
                    lead_id: '',
                    opportunity_id: ''
                  }));
                }}
              >
                <MenuItem value="">No Entity</MenuItem>
                <MenuItem value="contact">Contact</MenuItem>
                <MenuItem value="lead">Lead</MenuItem>
                <MenuItem value="opportunity">Opportunity</MenuItem>
              </Select>
            </FormControl>

            {formData.contact_id || formData.lead_id || formData.opportunity_id ? (
              <FormControl fullWidth>
                <InputLabel>Select Entity</InputLabel>
                <Select
                  value={formData.contact_id || formData.lead_id || formData.opportunity_id}
                  label="Select Entity"
                  onChange={(e) => {
                    const entityType = formData.contact_id ? 'contact_id' : formData.lead_id ? 'lead_id' : 'opportunity_id';
                    setFormData(prev => ({
                      ...prev,
                      contact_id: '',
                      lead_id: '',
                      opportunity_id: '',
                      [entityType]: e.target.value
                    }));
                  }}
                >
                  {formData.contact_id && contacts?.map(contact => (
                    <MenuItem key={contact.id} value={contact.id}>
                      {contact.name} - {contact.company}
                    </MenuItem>
                  ))}
                  {formData.lead_id && leads?.map(lead => (
                    <MenuItem key={lead.id} value={lead.id}>
                      {lead.name} - {lead.company}
                    </MenuItem>
                  ))}
                  {formData.opportunity_id && opportunities?.map(opp => (
                    <MenuItem key={opp.id} value={opp.id}>
                      {opp.name} - {opp.company}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            ) : (
              <Box />
            )}

            <FormControl fullWidth>
              <InputLabel>Communication Type</InputLabel>
              <Select
                value={formData.type}
                label="Communication Type"
                onChange={(e) => handleInputChange('type', e.target.value)}
              >
                {communicationTypes.map(type => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Direction</InputLabel>
              <Select
                value={formData.direction}
                label="Direction"
                onChange={(e) => handleInputChange('direction', e.target.value)}
              >
                <MenuItem value="inbound">Inbound</MenuItem>
                <MenuItem value="outbound">Outbound</MenuItem>
              </Select>
            </FormControl>

            <TextField
              label="Subject"
              value={formData.subject}
              onChange={(e) => handleInputChange('subject', e.target.value)}
              fullWidth
              sx={{ gridColumn: '1 / -1' }}
            />

            <TextField
              label="Content/Notes"
              value={formData.content}
              onChange={(e) => handleInputChange('content', e.target.value)}
              fullWidth
              multiline
              rows={4}
              sx={{ gridColumn: '1 / -1' }}
            />

            {formData.type === 'call' && (
              <TextField
                label="Duration (seconds)"
                type="number"
                value={formData.duration}
                onChange={(e) => handleInputChange('duration', e.target.value)}
                fullWidth
              />
            )}

            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                label="Status"
                onChange={(e) => handleInputChange('status', e.target.value)}
              >
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="scheduled">Scheduled</MenuItem>
                <MenuItem value="missed">Missed</MenuItem>
              </Select>
            </FormControl>

            {formData.status === 'scheduled' && (
              <TextField
                label="Scheduled For"
                type="datetime-local"
                value={formData.scheduled_for}
                onChange={(e) => handleInputChange('scheduled_for', e.target.value)}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.content}
          >
            {editingCommunication ? 'Update' : 'Log Communication'}
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

export default CRMCommunicationHistory;
