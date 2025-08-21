import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, TextField, FormControl, InputLabel, Select, MenuItem, Tab, Tabs, Alert, Snackbar, LinearProgress, Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Inventory as InventoryIcon,
  Category as CategoryIcon,
  Warehouse as WarehouseIcon,
  Receipt as ReceiptIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';

const InventoryModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Form and dialog states
  const [formOpen, setFormOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteItem, setDeleteItem] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedItemType, setSelectedItemType] = useState('');

  // Real-time data hooks
  const { 
    data: categories, 
    loading: categoriesLoading, 
    error: categoriesError,
    create: createCategory,
    update: updateCategory,
    remove: deleteCategory
  } = useRealTimeData('/api/inventory/categories');
  
  const { 
    data: products, 
    loading: productsLoading, 
    error: productsError,
    create: createProduct,
    update: updateProduct,
    remove: deleteProduct
  } = useRealTimeData('/api/inventory/products');
  
  const { 
    data: warehouses, 
    loading: warehousesLoading, 
    error: warehousesError,
    create: createWarehouse,
    update: updateWarehouse,
    remove: deleteWarehouse
  } = useRealTimeData('/api/inventory/warehouses');
  
  const { 
    data: transactions, 
    loading: transactionsLoading, 
    error: transactionsError
  } = useRealTimeData('/api/inventory/transactions');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleAdd = (type) => {
    setEditItem(null);
    setSelectedItemType(type);
    setFormOpen(true);
  };

  const handleEdit = (item, type) => {
    setEditItem(item);
    setSelectedItemType(type);
    setFormOpen(true);
  };

  const handleDelete = (item, type) => {
    setDeleteItem(item);
    setSelectedItemType(type);
    setDeleteDialogOpen(true);
  };

  const handleView = (item, type) => {
    setSelectedItem(item);
    setSelectedItemType(type);
    setDetailViewOpen(true);
  };

  const handleSave = async (formData) => {
    try {
      if (editItem) {
        switch (selectedItemType) {
          case 'category':
            await updateCategory(editItem.id, formData);
            showSnackbar(`Category "${formData.name}" updated successfully`);
            break;
          case 'product':
            await updateProduct(editItem.id, formData);
            showSnackbar(`Product "${formData.name}" updated successfully`);
            break;
          case 'warehouse':
            await updateWarehouse(editItem.id, formData);
            showSnackbar(`Warehouse "${formData.name}" updated successfully`);
            break;
          default:
            break;
        }
      } else {
        switch (selectedItemType) {
          case 'category':
            await createCategory(formData);
            showSnackbar(`Category "${formData.name}" created successfully`);
            break;
          case 'product':
            await createProduct(formData);
            showSnackbar(`Product "${formData.name}" created successfully`);
            break;
          case 'warehouse':
            await createWarehouse(formData);
            showSnackbar(`Warehouse "${formData.name}" created successfully`);
            break;
          default:
            break;
        }
      }
      setFormOpen(false);
      setEditItem(null);
    } catch (error) {
      showSnackbar(`Failed to save ${selectedItemType}: ${error.message}`, 'error');
    }
  };

  const handleConfirmDelete = async () => {
    try {
      switch (selectedItemType) {
        case 'category':
          await deleteCategory(deleteItem.id);
          showSnackbar(`Category "${deleteItem.name}" deleted successfully`);
          break;
        case 'product':
          await deleteProduct(deleteItem.id);
          showSnackbar(`Product "${deleteItem.name}" deleted successfully`);
          break;
        case 'warehouse':
          await deleteWarehouse(deleteItem.id);
          showSnackbar(`Warehouse "${deleteItem.name}" deleted successfully`);
          break;
        default:
          break;
      }
      setDeleteDialogOpen(false);
      setDeleteItem(null);
    } catch (error) {
      showSnackbar(`Failed to delete ${selectedItemType}: ${error.message}`, 'error');
    }
  };

  // Calculate metrics from real data
  const inventoryMetrics = {
    totalProducts: products.length,
    totalCategories: categories.length,
    totalWarehouses: warehouses.length,
    totalTransactions: transactions.length,
    lowStockCount: products.filter(prod => (prod.current_stock || 0) <= (prod.min_stock || 0)).length,
    totalValue: products.reduce((sum, prod) => sum + ((prod.current_stock || 0) * (prod.current_cost || 0)), 0)
  };

  const renderProductsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Products</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('product')}
        >
          Add Product
        </Button>
      </Box>

      {productsLoading && <LinearProgress />}
      
      {productsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {productsError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>SKU</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Stock</TableCell>
              <TableCell>Cost</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {products.map((product, index) => (
              <TableRow key={product.id || `product-${index}`}>
                <TableCell>{product.sku}</TableCell>
                <TableCell>{product.name}</TableCell>
                <TableCell>{product.category_name || ''}</TableCell>
                <TableCell>
                  <Chip
                    label={`${product.current_stock || 0} ${product.unit || 'units'}`}
                    color={product.current_stock <= product.min_stock ? 'error' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>${product.current_cost || 0}</TableCell>
                <TableCell>
                  <Chip
                    label={product.is_active ? 'Active' : 'Inactive'}
                    color={product.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(product, 'product')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(product, 'product')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(product, 'product')} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderCategoriesTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Categories</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('category')}
        >
          Add Category
        </Button>
      </Box>

      {categoriesLoading && <LinearProgress />}
      
      {categoriesError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {categoriesError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {categories.map((category, index) => (
              <TableRow key={category.id || `category-${index}`}>
                <TableCell>{category.name}</TableCell>
                <TableCell>{category.description || ''}</TableCell>
                <TableCell>
                  <Chip
                    label={category.is_active ? 'Active' : 'Inactive'}
                    color={category.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(category, 'category')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(category, 'category')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(category, 'category')} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderWarehousesTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Warehouses</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('warehouse')}
        >
          Add Warehouse
        </Button>
      </Box>

      {warehousesLoading && <LinearProgress />}
      
      {warehousesError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {warehousesError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Location</TableCell>
              <TableCell>Capacity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {warehouses.map((warehouse) => (
              <TableRow key={warehouse.id}>
                <TableCell>{warehouse.name}</TableCell>
                <TableCell>{warehouse.location || ''}</TableCell>
                <TableCell>{warehouse.capacity || 0}</TableCell>
                <TableCell>
                  <Chip
                    label={warehouse.is_active ? 'Active' : 'Inactive'}
                    color={warehouse.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(warehouse, 'warehouse')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(warehouse, 'warehouse')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(warehouse, 'warehouse')} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderTransactionsTab = () => (
    <Box>
      <Typography variant="h6" mb={2}>Inventory Transactions</Typography>

      {transactionsLoading && <LinearProgress />}
      
      {transactionsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {transactionsError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Product</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Quantity</TableCell>
              <TableCell>Unit Cost</TableCell>
              <TableCell>Total Cost</TableCell>
              <TableCell>Reference</TableCell>
              <TableCell>Date</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {transactions.map((transaction) => (
              <TableRow key={transaction.id}>
                <TableCell>{transaction.product_name || `Product ${transaction.product_id}`}</TableCell>
                <TableCell>
                  <Chip
                    label={transaction.transaction_type}
                    color={transaction.transaction_type === 'IN' ? 'success' : 'warning'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{transaction.quantity}</TableCell>
                <TableCell>${transaction.unit_cost || 0}</TableCell>
                <TableCell>${transaction.total_cost || 0}</TableCell>
                <TableCell>{transaction.reference || ''}</TableCell>
                <TableCell>
                  {transaction.created_at ? new Date(transaction.created_at).toLocaleDateString() : ''}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Inventory Management
      </Typography>

      {/* Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Products
              </Typography>
              <Typography variant="h4">
                {inventoryMetrics.totalProducts}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Categories
              </Typography>
              <Typography variant="h4">
                {inventoryMetrics.totalCategories}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Low Stock Items
              </Typography>
              <Typography variant="h4" color="error">
                {inventoryMetrics.lowStockCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Value
              </Typography>
              <Typography variant="h4">
                                                                   ${inventoryMetrics.totalValue ? inventoryMetrics.totalValue.toLocaleString() : ''}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Products" />
          <Tab label="Categories" />
          <Tab label="Warehouses" />
          <Tab label="Transactions" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && renderProductsTab()}
      {activeTab === 1 && renderCategoriesTab()}
      {activeTab === 2 && renderWarehousesTab()}
      {activeTab === 3 && renderTransactionsTab()}

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

      {/* Detail View Modal */}
      <DetailViewModal
        open={detailViewOpen}
        onClose={() => {
          setDetailViewOpen(false);
          setSelectedItem(null);
          setSelectedItemType('');
        }}
        data={selectedItem}
        type={selectedItemType}
        onEdit={(item) => {
          setDetailViewOpen(false);
          handleEdit(item, selectedItemType);
        }}
        title={`${selectedItemType ? selectedItemType.charAt(0).toUpperCase() + selectedItemType.slice(1) : 'Item'} Details`}
      />

      {/* Improved Form */}
      <ImprovedForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditItem(null);
        }}
        onSave={handleSave}
        data={editItem}
        type={selectedItemType}
        title={selectedItemType ? selectedItemType.charAt(0).toUpperCase() + selectedItemType.slice(1) : 'Item'}
        loading={categoriesLoading || productsLoading || warehousesLoading}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this {selectedItemType}? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InventoryModule;
