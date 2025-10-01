import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme, TextField, FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  ShoppingCart as ProcurementIcon,
  Business as VendorIcon,
  Description as POIcon,
  TrendingUp as AnalyticsIcon,
  Assessment as AssessmentIcon,
  Assignment as AssignmentIcon,
  Support as SupportIcon,
  BarChart as BarChartIcon
} from '@mui/icons-material';
// Removed API imports to prevent authentication calls

import ProcurementDashboard from './ProcurementDashboard';
import VendorManagement from './VendorManagement';
import PurchaseOrderManagement from './PurchaseOrderManagement';
import ProcurementAnalytics from './ProcurementAnalytics';
import RFQManagement from './RFQManagement';
import ContractsManagement from './ContractsManagement';

const ProcurementModule = () => {
  const [searchParams] = useSearchParams();
  const feature = searchParams.get('feature') || 'dashboard';
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

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

  return (
    <Box sx={{ width: '100%', height: '100%', p: 2 }}>
      {renderFeature()}
      
      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ProcurementModule;
