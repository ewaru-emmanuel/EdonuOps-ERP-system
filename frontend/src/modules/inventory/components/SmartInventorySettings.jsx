import React, { useState } from 'react';
import {
  Box, Typography, Paper, Grid, Card, CardContent, Button, Chip,
  Alert, CircularProgress, TextField, Dialog, DialogTitle, DialogContent, DialogActions,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, IconButton,
  Snackbar, FormControlLabel, Checkbox
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Settings as SettingsIcon,
  Category as CategoryIcon,
  Straighten as UOMIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const SmartInventorySettings = () => {
  const [openCategoryDialog, setOpenCategoryDialog] = useState(false);
  const [openUOMDialog, setOpenUOMDialog] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Form states
  const [categoryForm, setCategoryForm] = useState({ name: '', description: '' });
  const [uomForm, setUomForm] = useState({ code: '', name: '', description: '', is_base_unit: false });
  const [settingsForm, setSettingsForm] = useState({
    default_warehouse: 'Main Warehouse',
    low_stock_threshold: 10,
    auto_reorder_quantity: 50
  });
  
  // Real-time data hooks
  const { data: categories, loading: categoriesLoading, refresh: refreshCategories } = useRealTimeData('/api/inventory/core/categories');
  const { data: uoms, loading: uomsLoading, refresh: refreshUOMs } = useRealTimeData('/api/inventory/core/uom');

  const isLoading = categoriesLoading || uomsLoading || loading;

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleOpenDialog = (type, item = null) => {
    setSelectedItem(item);
    if (type === 'category') {
      setCategoryForm({
        name: item?.name || '',
        description: item?.description || ''
      });
      setOpenCategoryDialog(true);
    } else if (type === 'uom') {
      setUomForm({
        code: item?.code || '',
        name: item?.name || '',
        description: item?.description || '',
        is_base_unit: item?.is_base_unit || false
      });
      setOpenUOMDialog(true);
    }
  };

  const handleCloseDialog = (type) => {
    setSelectedItem(null);
    if (type === 'category') {
      setOpenCategoryDialog(false);
      setCategoryForm({ name: '', description: '' });
    } else if (type === 'uom') {
      setOpenUOMDialog(false);
      setUomForm({ code: '', name: '', description: '', is_base_unit: false });
    }
  };

  const handleCategorySubmit = async () => {
    if (!categoryForm.name.trim()) {
      showSnackbar('Category name is required', 'error');
      return;
    }

    setLoading(true);
    try {
      console.log('Saving category:', categoryForm);
      
      if (selectedItem) {
        // Update existing category
        const response = await apiClient.put(`/api/inventory/core/categories/${selectedItem.id}`, categoryForm);
        showSnackbar('Category updated successfully');
      } else {
        // Create new category
        const response = await apiClient.post('/api/inventory/core/categories', categoryForm);
        showSnackbar('Category created successfully');
      }
      
      handleCloseDialog('category');
      refreshCategories();
    } catch (error) {
      console.error('Error saving category:', error);
      showSnackbar('Error saving category', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleUOMSubmit = async () => {
    if (!uomForm.code.trim() || !uomForm.name.trim()) {
      showSnackbar('Code and name are required', 'error');
      return;
    }

    setLoading(true);
    try {
      console.log('Saving UOM:', uomForm);
      
      if (selectedItem) {
        // Update existing UOM
        const response = await apiClient.put(`/api/inventory/core/uom/${selectedItem.id}`, uomForm);
        showSnackbar('Unit of Measure updated successfully');
      } else {
        // Create new UOM
        const response = await apiClient.post('/api/inventory/core/uom', uomForm);
        showSnackbar('Unit of Measure created successfully');
      }
      
      handleCloseDialog('uom');
      refreshUOMs();
    } catch (error) {
      console.error('Error saving UoM:', error);
      showSnackbar('Error saving Unit of Measure', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (!window.confirm('Are you sure you want to delete this category?')) {
      return;
    }

    setLoading(true);
    try {
      console.log('Deleting category:', categoryId);
      const response = await apiClient.delete(`/api/inventory/core/categories/${categoryId}`);
      showSnackbar('Category deleted successfully');
      refreshCategories();
    } catch (error) {
      console.error('Error deleting category:', error);
      showSnackbar('Error deleting category', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUOM = async (uomId) => {
    if (!window.confirm('Are you sure you want to delete this Unit of Measure?')) {
      return;
    }

    setLoading(true);
    try {
      console.log('Deleting UOM:', uomId);
      const response = await apiClient.delete(`/api/inventory/core/uom/${uomId}`);
      showSnackbar('Unit of Measure deleted successfully');
      refreshUOMs();
    } catch (error) {
      console.error('Error deleting UoM:', error);
      showSnackbar('Error deleting Unit of Measure', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      // Mock API call - no authentication
      console.log('Mock save settings:', settingsForm);
      showSnackbar('Settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      showSnackbar('Error saving settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Inventory Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure categories, units of measure, and other inventory settings
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Categories */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CategoryIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">
                    Product Categories
                  </Typography>
                </Box>
                <Button
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={() => handleOpenDialog('category')}
                >
                  Add Category
                </Button>
              </Box>
              
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {categories?.map((category) => (
                      <TableRow key={category.id}>
                        <TableCell>
                          <Typography variant="subtitle2">
                            {category.name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {category.description || 'No description'}
                          </Typography>
                        </TableCell>
                        <TableCell align="center">
                          <IconButton 
                            size="small" 
                            onClick={() => handleOpenDialog('category', category)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => handleDeleteCategory(category.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {(!categories || categories.length === 0) && (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    No categories found. Add your first category to get started.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Units of Measure */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <UOMIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">
                    Units of Measure
                  </Typography>
                </Box>
                <Button
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={() => handleOpenDialog('uom')}
                >
                  Add UoM
                </Button>
              </Box>
              
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Code</TableCell>
                      <TableCell>Name</TableCell>
                      <TableCell>Base Unit</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {uoms?.map((uom) => (
                      <TableRow key={uom.id}>
                        <TableCell>
                          <Typography variant="subtitle2">
                            {uom.code}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {uom.name}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={uom.is_base_unit ? 'Yes' : 'No'} 
                            size="small" 
                            color={uom.is_base_unit ? 'success' : 'default'}
                          />
                        </TableCell>
                        <TableCell align="center">
                          <IconButton 
                            size="small" 
                            onClick={() => handleOpenDialog('uom', uom)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => handleDeleteUOM(uom.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {(!uoms || uoms.length === 0) && (
                <Box sx={{ textAlign: 'center', py: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    No units of measure found. Add your first UoM to get started.
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* General Settings */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SettingsIcon sx={{ mr: 1, color: 'primary.main' }} />
                <Typography variant="h6">
                  General Settings
                </Typography>
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Default Warehouse"
                    value={settingsForm.default_warehouse}
                    onChange={(e) => setSettingsForm({...settingsForm, default_warehouse: e.target.value})}
                    helperText="Default warehouse for new stock levels"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Low Stock Alert Threshold"
                    type="number"
                    value={settingsForm.low_stock_threshold}
                    onChange={(e) => setSettingsForm({...settingsForm, low_stock_threshold: parseInt(e.target.value)})}
                    helperText="Percentage below reorder point to trigger alerts"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="Auto-reorder Quantity"
                    type="number"
                    value={settingsForm.auto_reorder_quantity}
                    onChange={(e) => setSettingsForm({...settingsForm, auto_reorder_quantity: parseInt(e.target.value)})}
                    helperText="Default quantity for automatic reorders"
                  />
                </Grid>
              </Grid>

              <Box sx={{ mt: 3 }}>
                <Button 
                  variant="contained" 
                  color="primary"
                  onClick={handleSaveSettings}
                  disabled={loading}
                >
                  {loading ? <CircularProgress size={20} /> : 'Save Settings'}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Category Dialog */}
      <Dialog open={openCategoryDialog} onClose={() => handleCloseDialog('category')} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedItem ? 'Edit Category' : 'Add New Category'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Category Name"
            value={categoryForm.name}
            onChange={(e) => setCategoryForm({...categoryForm, name: e.target.value})}
            sx={{ mt: 1, mb: 2 }}
          />
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={3}
            value={categoryForm.description}
            onChange={(e) => setCategoryForm({...categoryForm, description: e.target.value})}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleCloseDialog('category')} disabled={loading}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleCategorySubmit}
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : (selectedItem ? 'Update' : 'Create')} Category
          </Button>
        </DialogActions>
      </Dialog>

      {/* UoM Dialog */}
      <Dialog open={openUOMDialog} onClose={() => handleCloseDialog('uom')} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedItem ? 'Edit Unit of Measure' : 'Add New Unit of Measure'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Code"
            value={uomForm.code}
            onChange={(e) => setUomForm({...uomForm, code: e.target.value})}
            sx={{ mt: 1, mb: 2 }}
            helperText="Short code (e.g., PCS, KG, L)"
          />
          <TextField
            fullWidth
            label="Name"
            value={uomForm.name}
            onChange={(e) => setUomForm({...uomForm, name: e.target.value})}
            sx={{ mb: 2 }}
            helperText="Full name (e.g., Pieces, Kilograms, Liters)"
          />
          <TextField
            fullWidth
            label="Description"
            multiline
            rows={2}
            value={uomForm.description}
            onChange={(e) => setUomForm({...uomForm, description: e.target.value})}
            sx={{ mb: 2 }}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={uomForm.is_base_unit}
                onChange={(e) => setUomForm({...uomForm, is_base_unit: e.target.checked})}
              />
            }
            label="Is Base Unit"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => handleCloseDialog('uom')} disabled={loading}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleUOMSubmit}
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : (selectedItem ? 'Update' : 'Create')} UoM
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
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

export default SmartInventorySettings;
