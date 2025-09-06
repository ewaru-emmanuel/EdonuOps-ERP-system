import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Tooltip,
  Divider
} from '@mui/material';
import {
  CurrencyExchange,
  Calculate,
  Assessment,
  Settings,
  Add,
  Refresh,
  TrendingUp,
  TrendingDown,
  Visibility
} from '@mui/icons-material';
import { Snackbar, Alert } from '@mui/material';
import apiClient from '../../../services/apiClient';

const MultiCurrencyValuation = () => {
  const [baseCurrency, setBaseCurrency] = useState('USD');
  const [exposureData, setExposureData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [valuationDialog, setValuationDialog] = useState(false);
  const [exposureDialog, setExposureDialog] = useState(false);
  const [settingsDialog, setSettingsDialog] = useState(false);
  const [valuationData, setValuationData] = useState({
    product_id: '',
    quantity: '',
    unit_cost: '',
    currency: 'USD',
    transaction_date: new Date().toISOString().split('T')[0]
  });
  const [newBaseCurrency, setNewBaseCurrency] = useState('USD');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [revalAsOf, setRevalAsOf] = useState(new Date().toISOString().split('T')[0]);
  const [revalPreview, setRevalPreview] = useState(null);

  const currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY'];

  useEffect(() => {
    loadBaseCurrency();
    loadExposureData();
  }, []);

  const loadBaseCurrency = async () => {
    try {
      const data = await apiClient.getBaseCurrency();
      setBaseCurrency(data.base_currency);
      setNewBaseCurrency(data.base_currency);
    } catch (error) {
      console.error('Error loading base currency:', error);
    }
  };

  const loadExposureData = async () => {
    setLoading(true);
    try {
      const data = await apiClient.getValuationExposure();
      setExposureData(data.exposure_data || []);
    } catch (error) {
      console.error('Error loading exposure data:', error);
      setSnackbar({ open: true, message: 'Failed to load foreign exchange exposure data', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const loadRevalPreview = async () => {
    try {
      const data = await apiClient.get(`/api/finance/fx/revaluation/preview?as_of=${revalAsOf}`);
      setRevalPreview(data);
    } catch (error) {
      setRevalPreview(null);
      setSnackbar({ open: true, message: 'Failed to load revaluation preview', severity: 'error' });
    }
  };

  const handleValuationSubmit = async () => {
    try {
      const result = await apiClient.calculatePurchaseValuation(valuationData);
        setSnackbar({ open: true, message: 'Purchase valuation calculated successfully', severity: 'success' });
        setValuationDialog(false);
        setValuationData({
          product_id: '',
          quantity: '',
          unit_cost: '',
          currency: 'USD',
          transaction_date: new Date().toISOString().split('T')[0]
        });
      } else {
        setSnackbar({ open: true, message: result.error || 'Failed to calculate valuation', severity: 'error' });
      }
    } catch (error) {
      console.error('Error calculating valuation:', error);
      setSnackbar({ open: true, message: 'Failed to calculate valuation', severity: 'error' });
    }
  };

  const handleBaseCurrencyChange = async () => {
    try {
      await apiClient.setBaseCurrency({ base_currency: newBaseCurrency });
      setBaseCurrency(newBaseCurrency);
      setSettingsDialog(false);
      setSnackbar({ open: true, message: 'Base currency updated successfully', severity: 'success' });
      loadExposureData(); // Refresh exposure data
    } catch (error) {
      console.error('Error updating base currency:', error);
      setSnackbar({ open: true, message: 'Failed to update base currency', severity: 'error' });
    }
  };

  const calculateTotalExposure = () => {
    return exposureData.reduce((total, item) => total + item.total_exposure_foreign, 0);
  };

  const calculateTotalUnrealizedGainLoss = () => {
    return exposureData.reduce((total, item) => total + item.unrealized_gain_loss, 0);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CurrencyExchange color="primary" />
        Multi-Currency Valuation Engine
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Base Currency
              </Typography>
              <Typography variant="h5" component="div">
                {baseCurrency}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Exposure
              </Typography>
              <Typography variant="h5" component="div">
                {calculateTotalExposure().toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Unrealized G/L
              </Typography>
              <Typography 
                variant="h5" 
                component="div"
                color={calculateTotalUnrealizedGainLoss() >= 0 ? 'success.main' : 'error.main'}
              >
                {calculateTotalUnrealizedGainLoss().toFixed(2)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Products with FX Exposure
              </Typography>
              <Typography variant="h5" component="div">
                {exposureData.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          startIcon={<Calculate />}
          onClick={() => setValuationDialog(true)}
        >
          Calculate Purchase Valuation
        </Button>
        <Button
          variant="outlined"
          startIcon={<Assessment />}
          onClick={() => setExposureDialog(true)}
        >
          View FX Exposure Report
        </Button>
        <Button
          variant="outlined"
          startIcon={<Settings />}
          onClick={() => setSettingsDialog(true)}
        >
          Base Currency Settings
        </Button>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={loadExposureData}
          disabled={loading}
        >
          Refresh Data
        </Button>
        <TextField
          type="date"
          label="Reval As Of"
          value={revalAsOf}
          onChange={(e) => setRevalAsOf(e.target.value)}
          size="small"
        />
        <Button variant="outlined" onClick={loadRevalPreview}>FX Reval Preview</Button>
      </Box>

      {/* Foreign Exchange Exposure Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Foreign Exchange Exposure
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Product</TableCell>
                  <TableCell>SKU</TableCell>
                  <TableCell>Currency</TableCell>
                  <TableCell align="right">Quantity</TableCell>
                  <TableCell align="right">Unit Cost (Foreign)</TableCell>
                  <TableCell align="right">Total Exposure (Foreign)</TableCell>
                  <TableCell align="right">Total Value ({baseCurrency})</TableCell>
                  <TableCell align="right">Exchange Rate</TableCell>
                  <TableCell align="right">Unrealized G/L</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {exposureData.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell>{item.product_name}</TableCell>
                    <TableCell>{item.product_sku}</TableCell>
                    <TableCell>
                      <Chip label={item.cost_currency} size="small" />
                    </TableCell>
                    <TableCell align="right">{item.quantity_on_hand}</TableCell>
                    <TableCell align="right">{item.unit_cost_foreign.toFixed(2)}</TableCell>
                    <TableCell align="right">{item.total_exposure_foreign.toFixed(2)}</TableCell>
                    <TableCell align="right">{item.total_value_base.toFixed(2)}</TableCell>
                    <TableCell align="right">{item.exchange_rate.toFixed(4)}</TableCell>
                    <TableCell align="right">
                      <Chip
                        label={item.unrealized_gain_loss.toFixed(2)}
                        color={item.unrealized_gain_loss >= 0 ? 'success' : 'error'}
                        size="small"
                        icon={item.unrealized_gain_loss >= 0 ? <TrendingUp /> : <TrendingDown />}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {revalPreview && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>FX Revaluation Preview</Typography>
            <Typography variant="body2" color="text.secondary">As of {revalPreview.as_of} (base {revalPreview.base_currency})</Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={4}><Chip label={`AR G/L: ${revalPreview.ar_unrealized_gl?.toFixed?.(2) || revalPreview.ar_unrealized_gl || 0}`} color="info" /></Grid>
              <Grid item xs={12} md={4}><Chip label={`AP G/L: ${revalPreview.ap_unrealized_gl?.toFixed?.(2) || revalPreview.ap_unrealized_gl || 0}`} color="warning" /></Grid>
              <Grid item xs={12} md={4}><Chip label={`Cash G/L: ${revalPreview.cash_unrealized_gl?.toFixed?.(2) || revalPreview.cash_unrealized_gl || 0}`} color="success" /></Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Purchase Valuation Dialog */}
      <Dialog open={valuationDialog} onClose={() => setValuationDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Calculate Purchase Valuation</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Product ID"
                value={valuationData.product_id}
                onChange={(e) => setValuationData({ ...valuationData, product_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Quantity"
                type="number"
                value={valuationData.quantity}
                onChange={(e) => setValuationData({ ...valuationData, quantity: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Unit Cost"
                type="number"
                value={valuationData.unit_cost}
                onChange={(e) => setValuationData({ ...valuationData, unit_cost: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Currency</InputLabel>
                <Select
                  value={valuationData.currency}
                  onChange={(e) => setValuationData({ ...valuationData, currency: e.target.value })}
                >
                  {currencies.map((currency) => (
                    <MenuItem key={currency} value={currency}>{currency}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Transaction Date"
                type="date"
                value={valuationData.transaction_date}
                onChange={(e) => setValuationData({ ...valuationData, transaction_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setValuationDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleValuationSubmit}>
            Calculate
          </Button>
        </DialogActions>
      </Dialog>

      {/* Base Currency Settings Dialog */}
      <Dialog open={settingsDialog} onClose={() => setSettingsDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Base Currency Settings</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Changing the base currency will affect all multi-currency calculations and may require revaluation of existing inventory.
          </Alert>
          <FormControl fullWidth>
            <InputLabel>Base Currency</InputLabel>
            <Select
              value={newBaseCurrency}
              onChange={(e) => setNewBaseCurrency(e.target.value)}
            >
              {currencies.map((currency) => (
                <MenuItem key={currency} value={currency}>{currency}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleBaseCurrencyChange}>
            Update Base Currency
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
    </Box>
  );
};

export default MultiCurrencyValuation;
