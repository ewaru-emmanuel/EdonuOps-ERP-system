import React, { useState } from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, Chip, IconButton, TextField, InputAdornment, Card, CardContent, Grid,
  Alert, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions,
  FormControl, InputLabel, Select, MenuItem, Snackbar
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { useCurrency } from '../../../components/GlobalCurrencySettings';

const SmartStockLevels = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newStockLevel, setNewStockLevel] = useState({
    product_id: '',
    quantity_on_hand: 0,
    unit_cost: 0,
    warehouse: 'Main Warehouse'
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Mock data to prevent API calls
  const stockLevels = [];
  const loading = false;
  const error = null;
  const refresh = () => { console.log('Mock refresh stock levels'); };
  
  const products = [];
  const { formatCurrency } = useCurrency();

  // Create a map of products for easy lookup
  const productsMap = products?.reduce((acc, product) => {
    acc[product.id] = product;
    return acc;
  }, {}) || {};

  // Filter stock levels based on search
  const filteredStockLevels = stockLevels?.filter(level => {
    const product = productsMap[level.product_id];
    if (!product) return false;
    
    return product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
           product.sku?.toLowerCase().includes(searchTerm.toLowerCase()) ||
           product.product_id?.toLowerCase().includes(searchTerm.toLowerCase());
  }) || [];

  // Calculate summary statistics
  const totalItems = filteredStockLevels.length;
  const lowStockItems = filteredStockLevels.filter(level => {
    const product = productsMap[level.product_id];
    return product && level.quantity_on_hand <= (product.reorder_point || 0);
  }).length;
  const outOfStockItems = filteredStockLevels.filter(level => level.quantity_on_hand <= 0).length;

  const getStockStatus = (level) => {
    const product = productsMap[level.product_id];
    if (!product) return 'unknown';
    
    if (level.quantity_on_hand <= 0) return 'out_of_stock';
    if (level.quantity_on_hand <= (product.reorder_point || 0)) return 'low_stock';
    return 'normal';
  };

  const getStatusChip = (status) => {
    switch (status) {
      case 'out_of_stock':
        return <Chip label="Out of Stock" color="error" size="small" />;
      case 'low_stock':
        return <Chip label="Low Stock" color="warning" size="small" />;
      case 'normal':
        return <Chip label="Normal" color="success" size="small" />;
      default:
        return <Chip label="Unknown" color="default" size="small" />;
    }
  };

  const handleAddStock = () => {
    setAddDialogOpen(true);
  };

  const handleSaveStock = () => {
    // Mock save stock level
    console.log('Mock save stock level:', newStockLevel);
    setSnackbar({
      open: true,
      message: 'Stock level added successfully!',
      severity: 'success'
    });
    setAddDialogOpen(false);
    setNewStockLevel({
      product_id: '',
      quantity_on_hand: 0,
      unit_cost: 0,
      warehouse: 'Main Warehouse'
    });
  };

  const handleCancelAdd = () => {
    setAddDialogOpen(false);
    setNewStockLevel({
      product_id: '',
      quantity_on_hand: 0,
      unit_cost: 0,
      warehouse: 'Main Warehouse'
    });
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
        Error loading stock levels: {error.message}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Stock Levels
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor your current inventory levels and reorder points
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Items
              </Typography>
              <Typography variant="h4">
                {totalItems}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'success.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckCircleIcon sx={{ color: 'success.main', mr: 1 }} />
                <Typography color="success.main" gutterBottom>
                  Normal Stock
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                {totalItems - lowStockItems - outOfStockItems}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'warning.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <WarningIcon sx={{ color: 'warning.main', mr: 1 }} />
                <Typography color="warning.main" gutterBottom>
                  Low Stock
                </Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                {lowStockItems}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'error.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <WarningIcon sx={{ color: 'error.main', mr: 1 }} />
                <Typography color="error.main" gutterBottom>
                  Out of Stock
                </Typography>
              </Box>
              <Typography variant="h4" color="error.main">
                {outOfStockItems}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Search and Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <TextField
          placeholder="Search products..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ width: 300 }}
        />
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddStock}
        >
          Add Stock Level
        </Button>
      </Box>

      {/* Stock Levels Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product</TableCell>
              <TableCell>SKU</TableCell>
              <TableCell align="right">Current Stock</TableCell>
              <TableCell align="right">Reorder Point</TableCell>
              <TableCell align="right">Unit Cost</TableCell>
              <TableCell align="right">Total Value</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredStockLevels.map((level) => {
              const product = productsMap[level.product_id];
              const status = getStockStatus(level);
              
              if (!product) return null;

              return (
                <TableRow key={level.id} hover>
                  <TableCell>
                    <Typography variant="subtitle2">
                      {product.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {product.description}
                    </Typography>
                  </TableCell>
                  <TableCell>{product.sku || product.product_id}</TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      {level.quantity_on_hand}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    {product.reorder_point || 0}
                  </TableCell>
                  <TableCell align="right">
                    {formatCurrency(level.unit_cost || 0)}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      {formatCurrency((level.quantity_on_hand || 0) * (level.unit_cost || 0))}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {getStatusChip(status)}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton size="small" onClick={() => {/* TODO: View details */}}>
                      <ViewIcon />
                    </IconButton>
                    <IconButton size="small" onClick={() => {/* TODO: Edit stock level */}}>
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredStockLevels.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No stock levels found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {searchTerm ? 'Try adjusting your search terms' : 'Add your first stock level to get started'}
          </Typography>
        </Box>
      )}

      {/* Add Stock Dialog */}
      <Dialog open={addDialogOpen} onClose={handleCancelAdd} maxWidth="sm" fullWidth>
        <DialogTitle>Add Stock Level</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Product ID"
                value={newStockLevel.product_id}
                onChange={(e) => setNewStockLevel({...newStockLevel, product_id: e.target.value})}
                placeholder="Enter product ID or SKU"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Quantity"
                type="number"
                value={newStockLevel.quantity_on_hand}
                onChange={(e) => setNewStockLevel({...newStockLevel, quantity_on_hand: parseFloat(e.target.value) || 0})}
                inputProps={{ min: 0 }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Unit Cost"
                type="number"
                value={newStockLevel.unit_cost}
                onChange={(e) => setNewStockLevel({...newStockLevel, unit_cost: parseFloat(e.target.value) || 0})}
                inputProps={{ min: 0, step: 0.01 }}
                InputProps={{
                  startAdornment: <InputAdornment position="start">{formatCurrency(0).replace(/[\d,.-]/g, '')}</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Warehouse</InputLabel>
                <Select
                  value={newStockLevel.warehouse}
                  onChange={(e) => setNewStockLevel({...newStockLevel, warehouse: e.target.value})}
                >
                  <MenuItem value="Main Warehouse">Main Warehouse</MenuItem>
                  <MenuItem value="Secondary Warehouse">Secondary Warehouse</MenuItem>
                  <MenuItem value="Storage Facility">Storage Facility</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelAdd}>Cancel</Button>
          <Button onClick={handleSaveStock} variant="contained">
            Add Stock Level
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({...snackbar, open: false})}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setSnackbar({...snackbar, open: false})}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SmartStockLevels;
