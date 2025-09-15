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
import { useAuth } from '../../../App';
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

  const handleLineChange = (index, field, value) => {
    const newLines = [...formData.lines];
    
    if (field === 'account_id') {
      const selectedAccount = accounts.find(acc => acc.id === value);
      if (selectedAccount) {
        newLines[index] = {
          ...newLines[index],
          account_id: value,
          account_code: selectedAccount.code,
          account_name: selectedAccount.name
        };
      }
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
                    <TableCell>Account</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell align="right">Debit</TableCell>
                    <TableCell align="right">Credit</TableCell>
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
                        <TextField
                          type="number"
                          value={line.debit_amount}
                          onChange={(e) => handleLineChange(index, 'debit_amount', e.target.value)}
                          placeholder="0.00"
                          size="small"
                          error={!!errors[`line_${index}_amount`]}
                          sx={{ width: 100 }}
                          InputProps={{
                            startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          type="number"
                          value={line.credit_amount}
                          onChange={(e) => handleLineChange(index, 'credit_amount', e.target.value)}
                          placeholder="0.00"
                          size="small"
                          error={!!errors[`line_${index}_amount`]}
                          sx={{ width: 100 }}
                          InputProps={{
                            startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>,
                          }}
                        />
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
