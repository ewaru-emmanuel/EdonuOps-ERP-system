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
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, LocalTaxi, AccountBalanceWallet,
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

const SmartBankReconciliation = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectedReconciliation, setSelectedReconciliation] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [matchingDialogOpen, setMatchingDialogOpen] = useState(false);
  const [discrepancyDialogOpen, setDiscrepancyDialogOpen] = useState(false);
  const [filterBank, setFilterBank] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('reconciliation_date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Data hooks
  const { data: reconciliations, loading: reconciliationLoading, error: reconciliationError } = useRealTimeData('/api/finance/bank-reconciliations');
  const { data: bankStatements, loading: statementsLoading, error: statementsError } = useRealTimeData('/api/finance/bank-statements');
  const { data: ledgerEntries, loading: ledgerLoading, error: ledgerError } = useRealTimeData('/api/finance/ledger-entries');

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!reconciliations) return {};
    
    const totalReconciliations = reconciliations.length;
    const reconciledAmount = reconciliations.filter(rec => rec.status === 'reconciled').reduce((sum, rec) => sum + (rec.total_amount || 0), 0);
    const pendingReconciliations = reconciliations.filter(rec => rec.status === 'pending').length;
    const discrepancies = reconciliations.filter(rec => rec.status === 'discrepancy').length;
    
    const totalDiscrepancyAmount = reconciliations.filter(rec => rec.status === 'discrepancy').reduce((sum, rec) => sum + (rec.discrepancy_amount || 0), 0);
    
    const lastReconciliation = reconciliations.sort((a, b) => new Date(b.reconciliation_date) - new Date(a.reconciliation_date))[0];
    const daysSinceLastReconciliation = lastReconciliation ? Math.ceil((new Date() - new Date(lastReconciliation.reconciliation_date)) / (1000 * 60 * 60 * 24)) : 0;

    return {
      totalReconciliations,
      reconciledAmount,
      pendingReconciliations,
      discrepancies,
      totalDiscrepancyAmount,
      daysSinceLastReconciliation
    };
  }, [reconciliations]);

  // Filter and sort reconciliations
  const filteredReconciliations = useMemo(() => {
    if (!reconciliations) return [];
    
    let filtered = reconciliations.filter(rec => {
      const matchesBank = filterBank === 'all' || rec.bank_name === filterBank;
      const matchesStatus = filterStatus === 'all' || rec.status === filterStatus;
      const matchesSearch = rec.bank_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           rec.account_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           rec.reference_number?.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesBank && matchesStatus && matchesSearch;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortBy === 'reconciliation_date') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      } else if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [reconciliations, filterBank, filterStatus, searchTerm, sortBy, sortOrder]);

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
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  {metrics.totalReconciliations || 0}
                </Typography>
                <Typography variant="body2">Total Reconciliations</Typography>
              </Box>
              <BankIcon sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  ${(metrics.reconciledAmount || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Reconciled Amount</Typography>
              </Box>
              <CheckIcon sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'warning.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  {metrics.pendingReconciliations || 0}
                </Typography>
                <Typography variant="body2">Pending</Typography>
              </Box>
              <ScheduleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'error.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  ${(metrics.totalDiscrepancyAmount || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Discrepancies</Typography>
              </Box>
              <WarningIcon sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderReconciliationTable = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Bank Reconciliations</Typography>
          <Box display="flex" gap={1}>
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
                  {filteredReconciliations
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((reconciliation) => {
                      const difference = (reconciliation.statement_balance || 0) - (reconciliation.ledger_balance || 0);
                      return (
                        <TableRow key={reconciliation.id} hover>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                                <BankIcon />
                              </Avatar>
                              <Box>
                                <Typography variant="body2" fontWeight="medium">
                                  {reconciliation.bank_name}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {reconciliation.account_type}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {reconciliation.account_number}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              ${(reconciliation.statement_balance || 0).toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              ${(reconciliation.ledger_balance || 0).toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography 
                              variant="body2" 
                              fontWeight="medium"
                              color={difference === 0 ? 'success.main' : 'error.main'}
                            >
                              ${difference.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {new Date(reconciliation.reconciliation_date).toLocaleDateString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={reconciliation.status} 
                              color={getStatusColor(reconciliation.status)}
                              size="small"
                              icon={getStatusIcon(reconciliation.status)}
                            />
                          </TableCell>
                          <TableCell>
                            <Box display="flex" gap={0.5}>
                              <Tooltip title="View Details">
                                <IconButton 
                                  size="small"
                                  onClick={() => {
                                    setSelectedReconciliation(reconciliation);
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
                              <Tooltip title="Download Report">
                                <IconButton size="small">
                                  <Download fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      );
                    })}
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
        {statementsLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={80} />
            ))}
          </Box>
        ) : (
          <List>
            {bankStatements?.slice(0, 5).map((statement) => (
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
      <Typography variant="h4" gutterBottom>
        Bank Reconciliation
      </Typography>
      
      {renderReconciliationMetrics()}
      
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          {renderReconciliationTable()}
        </Grid>
        <Grid item xs={12} lg={4}>
          <Box display="flex" flexDirection="column" gap={3}>
            {renderBankStatements()}
            {renderDiscrepancyAnalysis()}
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
    </Box>
  );
};

export default SmartBankReconciliation;

