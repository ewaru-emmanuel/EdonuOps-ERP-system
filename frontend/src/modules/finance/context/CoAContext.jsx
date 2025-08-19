import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { apiClient } from '../../../utils/apiClient.js';

const CoAContext = createContext();

export const CoAProvider = ({ children }) => {
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAccounts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.get('/finance/coa');
      setAccounts(data);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch accounts:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const addAccount = useCallback(async (accountData) => {
    try {
      const newAccount = await apiClient.post('/finance/coa', accountData);
      setAccounts(prev => [...prev, newAccount]);
      return newAccount;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const updateAccount = useCallback(async (id, accountData) => {
    try {
      const updatedAccount = await apiClient.put(`/finance/coa/${id}`, accountData);
      setAccounts(prev => prev.map(acc => acc.id === id ? updatedAccount : acc));
      return updatedAccount;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const deleteAccount = useCallback(async (id) => {
    try {
      await apiClient.delete(`/finance/coa/${id}`);
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

  useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  const value = {
    accounts,
    loading,
    error,
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