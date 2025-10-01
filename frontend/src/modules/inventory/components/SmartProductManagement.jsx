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
  ExpandMore, TrendingUp, TrendingDown,
  LocalOffer, Settings, Refresh, FilterList, Search, Sort,
  Straighten, Memory, Storage, Speed, Security
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { useCurrency } from '../../../components/GlobalCurrencySettings';
import apiClient from '../../../services/apiClient';

const SmartProductManagement = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { formatCurrency } = useCurrency();
  const [activeTab, setActiveTab] = useState(0);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [addStockDialogOpen, setAddStockDialogOpen] = useState(false);
  const [advancedFiltersOpen, setAdvancedFiltersOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [productToDelete, setProductToDelete] = useState(null);
  const [stockData, setStockData] = useState({
    quantity: 0,
    cost: 0,
    notes: ''
  });

  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [advancedFilters, setAdvancedFilters] = useState({
    minPrice: '',
    maxPrice: '',
    minStock: '',
    maxStock: '',
    status: 'all',
    trackingType: 'all'
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [editFormData, setEditFormData] = useState({
    name: '',
    sku: '',
    product_id: '',
    description: '',
    category_id: '',
    status: 'active',
    min_stock_level: 0,
    max_stock_level: 0,
    reorder_point: 0,
    current_cost: 0
  });
  const [useProductId, setUseProductId] = useState(false);

  // Real-time data hooks
  const { data: products, loading: productsLoading, error: productsError, refresh: refreshProducts } = useRealTimeData('/api/inventory/core/products');
  const { data: categories, loading: categoriesLoading } = useRealTimeData('/api/inventory/core/categories');
  const { data: uoms, loading: uomsLoading } = useRealTimeData('/api/inventory/core/uom');

  // Real-time data from API
  const productData = products || [];
  const categoryData = categories || [];
  // const uomData = uoms || []; // Removed unused variable

  const handleAddProduct = () => {
    setAddDialogOpen(true);
  };

  const createNewProduct = async () => {
    try {
      // Get form data from the add dialog
      const formData = {
        name: document.querySelector('input[placeholder="Enter product name"]')?.value || '',
        sku: useProductId ? '' : document.querySelector('input[placeholder="Enter SKU"]')?.value || '',
        product_id: useProductId ? document.querySelector('input[placeholder="Enter Product ID"]')?.value || '' : '',
        description: document.querySelector('textarea[placeholder="Enter product description"]')?.value || '',
        category_id: document.querySelector('select[aria-label="Category"]')?.value || '',
        base_uom_id: document.querySelector('select[aria-label="Base UoM"]')?.value || '',
        status: 'active',
        track_serial_numbers: document.querySelector('input[type="checkbox"][aria-label="Track Serial Numbers"]')?.checked || false,
        track_lots: document.querySelector('input[type="checkbox"][aria-label="Track Lots/Batches"]')?.checked || false,
        track_expiry: document.querySelector('input[type="checkbox"][aria-label="Track Expiry Dates"]')?.checked || false
      };
      
      if (!formData.name || (!formData.sku && !formData.product_id)) {
        setSnackbar({
          open: true,
          message: 'Product name and either SKU or Product ID are required!',
          severity: 'error'
        });
        return;
      }
      
      const response = await apiClient.post('/api/inventory/core/products', formData);
      
      // apiClient returns parsed JSON directly, not a Response object
      if (response && response.message) {
        setSnackbar({
          open: true,
          message: 'Product created successfully!',
          severity: 'success'
        });
        setAddDialogOpen(false);
        // Refresh the products data
        refreshProducts();
      } else {
        setSnackbar({
          open: true,
          message: `Failed to create product: ${response?.error || 'Unknown error'}`,
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error creating product:', error);
      setSnackbar({
        open: true,
        message: 'Failed to create product. Please try again.',
        severity: 'error'
      });
    }
  };

  const handleEditProduct = (product) => {
    setSelectedProduct(product);
    setEditFormData({
      name: product.name || '',
      sku: product.sku || '',
      description: product.description || '',
      category_id: product.category_id || '',
      status: product.status || 'active',
      min_stock_level: product.min_stock_level || 0,
      max_stock_level: product.max_stock_level || 0,
      reorder_point: product.reorder_point || 0,
      current_cost: product.current_cost || 0
    });
    setEditDialogOpen(true);
  };

  const handleViewProduct = (product) => {
    setSelectedProduct(product);
    setViewDialogOpen(true);
  };

  const handleDeleteProduct = (product) => {
    setProductToDelete(product);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteProduct = async () => {
    if (!productToDelete) {
      console.error('No product to delete');
      return;
    }
    
    console.log('Deleting product:', productToDelete);
    
    try {
      const response = await apiClient.delete(`/api/inventory/core/products/${productToDelete.id}`);
      
      if (response && response.message) {
        setSnackbar({
          open: true,
          message: 'Product deleted successfully!',
          severity: 'success'
        });
        setDeleteDialogOpen(false);
        setProductToDelete(null);
        // Refresh the products data
        refreshProducts();
      } else {
        setSnackbar({
          open: true,
          message: `Failed to delete product: ${response?.error || 'Unknown error'}`,
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error deleting product:', error);
      setSnackbar({
        open: true,
        message: 'Failed to delete product. Please try again.',
        severity: 'error'
      });
    }
  };

  const saveProductChanges = async () => {
    if (!selectedProduct) return;
    
    try {
      // Use the state data instead of querying DOM
      const formData = {
        name: editFormData.name,
        sku: editFormData.sku,
        description: editFormData.description,
        category_id: editFormData.category_id,
        status: editFormData.status,
        min_stock_level: parseFloat(editFormData.min_stock_level) || 0,
        max_stock_level: parseFloat(editFormData.max_stock_level) || 0,
        reorder_point: parseFloat(editFormData.reorder_point) || 0,
        current_cost: parseFloat(editFormData.current_cost) || 0
      };
      
      const response = await apiClient.put(`/api/inventory/core/products/${selectedProduct.id}`, formData);
      
      if (response && response.message) {
        setSnackbar({
          open: true,
          message: 'Product updated successfully!',
          severity: 'success'
        });
        setEditDialogOpen(false);
        setSelectedProduct(null);
        // Reset form data
        setEditFormData({
          name: '',
          sku: '',
          description: '',
          category_id: '',
          status: 'active',
          min_stock_level: 0,
          max_stock_level: 0,
          reorder_point: 0,
          current_cost: 0
        });
        // Refresh the products data
        refreshProducts();
      } else {
        setSnackbar({
          open: true,
          message: `Failed to update product: ${response?.error || 'Unknown error'}`,
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error updating product:', error);
      setSnackbar({
        open: true,
        message: 'Failed to update product. Please try again.',
        severity: 'error'
      });
    }
  };

  const addStockToProduct = async () => {
    if (!selectedProduct) {
      setSnackbar({
        open: true,
        message: 'No product selected for adding stock',
        severity: 'error'
      });
      return;
    }

    try {
      const response = await apiClient.post('/api/inventory/core/stock-levels', {
        product_id: selectedProduct.id,
        quantity: stockData.quantity,
        cost: stockData.cost,
        notes: stockData.notes
      });

      if (response && response.message) {
        setSnackbar({
          open: true,
          message: `Stock added successfully for ${selectedProduct.name}`,
          severity: 'success'
        });
        setAddStockDialogOpen(false);
        setSelectedProduct(null);
        setStockData({
          quantity: 0,
          cost: 0,
          notes: ''
        });
        refreshProducts();
      } else {
        throw new Error(response?.error || 'Failed to add stock');
      }
    } catch (error) {
      console.error('Add stock error:', error);
      setSnackbar({
        open: true,
        message: error.message || 'Failed to add stock',
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

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'error';
      case 'discontinued': return 'warning';
      default: return 'default';
    }
  };

  const getCategoryName = (categoryId) => {
    if (!categoryId) return 'Uncategorized';
    const category = categoryData.find(cat => cat.id === categoryId);
    return category ? category.name : 'Uncategorized';
  };

  const getTrackingChips = (product) => {
    const chips = [];
    if (product.track_serial_numbers) chips.push({ label: 'Serial', color: 'primary' });
    if (product.track_lots) chips.push({ label: 'Lot', color: 'secondary' });
    if (product.track_expiry) chips.push({ label: 'Expiry', color: 'warning' });
    return chips;
  };

  const hasActiveAdvancedFilters = () => {
    return advancedFilters.minPrice || 
           advancedFilters.maxPrice || 
           advancedFilters.minStock || 
           advancedFilters.maxStock || 
           advancedFilters.status !== 'all' || 
           advancedFilters.trackingType !== 'all';
  };

  const getFilteredProducts = () => {
    let filtered = productData.filter(product => {
      const matchesSearch = (product.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (product.sku || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (product.product_id || '').toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = filterCategory === 'all' || product.category_id === parseInt(filterCategory);
      
      // Apply advanced filters
      const matchesPrice = (!advancedFilters.minPrice || (product.unit_cost || 0) >= parseFloat(advancedFilters.minPrice)) &&
                          (!advancedFilters.maxPrice || (product.unit_cost || 0) <= parseFloat(advancedFilters.maxPrice));
      
      const matchesStock = (!advancedFilters.minStock || (product.current_stock || 0) >= parseFloat(advancedFilters.minStock)) &&
                          (!advancedFilters.maxStock || (product.current_stock || 0) <= parseFloat(advancedFilters.maxStock));
      
      const matchesStatus = advancedFilters.status === 'all' || product.status === advancedFilters.status;
      
      let matchesTracking = true;
      if (advancedFilters.trackingType !== 'all') {
        switch (advancedFilters.trackingType) {
          case 'serial':
            matchesTracking = product.track_serial_numbers === true;
            break;
          case 'lot':
            matchesTracking = product.track_lots === true;
            break;
          case 'expiry':
            matchesTracking = product.track_expiry === true;
            break;
        }
      }
      
      // Apply tab filters
      let matchesTab = true;
      switch (activeTab) {
        case 1: // Serialized
          matchesTab = product.track_serial_numbers === true;
          break;
        case 2: // Lot Tracked
          matchesTab = product.track_lots === true;
          break;
        case 3: // Low Stock
          matchesTab = (product.current_stock || 0) <= (product.min_stock_level || 0);
          break;
        case 4: // Expiring Soon
          // For now, we'll show products with expiry tracking enabled
          matchesTab = product.track_expiry === true;
          break;
        default: // All Products
          matchesTab = true;
      }
      
      return matchesSearch && matchesCategory && matchesPrice && matchesStock && matchesStatus && matchesTracking && matchesTab;
    });
    
    return filtered;
  };

  const filteredProducts = getFilteredProducts();

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>Product Management</Typography>
        {/* actions */}
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
                variant={hasActiveAdvancedFilters() ? "contained" : "outlined"}
                startIcon={<FilterList />}
                fullWidth
                onClick={() => setAdvancedFiltersOpen(true)}
                color={hasActiveAdvancedFilters() ? "primary" : "inherit"}
                sx={{
                  fontWeight: hasActiveAdvancedFilters() ? 'bold' : 'normal',
                  ...(hasActiveAdvancedFilters() && {
                    backgroundColor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'primary.dark'
                    }
                  })
                }}
              >
                Advanced Filters
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

      {/* Product Tabs */}
      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant={isMobile ? "scrollable" : "fullWidth"}
          scrollButtons={isMobile ? "auto" : false}
        >
          <Tab label="All Products" />
          <Tab label="Serialized" />
          <Tab label="Lot Tracked" />
          <Tab label="Low Stock" />
          <Tab label="Expiring Soon" />
        </Tabs>
      </Paper>

      {/* Products Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper} sx={{ width: '100%', overflowX: 'auto' }}>
            <Table sx={{ minWidth: 900 }}>
              <TableHead>
                <TableRow>
                  <TableCell>Product</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Tracking</TableCell>
                  <TableCell>Stock Levels</TableCell>
                  <TableCell>Cost</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredProducts.map((product) => (
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
                            SKU: {product.sku || 'No SKU'}
                          </Typography>
                          {product.variants.length > 0 && (
                            <Chip 
                              label={`${product.variants.length} variants`} 
                              size="small" 
                              color="info" 
                              sx={{ mt: 0.5 }}
                            />
                          )}
                        </Box>
                      </Box>
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
                        {getTrackingChips(product).map((chip, index) => (
                          <Chip 
                            key={index}
                            label={chip.label} 
                            size="small" 
                            color={chip.color}
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">
                          Min: {product.min_stock_level || 0} | Max: {product.max_stock_level || 0}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Reorder: {product.reorder_point || 0}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {formatCurrency(product.current_cost || 0)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {product.cost_method || 'Standard'}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={product.status || 'Unknown'} 
                        size="small" 
                        color={getStatusColor(product.status || 'Unknown')}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5 }}>
                        <Tooltip title="Add Stock">
                          <IconButton 
                            size="small" 
                            color="success"
                            onClick={() => {
                              setSelectedProduct(product);
                              setStockData({
                                quantity: 0,
                                cost: product.current_cost || 0,
                                notes: ''
                              });
                              setAddStockDialogOpen(true);
                            }}
                          >
                            <Add />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="View Details">
                          <IconButton 
                            size="small" 
                            color="primary"
                            onClick={() => handleViewProduct(product)}
                          >
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit Product">
                          <IconButton 
                            size="small" 
                            color="primary"
                            onClick={() => handleEditProduct(product)}
                          >
                            <Edit />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Product">
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => handleDeleteProduct(product)}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Product Variants Section */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" fontWeight="bold" gutterBottom>
            🎨 Product Variants Matrix
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Advanced variant management with flexible attributes
          </Typography>
          
          {filteredProducts.map((product) => (
            <Accordion key={product.id} sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Typography variant="body1" fontWeight="bold">
                    {product.name || 'Unnamed Product'}
                  </Typography>
                  <Chip label={`${product.variants.length} variants`} size="small" color="info" />
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Variant SKU</TableCell>
                        <TableCell>Name</TableCell>
                        <TableCell>Attributes</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {product.variants.map((variant) => (
                        <TableRow key={variant.id}>
                          <TableCell>
                            <Typography variant="body2" fontWeight="bold">
                              {variant.variant_sku || 'No SKU'}
                            </Typography>
                          </TableCell>
                          <TableCell>{variant.variant_name || 'Unnamed Variant'}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                              {Object.entries(variant.attributes).map(([key, value]) => (
                                <Chip 
                                  key={key}
                                  label={`${key}: ${value}`} 
                                  size="small" 
                                  variant="outlined"
                                />
                              ))}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <IconButton size="small" color="primary">
                              <Edit />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>

      {/* Loading States */}
      {(productsLoading || categoriesLoading || uomsLoading) && (
        <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }}>
          <LinearProgress />
        </Box>
      )}

      {/* Error Handling */}
      {productsError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Error loading products. Please refresh the page.
        </Alert>
      )}

      {/* Add Product Dialog */}
      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Add color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Add New Product
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Create a new product with advanced tracking and variant capabilities
          </Typography>
          
          <Box sx={{ mb: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={useProductId}
                  onChange={(e) => setUseProductId(e.target.checked)}
                />
              }
              label="Use Product ID instead of SKU"
            />
          </Box>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Product Name"
                placeholder="Enter product name"
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={useProductId ? "Product ID" : "SKU"}
                placeholder={useProductId ? "Enter Product ID" : "Enter SKU"}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                placeholder="Enter product description"
                multiline
                rows={3}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Category</InputLabel>
                <Select label="Category">
                  {categoryData.map(category => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Base UoM</InputLabel>
                <Select label="Base UoM">
                  {(uoms || []).map(uom => (
                    <MenuItem key={uom.id} value={uom.id}>
                      {uom.code} - {uom.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            {/* Tracking Options */}
            <Grid item xs={12}>
              <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
                Tracking Options
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <FormControlLabel
                  control={<Switch />}
                  label="Track Serial Numbers"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Track Lots/Batches"
                />
                <FormControlLabel
                  control={<Switch />}
                  label="Track Expiry Dates"
                />
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={createNewProduct}>
            Create Product
          </Button>
        </DialogActions>
      </Dialog>

      {/* View Product Details Dialog */}
      <Dialog open={viewDialogOpen} onClose={() => setViewDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Visibility color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Product Details
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedProduct && (
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Avatar sx={{ width: 60, height: 60, bgcolor: 'primary.main' }}>
                    {getProductTypeIcon(selectedProduct.type)}
                  </Avatar>
                  <Box>
                    <Typography variant="h5" fontWeight="bold">
                      {selectedProduct.name || 'Unnamed Product'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      SKU: {selectedProduct.sku || 'No SKU'}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>Basic Information</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Typography><strong>Category:</strong> {getCategoryName(selectedProduct.category_id)}</Typography>
                  <Typography><strong>Status:</strong> 
                    <Chip 
                      label={selectedProduct.status || 'Unknown'} 
                      size="small" 
                      color={getStatusColor(selectedProduct.status || 'Unknown')}
                      sx={{ ml: 1 }}
                    />
                  </Typography>
                  <Typography><strong>Base UoM:</strong> {selectedProduct.base_uom || 'Not specified'}</Typography>
                  <Typography><strong>Description:</strong> {selectedProduct.description || 'No description'}</Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>Stock Levels</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Typography><strong>Current Stock:</strong> {selectedProduct.current_stock || 0}</Typography>
                  <Typography><strong>Min Stock:</strong> {selectedProduct.min_stock_level || 0}</Typography>
                  <Typography><strong>Max Stock:</strong> {selectedProduct.max_stock_level || 0}</Typography>
                  <Typography><strong>Reorder Point:</strong> {selectedProduct.reorder_point || 0}</Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>Cost Information</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Typography><strong>Current Cost:</strong> {formatCurrency(selectedProduct.current_cost || 0)}</Typography>
                  <Typography><strong>Cost Method:</strong> {selectedProduct.cost_method || 'Standard'}</Typography>
                  <Typography><strong>Standard Cost:</strong> {formatCurrency(selectedProduct.standard_cost || 0)}</Typography>
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1" fontWeight="bold" gutterBottom>Tracking Options</Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {getTrackingChips(selectedProduct).map((chip, index) => (
                    <Chip 
                      key={index}
                      label={chip.label} 
                      size="small" 
                      color={chip.color}
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Grid>
              
              {(selectedProduct.variants || []).length > 0 && (
                <Grid item xs={12}>
                  <Typography variant="subtitle1" fontWeight="bold" gutterBottom>Product Variants</Typography>
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Variant SKU</TableCell>
                          <TableCell>Variant Name</TableCell>
                          <TableCell>Stock</TableCell>
                          <TableCell>Cost</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {selectedProduct.variants.map((variant, index) => (
                          <TableRow key={index}>
                            <TableCell>{variant.variant_sku || 'No SKU'}</TableCell>
                            <TableCell>{variant.variant_name || 'Unnamed Variant'}</TableCell>
                            <TableCell>{variant.stock || 0}</TableCell>
                            <TableCell>{formatCurrency(variant.cost || 0)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setViewDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            startIcon={<Edit />}
            onClick={() => {
              setViewDialogOpen(false);
              setEditDialogOpen(true);
            }}
          >
            Edit Product
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Product Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Edit color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Edit Product
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedProduct && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Edit product: {selectedProduct.name || 'Unnamed Product'}
            </Typography>
          )}
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Product Name"
                placeholder="Enter product name"
                value={editFormData.name}
                onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="SKU"
                placeholder="Enter SKU"
                value={editFormData.sku}
                onChange={(e) => setEditFormData({ ...editFormData, sku: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                placeholder="Enter product description"
                multiline
                rows={3}
                value={editFormData.description}
                onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Category</InputLabel>
                <Select 
                  label="Category" 
                  value={editFormData.category_id}
                  onChange={(e) => setEditFormData({ ...editFormData, category_id: e.target.value })}
                >
                  {categoryData.map(category => (
                    <MenuItem key={category.id} value={category.id}>
                      {category.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Status</InputLabel>
                <Select 
                  label="Status" 
                  value={editFormData.status}
                  onChange={(e) => setEditFormData({ ...editFormData, status: e.target.value })}
                >
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                  <MenuItem value="discontinued">Discontinued</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Min Stock"
                type="number"
                value={editFormData.min_stock_level}
                onChange={(e) => setEditFormData({ ...editFormData, min_stock_level: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Max Stock"
                type="number"
                value={editFormData.max_stock_level}
                onChange={(e) => setEditFormData({ ...editFormData, max_stock_level: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Reorder Point"
                type="number"
                value={editFormData.reorder_point}
                onChange={(e) => setEditFormData({ ...editFormData, reorder_point: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Current Cost"
                type="number"
                value={editFormData.current_cost}
                onChange={(e) => setEditFormData({ ...editFormData, current_cost: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setEditDialogOpen(false);
            setEditFormData({
              name: '',
              sku: '',
              description: '',
              category_id: '',
              status: 'active',
              min_stock_level: 0,
              max_stock_level: 0,
              reorder_point: 0,
              current_cost: 0
            });
          }}>Cancel</Button>
          <Button variant="contained" onClick={saveProductChanges}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Delete color="error" />
            <Typography variant="h6" fontWeight="bold">
              Delete Product
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Are you sure you want to delete the product "{productToDelete?.name || 'Unknown Product'}"?
          </Typography>
          <Alert severity="warning">
            This action cannot be undone. All product data, variants, and stock information will be permanently deleted.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            color="error" 
            onClick={confirmDeleteProduct}
          >
            Delete Product
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Stock Dialog */}
      <Dialog open={addStockDialogOpen} onClose={() => setAddStockDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Add color="success" />
            <Typography variant="h6" fontWeight="bold">
              Add Stock
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedProduct && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Adding stock for: {selectedProduct.name}
            </Typography>
          )}
          
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Quantity to Add"
                type="number"
                value={stockData.quantity}
                onChange={(e) => setStockData({ ...stockData, quantity: parseFloat(e.target.value) || 0 })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Unit Cost"
                type="number"
                value={stockData.cost}
                onChange={(e) => setStockData({ ...stockData, cost: parseFloat(e.target.value) || 0 })}
                sx={{ mb: 2 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Notes"
                multiline
                rows={3}
                value={stockData.notes}
                onChange={(e) => setStockData({ ...stockData, notes: e.target.value })}
                sx={{ mb: 2 }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddStockDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" color="success" onClick={addStockToProduct}>
            Add Stock
          </Button>
        </DialogActions>
      </Dialog>

      {/* Advanced Filters Dialog */}
      <Dialog open={advancedFiltersOpen} onClose={() => setAdvancedFiltersOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FilterList color="primary" />
            <Typography variant="h6" fontWeight="bold">
              Advanced Filters
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Min Price"
                type="number"
                value={advancedFilters.minPrice}
                onChange={(e) => setAdvancedFilters({ ...advancedFilters, minPrice: e.target.value })}
                placeholder="0.00"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Max Price"
                type="number"
                value={advancedFilters.maxPrice}
                onChange={(e) => setAdvancedFilters({ ...advancedFilters, maxPrice: e.target.value })}
                placeholder="9999.99"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Min Stock"
                type="number"
                value={advancedFilters.minStock}
                onChange={(e) => setAdvancedFilters({ ...advancedFilters, minStock: e.target.value })}
                placeholder="0"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Max Stock"
                type="number"
                value={advancedFilters.maxStock}
                onChange={(e) => setAdvancedFilters({ ...advancedFilters, maxStock: e.target.value })}
                placeholder="1000"
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={advancedFilters.status}
                  onChange={(e) => setAdvancedFilters({ ...advancedFilters, status: e.target.value })}
                  label="Status"
                >
                  <MenuItem value="all">All Statuses</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="inactive">Inactive</MenuItem>
                  <MenuItem value="discontinued">Discontinued</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Tracking Type</InputLabel>
                <Select
                  value={advancedFilters.trackingType}
                  onChange={(e) => setAdvancedFilters({ ...advancedFilters, trackingType: e.target.value })}
                  label="Tracking Type"
                >
                  <MenuItem value="all">All Types</MenuItem>
                  <MenuItem value="serial">Serial Numbers</MenuItem>
                  <MenuItem value="lot">Lot/Batch</MenuItem>
                  <MenuItem value="expiry">Expiry Dates</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setAdvancedFilters({
              minPrice: '',
              maxPrice: '',
              minStock: '',
              maxStock: '',
              status: 'all',
              trackingType: 'all'
            });
            setAdvancedFiltersOpen(false);
          }}>
            Clear All
          </Button>
          <Button variant="contained" onClick={() => setAdvancedFiltersOpen(false)}>
            Apply Filters
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

export default SmartProductManagement;
