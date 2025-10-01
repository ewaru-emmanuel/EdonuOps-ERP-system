import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography,
  Table, TableBody, TableCell, TableHead, TableRow, Paper, Alert, LinearProgress,
  Card, CardContent, Grid, Chip, Divider, List, ListItem, ListItemText,
  ListItemIcon, IconButton, Tooltip, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import {
  Download, Print, Share, CheckCircle, Warning, Error, Info,
  ExpandMore, AttachMoney, TrendingUp, TrendingDown, Schedule, Description,
  Receipt, AccountBalance, CompareArrows, Assessment, Timeline
} from '@mui/icons-material';
import apiClient from '../../../services/apiClient';

const ReconciliationReportDialog = ({ open, onClose, reconciliationSession }) => {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (open && reconciliationSession) {
      generateReport();
    }
  }, [open, reconciliationSession]);

  const generateReport = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get(`/api/finance/reconciliation-sessions/${reconciliationSession.id}/report`);
      setReportData(response.data);
    } catch (err) {
      setError(err.message || 'Failed to generate report');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await apiClient.get(`/api/finance/reconciliation-sessions/${reconciliationSession.id}/report/pdf`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `reconciliation-report-${reconciliationSession.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || 'Failed to download PDF');
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle color="success" />;
      case 'pending': return <Warning color="warning" />;
      case 'discrepancy': return <Error color="error" />;
      default: return <Info color="info" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'pending': return 'warning';
      case 'discrepancy': return 'error';
      default: return 'default';
    }
  };

  if (!reportData) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <DialogTitle>Reconciliation Report</DialogTitle>
        <DialogContent>
          {loading && <LinearProgress />}
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Close</Button>
        </DialogActions>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <Assessment color="primary" />
          <Typography variant="h6">Reconciliation Report</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {/* Report Header */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Bank Account Information
                </Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><AccountBalance /></ListItemIcon>
                    <ListItemText 
                      primary="Bank Account" 
                      secondary={reportData.bank_account_name} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Schedule /></ListItemIcon>
                    <ListItemText 
                      primary="Statement Date" 
                      secondary={reportData.statement_date} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Receipt /></ListItemIcon>
                    <ListItemText 
                      primary="Reconciliation ID" 
                      secondary={reportData.id} 
                    />
                  </ListItem>
                </List>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Reconciliation Status
                </Typography>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  {getStatusIcon(reportData.status)}
                  <Chip 
                    label={reportData.status} 
                    color={getStatusColor(reportData.status)}
                    size="large"
                  />
                </Box>
                <List dense>
                  <ListItem>
                    <ListItemIcon><AttachMoney /></ListItemIcon>
                    <ListItemText 
                      primary="Statement Balance" 
                      secondary={`$${reportData.statement_balance?.toLocaleString() || '0'}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><AccountBalance /></ListItemIcon>
                    <ListItemText 
                      primary="Book Balance" 
                      secondary={`$${reportData.book_balance?.toLocaleString() || '0'}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><CompareArrows /></ListItemIcon>
                    <ListItemText 
                      primary="Difference" 
                      secondary={`$${reportData.difference?.toLocaleString() || '0'}`} 
                    />
                  </ListItem>
                </List>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Summary Statistics */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Summary Statistics
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {reportData.total_transactions || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Transactions
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="success.main">
                    {reportData.matched_transactions || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Matched Transactions
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="warning.main">
                    {reportData.unmatched_transactions || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Unmatched Transactions
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="error.main">
                    {reportData.discrepancies || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Discrepancies
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Matched Transactions */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">
              Matched Transactions ({reportData.matched_transactions || 0})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Paper>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Bank Amount</TableCell>
                    <TableCell>GL Amount</TableCell>
                    <TableCell>Reference</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reportData.matched_transactions_list?.map((match, index) => (
                    <TableRow key={index}>
                      <TableCell>{match.bank_transaction?.transaction_date}</TableCell>
                      <TableCell>{match.bank_transaction?.description}</TableCell>
                      <TableCell>
                        <Typography 
                          color={match.bank_transaction?.amount >= 0 ? 'success.main' : 'error.main'}
                          fontWeight="medium"
                        >
                          ${Math.abs(match.bank_transaction?.amount || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography 
                          color={match.gl_entry?.balance >= 0 ? 'success.main' : 'error.main'}
                          fontWeight="medium"
                        >
                          ${Math.abs(match.gl_entry?.balance || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>{match.bank_transaction?.reference}</TableCell>
                      <TableCell>
                        <Chip 
                          label="Matched" 
                          size="small" 
                          color="success" 
                          icon={<CheckCircle />}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
          </AccordionDetails>
        </Accordion>

        {/* Unmatched Transactions */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Typography variant="h6">
              Unmatched Transactions ({reportData.unmatched_transactions || 0})
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Paper>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Reference</TableCell>
                    <TableCell>Type</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reportData.unmatched_transactions_list?.map((tx, index) => (
                    <TableRow key={index}>
                      <TableCell>{tx.transaction_date}</TableCell>
                      <TableCell>{tx.description}</TableCell>
                      <TableCell>
                        <Typography 
                          color={tx.amount >= 0 ? 'success.main' : 'error.main'}
                          fontWeight="medium"
                        >
                          ${Math.abs(tx.amount).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>{tx.reference}</TableCell>
                      <TableCell>
                        <Chip 
                          label={tx.type} 
                          size="small" 
                          color={tx.type === 'bank' ? 'primary' : 'secondary'}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
          </AccordionDetails>
        </Accordion>

        {/* Outstanding Items */}
        {reportData.outstanding_items && reportData.outstanding_items.length > 0 && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6">
                Outstanding Items ({reportData.outstanding_items.length})
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Paper>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Type</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {reportData.outstanding_items.map((item, index) => (
                      <TableRow key={index}>
                        <TableCell>{item.type}</TableCell>
                        <TableCell>{item.description}</TableCell>
                        <TableCell>
                          <Typography fontWeight="medium">
                            ${Math.abs(item.amount).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>{item.date}</TableCell>
                        <TableCell>
                          <Chip 
                            label={item.status} 
                            size="small" 
                            color={item.status === 'cleared' ? 'success' : 'warning'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Paper>
            </AccordionDetails>
          </Accordion>
        )}

        {/* Reconciliation Notes */}
        {reportData.notes && (
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Reconciliation Notes
              </Typography>
              <Typography variant="body1">
                {reportData.notes}
              </Typography>
            </CardContent>
          </Card>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button 
          variant="outlined" 
          startIcon={<Print />}
          onClick={handlePrint}
        >
          Print
        </Button>
        <Button 
          variant="contained" 
          startIcon={<Download />}
          onClick={handleDownloadPDF}
        >
          Download PDF
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ReconciliationReportDialog;










