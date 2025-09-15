import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
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
  ShoppingCart as ProcurementIcon,
  Business as VendorIcon,
  Description as POIcon,
  TrendingUp as AnalyticsIcon
} from '@mui/icons-material';

import ProcurementDashboard from './ProcurementDashboard';
import VendorManagement from './VendorManagement';
import PurchaseOrderManagement from './PurchaseOrderManagement';
import ProcurementAnalytics from './ProcurementAnalytics';
import RFQManagement from './RFQManagement';
import ContractsManagement from './ContractsManagement';

const ProcurementModule = () => {
  const [searchParams] = useSearchParams();
  const feature = searchParams.get('feature') || 'dashboard';
  const theme = useTheme();

  const renderFeature = () => {
    switch (feature) {
      case 'dashboard':
        return <ProcurementDashboard />;
      case 'vendors':
        return <VendorManagement />;
      case 'purchase-orders':
        return <PurchaseOrderManagement />;
      case 'rfq':
        return <RFQManagement />;
      case 'contracts':
        return <ContractsManagement />;
      case 'analytics':
        return <ProcurementAnalytics />;
      default:
        return <ProcurementDashboard />;
    }
  };

  const quickStats = [
    {
      title: 'Total POs',
      value: '24',
      change: '+12%',
      color: 'primary'
    },
    {
      title: 'Pending Approval',
      value: '8',
      change: '-3',
      color: 'warning'
    },
    {
      title: 'Total Value',
      value: '$45,230',
      change: '+8.5%',
      color: 'success'
    },
    {
      title: 'Active Vendors',
      value: '15',
      change: '+2',
      color: 'info'
    }
  ];

  return (
    <Box sx={{ width: '100%', height: '100%', p: 2 }}>
      {renderFeature()}
    </Box>
  );
};

export default ProcurementModule;
