import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  PlayArrow as PlayIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  AccountTree as WorkflowIcon,
  Trigger as TriggerIcon,
  Action as ActionIcon,
  Condition as ConditionIcon
} from '@mui/icons-material';

const WorkflowBuilder = () => {
  const [workflows, setWorkflows] = useState([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [workflowForm, setWorkflowForm] = useState({
    name: '',
    description: '',
    trigger: '',
    status: 'draft'
  });

  const triggers = [
    { value: 'invoice_created', label: 'Invoice Created' },
    { value: 'payment_received', label: 'Payment Received' },
    { value: 'purchase_order', label: 'Purchase Order' },
    { value: 'inventory_low', label: 'Low Inventory' },
    { value: 'customer_created', label: 'New Customer' },
    { value: 'scheduled', label: 'Scheduled' }
  ];

  const actions = [
    { value: 'send_email', label: 'Send Email', icon: '📧' },
    { value: 'create_task', label: 'Create Task', icon: '📋' },
    { value: 'update_status', label: 'Update Status', icon: '🔄' },
    { value: 'generate_report', label: 'Generate Report', icon: '📊' },
    { value: 'send_notification', label: 'Send Notification', icon: '🔔' },
    { value: 'create_record', label: 'Create Record', icon: '📝' }
  ];

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const fetchWorkflows = async () => {
    // Mock workflows data
    const mockWorkflows = [
      {
        id: 1,
        name: 'Invoice Processing',
        description: 'Automated invoice processing workflow',
        trigger: 'invoice_created',
        status: 'active',
        steps: 5,
        lastExecuted: '2024-03-15T10:30:00Z'
      },
      {
        id: 2,
        name: 'Payment Follow-up',
        description: 'Automatic payment reminder system',
        trigger: 'payment_received',
        status: 'active',
        steps: 3,
        lastExecuted: '2024-03-14T15:45:00Z'
      },
      {
        id: 3,
        name: 'Inventory Alert',
        description: 'Low inventory notification workflow',
        trigger: 'inventory_low',
        status: 'draft',
        steps: 2,
        lastExecuted: null
      }
    ];
    setWorkflows(mockWorkflows);
  };

  const handleOpenDialog = (workflow = null) => {
    if (workflow) {
      setWorkflowForm({
        name: workflow.name,
        description: workflow.description,
        trigger: workflow.trigger,
        status: workflow.status
      });
      setSelectedWorkflow(workflow);
    } else {
      setWorkflowForm({
        name: '',
        description: '',
        trigger: '',
        status: 'draft'
      });
      setSelectedWorkflow(null);
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedWorkflow(null);
    setWorkflowForm({
      name: '',
      description: '',
      trigger: '',
      status: 'draft'
    });
  };

  const handleSaveWorkflow = async () => {
    try {
      if (selectedWorkflow) {
        // Update existing workflow
        const updatedWorkflows = workflows.map(w =>
          w.id === selectedWorkflow.id
            ? { ...w, ...workflowForm }
            : w
        );
        setWorkflows(updatedWorkflows);
      } else {
        // Create new workflow
        const newWorkflow = {
          id: Date.now(),
          ...workflowForm,
          steps: 0,
          lastExecuted: null
        };
        setWorkflows(prev => [...prev, newWorkflow]);
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving workflow:', error);
    }
  };

  const handleDeleteWorkflow = async (id) => {
    try {
      setWorkflows(prev => prev.filter(w => w.id !== id));
    } catch (error) {
      console.error('Error deleting workflow:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'draft': return 'warning';
      case 'inactive': return 'error';
      default: return 'default';
    }
  };

  const getTriggerLabel = (trigger) => {
    return triggers.find(t => t.value === trigger)?.label || trigger;
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
          Workflow Builder
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ borderRadius: 2 }}
        >
          Create Workflow
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Workflow List */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Workflows
              </Typography>
              
              <List>
                {workflows.map((workflow) => (
                  <ListItem
                    key={workflow.id}
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 2,
                      '&:hover': {
                        bgcolor: 'action.hover'
                      }
                    }}
                  >
                    <ListItemIcon>
                      <WorkflowIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {workflow.name}
                          </Typography>
                          <Chip
                            label={workflow.status.toUpperCase()}
                            color={getStatusColor(workflow.status)}
                            size="small"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                            {workflow.description}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Trigger: {getTriggerLabel(workflow.trigger)} • {workflow.steps} steps
                          </Typography>
                        </Box>
                      }
                    />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(workflow)}
                        sx={{ color: 'primary.main' }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteWorkflow(workflow.id)}
                        sx={{ color: 'error.main' }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflow Designer */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Workflow Designer
              </Typography>
              
              <Box sx={{ 
                height: 400, 
                border: 2, 
                borderColor: 'divider', 
                borderRadius: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                bgcolor: 'grey.50'
              }}>
                <Box sx={{ textAlign: 'center' }}>
                  <WorkflowIcon sx={{ fontSize: 64, color: 'grey.400', mb: 2 }} />
                  <Typography color="textSecondary" gutterBottom>
                    Select a workflow to design
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Drag and drop components to build your workflow
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Available Actions */}
        <Grid item xs={12}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Available Actions
              </Typography>
              
              <Grid container spacing={2}>
                {actions.map((action) => (
                  <Grid item xs={12} sm={6} md={4} key={action.value}>
                    <Card variant="outlined" sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}>
                      <CardContent sx={{ textAlign: 'center', py: 2 }}>
                        <Typography variant="h4" sx={{ mb: 1 }}>
                          {action.icon}
                        </Typography>
                        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                          {action.label}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Create/Edit Workflow Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedWorkflow ? 'Edit Workflow' : 'Create New Workflow'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Workflow Name"
                value={workflowForm.name}
                onChange={(e) => setWorkflowForm(prev => ({ ...prev, name: e.target.value }))}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={workflowForm.description}
                onChange={(e) => setWorkflowForm(prev => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Trigger</InputLabel>
                <Select
                  value={workflowForm.trigger}
                  onChange={(e) => setWorkflowForm(prev => ({ ...prev, trigger: e.target.value }))}
                  label="Trigger"
                >
                  {triggers.map((trigger) => (
                    <MenuItem key={trigger.value} value={trigger.value}>
                      {trigger.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={workflowForm.status}
                  onChange={(e) => setWorkflowForm(prev => ({ ...prev, status: e.target.value }))}
                  label="Status"
                >
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Cancel
          </Button>
          <Button
            onClick={handleSaveWorkflow}
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={!workflowForm.name || !workflowForm.trigger}
          >
            {selectedWorkflow ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowBuilder;




