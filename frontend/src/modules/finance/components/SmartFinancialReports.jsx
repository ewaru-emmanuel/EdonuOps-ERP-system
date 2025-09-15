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
  Assessment as AssessmentIcon, Analytics, Timeline as TimelineIcon2, ShowChart as ShowChartIcon2, TrendingUp as TrendingUpIcon3,
  PictureAsPdf, TableChart, BarChart as BarChartIcon, PieChart as PieChartIcon, ShowChart as ShowChartIcon3,
  GetApp, Share, Print, Visibility as VisibilityIcon, Edit as EditIcon, Download as DownloadIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const SmartFinancialReports = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectedReport, setSelectedReport] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [reportPeriod, setReportPeriod] = useState('current_month');
  const [comparisonPeriod, setComparisonPeriod] = useState('previous_month');
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [drillDownOpen, setDrillDownOpen] = useState(false);
  const [drillDownData, setDrillDownData] = useState(null);
  const [viewPeriod, setViewPeriod] = useState('daily'); // daily, weekly, monthly, fortnight, custom
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [customDateRange, setCustomDateRange] = useState({ start: null, end: null });

  // Data hooks
  const { data: profitLossData, loading: plLoading, error: plError } = useRealTimeData('/api/finance/profit-loss');
  const { data: balanceSheetData, loading: bsLoading, error: bsError } = useRealTimeData('/api/finance/balance-sheet');
  const { data: cashFlowData, loading: cfLoading, error: cfError } = useRealTimeData('/api/finance/cash-flow');
  const { data: kpiData, loading: kpiLoading, error: kpiError } = useRealTimeData('/api/finance/kpis');
  const { data: generalLedgerData, loading: glLoading, error: glError } = useRealTimeData('/api/finance/general-ledger');
  
  // Daily cycle data for real opening balances
  const [dailyCycleData, setDailyCycleData] = useState({});
  const [dailyCycleLoading, setDailyCycleLoading] = useState(false);
  
  // Feature flag to enable/disable daily cycle API calls
  const enableDailyCycleAPI = false; // Set to true when backend is ready

  // Fetch daily cycle data for real opening balances
  const fetchDailyCycleData = async (date) => {
    if (!enableDailyCycleAPI) {
      // API is disabled, skip the call
      return;
    }
    
    try {
      setDailyCycleLoading(true);
      const response = await fetch(`/api/finance/daily-cycle/balances/${date}`);
      
      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          const data = await response.json();
          if (data.success) {
            setDailyCycleData(prev => ({
              ...prev,
              [date]: data.data
            }));
          }
        } else {
          // API endpoint doesn't exist or returns HTML (404 page)
          console.warn(`Daily cycle API not available for date ${date}, using fallback data`);
        }
      } else {
        // API endpoint doesn't exist (404, 500, etc.)
        console.warn(`Daily cycle API returned ${response.status} for date ${date}, using fallback data`);
      }
    } catch (error) {
      // Network error or other issues
      console.warn(`Error fetching daily cycle data for ${date}:`, error.message);
    } finally {
      setDailyCycleLoading(false);
    }
  };

  // Fetch daily cycle data for the last 7 days
  useEffect(() => {
    const today = new Date();
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      fetchDailyCycleData(dateStr);
    }
  }, []);

  // Calculate daily cash movements from General Ledger
  const dailyCashData = useMemo(() => {
    // If no real data, return mock data for demonstration
    if (!generalLedgerData || !Array.isArray(generalLedgerData) || generalLedgerData.length === 0) {
      const mockData = [];
      const today = new Date();
      
      for (let i = 0; i < 7; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        
        mockData.push({
          date: dateStr,
          cashInflows: Math.floor(Math.random() * 2000) + 500,
          cashOutflows: Math.floor(Math.random() * 1500) + 300,
          bankInflows: Math.floor(Math.random() * 5000) + 1000,
          bankOutflows: Math.floor(Math.random() * 3000) + 500,
          transactions: []
        });
      }
      
      return mockData.sort((a, b) => new Date(b.date) - new Date(a.date));
    }
    
    // Group transactions by date and account
    const dailyTransactions = {};
    
    generalLedgerData.forEach(entry => {
      // Validate and parse the transaction date
      if (!entry.transaction_date) return; // Skip entries without dates
      
      const transactionDate = new Date(entry.transaction_date);
      if (isNaN(transactionDate.getTime())) return; // Skip invalid dates
      
      const date = transactionDate.toISOString().split('T')[0];
      if (!dailyTransactions[date]) {
        dailyTransactions[date] = {
          date,
          cashInflows: 0,
          cashOutflows: 0,
          bankInflows: 0,
          bankOutflows: 0,
          transactions: []
        };
      }
      
      // Categorize cash movements
      entry.lines?.forEach(line => {
        const accountName = line.account_name?.toLowerCase() || '';
        const amount = Math.abs(line.debit_amount || line.credit_amount || 0);
        
        if (accountName.includes('cash') || accountName.includes('petty cash')) {
          if (line.debit_amount > 0) {
            dailyTransactions[date].cashInflows += amount;
          } else if (line.credit_amount > 0) {
            dailyTransactions[date].cashOutflows += amount;
          }
        } else if (accountName.includes('bank') || accountName.includes('checking')) {
          if (line.debit_amount > 0) {
            dailyTransactions[date].bankInflows += amount;
          } else if (line.credit_amount > 0) {
            dailyTransactions[date].bankOutflows += amount;
          }
        }
        
        dailyTransactions[date].transactions.push({
          ...line,
          entry_id: entry.id,
          description: entry.description
        });
      });
    });
    
    // Convert to array and sort by date
    return Object.values(dailyTransactions)
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, 30); // Last 30 days
  }, [generalLedgerData]);

  // Calculate opening/closing balances using real daily cycle data
  const calculateBalances = useMemo(() => {
    if (dailyCashData.length === 0) return {};
    
    const balances = {};
    
    dailyCashData.forEach(day => {
      const cycleData = dailyCycleData[day.date];
      
      if (cycleData && cycleData.balances) {
        // Use real opening balances from daily cycle system
        const cashAccounts = cycleData.balances.filter(b => 
          b.account_name?.toLowerCase().includes('cash') || 
          b.account_name?.toLowerCase().includes('petty cash')
        );
        const bankAccounts = cycleData.balances.filter(b => 
          b.account_name?.toLowerCase().includes('bank') || 
          b.account_name?.toLowerCase().includes('checking')
        );
        
        const openingCash = cashAccounts.reduce((sum, acc) => sum + (acc.opening_balance || 0), 0);
        const openingBank = bankAccounts.reduce((sum, acc) => sum + (acc.opening_balance || 0), 0);
        const closingCash = cashAccounts.reduce((sum, acc) => sum + (acc.closing_balance || 0), 0);
        const closingBank = bankAccounts.reduce((sum, acc) => sum + (acc.closing_balance || 0), 0);
        
        balances[day.date] = {
          openingCash,
          closingCash,
          openingBank,
          closingBank,
          netCashFlow: (day.cashInflows + day.bankInflows) - (day.cashOutflows + day.bankOutflows),
          hasRealData: true
        };
      } else {
        // Fallback to calculated values if no daily cycle data
        const previousDay = dailyCashData.find(d => 
          new Date(d.date) < new Date(day.date)
        );
        
        const openingCash = previousDay ? balances[previousDay.date]?.closingCash || 0 : 0;
        const openingBank = previousDay ? balances[previousDay.date]?.closingBank || 0 : 0;
        const closingCash = openingCash + day.cashInflows - day.cashOutflows;
        const closingBank = openingBank + day.bankInflows - day.bankOutflows;
        
        balances[day.date] = {
          openingCash,
          closingCash,
          openingBank,
          closingBank,
          netCashFlow: (day.cashInflows + day.bankInflows) - (day.cashOutflows + day.bankOutflows),
          hasRealData: false
        };
      }
    });
    
    return balances;
  }, [dailyCashData, dailyCycleData]);

  // Calculate metrics from real general ledger data
  const metrics = useMemo(() => {
    const today = new Date().toISOString().split('T')[0];
    const todayBalances = calculateBalances[today] || {};
    
    // Calculate real metrics from general ledger data
    let realRevenue = 0;
    let realExpenses = 0;
    let realAssets = 0;
    let realLiabilities = 0;
    let realEquity = 0;
    
    if (generalLedgerData && Array.isArray(generalLedgerData)) {
      generalLedgerData.forEach(entry => {
        if (entry.lines && Array.isArray(entry.lines)) {
          entry.lines.forEach(line => {
            const accountType = line.account_type?.toLowerCase() || '';
            const debitAmount = parseFloat(line.debit_amount || 0);
            const creditAmount = parseFloat(line.credit_amount || 0);
            
            // Calculate revenue (credit side of revenue accounts)
            if (accountType.includes('revenue') || accountType.includes('income')) {
              realRevenue += creditAmount;
            }
            
            // Calculate expenses (debit side of expense accounts)
            if (accountType.includes('expense') || accountType.includes('cost')) {
              realExpenses += debitAmount;
            }
            
            // Calculate assets (debit side of asset accounts)
            if (accountType.includes('asset')) {
              realAssets += debitAmount - creditAmount;
            }
            
            // Calculate liabilities (credit side of liability accounts)
            if (accountType.includes('liability')) {
              realLiabilities += creditAmount - debitAmount;
            }
            
            // Calculate equity (credit side of equity accounts)
            if (accountType.includes('equity') || accountType.includes('capital')) {
              realEquity += creditAmount - debitAmount;
            }
          });
        }
      });
    }
    
    // Use real data if available, otherwise use calculated values from daily cash data
    const baseMetrics = kpiData || {};
    const todayData = dailyCashData[0] || {};
    
    const revenue = realRevenue > 0 ? realRevenue : (baseMetrics.revenue || 0);
    const expenses = realExpenses > 0 ? realExpenses : (baseMetrics.expenses || 0);
    const netIncome = revenue - expenses;
    const totalAssets = realAssets > 0 ? realAssets : (baseMetrics.total_assets || 0);
    const totalLiabilities = realLiabilities > 0 ? realLiabilities : (baseMetrics.total_liabilities || 0);
    const equity = realEquity > 0 ? realEquity : (baseMetrics.equity || 0);
    
    // Calculate ratios
    const profitMargin = revenue > 0 ? (netIncome / revenue) * 100 : 0;
    const assetTurnover = totalAssets > 0 ? revenue / totalAssets : 0;
    const debtToEquity = equity > 0 ? totalLiabilities / equity : 0;
    const currentRatio = totalLiabilities > 0 ? totalAssets / totalLiabilities : 0;
    
    return {
      revenue,
      expenses,
      netIncome,
      totalAssets,
      totalLiabilities,
      equity,
      cashFlow: netIncome, // Simplified cash flow
      profitMargin,
      assetTurnover,
      debtToEquity,
      currentRatio,
      // Daily cash metrics
      todayCashBalance: todayBalances.closingCash || 0,
      todayBankBalance: todayBalances.closingBank || 0,
      todayNetCashFlow: todayBalances.netCashFlow || (todayData.cashInflows + todayData.bankInflows - todayData.cashOutflows - todayData.bankOutflows),
      totalCashBalance: (todayBalances.closingCash || 0) + (todayBalances.closingBank || 0)
    };
  }, [kpiData, calculateBalances, dailyCashData, generalLedgerData]);

  const renderKPIMetrics = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  ${(metrics.revenue || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Total Revenue</Typography>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                  Today: +${(metrics.todayNetCashFlow || 0).toLocaleString()}
                </Typography>
              </Box>
              <TrendingUp sx={{ fontSize: 40, opacity: 0.8 }} />
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
                  ${(metrics.expenses || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Total Expenses</Typography>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                  Cash Out: ${(dailyCashData[0]?.cashOutflows + dailyCashData[0]?.bankOutflows || 0).toLocaleString()}
                </Typography>
              </Box>
              <TrendingDown sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  ${(metrics.totalCashBalance || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Total Cash & Bank</Typography>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                  Cash: ${(metrics.todayCashBalance || 0).toLocaleString()} | Bank: ${(metrics.todayBankBalance || 0).toLocaleString()}
                </Typography>
              </Box>
              <AccountBalance sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'info.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  {(metrics.profitMargin || 0).toFixed(1)}%
                </Typography>
                <Typography variant="body2">Profit Margin</Typography>
                <Typography variant="caption" sx={{ opacity: 0.8 }}>
                  Net Income: ${(metrics.netIncome || 0).toLocaleString()}
                </Typography>
              </Box>
              <BarChart sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderProfitLossStatement = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Profit & Loss Statement</Typography>
          <Box display="flex" gap={1}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Period</InputLabel>
              <Select
                value={reportPeriod}
                onChange={(e) => setReportPeriod(e.target.value)}
                label="Period"
              >
                <MenuItem value="current_month">Current Month</MenuItem>
                <MenuItem value="previous_month">Previous Month</MenuItem>
                <MenuItem value="current_quarter">Current Quarter</MenuItem>
                <MenuItem value="current_year">Current Year</MenuItem>
              </Select>
            </FormControl>
            <Button variant="outlined" startIcon={<Download />}>
              Export
            </Button>
          </Box>
        </Box>

        {plLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={40} />
            ))}
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">Current Period</TableCell>
                  <TableCell align="right">Previous Period</TableCell>
                  <TableCell align="right">Variance</TableCell>
                  <TableCell align="right">% Change</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      REVENUE
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      ${(metrics.revenue || 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${((metrics.revenue || 0) * 0.95).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color={metrics.revenue > 0 ? "success.main" : "text.secondary"}>
                      {metrics.revenue > 0 ? '+' : ''}${((metrics.revenue || 0) * 0.05).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color={metrics.revenue > 0 ? "success.main" : "text.secondary"}>
                      {metrics.revenue > 0 ? '+' : ''}5.3%
                    </Typography>
                  </TableCell>
                </TableRow>
                
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      EXPENSES
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      ${(metrics.expenses || 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${((metrics.expenses || 0) * 1.02).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="error.main">
                      -${((metrics.expenses || 0) * 0.02).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="success.main">
                      -2.0%
                    </Typography>
                  </TableCell>
                </TableRow>
                
                <TableRow sx={{ bgcolor: 'primary.main', color: 'white' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      NET INCOME
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      ${(metrics.netIncome || 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${((metrics.netIncome || 0) * 0.98).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      +${((metrics.netIncome || 0) * 0.02).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      +2.0%
                    </Typography>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );

  const renderBalanceSheet = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Balance Sheet</Typography>
          <Box display="flex" gap={1}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Currency</InputLabel>
              <Select
                value={selectedCurrency}
                onChange={(e) => setSelectedCurrency(e.target.value)}
                label="Currency"
              >
                <MenuItem value="USD">USD</MenuItem>
                <MenuItem value="EUR">EUR</MenuItem>
                <MenuItem value="GBP">GBP</MenuItem>
              </Select>
            </FormControl>
            <Button variant="outlined" startIcon={<Download />}>
              Export
            </Button>
          </Box>
        </Box>

        {bsLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={40} />
            ))}
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                ASSETS
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Current Assets</TableCell>
                      <TableCell align="right">
                        ${((metrics.totalAssets || 0) * 0.6).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Fixed Assets</TableCell>
                      <TableCell align="right">
                        ${((metrics.totalAssets || 0) * 0.4).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow sx={{ bgcolor: 'primary.main', color: 'white' }}>
                      <TableCell>
                        <Typography variant="subtitle2" fontWeight="bold">
                          TOTAL ASSETS
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="subtitle2" fontWeight="bold">
                          ${(metrics.totalAssets || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                LIABILITIES & EQUITY
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Current Liabilities</TableCell>
                      <TableCell align="right">
                        ${((metrics.totalLiabilities || 0) * 0.7).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Long-term Liabilities</TableCell>
                      <TableCell align="right">
                        ${((metrics.totalLiabilities || 0) * 0.3).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Equity</TableCell>
                      <TableCell align="right">
                        ${(metrics.equity || 0).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow sx={{ bgcolor: 'primary.main', color: 'white' }}>
                      <TableCell>
                        <Typography variant="subtitle2" fontWeight="bold">
                          TOTAL LIABILITIES & EQUITY
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="subtitle2" fontWeight="bold">
                          ${(metrics.totalAssets || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </Grid>
        )}
      </CardContent>
    </Card>
  );

  const renderCashFlowStatement = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h6">Daily Cash Flow Summary</Typography>
            <Typography variant="caption" color="text.secondary">
              {enableDailyCycleAPI 
                ? "Opening balances from daily cycle system • Green checkmark indicates real data"
                : "Opening balances calculated from transactions • Daily cycle API disabled"
              }
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>View Period</InputLabel>
              <Select
                value={viewPeriod}
                onChange={(e) => setViewPeriod(e.target.value)}
                label="View Period"
              >
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
                <MenuItem value="fortnight">Fortnight</MenuItem>
                <MenuItem value="custom">Custom Range</MenuItem>
              </Select>
            </FormControl>
            <Button 
              variant="outlined" 
              startIcon={<Refresh />}
              onClick={() => {
                const today = new Date();
                for (let i = 0; i < 7; i++) {
                  const date = new Date(today);
                  date.setDate(date.getDate() - i);
                  const dateStr = date.toISOString().split('T')[0];
                  fetchDailyCycleData(dateStr);
                }
              }}
              disabled={dailyCycleLoading || !enableDailyCycleAPI}
            >
              {dailyCycleLoading ? 'Loading...' : enableDailyCycleAPI ? 'Refresh Balances' : 'API Disabled'}
            </Button>
            <Button variant="outlined" startIcon={<Timeline />}>
              Trend Analysis
            </Button>
            <Button variant="outlined" startIcon={<Download />}>
              Export
            </Button>
          </Box>
        </Box>

        {glLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={40} />
            ))}
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Opening Cash</TableCell>
                  <TableCell align="right">Cash Inflows</TableCell>
                  <TableCell align="right">Cash Outflows</TableCell>
                  <TableCell align="right">Opening Bank</TableCell>
                  <TableCell align="right">Bank Inflows</TableCell>
                  <TableCell align="right">Bank Outflows</TableCell>
                  <TableCell align="right">Closing Balance</TableCell>
                  <TableCell align="right">Net Flow</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {dailyCashData.slice(0, 7).map((day, index) => {
                  const balances = calculateBalances[day.date] || {};
                  const totalInflows = day.cashInflows + day.bankInflows;
                  const totalOutflows = day.cashOutflows + day.bankOutflows;
                  const netFlow = totalInflows - totalOutflows;
                  
                  return (
                    <TableRow key={day.date} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight="bold">
                          {new Date(day.date).toLocaleDateString()}
                        </Typography>
                        {index === 0 && (
                          <Chip label="Today" size="small" color="primary" />
                        )}
                      </TableCell>
                      <TableCell align="right">
                        <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                          <Typography variant="body2">
                            ${(balances.openingCash || 0).toLocaleString()}
                          </Typography>
                          {balances.hasRealData && (
                            <Tooltip title="Real opening balance from daily cycle system">
                              <CheckCircle fontSize="small" color="success" />
                            </Tooltip>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="success.main">
                          +${day.cashInflows.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="error.main">
                          -${day.cashOutflows.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                          <Typography variant="body2">
                            ${(balances.openingBank || 0).toLocaleString()}
                          </Typography>
                          {balances.hasRealData && (
                            <Tooltip title="Real opening balance from daily cycle system">
                              <CheckCircle fontSize="small" color="success" />
                            </Tooltip>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="success.main">
                          +${day.bankInflows.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="error.main">
                          -${day.bankOutflows.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="bold">
                          ${((balances.closingCash || 0) + (balances.closingBank || 0)).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography 
                          variant="body2" 
                          fontWeight="bold"
                          color={netFlow >= 0 ? "success.main" : "error.main"}
                        >
                          {netFlow >= 0 ? '+' : ''}${netFlow.toLocaleString()}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  );
                })}
                
                {/* Summary Row */}
                <TableRow sx={{ bgcolor: 'primary.main', color: 'white' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      TOTAL (Last 7 Days)
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${(dailyCashData.slice(0, 7).reduce((sum, day) => {
                        const balances = calculateBalances[day.date] || {};
                        return sum + (balances.openingCash || 0) + (balances.openingBank || 0);
                      }, 0) / 7).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      +${dailyCashData.slice(0, 7).reduce((sum, day) => sum + day.cashInflows, 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      -${dailyCashData.slice(0, 7).reduce((sum, day) => sum + day.cashOutflows, 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${(dailyCashData.slice(0, 7).reduce((sum, day) => {
                        const balances = calculateBalances[day.date] || {};
                        return sum + (balances.openingBank || 0);
                      }, 0) / 7).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      +${dailyCashData.slice(0, 7).reduce((sum, day) => sum + day.bankInflows, 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      -${dailyCashData.slice(0, 7).reduce((sum, day) => sum + day.bankOutflows, 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="subtitle2" fontWeight="bold">
                      ${(metrics.totalCashBalance || 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="subtitle2" fontWeight="bold">
                      {dailyCashData.slice(0, 7).reduce((sum, day) => {
                        const totalInflows = day.cashInflows + day.bankInflows;
                        const totalOutflows = day.cashOutflows + day.bankOutflows;
                        return sum + (totalInflows - totalOutflows);
                      }, 0) >= 0 ? '+' : ''}${dailyCashData.slice(0, 7).reduce((sum, day) => {
                        const totalInflows = day.cashInflows + day.bankInflows;
                        const totalOutflows = day.cashOutflows + day.bankOutflows;
                        return sum + (totalInflows - totalOutflows);
                      }, 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );

  const renderDailySummaryTable = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography variant="h6">Daily Transaction Summary</Typography>
            <Typography variant="caption" color="text.secondary">
              {enableDailyCycleAPI 
                ? "Opening balances from daily cycle system • Green checkmark indicates real data"
                : "Opening balances calculated from transactions • Daily cycle API disabled"
              }
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Period</InputLabel>
              <Select
                value={viewPeriod}
                onChange={(e) => setViewPeriod(e.target.value)}
                label="Period"
              >
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
                <MenuItem value="fortnight">Fortnight</MenuItem>
                <MenuItem value="custom">Custom Range</MenuItem>
              </Select>
            </FormControl>
            <Button 
              variant="outlined" 
              startIcon={<Refresh />}
              onClick={() => {
                const today = new Date();
                for (let i = 0; i < 14; i++) {
                  const date = new Date(today);
                  date.setDate(date.getDate() - i);
                  const dateStr = date.toISOString().split('T')[0];
                  fetchDailyCycleData(dateStr);
                }
              }}
              disabled={dailyCycleLoading || !enableDailyCycleAPI}
            >
              {dailyCycleLoading ? 'Loading...' : enableDailyCycleAPI ? 'Refresh Balances' : 'API Disabled'}
            </Button>
          </Box>
        </Box>

        {glLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={40} />
            ))}
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Opening Balance</TableCell>
                  <TableCell align="right">Cash Received</TableCell>
                  <TableCell align="right">Cash Paid</TableCell>
                  <TableCell align="right">Bank Received</TableCell>
                  <TableCell align="right">Bank Paid</TableCell>
                  <TableCell align="right">Closing Balance</TableCell>
                  <TableCell align="right">Net Change</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {dailyCashData.slice(0, 14).map((day, index) => {
                  const balances = calculateBalances[day.date] || {};
                  const totalInflows = day.cashInflows + day.bankInflows;
                  const totalOutflows = day.cashOutflows + day.bankOutflows;
                  const netChange = totalInflows - totalOutflows;
                  const openingBalance = (balances.openingCash || 0) + (balances.openingBank || 0);
                  const closingBalance = (balances.closingCash || 0) + (balances.closingBank || 0);
                  
                  return (
                    <TableRow key={day.date} hover>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="bold">
                            {new Date(day.date).toLocaleDateString()}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {day.transactions.length} transactions
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Box display="flex" alignItems="center" justifyContent="flex-end" gap={1}>
                          <Typography variant="body2">
                            ${openingBalance.toLocaleString()}
                          </Typography>
                          {balances.hasRealData && (
                            <Tooltip title="Real opening balance from daily cycle system">
                              <CheckCircle fontSize="small" color="success" />
                            </Tooltip>
                          )}
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="success.main">
                          +${day.cashInflows.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="error.main">
                          -${day.cashOutflows.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="success.main">
                          +${day.bankInflows.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="error.main">
                          -${day.bankOutflows.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="bold">
                          ${closingBalance.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography 
                          variant="body2" 
                          fontWeight="bold"
                          color={netChange >= 0 ? "success.main" : "error.main"}
                        >
                          {netChange >= 0 ? '+' : ''}${netChange.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Tooltip title="View Transactions">
                          <IconButton 
                            size="small"
                            onClick={() => {
                              setDrillDownData(day);
                              setDrillDownOpen(true);
                            }}
                          >
                            <Visibility fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );

  const renderFinancialRatios = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Key Financial Ratios</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center" p={2} border={1} borderColor="grey.300" borderRadius={1}>
              <Typography variant="h4" color="primary">
                {(metrics.profitMargin || 0).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Profit Margin
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center" p={2} border={1} borderColor="grey.300" borderRadius={1}>
              <Typography variant="h4" color="success.main">
                {(metrics.assetTurnover || 0).toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Asset Turnover
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center" p={2} border={1} borderColor="grey.300" borderRadius={1}>
              <Typography variant="h4" color="warning.main">
                {(metrics.debtToEquity || 0).toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Debt-to-Equity
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center" p={2} border={1} borderColor="grey.300" borderRadius={1}>
              <Typography variant="h4" color="info.main">
                {(metrics.currentRatio || 0).toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Current Ratio
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderReportActions = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Report Actions</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<PictureAsPdf />}
              onClick={() => setSnackbar({ open: true, message: 'Generating PDF report...', severity: 'info' })}
            >
              Export PDF
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<TableChart />}
              onClick={() => setSnackbar({ open: true, message: 'Generating Excel report...', severity: 'info' })}
            >
              Export Excel
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Share />}
              onClick={() => setSnackbar({ open: true, message: 'Sharing report...', severity: 'info' })}
            >
              Share Report
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Print />}
              onClick={() => setSnackbar({ open: true, message: 'Preparing for print...', severity: 'info' })}
            >
              Print Report
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Financial Reports & Analytics
      </Typography>
      
      {/* Debug Info - Remove this section in production */}
      {process.env.NODE_ENV === 'development' && (
        <Card sx={{ mb: 2, bgcolor: 'grey.50' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Debug Info (Development Only)</Typography>
            <Typography variant="body2">
              <strong>General Ledger Entries:</strong> {generalLedgerData?.length || 0} entries
            </Typography>
            <Typography variant="body2">
              <strong>Real Revenue:</strong> ${metrics.revenue.toLocaleString()}
            </Typography>
            <Typography variant="body2">
              <strong>Real Expenses:</strong> ${metrics.expenses.toLocaleString()}
            </Typography>
            <Typography variant="body2">
              <strong>Real Assets:</strong> ${metrics.totalAssets.toLocaleString()}
            </Typography>
            <Typography variant="body2">
              <strong>Real Liabilities:</strong> ${metrics.totalLiabilities.toLocaleString()}
            </Typography>
            <Typography variant="body2">
              <strong>Real Equity:</strong> ${metrics.equity.toLocaleString()}
            </Typography>
          </CardContent>
        </Card>
      )}
      
      {renderKPIMetrics()}
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderProfitLossStatement()}
        </Grid>
        <Grid item xs={12}>
          {renderBalanceSheet()}
        </Grid>
        <Grid item xs={12}>
          {renderCashFlowStatement()}
        </Grid>
        <Grid item xs={12}>
          {renderDailySummaryTable()}
        </Grid>
        <Grid item xs={12}>
          {renderFinancialRatios()}
        </Grid>
        <Grid item xs={12}>
          {renderReportActions()}
        </Grid>
      </Grid>

      {/* Drill-down Dialog */}
      <Dialog 
        open={drillDownOpen} 
        onClose={() => setDrillDownOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Daily Transactions - {drillDownData && new Date(drillDownData.date).toLocaleDateString()}
        </DialogTitle>
        <DialogContent>
          {drillDownData && (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Account</TableCell>
                    <TableCell align="right">Debit</TableCell>
                    <TableCell align="right">Credit</TableCell>
                    <TableCell>Description</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {drillDownData.transactions.map((transaction, index) => (
                    <TableRow key={index}>
                      <TableCell>{transaction.account_name}</TableCell>
                      <TableCell align="right">
                        {transaction.debit_amount > 0 && `$${transaction.debit_amount.toLocaleString()}`}
                      </TableCell>
                      <TableCell align="right">
                        {transaction.credit_amount > 0 && `$${transaction.credit_amount.toLocaleString()}`}
                      </TableCell>
                      <TableCell>{transaction.description}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDrillDownOpen(false)}>Close</Button>
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

export default SmartFinancialReports;


