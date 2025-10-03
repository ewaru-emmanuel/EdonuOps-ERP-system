import React, { useState, useEffect, useMemo } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Autocomplete, SpeedDial, SpeedDialAction, SpeedDialIcon,
  TablePagination, TableSortLabel, InputAdornment, OutlinedInput, FormHelperText, Collapse, List, ListItem, ListItemText, ListItemIcon,
  Checkbox, FormControlLabel, FormGroup, Badge, Avatar, Divider, Accordion, AccordionSummary, AccordionDetails,
  Slider, Switch, Rating, ToggleButton, ToggleButtonGroup, Skeleton, Backdrop, Modal, Fade, Grow, Zoom, Slide
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb,
  CloudUpload, Description, ReceiptLong, PaymentOutlined, ScheduleSend, AutoFixHigh, SmartToy, QrCode, CameraAlt,
  Email, Send, CreditCard, AccountBalanceWallet as WalletIcon, TrendingUp as TrendingUpIcon, CalendarToday,
  Timeline as TimelineIcon, ShowChart as ShowChartIcon, TrendingUp as TrendingUpIcon2, CompareArrows, ScatterPlot,
  Assessment as AssessmentIcon, Analytics, Timeline as TimelineIcon2, ShowChart as ShowChartIcon2, TrendingUp as TrendingUpIcon3,
  PictureAsPdf, TableChart, BarChart as BarChartIcon, PieChart as PieChartIcon, ShowChart as ShowChartIcon3,
  GetApp, Share, Print, Visibility as VisibilityIcon, Edit as EditIcon, Download as DownloadIcon, Inventory, Store, LocalShipping, Category, Warehouse
} from '@mui/icons-material';
import { useCurrency } from '../../../components/GlobalCurrencySettings';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const SmartInventoryReports = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const { formatCurrency } = useCurrency();
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectedReport, setSelectedReport] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [reportPeriod, setReportPeriod] = useState('current_month');
  const [comparisonPeriod, setComparisonPeriod] = useState('previous_month');
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [drillDownOpen, setDrillDownOpen] = useState(false);
  const [drillDownData, setDrillDownData] = useState(null);
  const [viewPeriod, setViewPeriod] = useState('daily'); // daily, weekly, monthly
  const [selectedDate, setSelectedDate] = useState(new Date());

  // Debug: Check current user context
  const currentUserId = localStorage.getItem('userId');
  const currentUserEmail = localStorage.getItem('userEmail');
  console.log('🔍 Inventory Reports - Current User Context:', {
    userId: currentUserId,
    userEmail: currentUserEmail
  });

  // Data hooks - inventory specific - REAL API CALLS
  const { data: inventoryKpiData, loading: kpiLoading, error: kpiError } = useRealTimeData('/api/inventory/core/reports/kpis');
  const { data: stockLevelsData, loading: stockLoading, error: stockError } = useRealTimeData('/api/inventory/core/reports/stock-levels');
  const { data: trendsData, loading: trendsLoading, error: trendsError } = useRealTimeData('/api/inventory/core/reports/trends');
  
  // Daily cycle data - REAL API CALLS
  const { data: dailyCycleSummary, loading: cycleLoading, error: cycleError } = useRealTimeData('/api/inventory/daily-cycle/summary');
  const { data: dailyBalancesData, loading: balancesLoading, error: balancesError } = useRealTimeData('/api/inventory/daily-cycle/balances');
  const { data: cycleHistoryData, loading: historyLoading, error: historyError } = useRealTimeData('/api/inventory/daily-cycle/history?start_date=2025-09-01&end_date=2025-10-02');
  
  const procurementData = [];
  const procurementLoading = false;
  const procurementError = null;
  
  const salesData = [];
  const salesLoading = false;
  const salesError = null;

  // Calculate comprehensive inventory metrics from REAL API DATA including daily cycles
  const metrics = useMemo(() => {
    console.log('📊 Inventory Reports - Processing real API data:', {
      inventoryKpiData,
      stockLevelsData,
      dailyCycleSummary,
      dailyBalancesData,
      kpiLoading,
      stockLoading,
      cycleLoading
    });
    
    console.log('📊 Raw API responses:', {
      inventoryKpiDataRaw: inventoryKpiData,
      stockLevelsDataRaw: stockLevelsData,
      dailyCycleSummaryRaw: dailyCycleSummary,
      dailyBalancesDataRaw: dailyBalancesData
    });

    // Use real API data
    const kpiData = inventoryKpiData?.data || {};
    const stockData = stockLevelsData?.data || []; // Fixed: was looking for report_data, should be data
    const cycleData = dailyCycleSummary?.data || {};
    const balancesData = dailyBalancesData?.data?.balances || [];
    
    console.log('📊 Processed data structures:', {
      kpiData,
      stockData,
      cycleData,
      balancesData
    });
    
    // Basic KPIs from API
    const totalProducts = kpiData.total_products || 0;
    const totalStockValue = kpiData.total_stock_value || 0;
    const lowStockItems = kpiData.low_stock_items || 0;
    const outOfStockItems = kpiData.out_of_stock_items || 0;
    const averageStockLevel = kpiData.average_stock_level || 0;
    
    console.log('📊 Extracted KPI values:', {
      totalProducts,
      totalStockValue,
      lowStockItems,
      outOfStockItems,
      averageStockLevel
    });
    
    // Calculate total quantity from stock data
    const totalQuantityOnHand = stockData.reduce((sum, item) => sum + (item.quantity_on_hand || 0), 0);
    
    // Daily cycle metrics
    const totalReceipts = balancesData.reduce((sum, balance) => sum + (balance.quantity_received || 0), 0);
    const totalIssues = balancesData.reduce((sum, balance) => sum + (balance.quantity_issued || 0), 0);
    const totalAdjustments = balancesData.reduce((sum, balance) => sum + (balance.quantity_adjusted || 0), 0);
    const netMovement = totalReceipts - totalIssues;
    
    // Calculate inventory turnover using daily cycle data
    const inventoryTurnover = totalStockValue > 0 ? (totalIssues * 365) / totalStockValue : 0;
    const daysInInventory = inventoryTurnover > 0 ? 365 / inventoryTurnover : 0;
    
    // Stock accuracy from adjustments
    const stockAccuracy = totalQuantityOnHand > 0 ? 
      Math.max(0, ((totalQuantityOnHand - Math.abs(totalAdjustments)) / totalQuantityOnHand) * 100) : 100;
    
    // Movement ratios from real data
    const receiptToIssueRatio = totalIssues > 0 ? totalReceipts / totalIssues : 0;
    const adjustmentRate = totalQuantityOnHand > 0 ? (Math.abs(totalAdjustments) / totalQuantityOnHand) * 100 : 0;
    
    console.log('📊 Calculated metrics with daily cycle data:', {
      totalProducts,
      totalStockValue,
      lowStockItems,
      totalQuantityOnHand,
      totalReceipts,
      totalIssues,
      totalAdjustments,
      inventoryTurnover,
      daysInInventory,
      stockAccuracy
    });
    
    return {
      // INVENTORY METRICS (not cash values)
      totalProducts,
      totalStockValue,
      lowStockItems,
      outOfStockItems,
      totalQuantityOnHand,
      totalInventoryValue: totalStockValue,
      averageStockLevel,
      
      // INVENTORY MOVEMENTS (quantities, not cash)
      totalReceipts,
      totalIssues,
      totalAdjustments,
      netMovement,
      
      // INVENTORY PERFORMANCE METRICS
      inventoryTurnover: Number(inventoryTurnover.toFixed(2)),
      daysInInventory: Number(daysInInventory.toFixed(0)),
      stockAccuracy: Number(stockAccuracy.toFixed(1)),
      receiptToIssueRatio: Number(receiptToIssueRatio.toFixed(2)),
      adjustmentRate: Number(adjustmentRate.toFixed(2)),
      
      // INVENTORY HEALTH INDICATORS
      stockHealthScore: stockAccuracy > 95 ? 'Excellent' : 
                       stockAccuracy > 90 ? 'Good' : 
                       stockAccuracy > 85 ? 'Fair' : 'Poor',
      turnoverHealth: inventoryTurnover > 12 ? 'Excellent' :
                     inventoryTurnover > 6 ? 'Good' :
                     inventoryTurnover > 3 ? 'Fair' : 'Poor',
    };
  }, [inventoryKpiData, stockLevelsData, dailyCycleSummary, dailyBalancesData]);

  // Daily inventory data processing from REAL CYCLE HISTORY DATA
  const dailyInventoryData = useMemo(() => {
    const cycles = cycleHistoryData?.data?.cycles || [];
    
    if (!cycles.length) {
      // If no cycle data, create mock data for today
      const today = new Date().toISOString().split('T')[0];
      return [{
        date: today,
        dateLabel: new Date(today).toLocaleDateString('en-US', { 
          month: 'numeric', day: 'numeric', year: 'numeric' 
        }),
        isToday: true,
        openingValue: 0,
        closingValue: 0,
        totalQuantity: 0,
        totalProducts: 0,
        status: 'No Data',
        movements: {
          receipts: 0,
          issues: 0,
          adjustments: 0,
          transfers: 0
        }
      }];
    }

    return cycles.slice(0, 7).map(cycle => ({
      date: cycle.cycle_date,
      dateLabel: new Date(cycle.cycle_date).toLocaleDateString('en-US', { 
        month: 'numeric', day: 'numeric', year: 'numeric' 
      }),
      isToday: cycle.cycle_date === new Date().toISOString().split('T')[0],
      openingValue: cycle.total_inventory_value || 0,
      closingValue: cycle.total_inventory_value || 0,
      totalQuantity: cycle.total_quantity_on_hand || 0,
      totalProducts: cycle.total_products || 0,
      status: cycle.is_complete ? 'Complete' : 'Pending',
      movements: {
        receipts: 0, // Would come from transaction summaries
        issues: 0,
        adjustments: 0,
        transfers: 0
      }
    }));
  }, [cycleHistoryData]);

  // Top products by value from REAL STOCK DATA - CONSOLIDATED
  const topProductsData = useMemo(() => {
    const stockData = stockLevelsData?.data || []; // Fixed: was looking for report_data, should be data
    
    if (!stockData.length) return [];

    // Consolidate duplicate products by product_id
    const consolidatedProducts = {};
    
    stockData.forEach(item => {
      const productId = item.product_id;
      
      if (!consolidatedProducts[productId]) {
        // First occurrence of this product
        consolidatedProducts[productId] = {
          productId: item.product_id,
          productName: item.product_name || `Product ${item.product_id}`,
          sku: item.sku || 'N/A',
          quantity: item.quantity_on_hand || 0,
          unitCost: item.unit_cost || 0,
          totalValue: item.total_value || 0,
          netChange: 0, // Would need historical data
          warehouse: item.warehouse_name || 'Main',
          costMethod: item.cost_method || 'FIFO',
          category: item.category || 'Unknown'
        };
      } else {
        // Consolidate with existing product
        const existing = consolidatedProducts[productId];
        existing.quantity += (item.quantity_on_hand || 0);
        existing.totalValue += (item.total_value || 0);
        // Recalculate unit cost as weighted average
        existing.unitCost = existing.totalValue / existing.quantity;
      }
    });

    // Convert to array and sort by total value
    return Object.values(consolidatedProducts)
      .filter(item => item.totalValue > 0)
      .sort((a, b) => b.totalValue - a.totalValue)
      .slice(0, 10);
  }, [stockLevelsData]);

  const loading = kpiLoading || stockLoading || trendsLoading || cycleLoading || balancesLoading || historyLoading;
  const hasError = kpiError || stockError || trendsError || cycleError || balancesError || historyError;

  if (hasError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          Error loading inventory reports: {kpiError || stockError || trendsError}
        </Alert>
        <Button
          variant="contained"
          startIcon={<Refresh />}
          onClick={() => window.location.reload()}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Skeleton variant="text" width="40%" height={40} />
        <Grid container spacing={3} sx={{ mt: 2 }}>
          {[1, 2, 3, 4].map(i => (
            <Grid item xs={12} sm={6} md={3} key={i}>
              <Skeleton variant="rectangular" height={120} />
            </Grid>
          ))}
        </Grid>
        <Skeleton variant="rectangular" height={400} sx={{ mt: 3 }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', color: theme.palette.primary.main }}>
          Smart Inventory Reports & Analytics
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => window.location.reload()}
          >
            Refresh Data
          </Button>
          <Button
            variant="contained"
            startIcon={<Download />}
            onClick={() => setSnackbar({ open: true, message: 'Export feature coming soon!', severity: 'info' })}
          >
            Export Reports
          </Button>
        </Box>
      </Box>

      {/* Key Performance Indicators */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
        Inventory KPIs & Metrics
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: theme.palette.primary.light, color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {metrics.totalProducts || '0'}
                  </Typography>
                  <Typography variant="body2">Total Products</Typography>
                  <Typography variant="caption">
                    📦 INVENTORY ITEMS
                  </Typography>
                </Box>
                <Inventory sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: theme.palette.success.light, color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {metrics.totalQuantityOnHand?.toLocaleString() || '0'}
                  </Typography>
                  <Typography variant="body2">Total Stock Units</Typography>
                  <Typography variant="caption">
                    📦 {metrics.totalProducts || 0} Products
                  </Typography>
                </Box>
                <Store sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: theme.palette.info.light, color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {metrics.lowStockItems || '0'}
                  </Typography>
                  <Typography variant="body2">Low Stock Items</Typography>
                  <Typography variant="caption">
                    ⚠️ Need Reorder
                  </Typography>
                </Box>
                <Warning sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: theme.palette.warning.light, color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {metrics.outOfStockItems || '0'}
                  </Typography>
                  <Typography variant="body2">Out of Stock</Typography>
                  <Typography variant="caption">
                    🚫 Zero Inventory
                  </Typography>
                </Box>
                <Error sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Daily Inventory Summary - STOCK MOVEMENTS */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
        Daily Stock Movements
      </Typography>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Daily inventory stock movements and quantities • Shows actual inventory items, not cash values
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Opening Stock</TableCell>
                  <TableCell align="right">Stock Received</TableCell>
                  <TableCell align="right">Stock Issued</TableCell>
                  <TableCell align="right">Stock Adjusted</TableCell>
                  <TableCell align="right">Closing Stock</TableCell>
                  <TableCell align="right">Net Change</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {dailyInventoryData.map((day, index) => (
                  <TableRow key={day.date} sx={{ bgcolor: day.isToday ? theme.palette.action.selected : 'inherit' }}>
                    <TableCell>
                      {day.dateLabel}
                    </TableCell>
                    <TableCell align="right">{day.totalQuantity?.toLocaleString() || '0'} units</TableCell>
                    <TableCell align="right" sx={{ color: theme.palette.success.main }}>
                      +{day.movements.receipts.toLocaleString()} units
                    </TableCell>
                    <TableCell align="right" sx={{ color: theme.palette.error.main }}>
                      -{day.movements.issues.toLocaleString()} units
                    </TableCell>
                    <TableCell align="right" sx={{ color: theme.palette.warning.main }}>
                      {day.movements.adjustments.toLocaleString()} units
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                      {day.totalQuantity?.toLocaleString() || '0'} units
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      color: (day.movements.receipts - day.movements.issues) >= 0 ? theme.palette.success.main : theme.palette.error.main 
                    }}>
                      {(day.movements.receipts - day.movements.issues) >= 0 ? '+' : ''}{(day.movements.receipts - day.movements.issues).toLocaleString()} units
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={day.status} 
                        size="small" 
                        color={day.status === 'Complete' ? 'success' : 'warning'} 
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Current Inventory Items */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
        Current Inventory Items
      </Typography>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Real inventory items with current stock levels and quantities
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Product</TableCell>
                  <TableCell>SKU</TableCell>
                  <TableCell align="right">Stock Quantity</TableCell>
                  <TableCell align="right">Unit Cost</TableCell>
                  <TableCell align="right">Total Value</TableCell>
                  <TableCell align="right">Reorder Point</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {topProductsData.map((product, index) => (
                  <TableRow key={product.productId}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: theme.palette.primary.light }}>
                          {index + 1}
                        </Avatar>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {product.productName}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{product.sku}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                      {product.quantity.toLocaleString()} units
                    </TableCell>
                    <TableCell align="right">{formatCurrency(product.unitCost)}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                      {formatCurrency(product.totalValue)}
                    </TableCell>
                    <TableCell align="right">
                      {product.quantity <= 10 ? (
                        <Chip label="Low Stock" size="small" color="warning" />
                      ) : (
                        <Chip label="OK" size="small" color="success" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Chip label={product.category} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={product.quantity > 0 ? "In Stock" : "Out of Stock"} 
                        size="small" 
                        color={product.quantity > 0 ? "success" : "error"} 
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Inventory Performance Metrics */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
        Inventory Performance Metrics
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: theme.palette.primary.main }}>
                {metrics.inventoryTurnover}x
              </Typography>
              <Typography variant="body2">Stock Turnover Rate</Typography>
              <Typography variant="caption" color="text.secondary">
                How often inventory is sold
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: theme.palette.success.main }}>
                {metrics.daysInInventory}
              </Typography>
              <Typography variant="body2">Days in Stock</Typography>
              <Typography variant="caption" color="text.secondary">
                Average holding period
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: theme.palette.info.main }}>
                {metrics.stockAccuracy}%
              </Typography>
              <Typography variant="body2">Stock Accuracy</Typography>
              <Typography variant="caption" color="text.secondary">
                Physical vs system count
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: theme.palette.warning.main }}>
                {metrics.averageStockLevel}
              </Typography>
              <Typography variant="body2">Avg Stock Level</Typography>
              <Typography variant="caption" color="text.secondary">
                Average units per product
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Report Actions */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', mt: 4 }}>
        <Button
          variant="outlined"
          startIcon={<Assessment />}
          onClick={() => setSnackbar({ open: true, message: 'Detailed analytics coming soon!', severity: 'info' })}
        >
          Detailed Analytics
        </Button>
        <Button
          variant="outlined"
          startIcon={<Download />}
          onClick={() => setSnackbar({ open: true, message: 'Export functionality coming soon!', severity: 'info' })}
        >
          Export to Excel
        </Button>
        <Button
          variant="outlined"
          startIcon={<Print />}
          onClick={() => window.print()}
        >
          Print Report
        </Button>
      </Box>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SmartInventoryReports;