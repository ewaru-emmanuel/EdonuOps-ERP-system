import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  Avatar,
  LinearProgress,
  Alert
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Warning,
  CheckCircle,
  Add as AddIcon,
  Inventory,
  LocalShipping,
  Category,
  AttachMoney
} from '@mui/icons-material';

const InventoryDashboard = () => {
  const recentTransactions = [
    {
      id: 'TXN-001',
      product: 'Laptop Dell XPS 13',
      type: 'IN',
      quantity: 25,
      warehouse: 'Main Warehouse',
      date: '2024-01-15',
      reference: 'PO-001'
    },
    {
      id: 'TXN-002',
      product: 'Office Chair',
      type: 'OUT',
      quantity: 5,
      warehouse: 'Main Warehouse',
      date: '2024-01-15',
      reference: 'SO-001'
    },
    {
      id: 'TXN-003',
      product: 'Wireless Mouse',
      type: 'IN',
      quantity: 100,
      warehouse: 'Main Warehouse',
      date: '2024-01-14',
      reference: 'PO-002'
    },
    {
      id: 'TXN-004',
      product: 'Monitor 24"',
      type: 'OUT',
      quantity: 8,
      warehouse: 'Main Warehouse',
      date: '2024-01-14',
      reference: 'SO-002'
    }
  ];

  const lowStockItems = [
    {
      product: 'Wireless Keyboard',
      current_stock: 3,
      min_stock: 10,
      category: 'Electronics'
    },
    {
      product: 'USB Cables',
      current_stock: 5,
      min_stock: 20,
      category: 'Accessories'
    },
    {
      product: 'Desk Lamp',
      current_stock: 2,
      min_stock: 8,
      category: 'Office Supplies'
    },
    {
      product: 'Paper Clips',
      current_stock: 1,
      min_stock: 15,
      category: 'Office Supplies'
    }
  ];

  const getTransactionIcon = (type) => {
    switch (type) {
      case 'IN': return <TrendingUp color="success" />;
      case 'OUT': return <TrendingDown color="error" />;
      default: return <Inventory />;
    }
  };

  const getTransactionColor = (type) => {
    switch (type) {
      case 'IN': return 'success';
      case 'OUT': return 'error';
      default: return 'default';
    }
  };

  return (
    <Grid container spacing={3}>
      {/* Stock Overview */}
      <Grid item xs={12} lg={8}>
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                Stock Overview
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                size="small"
                sx={{ textTransform: 'none' }}
              >
                Add Product
              </Button>
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main', mb: 1 }}>
                    156
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Products
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main', mb: 1 }}>
                    2,450
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Stock
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main', mb: 1 }}>
                    $89,230
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Stock Value
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box sx={{ textAlign: 'center', p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main', mb: 1 }}>
                    12
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Low Stock Items
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Low Stock Alerts */}
      <Grid item xs={12} lg={4}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 3 }}>
              Low Stock Alerts
            </Typography>
            
            <List sx={{ p: 0 }}>
              {lowStockItems.map((item, index) => (
                <ListItem
                  key={index}
                  sx={{
                    border: '1px solid',
                    borderColor: 'warning.main',
                    borderRadius: 1,
                    mb: 2,
                    bgcolor: 'warning.50'
                  }}
                >
                  <ListItemIcon>
                    <Warning color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>
                        {item.product}
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Box component="span" sx={{ display: 'block', fontSize: '0.875rem', color: 'text.secondary' }}>
                          {item.category}
                        </Box>
                        <Box component="span" sx={{ display: 'block', fontSize: '0.75rem', color: 'warning.main' }}>
                          Stock: {item.current_stock} / Min: {item.min_stock}
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>

            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                color="warning"
                fullWidth
                sx={{ textTransform: 'none' }}
              >
                View All Alerts
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Recent Transactions */}
      <Grid item xs={12} lg={8}>
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                Recent Transactions
              </Typography>
              <Button
                variant="outlined"
                startIcon={<LocalShipping />}
                size="small"
                sx={{ textTransform: 'none' }}
              >
                View All
              </Button>
            </Box>
            
            <List sx={{ p: 0 }}>
              {recentTransactions.map((transaction, index) => (
                <ListItem
                  key={transaction.id}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    '&:last-child': { mb: 0 }
                  }}
                >
                  <ListItemIcon>
                    {getTransactionIcon(transaction.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>
                          {transaction.product}
                        </Box>
                        <Box component="span">
                          <Chip
                            label={`${transaction.type} ${transaction.quantity}`}
                            size="small"
                            color={getTransactionColor(transaction.type)}
                            sx={{ textTransform: 'uppercase' }}
                          />
                        </Box>
                      </Box>
                    }
                    secondary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                        <Box component="span" sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
                          {transaction.warehouse} • {transaction.reference}
                        </Box>
                        <Box component="span" sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                          {transaction.date}
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Quick Actions */}
      <Grid item xs={12} lg={4}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 3 }}>
              Quick Actions
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  fullWidth
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Add Product
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<LocalShipping />}
                  fullWidth
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Receive Stock
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<Inventory />}
                  fullWidth
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Issue Stock
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<Category />}
                  fullWidth
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Stock Count
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Stock Movement Chart */}
      <Grid item xs={12}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
              Stock Movement (Last 7 Days)
            </Typography>
            
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Stock In</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>+450 units</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={75} 
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Stock Out</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>-320 units</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={60} 
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default InventoryDashboard;
