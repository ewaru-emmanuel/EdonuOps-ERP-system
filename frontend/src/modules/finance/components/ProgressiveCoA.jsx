import React, { useMemo } from 'react';
import {
  Box,
  Typography,
  Chip
} from '@mui/material';

const ProgressiveCoA = ({ accounts, onAccountSelect, onModeChange, showAccountCodes = false }) => {

  // Format amount helper
  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount || 0);
  };

  // Show all accounts (no filtering - user starts with 25 defaults, then adds/removes as needed)
  const filteredAccounts = useMemo(() => {
    if (!accounts || accounts.length === 0) return [];
    return accounts; // Always show all accounts
  }, [accounts]);

  // Group accounts by type with proper type detection
  const groupedAccounts = useMemo(() => {
    const groups = {
      asset: [],
      liability: [],
      equity: [],
      revenue: [],
      expense: [],
      other: [] // Catch-all for accounts that don't match any category
    };

    filteredAccounts.forEach(account => {
      // Try multiple ways to get account type
      const accountType = (account.account_type || account.type || '').toLowerCase();
      
      if (accountType === 'asset' || accountType === 'assets') {
        groups.asset.push(account);
      } else if (accountType === 'liability' || accountType === 'liabilities') {
        groups.liability.push(account);
      } else if (accountType === 'equity') {
        groups.equity.push(account);
      } else if (accountType === 'revenue' || accountType === 'income') {
        groups.revenue.push(account);
      } else if (accountType === 'expense' || accountType === 'expenses') {
        groups.expense.push(account);
      } else {
        // Account doesn't match any known type - add to "other" category so it's still shown
        console.warn(`Account ${account.code || account.id} has unknown type: "${accountType || 'missing'}" - adding to "other" category`);
        groups.other.push(account);
      }
    });

    return groups;
  }, [filteredAccounts]);

  // Account type configuration
  const accountTypeConfig = {
    asset: { color: '#4caf50' },
    liability: { color: '#f44336' },
    equity: { color: '#2196f3' },
    revenue: { color: '#9c27b0' },
    expense: { color: '#ff9800' },
    other: { color: '#9e9e9e' } // Gray for unknown types
  };

  const renderAccountItem = (account) => {
    const accountName = account.account_name || account.name || 'Unnamed Account';
    const accountType = (account.account_type || account.type || '').toLowerCase();
    const balance = account.balance || 0;
    const isActive = account.is_active !== false;
    const config = accountTypeConfig[accountType];

    return (
      <Box
        key={account.id}
        onClick={() => onAccountSelect?.(account)}
        sx={{
          display: 'flex',
          alignItems: 'center',
          py: 1.5,
          px: 2,
          borderLeft: `3px solid ${config?.color || '#ccc'}`,
          cursor: 'pointer',
          '&:hover': {
            backgroundColor: accountType === 'asset' ? 'rgba(46, 125, 50, 0.04)' :
                           accountType === 'liability' ? 'rgba(198, 40, 40, 0.04)' :
                           accountType === 'equity' ? 'rgba(21, 101, 192, 0.04)' :
                           accountType === 'revenue' ? 'rgba(123, 31, 162, 0.04)' :
                           'rgba(230, 81, 0, 0.04)',
            transform: 'translateX(2px)'
          },
          transition: 'all 0.2s ease',
          opacity: isActive ? 1 : 0.6
        }}
      >
        {showAccountCodes && account.code && (
          <Typography 
            variant="body2" 
            sx={{ 
              fontFamily: 'monospace',
              fontWeight: 500,
              color: 'text.secondary',
              minWidth: 80,
              mr: 2
            }}
          >
            {account.code}
          </Typography>
        )}
        <Typography 
          variant="body2" 
          sx={{ 
            flexGrow: 1,
            fontWeight: 'medium',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}
        >
          {accountName}
        </Typography>
        <Chip 
          label={accountType} 
          size="small"
          sx={{
            minWidth: 80,
            bgcolor: 
              accountType === 'asset' ? '#e8f5e9' :
              accountType === 'liability' ? '#ffebee' :
              accountType === 'equity' ? '#e3f2fd' :
              accountType === 'revenue' ? '#f3e5f5' :
              '#fff3e0',
            color:
              accountType === 'asset' ? '#2e7d32' :
              accountType === 'liability' ? '#c62828' :
              accountType === 'equity' ? '#1565c0' :
              accountType === 'revenue' ? '#7b1fa2' :
              '#e65100',
            fontWeight: 600,
            border: 'none',
            mr: 2
          }}
        />
        <Typography 
          variant="body2" 
          color={balance >= 0 ? 'text.primary' : 'error.main'}
          fontWeight="medium"
          sx={{ minWidth: 100, textAlign: 'right', mr: 2 }}
        >
          {formatAmount(balance)}
        </Typography>
        <Chip
          label={isActive ? 'Active' : 'Inactive'}
          size="small"
          color={isActive ? 'success' : 'error'}
          variant="outlined"
          sx={{ height: 24, fontSize: '0.7rem', minWidth: 70 }}
        />
      </Box>
    );
  };

  // Show loading state
  if (!accounts) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Loading Chart of Accounts...
        </Typography>
      </Box>
    );
  }

  // Show empty state
  if (accounts.length === 0) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No accounts found
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Start by adding your first account or importing from a template.
        </Typography>
      </Box>
    );
  }

  const totalAccounts = filteredAccounts.length;

  // Calculate totals for display
  const totalGrouped = Object.values(groupedAccounts).reduce((sum, arr) => sum + arr.length, 0);
  const missingAccounts = filteredAccounts.length - totalGrouped;

  return (
    <Box>
      {filteredAccounts.length === 0 ? (
        <Box sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No accounts found
          </Typography>
        </Box>
      ) : (
        <Box>
          {/* Summary header */}
          <Box sx={{ px: 2, py: 1.5, bgcolor: 'grey.50', borderBottom: '1px solid', borderColor: 'divider' }}>
            <Typography variant="subtitle2" color="text.secondary">
              Showing {filteredAccounts.length} account{filteredAccounts.length !== 1 ? 's' : ''}
              {missingAccounts > 0 && (
                <Typography component="span" variant="caption" color="warning.main" sx={{ ml: 1 }}>
                  (Warning: {missingAccounts} account{missingAccounts !== 1 ? 's' : ''} could not be categorized)
                </Typography>
              )}
            </Typography>
          </Box>
          
          {Object.entries(groupedAccounts)
            .filter(([category, accounts]) => accounts.length > 0)
            .map(([category, accounts]) => (
              <Box key={category}>
                <Typography 
                  variant="overline" 
                  sx={{ 
                    px: 2, 
                    py: 1, 
                    display: 'block', 
                    fontWeight: 600,
                    color: accountTypeConfig[category]?.color || '#666',
                    textTransform: 'uppercase',
                    borderBottom: `2px solid ${accountTypeConfig[category]?.color || '#ccc'}`,
                    bgcolor: 'grey.50'
                  }}
                >
                  {category === 'other' ? 'Other / Unclassified' : category} ({accounts.length})
                </Typography>
                {accounts
                  .sort((a, b) => (a.code || '').localeCompare(b.code || ''))
                  .map(renderAccountItem)}
              </Box>
            ))}
        </Box>
      )}
    </Box>
  );
};

export default ProgressiveCoA;
