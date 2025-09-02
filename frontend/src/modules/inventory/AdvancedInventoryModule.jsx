import React, { useState } from 'react';
import {
  Box, Typography, Tabs, Tab, Paper, Grid, Card, CardContent,
  useTheme, useMediaQuery, Container, Button
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Inventory as InventoryIcon,
  Warehouse as WarehouseIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

// Import smart components
import SmartInventoryDashboard from './components/SmartInventoryDashboard';
import SmartProductManagement from './components/SmartProductManagement';
import SmartWarehouseOperations from './components/SmartWarehouseOperations';
import SmartAnalytics from './components/SmartAnalytics';
import SmartSettings from './components/SmartSettings';
import ManagersDashboard from './components/ManagersDashboard';
import DataIntegrityAdminPanel from './components/DataIntegrityAdminPanel';
import InventoryTakingPopup from './components/InventoryTakingPopup';
import WarehouseInventoryView from './components/WarehouseInventoryView';

const AdvancedInventoryModule = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activeTab, setActiveTab] = useState(0);
  const [inventoryTakingOpen, setInventoryTakingOpen] = useState(false);

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
      label: 'Manager\'s View',
      icon: <DashboardIcon />,
      component: <ManagersDashboard />
    },
    {
      label: 'Product Management',
      icon: <InventoryIcon />,
      component: <SmartProductManagement />
    },
    {
      label: 'Inventory View',
      icon: <InventoryIcon />,
      component: <WarehouseInventoryView />
    },
    {
      label: 'Operations',
      icon: <TrendingUpIcon />,
      component: <SmartWarehouseOperations />
    },
    {
      label: 'Analytics',
      icon: <AnalyticsIcon />,
      component: <SmartAnalytics />
    },
    {
      label: 'Data Integrity',
      icon: <SecurityIcon />,
      component: <DataIntegrityAdminPanel />
    },
    {
      label: 'Settings',
      icon: <SettingsIcon />,
      component: <SmartSettings />
    }
  ];

  const handleInventoryTakingSave = (data) => {
    console.log('Inventory taking data:', data);
    // TODO: Submit to API
    // API call to save inventory count
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          📦 Advanced Inventory Management
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Enterprise-Grade Inventory System with AI-Powered Insights
        </Typography>
        
        {/* Feature Highlights */}
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'primary.light', color: 'white' }}>
              <CardContent sx={{ py: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SpeedIcon />
                  <Typography variant="body2" fontWeight="bold">
                    Real-Time Performance
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
              <CardContent sx={{ py: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <InventoryIcon />
                  <Typography variant="body2" fontWeight="bold">
                    Inventory Taking
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'warning.light', color: 'white' }}>
              <CardContent sx={{ py: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TrendingUpIcon />
                  <Typography variant="body2" fontWeight="bold">
                    Advanced Analytics
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ bgcolor: 'info.light', color: 'white' }}>
              <CardContent sx={{ py: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <SecurityIcon />
                  <Typography variant="body2" fontWeight="bold">
                    Data Integrity
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Box sx={{ mt: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<InventoryIcon />}
            onClick={() => setInventoryTakingOpen(true)}
            sx={{ fontWeight: 'bold' }}
          >
            Start Inventory Count
          </Button>
          <Button
            variant="outlined"
            startIcon={<TrendingUpIcon />}
            sx={{ fontWeight: 'bold' }}
          >
            View Reports
          </Button>
          <Button
            variant="outlined"
            startIcon={<SecurityIcon />}
            sx={{ fontWeight: 'bold' }}
          >
            Data Integrity Check
          </Button>
        </Box>
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
              fontWeight: 600
            }
          }}
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {tab.icon}
                  {tab.label}
                </Box>
              }
              sx={{
                '&.Mui-selected': {
                  color: 'primary.main',
                  fontWeight: 'bold'
                }
              }}
            />
          ))}
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box sx={{ minHeight: '60vh' }}>
        {tabs[activeTab].component}
      </Box>

      {/* Footer */}
      <Box sx={{ mt: 4, pt: 3, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="body2" color="text.secondary" align="center">
          🚀 Enterprise-Grade WMS • Real-Time Operations • AI-Powered Insights • Mobile-First Design
        </Typography>
      </Box>

      {/* Inventory Taking Popup */}
      <InventoryTakingPopup
        open={inventoryTakingOpen}
        onClose={() => setInventoryTakingOpen(false)}
        onSave={handleInventoryTakingSave}
      />
    </Container>
  );
};

export default AdvancedInventoryModule;
