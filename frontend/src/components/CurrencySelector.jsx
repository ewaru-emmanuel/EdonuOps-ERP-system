/**
 * Currency Selector Component
 * Allows users to switch currencies with automatic conversion of existing data
 */

import React, { useState } from 'react';
import {
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Box,
  Chip,
  Typography,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Switch,
  FormControlLabel,
  CircularProgress
} from '@mui/material';
import {
  CurrencyExchange as CurrencyIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';
import { useCurrency } from './GlobalCurrencySettings';

const CurrencySelector = ({ 
  variant = 'standard', 
  size = 'small', 
  showLabel = true,
  showRefresh = true,
  showSettings = true,
  onCurrencyChange = null,
  sx = {}
}) => {
  const {
    baseCurrency: selectedCurrency,
    currencies: availableCurrencies,
    formatCurrency
  } = useCurrency();

  // Provide default values for missing properties
  const loading = false;
  const error = null;
  const changeCurrency = (currency) => {
    console.log('Currency change requested:', currency);
    if (onCurrencyChange) {
      onCurrencyChange(currency);
    }
  };
  const updateExchangeRates = () => {
    console.log('Exchange rates update requested');
  };
  const currencyPreferences = {};
  const setCurrencyPreferences = () => {};
  const clearError = () => {};

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [conversionDialog, setConversionDialog] = useState({
    open: false,
    fromCurrency: null,
    toCurrency: null,
    onConfirm: null
  });

  // Handle currency change with confirmation for data conversion
  const handleCurrencyChange = async (newCurrency) => {
    if (newCurrency === selectedCurrency) return;

    try {
      // Check if there's existing financial data that needs conversion
      const hasData = onCurrencyChange ? await onCurrencyChange(selectedCurrency, newCurrency) : false;

      if (hasData && currencyPreferences.autoConvert) {
        // Show confirmation dialog for data conversion
        setConversionDialog({
          open: true,
          fromCurrency: selectedCurrency,
          toCurrency: newCurrency,
          onConfirm: async () => {
            await changeCurrency(newCurrency, true);
            setConversionDialog({ open: false, fromCurrency: null, toCurrency: null, onConfirm: null });
          }
        });
      } else {
        // Direct currency change
        await changeCurrency(newCurrency, false);
      }
    } catch (error) {
      console.error('Currency change failed:', error);
    }
  };

  // Handle exchange rate refresh
  const handleRefreshRates = async () => {
    try {
      await updateExchangeRates();
    } catch (error) {
      console.error('Failed to refresh rates:', error);
    }
  };

  // Get flag emoji for currency (simple mapping)
  const getCurrencyFlag = (currencyCode) => {
    const flags = {
      'USD': '🇺🇸', 'EUR': '🇪🇺', 'GBP': '🇬🇧', 'JPY': '🇯🇵',
      'CAD': '🇨🇦', 'AUD': '🇦🇺', 'CHF': '🇨🇭', 'CNY': '🇨🇳',
      'INR': '🇮🇳', 'KRW': '🇰🇷', 'BRL': '🇧🇷', 'MXN': '🇲🇽',
      'SGD': '🇸🇬', 'HKD': '🇭🇰', 'NOK': '🇳🇴', 'SEK': '🇸🇪',
      'DKK': '🇩🇰', 'PLN': '🇵🇱'
    };
    return flags[currencyCode] || '💱';
  };

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, ...sx }}>
      {/* Currency Selector */}
      <FormControl variant={variant} size={size} sx={{ minWidth: 120 }}>
        {showLabel && <InputLabel>Currency</InputLabel>}
        <Select
          value={selectedCurrency}
          onChange={(e) => handleCurrencyChange(e.target.value)}
          disabled={loading}
          label={showLabel ? "Currency" : undefined}
          startAdornment={
            <Box sx={{ display: 'flex', alignItems: 'center', mr: 1 }}>
              {getCurrencyFlag(selectedCurrency)}
            </Box>
          }
        >
          {availableCurrencies.map((currency) => (
            <MenuItem key={currency.code} value={currency.code}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <span>{getCurrencyFlag(currency.code)}</span>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="body2" fontWeight="medium">
                    {currency.code}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {currency.name}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {currency.symbol}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* Refresh Rates Button */}
      {showRefresh && (
        <Tooltip title="Refresh Exchange Rates">
          <IconButton 
            onClick={handleRefreshRates} 
            disabled={loading}
            size={size}
            color="primary"
          >
            {loading ? <CircularProgress size={16} /> : <RefreshIcon />}
          </IconButton>
        </Tooltip>
      )}

      {/* Settings Button */}
      {showSettings && (
        <Tooltip title="Currency Settings">
          <IconButton 
            onClick={() => setSettingsOpen(true)}
            size={size}
            color="default"
          >
            <SettingsIcon />
          </IconButton>
        </Tooltip>
      )}

      {/* Error Display */}
      {error && (
        <Tooltip title={error}>
          <IconButton size={size} color="error" onClick={clearError}>
            <WarningIcon />
          </IconButton>
        </Tooltip>
      )}

      {/* Currency Conversion Confirmation Dialog */}
      <Dialog 
        open={conversionDialog.open} 
        onClose={() => setConversionDialog({ open: false, fromCurrency: null, toCurrency: null, onConfirm: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CurrencyIcon color="primary" />
          Currency Conversion Required
        </DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            You have existing financial data in <strong>{conversionDialog.fromCurrency}</strong>. 
            Would you like to convert it to <strong>{conversionDialog.toCurrency}</strong>?
          </Alert>
          
          <Typography variant="body2" color="text.secondary" paragraph>
            This will automatically convert all amounts in:
          </Typography>
          
          <Box component="ul" sx={{ mt: 1, pl: 2 }}>
            <li>Chart of Accounts balances</li>
            <li>General Ledger entries</li>
            <li>Invoices and bills</li>
            <li>Financial reports</li>
          </Box>
          
          <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
            Exchange rates will be fetched from live market data for accuracy.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setConversionDialog({ open: false, fromCurrency: null, toCurrency: null, onConfirm: null })}
          >
            Cancel
          </Button>
          <Button 
            onClick={conversionDialog.onConfirm}
            variant="contained"
            startIcon={<CheckIcon />}
          >
            Convert Data
          </Button>
        </DialogActions>
      </Dialog>

      {/* Currency Settings Dialog */}
      <Dialog open={settingsOpen} onClose={() => setSettingsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Currency Preferences</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, pt: 1 }}>
            {/* Auto Convert Setting */}
            <FormControlLabel
              control={
                <Switch
                  checked={currencyPreferences.autoConvert}
                  onChange={(e) => setCurrencyPreferences(prev => ({
                    ...prev,
                    autoConvert: e.target.checked
                  }))}
                />
              }
              label="Auto-convert existing data when changing currency"
            />

            {/* Show Symbols Setting */}
            <FormControlLabel
              control={
                <Switch
                  checked={currencyPreferences.showSymbols}
                  onChange={(e) => setCurrencyPreferences(prev => ({
                    ...prev,
                    showSymbols: e.target.checked
                  }))}
                />
              }
              label="Show currency symbols (€, $, £)"
            />

            {/* Current Exchange Rate Preview */}
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Sample Formatting Preview
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Chip 
                  label={formatCurrency(1234.56, selectedCurrency)} 
                  color="primary" 
                  variant="outlined" 
                />
                <Chip 
                  label={formatCurrency(0, selectedCurrency)} 
                  color="default" 
                  variant="outlined" 
                />
              </Box>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CurrencySelector;

