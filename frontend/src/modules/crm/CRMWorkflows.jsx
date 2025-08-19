import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Button, Grid, Card, CardContent, Chip, Dialog, DialogTitle, DialogContent, DialogActions, TextField, FormControl, InputLabel, Select, MenuItem, IconButton, Tooltip, Snackbar, Alert } from '@mui/material';
import { AccountTree, Add, PlayArrow, Stop, Edit, Delete, Refresh } from '@mui/icons-material';
import { useWorkflow } from './context/WorkflowContext';

const CRMWorkflows = () => {
  const { workflows, loading, errors, createWorkflow, updateWorkflow, deleteWorkflow, fetchWorkflows, toggleWorkflow } = useWorkflow();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    trigger: 'manual',
    status: 'inactive',
    conditions: [],
    actions: []
  });

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  // Add safety check for loading state
  if (!workflows && loading.workflows) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6">Loading workflows...</Typography>
      </Box>
    );
  }

  const handleOpenDialog = (workflow = null) => {
    if (workflow) {
      setEditingWorkflow(workflow);
      setFormData({
        name: workflow.name || '',
        description: workflow.description || '',
        trigger: workflow.trigger || 'manual',
        status: workflow.status || 'inactive',
        conditions: workflow.conditions || [],
        actions: workflow.actions || []
      });
    } else {
      setEditingWorkflow(null);
      setFormData({
        name: '',
        description: '',
        trigger: 'manual',
        status: 'inactive',
        conditions: [],
        actions: []
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingWorkflow(null);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      if (editingWorkflow) {
        await updateWorkflow(editingWorkflow.id, formData);
        setSnackbar({ open: true, message: 'Workflow updated successfully!', severity: 'success' });
      } else {
        await createWorkflow(formData);
        setSnackbar({ open: true, message: 'Workflow created successfully!', severity: 'success' });
      }
      handleCloseDialog();
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  const handleDelete = async (workflowId) => {
    if (window.confirm('Are you sure you want to delete this workflow?')) {
      try {
        await deleteWorkflow(workflowId);
        setSnackbar({ open: true, message: 'Workflow deleted successfully!', severity: 'success' });
      } catch (error) {
        setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
      }
    }
  };

  const handleToggle = async (workflowId, currentStatus) => {
    try {
      await toggleWorkflow(workflowId, currentStatus === 'active' ? 'inactive' : 'active');
      setSnackbar({ open: true, message: `Workflow ${currentStatus === 'active' ? 'deactivated' : 'activated'}!`, severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight="bold">
          Workflows
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchWorkflows}
            disabled={loading.workflows}
          >
            Refresh
          </Button>
          <Button 
            variant="contained" 
            startIcon={<Add />}
            onClick={() => handleOpenDialog()}
          >
            Create Workflow
          </Button>
        </Box>
      </Box>
      
      <Grid container spacing={3}>
        {(workflows || []).map((workflow) => (
          <Grid item xs={12} md={6} lg={4} key={workflow.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" fontWeight="medium" sx={{ flex: 1 }}>
                    {workflow.name}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    <Tooltip title="Toggle Status">
                      <IconButton
                        size="small"
                        onClick={() => handleToggle(workflow.id, workflow.status)}
                        color={workflow.status === 'active' ? 'success' : 'default'}
                      >
                        {workflow.status === 'active' ? <Stop /> : <PlayArrow />}
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Edit">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(workflow)}
                        color="primary"
                      >
                        <Edit />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete">
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(workflow.id)}
                        color="error"
                      >
                        <Delete />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {workflow.description}
                </Typography>
                
                <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                  <Chip 
                    label={workflow.status} 
                    color={workflow.status === 'active' ? 'success' : 'default'} 
                    size="small" 
                    icon={workflow.status === 'active' ? <PlayArrow /> : <Stop />}
                  />
                  <Chip 
                    label={workflow.trigger} 
                    color="primary" 
                    size="small" 
                  />
                </Box>
                
                {workflow.conditions && workflow.conditions.length > 0 && (
                  <Typography variant="caption" color="text.secondary">
                    Conditions: {workflow.conditions.length}
                  </Typography>
                )}
                
                {workflow.actions && workflow.actions.length > 0 && (
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 2 }}>
                    Actions: {workflow.actions.length}
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
        
        {(workflows || []).length === 0 && (
          <Grid item xs={12}>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="body2" color="text.secondary">
                No workflows found. Create your first workflow!
              </Typography>
            </Box>
          </Grid>
        )}
      </Grid>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingWorkflow ? 'Edit Workflow' : 'Create New Workflow'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <TextField
              label="Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              fullWidth
              required
              sx={{ gridColumn: '1 / -1' }}
            />
            <TextField
              label="Description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              fullWidth
              multiline
              rows={3}
              sx={{ gridColumn: '1 / -1' }}
            />
            <FormControl fullWidth>
              <InputLabel>Trigger</InputLabel>
              <Select
                value={formData.trigger}
                label="Trigger"
                onChange={(e) => handleInputChange('trigger', e.target.value)}
              >
                <MenuItem value="manual">Manual</MenuItem>
                <MenuItem value="automatic">Automatic</MenuItem>
                <MenuItem value="scheduled">Scheduled</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={formData.status}
                label="Status"
                onChange={(e) => handleInputChange('status', e.target.value)}
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.name}
          >
            {editingWorkflow ? 'Update' : 'Create'}
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

export default CRMWorkflows;
