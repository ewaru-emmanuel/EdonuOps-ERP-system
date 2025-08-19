import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Avatar,
  Tooltip,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Category,
  Inventory,
  AttachMoney,
  Warning
} from '@mui/icons-material';

const ProductManagement = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    sku: '',
    name: '',
    description: '',
    category_id: '',
    unit: 'pcs',
    cost_method: 'FIFO',
    standard_cost: '',
    min_stock: '',
    max_stock: '',
    is_active: true
  });

  const products = [
    {
      id: 1,
      sku: 'LAP-001',
      name: 'Laptop Dell XPS 13',
      description: '13-inch laptop with Intel i7 processor',
      category: 'Electronics',
      unit: 'pcs',
      current_stock: 25,
      min_stock: 5,
      max_stock: 50,
      standard_cost: 1200,
      current_cost: 1200,
      is_active: true
    },
    {
      id: 2,
      sku: 'CHAIR-001',
      name: 'Office Chair',
      description: 'Ergonomic office chair with adjustable height',
      category: 'Furniture',
      unit: 'pcs',
      current_stock: 15,
      min_stock: 3,
      max_stock: 30,
      standard_cost: 350,
      current_cost: 350,
      is_active: true
    },
    {
      id: 3,
      sku: 'MOUSE-001',
      name: 'Wireless Mouse',
      description: 'Bluetooth wireless mouse',
      category: 'Electronics',
      unit: 'pcs',
      current_stock: 100,
      min_stock: 20,
      max_stock: 200,
      standard_cost: 25,
      current_cost: 25,
      is_active: true
    },
    {
      id: 4,
      sku: 'MON-001',
      name: 'Monitor 24"',
      description: '24-inch LED monitor',
      category: 'Electronics',
      unit: 'pcs',
      current_stock: 8,
      min_stock: 5,
      max_stock: 25,
      standard_cost: 180,
      current_cost: 180,
      is_active: false
    }
  ];

  const getStockStatus = (current, min) => {
    if (current <= min) return 'low';
    if (current <= min * 1.5) return 'medium';
    return 'good';
  };

  const getStockColor = (status) => {
    switch (status) {
      case 'low': return 'error';
      case 'medium': return 'warning';
      case 'good': return 'success';
      default: return 'default';
    }
  };

  const handleOpenDialog = (product = null) => {
    if (product) {
      setEditingProduct(product);
      setFormData(product);
    } else {
      setEditingProduct(null);
      setFormData({
        sku: '',
        name: '',
        description: '',
        category_id: '',
        unit: 'pcs',
        cost_method: 'FIFO',
        standard_cost: '',
        min_stock: '',
        max_stock: '',
        is_active: true
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingProduct(null);
  };

  const handleSubmit = () => {
    // TODO: Implement API call to save product
    console.log('Saving product:', formData);
    handleCloseDialog();
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>
          Product Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ textTransform: 'none' }}
        >
          Add New Product
        </Button>
      </Box>

      {/* Product Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {products.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Products
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1, color: 'success.main' }}>
                {products.filter(p => p.is_active).length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active Products
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {products.reduce((sum, p) => sum + p.current_stock, 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Stock
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1, color: 'warning.main' }}>
                {products.filter(p => getStockStatus(p.current_stock, p.min_stock) === 'low').length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Low Stock Items
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Products Table */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
            Product List
          </Typography>
          
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>Product</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Category</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Stock</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Cost</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Status</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {products.map((product) => {
                  const stockStatus = getStockStatus(product.current_stock, product.min_stock);
                  return (
                    <TableRow key={product.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar sx={{ bgcolor: 'primary.main' }}>
                            <Category />
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                              {product.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              SKU: {product.sku}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip label={product.category} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {product.current_stock} {product.unit}
                          </Typography>
                          <Chip
                            label={stockStatus}
                            size="small"
                            color={getStockColor(stockStatus)}
                            sx={{ textTransform: 'capitalize', mt: 0.5 }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            ${product.current_cost}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Standard: ${product.standard_cost}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={product.is_active ? 'Active' : 'Inactive'}
                          color={product.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton size="small" color="primary">
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Product">
                            <IconButton size="small" color="primary" onClick={() => handleOpenDialog(product)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Product">
                            <IconButton size="small" color="error">
                              <DeleteIcon />
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

      {/* Add/Edit Product Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingProduct ? 'Edit Product' : 'Add New Product'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="SKU"
                value={formData.sku}
                onChange={(e) => handleInputChange('sku', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Product Name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={formData.category_id}
                  label="Category"
                  onChange={(e) => handleInputChange('category_id', e.target.value)}
                >
                  <MenuItem value="electronics">Electronics</MenuItem>
                  <MenuItem value="furniture">Furniture</MenuItem>
                  <MenuItem value="office-supplies">Office Supplies</MenuItem>
                  <MenuItem value="accessories">Accessories</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Unit"
                value={formData.unit}
                onChange={(e) => handleInputChange('unit', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Cost Method</InputLabel>
                <Select
                  value={formData.cost_method}
                  label="Cost Method"
                  onChange={(e) => handleInputChange('cost_method', e.target.value)}
                >
                  <MenuItem value="FIFO">FIFO</MenuItem>
                  <MenuItem value="LIFO">LIFO</MenuItem>
                  <MenuItem value="Weighted Average">Weighted Average</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Standard Cost"
                type="number"
                value={formData.standard_cost}
                onChange={(e) => handleInputChange('standard_cost', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Minimum Stock"
                type="number"
                value={formData.min_stock}
                onChange={(e) => handleInputChange('min_stock', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Maximum Stock"
                type="number"
                value={formData.max_stock}
                onChange={(e) => handleInputChange('max_stock', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.is_active}
                    onChange={(e) => handleInputChange('is_active', e.target.checked)}
                  />
                }
                label="Active Product"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingProduct ? 'Update' : 'Create'} Product
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProductManagement;
