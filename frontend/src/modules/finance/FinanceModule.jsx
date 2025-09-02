import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Tab, Tabs, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Divider, List, ListItem, ListItemText, ListItemIcon, Accordion, AccordionSummary, AccordionDetails, Switch, FormControlLabel, Badge, CircularProgress, Avatar, SpeedDial, SpeedDialAction, SpeedDialIcon,
  Autocomplete, Slider, Rating, ToggleButton, ToggleButtonGroup, Skeleton, Backdrop, Modal, Fade, Grow, Zoom, Slide, Collapse, ListItemButton, ListItemAvatar,
  InputAdornment, OutlinedInput, InputBase, FormHelperText, FormLabel, RadioGroup, Radio, Checkbox, FormGroup,
  Breadcrumbs, Link, Stepper, Step, StepLabel, StepContent, MobileStepper, CardActions, CardMedia, CardHeader, CardActionArea, ExpansionPanel, ExpansionPanelSummary, ExpansionPanelDetails,
  Drawer, AppBar, Toolbar, Menu, Popover, Popper, ClickAwayListener, MenuList, ListItemSecondaryAction, ListSubheader,
  TablePagination, TableSortLabel, TableFooter, DialogContentText
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  AccountBalance as AccountBalanceIcon,
  Receipt as ReceiptIcon,
  Payment as PaymentIcon,
  Business as BusinessIcon,
  Assessment as AssessmentIcon,
  LocalTaxi as TaxIcon,
  AccountBalanceWallet as BankIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  AttachMoney as MoneyIcon,
  Schedule as ScheduleIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  ShowChart as LineChartIcon,
  Security as SecurityIcon,
  Lock as LockIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  FilterList as FilterIcon,
  Search as SearchIcon,
  Timeline as TimelineIcon,
  CurrencyExchange as CurrencyIcon,
  Audit as AuditIcon,
  Compliance as ComplianceIcon
} from '@mui/icons-material';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';
import SmartDashboard from './components/SmartDashboard';
import SmartGeneralLedger from './components/SmartGeneralLedger';
import SmartAccountsPayable from './components/SmartAccountsPayable';
import SmartAccountsReceivable from './components/SmartAccountsReceivable';
import SmartBudgeting from './components/SmartBudgeting';
import SmartFixedAssets from './components/SmartFixedAssets';
import SmartTaxManagement from './components/SmartTaxManagement';
import SmartBankReconciliation from './components/SmartBankReconciliation';
import SmartFinancialReports from './components/SmartFinancialReports';
import SmartAuditTrail from './components/SmartAuditTrail';

