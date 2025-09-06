import React, { useState, useEffect, createContext, useContext } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Grid
} from '@mui/material';
import { CurrencyExchange, Settings, Warning } from '@mui/icons-material';
import apiClient from '../services/apiClient';

// Global Currency Context
const CurrencyContext = createContext();

export const useCurrency = () => useContext(CurrencyContext);

export const CurrencyProvider = ({ children }) => {
  const [baseCurrency, setBaseCurrency] = useState('USD');
  const [currencySettings, setCurrencySettings] = useState(null);
  const [showChangeDialog, setShowChangeDialog] = useState(false);
  const [newCurrency, setNewCurrency] = useState('USD');
  const [conversionRates, setConversionRates] = useState({});

  const currencies = [
    { code: 'USD', name: 'US Dollar', symbol: '$' },
    { code: 'EUR', name: 'Euro', symbol: '€' },
    { code: 'GBP', name: 'British Pound', symbol: '£' },
    { code: 'JPY', name: 'Japanese Yen', symbol: '¥' },
    { code: 'CAD', name: 'Canadian Dollar', symbol: 'C$' },
    { code: 'AUD', name: 'Australian Dollar', symbol: 'A$' },
    { code: 'CHF', name: 'Swiss Franc', symbol: 'CHF' },
    { code: 'CNY', name: 'Chinese Yuan', symbol: '¥' },
    { code: 'INR', name: 'Indian Rupee', symbol: '₹' },
    { code: 'BRL', name: 'Brazilian Real', symbol: 'R$' }
  ];

  useEffect(() => {
    loadCurrencySettings();
    loadExchangeRates();
  }, []);

  const loadCurrencySettings = async () => {
    try {
      const res = await apiClient.getSettingsSection('currency');
      const data = res?.data || res || {};
      setCurrencySettings(data);
      const bc = data.base_currency || 'USD';
      setBaseCurrency(bc);
      setNewCurrency(bc);
    } catch (error) {
      console.error('Error loading currency settings:', error);
    }
  };

  const loadExchangeRates = async () => {
    try {
      const data = await apiClient.getExchangeRates();
      const rates = {};
      data.forEach(rate => {
        rates[`${rate.from_currency}_${rate.to_currency}`] = rate.rate;
      });
      setConversionRates(rates);
    } catch (error) {
      console.error('Error loading exchange rates:', error);
    }
  };

  const handleCurrencyChange = async () => {
    try {
      const updated = { ...(currencySettings || {}), base_currency: newCurrency };
      await apiClient.putSettingsSection('currency', { data: updated });
      setCurrencySettings(updated);
      setBaseCurrency(newCurrency);
      setShowChangeDialog(false);
      await convertAllData(newCurrency);
    } catch (error) {
      console.error('Error changing currency:', error);
    }
  };

  const convertAllData = async (newCurrency) => {
    try {
      // Convert all existing data to new currency
      await apiClient.convertAllCurrencies();
    } catch (error) {
      console.error('Error converting data:', error);
    }
  };

  const formatCurrency = (amount, currency = baseCurrency) => {
    const currencyInfo = currencies.find(c => c.code === currency);
    const symbol = currencyInfo?.symbol || currency;
    return `${symbol}${parseFloat(amount || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const convertAmount = (amount, fromCurrency, toCurrency = baseCurrency) => {
    if (fromCurrency === toCurrency) return amount;
    
    const rateKey = `${fromCurrency}_${toCurrency}`;
    const rate = conversionRates[rateKey] || 1;
    return amount * rate;
  };

  const value = {
    baseCurrency,
    currencies,
    formatCurrency,
    convertAmount,
    setShowChangeDialog
  };

  return (
    <CurrencyContext.Provider value={value}>
      {children}
      
      {/* Global Currency Settings Dialog */}
      <Dialog open={showChangeDialog} onClose={() => setShowChangeDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <CurrencyExchange color="primary" />
            <Typography variant="h6">Change Base Currency</Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            <strong>Warning:</strong> Changing the base currency will convert all existing financial data. 
            This action cannot be undone.
          </Alert>
          
          <Typography variant="body2" sx={{ mb: 2 }}>
            Current base currency: <Chip label={baseCurrency} color="primary" />
          </Typography>
          
          <FormControl fullWidth>
            <InputLabel>New Base Currency</InputLabel>
            <Select
              value={newCurrency}
              onChange={(e) => setNewCurrency(e.target.value)}
            >
              {currencies.map((currency) => (
                <MenuItem key={currency.code} value={currency.code}>
                  {currency.code} - {currency.name} ({currency.symbol})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Alert severity="info" sx={{ mt: 2 }}>
            All existing amounts will be automatically converted using current exchange rates.
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowChangeDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleCurrencyChange}
            disabled={newCurrency === baseCurrency}
          >
            Change Currency
          </Button>
        </DialogActions>
      </Dialog>
    </CurrencyContext.Provider>
  );
};

// Global Currency Settings Component
const GlobalCurrencySettings = () => {
  const { baseCurrency, currencies, setShowChangeDialog } = useCurrency();

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" display="flex" alignItems="center" gap={1}>
            <Settings />
            Global Currency Settings
          </Typography>
          <Button
            variant="outlined"
            startIcon={<CurrencyExchange />}
            onClick={() => setShowChangeDialog(true)}
          >
            Change Currency
          </Button>
        </Box>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Current Base Currency
            </Typography>
            <Chip 
              label={baseCurrency} 
              color="primary" 
              size="large"
              sx={{ mt: 1 }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" color="text.secondary">
              Available Currencies
            </Typography>
            <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
              {currencies.slice(0, 5).map((currency) => (
                <Chip 
                  key={currency.code}
                  label={`${currency.code} (${currency.symbol})`}
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default GlobalCurrencySettings;
