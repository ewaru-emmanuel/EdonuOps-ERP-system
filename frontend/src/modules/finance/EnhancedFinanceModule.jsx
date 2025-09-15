import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  Work as WorkIcon,
  Settings as SettingsIcon,
  Public as PublicIcon,
  Label as LabelIcon,
  Assessment as AssessmentIcon,
  Business as BusinessIcon,
  Payment as PaymentIcon,
  Receipt as ReceiptIcon,
  TrendingUp as TrendingUpIcon,
  LocalTaxi as TaxIcon,
  AccountBalanceWallet as BankIcon,
  BarChart as BarChartIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

// Import all Finance components
import { CoAProvider } from './context/CoAContext';
import ChartOfAccounts from './ChartOfAccounts';
import SmartDashboard from './components/SmartDashboard';
import SmartGeneralLedger from './components/SmartGeneralLedger';
import SmartAccountsPayable from './components/SmartAccountsPayable';
import SmartAccountsReceivable from './components/SmartAccountsReceivable';
import SmartFixedAssets from './components/SmartFixedAssets';
import SmartBudgeting from './components/SmartBudgeting';
import SmartTaxManagement from './components/SmartTaxManagement';
import SmartBankReconciliation from './components/SmartBankReconciliation';
import SmartFinancialReports from './components/SmartFinancialReports';
import SmartAuditTrail from './components/SmartAuditTrail';
import WorkflowBasedUX from './components/WorkflowBasedUX';
import StatutoryModuleManager from './components/StatutoryModuleManager';
import LocalizationManager from './components/LocalizationManager';
import TaggingSystem from './components/TaggingSystem';

const EnhancedFinanceModule = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const tabs = [
    // Core Finance Operations
    {
      label: 'Dashboard',
      icon: <AssessmentIcon />,
      component: <SmartDashboard />
    },
    {
      label: 'General Ledger',
      icon: <AccountBalanceIcon />,
      component: <SmartGeneralLedger />
    },
    {
      label: 'Chart of Accounts',
      icon: <BusinessIcon />,
      component: (
        <CoAProvider>
          <ChartOfAccounts />
        </CoAProvider>
      )
    },
    {
      label: 'Accounts Payable',
      icon: <PaymentIcon />,
      component: <SmartAccountsPayable />
    },
    {
      label: 'Accounts Receivable',
      icon: <ReceiptIcon />,
      component: <SmartAccountsReceivable />
    },
    {
      label: 'Fixed Assets',
      icon: <BusinessIcon />,
      component: <SmartFixedAssets />
    },
    {
      label: 'Budgeting',
      icon: <TrendingUpIcon />,
      component: <SmartBudgeting />
    },
    {
      label: 'Tax Management',
      icon: <TaxIcon />,
      component: <SmartTaxManagement />
    },
    {
      label: 'Bank Reconciliation',
      icon: <BankIcon />,
      component: <SmartBankReconciliation />
    },
    {
      label: 'Financial Reports',
      icon: <BarChartIcon />,
      component: <SmartFinancialReports />
    },
    {
      label: 'Audit Trail',
      icon: <SecurityIcon />,
      component: <SmartAuditTrail />
    },
    // Advanced Features
    {
      label: 'Business Workflows',
      icon: <WorkIcon />,
      component: <WorkflowBasedUX />
    },
    {
      label: 'Statutory Modules',
      icon: <SettingsIcon />,
      component: <StatutoryModuleManager />
    },
    {
      label: 'Country & Compliance',
      icon: <PublicIcon />,
      component: <LocalizationManager />
    },
    {
      label: 'Tagging System',
      icon: <LabelIcon />,
      component: <TaggingSystem />
    }
  ];

  return (
    <Box sx={{ width: '100%', height: '100%', backgroundColor: '#f8f9fa', overflow: 'auto', p: 2 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Complete Finance Module
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Comprehensive financial management with core accounting operations, advanced CoA features, 
          workflow automation, compliance management, and localization support.
        </Typography>
        
        {/* Feature Overview */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', p: 2 }}>
                <AssessmentIcon color="primary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="subtitle2">Dashboard</Typography>
                <Typography variant="caption" color="text.secondary">
                  Financial overview & KPIs
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', p: 2 }}>
                <AccountBalanceIcon color="success" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="subtitle2">General Ledger</Typography>
                <Typography variant="caption" color="text.secondary">
                  Core accounting entries
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', p: 2 }}>
                <BusinessIcon color="warning" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="subtitle2">Chart of Accounts</Typography>
                <Typography variant="caption" color="text.secondary">
                  Progressive CoA management
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', p: 2 }}>
                <PaymentIcon color="info" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="subtitle2">Payables</Typography>
                <Typography variant="caption" color="text.secondary">
                  Vendor management
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', p: 2 }}>
                <ReceiptIcon color="secondary" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="subtitle2">Receivables</Typography>
                <Typography variant="caption" color="text.secondary">
                  Customer management
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={2}>
            <Card>
              <CardContent sx={{ textAlign: 'center', p: 2 }}>
                <WorkIcon color="error" sx={{ fontSize: 32, mb: 1 }} />
                <Typography variant="subtitle2">Workflows</Typography>
                <Typography variant="caption" color="text.secondary">
                  Process automation
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Navigation Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange} variant="scrollable" scrollButtons="auto">
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              label={tab.label}
              icon={tab.icon}
              iconPosition="start"
              sx={{ minHeight: 64 }}
            />
          ))}
        </Tabs>
      </Box>

      {/* Tab Content */}
      <Box sx={{ mt: 3 }}>
        {tabs[activeTab].component}
      </Box>
    </Box>
  );
};

export default EnhancedFinanceModule;
