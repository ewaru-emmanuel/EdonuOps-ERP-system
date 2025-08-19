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
  Snackbar,
  Badge,
  Tabs,
  Tab
} from '@mui/material';
import {
  Phone,
  Email,
  VideoCall,
  Assignment,
  Add,
  CheckCircle,
  Schedule,
  Warning,
  Person,
  Business,
  TrendingUp,
  CalendarToday
} from '@mui/icons-material';
import { useCRM } from './context/CRMContext';

const CRMFollowUps = () => {
  const { followUps, contacts, leads, opportunities, users, createFollowUp, updateFollowUp } = useCRM();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingFollowUp, setEditingFollowUp] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [activeTab, setActiveTab] = useState(0);

  const [formData, setFormData] = useState({
    contact_id: '',
    lead_id: '',
    opportunity_id: '',
    type: 'call',
    due_date: '',
    notes: '',
    assigned_to: '',
    status: 'pending'
  });

  const followUpTypes = [
    { value: 'call', label: 'Phone Call', icon: <Phone />, color: 'primary' },
    { value: 'email', label: 'Email', icon: <Email />, color: 'info' },
    { value: 'meeting', label: 'Meeting', icon: <VideoCall />, color: 'secondary' },
    { value: 'task', label: 'Task', icon: <Assignment />, color: 'warning' }
  ];

  const getFollowUpIcon = (type) => {
    const followUpType = followUpTypes.find(t => t.value === type);
    return followUpType ? followUpType.icon : <Assignment />;
  };

  const getFollowUpColor = (type) => {
    const followUpType = followUpTypes.find(t => t.value === type);
    return followUpType ? followUpType.color : 'default';
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

  const getUserName = (userId) => {
    const user = users?.find(u => u.id === userId);
    return user ? user.username : 'Unknown User';
  };

  const getFollowUpStatus = (followUp) => {
    const dueDate = new Date(followUp.due_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (followUp.status === 'completed') return 'completed';
    if (dueDate < today) return 'overdue';
    if (dueDate.getTime() === today.getTime()) return 'today';
    return 'upcoming';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'overdue': return 'error';
      case 'today': return 'warning';
      case 'upcoming': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle />;
      case 'overdue': return <Warning />;
      case 'today': return <Schedule />;
      case 'upcoming': return <CalendarToday />;
      default: return <Schedule />;
    }
  };

  const handleOpenDialog = (followUp = null) => {
    if (followUp) {
      setEditingFollowUp(followUp);
      setFormData({
        contact_id: followUp.contact_id || '',
        lead_id: followUp.lead_id || '',
        opportunity_id: followUp.opportunity_id || '',
        type: followUp.type || 'call',
        due_date: followUp.due_date || '',
        notes: followUp.notes || '',
        assigned_to: followUp.assigned_to || '',
        status: followUp.status || 'pending'
      });
    } else {
      setEditingFollowUp(null);
      setFormData({
        contact_id: '',
        lead_id: '',
        opportunity_id: '',
        type: 'call',
        due_date: '',
        notes: '',
        assigned_to: '',
        status: 'pending'
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingFollowUp(null);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      if (editingFollowUp) {
        await updateFollowUp(editingFollowUp.id, formData);
        setSnackbar({ open: true, message: 'Follow-up updated successfully!', severity: 'success' });
      } else {
        await createFollowUp(formData);
        setSnackbar({ open: true, message: 'Follow-up created successfully!', severity: 'success' });
      }
      handleCloseDialog();
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  const handleComplete = async (followUp) => {
    try {
      await updateFollowUp(followUp.id, { ...followUp, status: 'completed' });
      setSnackbar({ open: true, message: 'Follow-up marked as completed!', severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  const overdueFollowUps = followUps?.filter(f => getFollowUpStatus(f) === 'overdue') || [];
  const todayFollowUps = followUps?.filter(f => getFollowUpStatus(f) === 'today') || [];
  const upcomingFollowUps = followUps?.filter(f => getFollowUpStatus(f) === 'upcoming') || [];
  const completedFollowUps = followUps?.filter(f => getFollowUpStatus(f) === 'completed') || [];

  const renderFollowUpCard = (followUp) => {
    const status = getFollowUpStatus(followUp);
    
    return (
      <Card key={followUp.id} sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getFollowUpIcon(followUp.type)}
              <Typography variant="h6" fontWeight="medium">
                {followUp.type.charAt(0).toUpperCase() + followUp.type.slice(1)} Follow-up
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip 
                label={followUp.type} 
                color={getFollowUpColor(followUp.type)}
                size="small"
              />
              <Chip 
                label={status} 
                color={getStatusColor(status)}
                icon={getStatusIcon(status)}
                size="small"
              />
            </Box>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {followUp.notes}
          </Typography>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              {followUp.contact_id && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Person sx={{ fontSize: 16 }} />
                  <Typography variant="caption">
                    {getEntityName('contact', followUp.contact_id)}
                  </Typography>
                </Box>
              )}
              {followUp.lead_id && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Business sx={{ fontSize: 16 }} />
                  <Typography variant="caption">
                    {getEntityName('lead', followUp.lead_id)}
                  </Typography>
                </Box>
              )}
              {followUp.opportunity_id && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <TrendingUp sx={{ fontSize: 16 }} />
                  <Typography variant="caption">
                    {getEntityName('opportunity', followUp.opportunity_id)}
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Due: {new Date(followUp.due_date).toLocaleDateString()}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Assigned to: {getUserName(followUp.assigned_to)}
              </Typography>
            </Box>
            {status !== 'completed' && (
              <Button
                size="small"
                variant="outlined"
                startIcon={<CheckCircle />}
                onClick={() => handleComplete(followUp)}
              >
                Mark Complete
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" color="primary">
            Follow-ups & Reminders
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage date-based follow-ups and never miss important interactions
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => handleOpenDialog()}
          sx={{ borderRadius: 2 }}
        >
          Create Follow-up
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Badge badgeContent={overdueFollowUps.length} color="error">
                <Warning sx={{ fontSize: 40, color: 'error.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 1 }}>
                Overdue
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {overdueFollowUps.length} follow-ups
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Badge badgeContent={todayFollowUps.length} color="warning">
                <Schedule sx={{ fontSize: 40, color: 'warning.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 1 }}>
                Today
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {todayFollowUps.length} follow-ups
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Badge badgeContent={upcomingFollowUps.length} color="info">
                <CalendarToday sx={{ fontSize: 40, color: 'info.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 1 }}>
                Upcoming
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {upcomingFollowUps.length} follow-ups
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Badge badgeContent={completedFollowUps.length} color="success">
                <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 1 }}>
                Completed
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {completedFollowUps.length} follow-ups
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab 
            label={
              <Badge badgeContent={overdueFollowUps.length} color="error">
                <span>Overdue</span>
              </Badge>
            } 
          />
          <Tab 
            label={
              <Badge badgeContent={todayFollowUps.length} color="warning">
                <span>Today</span>
              </Badge>
            } 
          />
          <Tab 
            label={
              <Badge badgeContent={upcomingFollowUps.length} color="info">
                <span>Upcoming</span>
              </Badge>
            } 
          />
          <Tab 
            label={
              <Badge badgeContent={completedFollowUps.length} color="success">
                <span>Completed</span>
              </Badge>
            } 
          />
        </Tabs>
      </Paper>

      {/* Follow-up Lists */}
      <Box>
        {activeTab === 0 && (
          <Box>
            {overdueFollowUps.length > 0 ? (
              overdueFollowUps.map(renderFollowUpCard)
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No overdue follow-ups
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Great job staying on top of your follow-ups!
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {activeTab === 1 && (
          <Box>
            {todayFollowUps.length > 0 ? (
              todayFollowUps.map(renderFollowUpCard)
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No follow-ups due today
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  You're all caught up for today!
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {activeTab === 2 && (
          <Box>
            {upcomingFollowUps.length > 0 ? (
              upcomingFollowUps.map(renderFollowUpCard)
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No upcoming follow-ups
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Create follow-ups to stay organized
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {activeTab === 3 && (
          <Box>
            {completedFollowUps.length > 0 ? (
              completedFollowUps.map(renderFollowUpCard)
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No completed follow-ups
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Complete follow-ups to see them here
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </Box>

      {/* Add/Edit Follow-up Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingFollowUp ? 'Edit Follow-up' : 'Create New Follow-up'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Entity Type</InputLabel>
              <Select
                value={formData.contact_id ? 'contact' : formData.lead_id ? 'lead' : formData.opportunity_id ? 'opportunity' : ''}
                label="Entity Type"
                onChange={(e) => {
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
              <InputLabel>Follow-up Type</InputLabel>
              <Select
                value={formData.type}
                label="Follow-up Type"
                onChange={(e) => handleInputChange('type', e.target.value)}
              >
                {followUpTypes.map(type => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Assign To</InputLabel>
              <Select
                value={formData.assigned_to}
                label="Assign To"
                onChange={(e) => handleInputChange('assigned_to', e.target.value)}
              >
                {users?.map(user => (
                  <MenuItem key={user.id} value={user.id}>
                    {user.username} ({user.role})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Due Date"
              type="datetime-local"
              value={formData.due_date}
              onChange={(e) => handleInputChange('due_date', e.target.value)}
              fullWidth
              InputLabelProps={{ shrink: true }}
              sx={{ gridColumn: '1 / -1' }}
            />

            <TextField
              label="Notes"
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              fullWidth
              multiline
              rows={4}
              sx={{ gridColumn: '1 / -1' }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.due_date}
          >
            {editingFollowUp ? 'Update' : 'Create Follow-up'}
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

export default CRMFollowUps;
