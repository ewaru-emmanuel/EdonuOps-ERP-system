import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box, Typography, Paper, Grid, Card, CardContent,
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
import SmartTransfers from './components/SmartTransfers';
// Removed apiClient to prevent authentication calls

const CoreInventoryModule = () => {
  const [searchParams] = useSearchParams();
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
      {renderFeature()}
    </Box>
  );
};

export default CoreInventoryModule;
