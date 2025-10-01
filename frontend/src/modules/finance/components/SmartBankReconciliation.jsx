import React, { useState, useEffect, useMemo } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Autocomplete, SpeedDial, SpeedDialAction, SpeedDialIcon,
  TablePagination, TableSortLabel, InputAdornment, OutlinedInput, FormHelperText, Collapse, List, ListItem, ListItemText, ListItemIcon,
  Checkbox, FormControlLabel, FormGroup, Badge, Avatar, Divider, Accordion, AccordionSummary, AccordionDetails,
  Slider, Switch, Rating, ToggleButton, ToggleButtonGroup, Skeleton, Backdrop, Modal, Fade, Grow, Zoom, Slide
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb,
  CloudUpload, Description, ReceiptLong, PaymentOutlined, ScheduleSend, AutoFixHigh, SmartToy, QrCode, CameraAlt,
  Email, Send, CreditCard, AccountBalanceWallet as WalletIcon, TrendingUp as TrendingUpIcon, CalendarToday,
  Timeline as TimelineIcon, ShowChart as ShowChartIcon, TrendingUp as TrendingUpIcon2, CompareArrows, ScatterPlot,
  AccountBalance as BankIcon, Sync, CompareArrows as CompareIcon, CheckCircle as CheckIcon, Warning as WarningIcon,
  Error as ErrorIcon, Info as InfoIcon, Schedule as ScheduleIcon, CalendarToday as CalendarIcon,
  Notifications as NotificationsIcon, Download as DownloadIcon, Upload as UploadIcon, CloudSync, AutoFixHigh as AutoFixIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import ReconciliationWizard from './ReconciliationWizard';
import ReconciliationReportDialog from './ReconciliationReportDialog';

