import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Grid,
  MenuItem,
  Chip,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  Autocomplete,
  Tooltip
} from '@mui/material';
import {
  Add,
  Delete,
  Save,
  Cancel,
  CheckCircle,
  Error
} from '@mui/icons-material';
import { useAuth } from '../../../hooks/useAuth';
import { useCoA } from '../context/CoAContext';

const JournalEntryForm = ({ open, onClose, entry = null, onSave }) => {
  const { user } = useAuth();
  const { accounts } = useCoA();
  
  const [formData, setFormData] = useState({
    period: new Date().toISOString().slice(0, 7), // YYYY-MM
    doc_date: new Date().toISOString().slice(0, 10), // YYYY-MM-DD
    reference: '',
    description: '',
    book_type: 'primary',
    entity: 'main',
    currency: 'USD',
    fx_rate: 1.0,
    lines: [
      { account_id: null, account_code: '', account_name: '', description: '', debit_amount: '', credit_amount: '', dimensions: {} },
      { account_id: null, account_code: '', account_name: '', description: '', debit_amount: '', credit_amount: '', dimensions: {} }
    ]
  });

  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);

  // Populate form when editing
  useEffect(() => {
    if (entry) {
      setFormData({
        period: entry.period || new Date().toISOString().slice(0, 7),
        doc_date: entry.doc_date || new Date().toISOString().slice(0, 10),
        reference: entry.reference || '',
        description: entry.description || '',
        book_type: entry.book_type || 'primary',
        entity: entry.entity || 'main',
        currency: entry.currency || 'USD',
        fx_rate: entry.fx_rate || 1.0,
        lines: entry.lines?.length > 0 ? entry.lines.map(line => ({
          ...line,
          debit_amount: line.debit_amount || '',
          credit_amount: line.credit_amount || ''
        })) : [
          { account_id: null, account_code: '', account_name: '', description: '', debit_amount: '', credit_amount: '', dimensions: {} },
          { account_id: null, account_code: '', account_name: '', description: '', debit_amount: '', credit_amount: '', dimensions: {} }
        ]
      });
    }
  }, [entry]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  // Smart account behavior logic
  const getAccountBehavior = (accountType) => {
    switch(accountType?.toLowerCase()) {
      case 'asset':
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Increase Asset',
          creditLabel: 'Decrease Asset',
          debitPlaceholder: 'Amount received/acquired',
          creditPlaceholder: 'Amount paid/reduced',
          normalSide: 'debit',
          helpText: 'Assets increase with debits, decrease with credits',
          color: '#1976d2', // Blue for assets
          icon: '💰'
        };
      case 'liability':
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Pay/Reduce Liability',
          creditLabel: 'Incur/Increase Liability',
          debitPlaceholder: 'Amount paid/reduced',
          creditPlaceholder: 'Amount owed/increased',
          normalSide: 'credit',
          helpText: 'Liabilities increase with credits, decrease with debits',
          color: '#d32f2f', // Red for liabilities
          icon: '💳'
        };
      case 'equity':
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Withdrawals/Losses',
          creditLabel: 'Investments/Profits',
          debitPlaceholder: 'Withdrawals/losses',
          creditPlaceholder: 'Investments/profits',
          normalSide: 'credit',
          helpText: 'Equity increases with credits, decreases with debits',
          color: '#388e3c', // Green for equity
          icon: '🏢'
        };
      case 'revenue':
        return {
          debitEnabled: false,
          creditEnabled: true,
          debitLabel: 'Refund/Reversal',
          creditLabel: 'Revenue Earned',
          debitPlaceholder: 'Refunds only',
          creditPlaceholder: 'Enter revenue amount',
          normalSide: 'credit',
          helpText: '💡 Revenue accounts normally have credit balances (money earned)',
          color: '#388e3c', // Green for revenue
          icon: '💵'
        };
      case 'expense':
        return {
          debitEnabled: true,
          creditEnabled: false,
          debitLabel: 'Expense Incurred',
          creditLabel: 'Expense Reversal',
          debitPlaceholder: 'Enter expense amount',
          creditPlaceholder: 'Reversals only',
          normalSide: 'debit',
          helpText: '💡 Expense accounts normally have debit balances (money spent)',
          color: '#f57c00', // Orange for expenses
          icon: '💸'
        };
      default:
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Debit',
          creditLabel: 'Credit',
          debitPlaceholder: 'Enter debit amount',
          creditPlaceholder: 'Enter credit amount',
          normalSide: 'debit',
          helpText: 'Select an account to see smart field behavior',
          color: '#757575', // Gray for unknown
          icon: '❓'
        };
    }
  };

  const handleLineChange = (index, field, value) => {
    const newLines = [...formData.lines];
    
    if (field === 'account_id') {
      const selectedAccount = accounts.find(acc => acc.id === value);
      if (selectedAccount) {
        newLines[index] = {
          ...newLines[index],
          account_id: value,
          account_code: selectedAccount.code,
          account_name: selectedAccount.name,
          account_type: selectedAccount.category || selectedAccount.account_type || selectedAccount.type // Store for smart behavior
        };
        
        // Smart field behavior: Clear amounts and apply account-specific logic
        const behavior = getAccountBehavior(selectedAccount.category || selectedAccount.account_type || selectedAccount.type);
        
        // Clear disabled fields
        if (!behavior.debitEnabled) {
          newLines[index].debit_amount = '';
        }
        if (!behavior.creditEnabled) {
          newLines[index].credit_amount = '';
        }
      }
    } else if (field === 'debit_amount' || field === 'credit_amount') {
      // Smart mutual exclusion: Clear opposite field when user enters amount
      if (field === 'debit_amount' && value) {
        newLines[index].credit_amount = '';
      } else if (field === 'credit_amount' && value) {
        newLines[index].debit_amount = '';
      }
      newLines[index][field] = value;
    } else {
      newLines[index] = { ...newLines[index], [field]: value };
    }
    
    setFormData(prev => ({ ...prev, lines: newLines }));
    
    // Clear line errors
    if (errors[`line_${index}_${field}`]) {
      setErrors(prev => ({ ...prev, [`line_${index}_${field}`]: null }));
    }
  };

  const addLine = () => {
    setFormData(prev => ({
      ...prev,
      lines: [...prev.lines, {
        account_id: null,
        account_code: '',
        account_name: '',
        description: '',
        debit_amount: '',
        credit_amount: '',
        dimensions: {}
      }]
    }));
  };

  const removeLine = (index) => {
    if (formData.lines.length > 2) {
      const newLines = formData.lines.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, lines: newLines }));
    }
  };

  const calculateTotals = () => {
    const totalDebits = formData.lines.reduce((sum, line) => 
      sum + (parseFloat(line.debit_amount) || 0), 0
    );
    const totalCredits = formData.lines.reduce((sum, line) => 
      sum + (parseFloat(line.credit_amount) || 0), 0
    );
    return { totalDebits, totalCredits, isBalanced: Math.abs(totalDebits - totalCredits) < 0.01 };
  };

  const validateForm = () => {
    const newErrors = {};
    
    // Header validation
    if (!formData.period) newErrors.period = 'Period is required';
    if (!formData.doc_date) newErrors.doc_date = 'Date is required';
    if (!formData.reference.trim()) newErrors.reference = 'Reference is required';
    if (!formData.description.trim()) newErrors.description = 'Description is required';
    
    // Lines validation
    formData.lines.forEach((line, index) => {
      if (!line.account_id) {
        newErrors[`line_${index}_account`] = 'Account is required';
      }
      if (!line.description.trim()) {
        newErrors[`line_${index}_description`] = 'Line description is required';
      }
      
      const debit = parseFloat(line.debit_amount) || 0;
      const credit = parseFloat(line.credit_amount) || 0;
      
      if (debit === 0 && credit === 0) {
        newErrors[`line_${index}_amount`] = 'Either debit or credit amount is required';
      }
      if (debit > 0 && credit > 0) {
        newErrors[`line_${index}_amount`] = 'Cannot have both debit and credit amounts';
      }
    });
    
    // Check if balanced
    const { isBalanced } = calculateTotals();
    if (!isBalanced) {
      newErrors.balance = 'Journal entry must be balanced (debits = credits)';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }
    
    setSaving(true);
    try {
      const journalData = {
        ...formData,
        created_by: user?.id || 'current_user',
        status: 'draft',
        lines: formData.lines.map((line, index) => ({
          ...line,
          line_no: index + 1,
          debit_amount: parseFloat(line.debit_amount) || 0,
          credit_amount: parseFloat(line.credit_amount) || 0
        }))
      };

      
      // For now, simulate API call - replace with actual API when ready
      setTimeout(() => {
        onSave(journalData);
        onClose();
        setSaving(false);
      }, 1000);
      
    } catch (error) {
      console.error('❌ Error saving journal entry:', error);
      setErrors({ submit: error.message || 'Failed to save journal entry' });
      setSaving(false);
    }
  };

  const { totalDebits, totalCredits, isBalanced } = calculateTotals();

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      fullScreen={typeof window !== 'undefined' ? window.matchMedia('(max-width:480px)').matches : false}
      PaperProps={{ sx: { minHeight: '80vh' } }}
      aria-labelledby="journal-entry-dialog-title"
      aria-describedby="journal-entry-dialog-content"
    >
      <DialogTitle 
        id="journal-entry-dialog-title"
        sx={{ display: 'flex', alignItems: 'center', gap: 2 }}
      >
        <Typography variant="h6">
          {entry ? 'Edit Journal Entry' : 'New Journal Entry'}
        </Typography>
        <Chip
          label={isBalanced ? 'Balanced' : 'Unbalanced'}
          color={isBalanced ? 'success' : 'error'}
          size="small"
          icon={isBalanced ? <CheckCircle /> : <Error />}
        />
      </DialogTitle>

      <DialogContent id="journal-entry-dialog-content">
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Smart Entry Information */}
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
              🧠 Smart Double-Entry Form
            </Typography>
            <Typography variant="body2">
              This form automatically enables/disables debit/credit fields based on account type to prevent errors:
            </Typography>
            <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              <Chip label="💰 Assets: Usually Debit" size="small" color="primary" variant="outlined" />
              <Chip label="💳 Liabilities: Usually Credit" size="small" color="error" variant="outlined" />
              <Chip label="💵 Revenue: Credit Only" size="small" color="success" variant="outlined" />
              <Chip label="💸 Expenses: Debit Only" size="small" color="warning" variant="outlined" />
            </Box>
          </Alert>

          {/* Header Information */}
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Journal Header
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <TextField
                  label="Period"
                  type="month"
                  value={formData.period}
                  onChange={(e) => handleInputChange('period', e.target.value)}
                  fullWidth
                  error={!!errors.period}
                  helperText={errors.period}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  label="Document Date"
                  type="date"
                  value={formData.doc_date}
                  onChange={(e) => handleInputChange('doc_date', e.target.value)}
                  fullWidth
                  error={!!errors.doc_date}
                  helperText={errors.doc_date}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  label="Reference"
                  value={formData.reference}
                  onChange={(e) => handleInputChange('reference', e.target.value)}
                  fullWidth
                  error={!!errors.reference}
                  helperText={errors.reference}
                  placeholder="e.g., INV-2024-001"
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <TextField
                  select
                  label="Book Type"
                  value={formData.book_type}
                  onChange={(e) => handleInputChange('book_type', e.target.value)}
                  fullWidth
                >
                  <MenuItem value="primary">Primary</MenuItem>
                  <MenuItem value="tax">Tax</MenuItem>
                  <MenuItem value="ifrs">IFRS</MenuItem>
                  <MenuItem value="consolidation">Consolidation</MenuItem>
                  <MenuItem value="management">Management</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  fullWidth
                  multiline
                  rows={2}
                  error={!!errors.description}
                  helperText={errors.description}
                  placeholder="Brief description of the transaction..."
                />
              </Grid>
            </Grid>
          </Paper>

          {/* Journal Lines */}
          <Paper sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Journal Lines
              </Typography>
              <Button
                startIcon={<Add />}
                onClick={addLine}
                variant="outlined"
                size="small"
              >
                Add Line
              </Button>
            </Box>

            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        Account
                        <Tooltip title="Select account to see smart field behavior">
                          <Typography variant="caption" sx={{ color: '#1976d2' }}>ℹ️</Typography>
                        </Tooltip>
                      </Box>
                    </TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" sx={{ color: '#1976d2' }}>💰</Typography>
                        Debit
                        <Typography variant="caption" color="text.secondary">(Dr)</Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" sx={{ color: '#388e3c' }}>💳</Typography>
                        Credit
                        <Typography variant="caption" color="text.secondary">(Cr)</Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {formData.lines.map((line, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Autocomplete
                          options={accounts}
                          getOptionLabel={(option) => option.name}
                          value={accounts.find(acc => acc.id === line.account_id) || null}
                          onChange={(e, newValue) => {
                            handleLineChange(index, 'account_id', newValue?.id || null);
                          }}
                          isOptionEqualToValue={(option, value) => option.id === value?.id}
                          groupBy={(option) => {
                            const categoryLabels = {
                              asset: '💰 Assets',
                              liability: '📋 Liabilities', 
                              equity: '👤 Equity',
                              revenue: '📈 Revenue',
                              expense: '💸 Expenses'
                            };
                            return categoryLabels[option.category] || 'Other';
                          }}
                          renderInput={(params) => (
                            <TextField
                              {...params}
                              placeholder="Select account..."
                              error={!!errors[`line_${index}_account`]}
                              helperText={errors[`line_${index}_account`]}
                              size="small"
                              sx={{ minWidth: 200 }}
                            />
                          )}
                          renderOption={(props, option) => (
                            <Box component="li" {...props}>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                                <Typography variant="body2" sx={{ flexGrow: 1 }}>
                                  {option.name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {option.type}
                                </Typography>
                              </Box>
                            </Box>
                          )}
                        />
                          <Tooltip title="Quick Add Account">
                            <IconButton
                              size="small"
                              onClick={() => {
                                // Quick add account functionality
                                const newAccountCode = prompt('Enter account code:');
                                const newAccountName = prompt('Enter account name:');
                                if (newAccountCode && newAccountName) {
                                  // Here you would call the API to create a new account
                                  // For now, just show a message
                                  alert('Account creation feature coming soon!');
                                }
                              }}
                            >
                              <Add />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <TextField
                          value={line.description}
                          onChange={(e) => handleLineChange(index, 'description', e.target.value)}
                          placeholder="Line description..."
                          size="small"
                          error={!!errors[`line_${index}_description`]}
                          helperText={errors[`line_${index}_description`]}
                          sx={{ minWidth: 150 }}
                        />
                      </TableCell>
                      <TableCell>
                        {(() => {
                          const selectedAccount = accounts.find(acc => acc.id === line.account_id);
                          const behavior = getAccountBehavior(selectedAccount?.category || selectedAccount?.account_type || selectedAccount?.type);
                          
                          return (
                            <Box sx={{ position: 'relative' }}>
                              <TextField
                                type="number"
                                value={line.debit_amount}
                                onChange={(e) => handleLineChange(index, 'debit_amount', e.target.value)}
                                placeholder={behavior.debitPlaceholder}
                                size="small"
                                disabled={!behavior.debitEnabled}
                                error={!!errors[`line_${index}_amount`]}
                                sx={{ 
                                  width: 120,
                                  '& .MuiInputBase-input.Mui-disabled': {
                                    backgroundColor: '#f5f5f5',
                                    color: '#999',
                                    WebkitTextFillColor: '#999'
                                  }
                                }}
                                InputProps={{
                                  startAdornment: <Typography sx={{ mr: 1, color: behavior.debitEnabled ? behavior.color : '#999' }}>$</Typography>,
                                }}
                                label={behavior.debitLabel}
                                InputLabelProps={{ shrink: true }}
                              />
                              {!behavior.debitEnabled && selectedAccount && (
                                <Tooltip title={`${selectedAccount.category || selectedAccount.account_type || selectedAccount.type} accounts don't normally have debits. ${behavior.helpText}`}>
                                  <Box sx={{ 
                                    position: 'absolute', 
                                    top: 0, 
                                    right: 0, 
                                    bgcolor: '#fff3cd', 
                                    color: '#856404',
                                    px: 0.5, 
                                    py: 0.25, 
                                    borderRadius: 1,
                                    fontSize: '0.75rem',
                                    border: '1px solid #ffeaa7'
                                  }}>
                                    🚫
                                  </Box>
                                </Tooltip>
                              )}
                            </Box>
                          );
                        })()}
                      </TableCell>
                      <TableCell>
                        {(() => {
                          const selectedAccount = accounts.find(acc => acc.id === line.account_id);
                          const behavior = getAccountBehavior(selectedAccount?.category || selectedAccount?.account_type || selectedAccount?.type);
                          
                          return (
                            <Box sx={{ position: 'relative' }}>
                              <TextField
                                type="number"
                                value={line.credit_amount}
                                onChange={(e) => handleLineChange(index, 'credit_amount', e.target.value)}
                                placeholder={behavior.creditPlaceholder}
                                size="small"
                                disabled={!behavior.creditEnabled}
                                error={!!errors[`line_${index}_amount`]}
                                sx={{ 
                                  width: 120,
                                  '& .MuiInputBase-input.Mui-disabled': {
                                    backgroundColor: '#f5f5f5',
                                    color: '#999',
                                    WebkitTextFillColor: '#999'
                                  }
                                }}
                                InputProps={{
                                  startAdornment: <Typography sx={{ mr: 1, color: behavior.creditEnabled ? behavior.color : '#999' }}>$</Typography>,
                                }}
                                label={behavior.creditLabel}
                                InputLabelProps={{ shrink: true }}
                              />
                              {!behavior.creditEnabled && selectedAccount && (
                                <Tooltip title={`${selectedAccount.category || selectedAccount.account_type || selectedAccount.type} accounts don't normally have credits. ${behavior.helpText}`}>
                                  <Box sx={{ 
                                    position: 'absolute', 
                                    top: 0, 
                                    right: 0, 
                                    bgcolor: '#fff3cd', 
                                    color: '#856404',
                                    px: 0.5, 
                                    py: 0.25, 
                                    borderRadius: 1,
                                    fontSize: '0.75rem',
                                    border: '1px solid #ffeaa7'
                                  }}>
                                    🚫
                                  </Box>
                                </Tooltip>
                              )}
                            </Box>
                          );
                        })()}
                      </TableCell>
                      <TableCell align="center">
                        <IconButton
                          onClick={() => removeLine(index)}
                          disabled={formData.lines.length <= 2}
                          size="small"
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {errors[`line_0_amount`] && (
              <Alert severity="error" sx={{ mt: 1 }}>
                {errors[`line_0_amount`]}
              </Alert>
            )}
          </Paper>

          {/* Totals Summary */}
          <Paper sx={{ p: 2, bgcolor: isBalanced ? 'success.50' : 'error.50' }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={3}>
                <Typography variant="h6" color={isBalanced ? 'success.main' : 'error.main'}>
                  Total Debits: ${totalDebits.toFixed(2)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="h6" color={isBalanced ? 'success.main' : 'error.main'}>
                  Total Credits: ${totalCredits.toFixed(2)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="h6" color={isBalanced ? 'success.main' : 'error.main'}>
                  Difference: ${Math.abs(totalDebits - totalCredits).toFixed(2)}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Chip
                  label={isBalanced ? 'BALANCED ✓' : 'UNBALANCED ✗'}
                  color={isBalanced ? 'success' : 'error'}
                  variant="filled"
                  icon={isBalanced ? <CheckCircle /> : <Error />}
                />
              </Grid>
            </Grid>
            
            {errors.balance && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {errors.balance}
              </Alert>
            )}
          </Paper>

          {/* Smart Account Guidance Panel */}
          {formData.lines.some(line => line.account_id) && (
            <Paper sx={{ p: 2, bgcolor: '#f8f9fa', border: '1px solid #e9ecef' }}>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                💡 Smart Entry Guidance
              </Typography>
              <Grid container spacing={2}>
                {formData.lines.map((line, index) => {
                  const selectedAccount = accounts.find(acc => acc.id === line.account_id);
                  if (!selectedAccount) return null;
                  
                  const behavior = getAccountBehavior(selectedAccount.category || selectedAccount.account_type || selectedAccount.type);
                  
                  return (
                    <Grid item xs={12} md={6} key={index}>
                      <Box sx={{ 
                        p: 1.5, 
                        border: '1px solid #dee2e6', 
                        borderRadius: 1, 
                        bgcolor: 'white',
                        borderLeft: `4px solid ${behavior.color}`
                      }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                          {behavior.icon} {selectedAccount.name}
                          <Chip label={selectedAccount.category || selectedAccount.account_type || selectedAccount.type} size="small" sx={{ ml: 1 }} />
                        </Typography>
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                          {behavior.helpText}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip 
                            label={`${behavior.debitLabel}: ${behavior.debitEnabled ? 'ENABLED' : 'DISABLED'}`}
                            size="small" 
                            color={behavior.debitEnabled ? 'primary' : 'default'}
                            variant={behavior.normalSide === 'debit' ? 'filled' : 'outlined'}
                          />
                          <Chip 
                            label={`${behavior.creditLabel}: ${behavior.creditEnabled ? 'ENABLED' : 'DISABLED'}`}
                            size="small" 
                            color={behavior.creditEnabled ? 'primary' : 'default'}
                            variant={behavior.normalSide === 'credit' ? 'filled' : 'outlined'}
                          />
                        </Box>
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </Paper>
          )}

          {/* General Errors */}
          {errors.submit && (
            <Alert severity="error">
              {errors.submit}
            </Alert>
          )}
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button
          onClick={onClose}
          startIcon={<Cancel />}
          disabled={saving}
        >
          Cancel
        </Button>
        <Button
          onClick={handleSave}
          variant="contained"
          startIcon={<Save />}
          disabled={saving || !isBalanced}
          sx={{ minWidth: 120 }}
        >
          {saving ? 'Saving...' : 'Save Journal'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default JournalEntryForm;