const FinanceModule = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Form and dialog states
  const [formOpen, setFormOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteItem, setDeleteItem] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedItemType, setSelectedItemType] = useState('');

  // Advanced Finance Data Hooks
  const { data: chartOfAccounts, loading: coaLoading, error: coaError } = useRealTimeData('/api/finance/chart-of-accounts');
  const { data: generalLedger, loading: glLoading, error: glError } = useRealTimeData('/api/finance/general-ledger');
  const { data: accountsPayable, loading: apLoading, error: apError } = useRealTimeData('/api/finance/accounts-payable');
  const { data: accountsReceivable, loading: arLoading, error: arError } = useRealTimeData('/api/finance/accounts-receivable');
  const { data: fixedAssets, loading: assetsLoading, error: assetsError } = useRealTimeData('/api/finance/fixed-assets');
  const { data: budgets, loading: budgetsLoading, error: budgetsError } = useRealTimeData('/api/finance/budgets');
  const { data: taxRecords, loading: taxLoading, error: taxError } = useRealTimeData('/api/finance/tax-records');
  const { data: bankReconciliations, loading: bankLoading, error: bankError } = useRealTimeData('/api/finance/bank-reconciliations');

  // Legacy data for backward compatibility with CRUD functions
  const { 
    data: accounts, 
    loading: accountsLoading, 
    error: accountsError,
    create: createAccount,
    update: updateAccount,
    remove: deleteAccount
  } = useRealTimeData('/api/finance/accounts');
  
  const { 
    data: journalEntries, 
    loading: journalEntriesLoading, 
    error: journalEntriesError,
    create: createJournalEntry,
    update: updateJournalEntry,
    remove: deleteJournalEntry
  } = useRealTimeData('/api/finance/journal-entries');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleAdd = (type) => {
    setEditItem(null);
    setSelectedItemType(type);
    setFormOpen(true);
  };

  const handleEdit = (item, type) => {
    setEditItem(item);
    setSelectedItemType(type);
    setFormOpen(true);
  };

  const handleDelete = (item, type) => {
    setDeleteItem(item);
    setSelectedItemType(type);
    setDeleteDialogOpen(true);
  };

  const handleView = (item, type) => {
    setSelectedItem(item);
    setSelectedItemType(type);
    setDetailViewOpen(true);
  };

  const handleSave = async (formData) => {
    try {
      if (editItem) {
        switch (selectedItemType) {
          case 'account':
            await updateAccount(editItem.id, formData);
            showSnackbar(`Account "${formData.name}" updated successfully`);
            break;
          case 'journal-entry':
            await updateJournalEntry(editItem.id, formData);
            showSnackbar(`Journal Entry "${formData.reference}" updated successfully`);
            break;
          default:
            break;
        }
      } else {
        switch (selectedItemType) {
          case 'account':
            await createAccount(formData);
            showSnackbar(`Account "${formData.name}" created successfully`);
            break;
          case 'journal-entry':
            await createJournalEntry(formData);
            showSnackbar(`Journal Entry "${formData.reference}" created successfully`);
            break;
          default:
            break;
        }
      }
      setFormOpen(false);
      setEditItem(null);
    } catch (error) {
      showSnackbar(`Failed to save ${selectedItemType}: ${error.message}`, 'error');
    }
  };

  const handleConfirmDelete = async () => {
    try {
      switch (selectedItemType) {
        case 'account':
          await deleteAccount(deleteItem.id);
          showSnackbar(`Account "${deleteItem.name}" deleted successfully`);
          break;
        case 'journal-entry':
          await deleteJournalEntry(deleteItem.id);
          showSnackbar(`Journal Entry "${deleteItem.reference}" deleted successfully`);
          break;
        default:
          break;
      }
      setDeleteDialogOpen(false);
      setDeleteItem(null);
    } catch (error) {
      showSnackbar(`Failed to delete ${selectedItemType}: ${error.message}`, 'error');
    }
  };

  // Calculate advanced financial metrics
  const calculateMetrics = () => {
    const totalAssets = fixedAssets?.reduce((sum, asset) => sum + (asset.current_value || 0), 0) || 0;
    const totalLiabilities = accountsPayable?.reduce((sum, ap) => sum + (ap.outstanding_amount || 0), 0) || 0;
    const totalEquity = totalAssets - totalLiabilities;
    const totalRevenue = generalLedger?.filter(entry => entry.account_type === 'Revenue')
      .reduce((sum, entry) => sum + (entry.credit_amount || 0), 0) || 0;
    const totalExpenses = generalLedger?.filter(entry => entry.account_type === 'Expense')
      .reduce((sum, entry) => sum + (entry.debit_amount || 0), 0) || 0;
    const netIncome = totalRevenue - totalExpenses;

    return {
      totalAssets,
      totalLiabilities,
      totalEquity,
      totalRevenue,
      totalExpenses,
      netIncome,
      accountsReceivable: accountsReceivable?.reduce((sum, ar) => sum + (ar.outstanding_amount || 0), 0) || 0,
      accountsPayable: accountsPayable?.reduce((sum, ap) => sum + (ap.outstanding_amount || 0), 0) || 0,
      pendingReconciliations: bankReconciliations?.filter(rec => rec.status === 'pending').length || 0,
      overdueInvoices: accountsReceivable?.filter(ar => ar.status === 'overdue').length || 0
    };
  };

  const metrics = calculateMetrics();

  // Legacy metrics for backward compatibility
  const financeMetrics = {
    totalAccounts: accounts?.length || 0,
    totalJournalEntries: journalEntries?.length || 0,
    totalDebits: journalEntries?.reduce((sum, entry) => sum + (entry?.total_debit || 0), 0) || 0,
    totalCredits: journalEntries?.reduce((sum, entry) => sum + (entry?.total_credit || 0), 0) || 0
  };

  const renderDashboardTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Financial Dashboard</Typography>
      
      {/* Key Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Total Assets
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"}>
                    ${metrics.totalAssets.toLocaleString()}
                  </Typography>
                </Box>
                <AccountBalanceIcon color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Net Income
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} color={metrics.netIncome >= 0 ? 'success.main' : 'error.main'}>
                    ${metrics.netIncome.toLocaleString()}
                  </Typography>
                </Box>
                <TrendingUpIcon color={metrics.netIncome >= 0 ? 'success' : 'error'} sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Accounts Receivable
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"}>
                    ${metrics.accountsReceivable.toLocaleString()}
                  </Typography>
                </Box>
                <ReceiptIcon color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography color="textSecondary" gutterBottom variant="body2">
                    Accounts Payable
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"}>
                    ${metrics.accountsPayable.toLocaleString()}
                  </Typography>
                </Box>
                <PaymentIcon color="warning" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Quick Actions</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Button
                    variant="outlined"
                    startIcon={<AddIcon />}
                    onClick={() => handleAdd('general-ledger')}
                    fullWidth
                  >
                    New Journal Entry
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    variant="outlined"
                    startIcon={<ReceiptIcon />}
                    onClick={() => handleAdd('accounts-receivable')}
                    fullWidth
                  >
                    Create Invoice
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    variant="outlined"
                    startIcon={<PaymentIcon />}
                    onClick={() => handleAdd('accounts-payable')}
                    fullWidth
                  >
                    Record Bill
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    variant="outlined"
                    startIcon={<AssessmentIcon />}
                    onClick={() => handleAdd('budget')}
                    fullWidth
                  >
                    Create Budget
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Alerts & Notifications</Typography>
              <Box>
                {metrics.overdueInvoices > 0 && (
                  <Alert severity="error" sx={{ mb: 1 }}>
                    {metrics.overdueInvoices} overdue invoices require attention
                  </Alert>
                )}
                {metrics.pendingReconciliations > 0 && (
                  <Alert severity="warning" sx={{ mb: 1 }}>
                    {metrics.pendingReconciliations} bank reconciliations pending
                  </Alert>
                )}
                {metrics.accountsPayable > 10000 && (
                  <Alert severity="info" sx={{ mb: 1 }}>
                    High accounts payable balance - consider payment prioritization
                  </Alert>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderGeneralLedgerTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">General Ledger</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => showSnackbar('GL Export started')}
            sx={{ mr: 1 }}
          >
            Export GL
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('general-ledger')}
          >
            Add Journal Entry
          </Button>
        </Box>
      </Box>

      {glLoading && <LinearProgress />}

      {glError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {glError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Reference</TableCell>
              <TableCell>Account</TableCell>
              <TableCell>Description</TableCell>
              <TableCell align="right">Debit</TableCell>
              <TableCell align="right">Credit</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {generalLedger?.map((entry, index) => (
              <TableRow key={entry.id || `gl-${index}`}>
                <TableCell>{entry.entry_date ? new Date(entry.entry_date).toLocaleDateString() : ''}</TableCell>
                <TableCell>{entry.reference || ''}</TableCell>
                <TableCell>{entry.account_name || ''}</TableCell>
                <TableCell>{entry.description || ''}</TableCell>
                <TableCell align="right">${entry.debit_amount || 0}</TableCell>
                <TableCell align="right">${entry.credit_amount || 0}</TableCell>
                <TableCell>
                  <Chip
                    label={entry.status || 'posted'}
                    color={entry.status === 'posted' ? 'success' : 'warning'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(entry, 'general-ledger')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(entry, 'general-ledger')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(entry, 'general-ledger')} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderAccountsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Chart of Accounts</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('account')}
        >
          Add Account
        </Button>
      </Box>

      {accountsLoading && <LinearProgress />}
      
      {accountsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {accountsError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Code</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Parent</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {accounts.map((account, index) => (
              <TableRow key={account.id || `account-${index}`}>
                <TableCell>{account.code}</TableCell>
                <TableCell>{account.name}</TableCell>
                <TableCell>
                  <Chip
                    label={account.type || 'asset'}
                    color={account.type === 'asset' ? 'primary' : account.type === 'liability' ? 'error' : 'success'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{account.parent_id || 'None'}</TableCell>
                <TableCell>
                  <Chip
                    label={account.is_active ? 'Active' : 'Inactive'}
                    color={account.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(account, 'account')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(account, 'account')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(account, 'account')} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderJournalEntriesTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Journal Entries</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('journal-entry')}
        >
          Add Journal Entry
        </Button>
      </Box>

      {journalEntriesLoading && <LinearProgress />}
      
      {journalEntriesError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {journalEntriesError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Reference</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Total Debit</TableCell>
              <TableCell>Total Credit</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {journalEntries.map((entry, index) => (
              <TableRow key={entry.id || `entry-${index}`}>
                <TableCell>
                                      {entry.entry_date ? new Date(entry.entry_date).toLocaleDateString() : ''}
                </TableCell>
                <TableCell>{entry.reference || ''}</TableCell>
                <TableCell>{entry.description || ''}</TableCell>
                <TableCell>
                  <Chip
                    label={entry.status || 'draft'}
                    color={entry.status === 'posted' ? 'success' : 'warning'}
                    size="small"
                  />
                </TableCell>
                <TableCell>${entry.total_debit || 0}</TableCell>
                <TableCell>${entry.total_credit || 0}</TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(entry, 'journal-entry')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(entry, 'journal-entry')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(entry, 'journal-entry')} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderAccountsPayableTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Accounts Payable</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Manage vendor invoices, payments, and cash flow. Track outstanding amounts and payment schedules.
      </Typography>
      <Alert severity="info">
        Advanced AP features including vendor management, payment scheduling, and approval workflows are available.
      </Alert>
    </Box>
  );

  const renderAccountsReceivableTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Accounts Receivable</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Manage customer invoices, payments, and credit management. Track outstanding balances and dunning.
      </Typography>
      <Alert severity="info">
        Advanced AR features including customer management, credit limits, and automated dunning are available.
      </Alert>
    </Box>
  );

  const renderFixedAssetsTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Fixed Assets</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Track fixed assets, depreciation, and asset lifecycle management.
      </Typography>
      <Alert severity="info">
        Advanced asset management including depreciation schedules, maintenance tracking, and disposal management are available.
      </Alert>
    </Box>
  );

  const renderBudgetingTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Budgeting & Forecasting</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Create budgets, track variances, and perform financial forecasting.
      </Typography>
      <Alert severity="info">
        Advanced budgeting features including variance analysis, scenario planning, and rolling forecasts are available.
      </Alert>
    </Box>
  );

  const renderTaxManagementTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Tax Management</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Manage tax records, compliance, and filing requirements.
      </Typography>
      <Alert severity="info">
        Advanced tax features including multi-jurisdiction support, automated calculations, and compliance tracking are available.
      </Alert>
    </Box>
  );

  const renderBankReconciliationTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Bank Reconciliation</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Reconcile bank statements with internal records and identify discrepancies.
      </Typography>
      <Alert severity="info">
        Advanced reconciliation features including automated matching, statement import, and discrepancy resolution are available.
      </Alert>
    </Box>
  );

  const renderFinancialReportsTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Financial Reports & Analysis</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Generate comprehensive financial reports including P&L, Balance Sheet, and Cash Flow statements.
      </Typography>
      <Alert severity="info">
        Advanced reporting features including custom reports, drill-down analysis, and automated report scheduling are available.
      </Alert>
    </Box>
  );

  const renderAuditTrailTab = () => (
    <Box>
      <Typography variant="h6" gutterBottom>Audit Trail & Compliance</Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Complete audit trail of all financial transactions and changes for compliance and transparency.
      </Typography>
      <Alert severity="info">
        Advanced audit features including detailed change tracking, compliance reporting, and automated audit alerts are available.
      </Alert>
    </Box>
  );

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      <Typography variant={isMobile ? "h5" : "h4"} gutterBottom>
        Advanced Finance Management
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Enterprise-grade financial management with comprehensive GL, AP, AR, Fixed Assets, Budgeting, Tax Management, and more.
      </Typography>

      {/* Metrics Cards */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Accounts
              </Typography>
              <Typography variant={isMobile ? "h5" : "h4"}>
                {financeMetrics.totalAccounts}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Journal Entries
              </Typography>
              <Typography variant={isMobile ? "h5" : "h4"}>
                {financeMetrics.totalJournalEntries}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Debits
              </Typography>
              <Typography variant={isMobile ? "h5" : "h4"}>
                ${financeMetrics.totalDebits ? financeMetrics.totalDebits.toLocaleString() : ''}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Credits
              </Typography>
              <Typography variant={isMobile ? "h5" : "h4"}>
                ${financeMetrics.totalCredits ? financeMetrics.totalCredits.toLocaleString() : ''}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
        >
          <Tab label="Dashboard" />
          <Tab label="General Ledger" />
          <Tab label="Chart of Accounts" />
          <Tab label="Accounts Payable" />
          <Tab label="Accounts Receivable" />
          <Tab label="Fixed Assets" />
          <Tab label="Budgeting" />
          <Tab label="Tax Management" />
          <Tab label="Bank Reconciliation" />
          <Tab label="Financial Reports" />
          <Tab label="Audit Trail" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && <SmartDashboard isMobile={isMobile} isTablet={isTablet} />}
      {activeTab === 1 && <SmartGeneralLedger isMobile={isMobile} isTablet={isTablet} />}
      {activeTab === 2 && renderAccountsTab()}
      {activeTab === 3 && <SmartAccountsPayable isMobile={isMobile} isTablet={isTablet} />}
      {activeTab === 4 && <SmartAccountsReceivable isMobile={isMobile} isTablet={isTablet} />}
                              {activeTab === 5 && <SmartFixedAssets isMobile={isMobile} isTablet={isTablet} />}
                        {activeTab === 6 && <SmartBudgeting isMobile={isMobile} isTablet={isTablet} />}
                        {activeTab === 7 && <SmartTaxManagement isMobile={isMobile} isTablet={isTablet} />}
                                                {activeTab === 8 && <SmartBankReconciliation isMobile={isMobile} isTablet={isTablet} />}
                        {activeTab === 9 && <SmartFinancialReports isMobile={isMobile} isTablet={isTablet} />}
                        {activeTab === 10 && <SmartAuditTrail isMobile={isMobile} isTablet={isTablet} />}

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Detail View Modal */}
      <DetailViewModal
        open={detailViewOpen}
        onClose={() => {
          setDetailViewOpen(false);
          setSelectedItem(null);
          setSelectedItemType('');
        }}
        data={selectedItem}
        type={selectedItemType}
        onEdit={(item) => {
          setDetailViewOpen(false);
          handleEdit(item, selectedItemType);
        }}
        title={`${selectedItemType ? selectedItemType.charAt(0).toUpperCase() + selectedItemType.slice(1) : 'Item'} Details`}
      />

      {/* Improved Form */}
      <ImprovedForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditItem(null);
        }}
        onSave={handleSave}
        data={editItem}
        type={selectedItemType}
        title={selectedItemType ? selectedItemType.charAt(0).toUpperCase() + selectedItemType.slice(1) : 'Item'}
        loading={accountsLoading || journalEntriesLoading}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog 
        open={deleteDialogOpen} 
        onClose={() => setDeleteDialogOpen(false)}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-content"
      >
        <DialogTitle id="delete-dialog-title">Confirm Delete</DialogTitle>
        <DialogContent id="delete-dialog-content">
          <Typography>
            Are you sure you want to delete this {selectedItemType}? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setDeleteDialogOpen(false)}
            aria-label="cancel delete"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmDelete} 
            color="error" 
            variant="contained"
            aria-label="confirm delete"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FinanceModule;