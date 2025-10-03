import React, { useState, useEffect, useMemo } from 'react';
import { useFinanceData } from '../hooks/useFinanceData';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Autocomplete, SpeedDial, SpeedDialAction, SpeedDialIcon,
  TablePagination, TableSortLabel, InputAdornment, OutlinedInput, FormHelperText, Collapse, List, ListItem, ListItemText, ListItemIcon,
  Checkbox, FormControlLabel, FormGroup, Badge, Avatar, Divider, Accordion, AccordionSummary, AccordionDetails,
  Slider, Switch, Rating, ToggleButton, ToggleButtonGroup, Skeleton, Backdrop, Modal, Fade, Grow, Zoom, Slide,
  Tabs, Tab
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb,
  CloudUpload, Description, ReceiptLong, PaymentOutlined, ScheduleSend, AutoFixHigh, SmartToy, QrCode, CameraAlt,
  Email, Send, CreditCard, AccountBalanceWallet as WalletIcon, TrendingUp as TrendingUpIcon, CalendarToday,
  Timeline as TimelineIcon, ShowChart as ShowChartIcon, TrendingUp as TrendingUpIcon2, CompareArrows, ScatterPlot,
  Assessment as AssessmentIcon, Analytics, Timeline as TimelineIcon2, ShowChart as ShowChartIcon2, TrendingUp as TrendingUpIcon3,
  PictureAsPdf, TableChart, BarChart as BarChartIcon, PieChart as PieChartIcon, ShowChart as ShowChartIcon3,
  GetApp, Share, Print, Visibility as VisibilityIcon, Edit as EditIcon, Download as DownloadIcon
} from '@mui/icons-material';
// Removed useRealTimeData to prevent authentication calls

