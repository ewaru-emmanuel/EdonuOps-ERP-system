import React, { useState } from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, Chip, IconButton, TextField, Card, CardContent, Grid,
  Alert, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions,
  FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  LocationOn as LocationIcon,
  Warehouse as WarehouseIcon,
  GridOn as ZoneIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const SmartLocationManagement = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const { data: locations, loading, error, refresh } = useRealTimeData('/api/inventory/wms/locations');
  const { data: warehouses } = useRealTimeData('/api/inventory/wms/warehouses');

  const handleOpenDialog = (location = null) => {
    setSelectedLocation(location);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedLocation(null);
  };

  const getLocationTypeChip = (type) => {
    switch (type) {
      case 'zone':
        return <Chip label="Zone" color="primary" size="small" />;
      case 'aisle':
        return <Chip label="Aisle" color="secondary" size="small" />;
      case 'rack':
        return <Chip label="Rack" color="warning" size="small" />;
      case 'level':
        return <Chip label="Level" color="info" size="small" />;
      case 'bin':
        return <Chip label="Bin" color="success" size="small" />;
      default:
        return <Chip label={type} color="default" size="small" />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading locations: {error.message}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Location Management
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Organize your warehouse with zones, aisles, racks, and bins
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Locations
              </Typography>
              <Typography variant="h4">
                {locations?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'primary.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <ZoneIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography color="primary.main" gutterBottom>
                  Zones
                </Typography>
              </Box>
              <Typography variant="h4" color="primary.main">
                {locations?.filter(l => l.type === 'zone').length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'success.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <LocationIcon sx={{ color: 'success.main', mr: 1 }} />
                <Typography color="success.main" gutterBottom>
                  Bins
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {locations?.filter(l => l.type === 'bin').length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'warning.50' }}>
            <CardContent>
              <Typography color="warning.main" gutterBottom>
                Utilization
              </Typography>
              <Typography variant="h4" color="warning.main">
                78%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">
          Warehouse Locations
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Location
        </Button>
      </Box>

      {/* Locations Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Location Code</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Warehouse</TableCell>
              <TableCell>Parent Location</TableCell>
              <TableCell>Capacity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {locations?.map((location) => (
              <TableRow key={location.id} hover>
                <TableCell>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {location.location_code}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="subtitle2">
                    {location.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {location.description}
                  </Typography>
                </TableCell>
                <TableCell>
                  {getLocationTypeChip(location.type)}
                </TableCell>
                <TableCell>
                  {location.warehouse_name || 'Main Warehouse'}
                </TableCell>
                <TableCell>
                  {location.parent_location_code || '-'}
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {location.capacity || 'Unlimited'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={location.status || 'Active'} 
                    color={location.status === 'active' ? 'success' : 'default'} 
                    size="small" 
                  />
                </TableCell>
                <TableCell align="center">
                  <IconButton size="small" onClick={() => handleOpenDialog(location)}>
                    <EditIcon />
                  </IconButton>
                  <IconButton size="small" color="error">
                    <DeleteIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {(!locations || locations.length === 0) && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No locations found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Create your first warehouse location to get started
          </Typography>
        </Box>
      )}

      {/* Location Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedLocation ? 'Edit Location' : 'Add New Location'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Location Code"
                defaultValue={selectedLocation?.location_code || ''}
                helperText="Unique identifier (e.g., A-01-01)"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Location Name"
                defaultValue={selectedLocation?.name || ''}
                helperText="Display name for the location"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Location Type</InputLabel>
                <Select
                  value={selectedLocation?.type || 'bin'}
                  label="Location Type"
                >
                  <MenuItem value="zone">Zone</MenuItem>
                  <MenuItem value="aisle">Aisle</MenuItem>
                  <MenuItem value="rack">Rack</MenuItem>
                  <MenuItem value="level">Level</MenuItem>
                  <MenuItem value="bin">Bin</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Warehouse</InputLabel>
                <Select
                  value={selectedLocation?.warehouse_id || ''}
                  label="Warehouse"
                >
                  {warehouses?.map((warehouse) => (
                    <MenuItem key={warehouse.id} value={warehouse.id}>
                      {warehouse.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Parent Location"
                defaultValue={selectedLocation?.parent_location_code || ''}
                helperText="Parent location code (optional)"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Capacity"
                type="number"
                defaultValue={selectedLocation?.capacity || ''}
                helperText="Maximum capacity (leave empty for unlimited)"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                defaultValue={selectedLocation?.description || ''}
                helperText="Additional details about this location"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained">
            {selectedLocation ? 'Update' : 'Create'} Location
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SmartLocationManagement;