const SmartBankReconciliation = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectedReconciliation, setSelectedReconciliation] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [matchingDialogOpen, setMatchingDialogOpen] = useState(false);
  const [discrepancyDialogOpen, setDiscrepancyDialogOpen] = useState(false);
  const [wizardOpen, setWizardOpen] = useState(false);
  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const [selectedReportSession, setSelectedReportSession] = useState(null);
  const [filterBank, setFilterBank] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPaymentMethod, setFilterPaymentMethod] = useState('all');
  const [filterBankAccount, setFilterBankAccount] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('reconciliation_date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Data hooks
  const { data: reconciliationSessions, loading: reconciliationLoading, error: reconciliationError, refresh: refreshSessions } = useRealTimeData('/api/finance/reconciliation-sessions');
  const { data: bankTransactions, loading: transactionsLoading, error: transactionsError, refresh: refreshTransactions } = useRealTimeData('/api/finance/bank-transactions');
  const { data: unreconciledGlEntries, loading: glLoading, error: glError, refresh: refreshGlEntries } = useRealTimeData('/api/finance/unreconciled-gl-entries');
  const { data: paymentMethods, loading: paymentMethodsLoading } = useRealTimeData('/api/finance/payment-methods');
  const { data: bankAccounts, loading: bankAccountsLoading } = useRealTimeData('/api/finance/bank-accounts');

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!reconciliationSessions) return {};
    
    const totalSessions = reconciliationSessions.length;
    const completedSessions = reconciliationSessions.filter(session => session.status === 'completed').length;
    const pendingSessions = reconciliationSessions.filter(session => session.status === 'pending').length;
    const inProgressSessions = reconciliationSessions.filter(session => session.status === 'in_progress').length;
    
    const totalDifference = reconciliationSessions.reduce((sum, session) => sum + (session.difference || 0), 0);
    const totalOutstandingDeposits = reconciliationSessions.reduce((sum, session) => sum + (session.outstanding_deposits || 0), 0);
    const totalOutstandingChecks = reconciliationSessions.reduce((sum, session) => sum + (session.outstanding_checks || 0), 0);
    
    const lastReconciliation = reconciliationSessions.sort((a, b) => new Date(b.statement_date) - new Date(a.statement_date))[0];
    const daysSinceLastReconciliation = lastReconciliation ? Math.ceil((new Date() - new Date(lastReconciliation.statement_date)) / (1000 * 60 * 60 * 24)) : 0;

    // Bank account analysis
    const bankAccountStats = {};
    reconciliationSessions.forEach(session => {
      const account = session.bank_account_name || 'Unknown';
      if (!bankAccountStats[account]) {
        bankAccountStats[account] = { count: 0, totalDifference: 0 };
      }
      bankAccountStats[account].count++;
      bankAccountStats[account].totalDifference += session.difference || 0;
    });

    return {
      totalSessions,
      completedSessions,
      pendingSessions,
      inProgressSessions,
      totalDifference,
      totalOutstandingDeposits,
      totalOutstandingChecks,
      daysSinceLastReconciliation,
      bankAccountStats
    };
  }, [reconciliationSessions]);

  // Filter and sort reconciliation sessions
  const filteredReconciliations = useMemo(() => {
    if (!reconciliationSessions) return [];
    
    let filtered = reconciliationSessions.filter(session => {
      const matchesBank = filterBank === 'all' || session.bank_account_name === filterBank;
      const matchesStatus = filterStatus === 'all' || session.status === filterStatus;
      const matchesPaymentMethod = filterPaymentMethod === 'all' || session.payment_method === filterPaymentMethod;
      const matchesBankAccount = filterBankAccount === 'all' || session.bank_account_id === filterBankAccount;
      const matchesSearch = (session.bank_account_name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                           (session.statement_date?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                           (session.status?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                           (session.notes?.toLowerCase() || '').includes(searchTerm.toLowerCase());
      return matchesBank && matchesStatus && matchesPaymentMethod && matchesBankAccount && matchesSearch;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortBy === 'statement_date') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      } else if (typeof aValue === 'string') {
        aValue = (aValue || '').toLowerCase();
        bValue = (bValue || '').toLowerCase();
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [reconciliationSessions, filterBank, filterStatus, filterPaymentMethod, filterBankAccount, searchTerm, sortBy, sortOrder]);

  const handleSort = (property) => {
    const isAsc = sortBy === property && sortOrder === 'asc';
    setSortOrder(isAsc ? 'desc' : 'asc');
    setSortBy(property);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'reconciled': return 'success';
      case 'pending': return 'warning';
      case 'discrepancy': return 'error';
      case 'in_progress': return 'info';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'reconciled': return <CheckIcon />;
      case 'pending': return <ScheduleIcon />;
      case 'discrepancy': return <WarningIcon />;
      case 'in_progress': return <Sync />;
      default: return <InfoIcon />;
    }
  };

  const renderReconciliationMetrics = () => (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)',
          borderRadius: 3,
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(102, 126, 234, 0.4)'
          },
          transition: 'all 0.3s ease'
        }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h3" component="div" fontWeight="bold">
                  {metrics.totalSessions || 0}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Total Sessions
                </Typography>
              </Box>
              <BankIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ 
          background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
          color: 'white',
          boxShadow: '0 8px 32px rgba(17, 153, 142, 0.3)',
          borderRadius: 3,
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(17, 153, 142, 0.4)'
          },
          transition: 'all 0.3s ease'
        }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h3" component="div" fontWeight="bold">
                  {metrics.completedSessions || 0}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Completed
                </Typography>
              </Box>
              <CheckIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ 
          background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          color: 'white',
          boxShadow: '0 8px 32px rgba(240, 147, 251, 0.3)',
          borderRadius: 3,
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(240, 147, 251, 0.4)'
          },
          transition: 'all 0.3s ease'
        }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h3" component="div" fontWeight="bold">
                  {metrics.pendingSessions || 0}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Pending
                </Typography>
              </Box>
              <ScheduleIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ 
          background: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
          color: 'white',
          boxShadow: '0 8px 32px rgba(255, 154, 158, 0.3)',
          borderRadius: 3,
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(255, 154, 158, 0.4)'
          },
          transition: 'all 0.3s ease'
        }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h3" component="div" fontWeight="bold">
                  ${(metrics.totalDifference || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2" sx={{ opacity: 0.9 }}>
                  Difference
                </Typography>
              </Box>
              <WarningIcon sx={{ fontSize: 48, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderReconciliationTable = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h5" fontWeight="bold" gutterBottom>
              Bank Reconciliation
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Match your bank statements with accounting records
            </Typography>
          </Box>
          <Box display="flex" gap={2} alignItems="center">
            <Button 
              variant="outlined" 
              startIcon={<Sync />}
              sx={{ 
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 500,
                px: 2,
                py: 1,
                borderColor: 'primary.main',
                color: 'primary.main',
                '&:hover': {
                  borderColor: 'primary.dark',
                  backgroundColor: 'primary.50'
                }
              }}
            >
              Sync Accounts
            </Button>
            <Button 
              variant="contained" 
              startIcon={<Add />}
              onClick={() => setWizardOpen(true)}
              sx={{ 
                borderRadius: 2,
                textTransform: 'none',
                fontWeight: 600,
                px: 3,
                py: 1.5,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                  boxShadow: '0 6px 20px rgba(102, 126, 234, 0.6)',
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.3s ease'
              }}
            >
              Start New Reconciliation
            </Button>
            <TextField
              size="small"
              placeholder="Search reconciliations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Bank</InputLabel>
              <Select
                value={filterBank}
                onChange={(e) => setFilterBank(e.target.value)}
                label="Bank"
              >
                <MenuItem value="all">All Banks</MenuItem>
                <MenuItem value="Chase Bank">Chase Bank</MenuItem>
                <MenuItem value="Bank of America">Bank of America</MenuItem>
                <MenuItem value="Wells Fargo">Wells Fargo</MenuItem>
                <MenuItem value="Citibank">Citibank</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                label="Status"
              >
                <MenuItem value="all">All Status</MenuItem>
                <MenuItem value="reconciled">Reconciled</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="discrepancy">Discrepancy</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 140 }}>
              <InputLabel>Payment Method</InputLabel>
              <Select
                value={filterPaymentMethod}
                onChange={(e) => setFilterPaymentMethod(e.target.value)}
                label="Payment Method"
                disabled={paymentMethodsLoading}
              >
                <MenuItem value="all">All Methods</MenuItem>
                {paymentMethods && paymentMethods.map((method) => (
                  <MenuItem key={method.id} value={method.name}>
                    {method.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 140 }}>
              <InputLabel>Bank Account</InputLabel>
              <Select
                value={filterBankAccount}
                onChange={(e) => setFilterBankAccount(e.target.value)}
                label="Bank Account"
                disabled={bankAccountsLoading}
              >
                <MenuItem value="all">All Accounts</MenuItem>
                {bankAccounts && bankAccounts.map((account) => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.account_name} ({account.account_type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </Box>

        {reconciliationLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={60} />
            ))}
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'bank_name'}
                        direction={sortBy === 'bank_name' ? sortOrder : 'asc'}
                        onClick={() => handleSort('bank_name')}
                      >
                        Bank Account
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>Account Number</TableCell>
                    <TableCell>Payment Method</TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'total_amount'}
                        direction={sortBy === 'total_amount' ? sortOrder : 'asc'}
                        onClick={() => handleSort('total_amount')}
                      >
                        Statement Balance
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>Ledger Balance</TableCell>
                    <TableCell>Difference</TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'reconciliation_date'}
                        direction={sortBy === 'reconciliation_date' ? sortOrder : 'asc'}
                        onClick={() => handleSort('reconciliation_date')}
                      >
                        Reconciliation Date
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredReconciliations.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                        <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
                          <AccountBalance sx={{ fontSize: 48, color: 'text.secondary' }} />
                          <Typography variant="h6" color="text.secondary">
                            No Bank Reconciliations Found
                          </Typography>
                          <Typography variant="body2" color="text.secondary" textAlign="center">
                            Bank reconciliation records will appear here once they are created.<br />
                            Start by importing bank statements or creating manual reconciliations.
                          </Typography>
                          <Button 
                            variant="contained" 
                            startIcon={<Add />}
                            sx={{ mt: 2 }}
                            onClick={() => {/* TODO: Add create reconciliation dialog */}}
                          >
                            Create First Reconciliation
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredReconciliations
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                      .map((session) => {
                      return (
                        <TableRow key={session.id} hover>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                                <BankIcon />
                              </Avatar>
                              <Box>
                                <Typography variant="body2" fontWeight="medium">
                                  {session.bank_account_name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {session.statement_date}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {session.id}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={session.status || 'N/A'} 
                              size="small" 
                              variant="outlined"
                              color={session.status === 'pending' ? 'warning' : session.status === 'completed' ? 'success' : 'default'}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              ${(session.statement_balance || 0).toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              ${(session.book_balance || 0).toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography 
                              variant="body2" 
                              fontWeight="medium"
                              color={session.difference === 0 ? 'success.main' : 'error.main'}
                            >
                              ${(session.difference || 0).toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {session.statement_date}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={session.status} 
                              color={getStatusColor(session.status)}
                              size="small"
                              icon={getStatusIcon(session.status)}
                            />
                          </TableCell>
                          <TableCell>
                            <Box display="flex" gap={0.5}>
                              <Tooltip title="View Details">
                                <IconButton 
                                  size="small"
                                  onClick={() => {
                                    setSelectedReconciliation(session);
                                    setDetailViewOpen(true);
                                  }}
                                >
                                  <Visibility fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Auto Match">
                                <IconButton 
                                  size="small"
                                  onClick={() => setMatchingDialogOpen(true)}
                                >
                                  <AutoFixIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Resolve Discrepancy">
                                <IconButton 
                                  size="small"
                                  onClick={() => setDiscrepancyDialogOpen(true)}
                                >
                                  <CompareIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Generate Report">
                                <IconButton 
                                  size="small"
                                  onClick={() => {
                                    setSelectedReportSession(session);
                                    setReportDialogOpen(true);
                                  }}
                                >
                                  <Download fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </TableContainer>
            
            <TablePagination
              component="div"
              count={filteredReconciliations.length}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
            />
          </>
        )}
      </CardContent>
    </Card>
  );

  const renderBankStatements = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Recent Bank Statements</Typography>
        {transactionsLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={80} />
            ))}
          </Box>
        ) : (
          <List>
            {bankTransactions?.slice(0, 5).map((statement) => (
              <ListItem key={statement.id} divider>
                <ListItemIcon>
                  <BankIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={statement.bank_name}
                  secondary={
                    <span>
                      <span style={{ display: 'block', fontSize: '0.875rem' }}>
                        Statement Date: {new Date(statement.statement_date).toLocaleDateString()}
                      </span>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'rgba(0, 0, 0, 0.6)' }}>
                        Account: {statement.account_number}
                      </span>
                    </span>
                  }
                />
                <Box display="flex" flexDirection="column" alignItems="flex-end">
                  <Typography variant="body2" fontWeight="medium">
                    ${(statement.ending_balance || 0).toLocaleString()}
                  </Typography>
                  <Chip 
                    label={statement.status} 
                    color={statement.status === 'processed' ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );

  const renderDiscrepancyAnalysis = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Discrepancy Analysis</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box textAlign="center" p={2}>
              <Typography variant="h4" color="error.main">
                {metrics.discrepancies || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Open Discrepancies
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box textAlign="center" p={2}>
              <Typography variant="h4" color="warning.main">
                {metrics.daysSinceLastReconciliation || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Days Since Last Reconciliation
              </Typography>
            </Box>
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="subtitle2" mb={1}>Common Discrepancy Types</Typography>
        <List dense>
          <ListItem>
            <ListItemIcon>
              <WarningIcon color="warning" />
            </ListItemIcon>
            <ListItemText
              primary="Timing Differences"
              secondary="Transactions recorded in different periods"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <ErrorIcon color="error" />
            </ListItemIcon>
            <ListItemText
              primary="Data Entry Errors"
              secondary="Incorrect amounts or dates entered"
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <InfoIcon color="info" />
            </ListItemIcon>
            <ListItemText
              primary="Bank Charges"
              secondary="Fees not yet recorded in ledger"
            />
          </ListItem>
        </List>
      </CardContent>
    </Card>
  );

  const renderPaymentMethodAnalysis = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Payment Method Analysis</Typography>
        <Box display="flex" flexDirection="column" gap={1}>
          {metrics.paymentMethodStats && Object.keys(metrics.paymentMethodStats).length > 0 ? (
            Object.entries(metrics.paymentMethodStats).map(([method, stats]) => (
              <Box key={method} display="flex" justifyContent="space-between" alignItems="center" p={1} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                <Box>
                  <Typography variant="body2" fontWeight="medium">
                    {method}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {stats.count} transactions
                  </Typography>
                </Box>
                <Typography variant="body2" fontWeight="medium">
                  ${stats.totalAmount.toLocaleString()}
                </Typography>
              </Box>
            ))
          ) : (
            <Typography variant="body2" color="text.secondary">
              No payment method data available
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );

  const renderAutoMatching = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Auto-Matching Suggestions</Typography>
        <Box display="flex" flexDirection="column" gap={2}>
          <Alert severity="info">
            <Typography variant="body2">
              AI-powered matching suggests potential matches between bank transactions and ledger entries.
            </Typography>
          </Alert>
          
          <Box display="flex" gap={1}>
            <Button 
              variant="contained" 
              startIcon={<AutoFixIcon />}
              onClick={() => setMatchingDialogOpen(true)}
            >
              Run Auto-Matching
            </Button>
            <Button 
              variant="outlined" 
              startIcon={<CloudSync />}
            >
              Sync Bank Feed
            </Button>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Professional Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom sx={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Bank Reconciliation Center
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 600 }}>
          Streamline your bank reconciliation process with automated matching, 
          real-time synchronization, and comprehensive reporting.
        </Typography>
      </Box>
      
      {renderReconciliationMetrics()}
      
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          {renderReconciliationTable()}
        </Grid>
        <Grid item xs={12} lg={4}>
          <Box display="flex" flexDirection="column" gap={3}>
            {renderBankStatements()}
            {renderDiscrepancyAnalysis()}
            {renderPaymentMethodAnalysis()}
            {renderAutoMatching()}
          </Box>
        </Grid>
      </Grid>

      {/* Detail View Modal */}
      <Dialog 
        open={detailViewOpen} 
        onClose={() => setDetailViewOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Reconciliation Details - {selectedReconciliation?.bank_name}
        </DialogTitle>
        <DialogContent>
          {selectedReconciliation && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Account Information</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Bank Name" 
                      secondary={selectedReconciliation.bank_name} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Account Number" 
                      secondary={selectedReconciliation.account_number} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Account Type" 
                      secondary={selectedReconciliation.account_type} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Reconciliation Date" 
                      secondary={new Date(selectedReconciliation.reconciliation_date).toLocaleDateString()} 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Balance Information</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Statement Balance" 
                      secondary={`$${(selectedReconciliation.statement_balance || 0).toLocaleString()}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Ledger Balance" 
                      secondary={`$${(selectedReconciliation.ledger_balance || 0).toLocaleString()}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Difference" 
                      secondary={`$${((selectedReconciliation.statement_balance || 0) - (selectedReconciliation.ledger_balance || 0)).toLocaleString()}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Status" 
                      secondary={selectedReconciliation.status} 
                    />
                  </ListItem>
                </List>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailViewOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
      
      <ReconciliationWizard 
        open={wizardOpen}
        onClose={() => setWizardOpen(false)}
        onComplete={() => {
          setSnackbar({ open: true, message: 'Reconciliation completed successfully!', severity: 'success' });
          // Refresh data
          refreshSessions?.();
          refreshTransactions?.();
        }}
      />
      
      <ReconciliationReportDialog 
        open={reportDialogOpen}
        onClose={() => setReportDialogOpen(false)}
        reconciliationSession={selectedReportSession}
      />
    </Box>
  );
};

export default SmartBankReconciliation;

