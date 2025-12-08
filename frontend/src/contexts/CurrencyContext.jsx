/**
 * Currency Context for Multi-Currency Support
 * Manages currency selection, conversion, and real-time data updates
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiClient from '../services/apiClient';

const CurrencyContext = createContext();

export const useCurrency = () => {
  const context = useContext(CurrencyContext);
  if (!context) {
    throw new Error('useCurrency must be used within a CurrencyProvider');
  }
  return context;
};

export const CurrencyProvider = ({ children }) => {
  // State management
  const [selectedCurrency, setSelectedCurrency] = useState('USD'); // Default currency
  const [availableCurrencies, setAvailableCurrencies] = useState([]);
  const [exchangeRates, setExchangeRates] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Currency preference persistence
  const [currencyPreferences, setCurrencyPreferences] = useState(() => {
    const saved = localStorage.getItem('edonuops_currency_preferences');
    return saved ? JSON.parse(saved) : {
      baseCurrency: 'USD',
      displayCurrency: 'USD',
      autoConvert: true,
      showSymbols: true
    };
  });

  // Save preferences to localStorage
  useEffect(() => {
    localStorage.setItem('edonuops_currency_preferences', JSON.stringify(currencyPreferences));
  }, [currencyPreferences]);

  // API call helper
  const apiCall = useCallback(async (endpoint, options = {}) => {
    try {
      const response = await apiClient.get(`/api/currency${endpoint}`, options);
      return response;
    } catch (error) {
      console.error(`Currency API Error (${endpoint}):`, error);
      throw error;
    }
  }, []);

  // Fetch available currencies
  const fetchCurrencies = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const currencies = await apiCall('/currencies?active_only=true');
      setAvailableCurrencies(currencies);
      
      console.log('✅ Loaded currencies:', currencies.length);
      return currencies;
    } catch (error) {
      setError('Failed to load currencies');
      console.error('❌ Currency fetch error:', error);
      
      // Fallback currencies if API fails
      const fallbackCurrencies = [
        { code: 'USD', name: 'US Dollar', symbol: '$' },
        { code: 'EUR', name: 'Euro', symbol: '€' },
        { code: 'GBP', name: 'British Pound', symbol: '£' },
        { code: 'JPY', name: 'Japanese Yen', symbol: '¥' }
      ];
      setAvailableCurrencies(fallbackCurrencies);
      return fallbackCurrencies;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  // Fetch current exchange rates
  const fetchExchangeRates = useCallback(async (baseCurrency = selectedCurrency) => {
    // Only fetch if user is authenticated
    const token = localStorage.getItem('sessionToken') || localStorage.getItem('access_token');
    if (!token) {
      console.log('⚠️ Skipping exchange rates fetch - user not authenticated');
      return exchangeRates;
    }
    
    try {
      const rates = await apiCall(`/exchange-rates?from_currency=${baseCurrency}`);
      
      // Convert to simple object format: { EUR: 0.85, GBP: 0.73, ... }
      const ratesMap = {};
      rates.forEach(rate => {
        ratesMap[rate.to_currency_code] = rate.rate;
      });
      
      // Always include base currency as 1.0
      ratesMap[baseCurrency] = 1.0;
      
      setExchangeRates(ratesMap);
      console.log('✅ Exchange rates loaded:', Object.keys(ratesMap).length);
      return ratesMap;
    } catch (error) {
      console.error('❌ Exchange rates fetch error:', error);
      // Keep existing rates on error
      return exchangeRates;
    }
  }, [selectedCurrency, apiCall, exchangeRates]);

  // Convert amount between currencies
  const convertAmount = useCallback((amount, fromCurrency, toCurrency) => {
    if (!amount || amount === 0) return 0;
    if (fromCurrency === toCurrency) return amount;
    
    const fromRate = exchangeRates[fromCurrency] || 1;
    const toRate = exchangeRates[toCurrency] || 1;
    
    // Convert to base currency first, then to target currency
    const baseAmount = amount / fromRate;
    const convertedAmount = baseAmount * toRate;
    
    return convertedAmount;
  }, [exchangeRates]);

  // Convert amount with API call for accuracy (for important conversions)
  const convertAmountAPI = useCallback(async (amount, fromCurrency, toCurrency) => {
    try {
      const response = await apiClient.post('/api/currency/convert', {
        amount: parseFloat(amount),
        from_currency: fromCurrency,
        to_currency: toCurrency,
        record_conversion: false // Don't record UI conversions
      });
      
      return response.converted_amount;
    } catch (error) {
      console.error('❌ API conversion error:', error);
      // Fallback to local conversion
      return convertAmount(amount, fromCurrency, toCurrency);
    }
  }, [apiCall, convertAmount]);

  // Format currency amount with proper symbol and decimals
  const formatCurrency = useCallback((amount, currency = selectedCurrency, options = {}) => {
    const currencyInfo = availableCurrencies.find(c => c.code === currency);
    const symbol = currencyInfo?.symbol || currency;
    const decimals = currencyInfo?.decimal_places || 2;
    
    const {
      showSymbol = currencyPreferences.showSymbols,
      showCode = false,
      minimumFractionDigits = decimals,
      maximumFractionDigits = decimals
    } = options;
    
    try {
      const formatter = new Intl.NumberFormat('en-US', {
        style: showSymbol ? 'currency' : 'decimal',
        currency: currency,
        minimumFractionDigits,
        maximumFractionDigits
      });
      
      let formatted = formatter.format(amount || 0);
      
      // If using symbol and we have custom symbol, replace
      if (showSymbol && symbol && !formatted.includes(symbol)) {
        formatted = `${symbol}${formatted.replace(/[^\d,.-]/g, '')}`;
      }
      
      // Add currency code if requested
      if (showCode) {
        formatted += ` ${currency}`;
      }
      
      return formatted;
    } catch (error) {
      console.error('Currency formatting error:', error);
      return `${symbol}${(amount || 0).toFixed(decimals)}`;
    }
  }, [selectedCurrency, availableCurrencies, currencyPreferences.showSymbols]);

  // Change currency with automatic conversion
  const changeCurrency = useCallback(async (newCurrency, shouldConvert = true) => {
    if (newCurrency === selectedCurrency) return;
    
    console.log(`🔄 Changing currency from ${selectedCurrency} to ${newCurrency}`);
    
    try {
      setLoading(true);
      
      // Update exchange rates for new currency
      await fetchExchangeRates(newCurrency);
      
      // Update selected currency
      const oldCurrency = selectedCurrency;
      setSelectedCurrency(newCurrency);
      
      // Update preferences
      setCurrencyPreferences(prev => ({
        ...prev,
        displayCurrency: newCurrency
      }));
      
      console.log('✅ Currency changed successfully');
      
      // Return conversion info for components to use
      return {
        oldCurrency,
        newCurrency,
        shouldConvert,
        convertAmount: (amount) => convertAmount(amount, oldCurrency, newCurrency)
      };
      
    } catch (error) {
      setError('Failed to change currency');
      console.error('❌ Currency change error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [selectedCurrency, fetchExchangeRates, convertAmount]);

  // Update exchange rates
  const updateExchangeRates = useCallback(async () => {
    try {
      setLoading(true);
      
      // Trigger backend to update rates from API
      await apiCall('/exchange-rates/update', {
        method: 'POST',
        body: JSON.stringify({ base_currency: selectedCurrency })
      });
      
      // Fetch updated rates
      await fetchExchangeRates();
      
      console.log('✅ Exchange rates updated from API');
    } catch (error) {
      setError('Failed to update exchange rates');
      console.error('❌ Exchange rate update error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [selectedCurrency, apiCall, fetchExchangeRates]);

  // Get currency info
  const getCurrencyInfo = useCallback((currencyCode) => {
    return availableCurrencies.find(c => c.code === currencyCode) || {
      code: currencyCode,
      name: currencyCode,
      symbol: currencyCode
    };
  }, [availableCurrencies]);

  // Initialize on mount (only if authenticated)
  useEffect(() => {
    const token = localStorage.getItem('sessionToken') || localStorage.getItem('access_token');
    if (!token) {
      console.log('⚠️ Skipping currency initialization - user not authenticated');
      return;
    }
    
    const initialize = async () => {
      await fetchCurrencies();
      await fetchExchangeRates();
    };
    
    initialize();
  }, [fetchCurrencies, fetchExchangeRates]);

  // Auto-update rates every 30 minutes (only if authenticated)
  useEffect(() => {
    const token = localStorage.getItem('sessionToken') || localStorage.getItem('access_token');
    if (!token) {
      return; // Don't start interval if not authenticated
    }
    
    const interval = setInterval(() => {
      // Check token again before each refresh
      const currentToken = localStorage.getItem('sessionToken') || localStorage.getItem('access_token');
      if (currentToken && !loading) {
        fetchExchangeRates();
      }
    }, 30 * 60 * 1000); // 30 minutes
    
    return () => clearInterval(interval);
  }, [fetchExchangeRates, loading]);

  const value = {
    // State
    selectedCurrency,
    availableCurrencies,
    exchangeRates,
    loading,
    error,
    currencyPreferences,
    
    // Actions
    changeCurrency,
    convertAmount,
    convertAmountAPI,
    formatCurrency,
    updateExchangeRates,
    fetchCurrencies,
    fetchExchangeRates,
    getCurrencyInfo,
    setCurrencyPreferences,
    
    // Utilities
    isLoading: loading,
    hasError: !!error,
    clearError: () => setError(null)
  };

  return (
    <CurrencyContext.Provider value={value}>
      {children}
    </CurrencyContext.Provider>
  );
};

