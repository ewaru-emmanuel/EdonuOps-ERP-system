import React, { useState } from 'react';
import {
  Box, Typography, Tabs, Tab, Paper, Grid, Card, CardContent,
  useTheme, useMediaQuery, Container, Button, Chip
} from '@mui/material';
import {
  Warehouse as WarehouseIcon,
  LocationOn as LocationIcon,
  LocalShipping as PickingIcon,
  Inventory2 as PutawayIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  QrCode as BarcodeIcon
} from '@mui/icons-material';

// Import WMS components
// Operations page removed; keep WMS loosely coupled from core inventory
import SmartLocationManagement from './components/SmartLocationManagement';
import SmartPickingOperations from './components/SmartPickingOperations';
import SmartPutawayOperations from './components/SmartPutawayOperations';
import SmartWMSAnalytics from './components/SmartWMSAnalytics';
import SmartWMSSettings from './components/SmartWMSSettings';

const WarehouseManagementModule = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const tabs = [
    {
      label: 'Locations',
      icon: <LocationIcon />,
      component: <SmartLocationManagement />
    },
    {
      label: 'Picking',
      icon: <PickingIcon />,
      component: <SmartPickingOperations />
    },
    {
      label: 'Putaway',
      icon: <PutawayIcon />,
      component: <SmartPutawayOperations />
    },
    {
      label: 'Analytics',
      icon: <AnalyticsIcon />,
      component: <SmartWMSAnalytics />
    },
    {
      label: 'Settings',
      icon: <SettingsIcon />,
      component: <SmartWMSSettings />
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Typography variant="h3" component="h1" sx={{ fontWeight: 'bold', mr: 2 }}>
            🏭 Warehouse Management System
          </Typography>
          <Chip 
            label="Advanced" 
            color="warning" 
            size="small" 
            sx={{ fontWeight: 'bold' }}
          />
        </Box>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Advanced warehouse operations for complex businesses
        </Typography>
        
        {/* Feature Highlights */}
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', bgcolor: 'primary.50' }}>
              <CardContent>
                <Typography variant="h6" color="primary" gutterBottom>
                  📍 Bin Management
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Organize inventory by locations and zones
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', bgcolor: 'success.50' }}>
              <CardContent>
                <Typography variant="h6" color="success.main" gutterBottom>
                  📦 Picking Operations
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Optimized picking routes and rules
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', bgcolor: 'warning.50' }}>
              <CardContent>
                <Typography variant="h6" color="warning.main" gutterBottom>
                  🔄 Putaway Strategies
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Smart putaway and storage optimization
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', bgcolor: 'info.50' }}>
              <CardContent>
                <Typography variant="h6" color="info.main" gutterBottom>
                  📊 WMS Analytics
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Performance metrics and optimization
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Advanced Features Banner */}
        <Card sx={{ mt: 3, bgcolor: 'warning.50', border: '1px solid', borderColor: 'warning.200' }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <BarcodeIcon sx={{ color: 'warning.main', mr: 1 }} />
              <Typography variant="h6" color="warning.main">
                Advanced Features Available
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary">
              This module includes advanced features like barcode scanning, batch/lot tracking, 
              cycle counting, and performance analytics. Perfect for warehouses with complex operations.
            </Typography>
          </CardContent>
        </Card>
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

export default WarehouseManagementModule;
