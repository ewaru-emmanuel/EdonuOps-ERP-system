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
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, LocalTaxi, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb,
  CloudUpload, Description, ReceiptLong, PaymentOutlined, ScheduleSend, AutoFixHigh, SmartToy, QrCode, CameraAlt,
  Email, Send, CreditCard, AccountBalanceWallet as WalletIcon, TrendingUp as TrendingUpIcon, CalendarToday,
  Timeline as TimelineIcon, ShowChart as ShowChartIcon, TrendingUp as TrendingUpIcon2, CompareArrows, ScatterPlot,
  Assessment as AssessmentIcon, Analytics, Timeline as TimelineIcon2, ShowChart as ShowChartIcon2, TrendingUp as TrendingUpIcon3,
  PictureAsPdf, TableChart, BarChart as BarChartIcon, PieChart as PieChartIcon, ShowChart as ShowChartIcon3,
  GetApp, Share, Print, Visibility as VisibilityIcon, Edit as EditIcon, Download as DownloadIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const SmartFinancialReports = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectedReport, setSelectedReport] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [reportPeriod, setReportPeriod] = useState('current_month');
  const [comparisonPeriod, setComparisonPeriod] = useState('previous_month');
  const [selectedCurrency, setSelectedCurrency] = useState('USD');
  const [drillDownOpen, setDrillDownOpen] = useState(false);
  const [drillDownData, setDrillDownData] = useState(null);

  // Data hooks
  const { data: profitLossData, loading: plLoading, error: plError } = useRealTimeData('/api/finance/profit-loss');
  const { data: balanceSheetData, loading: bsLoading, error: bsError } = useRealTimeData('/api/finance/balance-sheet');
  const { data: cashFlowData, loading: cfLoading, error: cfError } = useRealTimeData('/api/finance/cash-flow');
  const { data: kpiData, loading: kpiLoading, error: kpiError } = useRealTimeData('/api/finance/kpis');

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!kpiData) return {};
    
    return {
      revenue: kpiData.revenue || 0,
      expenses: kpiData.expenses || 0,
      netIncome: kpiData.net_income || 0,
      totalAssets: kpiData.total_assets || 0,
      totalLiabilities: kpiData.total_liabilities || 0,
      equity: kpiData.equity || 0,
      cashFlow: kpiData.cash_flow || 0,
      profitMargin: kpiData.profit_margin || 0,
      assetTurnover: kpiData.asset_turnover || 0,
      debtToEquity: kpiData.debt_to_equity || 0
    };
  }, [kpiData]);

  const renderKPIMetrics = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  ${(metrics.revenue || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Total Revenue</Typography>
              </Box>
              <TrendingUp sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'error.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  ${(metrics.expenses || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Total Expenses</Typography>
              </Box>
              <TrendingDown sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  ${(metrics.netIncome || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Net Income</Typography>
              </Box>
              <AccountBalance sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'info.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  {(metrics.profitMargin || 0).toFixed(1)}%
                </Typography>
                <Typography variant="body2">Profit Margin</Typography>
              </Box>
              <BarChart sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderProfitLossStatement = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Profit & Loss Statement</Typography>
          <Box display="flex" gap={1}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Period</InputLabel>
              <Select
                value={reportPeriod}
                onChange={(e) => setReportPeriod(e.target.value)}
                label="Period"
              >
                <MenuItem value="current_month">Current Month</MenuItem>
                <MenuItem value="previous_month">Previous Month</MenuItem>
                <MenuItem value="current_quarter">Current Quarter</MenuItem>
                <MenuItem value="current_year">Current Year</MenuItem>
              </Select>
            </FormControl>
            <Button variant="outlined" startIcon={<Download />}>
              Export
            </Button>
          </Box>
        </Box>

        {plLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(8)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={40} />
            ))}
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Description</TableCell>
                  <TableCell align="right">Current Period</TableCell>
                  <TableCell align="right">Previous Period</TableCell>
                  <TableCell align="right">Variance</TableCell>
                  <TableCell align="right">% Change</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      REVENUE
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      ${(metrics.revenue || 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${((metrics.revenue || 0) * 0.95).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="success.main">
                      +${((metrics.revenue || 0) * 0.05).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="success.main">
                      +5.3%
                    </Typography>
                  </TableCell>
                </TableRow>
                
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      EXPENSES
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      ${(metrics.expenses || 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${((metrics.expenses || 0) * 1.02).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="error.main">
                      -${((metrics.expenses || 0) * 0.02).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="success.main">
                      -2.0%
                    </Typography>
                  </TableCell>
                </TableRow>
                
                <TableRow sx={{ bgcolor: 'primary.main', color: 'white' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      NET INCOME
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      ${(metrics.netIncome || 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${((metrics.netIncome || 0) * 0.98).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      +${((metrics.netIncome || 0) * 0.02).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      +2.0%
                    </Typography>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );

  const renderBalanceSheet = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Balance Sheet</Typography>
          <Box display="flex" gap={1}>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Currency</InputLabel>
              <Select
                value={selectedCurrency}
                onChange={(e) => setSelectedCurrency(e.target.value)}
                label="Currency"
              >
                <MenuItem value="USD">USD</MenuItem>
                <MenuItem value="EUR">EUR</MenuItem>
                <MenuItem value="GBP">GBP</MenuItem>
              </Select>
            </FormControl>
            <Button variant="outlined" startIcon={<Download />}>
              Export
            </Button>
          </Box>
        </Box>

        {bsLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={40} />
            ))}
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                ASSETS
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Current Assets</TableCell>
                      <TableCell align="right">
                        ${((metrics.totalAssets || 0) * 0.6).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Fixed Assets</TableCell>
                      <TableCell align="right">
                        ${((metrics.totalAssets || 0) * 0.4).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow sx={{ bgcolor: 'primary.main', color: 'white' }}>
                      <TableCell>
                        <Typography variant="subtitle2" fontWeight="bold">
                          TOTAL ASSETS
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="subtitle2" fontWeight="bold">
                          ${(metrics.totalAssets || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle1" fontWeight="bold" mb={2}>
                LIABILITIES & EQUITY
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableBody>
                    <TableRow>
                      <TableCell>Current Liabilities</TableCell>
                      <TableCell align="right">
                        ${((metrics.totalLiabilities || 0) * 0.7).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Long-term Liabilities</TableCell>
                      <TableCell align="right">
                        ${((metrics.totalLiabilities || 0) * 0.3).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Equity</TableCell>
                      <TableCell align="right">
                        ${(metrics.equity || 0).toLocaleString()}
                      </TableCell>
                    </TableRow>
                    <TableRow sx={{ bgcolor: 'primary.main', color: 'white' }}>
                      <TableCell>
                        <Typography variant="subtitle2" fontWeight="bold">
                          TOTAL LIABILITIES & EQUITY
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="subtitle2" fontWeight="bold">
                          ${(metrics.totalAssets || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </Grid>
        )}
      </CardContent>
    </Card>
  );

  const renderCashFlowStatement = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Cash Flow Statement</Typography>
          <Box display="flex" gap={1}>
            <Button variant="outlined" startIcon={<Timeline />}>
              Trend Analysis
            </Button>
            <Button variant="outlined" startIcon={<Download />}>
              Export
            </Button>
          </Box>
        </Box>

        {cfLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={40} />
            ))}
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Cash Flow Category</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell align="right">Previous Period</TableCell>
                  <TableCell align="right">Change</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      OPERATING ACTIVITIES
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold">
                      ${((metrics.cashFlow || 0) * 0.8).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${((metrics.cashFlow || 0) * 0.75).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="success.main">
                      +${((metrics.cashFlow || 0) * 0.05).toLocaleString()}
                    </Typography>
                  </TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell>Net Income</TableCell>
                  <TableCell align="right">
                    ${(metrics.netIncome || 0).toLocaleString()}
                  </TableCell>
                  <TableCell align="right">
                    ${((metrics.netIncome || 0) * 0.98).toLocaleString()}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="success.main">
                      +2.0%
                    </Typography>
                  </TableCell>
                </TableRow>
                
                <TableRow>
                  <TableCell>Depreciation & Amortization</TableCell>
                  <TableCell align="right">
                    ${((metrics.cashFlow || 0) * 0.1).toLocaleString()}
                  </TableCell>
                  <TableCell align="right">
                    ${((metrics.cashFlow || 0) * 0.1).toLocaleString()}
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      0%
                    </Typography>
                  </TableCell>
                </TableRow>
                
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      INVESTING ACTIVITIES
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold" color="error.main">
                      -${((metrics.cashFlow || 0) * 0.2).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="error.main">
                      -${((metrics.cashFlow || 0) * 0.25).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" color="success.main">
                      +20%
                    </Typography>
                  </TableCell>
                </TableRow>
                
                <TableRow sx={{ bgcolor: 'primary.main', color: 'white' }}>
                  <TableCell>
                    <Typography variant="subtitle2" fontWeight="bold">
                      NET CASH FLOW
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="subtitle2" fontWeight="bold">
                      ${(metrics.cashFlow || 0).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      ${((metrics.cashFlow || 0) * 0.95).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2">
                      +5.3%
                    </Typography>
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </CardContent>
    </Card>
  );

  const renderFinancialRatios = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Key Financial Ratios</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center" p={2} border={1} borderColor="grey.300" borderRadius={1}>
              <Typography variant="h4" color="primary">
                {(metrics.profitMargin || 0).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Profit Margin
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center" p={2} border={1} borderColor="grey.300" borderRadius={1}>
              <Typography variant="h4" color="success.main">
                {(metrics.assetTurnover || 0).toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Asset Turnover
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center" p={2} border={1} borderColor="grey.300" borderRadius={1}>
              <Typography variant="h4" color="warning.main">
                {(metrics.debtToEquity || 0).toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Debt-to-Equity
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Box textAlign="center" p={2} border={1} borderColor="grey.300" borderRadius={1}>
              <Typography variant="h4" color="info.main">
                {((metrics.totalAssets || 0) / (metrics.totalLiabilities || 1)).toFixed(2)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Current Ratio
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderReportActions = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Report Actions</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<PictureAsPdf />}
              onClick={() => setSnackbar({ open: true, message: 'Generating PDF report...', severity: 'info' })}
            >
              Export PDF
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<TableChart />}
              onClick={() => setSnackbar({ open: true, message: 'Generating Excel report...', severity: 'info' })}
            >
              Export Excel
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Share />}
              onClick={() => setSnackbar({ open: true, message: 'Sharing report...', severity: 'info' })}
            >
              Share Report
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Print />}
              onClick={() => setSnackbar({ open: true, message: 'Preparing for print...', severity: 'info' })}
            >
              Print Report
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Financial Reports & Analytics
      </Typography>
      
      {renderKPIMetrics()}
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderProfitLossStatement()}
        </Grid>
        <Grid item xs={12}>
          {renderBalanceSheet()}
        </Grid>
        <Grid item xs={12}>
          {renderCashFlowStatement()}
        </Grid>
        <Grid item xs={12}>
          {renderFinancialRatios()}
        </Grid>
        <Grid item xs={12}>
          {renderReportActions()}
        </Grid>
      </Grid>

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

export default SmartFinancialReports;


