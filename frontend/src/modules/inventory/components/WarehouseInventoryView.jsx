import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Paper, Chip, Avatar,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, IconButton, Tooltip, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, FormControl, InputLabel, Select, MenuItem,
  Switch, FormControlLabel, Alert, LinearProgress, Badge, Tabs, Tab,
  List, ListItem, ListItemText, ListItemAvatar, ListItemIcon,
  Accordion, AccordionSummary, AccordionDetails, Autocomplete,
  useTheme, useMediaQuery, Snackbar
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, QrCode, Inventory, Category,
  ExpandMore, TrendingUp, TrendingDown, Search, Refresh, FilterList,
  LocalOffer, Settings, Sort, Straighten, Memory, Storage, Speed,
  Security, CheckCircle, Warning, Error, Info, Scanner, Assignment
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const WarehouseInventoryView = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activeTab, setActiveTab] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [stockTakeDialogOpen, setStockTakeDialogOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [stockTakeData, setStockTakeData] = useState({
    product_id: '',
    location: '',
    counted_quantity: 0,
    notes: ''
  });

  // Real-time data hooks
  const { data: products, loading: productsLoading, error: productsError, refresh: refreshProducts } = useRealTimeData('/api/inventory/core/products');
  const { data: categories, loading: categoriesLoading } = useRealTimeData('/api/inventory/core/categories');

  // Real-time data from API
  const productData = products || [];
  const categoryData = categories || [];

  const getCategoryName = (categoryId) => {
    if (!categoryId) return 'Uncategorized';
    const category = categoryData.find(cat => cat.id === categoryId);
    return category ? category.name : 'Uncategorized';
  };

  const getStockStatus = (product) => {
    const currentStock = product.current_stock || 0;
    const minStock = product.min_stock || 0;
    const maxStock = product.max_stock || 0;

    if (currentStock <= minStock) return { status: 'low', color: 'error', label: 'Low Stock' };
    if (currentStock >= maxStock * 0.9) return { status: 'high', color: 'warning', label: 'High Stock' };
    return { status: 'normal', color: 'success', label: 'Normal' };
  };

  const getFilteredProducts = () => {
    let filtered = productData.filter(product => {
      const matchesSearch = (product.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (product.sku || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (product.product_id || '').toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = filterCategory === 'all' || product.category_id === parseInt(filterCategory);
      
      // Apply tab filters
      let matchesTab = true;
      switch (activeTab) {
        case 1: // Low Stock
          matchesTab = (product.current_stock || 0) <= (product.min_stock || 0);
          break;
        case 2: // Out of Stock
          matchesTab = (product.current_stock || 0) === 0;
          break;
        case 3: // High Stock
          matchesTab = (product.current_stock || 0) >= ((product.max_stock || 0) * 0.9);
          break;
        case 4: // Serialized
          matchesTab = product.track_serial_numbers === true;
          break;
        case 5: // Lot Tracked
          matchesTab = product.track_lots === true;
          break;
        default: // All Products
          matchesTab = true;
      }
      
      return matchesSearch && matchesCategory && matchesTab;
    });
    
    return filtered;
  };

  const filteredProducts = getFilteredProducts();

  const openStockTakeDialog = (product) => {
    setSelectedProduct(product);
    setStockTakeData({
      product_id: product.id,
      location: product.location || '',
      counted_quantity: product.current_stock || 0,
      notes: ''
    });
    setStockTakeDialogOpen(true);
  };

  const handleStockTake = async () => {
    if (!selectedProduct) {
      setSnackbar({
        open: true,
        message: 'No product selected for stock take',
        severity: 'error'
      });
      return;
    }

    try {
      const result = await apiClient.post('/api/inventory/core/stock-take', {
        product_id: selectedProduct.id,
        counted_quantity: stockTakeData.counted_quantity,
        location: stockTakeData.location,
        notes: stockTakeData.notes
      });

      setSnackbar({
        open: true,
        message: `Stock take recorded successfully for ${selectedProduct.name}`,
        severity: 'success'
      });
      setStockTakeDialogOpen(false);
      setSelectedProduct(null);
      setStockTakeData({
        location: '',
        counted_quantity: 0,
        notes: ''
      });
      refreshProducts();
    } catch (error) {
      console.error('Stock take error:', error);
      setSnackbar({
        open: true,
        message: error.message || 'Failed to record stock take',
        severity: 'error'
      });
    }
  };

  const getProductTypeIcon = (type) => {
    switch (type) {
      case 'serialized': return <QrCode />;
      case 'lot_tracked': return <Inventory />;
      default: return <LocalOffer />;
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold' }}>
          📦 Warehouse Inventory View
        </Typography>
        <Button
          variant="contained"
          startIcon={<Assignment />}
          onClick={() => {
            setSnackbar({
              open: true,
              message: 'Please select a product first to record stock take',
              severity: 'info'
            });
          }}
          sx={{ fontWeight: 'bold' }}
        >
          Start Stock Take
        </Button>
      </Box>

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search products by name, SKU, or Product ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  label="Category"
                >
                  <MenuItem value="all">All Categories</MenuItem>
                  {categoryData.map(category => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                variant="outlined"
                startIcon={<FilterList />}
                fullWidth
                onClick={() => {
                  setSnackbar({
                    open: true,
                    message: 'Advanced filters coming soon!',
                    severity: 'info'
                  });
                }}
              >
                Filters
              </Button>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                fullWidth
                onClick={() => {
                  refreshProducts();
                  setSnackbar({
                    open: true,
                    message: 'Data refreshed successfully!',
                    severity: 'success'
                  });
                }}
              >
                Refresh
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Inventory Tabs */}
      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant={isMobile ? "scrollable" : "fullWidth"}
          scrollButtons={isMobile ? "auto" : false}
        >
          <Tab label="All Inventory" />
          <Tab label="Low Stock" />
          <Tab label="Out of Stock" />
          <Tab label="High Stock" />
          <Tab label="Serialized" />
          <Tab label="Lot Tracked" />
        </Tabs>
      </Paper>

      {/* Loading State */}
      {productsLoading && (
        <Box sx={{ width: '100%', mb: 2 }}>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Loading inventory data...
          </Typography>
        </Box>
      )}

      {/* Error State */}
      {productsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error loading inventory: {productsError}
        </Alert>
      )}

      {/* Inventory Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Product</TableCell>
                  <TableCell>Location</TableCell>
                  <TableCell>Current Stock</TableCell>
                  <TableCell>Stock Status</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Tracking</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredProducts.map((product) => {
                  const stockStatus = getStockStatus(product);
                  return (
                    <TableRow key={product.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar sx={{ bgcolor: 'primary.light' }}>
                            {getProductTypeIcon(product.product_type)}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {product.name || 'Unnamed Product'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {product.sku || product.product_id || 'No ID'}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {product.location || 'Main Warehouse'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {product.current_stock || 0}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Min: {product.min_stock || 0} | Max: {product.max_stock || 0}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={stockStatus.label}
                          size="small" 
                          color={stockStatus.color}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={getCategoryName(product.category_id)} 
                          size="small" 
                          color="default"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {product.track_serial_numbers && (
                            <Chip label="Serial" size="small" color="primary" variant="outlined" />
                          )}
                          {product.track_lots && (
                            <Chip label="Lot" size="small" color="secondary" variant="outlined" />
                          )}
                          {product.track_expiry && (
                            <Chip label="Expiry" size="small" color="warning" variant="outlined" />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <Tooltip title="Record Stock Take">
                            <IconButton 
                              size="small" 
                              color="primary"
                              onClick={() => openStockTakeDialog(product)}
                            >
                              <Assignment />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="View Details">
                            <IconButton 
                              size="small" 
                              color="info"
                              onClick={() => {
                                setSelectedProduct(product);
                                setSnackbar({
                                  open: true,
                                  message: `Viewing details for ${product.name}`,
                                  severity: 'info'
                                });
                              }}
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Stock Take Dialog */}
      <Dialog open={stockTakeDialogOpen} onClose={() => setStockTakeDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assignment color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Record Stock Take
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedProduct && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Recording stock take for: {selectedProduct.name}
            </Typography>
          )}
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Location"
                value={stockTakeData.location}
                onChange={(e) => setStockTakeData({ ...stockTakeData, location: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Counted Quantity"
                type="number"
                value={stockTakeData.counted_quantity}
                onChange={(e) => setStockTakeData({ ...stockTakeData, counted_quantity: parseFloat(e.target.value) || 0 })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={stockTakeData.notes}
                onChange={(e) => setStockTakeData({ ...stockTakeData, notes: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStockTakeDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleStockTake}>
            Record Stock Take
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

export default WarehouseInventoryView;

