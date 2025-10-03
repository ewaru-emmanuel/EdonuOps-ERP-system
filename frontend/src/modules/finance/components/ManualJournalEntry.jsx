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

const ManualJournalEntry = ({ open, onClose, onSuccess, editEntry = null }) => {
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

  // Load accounts on component mount
  useEffect(() => {
    if (open) {
      loadAccounts();
      if (editEntry) {
        loadEditData();
      } else {
        resetForm();
      }
    }
  }, [open, editEntry]);

  const loadAccounts = async () => {
    try {
      const response = await apiClient.get('/api/finance/double-entry/accounts');
      if (Array.isArray(response)) {
        setAccounts(response);
      }
    } catch (error) {
      console.error('Error loading accounts:', error);
      setSnackbar({
        open: true,
        message: 'Failed to load chart of accounts',
        severity: 'error'
      });
    }
  };

  const loadEditData = () => {
    if (editEntry) {
      setFormData({
        date: editEntry.date ? editEntry.date.split('T')[0] : new Date().toISOString().split('T')[0],
        reference: editEntry.reference || '',
        description: editEntry.description || '',
        status: editEntry.status || 'draft',
        payment_method: editEntry.payment_method || 'bank'
      });
      
      if (editEntry.lines && editEntry.lines.length > 0) {
        const lines = editEntry.lines.map((line, index) => ({
          id: index + 1,
          account_id: line.account_id,
          description: line.description || '',
          debit_amount: line.debit_amount || 0,
          credit_amount: line.credit_amount || 0
        }));
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
    const errors = [];
    
    // For business-friendly mode, we only need basic validation
    // The system will auto-balance the entries
    
    // Check if we have at least one line with an account and amount
    const validLines = journalLines.filter(line => 
      line.account_id && ((line.debit_amount || 0) > 0 || (line.credit_amount || 0) > 0)
    );
    
    if (validLines.length === 0) {
      errors.push('Please select an account and enter an amount');
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
    if (!validation.valid) {
      setSnackbar({
        open: true,
        message: 'Please fix validation errors before submitting',
        severity: 'error'
      });
      return;
    }

    setLoading(true);
    try {
      // For business-friendly mode, we'll use the transaction templates API
      // to automatically create balanced journal entries
      
      // Get the first valid line (business transaction)
      const validLine = journalLines.find(line => 
        line.account_id && ((line.debit_amount || 0) > 0 || (line.credit_amount || 0) > 0)
      );
      
      if (!validLine) {
        throw new Error('No valid transaction found');
      }
      
      // Determine transaction type based on account and amount
      const amount = validLine.debit_amount || validLine.credit_amount;
      const isDebit = validLine.debit_amount > 0;
      
      // Create a simple business transaction
      const transactionData = {
        template_id: 'simple_transaction',
        amount: amount,
        description: formData.description || validLine.description,
        account_id: validLine.account_id,
        is_debit: isDebit,
        date: formData.date,
        reference: formData.reference || `JE-${Date.now()}`,
        status: formData.status,
        payment_method: formData.payment_method
      };

      let response;
      if (editEntry) {
        response = await apiClient.put(`/api/finance/double-entry/journal-entries/${editEntry.id}`, transactionData);
      } else {
        // Use the transaction templates API for auto-balancing
        response = await apiClient.post('/api/finance/transactions/create', transactionData);
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
    return account ? `${account.code} - ${account.name}` : '';
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
                            <Select
                              value={line.account_id}
                              onChange={(e) => updateJournalLine(line.id, 'account_id', e.target.value)}
                              displayEmpty
                            >
                              <MenuItem value="" disabled>
                                Select Account
                              </MenuItem>
                              {accounts.map((account) => (
                                <MenuItem key={account.id} value={account.id}>
                                  {account.code} - {account.name}
                                </MenuItem>
                              ))}
                            </Select>
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
