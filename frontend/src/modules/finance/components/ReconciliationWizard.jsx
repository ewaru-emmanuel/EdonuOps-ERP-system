import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Stepper, Step, StepLabel, StepContent, Button, Card, CardContent,
  Grid, TextField, FormControl, InputLabel, Select, MenuItem, Alert, LinearProgress,
  Table, TableBody, TableCell, TableHead, TableRow, Paper, Chip, IconButton, Tooltip,
  Dialog, DialogTitle, DialogContent, DialogActions, Divider, List, ListItem, ListItemText,
  ListItemIcon, Checkbox, FormControlLabel, Switch, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import {
  AccountBalance, Upload, CompareArrows, CheckCircle, Warning, Error,
  ExpandMore, Visibility, AutoFixHigh, Download, Refresh, Add, Delete,
  CloudUpload, Description, Schedule, AttachMoney, TrendingUp, TrendingDown
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';
import CSVImportDialog from './CSVImportDialog';
import TransactionMatchingDialog from './TransactionMatchingDialog';

const ReconciliationWizard = ({ open, onClose, onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [selectedBankAccount, setSelectedBankAccount] = useState('');
  const [statementDate, setStatementDate] = useState('');
  const [statementBalance, setStatementBalance] = useState('');
  const [importedTransactions, setImportedTransactions] = useState([]);
  const [unreconciledGlEntries, setUnreconciledGlEntries] = useState([]);
  const [matchedTransactions, setMatchedTransactions] = useState([]);
  const [reconciliationSession, setReconciliationSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [csvImportOpen, setCsvImportOpen] = useState(false);
  const [matchingDialogOpen, setMatchingDialogOpen] = useState(false);

  // Data hooks
  const { data: bankAccounts, loading: bankAccountsLoading } = useRealTimeData('/api/finance/bank-accounts');
  const { data: bankTransactions, loading: transactionsLoading, refresh: refreshTransactions } = useRealTimeData('/api/finance/bank-transactions');

  const steps = [
    'Select Bank Account',
    'Import Bank Statement',
    'Review Transactions',
    'Match Transactions',
    'Complete Reconciliation'
  ];

  // Step 1: Select Bank Account
  const renderStep1 = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Select Bank Account for Reconciliation
      </Typography>
      <FormControl fullWidth margin="normal">
        <InputLabel>Bank Account</InputLabel>
        <Select
          value={selectedBankAccount}
          onChange={(e) => setSelectedBankAccount(e.target.value)}
          disabled={bankAccountsLoading}
        >
          {bankAccounts?.map((account) => (
            <MenuItem key={account.id} value={account.id}>
              {account.account_name} - {account.account_number}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <TextField
        fullWidth
        label="Statement Date"
        type="date"
        value={statementDate}
        onChange={(e) => setStatementDate(e.target.value)}
        margin="normal"
        InputLabelProps={{ shrink: true }}
      />
      
      <TextField
        fullWidth
        label="Statement Balance"
        type="number"
        value={statementBalance}
        onChange={(e) => setStatementBalance(e.target.value)}
        margin="normal"
        InputProps={{ startAdornment: '$' }}
      />
    </Box>
  );

  // Step 2: Import Bank Statement
  const renderStep2 = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Import Bank Statement
      </Typography>
      
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <CloudUpload color="primary" />
            <Typography variant="h6">CSV Import</Typography>
          </Box>
          <Button 
            variant="outlined" 
            onClick={() => setCsvImportOpen(true)}
            startIcon={<Upload />}
          >
            Upload CSV File
          </Button>
          <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 1 }}>
            Upload a CSV file with columns: Date, Amount, Description, Reference
          </Typography>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Description color="primary" />
            <Typography variant="h6">Manual Entry</Typography>
          </Box>
          <Button 
            variant="outlined" 
            startIcon={<Add />}
            onClick={handleAddTransaction}
          >
            Add Transaction Manually
          </Button>
        </CardContent>
      </Card>
    </Box>
  );

  // Step 3: Review Transactions
  const renderStep3 = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Review Imported Transactions
      </Typography>
      
      {importedTransactions.length > 0 ? (
        <Paper>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Reference</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {importedTransactions.map((tx, index) => (
                <TableRow key={index}>
                  <TableCell>{tx.date}</TableCell>
                  <TableCell>
                    <Typography 
                      color={tx.amount >= 0 ? 'success.main' : 'error.main'}
                      fontWeight="medium"
                    >
                      ${Math.abs(tx.amount).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell>{tx.description}</TableCell>
                  <TableCell>{tx.reference}</TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleDeleteTransaction(index)}>
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      ) : (
        <Alert severity="info">
          No transactions imported yet. Please import a CSV file or add transactions manually.
        </Alert>
      )}
    </Box>
  );

  // Step 4: Match Transactions
  const renderStep4 = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Match Bank Transactions with GL Entries
      </Typography>
      
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" gutterBottom>
            Bank Transactions
          </Typography>
          <Paper sx={{ maxHeight: 400, overflow: 'auto' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Match</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {importedTransactions.map((tx, index) => (
                  <TableRow key={index}>
                    <TableCell>{tx.date}</TableCell>
                    <TableCell>
                      <Typography 
                        color={tx.amount >= 0 ? 'success.main' : 'error.main'}
                        fontWeight="medium"
                      >
                        ${Math.abs(tx.amount).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>{tx.description}</TableCell>
                    <TableCell>
                      <Button 
                        size="small" 
                        variant="outlined"
                        onClick={() => handleAutoMatch(tx)}
                        startIcon={<AutoFixHigh />}
                      >
                        Auto Match
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" gutterBottom>
            GL Entries
          </Typography>
          <Paper sx={{ maxHeight: 400, overflow: 'auto' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Reference</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {unreconciledGlEntries.map((entry) => (
                  <TableRow key={entry.id}>
                    <TableCell>{entry.entry_date}</TableCell>
                    <TableCell>
                      <Typography 
                        color={entry.balance >= 0 ? 'success.main' : 'error.main'}
                        fontWeight="medium"
                      >
                        ${Math.abs(entry.balance).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>{entry.description}</TableCell>
                    <TableCell>{entry.reference}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
          </Grid>
        </Grid>
        
        <Box mt={2}>
          <Button 
            variant="contained" 
            onClick={() => setMatchingDialogOpen(true)}
            startIcon={<CompareArrows />}
            fullWidth
          >
            Open Advanced Matching Tool
          </Button>
        </Box>
      </Box>
    );

  // Step 5: Complete Reconciliation
  const renderStep5 = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Complete Reconciliation
      </Typography>
      
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="subtitle1" gutterBottom>
            Reconciliation Summary
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Statement Balance
              </Typography>
              <Typography variant="h6">
                ${parseFloat(statementBalance || 0).toLocaleString()}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Book Balance
              </Typography>
              <Typography variant="h6">
                ${reconciliationSession?.book_balance?.toLocaleString() || '0'}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Difference
              </Typography>
              <Typography 
                variant="h6" 
                color={reconciliationSession?.difference === 0 ? 'success.main' : 'error.main'}
              >
                ${reconciliationSession?.difference?.toLocaleString() || '0'}
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="text.secondary">
                Matched Transactions
              </Typography>
              <Typography variant="h6">
                {matchedTransactions.length}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      {reconciliationSession?.difference !== 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          There is a difference between statement and book balance. Please review and resolve discrepancies.
        </Alert>
      )}
    </Box>
  );

  // Event handlers
  const handleCSVImport = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const csv = e.target.result;
        const lines = csv.split('\n');
        const transactions = lines.slice(1).map(line => {
          const [date, amount, description, reference] = line.split(',');
          return {
            date: date?.trim(),
            amount: parseFloat(amount?.trim()) || 0,
            description: description?.trim(),
            reference: reference?.trim()
          };
        }).filter(tx => tx.date && tx.amount);
        
        setImportedTransactions(transactions);
      };
      reader.readAsText(file);
    }
  };

  const handleAddTransaction = () => {
    const newTransaction = {
      date: new Date().toISOString().split('T')[0],
      amount: 0,
      description: '',
      reference: ''
    };
    setImportedTransactions([...importedTransactions, newTransaction]);
  };

  const handleDeleteTransaction = (index) => {
    const updated = importedTransactions.filter((_, i) => i !== index);
    setImportedTransactions(updated);
  };

  const handleAutoMatch = async (transaction) => {
    try {
      setLoading(true);
      // Call auto-match API
      const response = await apiClient.post('/api/finance/auto-match', {
        session_id: reconciliationSession?.id,
        bank_account_id: selectedBankAccount
      });
      
      if (response.data.matches_found > 0) {
        setError(null);
        // Refresh data
        await refreshTransactions();
      } else {
        setError('No matches found for this transaction');
      }
    } catch (err) {
      setError(err.message || 'Auto-matching failed');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (activeStep === 0) {
      // Create reconciliation session
      try {
        setLoading(true);
        const response = await apiClient.post('/api/finance/reconciliation-sessions', {
          bank_account_id: selectedBankAccount,
          statement_date: statementDate,
          statement_balance: parseFloat(statementBalance)
        });
        
        setReconciliationSession(response.data);
        setActiveStep(1);
      } catch (err) {
        setError(err.message || 'Failed to create reconciliation session');
      } finally {
        setLoading(false);
      }
    } else if (activeStep === 1) {
      // Import transactions
      try {
        setLoading(true);
        for (const tx of importedTransactions) {
          await apiClient.post('/api/finance/bank-transactions', {
            bank_account_id: selectedBankAccount,
            transaction_date: tx.date,
            amount: tx.amount,
            description: tx.description,
            reference: tx.reference,
            reconciliation_session_id: reconciliationSession.id
          });
        }
        
        // Load unreconciled GL entries
        const glResponse = await apiClient.get(`/api/finance/unreconciled-gl-entries?bank_account_id=${selectedBankAccount}`);
        setUnreconciledGlEntries(glResponse.data);
        
        setActiveStep(2);
      } catch (err) {
        setError(err.message || 'Failed to import transactions');
      } finally {
        setLoading(false);
      }
    } else if (activeStep === 2) {
      setActiveStep(3);
    } else if (activeStep === 3) {
      setActiveStep(4);
    } else if (activeStep === 4) {
      // Complete reconciliation
      try {
        setLoading(true);
        await apiClient.post(`/api/finance/reconciliation-sessions/${reconciliationSession.id}/complete`);
        onComplete?.();
        onClose?.();
      } catch (err) {
        setError(err.message || 'Failed to complete reconciliation');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleBack = () => {
    setActiveStep(activeStep - 1);
  };

  const handleClose = () => {
    setActiveStep(0);
    setSelectedBankAccount('');
    setStatementDate('');
    setStatementBalance('');
    setImportedTransactions([]);
    setUnreconciledGlEntries([]);
    setMatchedTransactions([]);
    setReconciliationSession(null);
    setError(null);
    onClose?.();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <AccountBalance color="primary" />
          <Typography variant="h6">Bank Reconciliation Wizard</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        
        <Stepper activeStep={activeStep} orientation="vertical">
          <Step>
            <StepLabel>Select Bank Account</StepLabel>
            <StepContent>
              {renderStep1()}
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Import Bank Statement</StepLabel>
            <StepContent>
              {renderStep2()}
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Review Transactions</StepLabel>
            <StepContent>
              {renderStep3()}
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Match Transactions</StepLabel>
            <StepContent>
              {renderStep4()}
            </StepContent>
          </Step>
          
          <Step>
            <StepLabel>Complete Reconciliation</StepLabel>
            <StepContent>
              {renderStep5()}
            </StepContent>
          </Step>
        </Stepper>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        {activeStep > 0 && (
          <Button onClick={handleBack}>Back</Button>
        )}
        <Button 
          variant="contained" 
          onClick={handleNext}
          disabled={loading || (activeStep === 0 && (!selectedBankAccount || !statementDate || !statementBalance))}
        >
          {activeStep === steps.length - 1 ? 'Complete' : 'Next'}
        </Button>
      </DialogActions>
      
      <CSVImportDialog 
        open={csvImportOpen}
        onClose={() => setCsvImportOpen(false)}
        onImport={(transactions) => {
          setImportedTransactions(transactions);
          setCsvImportOpen(false);
        }}
        bankAccountId={selectedBankAccount}
      />
      
      <TransactionMatchingDialog 
        open={matchingDialogOpen}
        onClose={() => setMatchingDialogOpen(false)}
        bankTransactions={bankTransactions?.filter(tx => tx.bank_account_id === selectedBankAccount) || []}
        glEntries={unreconciledGlEntries}
        onMatch={(bankTxId, glEntryId) => {
          // Handle match result
          if (glEntryId) {
            setMatchedTransactions(prev => [...prev, { bankTxId, glEntryId }]);
          }
        }}
      />
    </Dialog>
  );
};

export default ReconciliationWizard;
