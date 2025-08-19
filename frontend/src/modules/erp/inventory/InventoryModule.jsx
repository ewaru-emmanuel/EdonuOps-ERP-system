import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  IconButton,
  useTheme
} from '@mui/material';
import {
  Add as AddIcon,
  Inventory as InventoryIcon,
  Category as CategoryIcon,
  LocalShipping as ReceiptIcon,
  TrendingUp as AnalyticsIcon,
  Warehouse as WarehouseIcon
} from '@mui/icons-material';

import InventoryDashboard from './InventoryDashboard';
import ProductManagement from './ProductManagement';
import InventoryTransactions from './InventoryTransactions';
import ReceiptManagement from './ReceiptManagement';
import WarehouseManagement from './WarehouseManagement';
import InventoryAnalytics from './InventoryAnalytics';

const InventoryModule = () => {
  const [activeSection, setActiveSection] = useState('dashboard');
  const theme = useTheme();

  const sections = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <InventoryIcon />,
      component: <InventoryDashboard />
    },
    {
      id: 'products',
      label: 'Products',
      icon: <CategoryIcon />,
      component: <ProductManagement />
    },
    {
      id: 'transactions',
      label: 'Transactions',
      icon: <InventoryIcon />,
      component: <InventoryTransactions />
    },
    {
      id: 'receipts',
      label: 'Receipts',
      icon: <ReceiptIcon />,
      component: <ReceiptManagement />
    },
    {
      id: 'warehouses',
      label: 'Warehouses',
      icon: <WarehouseIcon />,
      component: <WarehouseManagement />
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: <AnalyticsIcon />,
      component: <InventoryAnalytics />
    }
  ];

  const quickStats = [
    {
      title: 'Total Products',
      value: '156',
      change: '+8',
      color: 'primary'
    },
    {
      title: 'Total Stock',
      value: '2,450',
      change: '+125',
      color: 'success'
    },
    {
      title: 'Stock Value',
      value: '$89,230',
      change: '+12.5%',
      color: 'info'
    },
    {
      title: 'Low Stock Items',
      value: '12',
      change: '-3',
      color: 'warning'
    }
  ];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h2" gutterBottom sx={{ fontWeight: 'bold' }}>
          Inventory Management
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Manage products, track inventory levels, and monitor stock movements
        </Typography>
      </Box>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {quickStats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card elevation={2} sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Box>
                    <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                      {stat.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {stat.title}
                    </Typography>
                    <Chip
                      label={stat.change}
                      size="small"
                      color={stat.color}
                      sx={{ fontSize: '0.75rem' }}
                    />
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Navigation Tabs */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {sections.map((section) => (
            <Button
              key={section.id}
              variant={activeSection === section.id ? 'contained' : 'outlined'}
              startIcon={section.icon}
              onClick={() => setActiveSection(section.id)}
              sx={{
                textTransform: 'none',
                fontWeight: activeSection === section.id ? 600 : 400,
                borderRadius: 2,
                px: 3,
                py: 1
              }}
            >
              {section.label}
            </Button>
          ))}
        </Box>
      </Box>

      {/* Content */}
      <Box>
        {sections.find(s => s.id === activeSection)?.component}
      </Box>
    </Box>
  );
};

export default InventoryModule;
