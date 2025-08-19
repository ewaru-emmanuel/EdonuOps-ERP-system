import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Paper,
  Chip,
  IconButton
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  DragIndicator as DragIcon
} from '@mui/icons-material';

const DashboardBuilder = () => {
  const [dashboards, setDashboards] = useState([
    {
      id: 1,
      name: 'Executive Dashboard',
      description: 'High-level overview of business metrics',
      widgets: 8,
      status: 'Active',
      lastModified: '2024-01-15'
    },
    {
      id: 2,
      name: 'Sales Analytics',
      description: 'Detailed sales performance and trends',
      widgets: 12,
      status: 'Active',
      lastModified: '2024-01-14'
    },
    {
      id: 3,
      name: 'Financial Overview',
      description: 'Financial metrics and reporting',
      widgets: 6,
      status: 'Draft',
      lastModified: '2024-01-13'
    }
  ]);

  const [openDialog, setOpenDialog] = useState(false);
  const [editingDashboard, setEditingDashboard] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '' });

  const handleCreateDashboard = () => {
    setEditingDashboard(null);
    setFormData({ name: '', description: '' });
    setOpenDialog(true);
  };

  const handleEditDashboard = (dashboard) => {
    setEditingDashboard(dashboard);
    setFormData({ name: dashboard.name, description: dashboard.description });
    setOpenDialog(true);
  };

  const handleSaveDashboard = () => {
    if (editingDashboard) {
      setDashboards(dashboards.map(d => 
        d.id === editingDashboard.id 
          ? { ...d, ...formData, lastModified: new Date().toISOString().split('T')[0] }
          : d
      ));
    } else {
      const newDashboard = {
        id: Date.now(),
        ...formData,
        widgets: 0,
        status: 'Draft',
        lastModified: new Date().toISOString().split('T')[0]
      };
      setDashboards([...dashboards, newDashboard]);
    }
    setOpenDialog(false);
  };

  const handleDeleteDashboard = (id) => {
    setDashboards(dashboards.filter(d => d.id !== id));
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Dashboard Builder</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateDashboard}
        >
          Create Dashboard
        </Button>
      </Box>

      <Grid container spacing={3}>
        {dashboards.map((dashboard) => (
          <Grid item xs={12} md={6} lg={4} key={dashboard.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" component="div">
                    {dashboard.name}
                  </Typography>
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleEditDashboard(dashboard)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteDashboard(dashboard.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
                
                <Typography color="textSecondary" gutterBottom>
                  {dashboard.description}
                </Typography>
                
                <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                  <Chip
                    label={dashboard.status}
                    color={dashboard.status === 'Active' ? 'success' : 'default'}
                    size="small"
                  />
                  <Typography variant="body2" color="textSecondary">
                    {dashboard.widgets} widgets
                  </Typography>
                </Box>
                
                <Typography variant="body2" color="textSecondary" mt={1}>
                  Last modified: {dashboard.lastModified}
                </Typography>
                
                <Button
                  variant="outlined"
                  fullWidth
                  sx={{ mt: 2 }}
                  startIcon={<DragIcon />}
                >
                  Open Builder
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingDashboard ? 'Edit Dashboard' : 'Create New Dashboard'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Dashboard Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            margin="normal"
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveDashboard} variant="contained">
            {editingDashboard ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DashboardBuilder;


