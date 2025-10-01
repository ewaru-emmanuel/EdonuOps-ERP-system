import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { useTenantApi } from '../../../hooks/useTenantApi';
import { useTenant } from '../../../contexts/TenantContext';

const CoAContext = createContext();

// Template account definitions
const getTemplateAccounts = (templateId) => {
  const templates = {
    retail: [
      // Assets
      { id: 1, name: 'Cash & Bank', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 2, name: 'Business Checking', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 3, name: 'Inventory', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 4, name: 'Accounts Receivable', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 5, name: 'Equipment', category: 'asset', type: 'Fixed Asset', balance: 0 },
      { id: 6, name: 'Store Fixtures', category: 'asset', type: 'Fixed Asset', balance: 0 },
      
      // Liabilities
      { id: 7, name: 'Accounts Payable', category: 'liability', type: 'Current Liability', balance: 0 },
      { id: 8, name: 'Credit Cards', category: 'liability', type: 'Current Liability', balance: 0 },
      { id: 9, name: 'Loans Payable', category: 'liability', type: 'Long-term Liability', balance: 0 },
      
      // Equity
      { id: 10, name: 'Owner\'s Investment', category: 'equity', type: 'Owner Equity', balance: 0 },
      { id: 11, name: 'Retained Earnings', category: 'equity', type: 'Owner Equity', balance: 0 },
      
      // Revenue
      { id: 12, name: 'Sales Revenue', category: 'revenue', type: 'Income', balance: 0 },
      { id: 13, name: 'Service Revenue', category: 'revenue', type: 'Income', balance: 0 },
      
      // Expenses
      { id: 14, name: 'Cost of Goods Sold', category: 'expense', type: 'Cost of Sales', balance: 0 },
      { id: 15, name: 'Rent Expense', category: 'expense', type: 'Operating Expense', balance: 0 },
      { id: 16, name: 'Utilities', category: 'expense', type: 'Operating Expense', balance: 0 },
      { id: 17, name: 'Marketing', category: 'expense', type: 'Operating Expense', balance: 0 },
      { id: 18, name: 'Office Supplies', category: 'expense', type: 'Operating Expense', balance: 0 }
    ],
    
    services: [
      // Assets
      { id: 1, name: 'Cash & Bank', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 2, name: 'Business Checking', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 3, name: 'Accounts Receivable', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 4, name: 'Equipment', category: 'asset', type: 'Fixed Asset', balance: 0 },
      { id: 5, name: 'Software Licenses', category: 'asset', type: 'Intangible Asset', balance: 0 },
      
      // Liabilities
      { id: 6, name: 'Accounts Payable', category: 'liability', type: 'Current Liability', balance: 0 },
      { id: 7, name: 'Credit Cards', category: 'liability', type: 'Current Liability', balance: 0 },
      
      // Equity
      { id: 8, name: 'Owner\'s Investment', category: 'equity', type: 'Owner Equity', balance: 0 },
      { id: 9, name: 'Retained Earnings', category: 'equity', type: 'Owner Equity', balance: 0 },
      
      // Revenue
      { id: 10, name: 'Service Revenue', category: 'revenue', type: 'Income', balance: 0 },
      { id: 11, name: 'Consulting Revenue', category: 'revenue', type: 'Income', balance: 0 },
      
      // Expenses
      { id: 12, name: 'Professional Fees', category: 'expense', type: 'Operating Expense', balance: 0 },
      { id: 13, name: 'Office Rent', category: 'expense', type: 'Operating Expense', balance: 0 },
      { id: 14, name: 'Software Subscriptions', category: 'expense', type: 'Operating Expense', balance: 0 },
      { id: 15, name: 'Marketing', category: 'expense', type: 'Operating Expense', balance: 0 }
    ],
    
    manufacturing: [
      // Assets
      { id: 1, name: 'Cash & Bank', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 2, name: 'Raw Materials', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 3, name: 'Work in Progress', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 4, name: 'Finished Goods', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 5, name: 'Manufacturing Equipment', category: 'asset', type: 'Fixed Asset', balance: 0 },
      { id: 6, name: 'Factory Building', category: 'asset', type: 'Fixed Asset', balance: 0 },
      
      // Liabilities
      { id: 7, name: 'Accounts Payable', category: 'liability', type: 'Current Liability', balance: 0 },
      { id: 8, name: 'Equipment Loans', category: 'liability', type: 'Long-term Liability', balance: 0 },
      
      // Equity
      { id: 9, name: 'Owner\'s Investment', category: 'equity', type: 'Owner Equity', balance: 0 },
      { id: 10, name: 'Retained Earnings', category: 'equity', type: 'Owner Equity', balance: 0 },
      
      // Revenue
      { id: 11, name: 'Product Sales', category: 'revenue', type: 'Income', balance: 0 },
      
      // Expenses
      { id: 12, name: 'Raw Materials Cost', category: 'expense', type: 'Cost of Sales', balance: 0 },
      { id: 13, name: 'Labor Cost', category: 'expense', type: 'Cost of Sales', balance: 0 },
      { id: 14, name: 'Factory Overhead', category: 'expense', type: 'Operating Expense', balance: 0 },
      { id: 15, name: 'Quality Control', category: 'expense', type: 'Operating Expense', balance: 0 }
    ],
    
    freelancer: [
      // Assets
      { id: 1, name: 'Cash & Bank', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 2, name: 'Business Checking', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 3, name: 'Accounts Receivable', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 4, name: 'Equipment', category: 'asset', type: 'Fixed Asset', balance: 0 },
      
      // Liabilities
      { id: 5, name: 'Accounts Payable', category: 'liability', type: 'Current Liability', balance: 0 },
      
      // Equity
      { id: 6, name: 'Owner\'s Investment', category: 'equity', type: 'Owner Equity', balance: 0 },
      { id: 7, name: 'Retained Earnings', category: 'equity', type: 'Owner Equity', balance: 0 },
      
      // Revenue
      { id: 8, name: 'Service Revenue', category: 'revenue', type: 'Income', balance: 0 },
      
      // Expenses
      { id: 9, name: 'Home Office', category: 'expense', type: 'Operating Expense', balance: 0 },
      { id: 10, name: 'Internet & Phone', category: 'expense', type: 'Operating Expense', balance: 0 },
      { id: 11, name: 'Software Tools', category: 'expense', type: 'Operating Expense', balance: 0 }
    ],
    
    ngo: [
      // Assets
      { id: 1, name: 'Cash & Bank', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 2, name: 'Restricted Funds', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 3, name: 'Accounts Receivable', category: 'asset', type: 'Current Asset', balance: 0 },
      { id: 4, name: 'Equipment', category: 'asset', type: 'Fixed Asset', balance: 0 },
      
      // Liabilities
      { id: 5, name: 'Accounts Payable', category: 'liability', type: 'Current Liability', balance: 0 },
      { id: 6, name: 'Grants Payable', category: 'liability', type: 'Current Liability', balance: 0 },
      
      // Equity
      { id: 7, name: 'Unrestricted Net Assets', category: 'equity', type: 'Net Assets', balance: 0 },
      { id: 8, name: 'Temporarily Restricted', category: 'equity', type: 'Net Assets', balance: 0 },
      { id: 9, name: 'Permanently Restricted', category: 'equity', type: 'Net Assets', balance: 0 },
      
      // Revenue
      { id: 10, name: 'Donations', category: 'revenue', type: 'Support', balance: 0 },
      { id: 11, name: 'Grants', category: 'revenue', type: 'Support', balance: 0 },
      
      // Expenses
      { id: 12, name: 'Program Expenses', category: 'expense', type: 'Program', balance: 0 },
      { id: 13, name: 'Administrative', category: 'expense', type: 'Administrative', balance: 0 },
      { id: 14, name: 'Fundraising', category: 'expense', type: 'Fundraising', balance: 0 }
    ]
  };
  
  return templates[templateId] || templates.retail; // Default to retail if template not found
};

