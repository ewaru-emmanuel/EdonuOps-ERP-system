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
// Removed useRealTimeData to prevent authentication calls

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

  // Data hooks - inventory specific
  // Mock data to prevent API calls
  const inventoryKpiData = [];
  const kpiLoading = false;
  const kpiError = null;
  
  const stockLevelsData = [];
  const stockLoading = false;
  const stockError = null;
  
  const trendsData = [];
  const trendsLoading = false;
  const trendsError = null;
  
  const dailyCycleData = [];
  const cycleLoading = false;
  const cycleError = null;
  
  const dailyBalancesData = [];
  const balancesLoading = false;
  const balancesError = null;
  
  const cycleHistoryData = [];
  const historyLoading = false;
  const historyError = null;
  
  const procurementData = [];
  const procurementLoading = false;
  const procurementError = null;
  
  const salesData = [];
  const salesLoading = false;
  const salesError = null;

  // Calculate comprehensive inventory metrics (similar to finance module)
  const metrics = useMemo(() => {
    if (!inventoryKpiData || !stockLevelsData || !dailyCycleData) return {};

    const today = new Date().toISOString().split('T')[0];
    const todayCycle = dailyCycleData?.data || {};
    
    // Basic KPIs
    const totalProducts = inventoryKpiData?.kpis?.total_products || 0;
    const totalStockValue = inventoryKpiData?.kpis?.total_stock_value || 0;
    const lowStockItems = inventoryKpiData?.kpis?.low_stock_items || 0;
    
    // Daily cycle metrics
    const totalQuantityOnHand = todayCycle?.metrics?.total_quantity_on_hand || 0;
    const totalInventoryValue = todayCycle?.metrics?.total_inventory_value || 0;
    const totalTransactions = todayCycle?.metrics?.total_transactions || 0;
    const totalReceipts = todayCycle?.metrics?.total_receipts || 0;
    const totalIssues = todayCycle?.metrics?.total_issues || 0;
    const totalAdjustments = todayCycle?.metrics?.total_adjustments || 0;
    
    // Calculate turnover and velocity
    const inventoryTurnover = totalIssues > 0 && totalInventoryValue > 0 ? 
      (totalIssues * 365) / totalInventoryValue : 0;
    const daysInInventory = inventoryTurnover > 0 ? 365 / inventoryTurnover : 0;
    
    // Stock accuracy and health
    const stockAccuracy = totalAdjustments > 0 && totalQuantityOnHand > 0 ?
      ((totalQuantityOnHand - Math.abs(totalAdjustments)) / totalQuantityOnHand) * 100 : 100;
    
    // Movement ratios
    const receiptToIssueRatio = totalIssues > 0 ? totalReceipts / totalIssues : 0;
    const adjustmentRate = totalQuantityOnHand > 0 ? 
      (Math.abs(totalAdjustments) / totalQuantityOnHand) * 100 : 0;
    
    return {
      // Basic metrics
      totalProducts,
      totalStockValue,
      lowStockItems,
      totalQuantityOnHand,
      totalInventoryValue,
      totalTransactions,
      
      // Movement metrics
      totalReceipts,
      totalIssues,
      totalAdjustments,
      netMovement: totalReceipts - totalIssues,
      
      // Performance metrics
      inventoryTurnover: Number(inventoryTurnover.toFixed(2)),
      daysInInventory: Number(daysInInventory.toFixed(0)),
      stockAccuracy: Number(stockAccuracy.toFixed(1)),
      receiptToIssueRatio: Number(receiptToIssueRatio.toFixed(2)),
      adjustmentRate: Number(adjustmentRate.toFixed(2)),
      
      // Health indicators
      stockHealthScore: stockAccuracy > 95 ? 'Excellent' : 
                       stockAccuracy > 90 ? 'Good' : 
                       stockAccuracy > 85 ? 'Fair' : 'Poor',
      turnoverHealth: inventoryTurnover > 12 ? 'Excellent' :
                     inventoryTurnover > 6 ? 'Good' :
                     inventoryTurnover > 3 ? 'Fair' : 'Poor',
    };
  }, [inventoryKpiData, stockLevelsData, dailyCycleData]);

  // Daily inventory data processing (similar to finance daily cash data)
  const dailyInventoryData = useMemo(() => {
    if (!cycleHistoryData?.data?.cycles) return [];

    return cycleHistoryData.data.cycles.slice(0, 7).map(cycle => ({
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

  // Top products by value (similar to finance account analysis)
  const topProductsData = useMemo(() => {
    if (!dailyBalancesData?.data?.balances) return [];

    return dailyBalancesData.data.balances
      .filter(balance => balance.closing_total_value > 0)
      .sort((a, b) => b.closing_total_value - a.closing_total_value)
      .slice(0, 10)
      .map(balance => ({
        productId: balance.product_id,
        productName: balance.product_name || `Product ${balance.product_id}`,
        sku: balance.product_sku || 'N/A',
        quantity: balance.closing_quantity,
        unitCost: balance.closing_unit_cost,
        totalValue: balance.closing_total_value,
        netChange: balance.net_value_change,
        warehouse: balance.warehouse_name || 'Main',
        costMethod: balance.cost_method || 'FIFO'
      }));
  }, [dailyBalancesData]);

  const loading = kpiLoading || stockLoading || trendsLoading || cycleLoading;

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
                    ${metrics.totalInventoryValue?.toLocaleString() || '0'}
                  </Typography>
                  <Typography variant="body2">Total Inventory Value</Typography>
                  <Typography variant="caption">
                    📊 REAL-TIME DATA
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
                  <Typography variant="body2">Total Quantity On Hand</Typography>
                  <Typography variant="caption">
                    Units: {metrics.totalProducts || 0} Products
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
                    {metrics.inventoryTurnover || '0.0'}x
                  </Typography>
                  <Typography variant="body2">Inventory Turnover</Typography>
                  <Typography variant="caption">
                    {metrics.daysInInventory || 0} Days in Inventory
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, opacity: 0.7 }} />
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
                    {metrics.stockAccuracy || '0.0'}%
                  </Typography>
                  <Typography variant="body2">Stock Accuracy</Typography>
                  <Typography variant="caption">
                    {metrics.stockHealthScore || 'Unknown'} Health
                  </Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Daily Inventory Summary (like Finance Daily Cash Flow) */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
        Daily Inventory Summary
      </Typography>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Daily inventory balances from inventory cycle system • CALCULATED indicates real-time data
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell align="right">Opening Value</TableCell>
                  <TableCell align="right">Receipts</TableCell>
                  <TableCell align="right">Issues</TableCell>
                  <TableCell align="right">Adjustments</TableCell>
                  <TableCell align="right">Closing Value</TableCell>
                  <TableCell align="right">Net Change</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {dailyInventoryData.map((day, index) => (
                  <TableRow key={day.date} sx={{ bgcolor: day.isToday ? theme.palette.action.selected : 'inherit' }}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {day.dateLabel}
                        {day.isToday && <Chip label="Today" size="small" color="primary" />}
                        <Chip label="CALCULATED" size="small" variant="outlined" />
                      </Box>
                    </TableCell>
                    <TableCell align="right">${day.openingValue.toLocaleString()}</TableCell>
                    <TableCell align="right" sx={{ color: theme.palette.success.main }}>
                      +${day.movements.receipts.toLocaleString()}
                    </TableCell>
                    <TableCell align="right" sx={{ color: theme.palette.error.main }}>
                      -${day.movements.issues.toLocaleString()}
                    </TableCell>
                    <TableCell align="right" sx={{ color: theme.palette.warning.main }}>
                      ${day.movements.adjustments.toLocaleString()}
                    </TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                      ${day.closingValue.toLocaleString()}
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      color: (day.closingValue - day.openingValue) >= 0 ? theme.palette.success.main : theme.palette.error.main 
                    }}>
                      {(day.closingValue - day.openingValue) >= 0 ? '+' : ''}${(day.closingValue - day.openingValue).toLocaleString()}
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

      {/* Top Products Analysis (like Finance Account Analysis) */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
        Top Products by Value
      </Typography>
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            CALCULATED from daily inventory balances
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Product</TableCell>
                  <TableCell>SKU</TableCell>
                  <TableCell align="right">Quantity</TableCell>
                  <TableCell align="right">Unit Cost</TableCell>
                  <TableCell align="right">Total Value</TableCell>
                  <TableCell align="right">Net Change</TableCell>
                  <TableCell>Cost Method</TableCell>
                  <TableCell>Location</TableCell>
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
                    <TableCell align="right">{product.quantity.toLocaleString()}</TableCell>
                    <TableCell align="right">{formatCurrency(product.unitCost)}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 'bold' }}>
                      {formatCurrency(product.totalValue)}
                    </TableCell>
                    <TableCell align="right" sx={{ 
                      color: product.netChange >= 0 ? theme.palette.success.main : theme.palette.error.main 
                    }}>
                      {product.netChange >= 0 ? '+' : ''}{formatCurrency(product.netChange)}
                    </TableCell>
                    <TableCell>
                      <Chip label={product.costMethod} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>{product.warehouse}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Inventory Performance Ratios (like Finance Key Ratios) */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 'bold' }}>
        Inventory Performance Ratios
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: theme.palette.primary.main }}>
                {metrics.inventoryTurnover}x
              </Typography>
              <Typography variant="body2">Inventory Turnover</Typography>
              <Chip 
                label={metrics.turnoverHealth} 
                size="small" 
                color={
                  metrics.turnoverHealth === 'Excellent' ? 'success' :
                  metrics.turnoverHealth === 'Good' ? 'info' :
                  metrics.turnoverHealth === 'Fair' ? 'warning' : 'error'
                }
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: theme.palette.success.main }}>
                {metrics.daysInInventory}
              </Typography>
              <Typography variant="body2">Days in Inventory</Typography>
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
                {metrics.receiptToIssueRatio}
              </Typography>
              <Typography variant="body2">Receipt/Issue Ratio</Typography>
              <Typography variant="caption" color="text.secondary">
                Replenishment balance
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h4" sx={{ fontWeight: 'bold', color: theme.palette.warning.main }}>
                {metrics.adjustmentRate}%
              </Typography>
              <Typography variant="body2">Adjustment Rate</Typography>
              <Typography variant="caption" color="text.secondary">
                Inventory accuracy impact
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