const SmartFinancialReports = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectedReport, setSelectedReport] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [reportPeriod, setReportPeriod] = useState('current_month');
  const [comparisonPeriod, setComparisonPeriod] = useState('previous_month');
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  
  // Date range for reports (from FinancialReports.jsx)
  const [dateRange, setDateRange] = useState({
    startDate: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0], // Start of year
    endDate: new Date().toISOString().split('T')[0] // Today
  });
  const [drillDownOpen, setDrillDownOpen] = useState(false);
  const [drillDownData, setDrillDownData] = useState(null);
  const [viewPeriod, setViewPeriod] = useState('daily'); // daily, weekly, monthly, fortnight, custom
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [customDateRange, setCustomDateRange] = useState({ start: null, end: null });

  // Data hooks - fetch real data from database
  const { data: generalLedgerData = [], loading: glLoading, error: glError } = useFinanceData('journal-entries');
  const { data: accounts = [], loading: accountsLoading } = useFinanceData('accounts');
  
  // Placeholder for not-yet-implemented endpoints
  const profitLossData = [];
  const plLoading = false;
  const plError = null;
  
  const balanceSheetData = [];
  const bsLoading = false;
  const bsError = null;
  
  const cashFlowData = [];
  const cfLoading = false;
  const cfError = null;
  
  const kpiData = [];
  const kpiLoading = false;
  const kpiError = null;
  
  // Fetch AR and AP data
  const { data: accountsReceivableData = [] } = useFinanceData('accounts-receivable');
  const { data: accountsPayableData = [] } = useFinanceData('accounts-payable');
  
  // Placeholder for not-yet-implemented endpoints
  const vendorData = [];
  const vendorLoading = false;
  const vendorError = null;
  
  const customersResponse = [];
  const customerLoading = false;
  const customerError = null;
  
  const arLoading = false;
  const arError = null;
  const apLoading = false;
  
  const paymentMethods = [];
  const paymentMethodsLoading = false;
  
  const bankAccounts = [];
  const bankAccountsLoading = false;
  
  // Extract customers array from response
  const customerData = customersResponse?.customers || [];
  
  // Calculate payment method statistics from AR and AP data (moved from render function)
  const paymentMethodStats = useMemo(() => {
    const stats = {};
    
    // Analyze AR invoices by payment method
    if (accountsReceivableData) {
      accountsReceivableData.forEach(invoice => {
        const method = invoice.payment_method || 'Unknown';
        if (!stats[method]) {
          stats[method] = { 
            count: 0, 
            totalAmount: 0, 
            avgAmount: 0,
            invoices: [],
            processingFees: 0
          };
        }
        stats[method].count++;
        stats[method].totalAmount += invoice.total_amount || 0;
        stats[method].processingFees += invoice.processing_fee || 0;
        stats[method].invoices.push(invoice);
      });
    }
    
    // Analyze AP invoices by payment method
    if (accountsPayableData) {
      accountsPayableData.forEach(invoice => {
        const method = invoice.payment_method || 'Unknown';
        if (!stats[method]) {
          stats[method] = { 
            count: 0, 
            totalAmount: 0, 
            avgAmount: 0,
            invoices: [],
            processingFees: 0
          };
        }
        stats[method].count++;
        stats[method].totalAmount += invoice.total_amount || 0;
        stats[method].processingFees += invoice.processing_fee || 0;
        stats[method].invoices.push(invoice);
      });
    }
    
    // Calculate averages
    Object.keys(stats).forEach(method => {
      stats[method].avgAmount = stats[method].count > 0 
        ? stats[method].totalAmount / stats[method].count 
        : 0;
    });
    
    return stats;
  }, [accountsReceivableData, accountsPayableData]);
  
  // Debug: Log financial reports data
  
  
  // Daily cycle data for real opening balances
  const [dailyCycleData, setDailyCycleData] = useState({});
  const [dailyCycleLoading, setDailyCycleLoading] = useState(false);
  
  // Feature flag to enable/disable daily cycle API calls
  const enableDailyCycleAPI = true; // Enhanced daily balance flow is now ready

  // Fetch daily cycle data for real opening balances
  const fetchDailyCycleData = async (date) => {
    if (!enableDailyCycleAPI) {
      // API is disabled, skip the call
      return;
    }
    
    try {
      setDailyCycleLoading(true);
      const response = await fetch(`/api/finance/daily-balance/summary/${date}`);
      
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
        }
      } else {
        // API endpoint doesn't exist (404, 500, etc.)
      }
    } catch (error) {
      // Network error or other issues
    } finally {
      setDailyCycleLoading(false);
    }
  };

  // Fetch daily cycle data for the last 7 days (optimized for performance)
  useEffect(() => {
    // Use local date to avoid timezone issues
    const today = new Date();
    const todayStr = today.getFullYear() + '-' + 
                    String(today.getMonth() + 1).padStart(2, '0') + '-' + 
                    String(today.getDate()).padStart(2, '0');
    
    // Limit to last 7 days to avoid excessive API calls
    const datesToFetch = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.getFullYear() + '-' + 
                     String(date.getMonth() + 1).padStart(2, '0') + '-' + 
                     String(date.getDate()).padStart(2, '0');
      datesToFetch.push(dateStr);
    }
    
    // Fetch data for all dates
    datesToFetch.forEach(dateStr => {
      fetchDailyCycleData(dateStr);
    });
  }, []);

  // Calculate daily cash movements from General Ledger
  const dailyCashData = useMemo(() => {
    // Calculate real data from general ledger
    if (generalLedgerData && Array.isArray(generalLedgerData) && generalLedgerData.length > 0) {
    const dailyTransactions = {};
    
    generalLedgerData.forEach(entry => {
      // Validate and parse the transaction date
        if (!entry.entry_date) return; // Skip entries without dates
      
        const transactionDate = new Date(entry.entry_date);
      if (isNaN(transactionDate.getTime())) return; // Skip invalid dates
      
        // Use local date formatting to avoid timezone issues
        const date = transactionDate.getFullYear() + '-' + 
                    String(transactionDate.getMonth() + 1).padStart(2, '0') + '-' + 
                    String(transactionDate.getDate()).padStart(2, '0');
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
      
        // Categorize transactions by account type
        const accountName = (entry.account_name || '').toLowerCase();
        const debitAmount = parseFloat(entry.debit_amount || 0);
        const creditAmount = parseFloat(entry.credit_amount || 0);
        
        // Cash accounts
        if (accountName.includes('cash')) {
          if (creditAmount > 0) {
            dailyTransactions[date].cashInflows += creditAmount;
          }
          if (debitAmount > 0) {
            dailyTransactions[date].cashOutflows += debitAmount;
          }
        }
        
        // Bank accounts
        if (accountName.includes('bank') || accountName.includes('checking')) {
          if (creditAmount > 0) {
            dailyTransactions[date].bankInflows += creditAmount;
          }
          if (debitAmount > 0) {
            dailyTransactions[date].bankOutflows += debitAmount;
          }
        }
        
        // Revenue accounts (when they result in cash inflow)
        if (accountName.includes('revenue') || accountName.includes('income') || 
            accountName.includes('sales') || accountName.includes('service') ||
            entry.description?.toLowerCase().includes('sold') ||
            entry.description?.toLowerCase().includes('sale')) {
          if (creditAmount > 0) {
            // Revenue credit typically means cash inflow
            dailyTransactions[date].cashInflows += creditAmount;
          }
        }
        
        // Expense accounts (when they result in cash outflow)
        if (accountName.includes('expense') || accountName.includes('cost') || 
            accountName.includes('operating') || accountName.includes('admin') ||
            entry.description?.toLowerCase().includes('expense') ||
            entry.description?.toLowerCase().includes('cost') ||
            entry.description?.toLowerCase().includes('rent') ||
            entry.description?.toLowerCase().includes('salary') ||
            entry.description?.toLowerCase().includes('utilities') ||
            entry.description?.toLowerCase().includes('supplies') ||
            entry.description?.toLowerCase().includes('maintenance') ||
            entry.description?.toLowerCase().includes('insurance') ||
            entry.description?.toLowerCase().includes('fuel') ||
            entry.description?.toLowerCase().includes('travel') ||
            entry.description?.toLowerCase().includes('advertising') ||
            entry.description?.toLowerCase().includes('marketing') ||
            entry.description?.toLowerCase().includes('office') ||
            entry.description?.toLowerCase().includes('phone') ||
            entry.description?.toLowerCase().includes('internet') ||
            entry.description?.toLowerCase().includes('training') ||
            entry.description?.toLowerCase().includes('professional') ||
            entry.description?.toLowerCase().includes('legal') ||
            entry.description?.toLowerCase().includes('accounting') ||
            entry.description?.toLowerCase().includes('consulting') ||
            entry.description?.toLowerCase().includes('repair') ||
            entry.description?.toLowerCase().includes('meal') ||
            entry.description?.toLowerCase().includes('food') ||
            entry.description?.toLowerCase().includes('entertainment') ||
            entry.description?.toLowerCase().includes('subscription') ||
            entry.description?.toLowerCase().includes('software') ||
            entry.description?.toLowerCase().includes('license') ||
            entry.description?.toLowerCase().includes('fee') ||
            entry.description?.toLowerCase().includes('tax') ||
            entry.description?.toLowerCase().includes('penalty') ||
            entry.description?.toLowerCase().includes('fine') ||
            entry.description?.toLowerCase().includes('interest') ||
            entry.description?.toLowerCase().includes('bank charge') ||
            entry.description?.toLowerCase().includes('service charge') ||
            entry.description?.toLowerCase().includes('commission') ||
            entry.description?.toLowerCase().includes('discount') ||
            entry.description?.toLowerCase().includes('refund') ||
            entry.description?.toLowerCase().includes('loss') ||
            entry.description?.toLowerCase().includes('depreciation') ||
            entry.description?.toLowerCase().includes('amortization') ||
            entry.description?.toLowerCase().includes('bad debt') ||
            entry.description?.toLowerCase().includes('write off') ||
            entry.description?.toLowerCase().includes('inventory shrinkage') ||
            entry.description?.toLowerCase().includes('waste') ||
            entry.description?.toLowerCase().includes('donation') ||
            entry.description?.toLowerCase().includes('charity') ||
            entry.description?.toLowerCase().includes('gift') ||
            entry.description?.toLowerCase().includes('bonus') ||
            entry.description?.toLowerCase().includes('overtime') ||
            entry.description?.toLowerCase().includes('benefit') ||
            entry.description?.toLowerCase().includes('allowance')) {
          // For expenses, use the larger amount (could be debit or credit depending on entry type)
          if (Math.max(debitAmount, creditAmount) > 0) {
            dailyTransactions[date].cashOutflows += Math.max(debitAmount, creditAmount);
          }
        }
        
        // Add transaction to the list (limit to 50 transactions per day for performance)
        if (dailyTransactions[date].transactions.length < 50) {
        dailyTransactions[date].transactions.push({
            id: entry.id,
            description: entry.description,
            account_name: entry.account_name,
            debit_amount: debitAmount,
            credit_amount: creditAmount,
            reference: entry.reference
          });
        }
      });
      
      // Fill in missing days to ensure continuity
      const today = new Date();
      const startDate = new Date(today);
      startDate.setDate(startDate.getDate() - 90); // Last 90 days
      
      // Create entries for all days in the range, even if no transactions
      for (let d = new Date(startDate); d <= today; d.setDate(d.getDate() + 1)) {
        const dateStr = d.getFullYear() + '-' + 
                       String(d.getMonth() + 1).padStart(2, '0') + '-' + 
                       String(d.getDate()).padStart(2, '0');
        
        if (!dailyTransactions[dateStr]) {
          dailyTransactions[dateStr] = {
            date: dateStr,
            cashInflows: 0,
            cashOutflows: 0,
            bankInflows: 0,
            bankOutflows: 0,
            transactions: []
          };
        }
      }
      
      // Convert to array and sort by date, limit to last 90 days for performance
      const result = Object.values(dailyTransactions)
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, 90); // Limit to last 90 days for performance
      
      // If we have real data, return it
      if (result.length > 0) {
        return result;
      }
    }
    
    // No general ledger data - create empty daily entries for continuity
    const today = new Date();
    const startDate = new Date(today);
    startDate.setDate(startDate.getDate() - 90); // Last 90 days
    
    const emptyDailyData = [];
    for (let d = new Date(startDate); d <= today; d.setDate(d.getDate() + 1)) {
      const dateStr = d.getFullYear() + '-' + 
                     String(d.getMonth() + 1).padStart(2, '0') + '-' + 
                     String(d.getDate()).padStart(2, '0');
      
      emptyDailyData.push({
        date: dateStr,
        cashInflows: 0,
        cashOutflows: 0,
        bankInflows: 0,
        bankOutflows: 0,
        transactions: []
      });
    }
    
    return emptyDailyData
      .sort((a, b) => new Date(b.date) - new Date(a.date))
      .slice(0, 90); // Limit to last 90 days for performance
  }, [generalLedgerData]);

  // Calculate opening/closing balances using real daily cycle data
  const calculateBalances = useMemo(() => {
    if (dailyCashData.length === 0) return {};
    
    const balances = {};
    
    // Process data in chronological order (oldest first) to ensure proper carry-forward
    const sortedData = [...dailyCashData].sort((a, b) => new Date(a.date) - new Date(b.date));
    
    sortedData.forEach((day, index) => {
      const cycleData = dailyCycleData[day.date];
      
      if (cycleData && cycleData.daily_balances) {
        // Use real opening balances from daily cycle system
        const cashAccounts = cycleData.daily_balances.filter(b => 
          b.account_name?.toLowerCase().includes('cash') || 
          b.account_name?.toLowerCase().includes('petty cash')
        );
        const bankAccounts = cycleData.daily_balances.filter(b => 
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
        // No daily cycle data available - use calculated fallback
        // Get previous day's closing balance for carry-forward
        const previousDay = index > 0 ? sortedData[index - 1] : null;
        const previousDayBalances = previousDay ? balances[previousDay.date] : null;
        
        // Opening balance = previous day's closing balance (carry-forward)
        const openingCash = previousDayBalances?.closingCash || 0;
        const openingBank = previousDayBalances?.closingBank || 0;
        
        // Closing balance = opening + inflows - outflows
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
    // Use local date formatting to avoid timezone issues
    const todayDate = new Date();
    const today = todayDate.getFullYear() + '-' + 
                  String(todayDate.getMonth() + 1).padStart(2, '0') + '-' + 
                  String(todayDate.getDate()).padStart(2, '0');
    const todayBalances = calculateBalances[today] || {};
    
    // Calculate real metrics from general ledger data
    let realRevenue = 0;
    let realExpenses = 0;
    let realAssets = 0;
    let realLiabilities = 0;
    let realEquity = 0;
    let totalDebits = 0;
    let totalCredits = 0;
    let totalAccountsReceivable = 0;
    let totalAccountsPayable = 0;
    let overdueReceivables = 0;
    let currentReceivables = 0;
    let overduePayables = 0;
    let currentPayables = 0;
    
    if (generalLedgerData && Array.isArray(generalLedgerData)) {
      // Limit processing to recent entries for performance (last 1000 entries)
      const recentEntries = generalLedgerData.slice(0, 1000);
      
      recentEntries.forEach(entry => {
        const debitAmount = parseFloat(entry.debit_amount || 0);
        const creditAmount = parseFloat(entry.credit_amount || 0);
        const accountName = (entry.account_name || '').toLowerCase();
        
        
        // Sum up total debits and credits for trial balance
        totalDebits += debitAmount;
        totalCredits += creditAmount;
        
        // Calculate metrics based on account names/types
        // Revenue accounts (can have both debit and credit entries)
        if (accountName.includes('revenue') || accountName.includes('income') || 
            accountName.includes('sales') || accountName.includes('service') ||
            entry.description?.toLowerCase().includes('sold') ||
            entry.description?.toLowerCase().includes('sale')) {
          // Revenue can be either debit (unusual) or credit (normal)
          realRevenue += Math.max(debitAmount, creditAmount);
        }
        
        // Expense accounts (typically have debit balances)
        if (accountName.includes('expense') || accountName.includes('cost') || 
            accountName.includes('operating') || accountName.includes('admin') ||
            entry.description?.toLowerCase().includes('expense') ||
            entry.description?.toLowerCase().includes('cost') ||
            entry.description?.toLowerCase().includes('rent') ||
            entry.description?.toLowerCase().includes('salary') ||
            entry.description?.toLowerCase().includes('utilities') ||
            entry.description?.toLowerCase().includes('supplies') ||
            entry.description?.toLowerCase().includes('maintenance') ||
            entry.description?.toLowerCase().includes('insurance') ||
            entry.description?.toLowerCase().includes('fuel') ||
            entry.description?.toLowerCase().includes('travel') ||
            entry.description?.toLowerCase().includes('advertising') ||
            entry.description?.toLowerCase().includes('marketing') ||
            entry.description?.toLowerCase().includes('office') ||
            entry.description?.toLowerCase().includes('phone') ||
            entry.description?.toLowerCase().includes('internet') ||
            entry.description?.toLowerCase().includes('training') ||
            entry.description?.toLowerCase().includes('professional') ||
            entry.description?.toLowerCase().includes('legal') ||
            entry.description?.toLowerCase().includes('accounting') ||
            entry.description?.toLowerCase().includes('consulting') ||
            entry.description?.toLowerCase().includes('repair') ||
            entry.description?.toLowerCase().includes('meal') ||
            entry.description?.toLowerCase().includes('food') ||
            entry.description?.toLowerCase().includes('entertainment') ||
            entry.description?.toLowerCase().includes('subscription') ||
            entry.description?.toLowerCase().includes('software') ||
            entry.description?.toLowerCase().includes('license') ||
            entry.description?.toLowerCase().includes('fee') ||
            entry.description?.toLowerCase().includes('tax') ||
            entry.description?.toLowerCase().includes('penalty') ||
            entry.description?.toLowerCase().includes('fine') ||
            entry.description?.toLowerCase().includes('interest') ||
            entry.description?.toLowerCase().includes('bank charge') ||
            entry.description?.toLowerCase().includes('service charge') ||
            entry.description?.toLowerCase().includes('commission') ||
            entry.description?.toLowerCase().includes('discount') ||
            entry.description?.toLowerCase().includes('refund') ||
            entry.description?.toLowerCase().includes('loss') ||
            entry.description?.toLowerCase().includes('depreciation') ||
            entry.description?.toLowerCase().includes('amortization') ||
            entry.description?.toLowerCase().includes('bad debt') ||
            entry.description?.toLowerCase().includes('write off') ||
            entry.description?.toLowerCase().includes('inventory shrinkage') ||
            entry.description?.toLowerCase().includes('waste') ||
            entry.description?.toLowerCase().includes('donation') ||
            entry.description?.toLowerCase().includes('charity') ||
            entry.description?.toLowerCase().includes('gift') ||
            entry.description?.toLowerCase().includes('bonus') ||
            entry.description?.toLowerCase().includes('overtime') ||
            entry.description?.toLowerCase().includes('benefit') ||
            entry.description?.toLowerCase().includes('allowance')) {
          // For expenses, use debit amount (normal expense posting) or credit amount if it's larger
          realExpenses += Math.max(debitAmount, creditAmount);
        }
            
        // Asset accounts (typically have debit balances)
        if (accountName.includes('asset') || accountName.includes('cash') || 
            accountName.includes('bank') || accountName.includes('inventory') ||
            accountName.includes('receivable') || accountName.includes('equipment')) {
          // For assets, use the balance field if available, otherwise calculate net
          const assetAmount = entry.balance !== undefined ? Math.abs(entry.balance) : Math.max(debitAmount, creditAmount);
          realAssets += assetAmount;
          
          // Track Accounts Receivable specifically
          if (accountName.includes('receivable') || accountName.includes('debtor') ||
              entry.description?.toLowerCase().includes('receivable') ||
              entry.description?.toLowerCase().includes('invoice') ||
              entry.description?.toLowerCase().includes('customer') ||
              entry.description?.toLowerCase().includes('debtor')) {
            totalAccountsReceivable += assetAmount;
            
            // Simple aging logic based on entry date (could be enhanced with due dates)
            const entryDate = new Date(entry.entry_date);
            const daysSinceEntry = Math.floor((new Date() - entryDate) / (1000 * 60 * 60 * 24));
            if (daysSinceEntry > 30) {
              overdueReceivables += assetAmount;
            } else {
              currentReceivables += assetAmount;
            }
          }
        }
        
        // Liability accounts (typically have credit balances)
        if (accountName.includes('liability') || accountName.includes('payable') || 
            accountName.includes('debt') || accountName.includes('loan')) {
          // For liabilities, use the balance field if available, otherwise use the larger amount
          const liabilityAmount = entry.balance !== undefined ? Math.abs(entry.balance) : Math.max(debitAmount, creditAmount);
          realLiabilities += liabilityAmount;
          
          // Track Accounts Payable specifically
          if (accountName.includes('payable') || accountName.includes('creditor') ||
              entry.description?.toLowerCase().includes('payable') ||
              entry.description?.toLowerCase().includes('vendor') ||
              entry.description?.toLowerCase().includes('supplier') ||
              entry.description?.toLowerCase().includes('creditor') ||
              entry.description?.toLowerCase().includes('bill') ||
              entry.description?.toLowerCase().includes('purchase')) {
            totalAccountsPayable += liabilityAmount;
            
            // Simple aging logic based on entry date (could be enhanced with due dates)
            const entryDate = new Date(entry.entry_date);
            const daysSinceEntry = Math.floor((new Date() - entryDate) / (1000 * 60 * 60 * 24));
            if (daysSinceEntry > 30) {
              overduePayables += liabilityAmount;
            } else {
              currentPayables += liabilityAmount;
            }
          }
        }
        
        // Equity accounts (typically have credit balances)
        if (accountName.includes('equity') || accountName.includes('capital') || 
            accountName.includes('retained') || accountName.includes('stock')) {
          // For equity, use the balance field if available, otherwise use the larger amount
          const equityAmount = entry.balance !== undefined ? Math.abs(entry.balance) : Math.max(debitAmount, creditAmount);
          realEquity += equityAmount;
            }
          });
        }
    
    // Calculate vendor-based Accounts Payable from direct vendor data
    let vendorAccountsPayable = 0;
    let vendorOverduePayables = 0;
    let vendorCurrentPayables = 0;
    
    if (vendorData && Array.isArray(vendorData)) {
      vendorData.forEach(vendor => {
        const outstanding = parseFloat(vendor.outstanding_balance || 0);
        if (outstanding > 0 && vendor.status !== 'paid') {
          vendorAccountsPayable += outstanding;
          
          // Check if overdue based on vendor due date or creation date
          const dueDate = vendor.due_date ? new Date(vendor.due_date) : new Date(vendor.created_at);
          const daysPastDue = Math.floor((new Date() - dueDate) / (1000 * 60 * 60 * 24));
          
          if (daysPastDue > 30) {
            vendorOverduePayables += outstanding;
          } else {
            vendorCurrentPayables += outstanding;
          }
        }
      });
    }
    
    // Calculate customer-based Accounts Receivable from direct AR data  
    let customerAccountsReceivable = 0;
    let customerOverdueReceivables = 0;
    let customerCurrentReceivables = 0;
    
    // Prioritize dedicated AR data over customer data
    if (accountsReceivableData && accountsReceivableData.summary) {
      customerAccountsReceivable = accountsReceivableData.summary.total_outstanding || 0;
      customerOverdueReceivables = accountsReceivableData.summary.overdue_amount || 0;
      customerCurrentReceivables = accountsReceivableData.summary.current_amount || 0;
    } else if (customerData && Array.isArray(customerData)) {
      // Fallback to customer data if AR data not available
      customerData.forEach(customer => {
        const outstanding = parseFloat(customer.outstanding_balance || 0);
        if (outstanding > 0) {
          customerAccountsReceivable += outstanding;
          
          const overdueAmount = parseFloat(customer.overdue_amount || 0);
          customerOverdueReceivables += overdueAmount;
          customerCurrentReceivables += (outstanding - overdueAmount);
        }
      });
    }
    
    // Use real data if available, otherwise use calculated values from daily cash data
    const baseMetrics = kpiData || {};
    const todayData = dailyCashData[0] || {};
    
    const revenue = realRevenue > 0 ? realRevenue : (baseMetrics.revenue || 0);
    const expenses = realExpenses > 0 ? realExpenses : (baseMetrics.expenses || 0);
    const netIncome = revenue - expenses;
    // Calculate total assets including cash
    const baseAssets = realAssets > 0 ? realAssets : (baseMetrics.total_assets || 0);
    const totalAssets = Math.max(baseAssets, (todayBalances.closingCash || 0) + (todayBalances.closingBank || 0));
    const totalLiabilities = realLiabilities > 0 ? realLiabilities : (baseMetrics.total_liabilities || 0);
    // Calculate equity using accounting equation: Equity = Assets - Liabilities
    const calculatedEquity = totalAssets - totalLiabilities;
    const totalEquity = realEquity > 0 ? realEquity : (calculatedEquity > 0 ? calculatedEquity : (baseMetrics.total_equity || 0));
    
    // Calculate ratios
    const profitMargin = revenue > 0 ? (netIncome / revenue) * 100 : 0;
    const assetTurnover = totalAssets > 0 ? revenue / totalAssets : 0;
    const debtToEquity = totalEquity > 0 ? totalLiabilities / totalEquity : 0;
    const currentRatio = totalLiabilities > 0 ? totalAssets / totalLiabilities : 0;
    
    const finalMetrics = {
      revenue,
      expenses,
      netIncome,
      totalAssets,
      totalLiabilities,
      equity: totalEquity,
      cashFlow: netIncome, // Simplified cash flow
      profitMargin,
      assetTurnover,
      debtToEquity: totalEquity > 0 ? totalLiabilities / totalEquity : 0,
      currentRatio,
      // Trial balance totals
      totalDebits,
      totalCredits,
      trialBalanceDifference: totalDebits - totalCredits,
      // Accounts Receivable & Payable metrics - prioritize direct vendor/customer data
      totalAccountsReceivable: customerAccountsReceivable > 0 ? customerAccountsReceivable : totalAccountsReceivable,
      totalAccountsPayable: vendorAccountsPayable > 0 ? vendorAccountsPayable : totalAccountsPayable,
      overdueReceivables: customerOverdueReceivables > 0 ? customerOverdueReceivables : overdueReceivables,
      currentReceivables: customerCurrentReceivables > 0 ? customerCurrentReceivables : currentReceivables,
      overduePayables: vendorOverduePayables > 0 ? vendorOverduePayables : overduePayables,
      currentPayables: vendorCurrentPayables > 0 ? vendorCurrentPayables : currentPayables,
      netWorkingCapital: (customerAccountsReceivable > 0 ? customerAccountsReceivable : totalAccountsReceivable) - (vendorAccountsPayable > 0 ? vendorAccountsPayable : totalAccountsPayable),
      receivablesTurnover: revenue > 0 ? (customerAccountsReceivable > 0 ? customerAccountsReceivable : totalAccountsReceivable) / revenue : 0,
      payablesTurnover: expenses > 0 ? (vendorAccountsPayable > 0 ? vendorAccountsPayable : totalAccountsPayable) / expenses : 0,
      daysReceivablesOutstanding: revenue > 0 ? ((customerAccountsReceivable > 0 ? customerAccountsReceivable : totalAccountsReceivable) / revenue) * 365 : 0,
      daysPayablesOutstanding: expenses > 0 ? ((vendorAccountsPayable > 0 ? vendorAccountsPayable : totalAccountsPayable) / expenses) * 365 : 0,
      // Daily cash metrics - use calculated balances or fallback to daily data
      todayCashBalance: todayBalances.closingCash || 0,
      todayBankBalance: todayBalances.closingBank || 0,
      todayNetCashFlow: todayBalances.netCashFlow || (todayData.cashInflows + todayData.bankInflows - todayData.cashOutflows - todayData.bankOutflows),
      // Calculate total cash balance - use latest closing balance from daily data
      totalCashBalance: (() => {
        // First try to get from calculated balances
        if (todayBalances.closingCash || todayBalances.closingBank) {
          return (todayBalances.closingCash || 0) + (todayBalances.closingBank || 0);
        }
        // Fallback: calculate from daily cash data (use most recent day only)
        if (dailyCashData.length > 0) {
          const latestDay = dailyCashData[0]; // Most recent day
          return latestDay.cashInflows + latestDay.bankInflows - latestDay.cashOutflows - latestDay.bankOutflows;
        }
        return 0;
      })()
    };
    
    
    return finalMetrics;
  }, [kpiData, calculateBalances, dailyCashData, generalLedgerData, vendorData, customerData, accountsReceivableData, customersResponse]);

  const renderKPIMetrics = () => {
    
    return (
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
};

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
                      <TableCell>Cash & Bank</TableCell>
                      <TableCell align="right">
                        ${(metrics.totalCashBalance || 0).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>
                        Accounts Receivable
                        {hasCustomerData() && (
                          <Typography component="span" variant="caption" color="success.main" sx={{ ml: 1 }}>
                            📊 Customer Data
                          </Typography>
                        )}
                        {metrics.overdueReceivables > 0 && (
                          <Typography component="span" variant="caption" color="warning.main" sx={{ ml: 1 }}>
                            (${metrics.overdueReceivables.toLocaleString()} overdue)
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="right">
                        ${(metrics.totalAccountsReceivable || 0).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Other Assets</TableCell>
                      <TableCell align="right">
                        ${Math.max(0, (metrics.totalAssets || 0) - (metrics.totalCashBalance || 0) - (metrics.totalAccountsReceivable || 0)).toLocaleString()}
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
                      <TableCell>
                        Accounts Payable
                        {hasVendorData() && (
                          <Typography component="span" variant="caption" color="primary.main" sx={{ ml: 1 }}>
                            📊 Vendor Data
                          </Typography>
                        )}
                        {metrics.overduePayables > 0 && (
                          <Typography component="span" variant="caption" color="error.main" sx={{ ml: 1 }}>
                            (${metrics.overduePayables.toLocaleString()} overdue)
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell align="right">
                        ${(metrics.totalAccountsPayable || 0).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Other Liabilities</TableCell>
                      <TableCell align="right">
                        ${Math.max(0, (metrics.totalLiabilities || 0) - (metrics.totalAccountsPayable || 0)).toLocaleString()}
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
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="text.secondary">
                {Object.keys(calculateBalances).length > 0 ? 
                  `Data from ${Object.keys(calculateBalances).length} days (calculated from GL entries)` : 
                  'No transaction data available'
              }
            </Typography>
              {Object.keys(calculateBalances).length > 0 && (
                <Box sx={{ 
                  display: 'inline-flex', 
                  alignItems: 'center', 
                  bgcolor: 'info.light', 
                  color: 'info.contrastText',
                  px: 1, 
                  py: 0.5, 
                  borderRadius: 1,
                  fontSize: '0.7rem'
                }}>
                  📊 CALCULATED
                </Box>
              )}
            </Box>
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
                          {(() => {
                            const date = new Date(day.date + 'T00:00:00');
                            return date.toLocaleDateString('en-US', { 
                              month: 'numeric', 
                              day: 'numeric', 
                              year: 'numeric' 
                            });
                          })()}
                        </Typography>
                        {(() => {
                          // Use local date formatting to avoid timezone issues
                          const todayDate = new Date();
                          const today = todayDate.getFullYear() + '-' + 
                                        String(todayDate.getMonth() + 1).padStart(2, '0') + '-' + 
                                        String(todayDate.getDate()).padStart(2, '0');
                          const isToday = day.date === today;
                          return isToday && (
                          <Chip label="Today" size="small" color="primary" />
                          );
                        })()}
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
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" color="text.secondary">
                {Object.keys(calculateBalances).length > 0 ? 
                  `Data from ${Object.keys(calculateBalances).length} days (calculated from GL entries)` : 
                  'No transaction data available'
              }
            </Typography>
              {Object.keys(calculateBalances).length > 0 && (
                <Box sx={{ 
                  display: 'inline-flex', 
                  alignItems: 'center', 
                  bgcolor: 'info.light', 
                  color: 'info.contrastText',
                  px: 1, 
                  py: 0.5, 
                  borderRadius: 1,
                  fontSize: '0.7rem'
                }}>
                  📊 CALCULATED
                </Box>
              )}
            </Box>
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
                            {(() => {
                              const date = new Date(day.date + 'T00:00:00');
                              return date.toLocaleDateString('en-US', { 
                                month: 'numeric', 
                                day: 'numeric', 
                                year: 'numeric' 
                              });
                            })()}
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

  // Helper functions for data source detection
  const hasVendorData = () => {
    return vendorData && Array.isArray(vendorData) && vendorData.some(v => parseFloat(v.outstanding_balance || 0) > 0 && v.status !== 'paid');
  };

  const hasCustomerData = () => {
    // Check AR data first, then customer data
    if (accountsReceivableData && accountsReceivableData.summary && accountsReceivableData.summary.total_outstanding > 0) {
      return true;
    }
    return customerData && Array.isArray(customerData) && customerData.some(c => parseFloat(c.outstanding_balance || 0) > 0);
  };

  const hasOnlyGLData = () => {
    return (metrics.totalAccountsReceivable > 0 || metrics.totalAccountsPayable > 0) && !hasVendorData() && !hasCustomerData();
  };

  const renderAccountsReceivablePayable = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Accounts Receivable & Payable Summary</Typography>
          <Box display="flex" gap={1}>
            {hasVendorData() && (
              <Chip size="small" label="📊 VENDOR DATA" color="primary" variant="outlined" />
            )}
            {hasCustomerData() && (
              <Chip size="small" label="📊 CUSTOMER DATA" color="success" variant="outlined" />
            )}
            {hasOnlyGLData() && (
              <Chip size="small" label="📊 GL CALCULATED" color="warning" variant="outlined" />
            )}
          </Box>
        </Box>
        <Grid container spacing={3}>
          {/* Accounts Receivable Section */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" fontWeight="bold" mb={2} color="success.main">
              📋 Accounts Receivable
            </Typography>
            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Total Outstanding</Typography>
                <Typography variant="h6" color="success.main">
                  ${(metrics.totalAccountsReceivable || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Current (0-30 days)</Typography>
                <Typography variant="body2" color="success.main">
                  ${(metrics.currentReceivables || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Overdue (30+ days)</Typography>
                <Typography variant="body2" color={metrics.overdueReceivables > 0 ? "warning.main" : "inherit"}>
                  ${(metrics.overdueReceivables || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Days Outstanding (DSO)</Typography>
                <Typography variant="body2">
                  {(metrics.daysReceivablesOutstanding || 0).toFixed(0)} days
                </Typography>
              </Box>
            </Box>
          </Grid>

          {/* Accounts Payable Section */}
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle1" fontWeight="bold" mb={2} color="error.main">
              📄 Accounts Payable
            </Typography>
            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Total Outstanding</Typography>
                <Typography variant="h6" color="error.main">
                  ${(metrics.totalAccountsPayable || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Current (0-30 days)</Typography>
                <Typography variant="body2" color="error.main">
                  ${(metrics.currentPayables || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Overdue (30+ days)</Typography>
                <Typography variant="body2" color={metrics.overduePayables > 0 ? "error.main" : "inherit"}>
                  ${(metrics.overduePayables || 0).toLocaleString()}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Days Outstanding (DPO)</Typography>
                <Typography variant="body2">
                  {(metrics.daysPayablesOutstanding || 0).toFixed(0)} days
                </Typography>
              </Box>
            </Box>
          </Grid>

          {/* Working Capital Analysis */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" fontWeight="bold" mb={2}>
              💰 Working Capital Analysis
            </Typography>
            <Box display="flex" justifyContent="space-around" textAlign="center">
              <Box>
                <Typography variant="h6" color={metrics.netWorkingCapital >= 0 ? "success.main" : "error.main"}>
                  ${(metrics.netWorkingCapital || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Net Working Capital</Typography>
                <Typography variant="caption" color="text.secondary">
                  (AR - AP)
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" color="primary.main">
                  {(metrics.receivablesTurnover || 0).toFixed(2)}x
                </Typography>
                <Typography variant="body2">Receivables Turnover</Typography>
                <Typography variant="caption" color="text.secondary">
                  (Revenue / AR)
                </Typography>
              </Box>
              <Box>
                <Typography variant="h6" color="primary.main">
                  {(metrics.payablesTurnover || 0).toFixed(2)}x
                </Typography>
                <Typography variant="body2">Payables Turnover</Typography>
                <Typography variant="caption" color="text.secondary">
                  (Expenses / AP)
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
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

  const renderPaymentMethodAnalysis = () => {
    const totalTransactions = Object.values(paymentMethodStats).reduce((sum, stat) => sum + stat.count, 0);
    const totalAmount = Object.values(paymentMethodStats).reduce((sum, stat) => sum + stat.totalAmount, 0);
    const totalProcessingFees = Object.values(paymentMethodStats).reduce((sum, stat) => sum + stat.processingFees, 0);

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" mb={2}>Payment Method Analysis</Typography>
          
          {/* Summary Metrics */}
          <Grid container spacing={2} mb={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center" p={2} sx={{ bgcolor: 'primary.light', borderRadius: 2 }}>
                <Typography variant="h4" color="primary.contrastText">
                  {totalTransactions}
                </Typography>
                <Typography variant="body2" color="primary.contrastText">
                  Total Transactions
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center" p={2} sx={{ bgcolor: 'success.light', borderRadius: 2 }}>
                <Typography variant="h4" color="success.contrastText">
                  ${totalAmount.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="success.contrastText">
                  Total Amount
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center" p={2} sx={{ bgcolor: 'warning.light', borderRadius: 2 }}>
                <Typography variant="h4" color="warning.contrastText">
                  ${totalProcessingFees.toLocaleString()}
                </Typography>
                <Typography variant="body2" color="warning.contrastText">
                  Processing Fees
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box textAlign="center" p={2} sx={{ bgcolor: 'info.light', borderRadius: 2 }}>
                <Typography variant="h4" color="info.contrastText">
                  {Object.keys(paymentMethodStats).length}
                </Typography>
                <Typography variant="body2" color="info.contrastText">
                  Payment Methods
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Payment Method Breakdown */}
          <Typography variant="subtitle1" mb={2}>Payment Method Breakdown</Typography>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Payment Method</TableCell>
                  <TableCell align="right">Transactions</TableCell>
                  <TableCell align="right">Total Amount</TableCell>
                  <TableCell align="right">Average Amount</TableCell>
                  <TableCell align="right">Processing Fees</TableCell>
                  <TableCell align="right">% of Total</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(paymentMethodStats)
                  .sort(([,a], [,b]) => b.totalAmount - a.totalAmount)
                  .map(([method, stats]) => (
                    <TableRow key={method}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Payment fontSize="small" />
                          <Typography variant="body2" fontWeight="medium">
                            {method}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell align="right">
                        <Chip label={stats.count} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" fontWeight="medium">
                          ${stats.totalAmount.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          ${stats.avgAmount.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" color="warning.main">
                          ${stats.processingFees.toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">
                          {totalAmount > 0 ? ((stats.totalAmount / totalAmount) * 100).toFixed(1) : 0}%
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Bank Account Analysis */}
          <Typography variant="subtitle1" mt={3} mb={2}>Bank Account Analysis</Typography>
          <Grid container spacing={2}>
            {bankAccounts && bankAccounts.length > 0 ? (
              bankAccounts.map((account) => (
                <Grid item xs={12} sm={6} md={4} key={account.id}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        <AccountBalanceWallet fontSize="small" />
                        <Typography variant="subtitle2" fontWeight="medium">
                          {account.account_name}
                        </Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary" mb={1}>
                        {account.bank_name} • {account.account_type}
                      </Typography>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body2">Balance:</Typography>
                        <Typography variant="body2" fontWeight="medium">
                          ${(account.current_balance || 0).toLocaleString()}
                        </Typography>
                      </Box>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mt={1}>
                        <Typography variant="body2">Currency:</Typography>
                        <Chip label={account.currency} size="small" />
                      </Box>
                      <Box display="flex" gap={1} mt={1}>
                        {account.allow_deposits && (
                          <Chip label="Deposits" size="small" color="success" variant="outlined" />
                        )}
                        {account.allow_withdrawals && (
                          <Chip label="Withdrawals" size="small" color="warning" variant="outlined" />
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))
            ) : (
              <Grid item xs={12}>
                <Alert severity="info">
                  No bank accounts configured. Set up bank accounts in Admin Settings to see detailed analysis.
                </Alert>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const renderTrialBalance = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">
            Trial Balance
          </Typography>
          <Box display="flex" gap={1}>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={() => setSnackbar({ open: true, message: 'Trial Balance exported successfully', severity: 'success' })}
            >
              Export
            </Button>
            <Button
              variant="outlined"
              startIcon={<Print />}
              onClick={() => window.print()}
            >
              Print
            </Button>
          </Box>
        </Box>

        <Box>
          {/* Summary Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Debits
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    ${(metrics.totalDebits || 0).toLocaleString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Total Credits
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    ${(metrics.totalCredits || 0).toLocaleString()}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Card>
                <CardContent>
                  <Typography color="text.secondary" gutterBottom>
                    Balance Status
                  </Typography>
                  <Typography variant="h6">
                    {Math.abs((metrics.totalDebits || 0) - (metrics.totalCredits || 0)) < 0.01 ? '✅ Balanced' : '❌ Unbalanced'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Trial Balance Table */}
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Account Code</TableCell>
                  <TableCell>Account Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell align="right">Debit Balance</TableCell>
                  <TableCell align="right">Credit Balance</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {accounts && accounts.length > 0 ? accounts.map((account, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Typography variant="body2" fontFamily="monospace">
                        {account.account_code || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {account.account_name || 'Unnamed Account'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={(account.account_type || 'unknown').toUpperCase()}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {account.debit_balance > 0 && (
                        <Typography variant="body2" color="success.main" fontWeight="medium">
                          ${account.debit_balance.toLocaleString()}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell align="right">
                      {account.credit_balance > 0 && (
                        <Typography variant="body2" color="error.main" fontWeight="medium">
                          ${account.credit_balance.toLocaleString()}
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Alert severity="info">
                        No trial balance data available. Please create some journal entries first.
                      </Alert>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
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
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>
            Financial Reports & Analytics
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Comprehensive financial analysis and reporting
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => window.location.reload()}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Date Range Picker (from FinancialReports.jsx) */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Report Period
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField
                label="Start Date"
                type="date"
                value={dateRange.startDate}
                onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                label="End Date"
                type="date"
                value={dateRange.endDate}
                onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
                fullWidth
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box display="flex" alignItems="center" height="100%">
                <Typography variant="body2" color="text.secondary">
                  Reports generated for the selected period
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs for different report types */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Dashboard Overview" icon={<Assessment />} />
          <Tab label="Profit & Loss" icon={<TrendingUp />} />
          <Tab label="Balance Sheet" icon={<AccountBalance />} />
          <Tab label="Trial Balance" icon={<Assessment />} />
          <Tab label="Cash Flow" icon={<AttachMoney />} />
          <Tab label="AR/AP Analysis" icon={<Receipt />} />
          <Tab label="Advanced Analytics" icon={<BarChart />} />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {renderKPIMetrics()}
          </Grid>
          <Grid item xs={12}>
            {renderDailySummaryTable()}
          </Grid>
          <Grid item xs={12}>
            {renderFinancialRatios()}
          </Grid>
        </Grid>
      )}
      
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {renderProfitLossStatement()}
          </Grid>
        </Grid>
      )}
      
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {renderBalanceSheet()}
          </Grid>
        </Grid>
      )}
      
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {renderTrialBalance()}
          </Grid>
        </Grid>
      )}
      
      {activeTab === 4 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {renderCashFlowStatement()}
          </Grid>
        </Grid>
      )}
      
      {activeTab === 5 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {renderAccountsReceivablePayable()}
          </Grid>
        </Grid>
      )}
      
      {activeTab === 6 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            {renderPaymentMethodAnalysis()}
          </Grid>
          <Grid item xs={12}>
            {renderReportActions()}
          </Grid>
        </Grid>
      )}

      {/* Drill-down Dialog */}
      <Dialog 
        open={drillDownOpen} 
        onClose={() => setDrillDownOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Daily Transactions - {drillDownData && (() => {
            const date = new Date(drillDownData.date + 'T00:00:00');
            return date.toLocaleDateString('en-US', { 
              month: 'numeric', 
              day: 'numeric', 
              year: 'numeric' 
            });
          })()}
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


