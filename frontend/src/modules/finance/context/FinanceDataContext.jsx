import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { useAuth } from '../../../App';
import apiClient from '../../../services/apiClient';

const FinanceDataContext = createContext();

export const useFinanceData = () => {
  const context = useContext(FinanceDataContext);
  if (!context) {
    throw new Error('useFinanceData must be used within a FinanceDataProvider');
  }
  return context;
};

export const FinanceDataProvider = ({ children }) => {
  const { apiClient, isAuthenticated } = useAuth();
  
  // Centralized state for all finance data
  const [data, setData] = useState({
    gl_entries: [],
    accounts: [],
    invoices: [],
    bills: [],
    customers: [],
    vendors: []
  });
  
  const [loading, setLoading] = useState({
    gl_entries: false,
    accounts: false,
    invoices: false,
    bills: false,
    customers: false,
    vendors: false
  });
  
  const [errors, setErrors] = useState({});
  const [lastUpdated, setLastUpdated] = useState({});

  // Data will be handled by backend API

  // No fallback data - rely on backend API

  // Generic fetch function
  const fetchData = useCallback(async (endpoint) => {
    if (!isAuthenticated) return;
    
    setLoading(prev => ({ ...prev, [endpoint]: true }));
    setErrors(prev => ({ ...prev, [endpoint]: null }));
    
    try {
      
      // First check if backend is reachable
      try {
        await apiClient.healthCheck();
      } catch (healthError) {
        throw new Error('Backend server not reachable. Please ensure backend is running.');
      }
      
      const response = await apiClient.get(`/finance/${endpoint}`);
      
      setData(prev => ({ ...prev, [endpoint]: response }));
      setLastUpdated(prev => ({ ...prev, [endpoint]: new Date() }));
      
    } catch (error) {
      console.error(`❌ Failed to fetch ${endpoint}:`, error);
      
      let errorMessage = 'Network error';
      if (error.message.includes('fetch')) {
        errorMessage = 'Backend server not reachable. Please ensure backend is running.';
      } else if (error.message.includes('401')) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (error.message.includes('404')) {
        errorMessage = 'Resource not found. Please check the endpoint.';
      } else if (error.message.includes('500')) {
        errorMessage = 'Server error. Please try again later.';
      } else {
        errorMessage = error.message;
      }
      
      setErrors(prev => ({ ...prev, [endpoint]: errorMessage }));
    } finally {
      setLoading(prev => ({ ...prev, [endpoint]: false }));
    }
  }, [apiClient, isAuthenticated]);

  // Specific data fetchers
  const fetchGLEntries = useCallback(() => fetchData('gl_entries'), [fetchData]);
  const fetchAccounts = useCallback(() => fetchData('coa'), [fetchData]);
  const fetchInvoices = useCallback(() => fetchData('ar'), [fetchData]);
  const fetchBills = useCallback(() => fetchData('ap'), [fetchData]);

  // Data manipulation functions - will be handled by backend API
  const addJournalEntry = useCallback(async (formData) => {
    // Will be implemented with backend API call
  }, []);

  const updateJournalEntry = useCallback((id, formData) => {
    setData(prev => ({
      ...prev,
      gl_entries: prev.gl_entries.map(entry => 
        entry.id === id ? { ...entry, ...formData, updated_at: new Date().toISOString() } : entry
      )
    }));
  }, []);

  const addInvoice = useCallback(async (formData) => {
    // Will be implemented with backend API call
  }, []);

  const updateInvoice = useCallback((id, updates) => {
    setData(prev => ({
      ...prev,
      invoices: prev.invoices.map(invoice => 
        invoice.id === id ? { ...invoice, ...updates } : invoice
      )
    }));
  }, []);

  const recordPayment = useCallback((invoiceId, paymentData) => {
    setData(prev => ({
      ...prev,
      invoices: prev.invoices.map(invoice => 
        invoice.id === invoiceId ? { 
          ...invoice, 
          status: 'paid',
          paid_amount: paymentData.amount,
          paid_date: paymentData.date,
          payment_method: paymentData.method
        } : invoice
      )
    }));
  }, []);

  const addBill = useCallback(async (formData) => {
    // Will be implemented with backend API call
  }, []);

  const processBillPayment = useCallback((billId, paymentData) => {
    setData(prev => ({
      ...prev,
      bills: prev.bills.map(bill => 
        bill.id === billId ? { 
          ...bill, 
          status: 'paid',
          paid_amount: paymentData.amount,
          paid_date: paymentData.date,
          payment_method: paymentData.method
        } : bill
      )
    }));
  }, []);

  // Initial data load
  useEffect(() => {
    if (isAuthenticated) {
      fetchGLEntries();
      fetchAccounts();
      fetchInvoices();
      fetchBills();
    }
  }, [isAuthenticated, fetchGLEntries, fetchAccounts, fetchInvoices, fetchBills]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const interval = setInterval(() => {
      fetchGLEntries();
      fetchInvoices();
      fetchBills();
    }, 30000);

    return () => clearInterval(interval);
  }, [isAuthenticated, fetchGLEntries, fetchInvoices, fetchBills]);

  const value = {
    // Data
    glEntries: data.gl_entries,
    accounts: data.accounts,
    invoices: data.invoices,
    bills: data.bills,
    customers: data.customers,
    vendors: data.vendors,
    
    // Loading states
    loading,
    errors,
    lastUpdated,
    
    // Refresh functions
    refreshGLEntries: fetchGLEntries,
    refreshAccounts: fetchAccounts,
    refreshInvoices: fetchInvoices,
    refreshBills: fetchBills,
    refreshAll: useCallback(() => {
      fetchGLEntries();
      fetchAccounts();
      fetchInvoices();
      fetchBills();
    }, [fetchGLEntries, fetchAccounts, fetchInvoices, fetchBills]),
    
    // Data manipulation
    addJournalEntry,
    updateJournalEntry,
    addInvoice,
    updateInvoice,
    recordPayment,
    addBill,
    processBillPayment,
    
    // Utility functions
    getInvoicesByStatus: useCallback((status) => 
      data.invoices.filter(inv => inv.status === status), [data.invoices]),
    
    getBillsByStatus: useCallback((status) => 
      data.bills.filter(bill => bill.status === status), [data.bills]),
    
    getTotalOutstandingAR: useCallback(() => 
      data.invoices
        .filter(inv => inv.status !== 'paid')
        .reduce((sum, inv) => sum + (inv.amount || 0), 0), [data.invoices]),
    
    getTotalOutstandingAP: useCallback(() => 
      data.bills
        .filter(bill => bill.status !== 'paid')
        .reduce((sum, bill) => sum + (bill.amount || 0), 0), [data.bills]),
    
    getOverdueInvoices: useCallback(() => {
      const today = new Date();
      return data.invoices.filter(inv => 
        inv.status !== 'paid' && new Date(inv.due_date) < today
      );
    }, [data.invoices]),
    
    getOverdueBills: useCallback(() => {
      const today = new Date();
      return data.bills.filter(bill => 
        bill.status !== 'paid' && new Date(bill.due_date) < today
      );
    }, [data.bills])
  };

  return (
    <FinanceDataContext.Provider value={value}>
      {children}
    </FinanceDataContext.Provider>
  );
};

export default FinanceDataContext;
