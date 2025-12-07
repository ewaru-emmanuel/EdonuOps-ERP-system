import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Avatar, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Autocomplete, SpeedDial, SpeedDialAction, SpeedDialIcon,
  TablePagination, TableSortLabel, InputAdornment, OutlinedInput, FormHelperText, Collapse, List, ListItem, ListItemText, ListItemIcon,
  Switch, FormControlLabel, Divider
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, LocalTaxi, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb, Close
} from '@mui/icons-material';
import { useCoA } from '../context/CoAContext';
import { useCurrency } from '../../../components/GlobalCurrencySettings';
import apiClient from '../../../services/apiClient';
import PermissionGuard, { PermissionButton } from '../../../components/PermissionGuard';
import ManualJournalEntry from './ManualJournalEntry';

const SmartGeneralLedger = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [page, setPage] = useState(0);
  const { formatCurrency } = useCurrency();
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [orderBy, setOrderBy] = useState('entry_date');
  const [order, setOrder] = useState('desc');
  const [filters, setFilters] = useState({
    period: 'current',
    account: '',
    status: '',
    amount: ''
  });
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [showAiDialog, setShowAiDialog] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Local state for entries with localStorage persistence
  const [generalLedger, setGeneralLedger] = useState(() => {
    // Load from localStorage on component mount
    const saved = localStorage.getItem('edonuops_finance_entries');
    return saved ? JSON.parse(saved) : [];
  });
  
  // CRUD Dialog States
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState(null);
  const [editEntry, setEditEntry] = useState(null);
  const [manualJournalOpen, setManualJournalOpen] = useState(false);
  const [formData, setFormData] = useState({
    account_id: null,
    entry_date: '',
    description: '',
    debit_amount: '',
    credit_amount: '',
    reference: '',
    status: 'posted'
  });

  // Advanced features state
  const [isAdjustmentMode, setIsAdjustmentMode] = useState(false);
  const [userRole, setUserRole] = useState('admin'); // Default to admin/manager level for initial setup
  
  // Company-level configuration (loaded from AdminSettings)
  const [companySettings, setCompanySettings] = useState({
    defaultUserRole: 'admin',
    restrictionLevel: 'flexible', // 'strict', 'flexible', 'none'
    allowRoleOverride: true,
    requireApprovalForAdjustments: false,
    enableAuditTrail: true
  });

  // Load company settings from AdminSettings on component mount
  useEffect(() => {
    const loadCompanySettings = async () => {
      try {
        // In production, this would fetch from the same API that AdminSettings uses
        const savedSettings = localStorage.getItem('adminSettings_userPermissions');
        if (savedSettings) {
          const parsed = JSON.parse(savedSettings);
          setCompanySettings(parsed);
          setUserRole(parsed.defaultUserRole || 'admin');
        }
      } catch (error) {
        // Using default company settings - no action needed
      }
    };
    loadCompanySettings();
  }, []);

  // Real-time data hooks
  // Mock loading states
  const glLoading = false;
  const glError = null;
  
  // CRUD functions that use real API
  const create = async (data) => {
    try {
      console.log('Creating GL entry via API:', data);
      
      // Prepare data for API - ensure proper date format
      const apiData = {
        entry_date: data.entry_date || new Date().toISOString().split('T')[0],
        reference: data.reference || `JE-${Date.now()}`, // Generate unique reference if empty
        description: data.description || '',
        account_id: data.account_id,
        debit_amount: parseFloat(data.debit_amount) || 0,
        credit_amount: parseFloat(data.credit_amount) || 0,
        status: data.status || 'draft',
        journal_type: 'manual'
      };
      
      console.log('Sending API data:', apiData);
      const response = await apiClient.post('/api/finance/advanced/general-ledger', apiData);
      console.log('API response:', response);
      console.log('API response data:', response.data);
      
      // Check if response exists
      if (!response) {
        throw new Error('No response received from server');
      }
      
      // Find the account name from chart of accounts
      const account = chartOfAccounts?.find(acc => acc.id === data.account_id);
      const account_name = account?.name || 'Unknown Account';
      
      // Handle different response structures - the API returns the created entry directly
      const responseEntry = response.data || response;
      
      // Create new entry with proper structure
      const timestamp = Date.now();
      const now = new Date().toISOString();
      
      const newEntry = { 
        id: responseEntry?.id || timestamp, // Fallback to timestamp if no ID
        entry_date: apiData.entry_date,
        reference: apiData.reference,
        description: apiData.description,
        status: apiData.status,
        debit_amount: apiData.total_debit,
        credit_amount: apiData.total_credit,
        account_id: data.account_id,
        account_name,
        created_at: responseEntry?.created_at || now,
        updated_at: responseEntry?.created_at || now
      };
      
      setGeneralLedger(prev => [...prev, newEntry]);
      return newEntry;
    } catch (error) {
      console.error('Error creating journal entry:', error);
      // Provide more specific error message
      if (error.message.includes('500')) {
        throw new Error('Server error: Unable to create journal entry. Please try again.');
      } else if (error.message.includes('400')) {
        throw new Error('Invalid data: Please check your entry details.');
      } else {
        throw new Error(`Failed to create journal entry: ${error.message}`);
      }
    }
  };
  
  const update = async (id, data) => {
    try {
      console.log('Updating GL entry via API:', id, data);
      
      // Extract the actual entry ID from composite ID (format: "entryId-lineId")
      const entryId = id.includes('-') ? id.split('-')[0] : id;
      
      // Find the current entry to get account_id if not provided
      const currentEntry = generalLedger.find(entry => entry.id === id);
      if (!currentEntry) {
        throw new Error('Entry not found for update');
      }
      
      // Prepare data for API (matching backend expectations)
      const apiData = {
        entry_date: data.entry_date || currentEntry.entry_date || new Date().toISOString().split('T')[0],
        reference: data.reference || currentEntry.reference || `JE-${Date.now()}`,
        description: data.description || currentEntry.description || '',
        account_id: data.account_id || currentEntry.account_id,
        debit_amount: parseFloat(data.debit_amount) || 0,
        credit_amount: parseFloat(data.credit_amount) || 0,
        status: data.status || currentEntry.status || 'draft'
      };
      
      console.log('Sending update API data:', apiData);
      const response = await apiClient.put(`/api/finance/advanced/general-ledger/${entryId}`, apiData);
      console.log('Update API response:', response);
      console.log('Update API response data:', response.data);
      
      // Find the account name if account_id is being updated
      let account_name = data.account_name;
      if (data.account_id && !account_name) {
        const account = chartOfAccounts?.find(acc => acc.id === data.account_id);
        account_name = account?.name || 'Unknown Account';
      }
      
      // Update local state with the updated data
      const now = new Date().toISOString();
      setGeneralLedger(prev => prev.map(entry => 
        entry.id === id 
          ? { 
              ...entry, 
              entry_date: apiData.entry_date,
              reference: apiData.reference,
              description: apiData.description,
              status: apiData.status,
              debit_amount: apiData.debit_amount,
              credit_amount: apiData.credit_amount,
              account_id: apiData.account_id,
              account_name: account_name || currentEntry.account_name, 
              updated_at: now
            }
          : entry
      ));
      return { id, ...apiData };
    } catch (error) {
      console.error('Error updating journal entry:', error);
      throw error;
    }
  };
  
  const remove = async (id) => {
    try {
      console.log('🗑️ Deleting GL entry via API:', id);
      // Extract entry_id from the composite ID (format: "entryId-lineId")
      // Convert to string first to handle both number and string IDs
      const entryIdStr = String(id);
      const entryId = entryIdStr.includes('-') ? entryIdStr.split('-')[0] : entryIdStr;
      console.log('🗑️ Processed entry ID for deletion:', entryId);
      
      const response = await apiClient.delete(`/api/finance/advanced/general-ledger/${entryId}`);
      console.log('Delete API response:', response);
      
      // Remove all lines for this entry from local state
      setGeneralLedger(prev => prev.filter(entry => entry.entry_id !== entryId));
      return true;
    } catch (error) {
      console.error('Error deleting journal entry:', error);
      throw error;
    }
  };
  
  const refresh = async () => { 
    try {
      console.log('🔄 Loading GL entries from API...');
      // Use double-entry journal entries endpoint which is working
      const response = await apiClient.get('/api/finance/double-entry/journal-entries');
      console.log('📡 API response for loading entries:', response);
      
      // Check if response and data exist
      if (!response) {
        console.warn('No response received from API');
        setGeneralLedger([]);
        return;
      }
      
      // Handle different response structures
      let entriesArray = [];
      if (response.data) {
        if (Array.isArray(response.data)) {
          entriesArray = response.data;
        } else if (Array.isArray(response)) {
          entriesArray = response;
        }
      } else if (Array.isArray(response)) {
        entriesArray = response;
      }
      
      // Transform journal entries with lines into individual GL entries
      // Each journal line becomes a GL entry
      const dataArray = [];
      entriesArray.forEach(entry => {
        if (entry.lines && Array.isArray(entry.lines)) {
          entry.lines.forEach(line => {
            dataArray.push({
              id: line.id || `${entry.id}-${line.account_id}`,
              journal_header_id: entry.id,
              entry_date: entry.date || entry.doc_date,
              reference: entry.reference || '',
              description: line.description || entry.description || '',
              account_id: line.account_id,
              account_name: line.account_name || '',
              debit_amount: line.debit_amount || 0,
              credit_amount: line.credit_amount || 0,
              balance: (line.debit_amount || 0) - (line.credit_amount || 0),
              status: entry.status || 'posted',
              journal_type: 'manual',
              fiscal_period: null,
              created_at: entry.created_at || new Date().toISOString()
            });
          });
        }
      });
      
      console.log('📋 Transformed GL entries:', dataArray.length);
      const entries = dataArray.map(entry => ({
        id: entry.id,
        entry_id: entry.id,
        line_id: null,
        entry_date: entry.entry_date,
        reference: entry.reference,
        description: entry.description,
        status: entry.status,
        debit_amount: entry.debit_amount || 0,
        credit_amount: entry.credit_amount || 0,
        account_id: entry.account_id,
        account_name: entry.account_name || `Account ${entry.account_id}`,
        account_code: entry.account_code || 'N/A',
        created_at: entry.created_at,
        updated_at: entry.updated_at,
        payment_method: entry.payment_method
      }));
      
      console.log('✅ Processed entries for display:', entries);
      console.log('📊 Processed entries count:', entries.length);
      console.log('🎯 Setting generalLedger state with', entries.length, 'entries');
      setGeneralLedger(entries);
    } catch (error) {
      console.error('Error loading journal entries:', error);
      setSnackbar({ open: true, message: 'Error loading entries: ' + error.message, severity: 'error' });
      // Set empty array on error to prevent crashes
      setGeneralLedger([]);
    }
  };

  // Function to clear all entries (useful for testing)
  const clearAllEntries = () => {
    setGeneralLedger([]);
    setSnackbar({ open: true, message: 'All entries cleared!', severity: 'info' });
  };

  // Function to export entries to JSON
  const exportEntries = () => {
    const dataStr = JSON.stringify(generalLedger, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `finance_entries_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };
  
  // Load data from API on component mount
  useEffect(() => {
    refresh();
  }, []);

  // Save to localStorage whenever generalLedger changes (as backup)
  useEffect(() => {
    localStorage.setItem('edonuops_finance_entries', JSON.stringify(generalLedger));
  }, [generalLedger]);

  // Debug: Log GL data
  useEffect(() => {
    console.log('GL Data Debug:', {
      generalLedger,
      glLoading,
      glError,
      dataLength: generalLedger?.length || 0
    });
  }, [generalLedger, glLoading, glError]);

  
  // Chart of Accounts context
  const { accounts: chartOfAccounts, loading: coaLoading } = useCoA();

  // Calculate real-time trial balance
  const trialBalance = useMemo(() => {
    if (!generalLedger) return { debits: 0, credits: 0, balance: 0 };
    
    const debits = generalLedger.reduce((sum, entry) => sum + (entry.debit_amount || 0), 0);
    const credits = generalLedger.reduce((sum, entry) => sum + (entry.credit_amount || 0), 0);
    const balance = debits - credits;
    
    return { debits, credits, balance };
  }, [generalLedger]);

  // Filter and sort data
  const filteredData = useMemo(() => {
    console.log('🔍 Filtering data - generalLedger:', generalLedger);
    console.log('🔍 Current filters:', filters);
    
    if (!generalLedger) {
      console.log('❌ No generalLedger data available');
      return [];
    }
    
    let filtered = [...generalLedger];
    console.log('📊 Starting with', filtered.length, 'entries');
    
    // Apply filters
    if (filters.period !== 'all') {
      console.log('🔍 Applying period filter:', filters.period);
      const currentDate = new Date();
      const currentMonth = currentDate.getMonth();
      const currentYear = currentDate.getFullYear();
      
      filtered = filtered.filter(entry => {
        const entryDate = new Date(entry.entry_date);
        const matches = entryDate.getMonth() === currentMonth && entryDate.getFullYear() === currentYear;
        return matches;
      });
      console.log('📊 After period filter:', filtered.length, 'entries');
    }
    
    if (filters.account) {
      console.log('🔍 Applying account filter:', filters.account);
      filtered = filtered.filter(entry => 
        entry.account_name?.toLowerCase().includes(filters.account.toLowerCase())
      );
      console.log('📊 After account filter:', filtered.length, 'entries');
    }
    
    if (filters.status) {
      console.log('🔍 Applying status filter:', filters.status);
      filtered = filtered.filter(entry => entry.status === filters.status);
      console.log('📊 After status filter:', filtered.length, 'entries');
    }
    
    if (filters.amount) {
      const amount = parseFloat(filters.amount);
      filtered = filtered.filter(entry => 
        (entry.debit_amount || 0) >= amount || (entry.credit_amount || 0) >= amount
      );
    }
    
    // Sort data
    filtered.sort((a, b) => {
      const aValue = a[orderBy];
      const bValue = b[orderBy];
      
      if (order === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    return filtered;
  }, [generalLedger, filters, orderBy, order]);

  // Pagination
  const paginatedData = useMemo(() => {
    const startIndex = page * rowsPerPage;
    return filteredData.slice(startIndex, startIndex + rowsPerPage);
  }, [filteredData, page, rowsPerPage]);

  // AI Suggestions
  const generateAiSuggestions = useCallback(() => {
    const suggestions = [];
    
    // Analyze patterns and suggest optimizations
    if (trialBalance.balance !== 0) {
      suggestions.push({
        type: 'warning',
        icon: <Warning />,
        title: 'Unbalanced Entries',
        message: `Trial balance shows ${Math.abs(trialBalance.balance).toFixed(2)} difference. Review recent entries.`,
        action: 'Review Entries'
      });
    }
    
    // Suggest common journal entries based on patterns
    const commonAccounts = chartOfAccounts?.slice(0, 5) || [];
    suggestions.push({
      type: 'info',
      icon: <Lightbulb />,
      title: 'Common Entries',
      message: `Based on your patterns, you might want to record: ${commonAccounts.map(acc => acc.name).join(', ')}`,
      action: 'Quick Entry'
    });
    
    setAiSuggestions(suggestions);
  }, [trialBalance, chartOfAccounts]);

  useEffect(() => {
    generateAiSuggestions();
  }, [generateAiSuggestions]);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.account_id) {
      setSnackbar({ open: true, message: 'Please select an account', severity: 'error' });
      return;
    }
    
    if (!formData.entry_date) {
      setSnackbar({ open: true, message: 'Please select an entry date', severity: 'error' });
      return;
    }
    
    if (!formData.description) {
      setSnackbar({ open: true, message: 'Please enter a description', severity: 'error' });
      return;
    }
    
    // Validate double-entry bookkeeping
    const debitAmount = parseFloat(formData.debit_amount) || 0;
    const creditAmount = parseFloat(formData.credit_amount) || 0;
    
    if (debitAmount > 0 && creditAmount > 0) {
      setSnackbar({ open: true, message: 'Cannot have both debit and credit amounts', severity: 'error' });
      return;
    }
    
    if (debitAmount === 0 && creditAmount === 0) {
      setSnackbar({ open: true, message: 'Must have either debit or credit amount', severity: 'error' });
      return;
    }
    
    try {
      // Ensure account_id is a number
      const submitData = {
        ...formData,
        account_id: parseInt(formData.account_id) || null
      };
      
      
      if (editDialogOpen && selectedEntry) {
        await update(selectedEntry.id, submitData);
        setSnackbar({ open: true, message: 'Journal entry updated successfully!', severity: 'success' });
        // Refresh the data after successful update
        refresh();
      } else {
        await create(submitData);
        setSnackbar({ open: true, message: 'Journal entry created successfully!', severity: 'success' });
        // Refresh the data after successful creation
        refresh();
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Form submission error:', error); // Debug log
      setSnackbar({ open: true, message: 'Error saving journal entry: ' + error.message, severity: 'error' });
    }
  };


  // Handle delete
  const handleDelete = async (id) => {
    console.log('🗑️ Delete button clicked for entry ID:', id);
    if (window.confirm('Are you sure you want to delete this journal entry?')) {
      try {
        console.log('🗑️ User confirmed deletion, proceeding...');
        await remove(id);
        console.log('🗑️ Entry deleted successfully, refreshing table...');
        refresh(); // Refresh the table after deletion
        setSnackbar({ open: true, message: 'Journal entry deleted successfully!', severity: 'success' });
      } catch (error) {
        console.error('🗑️ Error deleting entry:', error);
        setSnackbar({ open: true, message: 'Error deleting journal entry: ' + error.message, severity: 'error' });
      }
    } else {
      console.log('🗑️ User cancelled deletion');
    }
  };

  // Handle dialog close
  const handleCloseDialog = () => {
    setAddDialogOpen(false);
    setEditDialogOpen(false);
    setSelectedEntry(null);
    setFormData({
      account_id: null,
      entry_date: '',
      description: '',
      debit_amount: '',
      credit_amount: '',
      reference: '',
      status: 'posted'
    });
  };

  // Smart account behavior logic with company-level configuration support
  const getAccountBehavior = (accountType, isAdjustmentMode = false, userRole = 'user') => {
    // Check company-level restrictions first
    if (companySettings.restrictionLevel === 'none') {
      // Company has disabled all restrictions - everyone gets full access
      return {
        debitEnabled: true,
        creditEnabled: true,
        debitLabel: 'Debit',
        creditLabel: 'Credit',
        normalSide: 'debit',
        helpText: 'Company policy: No field restrictions',
        color: '#4caf50',
        icon: '🏢'
      };
    }
    
    // Advanced users (accountants/admins) can override smart restrictions
    const canOverride = userRole === 'accountant' || userRole === 'admin' || userRole === 'manager';
    
    // In adjustment mode or for advanced users, allow both fields
    if (isAdjustmentMode || (canOverride && companySettings.allowRoleOverride)) {
      switch(accountType?.toLowerCase()) {
        case 'revenue':
          return {
            debitEnabled: true,
            creditEnabled: true,
            debitLabel: canOverride ? 'Refund/Reversal (Override)' : 'Refund/Reversal',
            creditLabel: 'Revenue Earned',
            normalSide: 'credit',
            helpText: canOverride ? 'Advanced user: Both fields enabled' : 'Adjustment mode: Both fields enabled',
            color: '#388e3c',
            icon: '💵'
          };
        case 'expense':
          return {
            debitEnabled: true,
            creditEnabled: true,
            debitLabel: 'Expense Incurred',
            creditLabel: canOverride ? 'Expense Reversal (Override)' : 'Expense Reversal',
            normalSide: 'debit',
            helpText: canOverride ? 'Advanced user: Both fields enabled' : 'Adjustment mode: Both fields enabled',
            color: '#f57c00',
            icon: '💸'
          };
      }
    }
    
    // Normal smart behavior for regular users
    const normalizedType = accountType?.toLowerCase().trim();
    
    switch(normalizedType) {
      case 'asset':
      case 'assets':
      case 'current asset':
      case 'fixed asset':
      case 'intangible asset':
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Increase Asset',
          creditLabel: 'Decrease Asset',
          normalSide: 'debit',
          helpText: 'Assets increase with debits, decrease with credits',
          color: '#1976d2',
          icon: '💰'
        };
        
      case 'liability':
      case 'liabilities':
      case 'current liability':
      case 'long-term liability':
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Pay/Reduce Liability',
          creditLabel: 'Incur/Increase Liability',
          normalSide: 'credit',
          helpText: 'Liabilities increase with credits, decrease with debits',
          color: '#d32f2f',
          icon: '💳'
        };
        
      case 'equity':
      case 'owner equity':
      case 'shareholders equity':
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Decrease Equity',
          creditLabel: 'Increase Equity',
          normalSide: 'credit',
          helpText: 'Equity increases with credits, decreases with debits',
          color: '#9c27b0',
          icon: '👑'
        };
        
      case 'revenue':
      case 'income':
      case 'sales revenue':
      case 'service revenue':
      case 'operating revenue':
      case 'other income':
        return {
          debitEnabled: false,
          creditEnabled: true,
          debitLabel: 'Refund/Reversal',
          creditLabel: 'Revenue Earned',
          normalSide: 'credit',
          helpText: 'Revenue accounts normally have credit balances (money earned). Use Adjustment Mode for reversals.',
          color: '#388e3c',
          icon: '💵'
        };
        
      case 'expense':
      case 'expenses':
      case 'cost of sales':
      case 'operating expense':
      case 'cost of goods sold':
        return {
          debitEnabled: true,
          creditEnabled: false,
          debitLabel: 'Expense Incurred',
          creditLabel: 'Expense Reversal',
          normalSide: 'debit',
          helpText: 'Expense accounts normally have debit balances (money spent). Use Adjustment Mode for reversals.',
          color: '#f57c00',
          icon: '💸'
        };
        
      default:
        return {
          debitEnabled: true,
          creditEnabled: true,
          debitLabel: 'Debit',
          creditLabel: 'Credit',
          normalSide: 'debit',
          helpText: 'Both fields available for this account type',
          color: '#757575',
          icon: '💼'
        };
    }
  };

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => {
      const newData = { ...prev, [field]: value };
      
      // Smart field behavior when account changes
      if (field === 'account_id') {
        const selectedAccount = chartOfAccounts?.find(acc => acc.id == value);
        if (selectedAccount) {
          const behavior = getAccountBehavior(
            selectedAccount.category || selectedAccount.account_type || selectedAccount.type,
            isAdjustmentMode,
            userRole
          );
          
          // Clear disabled fields
          if (!behavior.debitEnabled) {
            newData.debit_amount = '';
          }
          if (!behavior.creditEnabled) {
            newData.credit_amount = '';
          }
        }
      }
      
      // Mutual exclusion: clear opposite field when entering amount
      if (field === 'debit_amount' && value) {
        newData.credit_amount = '';
      } else if (field === 'credit_amount' && value) {
        newData.debit_amount = '';
      }
      
      return newData;
    });
  };


  const handleSort = (property) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const handleExport = () => {
    // Export functionality
    const csvContent = "data:text/csv;charset=utf-8," + 
      "Date,Reference,Account,Description,Debit,Credit,Status\n" +
      filteredData.map(row => 
        `${row.entry_date},${row.reference},${row.account_name},${row.description},${row.debit_amount},${row.credit_amount},${row.status}`
      ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "general_ledger.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleAiSuggestion = (suggestion) => {
    setShowAiDialog(false);
  };

  return (
    <Box sx={{ width: '100%', maxWidth: '100%', boxSizing: 'border-box' }}>
      {/* Header with Smart Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>
          Smart General Ledger
        </Typography>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<AutoAwesome />}
            onClick={() => setShowAiDialog(true)}
          >
            AI Insights
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={handleExport}
          >
            Export GL
          </Button>
          <PermissionButton
            permission="finance.journal.create"
            variant="contained"
            startIcon={<Add />}
            onClick={() => setManualJournalOpen(true)}
          >
            Add Entry
          </PermissionButton>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={exportEntries}
            sx={{ ml: 1 }}
          >
            Export
          </Button>
          <Button
            variant="outlined"
            color="warning"
            onClick={clearAllEntries}
            sx={{ ml: 1 }}
          >
            Clear All
          </Button>
        </Box>
      </Box>


      {/* Real-time Trial Balance */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Real-time Trial Balance
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h4" color="primary.main" gutterBottom>
{formatCurrency(trialBalance.debits)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Debits
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h4" color="secondary.main" gutterBottom>
{formatCurrency(trialBalance.credits)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total Credits
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box textAlign="center">
                <Typography variant="h4" color={trialBalance.balance === 0 ? 'success.main' : 'error.main'} gutterBottom>
{formatCurrency(Math.abs(trialBalance.balance))}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {trialBalance.balance === 0 ? 'Balanced' : 'Difference'}
                </Typography>
                {trialBalance.balance !== 0 && (
                  <Chip 
                    label="Unbalanced" 
                    color="error" 
                    size="small" 
                    sx={{ mt: 1 }}
                  />
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Smart Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Smart Filters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Period</InputLabel>
                <Select
                  value={filters.period}
                  onChange={(e) => setFilters({ ...filters, period: e.target.value })}
                >
                  <MenuItem value="all">All Periods</MenuItem>
                  <MenuItem value="current">Current Month</MenuItem>
                  <MenuItem value="previous">Previous Month</MenuItem>
                  <MenuItem value="quarter">This Quarter</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Autocomplete
                options={chartOfAccounts || []}
                getOptionLabel={(option) => option.name}
                value={filters.account ? chartOfAccounts?.find(acc => acc.name === filters.account) || null : null}
                onChange={(e, value) => setFilters({ ...filters, account: value?.name || '' })}
                renderInput={(params) => (
                  <TextField {...params} label="Account" size="small" />
                )}
                size="small"
                isOptionEqualToValue={(option, value) => option.id === value?.id}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Status</InputLabel>
                <Select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                >
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="draft">Draft</MenuItem>
                  <MenuItem value="posted">Posted</MenuItem>
                  <MenuItem value="void">Void</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                label="Min Amount"
                type="number"
                value={filters.amount}
                onChange={(e) => setFilters({ ...filters, amount: e.target.value })}
                size="small"
                fullWidth
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* General Ledger Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Journal Entries ({filteredData.length} entries)
            </Typography>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => {
                  refresh();
                }}
                disabled={glLoading || coaLoading}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          {glLoading && <LinearProgress sx={{ mb: 2 }} />}

          {glError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {glError}
            </Alert>
          )}

          <TableContainer component={Paper} sx={{ width: '100%', overflowX: 'auto' }}>
            <Table sx={{ minWidth: 900 }} stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'entry_date'}
                      direction={orderBy === 'entry_date' ? order : 'asc'}
                      onClick={() => handleSort('entry_date')}
                    >
                      Date
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>
                    <TableSortLabel
                      active={orderBy === 'reference'}
                      direction={orderBy === 'reference' ? order : 'asc'}
                      onClick={() => handleSort('reference')}
                    >
                      Reference
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Account</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">
                    <TableSortLabel
                      active={orderBy === 'debit_amount'}
                      direction={orderBy === 'debit_amount' ? order : 'asc'}
                      onClick={() => handleSort('debit_amount')}
                    >
                      Debit
                    </TableSortLabel>
                  </TableCell>
                  <TableCell align="right">
                    <TableSortLabel
                      active={orderBy === 'credit_amount'}
                      direction={orderBy === 'credit_amount' ? order : 'asc'}
                      onClick={() => handleSort('credit_amount')}
                    >
                      Credit
                    </TableSortLabel>
                  </TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedData.map((entry, index) => (
                  <TableRow 
                    key={entry.id || `entry-${index}`} 
                    hover 
                    onClick={() => setSelectedEntry(entry)}
                    sx={{ cursor: 'pointer' }}
                  >
                    <TableCell>
                      {entry.entry_date ? new Date(entry.entry_date).toLocaleDateString() : ''}
                    </TableCell>
                    <TableCell>
                      {entry.reference || ''}
                    </TableCell>
                    <TableCell>
                      {entry.account_name || ''}
                    </TableCell>
                    <TableCell>
                      {entry.description || ''}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(entry.debit_amount || 0)}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(entry.credit_amount || 0)}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={entry.status || 'draft'}
                        color={entry.status === 'posted' ? 'success' : entry.status === 'void' ? 'error' : 'warning'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <PermissionGuard permission="finance.journal.update" showFallback={false}>
                          <Tooltip title="Edit">
                            <IconButton onClick={(e) => {
                              e.stopPropagation(); // Prevent row click
                              console.log('✏️ Edit button clicked for entry:', entry);
                              console.log('✏️ Entry ID:', entry.id);
                              console.log('✏️ Entry data:', entry);
                              // For editing, we need to get the full journal entry, not just the line
                              // The entry object already contains the line data, so we can use it directly
                              setEditEntry(entry);
                              setManualJournalOpen(true);
                              console.log('✏️ Edit entry set, form should open...');
                            }} size="small">
                              <Edit />
                            </IconButton>
                          </Tooltip>
                        </PermissionGuard>
                        <PermissionGuard permission="finance.journal.delete" showFallback={false}>
                          <Tooltip title="Delete">
                            <IconButton color="error" size="small" onClick={(e) => {
                              e.stopPropagation(); // Prevent row click
                              handleDelete(entry.id);
                            }}>
                              <Delete />
                            </IconButton>
                          </Tooltip>
                        </PermissionGuard>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Pagination */}
          <TablePagination
            component="div"
            count={filteredData.length}
            page={page}
            onPageChange={(e, newPage) => setPage(newPage)}
            rowsPerPage={rowsPerPage}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            rowsPerPageOptions={[5, 10, 25, 50]}
          />
        </CardContent>
      </Card>

      {/* AI Insights Dialog */}
      <Dialog
        open={showAiDialog}
        onClose={() => setShowAiDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar sx={{ bgcolor: 'primary.main' }}>
              <Psychology />
            </Avatar>
            <Typography variant="h6">AI-Powered Insights</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Intelligent analysis of your General Ledger patterns:
          </Typography>
          
          <List>
            {aiSuggestions.map((suggestion, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {suggestion.icon}
                </ListItemIcon>
                <ListItemText
                  primary={suggestion.title}
                  secondary={suggestion.message}
                  primaryTypographyProps={{ fontWeight: 'bold' }}
                />
                <Button
                  variant="outlined"
                  size="small"
                  onClick={() => handleAiSuggestion(suggestion)}
                >
                  {suggestion.action}
                </Button>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAiDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Add/Edit Journal Entry Dialog */}
      <Dialog 
        open={addDialogOpen || editDialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editDialogOpen ? 'Edit Journal Entry' : 'Add New Journal Entry'}
        </DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            {/* Company Configuration Status */}
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="body2">
                🏢 <strong>Company Mode:</strong> {companySettings.restrictionLevel === 'none' ? 'No Restrictions (Full Access)' : 
                  userRole === 'admin' || userRole === 'manager' ? 'Manager Level - Full Access Enabled' : 'Smart Entry Mode Active'}
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', mt: 0.5, opacity: 0.8 }}>
                Default Role: {companySettings.defaultUserRole} | Restriction Level: {companySettings.restrictionLevel} | 
                Role Override: {companySettings.allowRoleOverride ? 'Allowed' : 'Disabled'}
              </Typography>
            </Alert>
            
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={isAdjustmentMode}
                      onChange={(e) => setIsAdjustmentMode(e.target.checked)}
                      color="warning"
                    />
                  }
                  label={
                    <Typography variant="body2">
                      🔧 Adjustment Mode {isAdjustmentMode ? '(ON - Both fields enabled)' : '(OFF - Smart restrictions)'}
                    </Typography>
                  }
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl size="small" sx={{ minWidth: 120 }}>
                  <InputLabel>User Role</InputLabel>
                  <Select
                    value={userRole}
                    onChange={(e) => setUserRole(e.target.value)}
                    label="User Role"
                    disabled={!companySettings.allowRoleOverride}
                  >
                    <MenuItem value="user">👤 Regular User</MenuItem>
                    <MenuItem value="accountant">👨‍💼 Accountant</MenuItem>
                    <MenuItem value="admin">👑 Admin</MenuItem>
                    <MenuItem value="manager">🎯 Manager/Owner</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
            
            <Divider sx={{ mb: 2 }} />
            
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Account</InputLabel>
                  <Select
                    value={formData.account_id || ''}
                    onChange={(e) => handleInputChange('account_id', e.target.value || null)}
                    label="Account"
                    required
                  >
                    {chartOfAccounts
                      ?.filter(account => account.is_active !== false)
                      .map((account) => (
                      <MenuItem key={account.id} value={account.id}>
                        {account.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Entry Date"
                  type="date"
                  value={formData.entry_date}
                  onChange={(e) => handleInputChange('entry_date', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputLabelProps={{ shrink: true }}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  fullWidth
                  margin="normal"
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Reference"
                  value={formData.reference}
                  onChange={(e) => handleInputChange('reference', e.target.value)}
                  fullWidth
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={formData.status}
                    onChange={(e) => handleInputChange('status', e.target.value)}
                    label="Status"
                  >
                    <MenuItem value="draft">Draft</MenuItem>
                    <MenuItem value="posted">Posted</MenuItem>
                    <MenuItem value="void">Void</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                {(() => {
                  const selectedAccount = chartOfAccounts?.find(acc => acc.id == formData.account_id);
                  const behavior = getAccountBehavior(
                    selectedAccount?.category || selectedAccount?.account_type || selectedAccount?.type,
                    isAdjustmentMode,
                    userRole
                  );
                  
                  return (
                    <TextField
                      label={behavior.debitLabel}
                      type="number"
                      value={formData.debit_amount}
                      onChange={(e) => handleInputChange('debit_amount', e.target.value)}
                      disabled={!behavior.debitEnabled}
                      fullWidth
                      margin="normal"
                      placeholder={behavior.debitEnabled ? 'Enter amount' : 'Not applicable for this account type'}
                      helperText={!behavior.debitEnabled ? `${behavior.icon} ${behavior.helpText}` : ''}
                      sx={{
                        '& .MuiInputBase-input.Mui-disabled': {
                          backgroundColor: '#f5f5f5',
                          color: '#999',
                          WebkitTextFillColor: '#999'
                        }
                      }}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">$</InputAdornment>,
                      }}
                    />
                  );
                })()}
              </Grid>
              <Grid item xs={12} sm={6}>
                {(() => {
                  const selectedAccount = chartOfAccounts?.find(acc => acc.id == formData.account_id);
                  const behavior = getAccountBehavior(
                    selectedAccount?.category || selectedAccount?.account_type || selectedAccount?.type,
                    isAdjustmentMode,
                    userRole
                  );
                  
                  return (
                    <TextField
                      label={behavior.creditLabel}
                      type="number"
                      value={formData.credit_amount}
                      onChange={(e) => handleInputChange('credit_amount', e.target.value)}
                      disabled={!behavior.creditEnabled}
                      fullWidth
                      margin="normal"
                      placeholder={behavior.creditEnabled ? 'Enter amount' : 'Not applicable for this account type'}
                      helperText={!behavior.creditEnabled ? `${behavior.icon} ${behavior.helpText}` : ''}
                      sx={{
                        '& .MuiInputBase-input.Mui-disabled': {
                          backgroundColor: '#f5f5f5',
                          color: '#999',
                          WebkitTextFillColor: '#999'
                        }
                      }}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">$</InputAdornment>,
                      }}
                    />
                  );
                })()}
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleSubmit}>
            {editDialogOpen ? 'Update' : 'Create'} Entry
          </Button>
        </DialogActions>
      </Dialog>

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

      {/* Floating Action Button */}
      <SpeedDial
        ariaLabel="General Ledger Actions"
        sx={{ 
          position: 'absolute', 
          bottom: 16, 
          right: 16,
          zIndex: 1000
        }}
        icon={<SpeedDialIcon />}
      >
        <SpeedDialAction
          icon={<Add />}
          tooltipTitle="New Entry"
          onClick={() => setAddDialogOpen(true)}
        />
        <SpeedDialAction
          icon={<AutoAwesome />}
          tooltipTitle="AI Insights"
          onClick={() => setShowAiDialog(true)}
        />
        <SpeedDialAction
          icon={<Download />}
          tooltipTitle="Export"
          onClick={handleExport}
        />
      </SpeedDial>

      {/* Manual Journal Entry Dialog */}
      <ManualJournalEntry
        open={manualJournalOpen}
        onClose={() => {
          setManualJournalOpen(false);
          setEditEntry(null); // Clear edit entry when closing
        }}
        onSuccess={(response) => {
          console.log('🎉 Manual journal entry success callback triggered!');
          console.log('🎉 Response:', response);
          setManualJournalOpen(false);
          setEditEntry(null); // Clear edit entry on success
          console.log('🔄 Refreshing GL data...');
          refresh(); // Refresh the general ledger data
        }}
        editEntry={editEntry}
      />

      {/* Entry Details Dialog */}
      <Dialog
        open={!!selectedEntry}
        onClose={() => setSelectedEntry(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Journal Entry Details
          <IconButton
            onClick={() => setSelectedEntry(null)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedEntry && (
            <Box sx={{ mt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Reference</Typography>
                  <Typography variant="body1">{selectedEntry.reference}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Date</Typography>
                  <Typography variant="body1">
                    {selectedEntry.entry_date ? new Date(selectedEntry.entry_date).toLocaleDateString() : ''}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">Description</Typography>
                  <Typography variant="body1">{selectedEntry.description}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Status</Typography>
                  <Chip 
                    label={selectedEntry.status} 
                    color={selectedEntry.status === 'posted' ? 'success' : 'default'}
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Account</Typography>
                  <Typography variant="body1">{selectedEntry.account_name || 'Database Entry'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Debit Amount</Typography>
                  <Typography variant="body1" color="success.main">
                    {formatCurrency(selectedEntry.debit_amount || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Credit Amount</Typography>
                  <Typography variant="body1" color="error.main">
                    {formatCurrency(selectedEntry.credit_amount || 0)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Created</Typography>
                  <Typography variant="body1">
                    {selectedEntry.created_at ? new Date(selectedEntry.created_at).toLocaleString() : ''}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">Updated</Typography>
                  <Typography variant="body1">
                    {selectedEntry.updated_at ? new Date(selectedEntry.updated_at).toLocaleString() : ''}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedEntry(null)}>Close</Button>
          <PermissionGuard permission="finance.journal.update" showFallback={false}>
            <Button 
              variant="contained" 
              onClick={() => {
                // For editing, we need to get the full journal entry, not just the line
                // The selectedEntry object already contains the line data, so we can use it directly
                setEditEntry(selectedEntry);
                setSelectedEntry(null);
                setManualJournalOpen(true);
              }}
            >
              Edit Entry
            </Button>
          </PermissionGuard>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SmartGeneralLedger;