export const CoAProvider = ({ children }) => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('tree'); // 'tree', 'table', 'list'
  const [selectedAccounts, setSelectedAccounts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [sortBy, setSortBy] = useState('code');
  const [sortOrder, setSortOrder] = useState('asc');
  const [editingAccount, setEditingAccount] = useState(null);
  const [showInactive, setShowInactive] = useState(false);
  const [templateLoaded, setTemplateLoaded] = useState(false);

  // Load template from onboarding
  const loadTemplateFromOnboarding = useCallback(async () => {
    try {
      const savedTemplate = localStorage.getItem('edonuops_coa_template');
      if (savedTemplate && !templateLoaded) {
        
        // Define template accounts based on selected template
        const templateAccounts = getTemplateAccounts(savedTemplate);
        
        // Set accounts directly (no API call needed for templates)
        setAccounts(templateAccounts);
        setTemplateLoaded(true);
      }
    } catch (err) {
      console.error('Failed to load template:', err);
    }
  }, [templateLoaded]);

  const fetchAccounts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Load template from onboarding
      await loadTemplateFromOnboarding();
      
      // If no template was loaded, use default retail template
      if (accounts.length === 0 && !templateLoaded) {
        const defaultAccounts = getTemplateAccounts('retail');
        setAccounts(defaultAccounts);
        setTemplateLoaded(true);
      }
    } catch (err) {
      setError(err.message);
      console.error('Failed to load accounts:', err);
    } finally {
      setLoading(false);
    }
  }, [loadTemplateFromOnboarding, accounts.length, templateLoaded]);

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  const addAccount = useCallback(async (accountData) => {
    try {
      // Generate a new ID for the account
      const newId = Math.max(...accounts.map(acc => acc.id), 0) + 1;
      const newAccount = {
        id: newId,
        ...accountData,
        balance: 0
      };
      
      // Update local state
      setAccounts(prev => [...prev, newAccount]);
      return newAccount;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, [accounts]);

  const updateAccount = useCallback(async (id, accountData) => {
    try {
      // Update local state
      setAccounts(prev => prev.map(acc => acc.id === id ? { ...acc, ...accountData } : acc));
      return { id, ...accountData };
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const deleteAccount = useCallback(async (id) => {
    try {
      // Update local state
      setAccounts(prev => prev.filter(acc => acc.id !== id));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const buildAccountTree = useCallback(() => {
    const accountMap = new Map();
    const rootAccounts = [];

    // Create a map of all accounts
    accounts.forEach(account => {
      accountMap.set(account.id, { ...account, children: [] });
    });

    // Build the tree structure
    accounts.forEach(account => {
      const node = accountMap.get(account.id);
      if (account.parent_id) {
        const parent = accountMap.get(account.parent_id);
        if (parent) {
          parent.children.push(node);
        }
      } else {
        rootAccounts.push(node);
      }
    });

    return rootAccounts;
  }, [accounts]);


  const value = {
    accounts,
    loading,
    error,
    viewMode,
    setViewMode,
    selectedAccounts,
    setSelectedAccounts,
    searchTerm,
    setSearchTerm,
    filterCategory,
    setFilterCategory,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
    editingAccount,
    setEditingAccount,
    showInactive,
    setShowInactive,
    fetchAccounts,
    addAccount,
    updateAccount,
    deleteAccount,
    buildAccountTree
  };

  return (
    <CoAContext.Provider value={value}>
      {children}
    </CoAContext.Provider>
  );
};

export const useCoA = () => {
  const context = useContext(CoAContext);
  if (!context) {
    throw new Error('useCoA must be used within a CoAProvider');
  }
  return context;
};