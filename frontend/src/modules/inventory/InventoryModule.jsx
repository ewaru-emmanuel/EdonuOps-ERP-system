import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';

// Import inventory components
import SmartInventoryDashboard from './components/SmartInventoryDashboard';
import SmartProductManagement from './components/SmartProductManagement';
import SmartStockLevels from './components/SmartStockLevels';
import SmartAdjustments from './components/SmartAdjustments';
import SmartTransfers from './components/SmartTransfers';
import SmartInventoryReports from './components/SmartInventoryReports';
import SmartInventorySettings from './components/SmartInventorySettings';

const InventoryModule = () => {
  const [searchParams] = useSearchParams();
  const feature = searchParams.get('feature') || 'dashboard';

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

export default InventoryModule;

