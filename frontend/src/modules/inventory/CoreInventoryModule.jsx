import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Paper, Grid, Card, CardContent,
  useTheme, useMediaQuery, Container, Button, Tabs, Tab
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Inventory as InventoryIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  Category as CategoryIcon,
  Storage as StorageIcon,
  SwapHoriz as TransferIcon,
  Report as ReportIcon
} from '@mui/icons-material';

// Import core inventory components
import SmartInventoryDashboard from './components/SmartInventoryDashboard';
import SmartProductManagement from './components/SmartProductManagement';
import SmartStockLevels from './components/SmartStockLevels';
import SmartAdjustments from './components/SmartAdjustments';
import SmartInventoryReports from './components/SmartInventoryReports';
import SmartInventorySettings from './components/SmartInventorySettings';
import SmartTransfers from './components/SmartTransfers';
// Removed apiClient to prevent authentication calls

const CoreInventoryModule = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const feature = searchParams.get('feature') || 'dashboard';
  const [warehousesCount, setWarehousesCount] = useState(0);

  useEffect(() => {
    const loadWarehouses = async () => {
      try {
        // Mock get warehouses - no API call
        console.log('Mock get warehouses');
        const list = [];
        setWarehousesCount(Array.isArray(list) ? list.length : 0);
      } catch {
        setWarehousesCount(0);
      }
    };
    loadWarehouses();
  }, []);

  const handleTabChange = (event, newValue) => {
    const featureMap = {
      0: 'dashboard',
      1: 'products',
      2: 'stock-levels',
      3: 'adjustments',
      4: 'transfers',
      5: 'reports',
      6: 'settings'
    };
    setSearchParams({ feature: featureMap[newValue] });
  };

  const getTabIndex = () => {
    const featureMap = {
      'dashboard': 0,
      'products': 1,
      'stock-levels': 2,
      'adjustments': 3,
      'transfers': 4,
      'reports': 5,
      'settings': 6
    };
    return featureMap[feature] || 0;
  };

  const renderFeature = () => {
    switch (feature) {
      case 'dashboard':
        return <SmartInventoryDashboard />;
      case 'products':
        return <SmartProductManagement />;
      case 'stock-levels':
        return <SmartStockLevels />;
      case 'adjustments':
        return <SmartAdjustments />;
      case 'transfers':
        return <SmartTransfers />;
      case 'reports':
        return <SmartInventoryReports />;
      case 'settings':
        return <SmartInventorySettings />;
      default:
        return <SmartInventoryDashboard />;
    }
  };

  return (
    <Box sx={{ width: '100%', height: '100%', p: 2 }}>
      {/* Navigation Tabs */}
      <Paper sx={{ mb: 3, borderRadius: 2 }}>
        <Tabs
          value={getTabIndex()}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              minHeight: 64,
              textTransform: 'none',
              fontSize: '0.875rem',
              fontWeight: 500,
            },
            '& .Mui-selected': {
              color: 'primary.main',
              fontWeight: 600,
            },
          }}
        >
          <Tab
            icon={<DashboardIcon />}
            label="Dashboard"
            iconPosition="start"
          />
          <Tab
            icon={<CategoryIcon />}
            label="Products"
            iconPosition="start"
          />
          <Tab
            icon={<StorageIcon />}
            label="Stock Levels"
            iconPosition="start"
          />
          <Tab
            icon={<SettingsIcon />}
            label="Adjustments"
            iconPosition="start"
          />
          <Tab
            icon={<TransferIcon />}
            label="Transfers"
            iconPosition="start"
          />
          <Tab
            icon={<ReportIcon />}
            label="Reports"
            iconPosition="start"
          />
          <Tab
            icon={<SettingsIcon />}
            label="Settings"
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      {/* Feature Content */}
      {renderFeature()}
    </Box>
  );
};

export default CoreInventoryModule;
