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
  const [activeSection, setActiveSection] = useState('dashboard');
  const theme = useTheme();

  const sections = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <ProcurementIcon />,
      component: <ProcurementDashboard />
    },
    {
      id: 'vendors',
      label: 'Vendors',
      icon: <VendorIcon />,
      component: <VendorManagement />
    },
    {
      id: 'purchase-orders',
      label: 'Purchase Orders',
      icon: <POIcon />,
      component: <PurchaseOrderManagement />
    },
    {
      id: 'rfq',
      label: 'RFx / RFQ',
      icon: <VendorIcon />,
      component: <RFQManagement />
    },
    {
      id: 'analytics',
      label: 'Analytics',
      icon: <AnalyticsIcon />,
      component: <ProcurementAnalytics />
    }
    ,{
      id: 'contracts',
      label: 'Contracts',
      icon: <VendorIcon />,
      component: <ContractsManagement />
    }
  ];

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
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h2" gutterBottom sx={{ fontWeight: 'bold' }}>
          Procurement Management
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Manage vendors, purchase orders, and procurement workflows
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

export default ProcurementModule;
