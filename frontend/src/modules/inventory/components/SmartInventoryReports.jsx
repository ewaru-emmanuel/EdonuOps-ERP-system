import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, Grid, Card, CardContent, Button, Chip,
  Alert, CircularProgress, FormControl, InputLabel, Select, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { apiClient } from '../../../utils/apiClient';

const SmartInventoryReports = () => {
  const [selectedReport, setSelectedReport] = useState('overview');
  const { data: kpis, loading: kpisLoading } = useRealTimeData('/api/inventory/core/reports/kpis');
  const { data: stockLevels, loading: stockLoading } = useRealTimeData('/api/inventory/core/reports/stock-levels');
  const { data: trends, loading: trendsLoading } = useRealTimeData('/api/inventory/core/reports/trends');

  const loading = kpisLoading || stockLoading || trendsLoading;
  const [gaps, setGaps] = useState([]);
  const [resolveOpen, setResolveOpen] = useState(false);
  const [mapForm, setMapForm] = useState({ po_number: '', item_id: '', product_id: '' });

  const loadGaps = async () => {
    try {
      const data = await apiClient.get('/api/procurement/integration/gaps');
      setGaps(data.gaps || []);
    } catch {}
  };

  useEffect(() => { loadGaps(); }, []);

  const openResolve = (gap) => {
    setMapForm({ po_number: gap.po_number || '', item_id: gap.item_id || '', product_id: '' });
    setResolveOpen(true);
  };

  const submitMapping = async () => {
    try {
      await apiClient.post('/api/procurement/purchase-orders/map-item-product', mapForm);
      setResolveOpen(false);
      setMapForm({ po_number: '', item_id: '', product_id: '' });
      loadGaps();
    } catch {}
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Inventory Reports
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track performance and analyze your inventory data
        </Typography>
      </Box>

      {gaps.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Some received PO items are missing product mapping. Please resolve.
          <Box sx={{ mt: 1 }}>
            {gaps.slice(0, 5).map((g, i) => (
              <Box key={i} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Typography variant="body2">PO {g.po_number} · Item {g.item_id}</Typography>
                <Button size="small" onClick={() => openResolve(g)}>Resolve</Button>
              </Box>
            ))}
            {gaps.length > 5 && <Typography variant="caption">+{gaps.length - 5} more…</Typography>}
          </Box>
        </Alert>
      )}

      {/* Report Type Selector */}
      <Box sx={{ mb: 3 }}>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Report Type</InputLabel>
          <Select
            value={selectedReport}
            label="Report Type"
            onChange={(e) => setSelectedReport(e.target.value)}
          >
            <MenuItem value="overview">Overview Dashboard</MenuItem>
            <MenuItem value="stock">Stock Levels Report</MenuItem>
            <MenuItem value="trends">Trends Analysis</MenuItem>
            <MenuItem value="low-stock">Low Stock Report</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Overview Dashboard */}
      {selectedReport === 'overview' && (
        <Grid container spacing={3}>
          {/* KPIs */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Key Performance Indicators
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {kpis?.total_products || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Products
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="success.main">
                        ${(kpis?.total_stock_value || 0).toLocaleString()}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Total Stock Value
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="warning.main">
                        {kpis?.low_stock_items || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Low Stock Items
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="info.main">
                        {kpis?.turnover_rate || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Turnover Rate
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Performance Metrics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Performance Metrics
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Stock Accuracy</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {kpis?.stock_accuracy || 0}%
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Order Fulfillment</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {kpis?.order_fulfillment_rate || 0}%
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Warehouse Utilization</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {kpis?.warehouse_utilization || 0}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activity
                </Typography>
                <Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CheckCircleIcon sx={{ color: 'success.main', mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">
                      Stock count completed for 15 items
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <WarningIcon sx={{ color: 'warning.main', mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">
                      3 items reached reorder point
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <TrendingUpIcon sx={{ color: 'info.main', mr: 1, fontSize: 16 }} />
                    <Typography variant="body2">
                      Inventory value increased by 12%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Stock Levels Report */}
      {selectedReport === 'stock' && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Stock Levels Report
              </Typography>
              <Button startIcon={<DownloadIcon />} variant="outlined">
                Export Report
              </Button>
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {stockLevels?.length || 0} products in inventory
            </Typography>
            {/* Stock levels table would go here */}
            <Typography variant="body2" color="text.secondary">
              Detailed stock levels report with current quantities, reorder points, and status.
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Trends Analysis */}
      {selectedReport === 'trends' && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Inventory Trends
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Analyze inventory movement patterns and trends over time.
            </Typography>
            {/* Trends chart would go here */}
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <TrendingUpIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                Trends Analysis
              </Typography>
              <Typography variant="body2" color="text.secondary">
                View inventory movement trends and patterns
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Low Stock Report */}
      {selectedReport === 'low-stock' && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Low Stock Report
              </Typography>
              <Chip label={`${kpis?.low_stock_items || 0} items`} color="warning" />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Products that have reached or fallen below their reorder points.
            </Typography>
            {/* Low stock items table would go here */}
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <WarningIcon sx={{ fontSize: 48, color: 'warning.main', mb: 2 }} />
              <Typography variant="h6" color="warning.main">
                Low Stock Items
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {kpis?.low_stock_items || 0} items need reordering
              </Typography>
            </Box>
          </CardContent>
        </Card>
      )}

      <Dialog open={resolveOpen} onClose={() => setResolveOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Resolve Missing Product Mapping</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="PO Number" value={mapForm.po_number} onChange={(e) => setMapForm({ ...mapForm, po_number: e.target.value })} sx={{ mb: 2 }} />
          <TextField fullWidth label="PO Item ID" value={mapForm.item_id} onChange={(e) => setMapForm({ ...mapForm, item_id: e.target.value })} sx={{ mb: 2 }} />
          <TextField fullWidth label="Product ID" value={mapForm.product_id} onChange={(e) => setMapForm({ ...mapForm, product_id: e.target.value })} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResolveOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={submitMapping}>Save Mapping</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SmartInventoryReports;
