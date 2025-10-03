import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Box, Typography, CircularProgress, Alert } from '@mui/material';
import { CoAProvider } from './context/CoAContext';

// Import existing finance components
import SmartDashboard from './components/SmartDashboard';
import SmartGeneralLedger from './components/SmartGeneralLedger';
import BusinessFinanceDashboard from './components/BusinessFinanceDashboard';
import ManualJournalEntry from './components/ManualJournalEntry';
import TrialBalance from './components/TrialBalance';
import ChartOfAccounts from './ChartOfAccounts';
import SmartAccountsPayable from './components/SmartAccountsPayable';
import SmartAccountsReceivable from './components/SmartAccountsReceivable';
import SmartFixedAssets from './components/SmartFixedAssets';
import SmartBudgeting from './components/SmartBudgeting';
import SmartTaxManagement from './components/SmartTaxManagement';
import SmartBankReconciliation from './components/SmartBankReconciliation';
import SmartFinancialReports from './components/SmartFinancialReports';
import SmartAuditTrail from './components/SmartAuditTrail';
import DailyCycleManager from './components/DailyCycleManager';

const FinanceModule = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const feature = searchParams.get('feature') || 'dashboard';

  const handleManualJournalClose = () => {
    // Navigate back to dashboard when closing manual journal entry
    setSearchParams({ feature: 'dashboard' });
  };

  const handleManualJournalSuccess = () => {
    // Navigate back to dashboard after successful entry creation
    setSearchParams({ feature: 'dashboard' });
  };

  const renderFeature = () => {
    switch (feature) {
      case 'dashboard':
        return <SmartDashboard />;
      case 'business-transactions':
        return <BusinessFinanceDashboard />;
      case 'manual-journal':
        return <ManualJournalEntry 
          open={true} 
          onClose={handleManualJournalClose} 
          onSuccess={handleManualJournalSuccess} 
        />;
      case 'trial-balance':
        return <TrialBalance />;
      case 'advanced-reports':
        return <SmartFinancialReports />;
      case 'general-ledger':
        return <SmartGeneralLedger />;
      case 'chart-of-accounts':
        return <ChartOfAccounts />;
      case 'accounts-payable':
        return <SmartAccountsPayable />;
      case 'accounts-receivable':
        return <SmartAccountsReceivable />;
      case 'fixed-assets':
        return <SmartFixedAssets />;
      case 'budgeting':
        return <SmartBudgeting />;
      case 'tax-management':
        return <SmartTaxManagement />;
      case 'bank-reconciliation':
        return <SmartBankReconciliation />;
      case 'financial-reports':
        return <SmartFinancialReports />;
      case 'audit-trail':
        return <SmartAuditTrail />;
      case 'daily-cycle':
        return <DailyCycleManager />;
      default:
        return <SmartDashboard />;
    }
  };

  return (
    <CoAProvider>
      <Box sx={{ width: '100%', height: '100%', p: 2 }}>
        {renderFeature()}
      </Box>
    </CoAProvider>
  );
};

export default FinanceModule;