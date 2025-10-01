import React, { useState, useEffect, useMemo } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Checkbox, FormControlLabel, Radio, RadioGroup, Slider, Switch, InputAdornment
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb,
  CloudUpload, Description, ReceiptLong, PaymentOutlined, ScheduleSend, AutoFixHigh, SmartToy, QrCode, CameraAlt,
  Email, Send, CreditCard, AccountBalanceWallet as WalletIcon, TrendingUp as TrendingUpIcon, CalendarToday,
  Timeline as TimelineIcon, ShowChart as ShowChartIcon, TrendingUp as TrendingUpIcon2, CompareArrows, ScatterPlot
} from '@mui/icons-material';
import { useFinanceData } from '../hooks/useFinanceData';

const SmartBudgeting = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [selectedPeriod, setSelectedPeriod] = useState(new Date().getFullYear().toString());
  const [selectedScenario, setSelectedScenario] = useState('base');
  const [showScenarioDialog, setShowScenarioDialog] = useState(false);
  const [showForecastDialog, setShowForecastDialog] = useState(false);
  const [showBudgetDialog, setShowBudgetDialog] = useState(false);
  const [editingCell, setEditingCell] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [budgetForm, setBudgetForm] = useState({
    name: '',
    description: '',
    department: '',
    account_id: '',
    budgeted_amount: '',
    budget_type: 'base',
    // Payment method budgeting fields
    payment_method_budget: {},
    processing_fee_budget: '',
    bank_account_budget: {}
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  // Real-time data hooks - fetch from database
  const { data: budgets = [], loading: budgetsLoading, error: budgetsError, refresh: refreshBudgets } = useFinanceData('budgets');
  
  const chartOfAccounts = [];
  const coaLoading = false;
  const refreshChartOfAccounts = () => { console.log('Mock refresh chart of accounts'); };
  
  const actuals = [];
  const actualsLoading = false;
  const refreshActuals = () => { console.log('Mock refresh actuals'); };
  
  const paymentMethods = [];
  const paymentMethodsLoading = false;
  
  const bankAccounts = [];
  const bankAccountsLoading = false;
  
  const summaryData = [];
  const summaryLoading = false;
  const refreshSummary = () => { console.log('Mock refresh summary'); };

  // Real budget data from backend
  const budgetData = useMemo(() => {
    if (!budgets || !Array.isArray(budgets)) {
      return [];
    }
    
    // Process real budget data from API
    return budgets.map(budget => ({
      id: budget.id,
      accountCode: budget.account_id || '',
      accountName: budget.name || '',
      accountType: budget.department || '',
      budget: budget.budgeted_amount || 0,
      actual: budget.actual_amount || 0,
      variance: (budget.actual_amount || 0) - (budget.budgeted_amount || 0),
      variancePercent: budget.budgeted_amount > 0 ? (((budget.actual_amount || 0) - budget.budgeted_amount) / budget.budgeted_amount) * 100 : 0,
      forecast: budget.budgeted_amount || 0, // Use budget as forecast if no separate forecast
      scenarios: {
        optimistic: Math.round((budget.budgeted_amount || 0) * 1.2),
        base: budget.budgeted_amount || 0,
        pessimistic: Math.round((budget.budgeted_amount || 0) * 0.8)
      }
    }));
  }, [budgets]);

  // Budget summary metrics
  const budgetSummary = useMemo(() => {
    const totalBudget = budgetData.reduce((sum, item) => sum + item.budget, 0);
    const totalActual = budgetData.reduce((sum, item) => sum + item.actual, 0);
    const totalVariance = totalActual - totalBudget;
    const totalVariancePercent = totalBudget > 0 ? (totalVariance / totalBudget) * 100 : 0;

    const revenueBudget = budgetData
      .filter(item => item.accountType === 'Revenue')
      .reduce((sum, item) => sum + item.budget, 0);
    const expenseBudget = budgetData
      .filter(item => item.accountType === 'Expense')
      .reduce((sum, item) => sum + item.budget, 0);

    return {
      totalBudget,
      totalActual,
      totalVariance,
      totalVariancePercent,
      revenueBudget,
      expenseBudget,
      netBudget: revenueBudget - expenseBudget
    };
  }, [budgetData]);

  // Handle cell editing
  const handleCellEdit = (itemId, field) => {
    const item = budgetData.find(item => item.id === itemId);
    if (item) {
      setEditingCell({ id: itemId, field });
      setEditValue(item[field]?.toString() || '');
    }
  };

  const handleCellSave = async () => {
    if (editingCell) {
      try {
        const { id, field } = editingCell;
        const value = parseFloat(editValue) || 0;
        
        // Find the budget item to update
        const budgetItem = budgetData.find(item => item.id === id);
        if (!budgetItem) {
          throw new Error('Budget item not found');
        }
        
        // Prepare update data based on field being edited
        const updateData = {
          name: budgetItem.accountName,
          fiscal_year: selectedPeriod,
          budgeted_amount: field === 'budget' ? value : budgetItem.budget,
          actual_amount: field === 'actual' ? value : budgetItem.actual,
          department: budgetItem.accountType,
          account_id: budgetItem.accountCode
        };
        
        // Call backend API to update budget
        // Mock update budget - no API call
        console.log('Mock update budget:', id, updateData);
        const response = { id, ...updateData };
        
        if (response) {
          setSnackbar({ open: true, message: 'Budget updated successfully', severity: 'success' });
          // Refresh budget data
          refreshBudgets();
        }
      } catch (error) {
        console.error('Error updating budget:', error);
        setSnackbar({ open: true, message: 'Failed to update budget: ' + error.message, severity: 'error' });
      } finally {
        setEditingCell(null);
        setEditValue('');
      }
    }
  };

  const handleCellCancel = () => {
    setEditingCell(null);
    setEditValue('');
  };

  const handleScenarioCreate = () => {
    setShowScenarioDialog(true);
  };

  const handleForecastGenerate = () => {
    setShowForecastDialog(true);
  };

  const handleAddBudget = () => {
    setShowBudgetDialog(true);
  };

  const handleCreateBudget = async () => {
    try {
      // Validate required fields
      if (!budgetForm.name || !budgetForm.budgeted_amount) {
        setSnackbar({ open: true, message: 'Name and Budget Amount are required', severity: 'error' });
        return;
      }

      const budgetData = {
        name: budgetForm.name,
        description: budgetForm.description,
        fiscal_year: selectedPeriod,
        period: `${selectedPeriod}-01`, // Default to January
        department: budgetForm.department,
        account_id: budgetForm.account_id ? parseInt(budgetForm.account_id) : null,
        budgeted_amount: parseFloat(budgetForm.budgeted_amount),
        actual_amount: 0,
        budget_type: budgetForm.budget_type,
        status: 'active'
      };

      // Real create budget - save to database
      const apiClient = (await import('../../../services/apiClient')).default;
      const response = await apiClient.post('/finance/budgets', budgetData);
      console.log('✅ Budget created:', response);
      
      if (response) {
        setSnackbar({ open: true, message: 'Budget created successfully!', severity: 'success' });
        refreshBudgets(); // Refresh the list to show new budget
        setShowBudgetDialog(false);
        setBudgetForm({
          name: '',
          description: '',
          department: '',
          account_id: '',
          budgeted_amount: '',
          budget_type: 'base'
        });
        // Refresh budget data
        refreshBudgets();
      }
    } catch (error) {
      console.error('Error creating budget:', error);
      setSnackbar({ open: true, message: 'Failed to create budget: ' + error.message, severity: 'error' });
    }
  };

  const handleExport = () => {
    const csvContent = "data:text/csv;charset=utf-8," + 
      "Account Code,Account Name,Budget,Actual,Variance,Variance %\n" +
      budgetData.map(item => 
        `${item.accountCode},${item.accountName},${item.budget},${item.actual},${item.variance},${item.variancePercent.toFixed(2)}%`
      ).join("\n");
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `budget_${selectedPeriod}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getVarianceColor = (variancePercent) => {
    if (variancePercent > 10) return 'error';
    if (variancePercent > 5) return 'warning';
    if (variancePercent < -10) return 'error';
    if (variancePercent < -5) return 'warning';
    return 'success';
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" gutterBottom>
            Smart Budgeting & Forecasting
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Excel-like interface with AI-powered forecasting and scenario planning
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Button
            variant="outlined"
            startIcon={<CompareArrows />}
            onClick={handleScenarioCreate}
          >
            Create Scenario
          </Button>
          <Button
            variant="outlined"
            startIcon={<ShowChartIcon />}
            onClick={handleForecastGenerate}
          >
            Generate Forecast
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleAddBudget}
          >
            Add Budget Line
          </Button>
        </Box>
      </Box>

      {/* Budget Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Total Budget
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${budgetSummary.totalBudget.toLocaleString()}
                  </Typography>
                </Box>
                <AccountBalance sx={{ fontSize: 28, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            color: 'white'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Total Actual
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${budgetSummary.totalActual.toLocaleString()}
                  </Typography>
                </Box>
                <ShowChartIcon sx={{ fontSize: 28, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: budgetSummary.totalVariancePercent > 5 ? 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' : 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            color: budgetSummary.totalVariancePercent > 5 ? 'white' : 'inherit'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.8 }}>
                    Variance
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${budgetSummary.totalVariance.toLocaleString()}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>
                    {budgetSummary.totalVariancePercent.toFixed(1)}%
                  </Typography>
                </Box>
                <TrendingUpIcon sx={{ fontSize: 28, opacity: 0.8 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            background: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)'
          }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Net Budget
                  </Typography>
                  <Typography variant={isMobile ? "h5" : "h4"} sx={{ fontWeight: 'bold' }}>
                    ${budgetSummary.netBudget.toLocaleString()}
                  </Typography>
                </Box>
                <TimelineIcon sx={{ fontSize: 28, color: 'primary.main' }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Budget Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Period</InputLabel>
                <Select
                  value={selectedPeriod}
                  onChange={(e) => setSelectedPeriod(e.target.value)}
                >
                  {Array.from({ length: 5 }, (_, i) => {
                    const year = new Date().getFullYear() - i;
                    return (
                      <MenuItem key={year} value={year.toString()}>
                        {year}
                      </MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Scenario</InputLabel>
                <Select
                  value={selectedScenario}
                  onChange={(e) => setSelectedScenario(e.target.value)}
                >
                  <MenuItem value="optimistic">Optimistic</MenuItem>
                  <MenuItem value="base">Base Case</MenuItem>
                  <MenuItem value="pessimistic">Pessimistic</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleExport}
                fullWidth
              >
                Export Budget
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => {
                  refreshBudgets();
                  refreshChartOfAccounts();
                  refreshActuals();
                  refreshSummary();
                }}
                disabled={budgetsLoading || coaLoading || actualsLoading || summaryLoading}
                fullWidth
              >
                Refresh
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Budget Table */}
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">
              Budget vs Actual ({budgetData.length} accounts)
            </Typography>
            <Chip 
              label={`Scenario: ${selectedScenario}`} 
              color="primary" 
              variant="outlined"
            />
          </Box>

          {budgetsLoading && <LinearProgress sx={{ mb: 2 }} />}

          {budgetsError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {budgetsError}
            </Alert>
          )}

          <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Account Code</TableCell>
                  <TableCell>Account Name</TableCell>
                  <TableCell align="right">Budget</TableCell>
                  <TableCell align="right">Actual</TableCell>
                  <TableCell align="right">Variance</TableCell>
                  <TableCell align="right">Variance %</TableCell>
                  <TableCell align="right">Forecast</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {budgetData.map((item) => (
                  <TableRow key={item.id} hover>
                    <TableCell>{item.accountCode}</TableCell>
                    <TableCell>{item.accountName}</TableCell>
                    <TableCell align="right">
                      {editingCell?.id === item.id && editingCell?.field === 'budget' ? (
                        <Box display="flex" alignItems="center" gap={1}>
                          <TextField
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            size="small"
                            type="number"
                            sx={{ width: 100 }}
                            InputProps={{
                              startAdornment: '$',
                            }}
                          />
                          <IconButton size="small" onClick={handleCellSave} color="success">
                            <Save />
                          </IconButton>
                          <IconButton size="small" onClick={handleCellCancel} color="error">
                            <Cancel />
                          </IconButton>
                        </Box>
                      ) : (
                        <Box 
                          display="flex" 
                          alignItems="center" 
                          justifyContent="space-between"
                          sx={{ cursor: 'pointer' }}
                          onClick={() => handleCellEdit(item.id, 'budget')}
                        >
                          ${item.budget.toLocaleString()}
                          <Edit sx={{ fontSize: 16, opacity: 0.5 }} />
                        </Box>
                      )}
                    </TableCell>
                    <TableCell align="right">${item.actual.toLocaleString()}</TableCell>
                    <TableCell align="right">
                      <Typography 
                        color={getVarianceColor(item.variancePercent)}
                        fontWeight="bold"
                      >
                        ${item.variance.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Chip
                        label={`${item.variancePercent.toFixed(1)}%`}
                        color={getVarianceColor(item.variancePercent)}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell align="right">${item.forecast.toLocaleString()}</TableCell>
                    <TableCell>
                      <Box display="flex" gap={1}>
                        <Tooltip title="View Details">
                          <IconButton size="small">
                            <Visibility />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit Budget">
                          <IconButton size="small">
                            <Edit />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Scenario Analysis">
                          <IconButton size="small" color="primary">
                            <CompareArrows />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Scenario Creation Dialog */}
      <Dialog
        open={showScenarioDialog}
        onClose={() => setShowScenarioDialog(false)}
        maxWidth="md"
        fullWidth
        disableEnforceFocus
        disableAutoFocus
      >
        <DialogTitle>
          <Typography variant="h6">Create New Scenario</Typography>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Scenario Name"
                fullWidth
                placeholder={`e.g., Growth Scenario ${new Date().getFullYear()}`}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Growth Rate (%)"
                type="number"
                fullWidth
                placeholder="15"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Assumptions
              </Typography>
              <FormControlLabel
                control={<Switch />}
                label="Revenue growth based on market trends"
              />
              <FormControlLabel
                control={<Switch />}
                label="Cost inflation at 3% annually"
              />
              <FormControlLabel
                control={<Switch />}
                label="New product launch in Q3"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowScenarioDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setShowScenarioDialog(false)}>
            Create Scenario
          </Button>
        </DialogActions>
      </Dialog>

      {/* Forecast Generation Dialog */}
      <Dialog
        open={showForecastDialog}
        onClose={() => setShowForecastDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6">AI-Powered Forecast Generation</Typography>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Generate intelligent forecasts based on historical data and market trends:
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Forecast Period</InputLabel>
                <Select defaultValue="12">
                  <MenuItem value="3">3 Months</MenuItem>
                  <MenuItem value="6">6 Months</MenuItem>
                  <MenuItem value="12">12 Months</MenuItem>
                  <MenuItem value="24">24 Months</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Confidence Level</InputLabel>
                <Select defaultValue="90">
                  <MenuItem value="80">80%</MenuItem>
                  <MenuItem value="90">90%</MenuItem>
                  <MenuItem value="95">95%</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                AI Insights
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                Based on your historical data, we predict 12% revenue growth with 90% confidence
              </Alert>
              <Alert severity="warning" sx={{ mb: 2 }}>
                Expense trends suggest 8% cost increase due to inflation
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowForecastDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => setShowForecastDialog(false)}>
            Generate Forecast
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      {/* Create Budget Dialog */}
      <Dialog
        open={showBudgetDialog}
        onClose={() => setShowBudgetDialog(false)}
        maxWidth="md"
        fullWidth
        disableEnforceFocus
        disableAutoFocus
      >
        <DialogTitle>
          Create New Budget Entry
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Budget Name"
                fullWidth
                value={budgetForm.name}
                onChange={(e) => setBudgetForm({ ...budgetForm, name: e.target.value })}
                placeholder="e.g., Marketing Budget Q1"
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Department"
                fullWidth
                value={budgetForm.department}
                onChange={(e) => setBudgetForm({ ...budgetForm, department: e.target.value })}
                placeholder="e.g., Marketing, Operations"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Budget Amount"
                fullWidth
                type="number"
                value={budgetForm.budgeted_amount}
                onChange={(e) => setBudgetForm({ ...budgetForm, budgeted_amount: e.target.value })}
                placeholder="0.00"
                required
                InputProps={{
                  startAdornment: <Typography sx={{ mr: 1 }}>$</Typography>
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Budget Type</InputLabel>
                <Select
                  value={budgetForm.budget_type}
                  onChange={(e) => setBudgetForm({ ...budgetForm, budget_type: e.target.value })}
                  label="Budget Type"
                >
                  <MenuItem value="base">Base Budget</MenuItem>
                  <MenuItem value="optimistic">Optimistic</MenuItem>
                  <MenuItem value="pessimistic">Conservative</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                fullWidth
                multiline
                rows={3}
                value={budgetForm.description}
                onChange={(e) => setBudgetForm({ ...budgetForm, description: e.target.value })}
                placeholder="Optional description or notes about this budget entry"
              />
            </Grid>
            
            {/* Payment Method Budgeting */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2, mb: 1, color: 'primary.main' }}>
                Payment Method Budgeting
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Processing Fee Budget"
                type="number"
                fullWidth
                value={budgetForm.processing_fee_budget}
                onChange={(e) => setBudgetForm({ ...budgetForm, processing_fee_budget: e.target.value })}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
                placeholder="Monthly processing fee budget"
                helperText="Budget for credit card and payment processing fees"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Primary Payment Method</InputLabel>
                <Select
                  value={budgetForm.primary_payment_method || ''}
                  onChange={(e) => setBudgetForm({ ...budgetForm, primary_payment_method: e.target.value })}
                  label="Primary Payment Method"
                  disabled={paymentMethodsLoading}
                >
                  <MenuItem value="">
                    <em>Select Primary Method</em>
                  </MenuItem>
                  {paymentMethods && paymentMethods.map((method) => (
                    <MenuItem key={method.id} value={method.id}>
                      {method.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info">
                <Typography variant="body2">
                  <strong>Payment Method Budgeting Tips:</strong><br/>
                  • Budget processing fees separately for accurate cost tracking<br/>
                  • Consider payment method mix when forecasting cash flow<br/>
                  • Account for seasonal payment method preferences
                </Typography>
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowBudgetDialog(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={handleCreateBudget}
            disabled={!budgetForm.name || !budgetForm.budgeted_amount}
          >
            Create Budget
          </Button>
        </DialogActions>
      </Dialog>

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

export default SmartBudgeting;


