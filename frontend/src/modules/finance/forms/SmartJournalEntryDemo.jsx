import React, { useState } from 'react';
import {
  Box, Typography, Paper, Grid, Card, CardContent, Button, Alert,
  TextField, MenuItem, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow
} from '@mui/material';
import { useCoA } from '../context/CoAContext';

const SmartJournalEntryDemo = () => {
  const { accounts } = useCoA();
  const [selectedAccountId, setSelectedAccountId] = useState('');
  const [debitAmount, setDebitAmount] = useState('');
  const [creditAmount, setCreditAmount] = useState('');

  // Smart account behavior logic (same as in JournalEntryForm)
  const getAccountBehavior = (accountType) => {
    switch(accountType?.toLowerCase()) {
      case 'asset':
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Increase Asset',
          creditLabel: 'Decrease Asset',
          normalSide: 'debit',
          helpText: 'Assets increase with debits, decrease with credits',
          color: '#1976d2',
          icon: '💰'
        };
      case 'liability':
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Pay/Reduce Liability',
          creditLabel: 'Incur/Increase Liability',
          normalSide: 'credit',
          helpText: 'Liabilities increase with credits, decrease with debits',
          color: '#d32f2f',
          icon: '💳'
        };
      case 'revenue':
        return {
          debitEnabled: false,
          creditEnabled: true,
          debitLabel: 'Refund/Reversal',
          creditLabel: 'Revenue Earned',
          normalSide: 'credit',
          helpText: '💡 Revenue accounts normally have credit balances (money earned)',
          color: '#388e3c',
          icon: '💵'
        };
      case 'expense':
        return {
          debitEnabled: true,
          creditEnabled: false,
          debitLabel: 'Expense Incurred',
          creditLabel: 'Expense Reversal',
          normalSide: 'debit',
          helpText: '💡 Expense accounts normally have debit balances (money spent)',
          color: '#f57c00',
          icon: '💸'
        };
      default:
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Debit',
          creditLabel: 'Credit',
          normalSide: 'debit',
          helpText: 'Select an account to see smart field behavior',
          color: '#757575',
          icon: '❓'
        };
    }
  };

  const selectedAccount = accounts.find(acc => acc.id == selectedAccountId);
  const behavior = selectedAccount ? getAccountBehavior(selectedAccount.category || selectedAccount.account_type || selectedAccount.type) : getAccountBehavior(null);

  const handleAccountChange = (accountId) => {
    setSelectedAccountId(accountId);
    // Clear amounts when account changes
    setDebitAmount('');
    setCreditAmount('');
  };

  const handleDebitChange = (value) => {
    if (behavior.debitEnabled) {
      setDebitAmount(value);
      if (value) setCreditAmount(''); // Clear opposite field
    }
  };

  const handleCreditChange = (value) => {
    if (behavior.creditEnabled) {
      setCreditAmount(value);
      if (value) setDebitAmount(''); // Clear opposite field
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        🧠 Smart Journal Entry Demo
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
          Test the Smart Field Behavior
        </Typography>
        <Typography variant="body2">
          Select different account types and watch how the debit/credit fields automatically enable/disable:
        </Typography>
        <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Chip label="💰 Assets: Both enabled" size="small" color="primary" />
          <Chip label="💵 Revenue: Credit only" size="small" color="success" />
          <Chip label="💸 Expenses: Debit only" size="small" color="warning" />
          <Chip label="💳 Liabilities: Both enabled" size="small" color="error" />
        </Box>
      </Alert>

      <Grid container spacing={3}>
        {/* Demo Form */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Demo Journal Line
            </Typography>

            {/* Account Selection */}
            <TextField
              select
              label="Select Account"
              value={selectedAccountId}
              onChange={(e) => handleAccountChange(e.target.value)}
              fullWidth
              sx={{ mb: 2 }}
            >
              <MenuItem value="">-- Select Account --</MenuItem>
              {accounts.map((account) => (
                <MenuItem key={account.id} value={account.id}>
                  {account.name} ({account.category || account.account_type || account.type})
                </MenuItem>
              ))}
            </TextField>

            {/* Debit Field */}
            <TextField
              type="number"
              label={behavior.debitLabel}
              value={debitAmount}
              onChange={(e) => handleDebitChange(e.target.value)}
              placeholder={behavior.debitEnabled ? behavior.debitPlaceholder : 'Disabled'}
              disabled={!behavior.debitEnabled}
              fullWidth
              sx={{ 
                mb: 2,
                '& .MuiInputBase-input.Mui-disabled': {
                  backgroundColor: '#f5f5f5',
                  color: '#999',
                  WebkitTextFillColor: '#999'
                },
                '& .MuiInputLabel-root.Mui-disabled': {
                  color: '#999'
                }
              }}
              InputProps={{
                startAdornment: (
                  <Typography sx={{ mr: 1, color: behavior.debitEnabled ? behavior.color : '#999' }}>
                    {behavior.icon} $
                  </Typography>
                ),
                endAdornment: !behavior.debitEnabled && (
                  <Typography sx={{ color: '#999', fontSize: '0.75rem' }}>🚫 DISABLED</Typography>
                )
              }}
            />

            {/* Credit Field */}
            <TextField
              type="number"
              label={behavior.creditLabel}
              value={creditAmount}
              onChange={(e) => handleCreditChange(e.target.value)}
              placeholder={behavior.creditEnabled ? behavior.creditPlaceholder : 'Disabled'}
              disabled={!behavior.creditEnabled}
              fullWidth
              sx={{ 
                '& .MuiInputBase-input.Mui-disabled': {
                  backgroundColor: '#f5f5f5',
                  color: '#999',
                  WebkitTextFillColor: '#999'
                },
                '& .MuiInputLabel-root.Mui-disabled': {
                  color: '#999'
                }
              }}
              InputProps={{
                startAdornment: (
                  <Typography sx={{ mr: 1, color: behavior.creditEnabled ? behavior.color : '#999' }}>
                    {behavior.icon} $
                  </Typography>
                ),
                endAdornment: !behavior.creditEnabled && (
                  <Typography sx={{ color: '#999', fontSize: '0.75rem' }}>🚫 DISABLED</Typography>
                )
              }}
            />
          </Paper>
        </Grid>

        {/* Behavior Explanation */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Current Behavior
            </Typography>

            {selectedAccount ? (
              <Box>
                <Typography variant="body1" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  {behavior.icon} <strong>{selectedAccount.name}</strong>
                  <Chip 
                    label={selectedAccount.category || selectedAccount.account_type || selectedAccount.type} 
                    size="small" 
                    sx={{ backgroundColor: behavior.color, color: 'white' }}
                  />
                </Typography>

                <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
                  {behavior.helpText}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip 
                    label={`Debit: ${behavior.debitEnabled ? 'ENABLED' : 'DISABLED'}`}
                    color={behavior.debitEnabled ? 'primary' : 'default'}
                    variant={behavior.normalSide === 'debit' ? 'filled' : 'outlined'}
                  />
                  <Chip 
                    label={`Credit: ${behavior.creditEnabled ? 'ENABLED' : 'DISABLED'}`}
                    color={behavior.creditEnabled ? 'primary' : 'default'}
                    variant={behavior.normalSide === 'credit' ? 'filled' : 'outlined'}
                  />
                </Box>

                {/* Current Values */}
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  Current Entry:
                </Typography>
                <Typography variant="body2">
                  Debit: ${debitAmount || '0.00'} | Credit: ${creditAmount || '0.00'}
                </Typography>
                
                {(debitAmount || creditAmount) && (
                  <Alert severity={debitAmount && creditAmount ? 'error' : 'success'} sx={{ mt: 1 }}>
                    {debitAmount && creditAmount ? 
                      '❌ Both fields have values - this should not be possible!' :
                      '✅ Only one field has a value - correct!'
                    }
                  </Alert>
                )}
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Select an account to see smart field behavior
              </Typography>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Account Types Reference */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          📚 Account Types Reference
        </Typography>
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Account Type</TableCell>
                <TableCell>Normal Balance</TableCell>
                <TableCell>Debit Means</TableCell>
                <TableCell>Credit Means</TableCell>
                <TableCell>Smart Behavior</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell>💰 Asset</TableCell>
                <TableCell>Debit</TableCell>
                <TableCell>Increase (money in)</TableCell>
                <TableCell>Decrease (money out)</TableCell>
                <TableCell>Both enabled</TableCell>
              </TableRow>
              <TableRow>
                <TableCell>💳 Liability</TableCell>
                <TableCell>Credit</TableCell>
                <TableCell>Decrease (pay debt)</TableCell>
                <TableCell>Increase (owe more)</TableCell>
                <TableCell>Both enabled</TableCell>
              </TableRow>
              <TableRow sx={{ bgcolor: '#f8f9fa' }}>
                <TableCell>💵 Revenue</TableCell>
                <TableCell>Credit</TableCell>
                <TableCell>Refund/Reversal</TableCell>
                <TableCell>Money earned</TableCell>
                <TableCell><strong>Credit only</strong></TableCell>
              </TableRow>
              <TableRow sx={{ bgcolor: '#f8f9fa' }}>
                <TableCell>💸 Expense</TableCell>
                <TableCell>Debit</TableCell>
                <TableCell>Money spent</TableCell>
                <TableCell>Expense reversal</TableCell>
                <TableCell><strong>Debit only</strong></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
};

export default SmartJournalEntryDemo;

