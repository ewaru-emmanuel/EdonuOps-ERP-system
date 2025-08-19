import React, { useState, useEffect } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Paper,
  Container,
  useTheme,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Button,
  Chip,
  Alert
} from '@mui/material';
import {
  Receipt as TaxIcon,
  Calculate as CalculateIcon,
  Assessment as ReportIcon,
  Settings as SettingsIcon,
  TrendingUp as TrendingIcon,
  Warning as ComplianceIcon
} from '@mui/icons-material';

// Import tax sub-components
import TaxRatesManagement from './TaxRatesManagement';
import TaxCalculations from './TaxCalculations';
import TaxReporting from './TaxReporting';
import TaxCompliance from './TaxCompliance';
import TaxSettings from './TaxSettings';
import TaxAnalytics from './TaxAnalytics';

const TaxModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [taxData, setTaxData] = useState({
    totalTaxCollected: 0,
    totalTaxPaid: 0,
    pendingReturns: 0,
    complianceScore: 0
  });
  const theme = useTheme();

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  useEffect(() => {
    // Fetch tax summary data
    fetchTaxSummary();
  }, []);

  const fetchTaxSummary = async () => {
    try {
      // TODO: Replace with actual API call
      const mockData = {
        totalTaxCollected: 125000,
        totalTaxPaid: 98000,
        pendingReturns: 3,
        complianceScore: 95
      };
      setTaxData(mockData);
    } catch (error) {
      console.error('Error fetching tax summary:', error);
    }
  };

  const tabs = [
    {
      label: 'Tax Rates',
      icon: <TaxIcon />,
      component: <TaxRatesManagement />
    },
    {
      label: 'Calculations',
      icon: <CalculateIcon />,
      component: <TaxCalculations />
    },
    {
      label: 'Reporting',
      icon: <ReportIcon />,
      component: <TaxReporting />
    },
    {
      label: 'Compliance',
      icon: <ComplianceIcon />,
      component: <TaxCompliance />
    },
    {
      label: 'Analytics',
      icon: <TrendingIcon />,
      component: <TaxAnalytics />
    },
    {
      label: 'Settings',
      icon: <SettingsIcon />,
      component: <TaxSettings />
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          Tax Management System
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
          Comprehensive tax calculation, reporting, and compliance management
        </Typography>
      </Box>

      {/* Tax Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Tax Collected
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                ${taxData.totalTaxCollected.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Current fiscal year
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Tax Paid
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                ${taxData.totalTaxPaid.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Current fiscal year
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending Returns
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                {taxData.pendingReturns}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Due this quarter
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Compliance Score
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {taxData.complianceScore}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Overall compliance rating
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper elevation={3} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                minHeight: 64,
                fontSize: '0.875rem',
                fontWeight: 500,
                textTransform: 'none',
                '&.Mui-selected': {
                  color: theme.palette.primary.main,
                  fontWeight: 600
                }
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
                sx={{ minWidth: 'auto', px: 3 }}
              />
            ))}
          </Tabs>
        </Box>

        <Box sx={{ p: 3, minHeight: '60vh' }}>
          {tabs[activeTab].component}
        </Box>
      </Paper>
    </Container>
  );
};

export default TaxModule;




