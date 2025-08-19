import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon
} from '@mui/icons-material';

const AuditFilters = () => {
  const [filters, setFilters] = useState([
    {
      id: 1,
      name: 'Critical Security Events',
      description: 'Filter for critical security-related events',
      severity: ['Critical', 'Error'],
      modules: ['Authentication', 'User Management'],
      users: ['admin@company.com'],
      active: true
    },
    {
      id: 2,
      name: 'Data Access Monitoring',
      description: 'Monitor all data access and export activities',
      severity: ['Warning', 'Info'],
      modules: ['Finance', 'CRM'],
      users: [],
      active: true
    },
    {
      id: 3,
      name: 'System Events',
      description: 'Track system-level events and backups',
      severity: ['Info'],
      modules: ['System'],
      users: ['system@company.com'],
      active: false
    }
  ]);

  const [openDialog, setOpenDialog] = useState(false);
  const [editingFilter, setEditingFilter] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    severity: [],
    modules: [],
    users: '',
    active: true
  });

  const severityOptions = ['Critical', 'Warning', 'Error', 'Info'];
  const moduleOptions = ['Authentication', 'Finance', 'CRM', 'User Management', 'System', 'Inventory', 'Procurement'];

  const handleCreateFilter = () => {
    setEditingFilter(null);
    setFormData({
      name: '',
      description: '',
      severity: [],
      modules: [],
      users: '',
      active: true
    });
    setOpenDialog(true);
  };

  const handleEditFilter = (filter) => {
    setEditingFilter(filter);
    setFormData({
      name: filter.name,
      description: filter.description,
      severity: filter.severity,
      modules: filter.modules,
      users: filter.users.join(', '),
      active: filter.active
    });
    setOpenDialog(true);
  };

  const handleSaveFilter = () => {
    const filterData = {
      ...formData,
      users: formData.users ? formData.users.split(',').map(u => u.trim()) : []
    };

    if (editingFilter) {
      setFilters(filters.map(f => 
        f.id === editingFilter.id 
          ? { ...f, ...filterData }
          : f
      ));
    } else {
      const newFilter = {
        id: Date.now(),
        ...filterData
      };
      setFilters([...filters, newFilter]);
    }
    setOpenDialog(false);
  };

  const handleDeleteFilter = (id) => {
    setFilters(filters.filter(f => f.id !== id));
  };

  const handleToggleFilter = (id) => {
    setFilters(filters.map(f => 
      f.id === id ? { ...f, active: !f.active } : f
    ));
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Audit Filters</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateFilter}
        >
          Create Filter
        </Button>
      </Box>

      <Grid container spacing={3}>
        {filters.map((filter) => (
          <Grid item xs={12} md={6} lg={4} key={filter.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6" component="div">
                    {filter.name}
                  </Typography>
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleEditFilter(filter)}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDeleteFilter(filter.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
                
                <Typography color="textSecondary" gutterBottom>
                  {filter.description}
                </Typography>
                
                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Severity:
                  </Typography>
                  <Box display="flex" gap={0.5} flexWrap="wrap">
                    {filter.severity.map((sev) => (
                      <Chip
                        key={sev}
                        label={sev}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
                
                <Box mb={2}>
                  <Typography variant="body2" color="textSecondary" gutterBottom>
                    Modules:
                  </Typography>
                  <Box display="flex" gap={0.5} flexWrap="wrap">
                    {filter.modules.map((module) => (
                      <Chip
                        key={module}
                        label={module}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
                
                {filter.users.length > 0 && (
                  <Box mb={2}>
                    <Typography variant="body2" color="textSecondary" gutterBottom>
                      Users:
                    </Typography>
                    <Typography variant="body2">
                      {filter.users.join(', ')}
                    </Typography>
                  </Box>
                )}
                
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <FormControlLabel
                    control={
                      <Switch
                        checked={filter.active}
                        onChange={() => handleToggleFilter(filter.id)}
                      />
                    }
                    label="Active"
                  />
                  <Chip
                    label={filter.active ? 'Active' : 'Inactive'}
                    color={filter.active ? 'success' : 'default'}
                    size="small"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingFilter ? 'Edit Filter' : 'Create New Filter'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Filter Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Severity Levels</InputLabel>
                <Select
                  multiple
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  label="Severity Levels"
                  renderValue={(selected) => (
                    <Box display="flex" gap={0.5} flexWrap="wrap">
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  {severityOptions.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Modules</InputLabel>
                <Select
                  multiple
                  value={formData.modules}
                  onChange={(e) => setFormData({ ...formData, modules: e.target.value })}
                  label="Modules"
                  renderValue={(selected) => (
                    <Box display="flex" gap={0.5} flexWrap="wrap">
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  {moduleOptions.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Users (comma-separated)"
                value={formData.users}
                onChange={(e) => setFormData({ ...formData, users: e.target.value })}
                placeholder="user1@company.com, user2@company.com"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.active}
                    onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                  />
                }
                label="Active Filter"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveFilter} variant="contained">
            {editingFilter ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AuditFilters;



