import React, { useState, useEffect } from 'react';
import { useCurrency } from '../../contexts/CurrencyContext';
import { useCurrencyConversion } from '../../hooks/useCurrencyConversion';
import CurrencySelector from '../../components/CurrencySelector';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Button,
  LinearProgress,
  Tooltip,
  Alert,
  Paper,
  Tabs,
  Tab,
  CardActions,
  Divider,
  Badge
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AccountBalance,
  Receipt,
  CreditCard,
  AttachMoney,
  Warning,
  CheckCircle,
  Refresh,
  GetApp,
  Visibility,
  Add,
  Edit,
  Payment,
  Assignment,
  Analytics,
  PlaylistAdd,
  Money,
  BusinessCenter,
  Schedule,
  ViewList
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useFinanceData } from './context/FinanceDataContext';
import BackendStatusChecker from '../../components/indicators/BackendStatusChecker';

const FinanceDashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [refreshTime, setRefreshTime] = useState(new Date());

  // Fetch data from centralized context
  const { 
    glEntries,
    accounts, 
    invoices,
    bills: apData,
    loading,
    refreshAll: contextRefreshAll,
    getTotalOutstandingAR,
    getTotalOutstandingAP,
    getOverdueInvoices,
    getOverdueBills
  } = useFinanceData();

  // Currency conversion
  const { selectedCurrency } = useCurrency();
  const { formatAmount } = useCurrencyConversion();

  const isLoading = loading.gl_entries || loading.accounts || loading.invoices || loading.bills;

  const refreshAll = () => {
    contextRefreshAll();
    setRefreshTime(new Date());
  };

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(refreshAll, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Calculate KPIs with currency conversion
  const kpis = {
    totalAssets: accounts
      ?.filter(acc => acc.type === 'asset')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0) || 0,
    
    totalLiabilities: accounts
      ?.filter(acc => acc.type === 'liability')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0) || 0,
    
    totalEquity: accounts
      ?.filter(acc => acc.type === 'equity')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0) || 0,
    
    totalRevenue: accounts
      ?.filter(acc => acc.type === 'revenue')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0) || 0,
    
    totalExpenses: accounts
      ?.filter(acc => acc.type === 'expense')
      .reduce((sum, acc) => sum + (acc.balance || 0), 0) || 0,
    
    arTotal: getTotalOutstandingAR(),
    arOverdue: getOverdueInvoices().reduce((sum, inv) => sum + (inv.amount || 0), 0),
    
    apTotal: getTotalOutstandingAP(),
    apOverdue: getOverdueBills().reduce((sum, bill) => sum + (bill.amount || 0), 0),
    
    glEntriesCount: glEntries?.length || 0,
    unbalancedEntries: glEntries?.filter(entry => {
      const totalDebits = entry.lines?.reduce((sum, line) => sum + (line.debit_amount || 0), 0) || 0;
      const totalCredits = entry.lines?.reduce((sum, line) => sum + (line.credit_amount || 0), 0) || 0;
      return Math.abs(totalDebits - totalCredits) > 0.01;
    }).length || 0
  };

  // Calculate ratios and trends
  const netIncome = kpis.totalRevenue - kpis.totalExpenses;
  const workingCapital = kpis.totalAssets - kpis.totalLiabilities;
  const arTurnover = kpis.arTotal > 0 ? kpis.totalRevenue / kpis.arTotal : 0;

  const KPICard = ({ title, value, icon: Icon, trend, color = 'primary', subtitle, alert, actions = [] }) => (
    <Card sx={{ height: '100%', position: 'relative', '&:hover': { boxShadow: 3 } }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="textSecondary" gutterBottom variant="body2">
              {title}
            </Typography>
            <Typography variant="h5" component="div" color={`${color}.main`}>
              {typeof value === 'number' ? `$${value.toLocaleString()}` : value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ textAlign: 'center' }}>
            <Icon sx={{ fontSize: 40, color: `${color}.main`, mb: 1 }} />
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {trend > 0 ? (
                  <TrendingUp sx={{ fontSize: 16, color: 'success.main' }} />
                ) : (
                  <TrendingDown sx={{ fontSize: 16, color: 'error.main' }} />
                )}
                <Typography variant="caption" sx={{ ml: 0.5 }}>
                  {Math.abs(trend)}%
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
        {alert && (
          <Alert severity={alert.severity} sx={{ mt: 1 }} size="small">
            {alert.message}
          </Alert>
        )}
      </CardContent>
      {actions.length > 0 && (
        <>
          <Divider />
          <CardActions sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {actions.map((action, index) => (
              <Button
                key={index}
                size="small"
                startIcon={action.icon}
                onClick={action.onClick}
                color={action.color || 'primary'}
                variant={action.variant || 'text'}
                sx={{ fontSize: '0.75rem' }}
              >
                {action.label}
              </Button>
            ))}
          </CardActions>
        </>
      )}
    </Card>
  );

  const TabPanel = ({ children, value, index }) => (
    <div hidden={value !== index} style={{ paddingTop: 16 }}>
      {value === index && children}
    </div>
  );

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Finance Dashboard
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Last updated: {refreshTime.toLocaleTimeString()}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={refreshAll} disabled={isLoading}>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button variant="outlined" startIcon={<GetApp />}>
            Export Report
          </Button>
          <Button variant="contained" startIcon={<Visibility />}>
            View Details
          </Button>
        </Box>
      </Box>

      {/* Backend Status Checker */}
      <BackendStatusChecker />

      {/* Loading indicator */}
      {isLoading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Quick Actions Section */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: 'background.default' }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <BusinessCenter />
          Quick Actions for Business Owners
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<Add />}
              onClick={() => navigate('/finance/gl')}
              sx={{ py: 2 }}
            >
              New Journal Entry
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<Receipt />}
              onClick={() => navigate('/finance/ar')}
              color="success"
              sx={{ py: 2 }}
            >
              Create Invoice
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={<Payment />}
              onClick={() => navigate('/finance/ap')}
              color="warning"
              sx={{ py: 2 }}
            >
              Pay Bills
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              size="large"
              startIcon={<AccountBalance />}
              onClick={() => navigate('/finance/coa')}
              sx={{ py: 2 }}
            >
              Manage Accounts
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Key Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Assets"
            value={formatAmount(kpis.totalAssets)}
            icon={AccountBalance}
            color="primary"
            subtitle={`${accounts?.filter(a => a.type === 'asset').length || 0} accounts`}
            actions={[
              {
                label: 'View Accounts',
                icon: <ViewList />,
                onClick: () => navigate('/finance/coa'),
                variant: 'outlined'
              },
              {
                label: 'Add Asset',
                icon: <Add />,
                onClick: () => navigate('/finance/coa'),
                color: 'primary'
              }
            ]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Net Income"
            value={netIncome}
            icon={AttachMoney}
            color={netIncome >= 0 ? "success" : "error"}
            subtitle="Revenue - Expenses"
            actions={[
              {
                label: 'View P&L',
                icon: <Analytics />,
                onClick: () => setActiveTab(2),
                variant: 'outlined'
              },
              {
                label: 'New Entry',
                icon: <Add />,
                onClick: () => navigate('/finance/gl'),
                color: 'success'
              }
            ]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Working Capital"
            value={workingCapital}
            icon={TrendingUp}
            color={workingCapital >= 0 ? "success" : "warning"}
            subtitle="Assets - Liabilities"
            actions={[
              {
                label: 'Balance Sheet',
                icon: <Assignment />,
                onClick: () => setActiveTab(1),
                variant: 'outlined'
              },
              {
                label: 'Cash Flow',
                icon: <Money />,
                onClick: () => setActiveTab(3),
                color: 'info'
              }
            ]}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Journal Entries"
            value={kpis.glEntriesCount}
            icon={Receipt}
            color="info"
            subtitle="This period"
            alert={kpis.unbalancedEntries > 0 ? {
              severity: 'warning',
              message: `${kpis.unbalancedEntries} unbalanced entries`
            } : null}
            actions={[
              {
                label: 'View All',
                icon: <ViewList />,
                onClick: () => navigate('/finance/gl'),
                variant: 'outlined'
              },
              {
                label: 'Add Entry',
                icon: <PlaylistAdd />,
                onClick: () => navigate('/finance/gl'),
                color: 'primary'
              }
            ]}
          />
        </Grid>
      </Grid>

      {/* Tabs for detailed views */}
      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          indicatorColor="primary"
          textColor="primary"
        >
          <Tab label="Receivables & Payables" />
          <Tab label="Balance Sheet Summary" />
          <Tab label="P&L Summary" />
          <Tab label="Recent Activity & Tasks" />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          {/* AR/AP Summary */}
          <Grid container spacing={3} sx={{ p: 3 }}>
            <Grid item xs={12} md={6}>
              <Card sx={{ '&:hover': { boxShadow: 3 } }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Money color="success" />
                    Accounts Receivable
                    <Badge badgeContent={getOverdueInvoices().length} color="error" sx={{ ml: 'auto' }}>
                      <Chip label="Outstanding" size="small" />
                    </Badge>
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="h4" color="primary.main">
                        ${formatAmount(kpis.arTotal)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Total Outstanding
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="h4" color="error.main">
                        ${formatAmount(kpis.arOverdue)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Overdue
                      </Typography>
                    </Grid>
                  </Grid>
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress
                      variant="determinate"
                      value={kpis.arTotal > 0 ? (kpis.arOverdue / kpis.arTotal) * 100 : 0}
                      color="error"
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                      {kpis.arTotal > 0 ? ((kpis.arOverdue / kpis.arTotal) * 100).toFixed(1) : 0}% overdue
                    </Typography>
                  </Box>
                </CardContent>
                <Divider />
                <CardActions sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    startIcon={<Receipt />}
                    onClick={() => navigate('/finance/ar')}
                    color="success"
                    variant="contained"
                  >
                    Create Invoice
                  </Button>
                  <Button
                    size="small"
                    startIcon={<ViewList />}
                    onClick={() => navigate('/finance/ar')}
                    variant="outlined"
                  >
                    View All
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Schedule />}
                    onClick={() => navigate('/finance/ar')}
                    color="warning"
                  >
                    {getOverdueInvoices().length} Overdue
                  </Button>
                </CardActions>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card sx={{ '&:hover': { boxShadow: 3 } }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CreditCard color="warning" />
                    Accounts Payable
                    <Badge badgeContent={getOverdueBills().length} color="error" sx={{ ml: 'auto' }}>
                      <Chip label="Outstanding" size="small" />
                    </Badge>
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="h4" color="primary.main">
                        ${formatAmount(kpis.apTotal)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Total Outstanding
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="h4" color="error.main">
                        ${formatAmount(kpis.apOverdue)}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Overdue
                      </Typography>
                    </Grid>
                  </Grid>
                  <Box sx={{ mt: 2 }}>
                    <LinearProgress
                      variant="determinate"
                      value={kpis.apTotal > 0 ? (kpis.apOverdue / kpis.apTotal) * 100 : 0}
                      color="error"
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                      {kpis.apTotal > 0 ? ((kpis.apOverdue / kpis.apTotal) * 100).toFixed(1) : 0}% overdue
                    </Typography>
                  </Box>
                </CardContent>
                <Divider />
                <CardActions sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    startIcon={<Add />}
                    onClick={() => navigate('/finance/ap')}
                    color="warning"
                    variant="contained"
                  >
                    Add Bill
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Payment />}
                    onClick={() => navigate('/finance/ap')}
                    color="success"
                    variant="outlined"
                  >
                    Pay Bills
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Schedule />}
                    onClick={() => navigate('/finance/ap')}
                    color="error"
                  >
                    {getOverdueBills().length} Overdue
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          {/* Balance Sheet Summary */}
          <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="primary.main" gutterBottom>
                      Assets
                    </Typography>
                    <Typography variant="h4">
                      ${formatAmount(kpis.totalAssets)}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {accounts?.filter(a => a.type === 'asset').length || 0} accounts
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="warning.main" gutterBottom>
                      Liabilities
                    </Typography>
                    <Typography variant="h4">
                      ${formatAmount(kpis.totalLiabilities)}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {accounts?.filter(a => a.type === 'liability').length || 0} accounts
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="success.main" gutterBottom>
                      Equity
                    </Typography>
                    <Typography variant="h4">
                      ${formatAmount(kpis.totalEquity)}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {accounts?.filter(a => a.type === 'equity').length || 0} accounts
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            {/* Balance Check */}
            <Box sx={{ mt: 3 }}>
              <Alert 
                severity={Math.abs((kpis.totalAssets) - (kpis.totalLiabilities + kpis.totalEquity)) < 0.01 ? "success" : "error"}
              >
                Balance Check: Assets = Liabilities + Equity
                <br />
                {formatAmount(kpis.totalAssets)} = {formatAmount(kpis.totalLiabilities + kpis.totalEquity)}
                {Math.abs((kpis.totalAssets) - (kpis.totalLiabilities + kpis.totalEquity)) < 0.01 ? 
                  " ✓ Balanced" : " ✗ Unbalanced"}
              </Alert>
            </Box>
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          {/* P&L Summary */}
          <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="success.main" gutterBottom>
                      Revenue
                    </Typography>
                    <Typography variant="h4">
                      ${formatAmount(kpis.totalRevenue)}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {accounts?.filter(a => a.type === 'revenue').length || 0} accounts
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" color="error.main" gutterBottom>
                      Expenses
                    </Typography>
                    <Typography variant="h4">
                      ${formatAmount(kpis.totalExpenses)}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {accounts?.filter(a => a.type === 'expense').length || 0} accounts
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 3 }}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Net Income
                  </Typography>
                  <Typography 
                    variant="h3" 
                    color={netIncome >= 0 ? "success.main" : "error.main"}
                  >
                    ${netIncome.toFixed(2)}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Revenue - Expenses = Net Income
                  </Typography>
                  
                  {/* Profit margin */}
                  {kpis.totalRevenue > 0 && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" color="textSecondary">
                        Profit Margin: {((netIncome / kpis.totalRevenue) * 100).toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(Math.abs((netIncome / kpis.totalRevenue) * 100), 100)}
                        color={netIncome >= 0 ? "success" : "error"}
                        sx={{ mt: 1, height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Box>
          </Box>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          {/* Recent Activity & Quick Links */}
          <Box sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Schedule />
                      Recent Activity
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      {[...glEntries, ...invoices, ...apData]
                        .sort((a, b) => new Date(b.created_at || b.invoice_date || b.due_date) - new Date(a.created_at || a.invoice_date || a.due_date))
                        .slice(0, 5)
                        .map((item, index) => (
                          <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 2, p: 1, borderRadius: 1, bgcolor: 'grey.50' }}>
                            {item.reference ? (
                              <Receipt color="primary" />
                            ) : item.invoice_number ? (
                              <Money color="success" />
                            ) : (
                              <CreditCard color="warning" />
                            )}
                            <Box sx={{ flex: 1 }}>
                              <Typography variant="body2" fontWeight="medium">
                                {item.reference || item.invoice_number || item.vendor_name || 'Transaction'}
                              </Typography>
                              <Typography variant="caption" color="textSecondary">
                                {item.description || item.customer_name || `Amount: $${item.amount}`}
                              </Typography>
                            </Box>
                            <Typography variant="caption" color="textSecondary">
                              {new Date(item.created_at || item.invoice_date || item.due_date).toLocaleDateString()}
                            </Typography>
                          </Box>
                        ))}
                    </Box>
                  </CardContent>
                  <CardActions>
                    <Button size="small" onClick={() => navigate('/finance/gl')}>View All Transactions</Button>
                  </CardActions>
                </Card>
              </Grid>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <BusinessCenter />
                      Quick Business Tasks
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Button
                        fullWidth
                        variant="outlined"
                        startIcon={<Add />}
                        onClick={() => navigate('/finance/gl')}
                        sx={{ justifyContent: 'flex-start', py: 1.5 }}
                      >
                        Record Daily Cash Sales
                      </Button>
                      <Button
                        fullWidth
                        variant="outlined"
                        startIcon={<Receipt />}
                        onClick={() => navigate('/finance/ar')}
                        sx={{ justifyContent: 'flex-start', py: 1.5 }}
                      >
                        Send Customer Invoice
                      </Button>
                      <Button
                        fullWidth
                        variant="outlined"
                        startIcon={<Payment />}
                        onClick={() => navigate('/finance/ap')}
                        sx={{ justifyContent: 'flex-start', py: 1.5 }}
                      >
                        Pay Vendor Bills
                      </Button>
                      <Button
                        fullWidth
                        variant="outlined"
                        startIcon={<AccountBalance />}
                        onClick={() => navigate('/finance/coa')}
                        sx={{ justifyContent: 'flex-start', py: 1.5 }}
                      >
                        Add New Account
                      </Button>
                      <Button
                        fullWidth
                        variant="outlined"
                        startIcon={<Analytics />}
                        onClick={() => setActiveTab(1)}
                        sx={{ justifyContent: 'flex-start', py: 1.5 }}
                      >
                        Review Financial Position
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default FinanceDashboard;

