/**
 * Currency Conversion Hook
 * Handles automatic conversion of financial data when currency changes
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useCurrency } from '../contexts/CurrencyContext';

export const useCurrencyConversion = (data, dataType = 'financial') => {
  const { 
    selectedCurrency, 
    convertAmount, 
    convertAmountAPI, 
    formatCurrency,
    exchangeRates 
  } = useCurrency();

  const [convertedData, setConvertedData] = useState(data);
  const [isConverting, setIsConverting] = useState(false);
  const [conversionHistory, setConversionHistory] = useState([]);
  const previousCurrency = useRef(selectedCurrency);
  const originalData = useRef(data);

  // Update original data when data prop changes
  useEffect(() => {
    originalData.current = data;
    setConvertedData(data);
  }, [data]);

  // Convert monetary fields in an object
  const convertMonetaryFields = useCallback((item, fromCurrency, toCurrency, useAPI = false) => {
    if (!item || fromCurrency === toCurrency) return item;

    const monetaryFields = getMonetaryFields(dataType);
    const converted = { ...item };

    monetaryFields.forEach(field => {
      if (item[field] !== undefined && item[field] !== null && item[field] !== '') {
        const originalAmount = parseFloat(item[field]) || 0;
        if (useAPI) {
          // For critical conversions, we'll update this later with API call
          converted[field + '_converting'] = true;
        } else {
          converted[field] = convertAmount(originalAmount, fromCurrency, toCurrency);
        }
      }
    });

    // Update currency field if present
    if (item.currency) {
      converted.currency = toCurrency;
    }

    return converted;
  }, [dataType, convertAmount]);

  // Get monetary fields based on data type
  const getMonetaryFields = useCallback((type) => {
    const fieldMappings = {
      'coa': ['balance', 'debit_balance', 'credit_balance', 'opening_balance'],
      'gl_entries': ['amount', 'debit_amount', 'credit_amount', 'balance'],
      'journal_entries': ['amount', 'debit', 'credit', 'total_amount'],
      'invoices': ['amount', 'total_amount', 'subtotal', 'tax_amount', 'discount_amount', 'balance_due'],
      'bills': ['amount', 'total_amount', 'subtotal', 'tax_amount', 'discount_amount', 'amount_due'],
      'transactions': ['amount', 'balance', 'debit', 'credit'],
      'financial': ['amount', 'balance', 'total', 'subtotal', 'tax', 'discount', 'debit', 'credit'],
      'reports': ['amount', 'balance', 'total_assets', 'total_liabilities', 'total_equity', 'net_income']
    };

    return fieldMappings[type] || fieldMappings['financial'];
  }, []);

  // Convert array of data
  const convertDataArray = useCallback(async (dataArray, fromCurrency, toCurrency, useAPI = false) => {
    if (!Array.isArray(dataArray)) return dataArray;

    setIsConverting(true);
    try {
      const converted = [];

      for (const item of dataArray) {
        const convertedItem = convertMonetaryFields(item, fromCurrency, toCurrency, useAPI);
        
        // If using API for critical fields
        if (useAPI) {
          const monetaryFields = getMonetaryFields(dataType);
          for (const field of monetaryFields) {
            if (item[field] !== undefined && item[field] !== null && item[field] !== '') {
              const originalAmount = parseFloat(item[field]) || 0;
              if (originalAmount !== 0) {
                try {
                  const convertedAmount = await convertAmountAPI(originalAmount, fromCurrency, toCurrency);
                  convertedItem[field] = convertedAmount;
                  delete convertedItem[field + '_converting'];
                } catch (error) {
                  console.error(`Failed to convert ${field} for item ${item.id}:`, error);
                  // Fallback to local conversion
                  convertedItem[field] = convertAmount(originalAmount, fromCurrency, toCurrency);
                  delete convertedItem[field + '_converting'];
                }
              }
            }
          }
        }

        converted.push(convertedItem);
      }

      return converted;
    } finally {
      setIsConverting(false);
    }
  }, [dataType, convertMonetaryFields, getMonetaryFields, convertAmountAPI, convertAmount]);

  // Convert single object
  const convertDataObject = useCallback(async (dataObject, fromCurrency, toCurrency, useAPI = false) => {
    if (!dataObject || typeof dataObject !== 'object') return dataObject;

    setIsConverting(true);
    try {
      let converted = convertMonetaryFields(dataObject, fromCurrency, toCurrency, useAPI);

      // If using API for critical fields
      if (useAPI) {
        const monetaryFields = getMonetaryFields(dataType);
        for (const field of monetaryFields) {
          if (dataObject[field] !== undefined && dataObject[field] !== null && dataObject[field] !== '') {
            const originalAmount = parseFloat(dataObject[field]) || 0;
            if (originalAmount !== 0) {
              try {
                const convertedAmount = await convertAmountAPI(originalAmount, fromCurrency, toCurrency);
                converted[field] = convertedAmount;
                delete converted[field + '_converting'];
              } catch (error) {
                console.error(`Failed to convert ${field}:`, error);
                // Fallback to local conversion
                converted[field] = convertAmount(originalAmount, fromCurrency, toCurrency);
                delete converted[field + '_converting'];
              }
            }
          }
        }
      }

      return converted;
    } finally {
      setIsConverting(false);
    }
  }, [dataType, convertMonetaryFields, getMonetaryFields, convertAmountAPI, convertAmount]);

  // Main conversion function
  const performConversion = useCallback(async (fromCurrency, toCurrency, useAPI = false) => {
    if (!data || fromCurrency === toCurrency) return;

    console.log(`🔄 Converting ${dataType} data from ${fromCurrency} to ${toCurrency}`);

    try {
      let converted;

      if (Array.isArray(data)) {
        converted = await convertDataArray(data, fromCurrency, toCurrency, useAPI);
      } else {
        converted = await convertDataObject(data, fromCurrency, toCurrency, useAPI);
      }

      setConvertedData(converted);

      // Record conversion history
      setConversionHistory(prev => [...prev, {
        timestamp: new Date(),
        fromCurrency,
        toCurrency,
        dataType,
        itemCount: Array.isArray(data) ? data.length : 1,
        useAPI
      }]);

      console.log(`✅ Converted ${dataType} data successfully`);
      return converted;
    } catch (error) {
      console.error(`❌ Failed to convert ${dataType} data:`, error);
      throw error;
    }
  }, [data, dataType, convertDataArray, convertDataObject]);

  // Auto-convert when currency changes
  useEffect(() => {
    const handleCurrencyChange = async () => {
      if (previousCurrency.current !== selectedCurrency && exchangeRates && Object.keys(exchangeRates).length > 0) {
        await performConversion(previousCurrency.current, selectedCurrency, false);
        previousCurrency.current = selectedCurrency;
      }
    };

    handleCurrencyChange();
  }, [selectedCurrency, exchangeRates, performConversion]);

  // Manual conversion with API accuracy
  const convertWithAPI = useCallback(async (fromCurrency, toCurrency) => {
    return await performConversion(fromCurrency, toCurrency, true);
  }, [performConversion]);

  // Format amounts in converted data
  const formatAmount = useCallback((amount, currencyCode = selectedCurrency, options = {}) => {
    return formatCurrency(amount, currencyCode, options);
  }, [formatCurrency, selectedCurrency]);

  // Check if data has monetary values
  const hasMonetaryData = useCallback(() => {
    if (!data) return false;

    const monetaryFields = getMonetaryFields(dataType);
    const checkItem = (item) => {
      return monetaryFields.some(field => {
        const value = item[field];
        return value !== undefined && value !== null && value !== '' && parseFloat(value) !== 0;
      });
    };

    if (Array.isArray(data)) {
      return data.some(checkItem);
    } else {
      return checkItem(data);
    }
  }, [data, dataType, getMonetaryFields]);

  // Get conversion summary
  const getConversionSummary = useCallback(() => {
    const recent = conversionHistory.slice(-5); // Last 5 conversions
    return {
      totalConversions: conversionHistory.length,
      recentConversions: recent,
      currentCurrency: selectedCurrency,
      hasData: hasMonetaryData(),
      isConverting
    };
  }, [conversionHistory, selectedCurrency, hasMonetaryData, isConverting]);

  return {
    // Converted data
    data: convertedData,
    originalData: originalData.current,
    
    // State
    isConverting,
    hasMonetaryData: hasMonetaryData(),
    
    // Actions
    convertWithAPI,
    performConversion,
    formatAmount,
    
    // Utilities
    getConversionSummary,
    conversionHistory,
    
    // Field helpers
    getMonetaryFields: () => getMonetaryFields(dataType)
  };
};

