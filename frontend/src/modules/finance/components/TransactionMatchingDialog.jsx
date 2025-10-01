import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography,
  Table, TableBody, TableCell, TableHead, TableRow, Paper, Alert, LinearProgress,
  IconButton, Tooltip, Chip, Card, CardContent, Grid, FormControl, InputLabel,
  Select, MenuItem, TextField, Checkbox, FormControlLabel, Divider, List,
  ListItem, ListItemText, ListItemIcon, Avatar, Badge
} from '@mui/material';
import {
  CompareArrows, CheckCircle, Warning, Error, AutoFixHigh, Visibility,
  AttachMoney, TrendingUp, TrendingDown, Schedule, Description, Receipt
} from '@mui/icons-material';
import apiClient from '../../../services/apiClient';

const TransactionMatchingDialog = ({ open, onClose, bankTransactions, glEntries, onMatch }) => {
  const [selectedBankTx, setSelectedBankTx] = useState(null);
  const [selectedGlEntry, setSelectedGlEntry] = useState(null);
  const [autoMatchResults, setAutoMatchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [matchCriteria, setMatchCriteria] = useState({
    amountTolerance: 0.01,
    dateTolerance: 3, // days
    requireReference: false
  });

  useEffect(() => {
    if (open && bankTransactions.length > 0) {
      setSelectedBankTx(bankTransactions[0]);
    }
  }, [open, bankTransactions]);

  const handleAutoMatch = async () => {
    if (!selectedBankTx) return;

    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.post('/api/finance/auto-match', {
        bank_transaction_id: selectedBankTx.id,
        amount_tolerance: matchCriteria.amountTolerance,
        date_tolerance: matchCriteria.dateTolerance,
        require_reference: matchCriteria.requireReference
      });

      setAutoMatchResults(response.data.matches || []);
    } catch (err) {
      setError(err.message || 'Auto-matching failed');
    } finally {
      setLoading(false);
    }
  };

  const handleManualMatch = async (glEntry) => {
    if (!selectedBankTx || !glEntry) return;

    try {
      setLoading(true);
      setError(null);

      await apiClient.post('/api/finance/match-transaction', {
        bank_transaction_id: selectedBankTx.id,
        gl_entry_id: glEntry.id,
        match_type: 'manual'
      });

      onMatch?.(selectedBankTx.id, glEntry.id);
      setSelectedBankTx(null);
      setSelectedGlEntry(null);
      setAutoMatchResults([]);
    } catch (err) {
      setError(err.message || 'Manual matching failed');
    } finally {
      setLoading(false);
    }
  };

  const handleUnmatch = async (bankTxId) => {
    try {
      setLoading(true);
      await apiClient.delete(`/api/finance/match-transaction/${bankTxId}`);
      onMatch?.(bankTxId, null);
    } catch (err) {
      setError(err.message || 'Unmatching failed');
    } finally {
      setLoading(false);
    }
  };

  const getMatchScore = (bankTx, glEntry) => {
    let score = 0;
    const amountDiff = Math.abs(bankTx.amount - glEntry.balance);
    const dateDiff = Math.abs(new Date(bankTx.transaction_date) - new Date(glEntry.entry_date)) / (1000 * 60 * 60 * 24);

    // Amount matching (40% weight)
    if (amountDiff === 0) score += 40;
    else if (amountDiff <= matchCriteria.amountTolerance) score += 30;
    else if (amountDiff <= matchCriteria.amountTolerance * 2) score += 20;

    // Date matching (30% weight)
    if (dateDiff === 0) score += 30;
    else if (dateDiff <= matchCriteria.dateTolerance) score += 25;
    else if (dateDiff <= matchCriteria.dateTolerance * 2) score += 15;

    // Reference matching (20% weight)
    if (bankTx.reference && glEntry.reference && 
        bankTx.reference.toLowerCase() === glEntry.reference.toLowerCase()) {
      score += 20;
    }

    // Description similarity (10% weight)
    if (bankTx.description && glEntry.description) {
      const similarity = calculateSimilarity(bankTx.description, glEntry.description);
      score += similarity * 10;
    }

    return Math.min(score, 100);
  };

  const calculateSimilarity = (str1, str2) => {
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;
    if (longer.length === 0) return 1.0;
    const distance = levenshteinDistance(longer, shorter);
    return (longer.length - distance) / longer.length;
  };

  const levenshteinDistance = (str1, str2) => {
    const matrix = [];
    for (let i = 0; i <= str2.length; i++) {
      matrix[i] = [i];
    }
    for (let j = 0; j <= str1.length; j++) {
      matrix[0][j] = j;
    }
    for (let i = 1; i <= str2.length; i++) {
      for (let j = 1; j <= str1.length; j++) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1,
            matrix[i][j - 1] + 1,
            matrix[i - 1][j] + 1
          );
        }
      }
    }
    return matrix[str2.length][str1.length];
  };

  const getMatchColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const filteredGlEntries = glEntries.filter(entry => 
    !entry.matched && entry.bank_account_id === selectedBankTx?.bank_account_id
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <CompareArrows color="primary" />
          <Typography variant="h6">Transaction Matching</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Bank Transaction Selection */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Bank Transactions
                </Typography>
                <Paper sx={{ maxHeight: 400, overflow: 'auto' }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Amount</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {bankTransactions.map((tx) => (
                        <TableRow 
                          key={tx.id}
                          onClick={() => setSelectedBankTx(tx)}
                          sx={{ 
                            cursor: 'pointer',
                            bgcolor: selectedBankTx?.id === tx.id ? 'action.selected' : 'transparent'
                          }}
                        >
                          <TableCell>{tx.transaction_date}</TableCell>
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
                            <Chip 
                              label={tx.matched ? 'Matched' : 'Unmatched'} 
                              size="small"
                              color={tx.matched ? 'success' : 'warning'}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </Paper>
              </CardContent>
            </Card>
          </Grid>

          {/* Selected Bank Transaction Details */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Selected Transaction
                </Typography>
                {selectedBankTx ? (
                  <Box>
                    <List dense>
                      <ListItem>
                        <ListItemIcon><Schedule /></ListItemIcon>
                        <ListItemText 
                          primary="Date" 
                          secondary={selectedBankTx.transaction_date} 
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><AttachMoney /></ListItemIcon>
                        <ListItemText 
                          primary="Amount" 
                          secondary={`$${Math.abs(selectedBankTx.amount).toLocaleString()}`} 
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><Description /></ListItemIcon>
                        <ListItemText 
                          primary="Description" 
                          secondary={selectedBankTx.description} 
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><Receipt /></ListItemIcon>
                        <ListItemText 
                          primary="Reference" 
                          secondary={selectedBankTx.reference || 'N/A'} 
                        />
                      </ListItem>
                    </List>
                    
                    <Box mt={2}>
                      <Button 
                        variant="outlined" 
                        onClick={handleAutoMatch}
                        startIcon={<AutoFixHigh />}
                        fullWidth
                        disabled={loading}
                      >
                        Auto Match
                      </Button>
                    </Box>
                  </Box>
                ) : (
                  <Typography color="text.secondary">
                    Select a bank transaction to view details
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* GL Entries for Matching */}
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  GL Entries
                </Typography>
                <Paper sx={{ maxHeight: 400, overflow: 'auto' }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Amount</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell>Score</TableCell>
                        <TableCell>Action</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filteredGlEntries.map((entry) => {
                        const score = selectedBankTx ? getMatchScore(selectedBankTx, entry) : 0;
                        return (
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
                            <TableCell>
                              <Chip 
                                label={`${score}%`}
                                size="small"
                                color={getMatchColor(score)}
                              />
                            </TableCell>
                            <TableCell>
                              <Button 
                                size="small"
                                onClick={() => handleManualMatch(entry)}
                                disabled={loading}
                              >
                                Match
                              </Button>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </Paper>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Auto Match Results */}
        {autoMatchResults.length > 0 && (
          <Box mt={3}>
            <Typography variant="h6" gutterBottom>
              Auto Match Results
            </Typography>
            <Grid container spacing={2}>
              {autoMatchResults.map((match, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Box>
                          <Typography variant="subtitle1">
                            {match.gl_entry.description}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Score: {match.score}% | Amount: ${Math.abs(match.gl_entry.balance).toLocaleString()}
                          </Typography>
                        </Box>
                        <Button 
                          size="small"
                          onClick={() => handleManualMatch(match.gl_entry)}
                          disabled={loading}
                        >
                          Confirm Match
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Match Criteria Settings */}
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Match Criteria
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Amount Tolerance"
                type="number"
                value={matchCriteria.amountTolerance}
                onChange={(e) => setMatchCriteria(prev => ({
                  ...prev,
                  amountTolerance: parseFloat(e.target.value) || 0
                }))}
                InputProps={{ startAdornment: '$' }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Date Tolerance (days)"
                type="number"
                value={matchCriteria.dateTolerance}
                onChange={(e) => setMatchCriteria(prev => ({
                  ...prev,
                  dateTolerance: parseInt(e.target.value) || 0
                }))}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={matchCriteria.requireReference}
                    onChange={(e) => setMatchCriteria(prev => ({
                      ...prev,
                      requireReference: e.target.checked
                    }))}
                  />
                }
                label="Require Reference Match"
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button 
          variant="contained" 
          onClick={() => {
            // Refresh data
            onClose();
          }}
        >
          Refresh
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TransactionMatchingDialog;










