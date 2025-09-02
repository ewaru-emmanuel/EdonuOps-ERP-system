import React, { useState } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Paper, Chip, Avatar,
  Button, IconButton, LinearProgress, Tabs, Tab,
  List, ListItem, ListItemText, ListItemAvatar, ListItemIcon,
  Switch, FormControlLabel, TextField, FormControl, InputLabel, Select, MenuItem,
  useTheme, useMediaQuery, Divider, Dialog, DialogTitle, DialogContent, DialogActions,
  Alert, Snackbar
} from '@mui/material';
import {
  Warehouse, Refresh, Save, Add, Edit, Delete,
  LocationOn
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const SmartSettings = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activeTab, setActiveTab] = useState(0);
  
  // State for dialogs
  const [uomDialogOpen, setUomDialogOpen] = useState(false);
  const [zoneDialogOpen, setZoneDialogOpen] = useState(false);
  const [aisleDialogOpen, setAisleDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Form states
  const [uomForm, setUomForm] = useState({ name: '', code: '', description: '', is_base_unit: false });
  const [zoneForm, setZoneForm] = useState({ name: '', description: '', capacity: '' });
  const [aisleForm, setAisleForm] = useState({ name: '', zone_id: '', length: '', width: '', height: '' });

  // Real-time data hooks
  const { data: uoms, loading: uomsLoading } = useRealTimeData('/api/inventory/core/uom');
  const { data: categories, loading: categoriesLoading } = useRealTimeData('/api/inventory/core/categories');
  const { data: zones, loading: zonesLoading } = useRealTimeData('/api/inventory/wms/warehouse-zones');
  const { data: aisles, loading: aislesLoading } = useRealTimeData('/api/inventory/wms/warehouse-aisles');

  // Real-time data from API
  const uomData = uoms || [];
  const categoriesData = categories || [];
  const zonesData = zones || [];
  const aislesData = aisles || [];

  // UoM Management Functions
  const handleAddUoM = () => {
    setEditingItem(null);
    setUomForm({ name: '', code: '', description: '', is_base_unit: false });
    setUomDialogOpen(true);
  };

  const handleEditUoM = (uom) => {
    setEditingItem(uom);
    setUomForm({
      name: uom.name,
      code: uom.code,
      description: uom.description,
      is_base_unit: uom.is_base_unit
    });
    setUomDialogOpen(true);
  };

  const handleSaveUoM = async () => {
    try {
      if (editingItem) {
        await apiClient.put(`/api/inventory/core/uom/${editingItem.id}`, uomForm);
      } else {
                  await apiClient.post('/api/inventory/core/uom', uomForm);
      }
      
      setSnackbar({
        open: true,
        message: `UoM ${editingItem ? 'updated' : 'created'} successfully!`,
        severity: 'success'
      });
      setUomDialogOpen(false);
      // Refresh data
      window.location.reload();
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Error: ${error.message}`,
        severity: 'error'
      });
    }
  };

  const handleDeleteUoM = async (uomId) => {
    if (window.confirm('Are you sure you want to delete this UoM?')) {
      try {
        await apiClient.delete(`/api/inventory/core/uom/${uomId}`);
        
        setSnackbar({
          open: true,
          message: 'UoM deleted successfully!',
          severity: 'success'
        });
        // Refresh data
        window.location.reload();
      } catch (error) {
        setSnackbar({
          open: true,
          message: `Error: ${error.message}`,
          severity: 'error'
        });
      }
    }
  };

  // Zone Management Functions
  const handleAddZone = () => {
    setEditingItem(null);
    setZoneForm({ name: '', description: '', capacity: '' });
    setZoneDialogOpen(true);
  };

  const handleEditZone = (zone) => {
    setEditingItem(zone);
    setZoneForm({
      name: zone.name,
      description: zone.description,
      capacity: zone.capacity.toString()
    });
    setZoneDialogOpen(true);
  };

  const handleSaveZone = async () => {
    try {
      const zoneData = {
        ...zoneForm,
        capacity: parseInt(zoneForm.capacity) || 0
      };
      
      if (editingItem) {
        await apiClient.put(`/api/inventory/wms/warehouse-zones/${editingItem.id}`, zoneData);
      } else {
                  await apiClient.post('/api/inventory/wms/warehouse-zones', zoneData);
      }
      
      setSnackbar({
        open: true,
        message: `Zone ${editingItem ? 'updated' : 'created'} successfully!`,
        severity: 'success'
      });
      setZoneDialogOpen(false);
      // Refresh data
      window.location.reload();
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Error: ${error.message}`,
        severity: 'error'
      });
    }
  };

  // Aisle Management Functions
  const handleAddAisle = () => {
    setEditingItem(null);
    setAisleForm({ name: '', zone_id: '', length: '', width: '', height: '' });
    setAisleDialogOpen(true);
  };

  const handleEditAisle = (aisle) => {
    setEditingItem(aisle);
    setAisleForm({
      name: aisle.name,
      zone_id: aisle.zone_id.toString(),
      length: aisle.length.toString(),
      width: aisle.width.toString(),
      height: aisle.height.toString()
    });
    setAisleDialogOpen(true);
  };

  const handleSaveAisle = async () => {
    try {
      const aisleData = {
        ...aisleForm,
        zone_id: parseInt(aisleForm.zone_id) || 1,
        length: parseInt(aisleForm.length) || 0,
        width: parseInt(aisleForm.width) || 0,
        height: parseInt(aisleForm.height) || 0
      };
      
      if (editingItem) {
        await apiClient.put(`/api/inventory/wms/warehouse-aisles/${editingItem.id}`, aisleData);
      } else {
                  await apiClient.post('/api/inventory/wms/warehouse-aisles', aisleData);
      }
      
      setSnackbar({
        open: true,
        message: `Aisle ${editingItem ? 'updated' : 'created'} successfully!`,
        severity: 'success'
      });
      setAisleDialogOpen(false);
      // Refresh data
      window.location.reload();
    } catch (error) {
      setSnackbar({
        open: true,
        message: `Error: ${error.message}`,
        severity: 'error'
      });
    }
  };


  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold' }}>
          ⚙️ Smart Settings & Configuration
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            sx={{ fontWeight: 'bold' }}
          >
            Reset
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            sx={{ fontWeight: 'bold' }}
          >
            Save All
          </Button>
        </Box>
      </Box>

      {/* Settings Tabs */}
      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant={isMobile ? "scrollable" : "fullWidth"}
          scrollButtons={isMobile ? "auto" : false}
        >
          <Tab label="Warehouse Config" />
          <Tab label="UoM Management" />
          <Tab label="Zone & Aisle Management" />
          <Tab label="System Preferences" />
          <Tab label="Mobile WMS" />
        </Tabs>
      </Paper>

      {/* Warehouse Configuration Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  🏭 Warehouse Configuration
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <TextField
                    fullWidth
                    label="Warehouse Name"
                    defaultValue="Main Distribution Center"
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    fullWidth
                    label="Warehouse Code"
                    defaultValue="WH-001"
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    fullWidth
                    label="Address"
                    multiline
                    rows={3}
                    defaultValue="123 Warehouse Street, Industrial District"
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    fullWidth
                    label="Contact Person"
                    defaultValue="John Smith"
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    fullWidth
                    label="Contact Phone"
                    defaultValue="+1-555-0123"
                    sx={{ mb: 2 }}
                  />
                  <TextField
                    fullWidth
                    label="Contact Email"
                    defaultValue="warehouse@company.com"
                    sx={{ mb: 2 }}
                  />
                </Box>
                
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Capacity Settings
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Total Capacity"
                      type="number"
                      defaultValue="10000"
                      InputProps={{ endAdornment: 'sq ft' }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Used Capacity"
                      type="number"
                      defaultValue="7500"
                      InputProps={{ endAdornment: 'sq ft' }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  📍 Location Hierarchy
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Warehouse Structure
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemIcon>
                        <Warehouse color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Main Warehouse"
                        secondary="4 zones, 12 aisles, 48 racks"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <LocationOn color="secondary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Zone A - Picking"
                        secondary="3 aisles, 12 racks, 144 locations"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <LocationOn color="secondary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Zone B - Storage"
                        secondary="4 aisles, 16 racks, 192 locations"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <LocationOn color="secondary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Zone C - Receiving"
                        secondary="2 aisles, 8 racks, 96 locations"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon>
                        <LocationOn color="secondary" />
                      </ListItemIcon>
                      <ListItemText
                        primary="Zone D - Shipping"
                        secondary="3 aisles, 12 racks, 144 locations"
                      />
                    </ListItem>
                  </List>
                </Box>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                    Zone Management
                  </Typography>
                  <List dense>
                    {zonesData.map((zone) => (
                      <ListItem key={zone.id} sx={{ px: 0, mb: 1 }}>
                        <ListItemIcon>
                          <LocationOn color="secondary" />
                        </ListItemIcon>
                        <ListItemText
                          primary={zone.name}
                          secondary={`Capacity: ${zone.capacity} | ${zone.description}`}
                        />
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <IconButton size="small" color="primary" onClick={() => handleEditZone(zone)}>
                            <Edit />
                          </IconButton>
                        </Box>
                      </ListItem>
                    ))}
                  </List>
                </Box>
                
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  fullWidth
                  onClick={handleAddZone}
                >
                  Add New Zone
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* UoM Management Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" fontWeight="bold">
                    📏 Unit of Measure Management
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    size="small"
                    onClick={handleAddUoM}
                  >
                    Add UoM
                  </Button>
                </Box>
                
                <List>
                  {uomData.map((uom) => (
                    <ListItem key={uom.id} sx={{ px: 0, mb: 1 }}>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: uom.is_base_unit ? 'primary.light' : 'secondary.light' }}>
                          {uom.is_base_unit ? 'B' : 'U'}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" fontWeight="bold">
                              {uom.code} - {uom.name}
                            </Typography>
                            {uom.is_base_unit && (
                              <Chip label="Base Unit" size="small" color="primary" />
                            )}
                          </Box>
                        }
                        secondary={`Unit of measure for ${uom.name.toLowerCase()}`}
                      />
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton size="small" color="primary" onClick={() => handleEditUoM(uom)}>
                          <Edit />
                        </IconButton>
                        <IconButton size="small" color="error" onClick={() => handleDeleteUoM(uom.id)}>
                          <Delete />
                        </IconButton>
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  🔄 UoM Conversions
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Conversion Factors
                  </Typography>
                  <List dense>
                    <ListItem>
                      <ListItemText
                        primary="1 Pallet = 48 Cases"
                        secondary="PLT → CS conversion"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="1 Case = 12 Each"
                        secondary="CS → EA conversion"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="1 Pallet = 576 Each"
                        secondary="PLT → EA conversion"
                      />
                    </ListItem>
                  </List>
                </Box>
                
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  fullWidth
                >
                  Add Conversion
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Zone & Aisle Management Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" fontWeight="bold">
                    📍 Zone Management
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    size="small"
                    onClick={handleAddZone}
                  >
                    Add Zone
                  </Button>
                </Box>
                
                <List>
                  {zonesData.map((zone) => (
                    <ListItem key={zone.id} sx={{ px: 0, mb: 1 }}>
                      <ListItemIcon>
                        <LocationOn color="secondary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={zone.name}
                        secondary={`Capacity: ${zone.capacity} | ${zone.description}`}
                      />
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton size="small" color="primary" onClick={() => handleEditZone(zone)}>
                          <Edit />
                        </IconButton>
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" fontWeight="bold">
                    🛤️ Aisle Management
                  </Typography>
                  <Button
                    variant="contained"
                    startIcon={<Add />}
                    size="small"
                    onClick={handleAddAisle}
                  >
                    Add Aisle
                  </Button>
                </Box>
                
                <List>
                  {aislesData && aislesData.length > 0 ? aislesData.map((aisle) => (
                    <ListItem key={aisle.id} sx={{ px: 0, mb: 1 }}>
                      <ListItemIcon>
                        <LocationOn color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={aisle.name}
                        secondary={`Zone: ${aisle.zone_id} | Dimensions: ${aisle.length}'×${aisle.width}'×${aisle.height}'`}
                      />
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <IconButton size="small" color="primary" onClick={() => handleEditAisle(aisle)}>
                          <Edit />
                        </IconButton>
                      </Box>
                    </ListItem>
                  )) : (
                    <ListItem>
                      <ListItemText
                        primary="No aisles configured"
                        secondary="Add aisles to organize your warehouse layout"
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* System Preferences Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  ⚙️ General Settings
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Real-time data synchronization"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Automatic stock level updates"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Enable predictive analytics"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Mobile WMS notifications"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Advanced reporting features"
                  />
                </Box>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Performance Settings
                </Typography>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Data Refresh Interval</InputLabel>
                  <Select defaultValue="30" label="Data Refresh Interval">
                    <MenuItem value="15">15 seconds</MenuItem>
                    <MenuItem value="30">30 seconds</MenuItem>
                    <MenuItem value="60">1 minute</MenuItem>
                    <MenuItem value="300">5 minutes</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Cache Duration</InputLabel>
                  <Select defaultValue="300" label="Cache Duration">
                    <MenuItem value="60">1 minute</MenuItem>
                    <MenuItem value="300">5 minutes</MenuItem>
                    <MenuItem value="900">15 minutes</MenuItem>
                    <MenuItem value="3600">1 hour</MenuItem>
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  🔔 Notification Settings
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Low stock alerts"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Predictive stockout warnings"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Performance degradation alerts"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="System maintenance notifications"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Security breach alerts"
                  />
                </Box>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Alert Thresholds
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Low Stock %"
                      type="number"
                      defaultValue="20"
                      InputProps={{ endAdornment: '%' }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Critical Stock %"
                      type="number"
                      defaultValue="5"
                      InputProps={{ endAdornment: '%' }}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Mobile WMS Tab */}
      {activeTab === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  📱 Mobile WMS Configuration
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Enable barcode scanning"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="GPS location tracking"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Real-time synchronization"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Offline mode support"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Voice commands"
                  />
                </Box>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Device Settings
                </Typography>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Scanner Type</InputLabel>
                  <Select defaultValue="camera" label="Scanner Type">
                    <MenuItem value="camera">Camera Scanner</MenuItem>
                    <MenuItem value="laser">Laser Scanner</MenuItem>
                    <MenuItem value="both">Both</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>GPS Accuracy</InputLabel>
                  <Select defaultValue="high" label="GPS Accuracy">
                    <MenuItem value="low">Low (10m)</MenuItem>
                    <MenuItem value="medium">Medium (5m)</MenuItem>
                    <MenuItem value="high">High (1m)</MenuItem>
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  🔐 Security Settings
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Two-factor authentication"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Session timeout"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Biometric login"
                  />
                  <FormControlLabel
                    control={<Switch defaultChecked />}
                    label="Activity logging"
                  />
                  <FormControlLabel
                    control={<Switch />}
                    label="Encrypted data transmission"
                  />
                </Box>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
                  Session Management
                </Typography>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Session Timeout</InputLabel>
                  <Select defaultValue="30" label="Session Timeout">
                    <MenuItem value="15">15 minutes</MenuItem>
                    <MenuItem value="30">30 minutes</MenuItem>
                    <MenuItem value="60">1 hour</MenuItem>
                    <MenuItem value="480">8 hours</MenuItem>
                  </Select>
                </FormControl>
                
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Max Login Attempts</InputLabel>
                  <Select defaultValue="3" label="Max Login Attempts">
                    <MenuItem value="3">3 attempts</MenuItem>
                    <MenuItem value="5">5 attempts</MenuItem>
                    <MenuItem value="10">10 attempts</MenuItem>
                  </Select>
                </FormControl>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Loading States */}
      {(uomsLoading || categoriesLoading || zonesLoading || aislesLoading) && (
        <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }}>
          <LinearProgress />
        </Box>
      )}

      {/* UoM Dialog */}
      <Dialog open={uomDialogOpen} onClose={() => setUomDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? 'Edit UoM' : 'Add New UoM'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Name"
              value={uomForm.name}
              onChange={(e) => setUomForm({ ...uomForm, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Code"
              value={uomForm.code}
              onChange={(e) => setUomForm({ ...uomForm, code: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description"
              value={uomForm.description}
              onChange={(e) => setUomForm({ ...uomForm, description: e.target.value })}
              sx={{ mb: 2 }}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={uomForm.is_base_unit}
                  onChange={(e) => setUomForm({ ...uomForm, is_base_unit: e.target.checked })}
                />
              }
              label="Is Base Unit"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUomDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveUoM} variant="contained">
            {editingItem ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Zone Dialog */}
      <Dialog open={zoneDialogOpen} onClose={() => setZoneDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? 'Edit Zone' : 'Add New Zone'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Zone Name"
              value={zoneForm.name}
              onChange={(e) => setZoneForm({ ...zoneForm, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description"
              value={zoneForm.description}
              onChange={(e) => setZoneForm({ ...zoneForm, description: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Capacity"
              type="number"
              value={zoneForm.capacity}
              onChange={(e) => setZoneForm({ ...zoneForm, capacity: e.target.value })}
              InputProps={{ endAdornment: 'sq ft' }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setZoneDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveZone} variant="contained">
            {editingItem ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Aisle Dialog */}
      <Dialog open={aisleDialogOpen} onClose={() => setAisleDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingItem ? 'Edit Aisle' : 'Add New Aisle'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Aisle Name"
              value={aisleForm.name}
              onChange={(e) => setAisleForm({ ...aisleForm, name: e.target.value })}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Zone</InputLabel>
              <Select
                value={aisleForm.zone_id}
                onChange={(e) => setAisleForm({ ...aisleForm, zone_id: e.target.value })}
                label="Zone"
              >
                {zonesData.map((zone) => (
                  <MenuItem key={zone.id} value={zone.id}>
                    {zone.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Grid container spacing={2}>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  label="Length"
                  type="number"
                  value={aisleForm.length}
                  onChange={(e) => setAisleForm({ ...aisleForm, length: e.target.value })}
                  InputProps={{ endAdornment: 'ft' }}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  label="Width"
                  type="number"
                  value={aisleForm.width}
                  onChange={(e) => setAisleForm({ ...aisleForm, width: e.target.value })}
                  InputProps={{ endAdornment: 'ft' }}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  label="Height"
                  type="number"
                  value={aisleForm.height}
                  onChange={(e) => setAisleForm({ ...aisleForm, height: e.target.value })}
                  InputProps={{ endAdornment: 'ft' }}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAisleDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveAisle} variant="contained">
            {editingItem ? 'Update' : 'Create'}
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
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SmartSettings;
