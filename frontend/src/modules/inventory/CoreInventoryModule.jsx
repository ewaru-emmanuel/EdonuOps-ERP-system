import React, { useState } from 'react';
import {
  Box, Typography, Tabs, Tab, Paper, Grid, Card, CardContent,
  useTheme, useMediaQuery, Container, Button
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Inventory as InventoryIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';

// Import core inventory components
import SmartInventoryDashboard from './components/SmartInventoryDashboard';
import SmartProductManagement from './components/SmartProductManagement';
import SmartStockLevels from './components/SmartStockLevels';
import SmartAdjustments from './components/SmartAdjustments';
import SmartInventoryReports from './components/SmartInventoryReports';
import SmartInventorySettings from './components/SmartInventorySettings';

const CoreInventoryModule = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const tabs = [
    {
      label: 'Dashboard',
      icon: <DashboardIcon />,
      component: <SmartInventoryDashboard />
    },
    {
      label: 'Products',
      icon: <InventoryIcon />,
      component: <SmartProductManagement />
    },
    {
      label: 'Stock Levels',
      icon: <TrendingUpIcon />,
      component: <SmartStockLevels />
    },
    {
      label: 'Adjustments',
      icon: <AddIcon />,
      component: <SmartAdjustments />
    },
    {
      label: 'Reports',
      icon: <AssessmentIcon />,
      component: <SmartInventoryReports />
    },
    {
      label: 'Settings',
      icon: <SettingsIcon />,
      component: <SmartInventorySettings />
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          📦 Core Inventory Management
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Essential inventory tracking for your business
        </Typography>
        
        {/* Feature Highlights */}
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', bgcolor: 'primary.50' }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  📊 Stock Overview
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Real-time stock levels and low stock alerts
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', bgcolor: 'success.50' }}>
              <CardContent>
                <Typography variant="h6" color="success.main" gutterBottom>
                  📦 Product Management
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Add, edit, and organize your products
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', bgcolor: 'warning.50' }}>
              <CardContent>
                <Typography variant="h6" color="warning.main" gutterBottom>
                  🔄 Stock Adjustments
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Count stock and make corrections
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', bgcolor: 'info.50' }}>
              <CardContent>
                <Typography variant="h6" color="info.main" gutterBottom>
                  📈 Reports & Analytics
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Track performance and trends
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Tabs */}
      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant={isMobile ? "scrollable" : "fullWidth"}
          scrollButtons={isMobile ? "auto" : false}
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': {
              minHeight: 64,
              fontSize: '0.9rem',
              fontWeight: 500
            }
          }}
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              label={tab.label}
              icon={tab.icon}
              iconPosition="start"
              sx={{
                textTransform: 'none',
                '& .MuiTab-iconWrapper': {
                  mr: 1
                }
              }}
            />
          ))}
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box sx={{ mt: 3 }}>
        {tabs[activeTab].component}
      </Box>
    </Container>
  );
};

export default CoreInventoryModule;
