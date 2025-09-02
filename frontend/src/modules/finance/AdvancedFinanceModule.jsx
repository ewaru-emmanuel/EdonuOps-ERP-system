import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, IconButton, Chip, Dialog, DialogTitle, 
  DialogContent, DialogActions, Tab, Tabs, Snackbar, LinearProgress, Tooltip, 
  useMediaQuery, useTheme, TextField, 
  Divider, List, ListItem, ListItemText, ListItemIcon, 
  Switch, FormControlLabel, Badge, CircularProgress, Avatar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  AccountBalance as AccountBalanceIcon,
  Receipt as ReceiptIcon,
  Payment as PaymentIcon,
  AccountBalanceWallet as WalletIcon,
  Business as BusinessIcon,
  Assessment as AssessmentIcon,
  LocalTaxi as TaxIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  AttachMoney as MoneyIcon,
  Schedule as ScheduleIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  ShowChart as LineChartIcon,
  Security as SecurityIcon,
  Lock as LockIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  FilterList as FilterIcon,
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  CurrencyExchange as CurrencyIcon,
  Audit as AuditIcon,
  Compliance as ComplianceIcon
} from '@mui/icons-material';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';

const AdvancedFinanceModule = () => {
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
  const { data: dashboardMetrics, loading: metricsLoading, error: metricsError } = useRealTimeData('/api/finance/dashboard-metrics');

  // Legacy data for backward compatibility
  const { data: accounts } = useRealTimeData('/api/finance/accounts');
  const { data: journalEntries } = useRealTimeData('/api/finance/journal-entries');
  const { data: auditTrail, loading: auditLoading } = useRealTimeData('/api/finance/audit-trail');

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

  // Calculate financial metrics
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

  const tabLabels = [
    'Dashboard',
    'General Ledger',
    'Chart of Accounts',
    'Accounts Payable',
    'Accounts Receivable',
    'Fixed Assets',
    'Budgeting',
    'Tax Management',
    'Bank Reconciliation',
    'Multi-Currency',
    'AI Analytics',
    'Financial Reports',
    'Audit Trail'
  ];

  const renderDashboard = () => (
    <Box>
      <Typography variant="h5" gutterBottom>Financial Dashboard</Typography>
      
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
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <AccountBalanceIcon />
                </Avatar>
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
                <Avatar sx={{ bgcolor: metrics.netIncome >= 0 ? 'success.main' : 'error.main' }}>
                  <TrendingUpIcon />
                </Avatar>
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
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <ReceiptIcon />
                </Avatar>
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
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <PaymentIcon />
                </Avatar>
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
              <List>
                {metrics.overdueInvoices > 0 && (
                  <ListItem>
                    <ListItemIcon>
                      <ErrorIcon color="error" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={`${metrics.overdueInvoices} overdue invoices`}
                      secondary="Requires immediate attention"
                    />
                  </ListItem>
                )}
                {metrics.pendingReconciliations > 0 && (
                  <ListItem>
                    <ListItemIcon>
                      <WarningIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={`${metrics.pendingReconciliations} pending reconciliations`}
                      secondary="Bank statements need reconciliation"
                    />
                  </ListItem>
                )}
                {metrics.accountsPayable > 10000 && (
                  <ListItem>
                    <ListItemIcon>
                      <InfoIcon color="info" />
                    </ListItemIcon>
                    <ListItemText 
                      primary="High accounts payable balance"
                      secondary="Consider payment prioritization"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderGeneralLedger = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">General Ledger</Typography>
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

  const renderChartOfAccounts = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Chart of Accounts</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('chart-of-accounts')}
        >
          Add Account
        </Button>
      </Box>

      {coaLoading && <LinearProgress />}

      {coaError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {coaError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Account Code</TableCell>
              <TableCell>Account Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {chartOfAccounts?.map((account, index) => (
              <TableRow key={account.id || `coa-${index}`}>
                <TableCell>{account.account_code || ''}</TableCell>
                <TableCell>{account.account_name || ''}</TableCell>
                <TableCell>
                  <Chip
                    label={account.account_type || ''}
                    color="primary"
                    size="small"
                  />
                </TableCell>
                <TableCell>{account.account_category || ''}</TableCell>
                <TableCell>
                  <Chip
                    label={account.is_active ? 'Active' : 'Inactive'}
                    color={account.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(account, 'chart-of-accounts')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(account, 'chart-of-accounts')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(account, 'chart-of-accounts')} color="error" size="small">
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

  const renderAccountsPayable = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Accounts Payable</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<ScheduleIcon />}
            onClick={() => showSnackbar('Payment schedule generated')}
            sx={{ mr: 1 }}
          >
            Payment Schedule
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('accounts-payable')}
          >
            Add Invoice
          </Button>
        </Box>
      </Box>

      {apLoading && <LinearProgress />}

      {apError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {apError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Invoice #</TableCell>
              <TableCell>Vendor</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell align="right">Outstanding</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {accountsPayable?.map((ap, index) => (
              <TableRow key={ap.id || `ap-${index}`}>
                <TableCell>{ap.invoice_number || ''}</TableCell>
                <TableCell>{ap.vendor_name || ''}</TableCell>
                <TableCell>{ap.due_date ? new Date(ap.due_date).toLocaleDateString() : ''}</TableCell>
                <TableCell align="right">${ap.total_amount || 0}</TableCell>
                <TableCell align="right">${ap.outstanding_amount || 0}</TableCell>
                <TableCell>
                  <Chip
                    label={ap.status || 'pending'}
                    color={
                      ap.status === 'paid' ? 'success' :
                      ap.status === 'overdue' ? 'error' : 'warning'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(ap, 'accounts-payable')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(ap, 'accounts-payable')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(ap, 'accounts-payable')} color="error" size="small">
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

  const renderAccountsReceivable = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Accounts Receivable</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<NotificationsIcon />}
            onClick={() => showSnackbar('Dunning notices sent')}
            sx={{ mr: 1 }}
          >
            Send Reminders
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('accounts-receivable')}
          >
            Create Invoice
          </Button>
        </Box>
      </Box>

      {arLoading && <LinearProgress />}

      {arError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {arError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Invoice #</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell align="right">Amount</TableCell>
              <TableCell align="right">Outstanding</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {accountsReceivable?.map((ar, index) => (
              <TableRow key={ar.id || `ar-${index}`}>
                <TableCell>{ar.invoice_number || ''}</TableCell>
                <TableCell>{ar.customer_name || ''}</TableCell>
                <TableCell>{ar.due_date ? new Date(ar.due_date).toLocaleDateString() : ''}</TableCell>
                <TableCell align="right">${ar.total_amount || 0}</TableCell>
                <TableCell align="right">${ar.outstanding_amount || 0}</TableCell>
                <TableCell>
                  <Chip
                    label={ar.status || 'pending'}
                    color={
                      ar.status === 'paid' ? 'success' :
                      ar.status === 'overdue' ? 'error' : 'warning'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(ar, 'accounts-receivable')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(ar, 'accounts-receivable')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(ar, 'accounts-receivable')} color="error" size="small">
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

  const renderFixedAssets = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Fixed Assets</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<TimelineIcon />}
            onClick={() => showSnackbar('Depreciation schedule generated')}
            sx={{ mr: 1 }}
          >
            Depreciation
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('fixed-asset')}
          >
            Add Asset
          </Button>
        </Box>
      </Box>

      {assetsLoading && <LinearProgress />}

      {assetsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {assetsError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Asset ID</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Purchase Date</TableCell>
              <TableCell align="right">Purchase Value</TableCell>
              <TableCell align="right">Current Value</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {fixedAssets?.map((asset, index) => (
              <TableRow key={asset.id || `asset-${index}`}>
                <TableCell>{asset.asset_id || ''}</TableCell>
                <TableCell>{asset.asset_name || ''}</TableCell>
                <TableCell>{asset.category || ''}</TableCell>
                <TableCell>{asset.purchase_date ? new Date(asset.purchase_date).toLocaleDateString() : ''}</TableCell>
                <TableCell align="right">${asset.purchase_value || 0}</TableCell>
                <TableCell align="right">${asset.current_value || 0}</TableCell>
                <TableCell>
                  <Chip
                    label={asset.status || 'active'}
                    color={asset.status === 'active' ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(asset, 'fixed-asset')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(asset, 'fixed-asset')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(asset, 'fixed-asset')} color="error" size="small">
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

  const renderBudgeting = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Budgeting & Forecasting</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<BarChartIcon />}
            onClick={() => showSnackbar('Budget variance report generated')}
            sx={{ mr: 1 }}
          >
            Variance Report
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('budget')}
          >
            Create Budget
          </Button>
        </Box>
      </Box>

      {budgetsLoading && <LinearProgress />}

      {budgetsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {budgetsError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Budget Name</TableCell>
              <TableCell>Period</TableCell>
              <TableCell>Department</TableCell>
              <TableCell align="right">Budgeted Amount</TableCell>
              <TableCell align="right">Actual Amount</TableCell>
              <TableCell align="right">Variance</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {budgets?.map((budget, index) => (
              <TableRow key={budget.id || `budget-${index}`}>
                <TableCell>{budget.name || ''}</TableCell>
                <TableCell>{budget.period || ''}</TableCell>
                <TableCell>{budget.department || ''}</TableCell>
                <TableCell align="right">${budget.budgeted_amount || 0}</TableCell>
                <TableCell align="right">${budget.actual_amount || 0}</TableCell>
                <TableCell align="right">
                  <Chip
                    label={`${((budget.actual_amount - budget.budgeted_amount) / budget.budgeted_amount * 100).toFixed(1)}%`}
                    color={
                      Math.abs(budget.actual_amount - budget.budgeted_amount) / budget.budgeted_amount > 0.1 ? 'error' : 'success'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={budget.status || 'active'}
                    color={budget.status === 'active' ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(budget, 'budget')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(budget, 'budget')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(budget, 'budget')} color="error" size="small">
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

  const renderTaxManagement = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Tax Management</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<SecurityIcon />}
            onClick={() => showSnackbar('Compliance report generated')}
            sx={{ mr: 1 }}
          >
            Compliance
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('tax-record')}
          >
            Add Tax Record
          </Button> 
        </Box>
      </Box>

      {taxLoading && <LinearProgress />}
      {taxError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {taxError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Tax Type</TableCell>
              <TableCell>Period</TableCell>
              <TableCell>Jurisdiction</TableCell>
              <TableCell align="right">Taxable Amount</TableCell>
              <TableCell align="right">Tax Amount</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {taxRecords?.map((tax, index) => (
              <TableRow key={tax.id || `tax-${index}`}>
                <TableCell>{tax.tax_type || ''}</TableCell>
                <TableCell>{tax.period || ''}</TableCell>
                <TableCell>{tax.jurisdiction || ''}</TableCell>
                <TableCell align="right">${tax.taxable_amount || 0}</TableCell>
                <TableCell align="right">${tax.tax_amount || 0}</TableCell>
                <TableCell>{tax.due_date ? new Date(tax.due_date).toLocaleDateString() : ''}</TableCell>
                <TableCell>
                  <Chip
                    label={tax.status || 'pending'}
                    color={
                      tax.status === 'filed' ? 'success' :
                      tax.status === 'overdue' ? 'error' : 'warning'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(tax, 'tax-record')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(tax, 'tax-record')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(tax, 'tax-record')} color="error" size="small">
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

  const renderBankReconciliation = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Bank Reconciliation</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => showSnackbar('Statement import started')}
            sx={{ mr: 1 }}
          >
            Import Statement
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('bank-reconciliation')}
          >
            New Reconciliation
          </Button>
        </Box>
      </Box>

      {bankLoading && <LinearProgress />}

      {bankError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {bankError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Bank Account</TableCell>
              <TableCell>Statement Date</TableCell>
              <TableCell align="right">Book Balance</TableCell>
              <TableCell align="right">Bank Balance</TableCell>
              <TableCell align="right">Difference</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {bankReconciliations?.map((rec, index) => (
              <TableRow key={rec.id || `rec-${index}`}>
                <TableCell>{rec.bank_account || ''}</TableCell>
                <TableCell>{rec.statement_date ? new Date(rec.statement_date).toLocaleDateString() : ''}</TableCell>
                <TableCell align="right">${rec.book_balance || 0}</TableCell>
                <TableCell align="right">${rec.bank_balance || 0}</TableCell>
                <TableCell align="right">
                  <Chip
                    label={`$${Math.abs(rec.book_balance - rec.bank_balance).toFixed(2)}`}
                    color={Math.abs(rec.book_balance - rec.bank_balance) > 0.01 ? 'error' : 'success'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={rec.status || 'pending'}
                    color={
                      rec.status === 'reconciled' ? 'success' :
                      rec.status === 'pending' ? 'warning' : 'error'
                    }
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(rec, 'bank-reconciliation')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(rec, 'bank-reconciliation')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(rec, 'bank-reconciliation')} color="error" size="small">
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

  const renderFinancialReports = () => (
    <Box>
      <Typography variant="h5" gutterBottom>Financial Reports & Analysis</Typography>

      <Grid container spacing={3}>
        {/* P&L Report */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6">Profit & Loss</Typography>
                <IconButton onClick={() => showSnackbar('P&L report generated')}>
                  <DownloadIcon />
                </IconButton>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Comprehensive income statement with revenue, expenses, and net profit analysis.
              </Typography>
              <Button variant="outlined" fullWidth>
                Generate P&L Report
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Balance Sheet */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6">Balance Sheet</Typography>
                <IconButton onClick={() => showSnackbar('Balance sheet generated')}>
                  <DownloadIcon />
                </IconButton>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Assets, liabilities, and equity snapshot at a specific point in time.
              </Typography>
              <Button variant="outlined" fullWidth>
                Generate Balance Sheet
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Cash Flow */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6">Cash Flow Statement</Typography>
                <IconButton onClick={() => showSnackbar('Cash flow report generated')}>
                  <DownloadIcon />
                </IconButton>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Operating, investing, and financing cash flow analysis.
              </Typography>
              <Button variant="outlined" fullWidth>
                Generate Cash Flow
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Audit Trail */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6">Audit Trail</Typography>
                <IconButton onClick={() => showSnackbar('Audit trail exported')}>
                  <LockIcon />
                </IconButton>
              </Box>
              <Typography variant="body2" color="text.secondary" paragraph>
                Complete transaction history and change tracking for compliance.
              </Typography>
              <Button variant="outlined" fullWidth>
                View Audit Trail
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderAuditTrail = () => (
    <Box>
      <Typography variant="h5" gutterBottom>Audit Trail & Compliance</Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Complete audit trail of all financial transactions and changes for compliance and transparency.
      </Typography>
      
      {auditLoading && <LinearProgress />}
      
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Recent Audit Events</Typography>
          <List>
            {auditTrail && auditTrail.length > 0 ? auditTrail.map((event, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <InfoIcon color="info" />
                </ListItemIcon>
                <ListItemText 
                  primary={event.action || 'Audit Event'}
                  secondary={`User: ${event.user || 'system'} | Time: ${event.timestamp || 'N/A'} | ${event.details || ''}`}
                />
              </ListItem>
            )) : (
              <>
                <ListItem>
                  <ListItemIcon>
                    <InfoIcon color="info" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Journal Entry Created"
                    secondary="User: admin | Time: 2024-01-15 10:30:00 | Amount: $5,000"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <InfoIcon color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Invoice Approved"
                    secondary="User: manager | Time: 2024-01-15 09:15:00 | Invoice: INV-001"
                  />
                </ListItem>
                <ListItem>
                  <ListItemIcon>
                    <WarningIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Budget Variance Alert"
                    secondary="User: system | Time: 2024-01-15 08:00:00 | Variance: 15%"
                  />
                </ListItem>
              </>
            )}
          </List>
        </CardContent>
      </Card>
    </Box>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return renderDashboard();
      case 1:
        return renderGeneralLedger();
      case 2:
        return renderChartOfAccounts();
      case 3:
        return renderAccountsPayable();
      case 4:
        return renderAccountsReceivable();
      case 5:
        return renderFixedAssets();
      case 6:
        return renderBudgeting();
      case 7:
        return renderTaxManagement();
      case 8:
        return renderBankReconciliation();
      case 9:
        return <MultiCurrencyValuation />;
      case 10:
        return <AIAnalyticsDashboard />;
      case 11:
        return renderFinancialReports();
      case 12:
        return renderAuditTrail();
      default:
        return renderDashboard();
    }
  };

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      <Typography variant={isMobile ? "h5" : "h4"} gutterBottom>
        Advanced Finance Management
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Enterprise-grade financial management with comprehensive GL, AP, AR, Fixed Assets, Budgeting, Tax Management, and more.
      </Typography>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
        >
          {tabLabels.map((label, index) => (
            <Tab key={index} label={label} />
          ))}
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box sx={{ minHeight: '60vh' }}>
        {renderTabContent()}
      </Box>

      {/* Forms and Modals */}
      {formOpen && (
        <ImprovedForm
          open={formOpen}
          onClose={() => setFormOpen(false)}
          type={selectedItemType}
          editData={editItem}
          onSave={handleSave}
        />
      )}

      {detailViewOpen && (
        <DetailViewModal
          open={detailViewOpen}
          onClose={() => setDetailViewOpen(false)}
          data={selectedItem}
          type={selectedItemType}
        />
      )}

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
    </Box>
  );
};

export default AdvancedFinanceModule;
