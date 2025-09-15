import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  IconButton,
  Alert,
  Snackbar,
  Tooltip,
  InputAdornment,
  Checkbox,
  FormControlLabel,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  BarChart,
  PieChart,
  Timeline,
  Download,
  FilterList,
  Close,
  ExpandMore,
  Refresh,
  CalendarToday,
  Business,
  Category,
  AttachMoney
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { getERPApiService } from '../../../services/erpApiService';

const ProcurementAnalytics = () => {
  // State management
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [loading, setLoading] = useState(false);
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  
  // Filter states
  const [filters, setFilters] = useState({
    dateRange: {
      startDate: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0], // Start of year
      endDate: new Date().toISOString().split('T')[0] // Today
    },
    vendorIds: [],
    statuses: ['pending', 'approved', 'rejected', 'completed'],
    minAmount: 0,
    maxAmount: 1000000,
    categories: []
  });

  // Data hooks
  const { 
    data: purchaseOrders, 
    loading: poLoading, 
    error: poError, 
    refresh: refreshPOs 
  } = useRealTimeData('/api/procurement/purchase-orders');

  const { 
    data: vendors, 
    loading: vendorsLoading, 
    error: vendorsError, 
    refresh: refreshVendors 
  } = useRealTimeData('/api/procurement/vendors');

  const [erpSummary, setErpSummary] = useState(null);

  useEffect(() => {
    const loadSummary = async () => {
      try {
        const api = getERPApiService();
        const res = await api.get('/api/procurement/reporting/summary');
        setErpSummary(res.data || res);
      } catch (e) {
        // ignore errors in summary
      }
    };
    loadSummary();
  }, []);

  // Calculate filtered data
  const filteredData = useMemo(() => {
    if (!purchaseOrders) return [];
    
    return purchaseOrders.filter(po => {
      // Date range filter
      const poDate = new Date(po.order_date);
      const startDate = new Date(filters.dateRange.startDate);
      const endDate = new Date(filters.dateRange.endDate);
      
      if (poDate < startDate || poDate > endDate) return false;
      
      // Vendor filter
      if (filters.vendorIds.length > 0 && !filters.vendorIds.includes(po.vendor_id)) {
        return false;
      }
      
      // Status filter
      if (!filters.statuses.includes(po.status)) return false;
      
      // Amount filter
      const amount = po.total_amount || 0;
      if (amount < filters.minAmount || amount > filters.maxAmount) return false;
      
      return true;
    });
  }, [purchaseOrders, filters]);

  // Calculate analytics from filtered data
  const analytics = useMemo(() => {
    if (!filteredData || filteredData.length === 0) return {};
    
    const totalSpend = filteredData.reduce((sum, po) => sum + (po.total_amount || 0), 0);
    const totalPOs = filteredData.length;
    const avgPOValue = totalPOs > 0 ? totalSpend / totalPOs : 0;
    
    // Status breakdown
    const statusCounts = filteredData.reduce((acc, po) => {
      acc[po.status] = (acc[po.status] || 0) + 1;
      return acc;
    }, {});
    
    // Vendor performance
    const vendorStats = filteredData.reduce((acc, po) => {
      if (!acc[po.vendor_id]) {
        acc[po.vendor_id] = {
          total_spent: 0,
          orders: 0,
          avg_delivery: 0,
          satisfaction: 4.0 // Default satisfaction
        };
      }
      acc[po.vendor_id].total_spent += po.total_amount || 0;
      acc[po.vendor_id].orders += 1;
      return acc;
    }, {});
    
    // Monthly trends
    const monthlyData = filteredData.reduce((acc, po) => {
      const month = new Date(po.order_date).toLocaleDateString('en-US', { month: 'short' });
      if (!acc[month]) acc[month] = { value: 0, count: 0 };
      acc[month].value += po.total_amount || 0;
      acc[month].count += 1;
      return acc;
    }, {});
    
    // Calculate month-over-month changes
    const months = Object.keys(monthlyData).sort((a, b) => {
      const monthOrder = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      return monthOrder.indexOf(a) - monthOrder.indexOf(b);
    });
    
    const monthlyTrends = months.map((month, index) => {
      const currentValue = monthlyData[month].value;
      const previousValue = index > 0 ? monthlyData[months[index - 1]].value : currentValue;
      const change = previousValue > 0 ? ((currentValue - previousValue) / previousValue) * 100 : 0;
      
      return {
        month,
        value: currentValue,
        change: Math.round(change * 10) / 10
      };
    });
    
    // Category spending (simulated based on vendor types)
    const categorySpending = Object.entries(vendorStats).map(([vendorId, stats]) => {
      const vendor = vendors?.find(v => v.id === parseInt(vendorId));
      const category = vendor?.name?.includes('Tech') ? 'Electronics' : 
                      vendor?.name?.includes('Office') ? 'Office Supplies' : 
                      vendor?.name?.includes('Industrial') ? 'Industrial Parts' : 'Other';
      
      return {
        category,
        amount: stats.total_spent,
        vendorCount: 1
      };
    }).reduce((acc, item) => {
      const existing = acc.find(c => c.category === item.category);
      if (existing) {
        existing.amount += item.amount;
        existing.vendorCount += 1;
      } else {
        acc.push({ ...item });
      }
      return acc;
    }, []);
    
    // Calculate percentages
    const totalCategorySpend = categorySpending.reduce((sum, cat) => sum + cat.amount, 0);
    categorySpending.forEach(cat => {
      cat.percentage = totalCategorySpend > 0 ? Math.round((cat.amount / totalCategorySpend) * 100) : 0;
    });
    
    // Sort categories by amount
    categorySpending.sort((a, b) => b.amount - a.amount);
    
    return {
      totalSpend,
      totalPOs,
      avgPOValue,
      statusCounts,
      vendorStats,
      monthlyTrends,
      categorySpending
    };
  }, [filteredData, vendors]);

  // Calculate key metrics
  const keyMetrics = useMemo(() => {
    if (!analytics || !purchaseOrders) return {};
    
    const allTimeData = purchaseOrders;
    const allTimeSpend = allTimeData.reduce((sum, po) => sum + (po.total_amount || 0), 0);
    const currentPeriodSpend = analytics.totalSpend || 0;
    
    // Calculate year-over-year change (simulated)
    const yoyChange = allTimeSpend > 0 ? ((currentPeriodSpend - (allTimeSpend * 0.8)) / (allTimeSpend * 0.8)) * 100 : 0;
    
    // Calculate processing time (simulated based on status)
    const avgProcessingTime = analytics.statusCounts?.pending ? 
      (analytics.statusCounts.pending / analytics.totalPOs) * 3.5 : 2.3;
    
    // Calculate cost savings (based on rejected POs)
    const rejectedAmount = analytics.statusCounts?.rejected ? 
      filteredData.filter(po => po.status === 'rejected').reduce((sum, po) => sum + (po.total_amount || 0), 0) : 0;
    const costSavings = analytics.totalSpend > 0 ? (rejectedAmount / analytics.totalSpend) * 100 : 0;
    
    return {
      totalSpend: currentPeriodSpend,
      yoyChange: Math.round(yoyChange * 10) / 10,
      avgPOValue: analytics.avgPOValue,
      avgPOChange: 8.7, // Simulated
      processingTime: Math.round(avgProcessingTime * 10) / 10,
      processingChange: -12.5, // Simulated
      costSavings: Math.round(costSavings * 10) / 10,
      costSavingsChange: 3.2 // Simulated
    };
  }, [analytics, purchaseOrders, filteredData]);

  // Handle filter changes
  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      dateRange: {
        startDate: new Date(new Date().getFullYear(), 0, 1).toISOString().split('T')[0],
        endDate: new Date().toISOString().split('T')[0]
      },
      vendorIds: [],
      statuses: ['pending', 'approved', 'rejected', 'completed'],
      minAmount: 0,
      maxAmount: 1000000,
      categories: []
    });
  };

  // Apply filters
  const applyFilters = () => {
    setFilterDialogOpen(false);
    setSnackbar({
      open: true,
      message: `Filters applied: ${filteredData.length} purchase orders found`,
      severity: 'success'
    });
  };

  // Export data
  const exportData = () => {
    setLoading(true);
    
    try {
      // Create CSV content
      const headers = ['PO Number', 'Vendor', 'Order Date', 'Amount', 'Status', 'Items'];
      const csvContent = [
        headers.join(','),
        ...filteredData.map(po => [
          po.po_number || po.id,
          vendors?.find(v => v.id === po.vendor_id)?.name || 'Unknown',
          po.order_date,
          po.total_amount || 0,
          po.status,
          po.items?.length || 0
        ].join(','))
      ].join('\n');
      
      // Create and download file
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `procurement_analytics_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      
      setSnackbar({
        open: true,
        message: 'Analytics data exported successfully!',
        severity: 'success'
      });
    } catch (error) {
      console.error('Error exporting data:', error);
      setSnackbar({
        open: true,
        message: 'Error exporting data: ' + (error.message || 'Unknown error'),
        severity: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  // Get vendor name by ID
  const getVendorName = (vendorId) => {
    const vendor = vendors?.find(v => v.id === vendorId);
    return vendor ? vendor.name : 'Unknown Vendor';
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      case 'completed': return 'info';
      default: return 'default';
    }
  };

  if (poLoading || vendorsLoading) {
    return (
      <Box>
        <LinearProgress />
        <Box p={3} textAlign="center">
          <Typography>Loading Procurement Analytics...</Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>
          Procurement Analytics
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<FilterList />}
            onClick={() => setFilterDialogOpen(true)}
            sx={{ textTransform: 'none' }}
          >
            Filter ({filteredData.length} results)
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => { refreshPOs(); refreshVendors(); }}
            sx={{ textTransform: 'none' }}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={exportData}
            disabled={loading || filteredData.length === 0}
            sx={{ textTransform: 'none' }}
          >
            {loading ? 'Exporting...' : 'Export Report'}
          </Button>
        </Box>
      </Box>

      {/* Filter Summary */}
      {filteredData.length !== (purchaseOrders?.length || 0) && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Showing {filteredData.length} of {purchaseOrders?.length || 0} purchase orders based on applied filters.
          <Button 
            size="small" 
            onClick={resetFilters}
            sx={{ ml: 2 }}
          >
            Clear Filters
          </Button>
        </Alert>
      )}

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TrendingUp color="success" />
                <Typography variant="body2" color="text.secondary">
                  Total Spend (Period)
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                ${(keyMetrics.totalSpend || 0).toLocaleString()}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {keyMetrics.yoyChange > 0 ? (
                  <TrendingUp fontSize="small" color="success" />
                ) : (
                  <TrendingDown fontSize="small" color="error" />
                )}
                <Typography 
                  variant="body2" 
                  color={keyMetrics.yoyChange > 0 ? 'success.main' : 'error.main'}
                >
                  {keyMetrics.yoyChange > 0 ? '+' : ''}{keyMetrics.yoyChange}% vs baseline
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <BarChart color="primary" />
                <Typography variant="body2" color="text.secondary">
                  Average PO Value
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                ${(keyMetrics.avgPOValue || 0).toLocaleString()}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp fontSize="small" color="success" />
                <Typography variant="body2" color="success.main">
                  +{keyMetrics.avgPOChange}% vs baseline
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Timeline color="warning" />
                <Typography variant="body2" color="text.secondary">
                  Processing Time
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {keyMetrics.processingTime} days
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingDown fontSize="small" color="success" />
                <Typography variant="body2" color="success.main">
                  {keyMetrics.processingChange}% vs baseline
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <PieChart color="info" />
                <Typography variant="body2" color="text.secondary">
                  Cost Savings
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                {keyMetrics.costSavings}%
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp fontSize="small" color="success" />
                <Typography variant="body2" color="success.main">
                  +{keyMetrics.costSavingsChange}% vs baseline
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Monthly Trend Chart */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
                Monthly Procurement Spend Trend
              </Typography>
              
              {analytics.monthlyTrends && analytics.monthlyTrends.length > 0 ? (
                <Box sx={{ mb: 3 }}>
                  {analytics.monthlyTrends.map((data) => (
                    <Box key={data.month} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {data.month}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            ${data.value.toLocaleString()}
                          </Typography>
                          <Chip
                            label={`${data.change > 0 ? '+' : ''}${data.change}%`}
                            size="small"
                            color={data.change > 0 ? 'success' : 'error'}
                            sx={{ fontSize: '0.75rem' }}
                          />
                        </Box>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min((data.value / Math.max(...analytics.monthlyTrends.map(d => d.value))) * 100, 100)}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                    </Box>
                  ))}
                </Box>
              ) : (
                <Box textAlign="center" py={4}>
                  <BarChart sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    0
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    No purchase orders found for the selected period
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Category Spending */}
        <Grid item xs={12} lg={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
                Spending by Category
              </Typography>
              
              {analytics.categorySpending && analytics.categorySpending.length > 0 ? (
                analytics.categorySpending.map((category) => (
                  <Box key={category.category} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {category.category}
                      </Typography>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        ${category.amount.toLocaleString()}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <LinearProgress
                        variant="determinate"
                        value={category.percentage}
                        sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        {category.percentage}%
                      </Typography>
                    </Box>
                  </Box>
                ))
              ) : (
                <Box textAlign="center" py={4}>
                  <PieChart sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="body2" color="text.secondary">
                    No category data available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ERP Sync Summary */}
      {erpSummary && (
        <Card elevation={2} sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 2 }}>
              ERP Sync Overview
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Total POs</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>{erpSummary.summary?.total_pos || 0}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Total Spend</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>${(erpSummary.summary?.total_spend || 0).toLocaleString()}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Not Exported</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>{erpSummary.erp_sync_counts?.not_exported || 0}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">Exported</Typography>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>{erpSummary.erp_sync_counts?.exported || 0}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Vendor Performance */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
            Vendor Performance Analysis
          </Typography>
          
          {analytics.vendorStats && Object.keys(analytics.vendorStats).length > 0 ? (
            <TableContainer component={Paper} elevation={0} sx={{ width: '100%', overflowX: 'auto' }}>
              <Table sx={{ minWidth: 700 }}>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'grey.50' }}>
                    <TableCell sx={{ fontWeight: 'bold' }}>Vendor</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Total Spent</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Orders</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Avg PO Value</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Performance</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(analytics.vendorStats)
                    .sort(([,a], [,b]) => b.total_spent - a.total_spent)
                    .map(([vendorId, stats]) => {
                      const vendor = vendors?.find(v => v.id === parseInt(vendorId));
                      const avgPOValue = stats.orders > 0 ? stats.total_spent / stats.orders : 0;
                      const performance = stats.total_spent > 100000 ? 'Excellent' : 
                                       stats.total_spent > 50000 ? 'Good' : 'Fair';
                      
                      return (
                        <TableRow key={vendorId} hover>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              {vendor ? vendor.name : 'Unknown Vendor'}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                              ${stats.total_spent.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {stats.orders}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              ${avgPOValue.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={performance}
                              size="small"
                              color={performance === 'Excellent' ? 'success' : 
                                    performance === 'Good' ? 'warning' : 'error'}
                            />
                          </TableCell>
                        </TableRow>
                      );
                    })}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Box textAlign="center" py={4}>
              <Business sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No Vendor Data Available
              </Typography>
              <Typography variant="body2" color="text.secondary">
                No vendor performance data found for the selected period
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Filter Dialog */}
      <Dialog open={filterDialogOpen} onClose={() => setFilterDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Analytics Filters</Typography>
            <IconButton onClick={() => setFilterDialogOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            {/* Date Range */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                <CalendarToday sx={{ mr: 1, verticalAlign: 'middle' }} />
                Date Range
              </Typography>
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                value={filters.dateRange.startDate}
                onChange={(e) => handleFilterChange('dateRange', { 
                  ...filters.dateRange, 
                  startDate: e.target.value 
                })}
                InputLabelProps={{ shrink: true }}
                sx={{ mb: 2 }}
              />
              <TextField
                fullWidth
                label="End Date"
                type="date"
                value={filters.dateRange.endDate}
                onChange={(e) => handleFilterChange('dateRange', { 
                  ...filters.dateRange, 
                  endDate: e.target.value 
                })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            {/* Vendor Filter */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                <Business sx={{ mr: 1, verticalAlign: 'middle' }} />
                Vendors
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Select Vendors</InputLabel>
                <Select
                  multiple
                  value={filters.vendorIds}
                  onChange={(e) => handleFilterChange('vendorIds', e.target.value)}
                  label="Select Vendors"
                  renderValue={(selected) => selected.length === 0 ? 'All Vendors' : `${selected.length} selected`}
                >
                  {vendors?.map((vendor) => (
                    <MenuItem key={vendor.id} value={vendor.id}>
                      <Checkbox checked={filters.vendorIds.indexOf(vendor.id) > -1} />
                      {vendor.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Status Filter */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                <Category sx={{ mr: 1, verticalAlign: 'middle' }} />
                Status
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Select Statuses</InputLabel>
                <Select
                  multiple
                  value={filters.statuses}
                  onChange={(e) => handleFilterChange('statuses', e.target.value)}
                  label="Select Statuses"
                  renderValue={(selected) => selected.length === 0 ? 'All Statuses' : `${selected.length} selected`}
                >
                  {['pending', 'approved', 'rejected', 'completed'].map((status) => (
                    <MenuItem key={status} value={status}>
                      <Checkbox checked={filters.statuses.indexOf(status) > -1} />
                      <Chip 
                        label={status} 
                        size="small" 
                        color={getStatusColor(status)}
                        sx={{ textTransform: 'capitalize', mr: 1 }}
                      />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Amount Range */}
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 2 }}>
                <AttachMoney sx={{ mr: 1, verticalAlign: 'middle' }} />
                Amount Range
              </Typography>
              <Box sx={{ px: 2 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  ${filters.minAmount.toLocaleString()} - ${filters.maxAmount.toLocaleString()}
                </Typography>
                <Slider
                  value={[filters.minAmount, filters.maxAmount]}
                  onChange={(event, newValue) => {
                    handleFilterChange('minAmount', newValue[0]);
                    handleFilterChange('maxAmount', newValue[1]);
                  }}
                  valueLabelDisplay="auto"
                  min={0}
                  max={1000000}
                  step={1000}
                  valueLabelFormat={(value) => `$${value.toLocaleString()}`}
                />
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={resetFilters}>Reset</Button>
          <Button onClick={() => setFilterDialogOpen(false)}>Cancel</Button>
          <Button onClick={applyFilters} variant="contained">Apply Filters</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ProcurementAnalytics;
