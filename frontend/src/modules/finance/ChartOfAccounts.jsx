import React, { useState, useMemo, useEffect } from 'react';
import apiClient from '../../services/apiClient';
import { 
  Box, 
  Tabs, 
  Tab, 
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Typography,
  Chip,
  Card,
  CardContent,
  Grid,
  Checkbox,
  FormControlLabel,
  Switch,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Toolbar,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Snackbar,
  TextField,
  InputAdornment,
  Divider,
  Stack,
  Drawer,
  Badge,
  Radio,
  RadioGroup,
  FormLabel,
  Collapse,
  FormControl,
  Select,
  InputLabel
} from '@mui/material';
import { 
  Add as AddIcon,
  Settings as SettingsIcon,
  AutoAwesome as MagicIcon,
  Refresh as RefreshIcon,
  Lightbulb as LightbulbIcon,
  MoreVert as MoreVertIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  FilterList as FilterIcon,
  CheckBox as CheckBoxIcon,
  CheckBoxOutlineBlank as CheckBoxOutlineBlankIcon,
  Work as WorkIcon,
  List as ListIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Insights as InsightsIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { CoAProvider, useCoA } from './context/CoAContext';
import CoATree from './components/CoATree';
import CoATreeEnhanced from './components/CoATreeEnhanced';
import CoAForm from './forms/CoAForm';
import FinanceTableDisplay from '../../components/tables/FinanceTableDisplay';
import ProgressiveCoA from './components/ProgressiveCoA';

const ChartOfAccountsContent = () => {
  const { 
    accounts, 
    loading, 
    error,
    viewMode, 
    setViewMode,
    deleteAccount,
    updateAccount
  } = useCoA();

  // Format amount helper
  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount || 0);
  };
  
  const [openDialog, setOpenDialog] = useState(false);
  const [currentAccount, setCurrentAccount] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [selectedAccountDetails, setSelectedAccountDetails] = useState(null);
  const [showDetailsPanel, setShowDetailsPanel] = useState(false);
  const [selectedAccounts, setSelectedAccounts] = useState(new Set());
  const [showOnlySelected, setShowOnlySelected] = useState(false);
  const [sortBy, setSortBy] = useState('code');
  const [sortDirection, setSortDirection] = useState('asc');
  const [actionMenuAnchor, setActionMenuAnchor] = useState(null);
  const [coaViewMode, setCoaViewMode] = useState('progressive'); // 'progressive', 'table', 'tree'
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [accountsLoaded, setAccountsLoaded] = useState(false);
  const [apiAccounts, setApiAccounts] = useState([]);
  const [loadingAccounts, setLoadingAccounts] = useState(true);
  const [showIndustryTemplates, setShowIndustryTemplates] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilterPanel, setShowFilterPanel] = useState(false);
  
  // Advanced filter state
  const [filters, setFilters] = useState({
    types: [], // Array of selected types: ['asset', 'liability', etc.]
    balanceMin: '',
    balanceMax: '',
    hideZeroBalance: false,
    status: 'all', // 'all', 'active', 'inactive'
    codeMin: '',
    codeMax: '',
    coreOnly: false
  });
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [showBulkEditDialog, setShowBulkEditDialog] = useState(false);
  const [showMergeDialog, setShowMergeDialog] = useState(false);
  const [mergeSourceAccount, setMergeSourceAccount] = useState(null);
  const [mergeTargetAccount, setMergeTargetAccount] = useState(null);
  const [mergeConfirmationText, setMergeConfirmationText] = useState('');
  const [mergeValidation, setMergeValidation] = useState({ status: 'none', blockers: [], warnings: [] });
  const [bulkEditForm, setBulkEditForm] = useState({
    type: '',
    description: '',
    parent_id: '',
    category: '',
    is_active: null
  });
  const [accountActivity, setAccountActivity] = useState({}); // { accountId: { lastTransaction, transactionCount } }
  const [loadingActivity, setLoadingActivity] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [accountInsights, setAccountInsights] = useState([]);
  const [showAccountCodes, setShowAccountCodes] = useState(() => {
    // Load preference from localStorage, default to false (hidden)
    const saved = localStorage.getItem('coa_show_account_codes');
    return saved === 'true';
  });
  const [addAccountMode, setAddAccountMode] = useState('templates'); // 'templates' or 'custom'
  const [selectedTemplates, setSelectedTemplates] = useState(new Set());
  const [templateSearchTerm, setTemplateSearchTerm] = useState('');

  // Account Template Library (30-50 common accounts, excluding the 25 defaults)
  const ACCOUNT_TEMPLATES = [
    // Additional Asset Accounts
    { name: "Savings Account", type: "asset", suggestedCode: "1010", description: "Business savings account", category: "Current Assets" },
    { name: "Money Market Account", type: "asset", suggestedCode: "1020", description: "Money market savings account", category: "Current Assets" },
    { name: "Petty Cash", type: "asset", suggestedCode: "1030", description: "Small cash fund for minor expenses", category: "Current Assets" },
    { name: "Accounts Receivable - Trade", type: "asset", suggestedCode: "1210", description: "Trade receivables from customers", category: "Current Assets" },
    { name: "Accounts Receivable - Other", type: "asset", suggestedCode: "1220", description: "Other receivables", category: "Current Assets" },
    { name: "Allowance for Doubtful Accounts", type: "asset", suggestedCode: "1230", description: "Reserve for uncollectible receivables", category: "Current Assets" },
    { name: "Inventory - Raw Materials", type: "asset", suggestedCode: "1310", description: "Raw materials inventory", category: "Current Assets" },
    { name: "Inventory - Work in Progress", type: "asset", suggestedCode: "1320", description: "Work in progress inventory", category: "Current Assets" },
    { name: "Inventory - Finished Goods", type: "asset", suggestedCode: "1330", description: "Finished goods inventory", category: "Current Assets" },
    { name: "Prepaid Insurance", type: "asset", suggestedCode: "1410", description: "Prepaid insurance premiums", category: "Current Assets" },
    { name: "Prepaid Rent", type: "asset", suggestedCode: "1420", description: "Prepaid rent payments", category: "Current Assets" },
    { name: "Prepaid Subscriptions", type: "asset", suggestedCode: "1430", description: "Prepaid software and service subscriptions", category: "Current Assets" },
    { name: "Office Equipment", type: "asset", suggestedCode: "1510", description: "Office furniture and equipment", category: "Fixed Assets" },
    { name: "Computer Equipment", type: "asset", suggestedCode: "1520", description: "Computers, laptops, and IT equipment", category: "Fixed Assets" },
    { name: "Vehicles", type: "asset", suggestedCode: "1530", description: "Company vehicles", category: "Fixed Assets" },
    { name: "Accumulated Depreciation - Equipment", type: "asset", suggestedCode: "1540", description: "Accumulated depreciation on equipment", category: "Fixed Assets" },
    { name: "Buildings", type: "asset", suggestedCode: "1600", description: "Owned buildings and structures", category: "Fixed Assets" },
    { name: "Land", type: "asset", suggestedCode: "1700", description: "Owned land", category: "Fixed Assets" },
    
    // Additional Liability Accounts
    { name: "Notes Payable", type: "liability", suggestedCode: "2010", description: "Short-term notes and loans payable", category: "Current Liabilities" },
    { name: "Accrued Wages", type: "liability", suggestedCode: "2110", description: "Accrued employee wages", category: "Current Liabilities" },
    { name: "Accrued Interest", type: "liability", suggestedCode: "2120", description: "Accrued interest payable", category: "Current Liabilities" },
    { name: "Sales Tax Payable", type: "liability", suggestedCode: "2130", description: "Sales tax collected and owed", category: "Current Liabilities" },
    { name: "Payroll Tax Payable", type: "liability", suggestedCode: "2140", description: "Payroll taxes owed", category: "Current Liabilities" },
    { name: "Long-term Loans", type: "liability", suggestedCode: "2400", description: "Long-term loans and mortgages", category: "Long-term Liabilities" },
    { name: "Mortgage Payable", type: "liability", suggestedCode: "2500", description: "Mortgage on property", category: "Long-term Liabilities" },
    
    // Additional Equity Accounts
    { name: "Owner's Draw", type: "equity", suggestedCode: "3001", description: "Owner withdrawals from business", category: "Owner Equity" },
    { name: "Additional Paid-in Capital", type: "equity", suggestedCode: "3101", description: "Capital contributions beyond initial investment", category: "Owner Equity" },
    
    // Additional Revenue Accounts
    { name: "Interest Income", type: "revenue", suggestedCode: "4001", description: "Interest earned on investments and savings", category: "Other Income" },
    { name: "Rental Income", type: "revenue", suggestedCode: "4002", description: "Income from property rental", category: "Other Income" },
    { name: "Consulting Revenue", type: "revenue", suggestedCode: "4101", description: "Revenue from consulting services", category: "Service Revenue" },
    { name: "Subscription Revenue", type: "revenue", suggestedCode: "4102", description: "Recurring subscription income", category: "Service Revenue" },
    { name: "Commission Income", type: "revenue", suggestedCode: "4103", description: "Commission and referral income", category: "Service Revenue" },
    
    // Additional Expense Accounts
    { name: "Bank Fees", type: "expense", suggestedCode: "5001", description: "Banking and transaction fees", category: "Operating Expenses" },
    { name: "Travel Expense", type: "expense", suggestedCode: "6101", description: "Business travel and transportation", category: "Operating Expenses" },
    { name: "Meals and Entertainment", type: "expense", suggestedCode: "6102", description: "Business meals and entertainment", category: "Operating Expenses" },
    { name: "Software Subscriptions", type: "expense", suggestedCode: "6103", description: "Software and SaaS subscriptions", category: "Operating Expenses" },
    { name: "Website and Hosting", type: "expense", suggestedCode: "6104", description: "Website maintenance and hosting costs", category: "Operating Expenses" },
    { name: "Training and Education", type: "expense", suggestedCode: "6105", description: "Employee training and education expenses", category: "Operating Expenses" },
    { name: "Repairs and Maintenance", type: "expense", suggestedCode: "6106", description: "Equipment and facility repairs", category: "Operating Expenses" },
    { name: "Bad Debt Expense", type: "expense", suggestedCode: "6107", description: "Uncollectible accounts written off", category: "Operating Expenses" },
    { name: "Interest Expense", type: "expense", suggestedCode: "6108", description: "Interest paid on loans and credit", category: "Financial Expenses" },
    { name: "Tax Expense", type: "expense", suggestedCode: "6109", description: "Income and business taxes", category: "Tax Expenses" },
    { name: "Charitable Contributions", type: "expense", suggestedCode: "6110", description: "Charitable donations and contributions", category: "Other Expenses" },
    { name: "Legal Fees", type: "expense", suggestedCode: "6501", description: "Legal and attorney fees", category: "Professional Services" },
    { name: "Accounting Fees", type: "expense", suggestedCode: "6502", description: "Accounting and bookkeeping services", category: "Professional Services" },
    { name: "Consulting Fees", type: "expense", suggestedCode: "6503", description: "External consulting services", category: "Professional Services" },
    { name: "Vehicle Expense", type: "expense", suggestedCode: "6801", description: "Vehicle fuel, maintenance, and expenses", category: "Operating Expenses" },
    { name: "Telephone Expense", type: "expense", suggestedCode: "6802", description: "Phone and communication expenses", category: "Operating Expenses" },
    { name: "Postage and Shipping", type: "expense", suggestedCode: "6803", description: "Postage, shipping, and delivery costs", category: "Operating Expenses" },
    { name: "Office Rent", type: "expense", suggestedCode: "6804", description: "Office space rental", category: "Operating Expenses" },
    { name: "Equipment Rental", type: "expense", suggestedCode: "6805", description: "Rental of equipment and machinery", category: "Operating Expenses" }
  ];

  // Fetch account activity data
  useEffect(() => {
    const loadAccountActivity = async () => {
      if (apiAccounts.length === 0) return;
      
      try {
        setLoadingActivity(true);
        // Fetch journal entries to calculate activity
        const journalEntries = await apiClient.get('/api/finance/double-entry/journal-entries').catch(() => []);
        
        // Calculate activity per account
        const activity = {};
        apiAccounts.forEach(account => {
          // Find journal lines for this account
          const accountLines = [];
          if (Array.isArray(journalEntries)) {
            journalEntries.forEach(entry => {
              if (entry.lines && Array.isArray(entry.lines)) {
                entry.lines.forEach(line => {
                  if (line.account_id === account.id) {
                    accountLines.push({ line, entry });
                  }
                });
              }
            });
          }
          
          if (accountLines.length > 0) {
            // Get last transaction date
            const dates = accountLines
              .map(({ entry }) => entry?.entry_date || entry?.doc_date || entry?.created_at)
              .filter(Boolean)
              .map(date => new Date(date))
              .sort((a, b) => b - a);
            
            const lastTransaction = dates.length > 0 ? dates[0].toISOString() : null;
            
            // Count transactions by period
            const now = new Date();
            const thisMonth = accountLines.filter(({ entry }) => {
              const entryDate = entry?.entry_date || entry?.doc_date || entry?.created_at;
              if (!entryDate) return false;
              const date = new Date(entryDate);
              return date.getMonth() === now.getMonth() && 
                     date.getFullYear() === now.getFullYear();
            }).length;
            
            const thisYear = accountLines.filter(({ entry }) => {
              const entryDate = entry?.entry_date || entry?.doc_date || entry?.created_at;
              if (!entryDate) return false;
              const date = new Date(entryDate);
              return date.getFullYear() === now.getFullYear();
            }).length;
            
            activity[account.id] = {
              lastTransaction: lastTransaction,
              transactionCount: accountLines.length,
              thisMonth,
              thisYear
            };
          } else {
            activity[account.id] = {
              lastTransaction: null,
              transactionCount: 0,
              thisMonth: 0,
              thisYear: 0
            };
          }
        });
        
        setAccountActivity(activity);
      } catch (error) {
        console.error('Error loading account activity:', error);
        // Set empty activity on error
        const emptyActivity = {};
        apiAccounts.forEach(account => {
          emptyActivity[account.id] = {
            lastTransaction: null,
            transactionCount: 0,
            thisMonth: 0,
            thisYear: 0
          };
        });
        setAccountActivity(emptyActivity);
      } finally {
        setLoadingActivity(false);
      }
    };

    if (apiAccounts.length > 0) {
      loadAccountActivity();
    }
  }, [apiAccounts]);

  // Fetch accounts from API - only create if backend says no accounts exist
  useEffect(() => {
    const loadAccountsFromAPI = async () => {
      try {
        setLoadingAccounts(true);
        
        // Fetch all accounts from single source
        const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
        const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
        
        // If no accounts exist, ask backend to create default accounts (backend will check and only create if needed)
        if (accountsArray.length === 0) {
          console.log('📊 No accounts found - requesting default accounts creation...');
          try {
            const createResponse = await apiClient.post('/api/finance/double-entry/accounts/default/create', {});
            console.log('✅ Default accounts creation response:', createResponse);
            
            // Backend returns early if accounts already exist, so check the response
            if (createResponse.has_accounts && createResponse.new_count === 0) {
              // Accounts already exist, just reload
              console.log('ℹ️ Accounts already exist, reloading...');
              const reloadResponse = await apiClient.get('/api/finance/double-entry/accounts');
              const reloadedAccounts = Array.isArray(reloadResponse) ? reloadResponse : [];
              setApiAccounts(reloadedAccounts);
            } else if (createResponse.new_count > 0) {
              // New accounts were created, reload
              const reloadResponse = await apiClient.get('/api/finance/double-entry/accounts');
              const reloadedAccounts = Array.isArray(reloadResponse) ? reloadResponse : [];
              setApiAccounts(reloadedAccounts);
              
              setSnackbar({
                open: true,
                message: `Created ${createResponse.new_count} default accounts (12 core + 13 standard). Total: ${reloadedAccounts.length} accounts`,
                severity: 'success'
              });
            } else {
              // No new accounts created, use existing
              setApiAccounts(accountsArray);
            }
          } catch (createError) {
            console.error('❌ Error creating default accounts:', createError);
            // If creation fails, still try to show existing accounts
            setApiAccounts(accountsArray);
            setSnackbar({
              open: true,
              message: 'Failed to create default accounts: ' + (createError.message || 'Unknown error'),
              severity: 'error'
            });
          }
        } else {
          // Accounts already exist - just use them (no need to create)
          console.log(`✅ Found ${accountsArray.length} existing accounts - using them`);
          setApiAccounts(accountsArray);
        }
        
        setAccountsLoaded(true);
        console.log('✅ Accounts loaded from API:', accountsArray.length);
        
      } catch (error) {
        console.error('❌ Error loading accounts:', error);
        setSnackbar({
          open: true,
          message: 'Failed to load accounts: ' + (error.message || 'Unknown error'),
          severity: 'error'
        });
      } finally {
        setLoadingAccounts(false);
      }
    };

    loadAccountsFromAPI();
  }, []); // Only run once on mount

  const handleTabChange = (_, newValue) => {
    setViewMode(newValue);
  };

  const handleCoaViewModeChange = (mode) => {
    setCoaViewMode(mode);
  };


  const handleEdit = (account) => {
    setCurrentAccount(account);
    setAddAccountMode('custom'); // Always use custom mode for editing
    setOpenDialog(true);
  };

  const handleAddAccount = () => {
    setCurrentAccount(null);
    setAddAccountMode('templates'); // Default to templates view
    setSelectedTemplates(new Set());
    setTemplateSearchTerm('');
    setOpenDialog(true);
  };

  // Filter templates to hide existing accounts and defaults
  const getAvailableTemplates = useMemo(() => {
    // Default account codes (25 defaults that should be filtered out)
    const defaultCodes = new Set([
      '1000', '1100', '1200', '1300', '1400', '1500', // Assets
      '2000', '2100', '2200', '2300', // Liabilities
      '3000', '3100', '3200', // Equity
      '4000', '4100', // Revenue
      '5000', '6000', '6100', '6200', '6300', '6400', '6500', '6600', '6700', '6800' // Expenses
    ]);

    // Get existing account codes and names
    const existingCodes = new Set(apiAccounts.map(acc => acc.code));
    const existingNames = new Set(apiAccounts.map(acc => (acc.name || acc.account_name || '').toLowerCase()));

    return ACCOUNT_TEMPLATES.filter(template => {
      // Filter out if code matches a default
      if (defaultCodes.has(template.suggestedCode)) {
        return false;
      }
      
      // Filter out if code already exists
      if (existingCodes.has(template.suggestedCode)) {
        return false;
      }
      
      // Filter out if similar name exists (fuzzy match)
      const templateNameLower = template.name.toLowerCase();
      for (const existingName of existingNames) {
        // Check for exact match or very similar names
        if (existingName === templateNameLower || 
            existingName.includes(templateNameLower) || 
            templateNameLower.includes(existingName)) {
          return false;
        }
      }
      
      return true;
    });
  }, [apiAccounts]);

  // Filter templates by search term
  const filteredTemplates = useMemo(() => {
    if (!templateSearchTerm.trim()) {
      return getAvailableTemplates;
    }
    
    const searchLower = templateSearchTerm.toLowerCase();
    return getAvailableTemplates.filter(template =>
      template.name.toLowerCase().includes(searchLower) ||
      template.type.toLowerCase().includes(searchLower) ||
      template.category.toLowerCase().includes(searchLower) ||
      template.description.toLowerCase().includes(searchLower)
    );
  }, [getAvailableTemplates, templateSearchTerm]);

  // Group templates by category
  const groupedTemplates = useMemo(() => {
    const groups = {};
    filteredTemplates.forEach(template => {
      const category = template.category || template.type;
      if (!groups[category]) {
        groups[category] = [];
      }
      groups[category].push(template);
    });
    return groups;
  }, [filteredTemplates]);

  // Generate next available code
  const generateNextCode = (suggestedCode, existingCodes) => {
    if (!existingCodes.has(suggestedCode)) {
      return suggestedCode;
    }
    
    // Try incrementing the last digit
    const base = suggestedCode.slice(0, -1);
    const lastDigit = parseInt(suggestedCode.slice(-1));
    
    for (let i = 1; i <= 9; i++) {
      const newCode = base + (lastDigit + i).toString();
      if (!existingCodes.has(newCode)) {
        return newCode;
      }
    }
    
    // If that doesn't work, try adding 10, 20, etc.
    for (let i = 10; i <= 90; i += 10) {
      const newCode = base + (lastDigit + i).toString();
      if (!existingCodes.has(newCode)) {
        return newCode;
      }
    }
    
    // Fallback: return original with suffix
    return suggestedCode + '1';
  };

  // Handle template selection toggle
  const handleTemplateToggle = (templateName) => {
    setSelectedTemplates(prev => {
      const newSet = new Set(prev);
      if (newSet.has(templateName)) {
        newSet.delete(templateName);
      } else {
        newSet.add(templateName);
      }
      return newSet;
    });
  };

  // Handle bulk add selected templates
  const handleAddSelectedTemplates = async () => {
    if (selectedTemplates.size === 0) {
      setSnackbar({
        open: true,
        message: 'Please select at least one template to add',
        severity: 'warning'
      });
      return;
    }

    try {
      const existingCodes = new Set(apiAccounts.map(acc => acc.code));
      const accountsToCreate = [];
      
      // Get selected templates
      const selectedTemplateObjects = ACCOUNT_TEMPLATES.filter(t => selectedTemplates.has(t.name));
      
      for (const template of selectedTemplateObjects) {
        const code = generateNextCode(template.suggestedCode, existingCodes);
        existingCodes.add(code); // Track newly generated codes
        
        accountsToCreate.push({
          name: template.name,
          type: template.type,
          code: code,
          description: template.description,
          is_active: true
        });
      }

      // Create accounts via API
      let successCount = 0;
      let errorCount = 0;
      
      for (const accountData of accountsToCreate) {
        try {
          await apiClient.post('/api/finance/double-entry/accounts', accountData);
          successCount++;
        } catch (error) {
          console.error(`Failed to create account ${accountData.name}:`, error);
          errorCount++;
        }
      }

      // Reload accounts
      const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
      const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
      setApiAccounts(accountsArray);

      // Close dialog and show success
      setOpenDialog(false);
      setSelectedTemplates(new Set());
      
      if (errorCount === 0) {
        setSnackbar({
          open: true,
          message: `Successfully added ${successCount} account${successCount > 1 ? 's' : ''}`,
          severity: 'success'
        });
      } else {
        setSnackbar({
          open: true,
          message: `Added ${successCount} account${successCount > 1 ? 's' : ''}, ${errorCount} failed`,
          severity: 'warning'
        });
      }
    } catch (error) {
      console.error('Error adding templates:', error);
      setSnackbar({
        open: true,
        message: 'Failed to add accounts: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };

  const handleRowClick = (account, event) => {
    // Don't open details if clicking on checkbox
    if (event.target.type === 'checkbox' || event.target.closest('input[type="checkbox"]')) {
      return;
    }
    // Don't open details if clicking on action icons
    if (event.target.closest('button') || event.target.closest('[role="button"]')) {
      return;
    }
    setSelectedAccountDetails(account);
    setShowDetailsPanel(true);
  };

  const handleCloseDetailsPanel = () => {
    setShowDetailsPanel(false);
    setSelectedAccountDetails(null);
  };

  const handleCreate = () => {
    handleAddAccount();
  };

  const handleDelete = (account) => {
    // Check if it's a core default account
    const isCoreDefault = account.is_core || account.is_default;
    const accountName = account.account_name || account.name || 'this account';
    
    setDeleteConfirm({
      account: account,
      type: 'single',
      accountName: accountName,
      isCoreDefault: isCoreDefault
    });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm) return;

    try {
      if (deleteConfirm.type === 'single') {
        // Single account delete
        const account = deleteConfirm.account;
        const accountName = deleteConfirm.accountName;
        
        // Use API directly to get proper error messages
        try {
          await apiClient.delete(`/api/finance/double-entry/accounts/${account.id}`);
        } catch (apiError) {
          // Handle specific error responses from backend
          const errorData = apiError.response?.data || {};
          const errorMessage = errorData.error || apiError.message || 'Unknown error';
          
          // Check if it's a balance or transaction error
          if (errorData.suggestion === 'deactivate' || errorData.suggestion === 'deactivate_or_transfer') {
            setSnackbar({
              open: true,
              message: `${errorMessage} Consider deactivating the account instead.`,
              severity: 'warning'
            });
          } else {
            setSnackbar({
              open: true,
              message: errorMessage,
              severity: 'error'
            });
          }
          
          setDeleteConfirm(null);
          return;
        }
        
        // Close details panel if it's open for this account
        if (selectedAccountDetails?.id === account.id) {
          handleCloseDetailsPanel();
        }
        
        // Refresh accounts after deletion
        const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
        const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
        setApiAccounts(accountsArray);
        
        setSnackbar({
          open: true,
          message: `Account "${accountName}" deleted successfully`,
          severity: 'success'
        });
      } else if (deleteConfirm.type === 'bulk') {
        // Bulk delete
        const count = selectedAccounts.size;
        const failedAccounts = [];
        
        for (const accountId of selectedAccounts) {
          try {
            await apiClient.delete(`/api/finance/double-entry/accounts/${accountId}`);
          } catch (error) {
            const account = apiAccounts.find(acc => acc.id === accountId);
            failedAccounts.push(account?.name || account?.account_name || `Account ${accountId}`);
          }
        }
        
        setSelectedAccounts(new Set());
        
        // Refresh accounts after deletion
        const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
        const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
        setApiAccounts(accountsArray);
        
        const successCount = count - failedAccounts.length;
        if (failedAccounts.length === 0) {
          setSnackbar({
            open: true,
            message: `Deleted ${successCount} account${successCount !== 1 ? 's' : ''} successfully`,
            severity: 'success'
          });
        } else {
          setSnackbar({
            open: true,
            message: `Deleted ${successCount} account${successCount !== 1 ? 's' : ''}, ${failedAccounts.length} failed (may have balance or transactions)`,
            severity: 'warning'
          });
        }
      }
      
      setDeleteConfirm(null);
    } catch (error) {
      console.error("Delete failed:", error);
      setSnackbar({
        open: true,
        message: 'Failed to delete: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
      setDeleteConfirm(null);
    }
  };

  const handleDialogClose = async () => {
    setOpenDialog(false);
    setCurrentAccount(null);
    // Refresh accounts after create/edit
    try {
      const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
      const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
      setApiAccounts(accountsArray);
    } catch (error) {
      console.error('Error refreshing accounts:', error);
    }
  };

  // Account selection handlers
  const handleSelectAccount = (accountId, checked) => {
    const newSelected = new Set(selectedAccounts);
    if (checked) {
      newSelected.add(accountId);
    } else {
      newSelected.delete(accountId);
    }
    setSelectedAccounts(newSelected);
  };

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedAccounts(new Set(filteredAccounts.map(acc => acc.id)));
    } else {
      setSelectedAccounts(new Set());
    }
  };

  const handleToggleAccountActive = async (account) => {
    const newActiveStatus = !account.is_active;
    const previousStatus = account.is_active;
    
    // OPTIMISTIC UPDATE: Update UI immediately for instant feedback
    setApiAccounts(prevAccounts => 
      prevAccounts.map(acc => 
        acc.id === account.id 
          ? { ...acc, is_active: newActiveStatus }
          : acc
      )
    );
    
    // Update context immediately
    updateAccount(account.id, { is_active: newActiveStatus });
    
    try {
      // Make API call in background (non-blocking)
      await apiClient.put(
        `/api/finance/double-entry/accounts/${account.id}`,
        { is_active: newActiveStatus }
      );
      
      // Success - no need to reload, UI already updated
      setSnackbar({
        open: true,
        message: `Account ${newActiveStatus ? 'activated' : 'deactivated'} successfully`,
        severity: 'success'
      });
    } catch (error) {
      console.error("Failed to toggle account:", error);
      
      // ROLLBACK: Revert optimistic update on error
      setApiAccounts(prevAccounts => 
        prevAccounts.map(acc => 
          acc.id === account.id 
            ? { ...acc, is_active: previousStatus }
            : acc
        )
      );
      
      // Rollback context
      updateAccount(account.id, { is_active: previousStatus });
      
      setSnackbar({
        open: true,
        message: `Failed to ${newActiveStatus ? 'activate' : 'deactivate'} account: ${error.message || 'Unknown error'}`,
        severity: 'error'
      });
    }
  };

  const handleToggleAccountActiveFromDetails = async () => {
    if (!selectedAccountDetails) return;
    
    const newActiveStatus = !selectedAccountDetails.is_active;
    const previousStatus = selectedAccountDetails.is_active;
    
    // OPTIMISTIC UPDATE: Update UI immediately for instant feedback
    setSelectedAccountDetails({
      ...selectedAccountDetails,
      is_active: newActiveStatus
    });
    
    // Update accounts list immediately
    setApiAccounts(prevAccounts => 
      prevAccounts.map(acc => 
        acc.id === selectedAccountDetails.id 
          ? { ...acc, is_active: newActiveStatus }
          : acc
      )
    );
    
    // Update context immediately
    updateAccount(selectedAccountDetails.id, { is_active: newActiveStatus });
    
    try {
      // Make API call in background (non-blocking)
      await apiClient.put(
        `/api/finance/double-entry/accounts/${selectedAccountDetails.id}`,
        { is_active: newActiveStatus }
      );
      
      // Success - no need to reload, UI already updated
      setSnackbar({
        open: true,
        message: `Account ${newActiveStatus ? 'activated' : 'deactivated'} successfully`,
        severity: 'success'
      });
    } catch (error) {
      console.error("Failed to toggle account:", error);
      
      // ROLLBACK: Revert optimistic update on error
      setSelectedAccountDetails({
        ...selectedAccountDetails,
        is_active: previousStatus
      });
      
      setApiAccounts(prevAccounts => 
        prevAccounts.map(acc => 
          acc.id === selectedAccountDetails.id 
            ? { ...acc, is_active: previousStatus }
            : acc
        )
      );
      
      // Rollback context
      updateAccount(selectedAccountDetails.id, { is_active: previousStatus });
      
      setSnackbar({
        open: true,
        message: `Failed to ${newActiveStatus ? 'activate' : 'deactivate'} account: ${error.message || 'Unknown error'}`,
        severity: 'error'
      });
    }
  };

  const handleBulkDelete = () => {
    if (selectedAccounts.size === 0) return;
    setDeleteConfirm({
      type: 'bulk',
      count: selectedAccounts.size
    });
  };

  // Bulk operations
  const handleBulkActivate = async () => {
    if (selectedAccounts.size === 0) return;
    
    try {
      for (const accountId of selectedAccounts) {
        const account = accountsToUse.find(acc => acc.id === accountId);
        if (account) {
          await apiClient.put(`/api/finance/double-entry/accounts/${accountId}`, {
            ...account,
            is_active: true
          });
        }
      }
      // Refresh accounts
      const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
      const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
      setApiAccounts(accountsArray);
      setSnackbar({
        open: true,
        message: `Activated ${selectedAccounts.size} accounts`,
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to activate accounts: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };

  const handleBulkDeactivate = async () => {
    if (selectedAccounts.size === 0) return;
    
    try {
      for (const accountId of selectedAccounts) {
        const account = accountsToUse.find(acc => acc.id === accountId);
        if (account) {
          await apiClient.put(`/api/finance/double-entry/accounts/${accountId}`, {
            ...account,
            is_active: false
          });
        }
      }
      // Refresh accounts
      const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
      const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
      setApiAccounts(accountsArray);
      setSnackbar({
        open: true,
        message: `Deactivated ${selectedAccounts.size} accounts`,
        severity: 'success'
      });
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to deactivate accounts: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };

  const handleBulkEdit = () => {
    if (selectedAccounts.size === 0) {
      setSnackbar({
        open: true,
        message: 'Please select accounts to edit',
        severity: 'warning'
      });
      return;
    }
    // Reset form when opening
    setBulkEditForm({
      type: '',
      description: '',
      parent_id: '',
      category: '',
      is_active: null
    });
    setShowBulkEditDialog(true);
  };

  const handleBulkEditSubmit = async () => {
    // Build edit data object with only fields that have values
    const editData = {};
    
    if (bulkEditForm.type) {
      editData.type = bulkEditForm.type;
    }
    if (bulkEditForm.description !== '') {
      editData.description = bulkEditForm.description || null;
    }
    // Handle parent_id: '' means keep current, null means remove parent, number means set parent
    if (bulkEditForm.parent_id !== '') {
      editData.parent_id = bulkEditForm.parent_id;
    }
    if (bulkEditForm.category !== '') {
      editData.category = bulkEditForm.category || null;
    }
    if (bulkEditForm.is_active !== null) {
      editData.is_active = bulkEditForm.is_active;
    }

    // Check if there's anything to update
    if (Object.keys(editData).length === 0) {
      setSnackbar({
        open: true,
        message: 'Please select at least one field to update',
        severity: 'warning'
      });
      return;
    }

    try {
      const accountCount = selectedAccounts.size;
      let successCount = 0;
      let errorCount = 0;

      for (const accountId of selectedAccounts) {
        const account = accountsToUse.find(acc => acc.id === accountId);
        if (account) {
          try {
            // Don't include parent_id if it would create a circular reference
            const finalEditData = { ...editData };
            if (finalEditData.parent_id && finalEditData.parent_id === accountId) {
              delete finalEditData.parent_id;
            }
            
            // Also prevent setting a parent that is a descendant of this account
            if (finalEditData.parent_id) {
              const potentialParent = accountsToUse.find(acc => acc.id === finalEditData.parent_id);
              if (potentialParent && potentialParent.parent_id === accountId) {
                // This would create a circular reference, skip it
                console.warn(`Skipping parent_id for account ${accountId} to prevent circular reference`);
                delete finalEditData.parent_id;
              }
            }
            
            await apiClient.put(`/api/finance/double-entry/accounts/${accountId}`, {
              ...account,
              ...finalEditData
            });
            successCount++;
          } catch (err) {
            console.error(`Error updating account ${accountId}:`, err);
            errorCount++;
          }
        }
      }
      
      // Refresh accounts
      const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
      const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
      setApiAccounts(accountsArray);
      
      // Reset form and close dialog
      setBulkEditForm({
        type: '',
        description: '',
        parent_id: '',
        category: '',
        is_active: null
      });
      setShowBulkEditDialog(false);
      setSelectedAccounts(new Set());
      
      if (errorCount > 0) {
        setSnackbar({
          open: true,
          message: `Updated ${successCount} accounts successfully. ${errorCount} failed.`,
          severity: 'warning'
        });
      } else {
        setSnackbar({
          open: true,
          message: `Updated ${successCount} account${successCount !== 1 ? 's' : ''} successfully`,
          severity: 'success'
        });
      }
    } catch (error) {
      setSnackbar({
        open: true,
        message: 'Failed to update accounts: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortDirection('asc');
    }
  };

  // Export to CSV (using backend API for professional format)
  const handleExportCSV = async () => {
    try {
      // Use fetch directly for blob response
      const url = `/api/finance/double-entry/accounts/export`;
      const token = localStorage.getItem('access_token') || localStorage.getItem('sessionToken');
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = localStorage.getItem('userId') || user.id || user.user_id || '1';
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'X-User-ID': userId
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      // Create download link
      const blob = await response.blob();
      const link = document.createElement('a');
      const blobUrl = URL.createObjectURL(blob);
      link.setAttribute('href', blobUrl);
      link.setAttribute('download', `chart-of-accounts-${new Date().toISOString().split('T')[0]}.csv`);
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(blobUrl);

      setSnackbar({
        open: true,
        message: `Exported accounts to CSV successfully`,
        severity: 'success'
      });
    } catch (error) {
      console.error('Export error:', error);
      setSnackbar({
        open: true,
        message: 'Failed to export CSV: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };

  // Import from CSV (using backend API for professional validation)
  const handleImportCSV = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      // Use fetch directly for FormData to avoid JSON.stringify
      const url = `/api/finance/double-entry/accounts/import`;
      const token = localStorage.getItem('access_token') || localStorage.getItem('sessionToken');
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const userId = localStorage.getItem('userId') || user.id || user.user_id || '1';
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': token ? `Bearer ${token}` : '',
          'X-User-ID': userId
        },
        body: formData
      });
      
      const responseData = await response.json();
      
      if (!response.ok) {
        throw new Error(responseData.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      // Reload accounts after import
      const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
      const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
      setApiAccounts(accountsArray);
      
      setShowImportDialog(false);
      
      if (responseData.errors && responseData.errors.length > 0) {
        setSnackbar({
          open: true,
          message: `${responseData.message}. ${responseData.errors.length} error(s) occurred. Check console for details.`,
          severity: 'warning'
        });
        console.warn('Import errors:', responseData.errors);
      } else {
        setSnackbar({
          open: true,
          message: responseData.message || `Successfully imported ${responseData.total_processed || 0} accounts`,
          severity: 'success'
        });
      }
    } catch (error) {
      console.error('Import error:', error);
      setSnackbar({
        open: true,
        message: 'Failed to import CSV: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    }
  };

  // Handle account code visibility toggle
  const handleToggleAccountCodes = (event) => {
    const newValue = event.target.checked;
    setShowAccountCodes(newValue);
    localStorage.setItem('coa_show_account_codes', newValue.toString());
  };

  // Validate merge compatibility
  const validateMerge = useMemo(() => {
    if (!mergeSourceAccount || !mergeTargetAccount) {
      return { status: 'none', blockers: [], warnings: [] };
    }

    const defaultCodes = new Set([
      '1000', '1100', '1200', '1300', '1400', '1500',  // Assets
      '2000', '2100', '2200', '2300',  // Liabilities
      '3000', '3100', '3200',  // Equity
      '4000', '4100',  // Revenue
      '5000', '6000', '6100', '6200', '6300', '6400', '6500', '6600', '6700', '6800'  // Expenses
    ]);

    const blockers = [];
    const warnings = [];

    // Blockers
    if (mergeSourceAccount.code && defaultCodes.has(mergeSourceAccount.code)) {
      blockers.push(`Source account '${mergeSourceAccount.name}' is a default account and cannot be merged.`);
    }
    if (mergeTargetAccount.code && defaultCodes.has(mergeTargetAccount.code)) {
      blockers.push(`Target account '${mergeTargetAccount.name}' is a default account and cannot be merged.`);
    }
    if (mergeSourceAccount.is_active === false) {
      blockers.push(`Source account '${mergeSourceAccount.name}' is inactive. Activate it before merging.`);
    }
    if (mergeTargetAccount.is_active === false) {
      blockers.push(`Target account '${mergeTargetAccount.name}' is inactive. Activate it before merging.`);
    }
    if (mergeSourceAccount.type !== mergeTargetAccount.type) {
      blockers.push(`Cannot merge different account types: ${mergeSourceAccount.type} and ${mergeTargetAccount.type}.`);
    }
    const sourceCurrency = mergeSourceAccount.currency || 'USD';
    const targetCurrency = mergeTargetAccount.currency || 'USD';
    if (sourceCurrency !== targetCurrency) {
      blockers.push(`Cannot merge accounts with different currencies: ${sourceCurrency} and ${targetCurrency}.`);
    }

    // Warnings (non-blocking but important)
    if (mergeSourceAccount.balance && Math.abs(mergeSourceAccount.balance) > 0.01) {
      warnings.push(`Source account has a balance of ${formatAmount(mergeSourceAccount.balance)} that will be transferred.`);
    }

    const status = blockers.length > 0 ? 'blocked' : warnings.length > 0 ? 'warning' : 'ready';
    return { status, blockers, warnings };
  }, [mergeSourceAccount, mergeTargetAccount]);

  // Update validation when accounts change
  useEffect(() => {
    setMergeValidation(validateMerge);
  }, [validateMerge]);

  // Handle account merge
  const handleMergeAccounts = async () => {
    if (!mergeSourceAccount || !mergeTargetAccount) {
      setSnackbar({
        open: true,
        message: 'Please select both source and target accounts',
        severity: 'warning'
      });
      return;
    }

    // Check confirmation text
    const targetName = mergeTargetAccount.name || mergeTargetAccount.account_name || '';
    if (mergeConfirmationText.trim() !== targetName.trim()) {
      setSnackbar({
        open: true,
        message: `Confirmation text must match the target account name: "${targetName}"`,
        severity: 'error'
      });
      return;
    }

    // Check validation
    if (mergeValidation.status === 'blocked') {
      setSnackbar({
        open: true,
        message: 'Cannot merge accounts due to validation errors. Please review the issues above.',
        severity: 'error'
      });
      return;
    }

    try {
      const response = await apiClient.post('/api/finance/double-entry/accounts/merge', {
        source_account_id: mergeSourceAccount.id,
        target_account_id: mergeTargetAccount.id
      });

      // Reload accounts after merge
      const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
      const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
      setApiAccounts(accountsArray);

      setShowMergeDialog(false);
      setMergeSourceAccount(null);
      setMergeTargetAccount(null);
      setMergeConfirmationText('');

      setSnackbar({
        open: true,
        message: response.message || 'Accounts merged successfully',
        severity: 'success'
      });
    } catch (error) {
      console.error('Merge error:', error);
      const errorData = error.response?.data || {};
      setSnackbar({
        open: true,
        message: errorData.error || error.message || 'Failed to merge accounts',
        severity: 'error'
      });
    }
  };

  // Use API accounts if available, otherwise fall back to context accounts
  const accountsToUse = apiAccounts.length > 0 ? apiAccounts : accounts;

  // Calculate account statistics
  const accountStats = useMemo(() => {
    const stats = {
      total: accountsToUse.length,
      active: accountsToUse.filter(acc => acc.is_active !== false).length,
      inactive: accountsToUse.filter(acc => acc.is_active === false).length,
      byType: {
        asset: { count: 0, balance: 0 },
        liability: { count: 0, balance: 0 },
        equity: { count: 0, balance: 0 },
        revenue: { count: 0, balance: 0 },
        expense: { count: 0, balance: 0 }
      },
      totalBalance: 0
    };

    accountsToUse.forEach(account => {
      const accountType = (account.account_type || account.type || '').toLowerCase();
      const balance = Math.abs(account.balance || 0);
      
      if (stats.byType[accountType]) {
        stats.byType[accountType].count++;
        stats.byType[accountType].balance += balance;
      }
      
      stats.totalBalance += balance;
    });

    return stats;
  }, [accountsToUse]);

  // Calculate account health scores and insights
  const accountHealthAndInsights = useMemo(() => {
    const insights = [];
    const healthScores = {};
    const now = new Date();
    const ninetyDaysAgo = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);

    accountsToUse.forEach(account => {
      const activity = accountActivity[account.id] || {};
      const balance = Math.abs(account.balance || 0);
      const isActive = account.is_active !== false;
      const hasTransactions = activity.transactionCount > 0;
      const lastTransaction = activity.lastTransaction ? new Date(activity.lastTransaction) : null;
      const daysSinceLastTransaction = lastTransaction ? Math.floor((now - lastTransaction) / (1000 * 60 * 60 * 24)) : null;

      // Calculate health score (0-100)
      let healthScore = 100;
      let healthStatus = 'healthy';
      const issues = [];

      // Deduct points for inactive accounts
      if (!isActive) {
        healthScore -= 30;
        issues.push('Account is inactive');
        healthStatus = 'critical';
      }

      // Deduct points for unused accounts
      if (isActive && !hasTransactions) {
        healthScore -= 20;
        issues.push('No transactions recorded');
        if (healthStatus === 'healthy') healthStatus = 'warning';
      }

      // Deduct points for accounts with no recent activity
      if (hasTransactions && daysSinceLastTransaction !== null && daysSinceLastTransaction > 90) {
        healthScore -= 15;
        issues.push(`No activity in ${daysSinceLastTransaction} days`);
        if (healthStatus === 'healthy') healthStatus = 'warning';
      }

      // Deduct points for zero balance accounts that should have activity
      if (balance === 0 && isActive && account.is_core) {
        healthScore -= 10;
        issues.push('Core account has zero balance');
        if (healthStatus === 'healthy') healthStatus = 'warning';
      }

      healthScores[account.id] = {
        score: Math.max(0, healthScore),
        status: healthStatus,
        issues
      };

      // Generate insights
      if (!isActive && balance > 0) {
        insights.push({
          type: 'warning',
          account: account,
          message: `Inactive account "${account.account_name || account.name}" has balance of ${formatAmount(balance)}`,
          action: 'Consider activating or archiving'
        });
      }

      if (isActive && !hasTransactions && account.is_core) {
        insights.push({
          type: 'info',
          account: account,
          message: `Core account "${account.account_name || account.name}" has no transactions`,
          action: 'This may be expected for new accounts'
        });
      }

      if (hasTransactions && daysSinceLastTransaction !== null && daysSinceLastTransaction > 180) {
        insights.push({
          type: 'warning',
          account: account,
          message: `Account "${account.account_name || account.name}" hasn't been used in ${daysSinceLastTransaction} days`,
          action: 'Consider archiving if no longer needed'
        });
      }

      if (balance === 0 && isActive && !hasTransactions) {
        insights.push({
          type: 'info',
          account: account,
          message: `Account "${account.account_name || account.name}" has zero balance and no transactions`,
          action: 'Ready to use or can be archived'
        });
      }
    });

    // Find unused accounts
    const unusedAccounts = accountsToUse.filter(acc => {
      const activity = accountActivity[acc.id] || {};
      return acc.is_active !== false && activity.transactionCount === 0;
    });

    if (unusedAccounts.length > 0) {
      insights.push({
        type: 'info',
        account: null,
        message: `You have ${unusedAccounts.length} active accounts with no transactions`,
        action: 'Consider reviewing and archiving unused accounts'
      });
    }

    // Find zero balance accounts
    const zeroBalanceAccounts = accountsToUse.filter(acc => {
      const balance = Math.abs(acc.balance || 0);
      return balance === 0 && acc.is_active !== false;
    });

    if (zeroBalanceAccounts.length > 5) {
      insights.push({
        type: 'info',
        account: null,
        message: `You have ${zeroBalanceAccounts.length} accounts with zero balance`,
        action: 'Use "Hide zero balance" filter to focus on active accounts'
      });
    }

    return { insights, healthScores };
  }, [accountsToUse, accountActivity, formatAmount]);

  // Chart data for balance distribution
  const chartData = useMemo(() => {
    const pieData = Object.entries(accountStats.byType)
      .filter(([_, data]) => data.count > 0)
      .map(([type, data]) => ({
        name: type.charAt(0).toUpperCase() + type.slice(1),
        value: data.balance,
        count: data.count
      }));

    // Top 10 accounts by balance
    const topAccounts = [...accountsToUse]
      .sort((a, b) => Math.abs(b.balance || 0) - Math.abs(a.balance || 0))
      .slice(0, 10)
      .map(account => ({
        name: (account.account_name || account.name || '').substring(0, 20),
        balance: Math.abs(account.balance || 0),
        code: account.code
      }));

    return { pieData, topAccounts };
  }, [accountStats, accountsToUse]);

  // Calculate active filter count
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.types.length > 0) count++;
    if (filters.balanceMin || filters.balanceMax) count++;
    if (filters.hideZeroBalance) count++;
    if (filters.status !== 'all') count++;
    if (filters.codeMin || filters.codeMax) count++;
    if (filters.coreOnly) count++;
    return count;
  }, [filters]);

  // Filtered and sorted accounts (use converted accounts)
  const filteredAccounts = useMemo(() => {
    let filtered = accountsToUse;
    
    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(account => {
        const code = (account.code || '').toString().toLowerCase();
        const name = (account.account_name || account.name || '').toLowerCase();
        const type = (account.account_type || account.type || '').toLowerCase();
        return code.includes(searchLower) || name.includes(searchLower) || type.includes(searchLower);
      });
    }
    
    // Apply type filter (multi-select)
    if (filters.types.length > 0) {
      filtered = filtered.filter(account => {
        const accountType = (account.account_type || account.type || '').toLowerCase();
        return filters.types.includes(accountType);
      });
    }
    
    // Apply balance range filter
    if (filters.balanceMin || filters.balanceMax) {
      filtered = filtered.filter(account => {
        const balance = account.balance || 0;
        const min = filters.balanceMin ? parseFloat(filters.balanceMin) : -Infinity;
        const max = filters.balanceMax ? parseFloat(filters.balanceMax) : Infinity;
        return balance >= min && balance <= max;
      });
    }
    
    // Filter zero balance accounts if enabled
    if (filters.hideZeroBalance) {
      filtered = filtered.filter(account => {
        const balance = account.balance || 0;
        return Math.abs(balance) > 0.01; // Account for floating point precision
      });
    }
    
    // Apply status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(account => {
        if (filters.status === 'active') {
          return account.is_active !== false;
        } else if (filters.status === 'inactive') {
          return account.is_active === false;
        }
        return true;
      });
    }
    
    // Apply account code range filter (if codes are enabled)
    if (showAccountCodes && (filters.codeMin || filters.codeMax)) {
      filtered = filtered.filter(account => {
        const code = parseInt(account.code) || 0;
        const min = filters.codeMin ? parseInt(filters.codeMin) : -Infinity;
        const max = filters.codeMax ? parseInt(filters.codeMax) : Infinity;
        return code >= min && code <= max;
      });
    }
    
    // Apply core accounts only filter
    if (filters.coreOnly) {
      filtered = filtered.filter(account => account.is_core === true);
    }
    
    if (showOnlySelected && selectedAccounts.size > 0) {
      filtered = filtered.filter(account => selectedAccounts.has(account.id));
    }
    
    // Sort accounts
    filtered.sort((a, b) => {
      let aValue = a[sortBy] || '';
      let bValue = b[sortBy] || '';
      
      if (sortBy === 'code') {
        aValue = parseInt(aValue) || 0;
        bValue = parseInt(bValue) || 0;
      } else if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }
      
      if (sortDirection === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
    
    return filtered;
  }, [accountsToUse, selectedAccounts, showOnlySelected, sortBy, sortDirection, filters, showAccountCodes, searchTerm]);

  const isAllSelected = filteredAccounts.length > 0 && 
    filteredAccounts.every(account => selectedAccounts.has(account.id));
  const isIndeterminate = selectedAccounts.size > 0 && !isAllSelected;

  // Check status of selected accounts to show appropriate action (only one at a time)
  const selectedAccountsStatus = useMemo(() => {
    if (selectedAccounts.size === 0) return { showActivate: false, showDeactivate: false };
    
    const selectedAccountsList = accountsToUse.filter(acc => selectedAccounts.has(acc.id));
    const inactiveCount = selectedAccountsList.filter(acc => acc.is_active === false).length;
    const activeCount = selectedAccountsList.filter(acc => acc.is_active !== false).length;
    
    // Show only one action:
    // - If any accounts are inactive, show "Activate" (to activate the inactive ones)
    // - If all accounts are active, show "Deactivate" (to deactivate them)
    const showActivate = inactiveCount > 0;
    const showDeactivate = inactiveCount === 0 && activeCount > 0;
    
    return { showActivate, showDeactivate };
  }, [selectedAccounts, accountsToUse]);

  if (loading || loadingAccounts) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
      <CircularProgress />
    </Box>
  );



  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Empty state */}
      {accountsToUse.length === 0 && (
        <Card sx={{ mb: 3, textAlign: 'center', py: 4 }}>
          <CardContent>
            <LightbulbIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Welcome to EdonuOps Chart of Accounts!
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Build a world-class Chart of Accounts tailored to your business needs.
              Choose from industry templates or start from scratch.
            </Typography>
            <Grid container spacing={2} justifyContent="center" sx={{ mt: 2 }}>
              <Grid item>
                <Button 
                  variant="contained" 
                  size="large"
                  startIcon={<AddIcon />}
                  onClick={handleCreate}
                >
                  Add Your First Account
                </Button>
              </Grid>
              <Grid item>
                <Button 
                  variant="outlined" 
                  size="large"
                  startIcon={<SettingsIcon />}
                  onClick={() => {}}
                >
                  Import Template
                </Button>
              </Grid>
            </Grid>
            <Box sx={{ mt: 3 }}>
              <Chip label="AI-Powered" color="primary" sx={{ mr: 1 }} />
              <Chip label="Industry Templates" color="secondary" sx={{ mr: 1 }} />
              <Chip label="Fully Customizable" color="success" />
            </Box>
          </CardContent>
        </Card>
      )}




      {/* Account Type Summary Cards - Available in All Views */}
      {accountsToUse.length > 0 && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {Object.entries(accountStats.byType).map(([type, data]) => {
            if (data.count === 0) return null;
            const colors = {
              asset: { bg: '#e8f5e9', color: '#2e7d32' },
              liability: { bg: '#ffebee', color: '#c62828' },
              equity: { bg: '#e3f2fd', color: '#1565c0' },
              revenue: { bg: '#f3e5f5', color: '#7b1fa2' },
              expense: { bg: '#fff3e0', color: '#e65100' }
            };
            const typeColors = colors[type] || { bg: '#f5f5f5', color: '#424242' };
            return (
              <Grid item xs={12} sm={6} md={2.4} key={type}>
                <Card sx={{ bgcolor: typeColors.bg, border: `1px solid ${typeColors.color}20` }}>
                  <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Typography variant="caption" sx={{ textTransform: 'uppercase', fontWeight: 600, color: typeColors.color, display: 'block', mb: 0.5 }}>
                      {type}
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 700, color: typeColors.color, mb: 0.5 }}>
                      {formatAmount(data.balance)}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {data.count} {data.count === 1 ? 'account' : 'accounts'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}

      {/* Analytics & Insights Panel - Available in All Views, Collapsed by Default */}
      {showAnalytics && accountsToUse.length > 0 && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {/* Quick Insights */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <InsightsIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Quick Insights</Typography>
                </Box>
                <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                  {accountHealthAndInsights.insights.length > 0 ? (
                    accountHealthAndInsights.insights.slice(0, 5).map((insight, index) => (
                      <Alert 
                        key={index} 
                        severity={insight.type} 
                        sx={{ mb: 1 }}
                        icon={
                          insight.type === 'warning' ? <WarningIcon /> :
                          insight.type === 'error' ? <ErrorIcon /> :
                          <InfoIcon />
                        }
                      >
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {insight.message}
                        </Typography>
                        {insight.action && (
                          <Typography variant="caption" color="text.secondary">
                            {insight.action}
                          </Typography>
                        )}
                      </Alert>
                    ))
                  ) : (
                    <Alert severity="success">
                      <Typography variant="body2">All accounts are in good health!</Typography>
                    </Alert>
                  )}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Account Health Summary */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AssessmentIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Account Health</Typography>
                </Box>
                <Box>
                  {(() => {
                    const healthCounts = { healthy: 0, warning: 0, critical: 0 };
                    Object.values(accountHealthAndInsights.healthScores).forEach(health => {
                      healthCounts[health.status]++;
                    });
                    return (
                      <Grid container spacing={2}>
                        <Grid item xs={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main', mb: 1 }} />
                            <Typography variant="h4">{healthCounts.healthy}</Typography>
                            <Typography variant="caption" color="text.secondary">Healthy</Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <WarningIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                            <Typography variant="h4">{healthCounts.warning}</Typography>
                            <Typography variant="caption" color="text.secondary">Warning</Typography>
                          </Box>
                        </Grid>
                        <Grid item xs={4}>
                          <Box sx={{ textAlign: 'center' }}>
                            <ErrorIcon sx={{ fontSize: 40, color: 'error.main', mb: 1 }} />
                            <Typography variant="h4">{healthCounts.critical}</Typography>
                            <Typography variant="caption" color="text.secondary">Critical</Typography>
                          </Box>
                        </Grid>
                      </Grid>
                    );
                  })()}
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Balance Distribution Chart */}
          {chartData.pieData.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Balance by Account Type</Typography>
                  <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Grid container spacing={2}>
                      {chartData.pieData.map((item, index) => (
                        <Grid item xs={6} key={index}>
                          <Box sx={{ textAlign: 'center', p: 1, bgcolor: 'grey.50', borderRadius: 1 }}>
                            <Typography variant="h6" sx={{ fontWeight: 600 }}>
                              {formatAmount(item.value)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {item.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {item.count} accounts
                            </Typography>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Top Accounts by Balance */}
          {chartData.topAccounts.length > 0 && (
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Top 10 Accounts by Balance</Typography>
                  <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
                    {chartData.topAccounts.map((account, index) => (
                      <Box 
                        key={index}
                        sx={{ 
                          display: 'flex', 
                          justifyContent: 'space-between', 
                          alignItems: 'center',
                          py: 1,
                          borderBottom: index < chartData.topAccounts.length - 1 ? '1px solid' : 'none',
                          borderColor: 'divider'
                        }}
                      >
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>
                            #{index + 1} {account.name}
                          </Typography>
                        </Box>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {formatAmount(account.balance)}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}
      
      {/* Compact Ribbon - Shared Across All Views */}
      {accountsToUse.length > 0 && (
        <>
          <Paper 
            elevation={1}
            sx={{ 
              p: 1, 
              mb: 0,
              borderBottom: '1px solid',
              borderColor: 'divider',
              bgcolor: 'background.paper',
              position: 'sticky',
              top: 0,
              zIndex: 10
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
              {/* Essential Actions - Left Side */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Button
                  variant="contained"
                  size="small"
                  startIcon={<AddIcon />}
                  onClick={handleCreate}
                  sx={{ minWidth: 'auto', px: 1.5 }}
                >
                  Add
                </Button>
                
                <TextField
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  size="small"
                  sx={{ width: 200 }}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon fontSize="small" />
                      </InputAdornment>
                    ),
                  }}
                />
                
                <Badge badgeContent={activeFilterCount} color="primary">
                  <Button
                    variant={activeFilterCount > 0 ? "contained" : "outlined"}
                    size="small"
                    startIcon={<FilterIcon />}
                    onClick={() => setShowFilterPanel(true)}
                    sx={{ minWidth: 'auto', px: 1.5 }}
                  >
                    Filters
                  </Button>
                </Badge>
              </Box>

              {/* Compact Stats - Center */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ml: 'auto', mr: 'auto' }}>
                <Chip 
                  label={`Total: ${accountStats.total}`}
                  size="small"
                  variant="outlined"
                  sx={{ height: 24, fontSize: '0.75rem' }}
                />
                <Chip 
                  label={`Active: ${accountStats.active}`}
                  size="small"
                  color="success"
                  variant="outlined"
                  sx={{ height: 24, fontSize: '0.75rem' }}
                />
                <Chip 
                  label={`Balance: ${formatAmount(accountStats.totalBalance)}`}
                  size="small"
                  variant="outlined"
                  sx={{ height: 24, fontSize: '0.75rem' }}
                />
              </Box>

              {/* View Tabs - Compact */}
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Button
                  variant={coaViewMode === 'progressive' ? "contained" : "outlined"}
                  size="small"
                  onClick={() => handleCoaViewModeChange('progressive')}
                  sx={{ minWidth: 'auto', px: 1.5, fontSize: '0.75rem' }}
                >
                  Progressive
                </Button>
                <Button
                  variant={coaViewMode === 'table' ? "contained" : "outlined"}
                  size="small"
                  onClick={() => handleCoaViewModeChange('table')}
                  sx={{ minWidth: 'auto', px: 1.5, fontSize: '0.75rem' }}
                >
                  Table
                </Button>
                <Button
                  variant={coaViewMode === 'tree' ? "contained" : "outlined"}
                  size="small"
                  onClick={() => handleCoaViewModeChange('tree')}
                  sx={{ minWidth: 'auto', px: 1.5, fontSize: '0.75rem' }}
                >
                  Tree
                </Button>
              </Box>

              {/* Secondary Actions - Right Side */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {selectedAccounts.size > 0 && (
                  <Chip 
                    label={`${selectedAccounts.size} selected`} 
                    color="primary" 
                    size="small"
                    sx={{ height: 24, fontSize: '0.75rem' }}
                  />
                )}
                
                <Tooltip title="More Actions">
                  <IconButton
                    onClick={(e) => setActionMenuAnchor(e.currentTarget)}
                    size="small"
                  >
                    <MoreVertIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          </Paper>

          {/* Bulk Actions Toolbar - Sticky below ribbon when accounts selected */}
          {selectedAccounts.size > 0 && (
            <Paper
              elevation={0}
              sx={{
                position: 'sticky',
                top: 48, // Below compact ribbon
                zIndex: 9,
                bgcolor: 'action.selected',
                borderBottom: '1px solid',
                borderColor: 'divider',
                py: 0.5
              }}
            >
              <Toolbar 
                variant="dense" 
                sx={{ 
                  pl: 1.5, 
                  pr: 1, 
                  minHeight: '40px !important'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, gap: 1 }}>
                  <Chip 
                    label={`${selectedAccounts.size} selected`} 
                    color="primary" 
                    size="small"
                    sx={{ height: 24 }}
                  />
                </Box>
                
                <Box sx={{ display: 'flex', gap: 0.5 }}>
                  <Tooltip title="More Actions">
                    <IconButton
                      onClick={(e) => setActionMenuAnchor(e.currentTarget)}
                      size="small"
                    >
                      <MoreVertIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Toolbar>
            </Paper>
          )}

          {/* Secondary Actions Menu - Shared Across All Views */}
          <Menu
            anchorEl={actionMenuAnchor}
            open={Boolean(actionMenuAnchor)}
            onClose={() => setActionMenuAnchor(null)}
          >
            {/* Secondary Actions */}
            <MenuItem onClick={() => {
              handleExportCSV();
              setActionMenuAnchor(null);
            }}>
              <DownloadIcon sx={{ mr: 2, fontSize: 20 }} />
              Export CSV
            </MenuItem>
            <MenuItem onClick={() => {
              setShowImportDialog(true);
              setActionMenuAnchor(null);
            }}>
              <UploadIcon sx={{ mr: 2, fontSize: 20 }} />
              Import CSV
            </MenuItem>
            <MenuItem onClick={() => {
              setShowMergeDialog(true);
              setActionMenuAnchor(null);
            }}>
              <AccountBalanceIcon sx={{ mr: 2, fontSize: 20 }} />
              Merge Accounts
            </MenuItem>
            <MenuItem onClick={() => {
              setShowIndustryTemplates(true);
              setActionMenuAnchor(null);
            }}>
              <MagicIcon sx={{ mr: 2, fontSize: 20 }} />
              Templates
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => {
              handleToggleAccountCodes();
              setActionMenuAnchor(null);
            }}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <Box sx={{ flexGrow: 1 }}>Show Account Codes</Box>
                <Switch
                  checked={showAccountCodes}
                  size="small"
                  readOnly
                />
              </Box>
            </MenuItem>
            <MenuItem onClick={() => {
              setShowAnalytics(!showAnalytics);
              setActionMenuAnchor(null);
            }}>
              <InsightsIcon sx={{ mr: 2, fontSize: 20 }} />
              {showAnalytics ? 'Hide' : 'Show'} Analytics
            </MenuItem>
            {/* Bulk Actions - Only show when accounts are selected */}
            {selectedAccounts.size > 0 && (
              <>
                <Divider />
                <MenuItem onClick={() => {
                  handleBulkEdit();
                  setActionMenuAnchor(null);
                }}>
                  <EditIcon sx={{ mr: 2, fontSize: 20 }} />
                  Bulk Edit ({selectedAccounts.size})
                </MenuItem>
                {selectedAccountsStatus.showActivate && (
                  <MenuItem onClick={() => {
                    handleBulkActivate();
                    setActionMenuAnchor(null);
                  }}>
                    <VisibilityIcon sx={{ mr: 2, fontSize: 20, color: 'success.main' }} />
                    Activate Selected ({selectedAccounts.size})
                  </MenuItem>
                )}
                {selectedAccountsStatus.showDeactivate && (
                  <MenuItem onClick={() => {
                    handleBulkDeactivate();
                    setActionMenuAnchor(null);
                  }}>
                    <VisibilityOffIcon sx={{ mr: 2, fontSize: 20, color: 'warning.main' }} />
                    Deactivate Selected ({selectedAccounts.size})
                  </MenuItem>
                )}
                <MenuItem onClick={() => {
                  handleBulkDelete();
                  setActionMenuAnchor(null);
                }}>
                  <DeleteIcon sx={{ mr: 2, fontSize: 20, color: 'error.main' }} />
                  Delete Selected ({selectedAccounts.size})
                </MenuItem>
                <Divider />
                <MenuItem onClick={() => {
                  setShowOnlySelected(!showOnlySelected);
                  setActionMenuAnchor(null);
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                    <Box sx={{ flexGrow: 1 }}>
                      {showOnlySelected ? 'Show All Accounts' : 'Show Selected Only'}
                    </Box>
                    <Switch
                      checked={showOnlySelected}
                      size="small"
                      readOnly
                    />
                  </Box>
                </MenuItem>
                <MenuItem onClick={() => {
                  setSelectedAccounts(new Set());
                  setActionMenuAnchor(null);
                }}>
                  Clear Selection
                </MenuItem>
              </>
            )}
          </Menu>
        </>
      )}

      {accountsToUse.length > 0 && (
        coaViewMode === 'progressive' ? (
          <ProgressiveCoA 
            accounts={accountsToUse}
            onAccountSelect={(account) => {
              setSelectedAccountDetails(account);
              setShowDetailsPanel(true);
            }}
            onModeChange={(mode) => {}}
            showAccountCodes={showAccountCodes}
          />
        ) : coaViewMode === 'table' ? (
          <>
            {/* Enhanced Table - Full Page (No Container Constraints) */}
            <TableContainer>
                {filteredAccounts.length === 0 ? (
                  <Box sx={{ p: 4, textAlign: 'center' }}>
                    <Typography variant="body1" color="text.secondary">
                      {showOnlySelected ? 'No accounts selected' : 'No accounts found'}
                    </Typography>
                  </Box>
                ) : (
                  <Table stickyHeader>
                    <TableHead>
                      <TableRow sx={{ bgcolor: 'grey.50' }}>
                        <TableCell padding="checkbox" sx={{ bgcolor: 'grey.50', fontWeight: 600 }}>
                          <Checkbox
                            indeterminate={isIndeterminate}
                            checked={isAllSelected}
                            onChange={(e) => handleSelectAll(e.target.checked)}
                            inputProps={{ 'aria-label': 'select all accounts' }}
                          />
                        </TableCell>
                        {showAccountCodes && (
                          <TableCell sx={{ bgcolor: 'grey.50', fontWeight: 600 }}>
                            <TableSortLabel
                              active={sortBy === 'code'}
                              direction={sortBy === 'code' ? sortDirection : 'asc'}
                              onClick={() => handleSort('code')}
                            >
                              Account Code
                            </TableSortLabel>
                          </TableCell>
                        )}
                        <TableCell sx={{ bgcolor: 'grey.50', fontWeight: 600 }}>
                          <TableSortLabel
                            active={sortBy === 'account_name'}
                            direction={sortBy === 'account_name' ? sortDirection : 'asc'}
                            onClick={() => handleSort('account_name')}
                          >
                            Account Name
                          </TableSortLabel>
                        </TableCell>
                        <TableCell sx={{ bgcolor: 'grey.50', fontWeight: 600 }}>
                          <TableSortLabel
                            active={sortBy === 'account_type'}
                            direction={sortBy === 'account_type' ? sortDirection : 'asc'}
                            onClick={() => handleSort('account_type')}
                          >
                            Type
                          </TableSortLabel>
                        </TableCell>
                        <TableCell sx={{ bgcolor: 'grey.50', fontWeight: 600 }}>
                          <TableSortLabel
                            active={sortBy === 'balance'}
                            direction={sortBy === 'balance' ? sortDirection : 'asc'}
                            onClick={() => handleSort('balance')}
                          >
                            Balance
                          </TableSortLabel>
                        </TableCell>
                        <TableCell sx={{ bgcolor: 'grey.50', fontWeight: 600 }}>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filteredAccounts.map((account) => {
                        const isSelected = selectedAccounts.has(account.id);
                        const accountType = account.account_type || account.type;
                        const accountName = account.account_name || account.name;
                        const balance = account.balance || 0;
                        
                        return (
                          <TableRow
                            key={account.id}
                            hover
                            selected={isSelected}
                            onClick={(e) => handleRowClick(account, e)}
                            sx={{ 
                              cursor: 'pointer',
                              transition: 'all 0.2s ease',
                              '&:hover': { 
                                backgroundColor: accountType === 'asset' ? 'rgba(46, 125, 50, 0.04)' :
                                               accountType === 'liability' ? 'rgba(198, 40, 40, 0.04)' :
                                               accountType === 'equity' ? 'rgba(21, 101, 192, 0.04)' :
                                               accountType === 'revenue' ? 'rgba(123, 31, 162, 0.04)' :
                                               'rgba(230, 81, 0, 0.04)',
                                transform: 'translateX(2px)'
                              },
                              opacity: account.is_active === false ? 0.6 : 1,
                              borderLeft: `3px solid ${
                                accountType === 'asset' ? '#4caf50' :
                                accountType === 'liability' ? '#f44336' :
                                accountType === 'equity' ? '#2196f3' :
                                accountType === 'revenue' ? '#9c27b0' :
                                '#ff9800'
                              }`
                            }}
                          >
                            <TableCell padding="checkbox" onClick={(e) => e.stopPropagation()}>
                              <Checkbox
                                checked={isSelected}
                                onChange={(e) => {
                                  e.stopPropagation();
                                  handleSelectAccount(account.id, e.target.checked);
                                }}
                                inputProps={{ 'aria-labelledby': `account-${account.id}` }}
                              />
                            </TableCell>
                            {showAccountCodes && (
                              <TableCell>
                                <Typography 
                                  variant="body2" 
                                  sx={{ 
                                    fontFamily: 'monospace',
                                    fontWeight: 500,
                                    color: 'text.secondary'
                                  }}
                                >
                                  {account.code || 'N/A'}
                                </Typography>
                              </TableCell>
                            )}
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography 
                                  variant="body2" 
                                  id={`account-${account.id}`}
                                  fontWeight="medium"
                                  sx={{ 
                                    maxWidth: 200, 
                                    overflow: 'hidden', 
                                    textOverflow: 'ellipsis' 
                                  }}
                                >
                                  {accountName}
                                </Typography>
                                {account.is_core && (
                                  <Chip 
                                    label="Core" 
                                    size="small" 
                                    color="primary"
                                    variant="filled"
                                    sx={{ height: 20, fontSize: '0.65rem', fontWeight: 'bold' }}
                                  />
                                )}
                                {account.is_default && !account.is_core && (
                                  <Chip 
                                    label="Default" 
                                    size="small" 
                                    color="primary"
                                    variant="outlined"
                                    sx={{ height: 20, fontSize: '0.65rem' }}
                                  />
                                )}
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Chip 
                                label={accountType} 
                                size="small"
                                sx={{
                                  bgcolor: 
                                    accountType === 'asset' ? '#e8f5e9' :
                                    accountType === 'liability' ? '#ffebee' :
                                    accountType === 'equity' ? '#e3f2fd' :
                                    accountType === 'revenue' ? '#f3e5f5' :
                                    '#fff3e0',
                                  color:
                                    accountType === 'asset' ? '#2e7d32' :
                                    accountType === 'liability' ? '#c62828' :
                                    accountType === 'equity' ? '#1565c0' :
                                    accountType === 'revenue' ? '#7b1fa2' :
                                    '#e65100',
                                  fontWeight: 600,
                                  border: 'none'
                                }}
                              />
                            </TableCell>
                            <TableCell>
                              <Typography 
                                variant="body2" 
                                color={balance >= 0 ? 'text.primary' : 'error.main'}
                                fontWeight="medium"
                              >
                                {formatAmount(balance)}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Chip
                                  label={account.is_active === false ? 'Inactive' : 'Active'}
                                  size="small"
                                  color={account.is_active === false ? 'error' : 'success'}
                                  variant="outlined"
                                  sx={{ height: 24, fontSize: '0.7rem' }}
                                />
                                {accountHealthAndInsights.healthScores[account.id] && (
                                  <Tooltip title={`Health: ${accountHealthAndInsights.healthScores[account.id].score}/100 - ${accountHealthAndInsights.healthScores[account.id].status}`}>
                                    <Chip
                                      size="small"
                                      icon={
                                        accountHealthAndInsights.healthScores[account.id].status === 'healthy' ? <CheckCircleIcon /> :
                                        accountHealthAndInsights.healthScores[account.id].status === 'warning' ? <WarningIcon /> :
                                        <ErrorIcon />
                                      }
                                      label={accountHealthAndInsights.healthScores[account.id].score}
                                      color={
                                        accountHealthAndInsights.healthScores[account.id].status === 'healthy' ? 'success' :
                                        accountHealthAndInsights.healthScores[account.id].status === 'warning' ? 'warning' :
                                        'error'
                                      }
                                      sx={{ height: 20, fontSize: '0.65rem' }}
                                    />
                                  </Tooltip>
                                )}
                              </Box>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                )}
              </TableContainer>
          </>
        ) : coaViewMode === 'tree' ? (
          <CoATreeEnhanced 
            accounts={accountsToUse}
            onSelect={handleEdit}
            selectedAccounts={selectedAccounts}
            onSelectAccount={handleSelectAccount}
          />
        ) : null
      )}

      <Dialog 
        open={openDialog} 
        onClose={handleDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {currentAccount ? 'Edit Account' : 'Add New Account'}
        </DialogTitle>
        <DialogContent>
          {currentAccount ? (
            // Edit mode - always show custom form
            <CoAForm 
              selectedAccount={currentAccount}
              onDone={handleDialogClose}
              allAccounts={accountsToUse}
              showAccountCodes={showAccountCodes}
            />
          ) : (
            // Add mode - show tabs
            <Box>
              <Tabs 
                value={addAccountMode} 
                onChange={(e, newValue) => setAddAccountMode(newValue)}
                sx={{ mb: 3, borderBottom: 1, borderColor: 'divider' }}
              >
                <Tab label="In-App Accounts" value="templates" />
                <Tab label="Custom Account" value="custom" />
              </Tabs>

              {addAccountMode === 'templates' ? (
                // Template selection view
                <Box>
                  <TextField
                    fullWidth
                    placeholder="Search templates..."
                    value={templateSearchTerm}
                    onChange={(e) => setTemplateSearchTerm(e.target.value)}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <SearchIcon />
                        </InputAdornment>
                      )
                    }}
                    sx={{ mb: 3 }}
                  />

                  {filteredTemplates.length === 0 ? (
                    <Alert severity="info" sx={{ mb: 2 }}>
                      {templateSearchTerm 
                        ? 'No templates match your search. Try different keywords.'
                        : 'You already have all available account templates. Create a custom account instead.'}
                    </Alert>
                  ) : (
                    <>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          {filteredTemplates.length} template{filteredTemplates.length !== 1 ? 's' : ''} available
                          {selectedTemplates.size > 0 && ` • ${selectedTemplates.size} selected`}
                        </Typography>
                        {selectedTemplates.size > 0 && (
                          <Button
                            size="small"
                            onClick={() => setSelectedTemplates(new Set())}
                          >
                            Clear Selection
                          </Button>
                        )}
                      </Box>

                      <Box sx={{ maxHeight: '400px', overflowY: 'auto', mb: 2 }}>
                        {Object.entries(groupedTemplates).map(([category, templates]) => (
                          <Box key={category} sx={{ mb: 3 }}>
                            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: 'text.secondary' }}>
                              {category}
                            </Typography>
                            <Grid container spacing={1}>
                              {templates.map((template) => {
                                const isSelected = selectedTemplates.has(template.name);
                                return (
                                  <Grid item xs={12} sm={6} key={template.name}>
                                    <Card
                                      sx={{
                                        cursor: 'pointer',
                                        border: isSelected ? 2 : 1,
                                        borderColor: isSelected ? 'primary.main' : 'divider',
                                        bgcolor: isSelected ? 'action.selected' : 'background.paper',
                                        '&:hover': {
                                          borderColor: 'primary.main',
                                          bgcolor: 'action.hover'
                                        }
                                      }}
                                      onClick={() => handleTemplateToggle(template.name)}
                                    >
                                      <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                                        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
                                          <Checkbox
                                            checked={isSelected}
                                            size="small"
                                            sx={{ p: 0, mt: -0.5 }}
                                          />
                                          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                                            <Typography variant="body2" sx={{ fontWeight: 500, mb: 0.5 }}>
                                              {template.name}
                                            </Typography>
                                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                                              {template.description}
                                            </Typography>
                                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                              <Chip 
                                                label={template.type} 
                                                size="small" 
                                                sx={{ height: 20, fontSize: '0.65rem' }}
                                                color="primary"
                                                variant="outlined"
                                              />
                                              {showAccountCodes && (
                                                <Chip 
                                                  label={`Code: ${template.suggestedCode}`} 
                                                  size="small" 
                                                  sx={{ height: 20, fontSize: '0.65rem', fontFamily: 'monospace' }}
                                                  variant="outlined"
                                                />
                                              )}
                                            </Box>
                                          </Box>
                                        </Box>
                                      </CardContent>
                                    </Card>
                                  </Grid>
                                );
                              })}
                            </Grid>
                          </Box>
                        ))}
                      </Box>

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', pt: 2, borderTop: 1, borderColor: 'divider' }}>
                        <Typography variant="body2" color="text.secondary">
                          {selectedTemplates.size > 0 
                            ? `${selectedTemplates.size} template${selectedTemplates.size !== 1 ? 's' : ''} selected`
                            : 'Select templates to add'}
                        </Typography>
                        <Button
                          variant="contained"
                          onClick={handleAddSelectedTemplates}
                          disabled={selectedTemplates.size === 0}
                          startIcon={<AddIcon />}
                        >
                          Add Selected ({selectedTemplates.size})
                        </Button>
                      </Box>
                    </>
                  )}
                </Box>
              ) : (
                // Custom account form
                <CoAForm 
                  selectedAccount={null}
                  onDone={handleDialogClose}
                  allAccounts={accountsToUse}
                  showAccountCodes={showAccountCodes}
                />
              )}
            </Box>
          )}
        </DialogContent>
        {currentAccount && (
          <DialogActions>
            <Button onClick={handleDialogClose}>Cancel</Button>
          </DialogActions>
        )}
      </Dialog>



      {/* Industry Templates Dialog */}
      <Dialog 
        open={showIndustryTemplates} 
        onClose={() => setShowIndustryTemplates(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Import Industry Template</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Select an industry template to add specialized accounts to your Chart of Accounts. 
            These will be added in addition to your existing accounts.
          </Typography>
          <Grid container spacing={2}>
            {[
              { id: 'retail', name: 'Retail Business', description: 'Stores, e-commerce, inventory management', accounts: 45 },
              { id: 'services', name: 'Services Business', description: 'Consulting, agencies, service providers', accounts: 38 },
              { id: 'manufacturing', name: 'Manufacturing', description: 'Production, equipment, inventory', accounts: 52 },
              { id: 'freelancer', name: 'Freelancer/Solo', description: 'Individual entrepreneurs', accounts: 25 },
              { id: 'ngo', name: 'Non-Profit', description: 'Charitable organizations', accounts: 41 }
            ].map((template) => (
              <Grid item xs={12} md={6} key={template.id}>
                <Card 
                  variant="outlined"
                  sx={{ 
                    cursor: 'pointer',
                    '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' }
                  }}
                  onClick={async () => {
                    try {
                      setSnackbar({
                        open: true,
                        message: `Industry template "${template.name}" import feature coming soon!`,
                        severity: 'info'
                      });
                      setShowIndustryTemplates(false);
                    } catch (error) {
                      setSnackbar({
                        open: true,
                        message: 'Failed to import template: ' + (error.message || 'Unknown error'),
                        severity: 'error'
                      });
                    }
                  }}
                >
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      {template.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {template.description}
                    </Typography>
                    <Chip label={`${template.accounts} accounts`} size="small" color="primary" variant="outlined" />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowIndustryTemplates(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Edit Dialog */}
      <Dialog 
        open={showBulkEditDialog} 
        onClose={() => setShowBulkEditDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <EditIcon color="primary" />
            <Typography variant="h6" component="span">
              Bulk Edit {selectedAccounts.size} Account{selectedAccounts.size !== 1 ? 's' : ''}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Update the following fields for all selected accounts. Leave fields empty to keep current values.
          </Typography>
          
          <Stack spacing={3} sx={{ mt: 1 }}>
            {/* Account Type Section */}
            <Box>
              <FormLabel sx={{ mb: 1.5, display: 'block', fontWeight: 600 }}>
                Account Type
              </FormLabel>
              <FormControl fullWidth>
                <Select
                  value={bulkEditForm.type}
                  onChange={(e) => setBulkEditForm({ ...bulkEditForm, type: e.target.value })}
                  displayEmpty
                  sx={{ 
                    '& .MuiSelect-select': {
                      py: 1.5
                    }
                  }}
                >
                  <MenuItem value="">
                    <em>Keep current type</em>
                  </MenuItem>
                  <MenuItem value="asset">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: '#4caf50' }} />
                      Asset
                    </Box>
                  </MenuItem>
                  <MenuItem value="liability">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: '#f44336' }} />
                      Liability
                    </Box>
                  </MenuItem>
                  <MenuItem value="equity">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: '#2196f3' }} />
                      Equity
                    </Box>
                  </MenuItem>
                  <MenuItem value="revenue">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: '#9c27b0' }} />
                      Revenue
                    </Box>
                  </MenuItem>
                  <MenuItem value="expense">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: '#ff9800' }} />
                      Expense
                    </Box>
                  </MenuItem>
                </Select>
              </FormControl>
            </Box>

            <Divider />

            {/* Description Section */}
            <Box>
              <FormLabel sx={{ mb: 1.5, display: 'block', fontWeight: 600 }}>
                Description
              </FormLabel>
              <TextField
                fullWidth
                multiline
                rows={3}
                placeholder="Leave empty to keep current descriptions"
                value={bulkEditForm.description}
                onChange={(e) => setBulkEditForm({ ...bulkEditForm, description: e.target.value })}
                helperText="This will replace the description for all selected accounts"
              />
            </Box>

            <Divider />

            {/* Parent Account Section */}
            <Box>
              <FormLabel sx={{ mb: 1.5, display: 'block', fontWeight: 600 }}>
                Parent Account
              </FormLabel>
              <FormControl fullWidth>
                <Select
                  value={bulkEditForm.parent_id === null ? 'REMOVE_PARENT' : (bulkEditForm.parent_id || '')}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === 'REMOVE_PARENT') {
                      setBulkEditForm({ ...bulkEditForm, parent_id: null });
                    } else {
                      setBulkEditForm({ ...bulkEditForm, parent_id: value });
                    }
                  }}
                  displayEmpty
                  sx={{ 
                    '& .MuiSelect-select': {
                      py: 1.5
                    }
                  }}
                >
                  <MenuItem value="">
                    <em>Keep current parent</em>
                  </MenuItem>
                  <MenuItem value="REMOVE_PARENT">
                    <em>Remove parent (make top-level)</em>
                  </MenuItem>
                  {accountsToUse
                    .filter(acc => !selectedAccounts.has(acc.id)) // Don't allow selecting one of the accounts being edited
                    .map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.code ? `${account.code} - ` : ''}
                        {account.account_name || account.name || 'Unnamed Account'}
                      </MenuItem>
                    ))}
                </Select>
              </FormControl>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Select a parent account to organize accounts hierarchically. Circular references are prevented.
              </Typography>
            </Box>

            <Divider />

            {/* Category Section */}
            <Box>
              <FormLabel sx={{ mb: 1.5, display: 'block', fontWeight: 600 }}>
                Category
              </FormLabel>
              <TextField
                fullWidth
                placeholder="e.g., Operating, Non-Operating, Investment"
                value={bulkEditForm.category}
                onChange={(e) => setBulkEditForm({ ...bulkEditForm, category: e.target.value })}
                helperText="Leave empty to keep current categories"
              />
            </Box>

            <Divider />

            {/* Active Status Section */}
            <Box>
              <FormLabel sx={{ mb: 1.5, display: 'block', fontWeight: 600 }}>
                Active Status
              </FormLabel>
              <FormControl component="fieldset">
                <RadioGroup
                  row
                  value={bulkEditForm.is_active === null ? '' : bulkEditForm.is_active ? 'active' : 'inactive'}
                  onChange={(e) => {
                    const value = e.target.value;
                    setBulkEditForm({ 
                      ...bulkEditForm, 
                      is_active: value === '' ? null : value === 'active' 
                    });
                  }}
                >
                  <FormControlLabel 
                    value="" 
                    control={<Radio />} 
                    label="Keep current status" 
                  />
                  <FormControlLabel 
                    value="active" 
                    control={<Radio />} 
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <CheckCircleIcon color="success" sx={{ fontSize: 18 }} />
                        <span>Activate All</span>
                      </Box>
                    } 
                  />
                  <FormControlLabel 
                    value="inactive" 
                    control={<Radio />} 
                    label={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <CancelIcon color="warning" sx={{ fontSize: 18 }} />
                        <span>Deactivate All</span>
                      </Box>
                    } 
                  />
                </RadioGroup>
              </FormControl>
            </Box>
          </Stack>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button 
            onClick={() => {
              setShowBulkEditDialog(false);
              // Reset form on cancel
              setBulkEditForm({
                type: '',
                description: '',
                parent_id: '',
                category: '',
                is_active: null
              });
            }}
            variant="outlined"
          >
            Cancel
          </Button>
          <Button 
            onClick={() => handleBulkEditSubmit()}
            variant="contained"
            color="primary"
            startIcon={<CheckCircleIcon />}
          >
            Apply Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Import Dialog */}
      <Dialog 
        open={showImportDialog} 
        onClose={() => setShowImportDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Import Accounts from CSV</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Upload a CSV file with the following columns: Code, Name, Type, Balance, Currency, Parent Code, Active, Notes
          </Typography>
          <Button
            variant="outlined"
            component="label"
            startIcon={<UploadIcon />}
            fullWidth
            sx={{ mb: 2 }}
          >
            Choose CSV File
            <input
              type="file"
              hidden
              accept=".csv"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  handleImportCSV(file);
                }
              }}
            />
          </Button>
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>CSV Format:</strong><br />
              Code, Name, Type, Balance, Currency, Parent Code, Active, Notes<br />
              Example: 1000, Cash, asset, 50000, USD, , Yes, Main cash account<br />
              <br />
              <strong>Note:</strong> Accounts with existing codes will be updated. New codes will create new accounts.
            </Typography>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowImportDialog(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      {/* Merge Accounts Dialog */}
      <Dialog 
        open={showMergeDialog} 
        onClose={() => {
          setShowMergeDialog(false);
          setMergeSourceAccount(null);
          setMergeTargetAccount(null);
          setMergeConfirmationText('');
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AccountBalanceIcon color="primary" />
            <Typography variant="h6" component="span">
              Merge Accounts
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 3 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
              Important: This action cannot be undone
            </Typography>
            <Typography variant="body2">
              Merging will transfer all balance and transactions from the source account to the target account, 
              then delete the source account. Both accounts must be of the same type, active, and use the same currency.
            </Typography>
          </Alert>

          {/* Default account codes for filtering */}
          {(() => {
            const defaultCodes = new Set([
              '1000', '1100', '1200', '1300', '1400', '1500',  // Assets
              '2000', '2100', '2200', '2300',  // Liabilities
              '3000', '3100', '3200',  // Equity
              '4000', '4100',  // Revenue
              '5000', '6000', '6100', '6200', '6300', '6400', '6500', '6600', '6700', '6800'  // Expenses
            ]);
            
            // Filter accounts: exclude default accounts and inactive accounts
            const mergeableAccounts = accountsToUse.filter(acc => {
              const isDefault = acc.code && defaultCodes.has(acc.code);
              const isActive = acc.is_active !== false;
              return !isDefault && isActive;
            });

            return (
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Source Account (to merge from)</InputLabel>
                    <Select
                      value={mergeSourceAccount?.id || ''}
                      onChange={(e) => {
                        const account = mergeableAccounts.find(acc => acc.id === e.target.value);
                        setMergeSourceAccount(account || null);
                        setMergeConfirmationText(''); // Reset confirmation
                      }}
                      label="Source Account (to merge from)"
                    >
                      <MenuItem value="">
                        <em>Select source account</em>
                      </MenuItem>
                      {mergeableAccounts
                        .filter(acc => !mergeTargetAccount || acc.id !== mergeTargetAccount.id)
                        .map((account) => (
                        <MenuItem key={account.id} value={account.id}>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {account.name || account.account_name}
                            </Typography>
                            {showAccountCodes && account.code && (
                              <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                                {account.code} • {account.type} • Balance: {formatAmount(account.balance || 0)}
                              </Typography>
                            )}
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  {mergeSourceAccount && (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                      <Typography variant="caption" color="text.secondary">Source Account Details</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 500, mt: 0.5 }}>
                        {mergeSourceAccount.name || mergeSourceAccount.account_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                        Code: {mergeSourceAccount.code} • Type: {mergeSourceAccount.type} • 
                        Balance: {formatAmount(mergeSourceAccount.balance || 0)} • 
                        Currency: {mergeSourceAccount.currency || 'USD'}
                      </Typography>
                    </Box>
                  )}
                </Grid>

                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Target Account (to merge into)</InputLabel>
                    <Select
                      value={mergeTargetAccount?.id || ''}
                      onChange={(e) => {
                        const account = mergeableAccounts.find(acc => acc.id === e.target.value);
                        setMergeTargetAccount(account || null);
                        setMergeConfirmationText(''); // Reset confirmation
                      }}
                      label="Target Account (to merge into)"
                    >
                      <MenuItem value="">
                        <em>Select target account</em>
                      </MenuItem>
                      {mergeableAccounts
                        .filter(acc => !mergeSourceAccount || acc.id !== mergeSourceAccount.id)
                        .map((account) => (
                        <MenuItem key={account.id} value={account.id}>
                          <Box>
                            <Typography variant="body2" sx={{ fontWeight: 500 }}>
                              {account.name || account.account_name}
                            </Typography>
                            {showAccountCodes && account.code && (
                              <Typography variant="caption" color="text.secondary" sx={{ fontFamily: 'monospace' }}>
                                {account.code} • {account.type} • Balance: {formatAmount(account.balance || 0)}
                              </Typography>
                            )}
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                  {mergeTargetAccount && (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                      <Typography variant="caption" color="text.secondary">Target Account Details</Typography>
                      <Typography variant="body2" sx={{ fontWeight: 500, mt: 0.5 }}>
                        {mergeTargetAccount.name || mergeTargetAccount.account_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                        Code: {mergeTargetAccount.code} • Type: {mergeTargetAccount.type} • 
                        Balance: {formatAmount(mergeTargetAccount.balance || 0)} • 
                        Currency: {mergeTargetAccount.currency || 'USD'}
                      </Typography>
                    </Box>
                  )}
                </Grid>

                {/* Validation Status */}
                {mergeSourceAccount && mergeTargetAccount && (
                  <Grid item xs={12}>
                    {mergeValidation.status === 'blocked' && (
                      <Alert severity="error" sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                          Cannot Merge - Validation Errors:
                        </Typography>
                        <Box component="ul" sx={{ m: 0, pl: 2 }}>
                          {mergeValidation.blockers.map((blocker, idx) => (
                            <Typography key={idx} component="li" variant="body2" sx={{ mb: 0.5 }}>
                              {blocker}
                            </Typography>
                          ))}
                        </Box>
                      </Alert>
                    )}
                    {mergeValidation.status === 'warning' && (
                      <Alert severity="warning" sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                          Warnings:
                        </Typography>
                        <Box component="ul" sx={{ m: 0, pl: 2 }}>
                          {mergeValidation.warnings.map((warning, idx) => (
                            <Typography key={idx} component="li" variant="body2" sx={{ mb: 0.5 }}>
                              {warning}
                            </Typography>
                          ))}
                        </Box>
                      </Alert>
                    )}
                    {mergeValidation.status === 'ready' && (
                      <Alert severity="success" sx={{ mt: 2 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                          ✓ Ready to Merge
                        </Typography>
                        <Typography variant="body2">
                          Both accounts are compatible. Balance of {formatAmount(mergeSourceAccount.balance || 0)} will be transferred to "{mergeTargetAccount.name || mergeTargetAccount.account_name}".
                        </Typography>
                      </Alert>
                    )}
                  </Grid>
                )}

                {/* Confirmation Step */}
                {mergeSourceAccount && mergeTargetAccount && mergeValidation.status !== 'blocked' && (
                  <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                    <Box>
                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                        Confirmation Required
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Type the target account name to confirm: <strong>"{mergeTargetAccount.name || mergeTargetAccount.account_name}"</strong>
                      </Typography>
                      <TextField
                        fullWidth
                        value={mergeConfirmationText}
                        onChange={(e) => setMergeConfirmationText(e.target.value)}
                        placeholder={mergeTargetAccount.name || mergeTargetAccount.account_name}
                        error={mergeConfirmationText.trim() !== '' && mergeConfirmationText.trim() !== (mergeTargetAccount.name || mergeTargetAccount.account_name || '').trim()}
                        helperText={
                          mergeConfirmationText.trim() !== '' && mergeConfirmationText.trim() !== (mergeTargetAccount.name || mergeTargetAccount.account_name || '').trim()
                            ? 'Account name does not match'
                            : 'Type the exact target account name to proceed'
                        }
                      />
                    </Box>
                  </Grid>
                )}
              </Grid>
            );
          })()}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setShowMergeDialog(false);
            setMergeSourceAccount(null);
            setMergeTargetAccount(null);
            setMergeConfirmationText('');
          }}>
            Cancel
          </Button>
          <Button
            onClick={handleMergeAccounts}
            variant="contained"
            color="primary"
            disabled={
              !mergeSourceAccount || 
              !mergeTargetAccount || 
              mergeValidation.status === 'blocked' ||
              mergeConfirmationText.trim() !== (mergeTargetAccount?.name || mergeTargetAccount?.account_name || '').trim()
            }
            startIcon={<AccountBalanceIcon />}
          >
            Merge Accounts
          </Button>
        </DialogActions>
      </Dialog>

      {/* Advanced Filter Panel */}
      <Drawer
        anchor="right"
        open={showFilterPanel}
        onClose={() => setShowFilterPanel(false)}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 400 }, p: 3 }
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">Filters</Typography>
          <IconButton onClick={() => setShowFilterPanel(false)} size="small">
            <CloseIcon />
          </IconButton>
        </Box>

        <Stack spacing={3}>
          {/* Account Type Filter */}
          <Box>
            <FormLabel component="legend" sx={{ mb: 1, fontWeight: 600 }}>Account Type</FormLabel>
            <Stack spacing={1}>
              {['asset', 'liability', 'equity', 'revenue', 'expense'].map((type) => (
                <FormControlLabel
                  key={type}
                  control={
                    <Checkbox
                      checked={filters.types.includes(type)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setFilters({ ...filters, types: [...filters.types, type] });
                        } else {
                          setFilters({ ...filters, types: filters.types.filter(t => t !== type) });
                        }
                      }}
                    />
                  }
                  label={type.charAt(0).toUpperCase() + type.slice(1)}
                />
              ))}
            </Stack>
          </Box>

          <Divider />

          {/* Balance Range Filter */}
          <Box>
            <FormLabel component="legend" sx={{ mb: 1, fontWeight: 600 }}>Balance Range</FormLabel>
            <Stack direction="row" spacing={2}>
              <TextField
                label="Min"
                type="number"
                size="small"
                value={filters.balanceMin}
                onChange={(e) => setFilters({ ...filters, balanceMin: e.target.value })}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>
                }}
                fullWidth
              />
              <TextField
                label="Max"
                type="number"
                size="small"
                value={filters.balanceMax}
                onChange={(e) => setFilters({ ...filters, balanceMax: e.target.value })}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>
                }}
                fullWidth
              />
            </Stack>
            <FormControlLabel
              control={
                <Checkbox
                  checked={filters.hideZeroBalance}
                  onChange={(e) => setFilters({ ...filters, hideZeroBalance: e.target.checked })}
                />
              }
              label="Hide zero balance accounts"
              sx={{ mt: 1 }}
            />
          </Box>

          <Divider />

          {/* Status Filter */}
          <Box>
            <FormLabel component="legend" sx={{ mb: 1, fontWeight: 600 }}>Status</FormLabel>
            <RadioGroup
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <FormControlLabel value="all" control={<Radio />} label="All" />
              <FormControlLabel value="active" control={<Radio />} label="Active Only" />
              <FormControlLabel value="inactive" control={<Radio />} label="Inactive Only" />
            </RadioGroup>
          </Box>

          <Divider />

          {/* Account Code Range Filter (only if codes are enabled) */}
          {showAccountCodes && (
            <>
              <Box>
                <FormLabel component="legend" sx={{ mb: 1, fontWeight: 600 }}>Account Code Range</FormLabel>
                <Stack direction="row" spacing={2}>
                  <TextField
                    label="Min Code"
                    type="number"
                    size="small"
                    value={filters.codeMin}
                    onChange={(e) => setFilters({ ...filters, codeMin: e.target.value })}
                    fullWidth
                    sx={{ fontFamily: 'monospace' }}
                  />
                  <TextField
                    label="Max Code"
                    type="number"
                    size="small"
                    value={filters.codeMax}
                    onChange={(e) => setFilters({ ...filters, codeMax: e.target.value })}
                    fullWidth
                    sx={{ fontFamily: 'monospace' }}
                  />
                </Stack>
              </Box>
              <Divider />
            </>
          )}

          {/* Core Accounts Only */}
          <Box>
            <FormControlLabel
              control={
                <Checkbox
                  checked={filters.coreOnly}
                  onChange={(e) => setFilters({ ...filters, coreOnly: e.target.checked })}
                />
              }
              label="Core accounts only"
            />
          </Box>

          <Divider />

          {/* Action Buttons */}
          <Stack direction="row" spacing={2}>
            <Button
              variant="outlined"
              onClick={() => {
                setFilters({
                  types: [],
                  balanceMin: '',
                  balanceMax: '',
                  hideZeroBalance: false,
                  status: 'all',
                  codeMin: '',
                  codeMax: '',
                  coreOnly: false
                });
              }}
              fullWidth
            >
              Clear All
            </Button>
            <Button
              variant="contained"
              onClick={() => setShowFilterPanel(false)}
              fullWidth
            >
              Apply Filters
            </Button>
          </Stack>
        </Stack>
      </Drawer>

      {/* Active Filter Chips */}
      {activeFilterCount > 0 && (
        <Paper sx={{ p: 1.5, mb: 2 }}>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
            <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
              Active filters:
            </Typography>
            {filters.types.length > 0 && filters.types.map(type => (
              <Chip
                key={type}
                label={`Type: ${type}`}
                size="small"
                onDelete={() => {
                  setFilters({ ...filters, types: filters.types.filter(t => t !== type) });
                }}
              />
            ))}
            {filters.balanceMin && (
              <Chip
                label={`Min: $${filters.balanceMin}`}
                size="small"
                onDelete={() => setFilters({ ...filters, balanceMin: '' })}
              />
            )}
            {filters.balanceMax && (
              <Chip
                label={`Max: $${filters.balanceMax}`}
                size="small"
                onDelete={() => setFilters({ ...filters, balanceMax: '' })}
              />
            )}
            {filters.hideZeroBalance && (
              <Chip
                label="Hide Zero Balance"
                size="small"
                onDelete={() => setFilters({ ...filters, hideZeroBalance: false })}
              />
            )}
            {filters.status !== 'all' && (
              <Chip
                label={`Status: ${filters.status}`}
                size="small"
                onDelete={() => setFilters({ ...filters, status: 'all' })}
              />
            )}
            {showAccountCodes && filters.codeMin && (
              <Chip
                label={`Code Min: ${filters.codeMin}`}
                size="small"
                onDelete={() => setFilters({ ...filters, codeMin: '' })}
              />
            )}
            {showAccountCodes && filters.codeMax && (
              <Chip
                label={`Code Max: ${filters.codeMax}`}
                size="small"
                onDelete={() => setFilters({ ...filters, codeMax: '' })}
              />
            )}
            {filters.coreOnly && (
              <Chip
                label="Core Only"
                size="small"
                onDelete={() => setFilters({ ...filters, coreOnly: false })}
              />
            )}
            <Button
              size="small"
              onClick={() => {
                setFilters({
                  types: [],
                  balanceMin: '',
                  balanceMax: '',
                  hideZeroBalance: false,
                  status: 'all',
                  codeMin: '',
                  codeMax: '',
                  coreOnly: false
                });
              }}
              sx={{ ml: 'auto' }}
            >
              Clear All
            </Button>
          </Box>
        </Paper>
      )}

      {/* Account Details Panel */}
      <Drawer
        anchor="right"
        open={showDetailsPanel}
        onClose={handleCloseDetailsPanel}
        PaperProps={{
          sx: { width: { xs: '100%', sm: 500 }, p: 0 }
        }}
      >
        {selectedAccountDetails && (
          <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <Box sx={{ 
              p: 3, 
              bgcolor: 'primary.main', 
              color: 'white',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start'
            }}>
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 600, mb: 1 }}>
                  {selectedAccountDetails.account_name || selectedAccountDetails.name}
                </Typography>
                <Stack direction="row" spacing={1} sx={{ mb: 1 }}>
                  <Chip 
                    label={selectedAccountDetails.account_type || selectedAccountDetails.type}
                    size="small"
                    sx={{ 
                      bgcolor: 'rgba(255,255,255,0.2)', 
                      color: 'white',
                      fontWeight: 600
                    }}
                  />
                  {showAccountCodes && selectedAccountDetails.code && (
                    <Chip 
                      label={`Code: ${selectedAccountDetails.code}`}
                      size="small"
                      sx={{ 
                        bgcolor: 'rgba(255,255,255,0.2)', 
                        color: 'white',
                        fontFamily: 'monospace'
                      }}
                    />
                  )}
                  <Chip 
                    label={selectedAccountDetails.is_active === false ? 'Inactive' : 'Active'}
                    size="small"
                    color={selectedAccountDetails.is_active === false ? 'error' : 'success'}
                    sx={{ bgcolor: 'rgba(255,255,255,0.9)' }}
                  />
                </Stack>
                <Typography variant="h4" sx={{ fontWeight: 700 }}>
                  {formatAmount(selectedAccountDetails.balance || 0)}
                </Typography>
              </Box>
              <IconButton 
                onClick={handleCloseDetailsPanel}
                sx={{ color: 'white' }}
                size="small"
              >
                <CloseIcon />
              </IconButton>
            </Box>

            {/* Content */}
            <Box sx={{ flexGrow: 1, overflow: 'auto', p: 3 }}>
              {/* Account Information */}
              <Card sx={{ mb: 2 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      Account Information
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        {selectedAccountDetails.is_active === false ? 'Inactive' : 'Active'}
                      </Typography>
                      <Switch
                        checked={selectedAccountDetails.is_active !== false}
                        onChange={handleToggleAccountActiveFromDetails}
                        color="primary"
                        size="small"
                      />
                    </Box>
                  </Box>
                  <Stack spacing={2}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Account Name
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {selectedAccountDetails.account_name || selectedAccountDetails.name}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Account Type
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {(selectedAccountDetails.account_type || selectedAccountDetails.type || '').charAt(0).toUpperCase() + 
                         (selectedAccountDetails.account_type || selectedAccountDetails.type || '').slice(1)}
                      </Typography>
                    </Box>
                    {showAccountCodes && selectedAccountDetails.code && (
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Account Code
                        </Typography>
                        <Typography variant="body1" sx={{ fontWeight: 500, fontFamily: 'monospace' }}>
                          {selectedAccountDetails.code}
                        </Typography>
                      </Box>
                    )}
                    {selectedAccountDetails.description && (
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Description
                        </Typography>
                        <Typography variant="body1">
                          {selectedAccountDetails.description}
                        </Typography>
                      </Box>
                    )}
                    {selectedAccountDetails.notes && (
                      <Box>
                        <Typography variant="caption" color="text.secondary">
                          Notes
                        </Typography>
                        <Typography variant="body2" sx={{ mt: 0.5, whiteSpace: 'pre-wrap', color: 'text.secondary' }}>
                          {selectedAccountDetails.notes}
                        </Typography>
                      </Box>
                    )}
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Status
                      </Typography>
                      <Chip 
                        label={selectedAccountDetails.is_active === false ? 'Inactive' : 'Active'}
                        size="small"
                        color={selectedAccountDetails.is_active === false ? 'error' : 'success'}
                        sx={{ mt: 0.5 }}
                      />
                    </Box>
                  </Stack>
                </CardContent>
              </Card>

              {/* Activity & Statistics */}
              {accountActivity[selectedAccountDetails.id] && (
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                      Activity & Statistics
                    </Typography>
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Total Transactions
                          </Typography>
                          <Typography variant="h5" sx={{ fontWeight: 600 }}>
                            {accountActivity[selectedAccountDetails.id].transactionCount || 0}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={6}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            This Month
                          </Typography>
                          <Typography variant="h5" sx={{ fontWeight: 600 }}>
                            {accountActivity[selectedAccountDetails.id].thisMonth || 0}
                          </Typography>
                        </Box>
                      </Grid>
                      {accountActivity[selectedAccountDetails.id].lastTransaction && (
                        <Grid item xs={12}>
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              Last Transaction
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 500 }}>
                              {new Date(accountActivity[selectedAccountDetails.id].lastTransaction).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                              })}
                            </Typography>
                          </Box>
                        </Grid>
                      )}
                    </Grid>
                  </CardContent>
                </Card>
              )}

              {/* Health Score */}
              {accountHealthAndInsights.healthScores[selectedAccountDetails.id] && (
                <Card sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                      Account Health
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>
                          {accountHealthAndInsights.healthScores[selectedAccountDetails.id].score}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          / 100
                        </Typography>
                      </Box>
                      <Chip
                        icon={
                          accountHealthAndInsights.healthScores[selectedAccountDetails.id].status === 'healthy' ? <CheckCircleIcon /> :
                          accountHealthAndInsights.healthScores[selectedAccountDetails.id].status === 'warning' ? <WarningIcon /> :
                          <ErrorIcon />
                        }
                        label={accountHealthAndInsights.healthScores[selectedAccountDetails.id].status.charAt(0).toUpperCase() + 
                               accountHealthAndInsights.healthScores[selectedAccountDetails.id].status.slice(1)}
                        color={
                          accountHealthAndInsights.healthScores[selectedAccountDetails.id].status === 'healthy' ? 'success' :
                          accountHealthAndInsights.healthScores[selectedAccountDetails.id].status === 'warning' ? 'warning' :
                          'error'
                        }
                        sx={{ height: 32 }}
                      />
                    </Box>
                  </CardContent>
                </Card>
              )}
            </Box>

            {/* Action Buttons */}
            <Box sx={{ p: 3, borderTop: '1px solid', borderColor: 'divider', bgcolor: 'background.paper' }}>
              <Stack direction="row" spacing={2}>
                <Button
                  variant="outlined"
                  startIcon={<EditIcon />}
                  onClick={() => {
                    handleEdit(selectedAccountDetails);
                    handleCloseDetailsPanel();
                  }}
                  fullWidth
                >
                  Edit Account
                </Button>
                <Button
                  variant="outlined"
                  color="error"
                  startIcon={<DeleteIcon />}
                  onClick={() => {
                    handleDelete(selectedAccountDetails);
                  }}
                  fullWidth
                >
                  Delete
                </Button>
              </Stack>
            </Box>
          </Box>
        )}
      </Drawer>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={Boolean(deleteConfirm)}
        onClose={() => setDeleteConfirm(null)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {deleteConfirm?.isCoreDefault && (
            <WarningIcon sx={{ color: 'warning.main', fontSize: 28 }} />
          )}
          <Typography variant="h6" component="span">
            {deleteConfirm?.isCoreDefault ? 'Warning: Core Account Deletion' : 'Confirm Deletion'}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {deleteConfirm?.type === 'single' ? (
            <>
              {deleteConfirm.isCoreDefault && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                    This is a core default account!
                  </Typography>
                  <Typography variant="body2">
                    Deleting "{deleteConfirm.accountName}" may affect your financial reports and transactions.
                    Consider deactivating it instead if you don't want to use it.
                  </Typography>
                </Alert>
              )}
              
              {(() => {
                const account = deleteConfirm.account;
                const balance = account?.balance || 0;
                const hasBalance = Math.abs(balance) > 0.01;
                
                if (hasBalance) {
                  return (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                        Cannot Delete Account with Balance
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        This account has a balance of <strong>{formatAmount(balance)}</strong>. 
                        Accounts with balances cannot be deleted to maintain accounting integrity.
                      </Typography>
                      <Typography variant="body2">
                        <strong>Recommendation:</strong> Deactivate the account instead to preserve transaction history 
                        and maintain accurate financial records.
                      </Typography>
                    </Alert>
                  );
                }
                return null;
              })()}
              
              <Typography variant="body1">
                Are you sure you want to delete <strong>"{deleteConfirm?.accountName}"</strong>?
              </Typography>
              <Typography variant="body2" color="error" sx={{ mt: 2, fontWeight: 600 }}>
                This action cannot be undone.
              </Typography>
            </>
          ) : (
            <>
              <Typography variant="body1">
                Are you sure you want to delete <strong>{deleteConfirm?.count} selected accounts</strong>?
              </Typography>
              <Typography variant="body2" color="error" sx={{ mt: 2, fontWeight: 600 }}>
                This action cannot be undone. Accounts with balances or transactions will not be deleted.
              </Typography>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirm(null)}>
            Cancel
          </Button>
          {deleteConfirm?.type === 'single' && (() => {
            const account = deleteConfirm.account;
            const balance = account?.balance || 0;
            const hasBalance = Math.abs(balance) > 0.01;
            
            if (hasBalance) {
              return (
                <Button
                  onClick={async () => {
                    try {
                      const account = deleteConfirm.account;
                      await apiClient.put(`/api/finance/double-entry/accounts/${account.id}`, { is_active: false });
                      const accountsResponse = await apiClient.get('/api/finance/double-entry/accounts');
                      const accountsArray = Array.isArray(accountsResponse) ? accountsResponse : [];
                      setApiAccounts(accountsArray);
                      setDeleteConfirm(null);
                      setSnackbar({
                        open: true,
                        message: `Account "${deleteConfirm.accountName}" deactivated successfully`,
                        severity: 'success'
                      });
                    } catch (error) {
                      setSnackbar({
                        open: true,
                        message: 'Failed to deactivate account: ' + (error.message || 'Unknown error'),
                        severity: 'error'
                      });
                    }
                  }}
                  variant="contained"
                  color="primary"
                  startIcon={<CancelIcon />}
                >
                  Deactivate Instead
                </Button>
              );
            }
            return null;
          })()}
          <Button
            onClick={confirmDelete}
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
            disabled={deleteConfirm?.type === 'single' && (() => {
              const account = deleteConfirm?.account;
              const balance = account?.balance || 0;
              return Math.abs(balance) > 0.01;
            })()}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
      >
        <Alert 
          severity={snackbar.severity}
          onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

const ChartOfAccounts = () => {
  return (
    <CoAProvider>
      <ChartOfAccountsContent />
    </CoAProvider>
  );
};

export default ChartOfAccounts;