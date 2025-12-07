import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, FormControl, InputLabel, Select, MenuItem, Alert, Snackbar, Chip, Avatar, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Tooltip,
  InputAdornment, FormHelperText, CircularProgress
} from '@mui/material';
import {
  Add, Delete, Save, Cancel, AttachMoney, AccountBalance, Receipt, Payment, Business, 
  TrendingUp, TrendingDown, CheckCircle, Warning, Error, Info, Close, Edit
} from '@mui/icons-material';
import apiClient from '../../../services/apiClient';

const ManualJournalEntry = ({ open, onClose, onSuccess, editEntry = null, showAccountCodes: propShowAccountCodes }) => {
  // Read preference from localStorage, with prop as override
  const showAccountCodes = propShowAccountCodes !== undefined 
    ? propShowAccountCodes 
    : (localStorage.getItem('coa_show_account_codes') === 'true');
  
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split('T')[0],
    reference: '',
    description: '',
    status: 'draft',
    payment_method: 'bank'
  });
  
  const [journalLines, setJournalLines] = useState([
    { id: 1, account_id: '', description: '', debit_amount: 0, credit_amount: 0 }
  ]);
  
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [validation, setValidation] = useState({ valid: false, errors: [] });
  const [quickAddOpen, setQuickAddOpen] = useState(false);
  const [quickAddForm, setQuickAddForm] = useState({ name: '', type: '', code: '' });
  
  // Reset quick add form when dialog opens/closes
  useEffect(() => {
    if (!quickAddOpen) {
      setQuickAddForm({ name: '', type: '', code: '' });
    }
  }, [quickAddOpen]);
  const [quickAddLoading, setQuickAddLoading] = useState(false);

  // Load accounts on component mount
  useEffect(() => {
    if (open) {
      loadAccounts();
      if (editEntry) {
        // Wait a bit for accounts to load before loading edit data
        setTimeout(() => {
          loadEditData();
        }, 100);
      } else {
        resetForm();
      }
    }
  }, [open, editEntry]);

  // Also load edit data when accounts are loaded
  useEffect(() => {
    if (open && editEntry && accounts.length > 0) {
      loadEditData();
    }
  }, [accounts, open, editEntry]);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      
      // Fetch all accounts from single source
      const response = await apiClient.get('/api/finance/double-entry/accounts');
      console.log('🔍 Accounts API response:', response);
      
      // Handle different response structures
      let accountsArray = [];
      if (Array.isArray(response)) {
        accountsArray = response;
      } else if (response && Array.isArray(response.data)) {
        accountsArray = response.data;
      } else if (response && response.data && Array.isArray(response.data)) {
        accountsArray = response.data;
      }
      
      console.log('🔍 Processed accounts array:', accountsArray);
      console.log('🔍 Accounts count:', accountsArray.length);
      
      // If no accounts exist, auto-create the 25 default accounts
      if (accountsArray.length === 0) {
        console.log('📊 No accounts found - creating 25 default accounts...');
        try {
          const createResponse = await apiClient.post('/api/finance/double-entry/accounts/default/create', {});
          console.log('✅ Default accounts created:', createResponse);
          
          if (createResponse.new_count > 0) {
            // Reload accounts after creation
            const reloadResponse = await apiClient.get('/api/finance/double-entry/accounts');
            const reloadedAccounts = Array.isArray(reloadResponse) ? reloadResponse : [];
            setAccounts(reloadedAccounts);
            
            setSnackbar({
              open: true,
              message: `Created ${createResponse.new_count} default accounts. You can now select an account.`,
              severity: 'success'
            });
            return;
          }
        } catch (createError) {
          console.error('❌ Error creating default accounts:', createError);
          setSnackbar({
            open: true,
            message: 'Failed to create default accounts. Please try again.',
            severity: 'error'
          });
        }
      }
      
      if (accountsArray.length > 0) {
        // Filter out inactive accounts for transaction use
        const activeAccounts = accountsArray.filter(acc => acc.is_active !== false);
        setAccounts(activeAccounts);
        console.log('✅ Accounts loaded successfully:', activeAccounts.length, 'active accounts out of', accountsArray.length, 'total');
      } else {
        console.warn('⚠️ No accounts found in response');
        setSnackbar({
          open: true,
          message: 'No accounts found. Please create accounts in Chart of Accounts.',
          severity: 'warning'
        });
      }
    } catch (error) {
      console.error('❌ Error loading accounts:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load chart of accounts: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  };

  const loadEditData = () => {
    if (editEntry) {
      console.log('🔍 Loading edit data for entry:', editEntry);
      console.log('🔍 Available accounts:', accounts);
      console.log('🔍 Edit mode activated - form will be pre-filled');
      
      setFormData({
        date: editEntry.entry_date ? editEntry.entry_date.split('T')[0] : 
              editEntry.date ? editEntry.date.split('T')[0] : 
              new Date().toISOString().split('T')[0],
        reference: editEntry.reference || '',
        description: editEntry.description || '',
        status: editEntry.status || 'draft',
        payment_method: editEntry.payment_method || 'bank'
      });
      
      // Handle different entry structures
      if (editEntry.lines && editEntry.lines.length > 0) {
        // New structure with lines array
        const lines = editEntry.lines.map((line, index) => ({
          id: index + 1,
          account_id: parseInt(line.account_id) || line.account_id, // Ensure it's a number
          description: line.description || '',
          debit_amount: line.debit_amount || 0,
          credit_amount: line.credit_amount || 0
        }));
        console.log('🔍 Processed lines for editing:', lines);
        setJournalLines(lines);
      } else if (editEntry.debit_amount !== undefined || editEntry.credit_amount !== undefined) {
        // General Ledger structure - create a single line
        const lines = [{
          id: 1,
          account_id: parseInt(editEntry.account_id) || editEntry.account_id || '', // Ensure it's a number
          description: editEntry.description || '',
          debit_amount: editEntry.debit_amount || 0,
          credit_amount: editEntry.credit_amount || 0
        }];
        console.log('🔍 Processed single line for editing:', lines);
        setJournalLines(lines);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      date: new Date().toISOString().split('T')[0],
      reference: '',
      description: '',
      status: 'draft',
      payment_method: 'bank'
    });
    setJournalLines([
      { id: 1, account_id: '', description: '', debit_amount: 0, credit_amount: 0 }
    ]);
    setValidation({ valid: false, errors: [] });
  };

  const addJournalLine = () => {
    const newId = Math.max(...journalLines.map(line => line.id)) + 1;
    setJournalLines([...journalLines, {
      id: newId,
      account_id: '',
      description: '',
      debit_amount: 0,
      credit_amount: 0
    }]);
  };

  const removeJournalLine = (id) => {
    if (journalLines.length > 1) {
      setJournalLines(journalLines.filter(line => line.id !== id));
    }
  };

  const updateJournalLine = (id, field, value) => {
    setJournalLines(journalLines.map(line => {
      if (line.id === id) {
        const updatedLine = { ...line, [field]: value };
        
        // Ensure only one of debit or credit has a value
        if (field === 'debit_amount' && value > 0) {
          updatedLine.credit_amount = 0;
        } else if (field === 'credit_amount' && value > 0) {
          updatedLine.debit_amount = 0;
        }
        
        return updatedLine;
      }
      return line;
    }));
    
    validateJournalEntry();
  };

  const validateJournalEntry = () => {
    console.log('🔍 Validating journal entry...');
    console.log('🔍 Current journal lines:', journalLines);
    
    const errors = [];
    
    // For business-friendly mode, we only need basic validation
    // The system will auto-balance the entries
    
    // Check if we have at least one line with an account and amount
    const validLines = journalLines.filter(line => 
      line.account_id && ((line.debit_amount || 0) > 0 || (line.credit_amount || 0) > 0)
    );
    
    console.log('🔍 Valid lines found:', validLines);
    
    if (validLines.length === 0) {
      errors.push('Please select an account and enter an amount');
      console.log('❌ No valid lines found');
    } else {
      console.log('✅ Valid lines found:', validLines.length);
      
      // Validate that all selected accounts are active
      const inactiveAccounts = [];
      validLines.forEach(line => {
        const account = accounts.find(acc => acc.id === line.account_id);
        if (account && account.is_active === false) {
          inactiveAccounts.push({
            code: account.code || 'N/A',
            name: account.name
          });
        }
      });
      
      if (inactiveAccounts.length > 0) {
        const accountList = inactiveAccounts.map(acc => `${acc.code} (${acc.name})`).join(', ');
        errors.push(`Cannot use inactive accounts: ${accountList}. Please select active accounts only.`);
        console.log('❌ Inactive accounts detected:', inactiveAccounts);
      }
    }
    
    // Calculate totals for display
    const totalDebits = journalLines.reduce((sum, line) => sum + (line.debit_amount || 0), 0);
    const totalCredits = journalLines.reduce((sum, line) => sum + (line.credit_amount || 0), 0);
    
    setValidation({
      valid: errors.length === 0,
      errors,
      totalDebits,
      totalCredits
    });
  };

  const handleSubmit = async () => {
    console.log('🔍 Submit button clicked!');
    console.log('🔍 Validation state:', validation);
    console.log('🔍 Journal lines:', journalLines);
    console.log('🔍 Form data:', formData);
    
    if (!validation.valid) {
      console.log('❌ Validation failed:', validation.errors);
      setSnackbar({
        open: true,
        message: 'Please fix validation errors before submitting',
        severity: 'error'
      });
      return;
    }
    
    console.log('✅ Validation passed, proceeding with submission...');

    setLoading(true);
    try {
      // For business-friendly mode, we'll use the transaction templates API
      // to automatically create balanced journal entries
      
      // Get the first valid line (business transaction)
      const validLine = journalLines.find(line => 
        line.account_id && ((line.debit_amount || 0) > 0 || (line.credit_amount || 0) > 0)
      );
      
      console.log('🔍 All journal lines:', journalLines);
      console.log('🔍 Valid line found:', validLine);
      
      if (!validLine) {
        throw new Error('No valid transaction found');
      }
      
      // Determine transaction type based on account and amount
      const amount = validLine.debit_amount || validLine.credit_amount;
      const isDebit = validLine.debit_amount > 0;
      
      console.log('🔍 Transaction details:', {
        amount,
        isDebit,
        account_id: validLine.account_id,
        description: validLine.description
      });
      
      // Prepare data for the backend API (matching backend expectations)
      const transactionData = {
        entry_date: formData.date,
        reference: formData.reference || `JE-${Date.now()}`,
        description: formData.description || validLine.description,
        account_id: parseInt(validLine.account_id), // Ensure account_id is an integer
        debit_amount: isDebit ? amount : 0,
        credit_amount: isDebit ? 0 : amount,
        status: formData.status || 'posted',
        journal_type: 'manual'
      };

      console.log('🔍 Frontend sending transaction data:', transactionData);
      console.log('🔍 Data types:', {
        debit_amount: typeof transactionData.debit_amount,
        credit_amount: typeof transactionData.credit_amount,
        description: typeof transactionData.description,
        account_id: typeof transactionData.account_id
      });

      let response;
      if (editEntry) {
        // Extract the actual entry ID from composite ID (format: "entryId-lineId")
        // Convert to string first to handle both number and string IDs
        const entryIdStr = String(editEntry.id);
        const entryId = entryIdStr.includes('-') ? entryIdStr.split('-')[0] : entryIdStr;
        console.log('✏️ Updating existing entry ID:', entryId);
        console.log('✏️ Original editEntry.id:', editEntry.id, 'type:', typeof editEntry.id);
        console.log('✏️ Processed entryId:', entryId, 'type:', typeof entryId);
        console.log('✏️ Update data:', transactionData);
        response = await apiClient.put(`/api/finance/advanced/general-ledger/${entryId}`, transactionData);
      } else {
        // Use the advanced general ledger API for creating entries
        console.log('🆕 Creating new entry...');
        response = await apiClient.post('/api/finance/advanced/general-ledger', transactionData);
      }

      if (response.success || response.id) {
        setSnackbar({
          open: true,
          message: editEntry ? 'Journal entry updated successfully!' : 'Journal entry created successfully!',
          severity: 'success'
        });
        onSuccess && onSuccess(response);
        handleClose();
      } else {
        setSnackbar({
          open: true,
          message: response.error || 'Failed to save journal entry',
          severity: 'error'
        });
      }
    } catch (error) {
      console.error('Error saving journal entry:', error);
      setSnackbar({
        open: true,
        message: 'Failed to save journal entry',
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  const getAccountName = (accountId) => {
    const account = accounts.find(acc => acc.id === accountId);
    return account ? account.name : '';
  };

  const handleQuickAdd = async () => {
    if (!quickAddForm.name || !quickAddForm.type) {
      setSnackbar({
        open: true,
        message: 'Please fill in account name and type',
        severity: 'error'
      });
      return;
    }

    setQuickAddLoading(true);
    try {
      const response = await apiClient.post('/api/finance/double-entry/accounts', {
        name: quickAddForm.name,
        type: quickAddForm.type,
        code: quickAddForm.code || undefined // Let backend auto-generate if empty
      });

      if (response.id) {
        // Reload accounts to include the new one
        await loadAccounts();
        
        // Auto-select the newly created account in the current line
        const currentLine = journalLines[journalLines.length - 1];
        if (currentLine && !currentLine.account_id) {
          updateJournalLine(currentLine.id, 'account_id', response.id);
        }

        setSnackbar({
          open: true,
          message: `Account "${response.name}" created successfully!`,
          severity: 'success'
        });
        
        setQuickAddOpen(false);
        setQuickAddForm({ name: '', type: '', code: '' });
      }
    } catch (error) {
      console.error('Error creating account:', error);
      setSnackbar({
        open: true,
        message: error.message || 'Failed to create account',
        severity: 'error'
      });
    } finally {
      setQuickAddLoading(false);
    }
  };

  return (
    <>
      <Dialog 
        open={open} 
        onClose={handleClose}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h5">
              {editEntry ? 'Edit Manual Journal Entry' : 'Create Manual Journal Entry'}
            </Typography>
            <IconButton onClick={handleClose}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {/* Header Information */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Entry Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Date"
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    label="Reference"
                    value={formData.reference}
                    onChange={(e) => setFormData({ ...formData, reference: e.target.value })}
                    fullWidth
                    placeholder="Auto-generated if empty"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    label="Description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    fullWidth
                    multiline
                    rows={2}
                    required
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                      label="Status"
                    >
                      <MenuItem value="draft">Draft</MenuItem>
                      <MenuItem value="posted">Posted</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth>
                    <InputLabel>Payment Method</InputLabel>
                    <Select
                      value={formData.payment_method}
                      onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                      label="Payment Method"
                    >
                      <MenuItem value="cash">💵 Cash</MenuItem>
                      <MenuItem value="bank">🏦 Bank Transfer</MenuItem>
                      <MenuItem value="wire">🌐 Wire Transfer</MenuItem>
                      <MenuItem value="credit_card">💳 Credit Card</MenuItem>
                      <MenuItem value="check">📝 Check</MenuItem>
                      <MenuItem value="digital">📱 Digital Payment</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Journal Lines */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Journal Lines
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={addJournalLine}
                >
                  Add Line
                </Button>
              </Box>

              <TableContainer component={Paper}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Account</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell align="right">Debit</TableCell>
                      <TableCell align="right">Credit</TableCell>
                      <TableCell width="60">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {journalLines.map((line) => (
                      <TableRow key={line.id}>
                        <TableCell>
                          <FormControl fullWidth size="small">
                            {loading ? (
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1 }}>
                                <CircularProgress size={16} />
                                <Typography variant="body2" color="text.secondary">
                                  Loading accounts...
                                </Typography>
                              </Box>
                            ) : (
                              <Select
                                value={line.account_id || ''}
                                onChange={(e) => updateJournalLine(line.id, 'account_id', e.target.value)}
                                displayEmpty
                                disabled={accounts.length === 0}
                              >
                                <MenuItem value="" disabled>
                                  {accounts.length === 0 ? 'No active accounts available' : 'Select Account'}
                                </MenuItem>
                                {accounts
                                  .filter(account => account.is_active !== false)
                                  .map((account) => (
                                  <MenuItem key={account.id} value={account.id}>
                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                                      {showAccountCodes && account.code && (
                                        <Typography 
                                          variant="caption" 
                                          sx={{ 
                                            fontFamily: 'monospace',
                                            color: 'text.secondary',
                                            mr: 0.5
                                          }}
                                        >
                                          {account.code}
                                        </Typography>
                                      )}
                                      <Typography component="span" sx={{ flexGrow: 1 }}>
                                        {account.name}
                                      </Typography>
                                      {account.is_core && (
                                        <Chip 
                                          label="Core" 
                                          size="small" 
                                          sx={{ height: 18, fontSize: '0.65rem' }}
                                          color="primary"
                                          variant="filled"
                                        />
                                      )}
                                      {account.is_default && !account.is_core && (
                                        <Chip 
                                          label="Default" 
                                          size="small" 
                                          sx={{ height: 18, fontSize: '0.65rem' }}
                                          color="primary"
                                          variant="outlined"
                                        />
                                      )}
                                    </Box>
                                  </MenuItem>
                                ))}
                                <Divider />
                                <MenuItem 
                                  value="__create_new__"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setQuickAddOpen(true);
                                  }}
                                  sx={{ fontStyle: 'italic', color: 'primary.main' }}
                                >
                                  <Add sx={{ mr: 1, fontSize: 18 }} />
                                  Create New Account...
                                </MenuItem>
                              </Select>
                            )}
                          </FormControl>
                        </TableCell>
                        <TableCell>
                          <TextField
                            value={line.description}
                            onChange={(e) => updateJournalLine(line.id, 'description', e.target.value)}
                            size="small"
                            fullWidth
                            placeholder="Line description"
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            type="number"
                            value={line.debit_amount || ''}
                            onChange={(e) => updateJournalLine(line.id, 'debit_amount', parseFloat(e.target.value) || 0)}
                            size="small"
                            fullWidth
                            InputProps={{
                              startAdornment: <InputAdornment position="start">$</InputAdornment>,
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <TextField
                            type="number"
                            value={line.credit_amount || ''}
                            onChange={(e) => updateJournalLine(line.id, 'credit_amount', parseFloat(e.target.value) || 0)}
                            size="small"
                            fullWidth
                            InputProps={{
                              startAdornment: <InputAdornment position="start">$</InputAdornment>,
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Tooltip title="Remove Line">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => removeJournalLine(line.id)}
                              disabled={journalLines.length <= 1}
                            >
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>

          {/* Validation Summary */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Validation Summary
              </Typography>
              
              {validation.errors.length > 0 ? (
                <Alert severity="error" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Please fix the following errors:
                  </Typography>
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    {validation.errors.map((error, index) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </Alert>
              ) : (
                <Alert severity="success" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">
                    ✅ Ready to create journal entry - system will auto-balance
                  </Typography>
                </Alert>
              )}
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h6" color="success.main">
                      Total Debits: ${validation.totalDebits?.toFixed(2) || '0.00'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h6" color="error.main">
                      Total Credits: ${validation.totalCredits?.toFixed(2) || '0.00'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
              
              {validation.totalDebits && validation.totalCredits && (
                <Box textAlign="center" mt={2}>
                  <Chip
                    label="🤖 Auto-Balanced by System"
                    color="info"
                    variant="filled"
                  />
                </Box>
              )}
            </CardContent>
          </Card>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={!validation.valid || loading}
            startIcon={loading ? <CircularProgress size={20} /> : <Save />}
          >
            {loading ? 'Saving...' : (editEntry ? 'Update Entry' : 'Create Entry')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Quick Add Account Dialog */}
      <Dialog open={quickAddOpen} onClose={() => setQuickAddOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Account</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Account Name *"
              value={quickAddForm.name}
              onChange={(e) => setQuickAddForm({ ...quickAddForm, name: e.target.value })}
              fullWidth
              required
            />
            <FormControl fullWidth required>
              <InputLabel>Account Type *</InputLabel>
              <Select
                value={quickAddForm.type}
                onChange={(e) => {
                  setQuickAddForm({ ...quickAddForm, type: e.target.value });
                  // Auto-suggest code based on type
                  if (!quickAddForm.code) {
                    const typePrefixes = {
                      'asset': '1',
                      'liability': '2',
                      'equity': '3',
                      'revenue': '4',
                      'expense': '5'
                    };
                    const prefix = typePrefixes[e.target.value] || '9';
                    // Find next available code for this type
                    const existingCodes = accounts
                      .filter(acc => acc.code && acc.code.startsWith(prefix))
                      .map(acc => parseInt(acc.code))
                      .filter(code => !isNaN(code));
                    const maxCode = existingCodes.length > 0 ? Math.max(...existingCodes) : parseInt(`${prefix}000`);
                    const suggestedCode = String(maxCode + 10);
                    setQuickAddForm({ ...quickAddForm, type: e.target.value, code: suggestedCode });
                  }
                }}
                label="Account Type *"
              >
                <MenuItem value="asset">Asset</MenuItem>
                <MenuItem value="liability">Liability</MenuItem>
                <MenuItem value="equity">Equity</MenuItem>
                <MenuItem value="revenue">Revenue</MenuItem>
                <MenuItem value="expense">Expense</MenuItem>
              </Select>
            </FormControl>
            {showAccountCodes && (
              <TextField
                label="Account Code"
                value={quickAddForm.code}
                onChange={(e) => setQuickAddForm({ ...quickAddForm, code: e.target.value })}
                fullWidth
                helperText="Optional - leave blank for auto-generation"
                sx={{ fontFamily: 'monospace' }}
              />
            )}
            <Alert severity="info" sx={{ mt: 1 }}>
              You can edit this account later in Chart of Accounts for more details.
            </Alert>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setQuickAddOpen(false);
            setQuickAddForm({ name: '', type: '', code: '' });
          }}>
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleQuickAdd}
            disabled={!quickAddForm.name || !quickAddForm.type || quickAddLoading}
            startIcon={quickAddLoading ? <CircularProgress size={20} /> : <Add />}
          >
            {quickAddLoading ? 'Creating...' : 'Create Account'}
          </Button>
        </DialogActions>
      </Dialog>

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
    </>
  );
};

export default ManualJournalEntry;
