import React, { useState } from 'react';
import {
  Box, Container, Grid, Card, CardContent, Typography, Button,
  Avatar, Chip, Alert, useTheme, useMediaQuery
} from '@mui/material';
import {
  TrendingUp, AccountBalance, Inventory, People, Business,
  CheckCircle, Warning, AttachMoney, ShoppingCart, Person
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const MagicDashboard = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  
  // Mock user data
  const [userProfile] = useState({
    name: 'John Smith',
    role: 'CEO',
    company: 'TechFlow Inc.'
  });

  // Mock enabled modules
  const [enabledModules] = useState(['financials', 'inventory', 'crm']);
  
  // Mock dashboard data
  const [dashboardData] = useState({
    financials: {
      cashFlow: 125000,
      cashFlowChange: 8.5,
      outstandingInvoices: 45000,
      overdueInvoices: 12000
    },
    inventory: {
      totalProducts: 1250,
      lowStockItems: 23,
      totalValue: 450000
    },
    crm: {
      totalCustomers: 342,
      newLeads: 28,
      conversionRate: 15.2,
      salesPipeline: 125000
    }
  });

  const renderFinancialsCard = () => {
    const data = dashboardData.financials;
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <AccountBalance />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight="bold">Financial Overview</Typography>
              <Typography variant="body2" color="text.secondary">Real-time financial metrics</Typography>
            </Box>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="h4" fontWeight="bold" color="primary.main">
                ${(data.cashFlow / 1000).toFixed(0)}K
              </Typography>
              <Typography variant="body2" color="text.secondary">Cash Flow</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                <TrendingUp sx={{ fontSize: 16, color: 'success.main' }} />
                <Typography variant="caption" color="success.main">
                  +{data.cashFlowChange}%
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="h4" fontWeight="bold" color="error.main">
                ${(data.overdueInvoices / 1000).toFixed(0)}K
              </Typography>
              <Typography variant="body2" color="text.secondary">Overdue</Typography>
            </Grid>
          </Grid>

          <Button
            variant="outlined"
            fullWidth
            sx={{ mt: 2 }}
            onClick={() => navigate('/finance')}
          >
            View Financials
          </Button>
        </CardContent>
      </Card>
    );
  };

  const renderInventoryCard = () => {
    const data = dashboardData.inventory;
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Avatar sx={{ bgcolor: 'success.main' }}>
              <Inventory />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight="bold">Inventory Status</Typography>
              <Typography variant="body2" color="text.secondary">Stock levels and alerts</Typography>
            </Box>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {data.totalProducts}
              </Typography>
              <Typography variant="body2" color="text.secondary">Total Products</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="h4" fontWeight="bold" color="warning.main">
                {data.lowStockItems}
              </Typography>
              <Typography variant="body2" color="text.secondary">Low Stock</Typography>
            </Grid>
          </Grid>

          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Inventory Value
            </Typography>
            <Typography variant="h5" fontWeight="bold" color="primary.main">
              ${(data.totalValue / 1000).toFixed(0)}K
            </Typography>
          </Box>

          {data.lowStockItems > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              {data.lowStockItems} items need reordering
            </Alert>
          )}

          <Button
            variant="outlined"
            fullWidth
            sx={{ mt: 2 }}
            onClick={() => navigate('/inventory')}
          >
            View Inventory
          </Button>
        </CardContent>
      </Card>
    );
  };

  const renderCRMCard = () => {
    const data = dashboardData.crm;
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
            <Avatar sx={{ bgcolor: 'info.main' }}>
              <People />
            </Avatar>
            <Box>
              <Typography variant="h6" fontWeight="bold">Customer Insights</Typography>
              <Typography variant="body2" color="text.secondary">Sales and customer metrics</Typography>
            </Box>
          </Box>

          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="h4" fontWeight="bold" color="info.main">
                {data.totalCustomers}
              </Typography>
              <Typography variant="body2" color="text.secondary">Customers</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="h4" fontWeight="bold" color="success.main">
                {data.newLeads}
              </Typography>
              <Typography variant="body2" color="text.secondary">New Leads</Typography>
            </Grid>
          </Grid>

          <Box sx={{ mt: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Sales Pipeline
            </Typography>
            <Typography variant="h5" fontWeight="bold" color="primary.main">
              ${(data.salesPipeline / 1000).toFixed(0)}K
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {data.conversionRate}% conversion rate
            </Typography>
          </Box>

          <Button
            variant="outlined"
            fullWidth
            sx={{ mt: 2 }}
            onClick={() => navigate('/crm')}
          >
            View CRM
          </Button>
        </CardContent>
      </Card>
    );
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mb: 1 }}>
          Welcome back, {userProfile.name}! 👋
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          Here's what's happening with your business today
        </Typography>
        
        <Alert severity="info">
          <Typography variant="body2">
            <strong>Tip:</strong> Your dashboard is personalized based on your enabled modules. 
            You can customize this view in your settings.
          </Typography>
        </Alert>
      </Box>

      {/* Module Cards */}
      <Grid container spacing={3}>
        {enabledModules.includes('financials') && (
          <Grid item xs={12} md={6} lg={4}>
            {renderFinancialsCard()}
          </Grid>
        )}
        
        {enabledModules.includes('inventory') && (
          <Grid item xs={12} md={6} lg={4}>
            {renderInventoryCard()}
          </Grid>
        )}
        
        {enabledModules.includes('crm') && (
          <Grid item xs={12} md={6} lg={4}>
            {renderCRMCard()}
          </Grid>
        )}
      </Grid>

      {/* Quick Actions */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" fontWeight="bold" sx={{ mb: 2 }}>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          {enabledModules.includes('financials') && (
            <Grid item xs={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<AttachMoney />}
                onClick={() => navigate('/finance/invoices/new')}
              >
                New Invoice
              </Button>
            </Grid>
          )}
          
          {enabledModules.includes('inventory') && (
            <Grid item xs={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Inventory />}
                onClick={() => navigate('/inventory/products/new')}
              >
                Add Product
              </Button>
            </Grid>
          )}
          
          {enabledModules.includes('crm') && (
            <Grid item xs={6} md={3}>
              <Button
                variant="outlined"
                fullWidth
                startIcon={<Person />}
                onClick={() => navigate('/crm/leads/new')}
              >
                New Lead
              </Button>
            </Grid>
          )}
        </Grid>
      </Box>
    </Container>
  );
};

export default MagicDashboard;
