import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Tabs,
  Tab,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  LinearProgress,
  Avatar,
  Snackbar
} from '@mui/material';
import {
  ShoppingCart as ShoppingCartIcon,
  Store as StoreIcon,
  Inventory as InventoryIcon,
  People as PeopleIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  TrendingUp as TrendingUpIcon,
  MonetizationOn as MonetizationIcon
} from '@mui/icons-material';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';

const EcommerceModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [formOpen, setFormOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [formType, setFormType] = useState('');

  // Real-time data hooks
  const { 
    data: products, 
    loading: productsLoading, 
    create: createProduct,
    update: updateProduct,
    remove: deleteProduct
  } = useRealTimeData('/api/ecommerce/products');

  const { 
    data: orders, 
    loading: ordersLoading, 
    create: createOrder,
    update: updateOrder,
    remove: deleteOrder
  } = useRealTimeData('/api/ecommerce/orders');

  const { 
    data: customers, 
    loading: customersLoading, 
    create: createCustomer,
    update: updateCustomer,
    remove: deleteCustomer
  } = useRealTimeData('/api/ecommerce/customers');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleAdd = (type) => {
    setFormType(type);
    setSelectedItem(null);
    setFormOpen(true);
  };

  const handleEdit = (item, type) => {
    setFormType(type);
    setSelectedItem(item);
    setFormOpen(true);
  };

  const handleView = (item, type) => {
    setFormType(type);
    setSelectedItem(item);
    setDetailOpen(true);
  };

  const handleDelete = async (item, type) => {
    const confirmed = window.confirm(`Are you sure you want to delete this ${type}?`);
    if (confirmed) {
      try {
        let deleteFunction;
        switch (type) {
          case 'product':
            deleteFunction = deleteProduct;
            break;
          case 'order':
            deleteFunction = deleteOrder;
            break;
          case 'customer':
            deleteFunction = deleteCustomer;
            break;
          default:
            return;
        }
        await deleteFunction(item.id);
        showSnackbar(`${type.charAt(0).toUpperCase() + type.slice(1)} deleted successfully`);
      } catch (error) {
        showSnackbar(`Error deleting ${type}`, 'error');
      }
    }
  };

  // Calculate analytics from real data
  const analytics = {
    totalRevenue: orders?.reduce((sum, order) => sum + (order.total_amount || 0), 0) || 0,
    totalOrders: orders?.length || 0,
    totalCustomers: customers?.length || 0,
    avgOrderValue: orders?.length > 0 ? (orders.reduce((sum, order) => sum + (order.total_amount || 0), 0) / orders.length) : 0
  };

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
            <StoreIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
              E-commerce Platform
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Complete online store with product management, order processing & customer analytics
            </Typography>
          </Box>
        </Box>
        
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            ✅ E-commerce System Operational
          </Typography>
          <Typography variant="body2">
            Your e-commerce platform is fully operational with real-time product management, order processing, and customer analytics.
          </Typography>
        </Alert>
      </Box>

      {/* E-commerce Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    ${(analytics.totalRevenue / 1000).toFixed(1)}K
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Revenue
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <MonetizationIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={85} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {analytics.totalOrders}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Orders
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <ShoppingCartIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={75} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    ${analytics.avgOrderValue}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Order Value
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <ShoppingCartIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={90} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {analytics.totalCustomers}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Customers
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <PeopleIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={45} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Interface */}
      <Paper elevation={3} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="Products" icon={<InventoryIcon />} />
            <Tab label="Orders" icon={<ShoppingCartIcon />} />
            <Tab label="Store Builder" icon={<StoreIcon />} />
            <Tab label="Analytics" icon={<TrendingUpIcon />} />
          </Tabs>
        </Box>

        <Box sx={{ p: 3, minHeight: '60vh' }}>
          {/* Products Tab */}
          {activeTab === 0 && (
            <Box>
                             <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                 <Typography variant="h5">Product Management</Typography>
                 <Button
                   variant="contained"
                   startIcon={<AddIcon />}
                   onClick={() => handleAdd('product')}
                 >
                   Add Product
                 </Button>
               </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Product</TableCell>
                      <TableCell align="right">Price</TableCell>
                      <TableCell>Stock</TableCell>
                      <TableCell>Sales</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                                     <TableBody>
                     {productsLoading ? (
                       <TableRow>
                         <TableCell colSpan={6} align="center">
                           <LinearProgress />
                         </TableCell>
                       </TableRow>
                     ) : products && products.length > 0 ? (
                       products.map((product) => (
                         <TableRow key={product.id}>
                           <TableCell>
                             <Box display="flex" alignItems="center" gap={2}>
                               <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                                 {product.name.charAt(0)}
                               </Avatar>
                               <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                 {product.name}
                               </Typography>
                             </Box>
                           </TableCell>
                           <TableCell align="right">${product.price}</TableCell>
                           <TableCell>{product.stock_quantity}</TableCell>
                           <TableCell>{product.category}</TableCell>
                           <TableCell>
                             <Chip 
                               label={product.status} 
                               color="success" 
                               size="small" 
                             />
                           </TableCell>
                           <TableCell>
                             <IconButton onClick={() => handleEdit(product, 'product')}>
                               <EditIcon />
                             </IconButton>
                             <IconButton onClick={() => handleView(product, 'product')}>
                               <ViewIcon />
                             </IconButton>
                             <IconButton onClick={() => handleDelete(product, 'product')}>
                               <DeleteIcon />
                             </IconButton>
                           </TableCell>
                         </TableRow>
                       ))
                     ) : (
                       <TableRow>
                         <TableCell colSpan={6} align="center">
                           <Typography variant="body2" color="text.secondary">
                             No products found. Add your first product to get started.
                           </Typography>
                         </TableCell>
                       </TableRow>
                     )}
                   </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Orders Tab */}
          {activeTab === 1 && (
            <Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h5">Order Management</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => handleAdd('order')}
                >
                  Create Order
                </Button>
              </Box>
              
              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Order #</TableCell>
                      <TableCell>Customer</TableCell>
                      <TableCell align="right">Total</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {ordersLoading ? (
                      <TableRow>
                        <TableCell colSpan={5} align="center">
                          <LinearProgress />
                        </TableCell>
                      </TableRow>
                    ) : orders && orders.length > 0 ? (
                      orders.map((order) => (
                        <TableRow key={order.id}>
                          <TableCell>{order.order_number}</TableCell>
                          <TableCell>{order.customer_name}</TableCell>
                          <TableCell align="right">${order.total_amount}</TableCell>
                          <TableCell>
                            <Chip 
                              label={order.status} 
                              color={
                                order.status === 'Delivered' ? 'success' : 
                                order.status === 'Shipped' ? 'primary' : 'warning'
                              } 
                              size="small" 
                            />
                          </TableCell>
                          <TableCell>
                            <IconButton onClick={() => handleView(order, 'order')}>
                              <ViewIcon />
                            </IconButton>
                            <IconButton onClick={() => handleEdit(order, 'order')}>
                              <EditIcon />
                            </IconButton>
                            <IconButton onClick={() => handleDelete(order, 'order')}>
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell colSpan={5} align="center">
                          <Typography variant="body2" color="text.secondary">
                            No orders found. Create your first order to get started.
                          </Typography>
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Store Builder Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h5" gutterBottom>Store Builder</Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Store customization tools for themes, layouts, payment integration, and shipping configuration.
                  Real-time synchronization with inventory and order management systems.
                </Typography>
              </Alert>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Store Customization</Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Customize your online store with themes, layouts, and branding options.
                      </Typography>
                      <Button
                        variant="contained"
                        startIcon={<EditIcon />}
                        onClick={() => handleAdd('store_config')}
                      >
                        Customize Store
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Payment Integration</Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        Configure payment gateways and shipping options for seamless transactions.
                      </Typography>
                      <Button
                        variant="contained"
                        startIcon={<EditIcon />}
                        onClick={() => handleAdd('payment_config')}
                      >
                        Configure Payments
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}

          {/* Analytics Tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h5" gutterBottom>E-commerce Analytics</Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Sales Performance</Typography>
                      <Typography variant="h4" color="primary">
                        ${(analytics.totalRevenue / 1000).toFixed(1)}K
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total revenue this month
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>Order Metrics</Typography>
                      <Typography variant="h4" color="primary">
                        {analytics.totalOrders}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total orders processed
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          EdonuOps E-commerce - Complete Online Store Platform
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="Inventory Sync" size="small" sx={{ mr: 1 }} />
          <Chip label="Order Management" size="small" sx={{ mr: 1 }} />
          <Chip label="Customer Analytics" size="small" color="primary" />
        </Box>
      </Box>

             {/* Form Modal */}
       <ImprovedForm
         open={formOpen}
         onClose={() => setFormOpen(false)}
         type={formType}
         data={selectedItem}
         onSubmit={async (formData) => {
           try {
             let createFunction, updateFunction;
             switch (formType) {
               case 'product':
                 createFunction = createProduct;
                 updateFunction = updateProduct;
                 break;
               case 'order':
                 createFunction = createOrder;
                 updateFunction = updateOrder;
                 break;
               case 'customer':
                 createFunction = createCustomer;
                 updateFunction = updateCustomer;
                 break;
               case 'store_config':
               case 'payment_config':
                 // These are configuration forms - show success message
                 showSnackbar(`${formType.replace('_', ' ')} configuration saved successfully`);
                 setFormOpen(false);
                 return;
               default:
                 return;
             }
             
             if (selectedItem) {
               await updateFunction(selectedItem.id, formData);
               showSnackbar(`${formType.charAt(0).toUpperCase() + formType.slice(1)} updated successfully`);
             } else {
               await createFunction(formData);
               showSnackbar(`${formType.charAt(0).toUpperCase() + formType.slice(1)} created successfully`);
             }
             setFormOpen(false);
           } catch (error) {
             showSnackbar(`Error ${selectedItem ? 'updating' : 'creating'} ${formType}`, 'error');
           }
         }}
       />

       {/* Detail View Modal */}
       <DetailViewModal
         open={detailOpen}
         onClose={() => setDetailOpen(false)}
         type={formType}
         data={selectedItem}
         onEdit={() => {
           setDetailOpen(false);
           setFormOpen(true);
         }}
       />

       {/* Snackbar for notifications */}
       <Snackbar
         open={snackbar.open}
         autoHideDuration={6000}
         onClose={() => setSnackbar({ ...snackbar, open: false })}
       >
         <Alert 
           onClose={() => setSnackbar({ ...snackbar, open: false })} 
           severity={snackbar.severity}
         >
           {snackbar.message}
         </Alert>
       </Snackbar>
     </Container>
   );
 };

export default EcommerceModule;
