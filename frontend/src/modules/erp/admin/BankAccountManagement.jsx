import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, 
  DialogContent, DialogActions, TextField, FormControl, InputLabel, Select, MenuItem, 
  Switch, FormControlLabel, Alert, Snackbar, LinearProgress, Tooltip
} from '@mui/material';
import {
  Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, AccountBalance as BankIcon,
  Visibility as ViewIcon, VisibilityOff as HideIcon, CheckCircle as ActiveIcon,
  Cancel as InactiveIcon, AttachMoney as MoneyIcon, Security as SecurityIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const BankAccountManagement = () => {
  // State management
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [formData, setFormData] = useState({
    account_name: '',
    account_number: '',
    bank_name: '',
    bank_code: '',
    account_type: 'checking',
    currency: 'USD',
    gl_account_id: '',
    is_default: false,
    allow_deposits: true,
    allow_withdrawals: true,
    daily_limit: '',
    monthly_limit: '',
    requires_approval: false
  });

  // Data hooks
  const { data: bankAccounts, loading: accountsLoading, refresh: refreshAccounts } = useRealTimeData('/api/finance/bank-accounts');
  const { data: glAccounts, loading: glLoading } = useRealTimeData('/api/finance/chart-of-accounts');

  // Filter GL accounts to show only asset accounts (typically 1xxx)
  const assetAccounts = glAccounts?.filter(account => 
    account.account_type === 'Asset' || account.account_code?.startsWith('1')
  ) || [];

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        daily_limit: formData.daily_limit ? parseFloat(formData.daily_limit) : null,
        monthly_limit: formData.monthly_limit ? parseFloat(formData.monthly_limit) : null,
        gl_account_id: formData.gl_account_id ? parseInt(formData.gl_account_id) : null
      };

      if (editMode && selectedAccount) {
        await apiClient.put(`/finance/bank-accounts/${selectedAccount.id}`, submitData);
        setSnackbar({ open: true, message: 'Bank account updated successfully!', severity: 'success' });
      } else {
        await apiClient.post('/finance/bank-accounts', submitData);
        setSnackbar({ open: true, message: 'Bank account created successfully!', severity: 'success' });
      }

      handleCloseDialog();
      refreshAccounts();
    } catch (error) {
      console.error('Error saving bank account:', error);
      setSnackbar({ 
        open: true, 
        message: error.response?.data?.error || 'Error saving bank account', 
        severity: 'error' 
      });
    }
  };

  // Handle edit
  const handleEdit = (account) => {
    setSelectedAccount(account);
    setFormData({
      account_name: account.account_name || '',
      account_number: account.account_number || '',
      bank_name: account.bank_name || '',
      bank_code: account.bank_code || '',
      account_type: account.account_type || 'checking',
      currency: account.currency || 'USD',
      gl_account_id: account.gl_account_id || '',
      is_default: account.is_default || false,
      allow_deposits: account.allow_deposits !== false,
      allow_withdrawals: account.allow_withdrawals !== false,
      daily_limit: account.daily_limit || '',
      monthly_limit: account.monthly_limit || '',
      requires_approval: account.requires_approval || false
    });
    setEditMode(true);
    setDialogOpen(true);
  };

  // Handle delete
  const handleDelete = async (account) => {
    if (window.confirm(`Are you sure you want to delete the bank account "${account.account_name}"?`)) {
      try {
        await apiClient.put(`/finance/bank-accounts/${account.id}`, { is_active: false });
        setSnackbar({ open: true, message: 'Bank account deactivated successfully!', severity: 'success' });
        refreshAccounts();
      } catch (error) {
        setSnackbar({ 
          open: true, 
          message: error.response?.data?.error || 'Error deactivating bank account', 
          severity: 'error' 
        });
      }
    }
  };

  // Handle close dialog
  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditMode(false);
    setSelectedAccount(null);
    setFormData({
      account_name: '',
      account_number: '',
      bank_name: '',
      bank_code: '',
      account_type: 'checking',
      currency: 'USD',
      gl_account_id: '',
      is_default: false,
      allow_deposits: true,
      allow_withdrawals: true,
      daily_limit: '',
      monthly_limit: '',
      requires_approval: false
    });
  };

  // Handle add new
  const handleAddNew = () => {
    setEditMode(false);
    setSelectedAccount(null);
    setDialogOpen(true);
  };

  // Seed default bank accounts
  const handleSeedDefaults = async () => {
    try {
      const defaultAccounts = [
        {
          account_name: 'Main Checking Account',
          account_type: 'checking',
          bank_name: 'First National Bank',
          currency: 'USD',
          is_default: true,
          allow_deposits: true,
          allow_withdrawals: true
        },
        {
          account_name: 'Merchant Account',
          account_type: 'merchant',
          bank_name: 'Payment Processor',
          currency: 'USD',
          allow_deposits: true,
          allow_withdrawals: false
        },
        {
          account_name: 'Savings Account',
          account_type: 'savings',
          bank_name: 'First National Bank',
          currency: 'USD',
          allow_deposits: true,
          allow_withdrawals: true
        }
      ];

      for (const account of defaultAccounts) {
        await apiClient.post('/finance/bank-accounts', account);
      }

      setSnackbar({ open: true, message: 'Default bank accounts created successfully!', severity: 'success' });
      refreshAccounts();
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: error.response?.data?.error || 'Error creating default accounts', 
        severity: 'error' 
      });
    }
  };

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h5" display="flex" alignItems="center" gap={1}>
              <BankIcon color="primary" />
              Bank Account Management
            </Typography>
            <Box display="flex" gap={1}>
              {(!bankAccounts || bankAccounts.length === 0) && (
                <Button
                  variant="outlined"
                  onClick={handleSeedDefaults}
                  disabled={accountsLoading}
                >
                  Create Default Accounts
                </Button>
              )}
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddNew}
              >
                Add Bank Account
              </Button>
            </Box>
          </Box>
        </Grid>

        {/* Bank Accounts Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Bank Accounts
              </Typography>
              
              {accountsLoading ? (
                <LinearProgress />
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Account Name</TableCell>
                        <TableCell>Bank</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Currency</TableCell>
                        <TableCell>Permissions</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {bankAccounts && bankAccounts.length > 0 ? (
                        bankAccounts.map((account) => (
                          <TableRow key={account.id}>
                            <TableCell>
                              <Box display="flex" alignItems="center" gap={1}>
                                <BankIcon fontSize="small" />
                                <Box>
                                  <Typography variant="body2" fontWeight="bold">
                                    {account.account_name}
                                  </Typography>
                                  {account.account_number && (
                                    <Typography variant="caption" color="text.secondary">
                                      ****{account.account_number.slice(-4)}
                                    </Typography>
                                  )}
                                </Box>
                                {account.is_default && (
                                  <Chip label="Default" size="small" color="primary" />
                                )}
                              </Box>
                            </TableCell>
                            <TableCell>{account.bank_name || 'N/A'}</TableCell>
                            <TableCell>
                              <Chip 
                                label={account.account_type} 
                                size="small" 
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell>{account.currency}</TableCell>
                            <TableCell>
                              <Box display="flex" gap={0.5}>
                                {account.allow_deposits && (
                                  <Chip label="Deposits" size="small" color="success" variant="outlined" />
                                )}
                                {account.allow_withdrawals && (
                                  <Chip label="Withdrawals" size="small" color="warning" variant="outlined" />
                                )}
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Chip 
                                icon={account.is_active !== false ? <ActiveIcon /> : <InactiveIcon />}
                                label={account.is_active !== false ? 'Active' : 'Inactive'}
                                color={account.is_active !== false ? 'success' : 'error'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              <Box display="flex" gap={1}>
                                <Tooltip title="Edit">
                                  <IconButton 
                                    size="small" 
                                    onClick={() => handleEdit(account)}
                                  >
                                    <EditIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                                <Tooltip title="Deactivate">
                                  <IconButton 
                                    size="small" 
                                    onClick={() => handleDelete(account)}
                                    color="error"
                                  >
                                    <DeleteIcon fontSize="small" />
                                  </IconButton>
                                </Tooltip>
                              </Box>
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell colSpan={7} align="center">
                            <Box py={4}>
                              <BankIcon fontSize="large" color="disabled" />
                              <Typography variant="body1" color="text.secondary">
                                No bank accounts found
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                Click "Add Bank Account" or "Create Default Accounts" to get started
                              </Typography>
                            </Box>
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add/Edit Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editMode ? 'Edit Bank Account' : 'Add Bank Account'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Account Name"
                  value={formData.account_name}
                  onChange={(e) => handleInputChange('account_name', e.target.value)}
                  fullWidth
                  required
                  placeholder="Main Checking Account"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Account Number"
                  value={formData.account_number}
                  onChange={(e) => handleInputChange('account_number', e.target.value)}
                  fullWidth
                  placeholder="Last 4 digits or masked"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Bank Name"
                  value={formData.bank_name}
                  onChange={(e) => handleInputChange('bank_name', e.target.value)}
                  fullWidth
                  placeholder="First National Bank"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Bank Code"
                  value={formData.bank_code}
                  onChange={(e) => handleInputChange('bank_code', e.target.value)}
                  fullWidth
                  placeholder="Routing number, SWIFT, etc."
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Account Type</InputLabel>
                  <Select
                    value={formData.account_type}
                    onChange={(e) => handleInputChange('account_type', e.target.value)}
                    label="Account Type"
                  >
                    <MenuItem value="checking">Checking</MenuItem>
                    <MenuItem value="savings">Savings</MenuItem>
                    <MenuItem value="merchant">Merchant Account</MenuItem>
                    <MenuItem value="credit_line">Credit Line</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Currency</InputLabel>
                  <Select
                    value={formData.currency}
                    onChange={(e) => handleInputChange('currency', e.target.value)}
                    label="Currency"
                  >
                    <MenuItem value="USD">USD - US Dollar</MenuItem>
                    <MenuItem value="EUR">EUR - Euro</MenuItem>
                    <MenuItem value="GBP">GBP - British Pound</MenuItem>
                    <MenuItem value="CAD">CAD - Canadian Dollar</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>GL Account</InputLabel>
                  <Select
                    value={formData.gl_account_id}
                    onChange={(e) => handleInputChange('gl_account_id', e.target.value)}
                    label="GL Account"
                    disabled={glLoading}
                  >
                    <MenuItem value="">
                      <em>Select GL Account</em>
                    </MenuItem>
                    {assetAccounts.map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.account_code} - {account.account_name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Daily Limit"
                  type="number"
                  value={formData.daily_limit}
                  onChange={(e) => handleInputChange('daily_limit', e.target.value)}
                  fullWidth
                  placeholder="Optional transaction limit"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Monthly Limit"
                  type="number"
                  value={formData.monthly_limit}
                  onChange={(e) => handleInputChange('monthly_limit', e.target.value)}
                  fullWidth
                  placeholder="Optional monthly limit"
                />
              </Grid>
              
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                  Account Settings
                </Typography>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.is_default}
                      onChange={(e) => handleInputChange('is_default', e.target.checked)}
                    />
                  }
                  label="Default Account"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.requires_approval}
                      onChange={(e) => handleInputChange('requires_approval', e.target.checked)}
                    />
                  }
                  label="Requires Approval"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.allow_deposits}
                      onChange={(e) => handleInputChange('allow_deposits', e.target.checked)}
                    />
                  }
                  label="Allow Deposits"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.allow_withdrawals}
                      onChange={(e) => handleInputChange('allow_withdrawals', e.target.checked)}
                    />
                  }
                  label="Allow Withdrawals"
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            {editMode ? 'Update' : 'Create'} Account
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default BankAccountManagement;
