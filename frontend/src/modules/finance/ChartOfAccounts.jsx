import React, { useState, useMemo } from 'react';
import { useCurrency } from '../../components/GlobalCurrencySettings';
import { useCurrencyConversion } from '../../hooks/useCurrencyConversion';
import CurrencySelector from '../../components/CurrencySelector';
import { 
  Box, 
  Tabs, 
  Tab, 
  CircularProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  Alert,
  Typography,
  Chip,
  Card,
  CardContent,
  Grid,
  Checkbox,
  FormControlLabel,
  Switch,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Toolbar,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  Snackbar
} from '@mui/material';
import { 
  Add as AddIcon,
  Settings as SettingsIcon,
  AutoAwesome as MagicIcon,
  Refresh as RefreshIcon,
  Lightbulb as LightbulbIcon,
  MoreVert as MoreVertIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  FilterList as FilterIcon,
  CheckBox as CheckBoxIcon,
  CheckBoxOutlineBlank as CheckBoxOutlineBlankIcon,
  Work as WorkIcon,
  List as ListIcon
} from '@mui/icons-material';
import { CoAProvider, useCoA } from './context/CoAContext';
import CoATree from './components/CoATree';
import CoATreeEnhanced from './components/CoATreeEnhanced';
import CoAForm from './forms/CoAForm';
import FinanceTableDisplay from '../../components/tables/FinanceTableDisplay';
import ProgressiveCoA from './components/ProgressiveCoA';
import WorkflowBasedUX from './components/WorkflowBasedUX';

const ChartOfAccountsContent = () => {
  const { 
    accounts, 
    loading, 
    error,
    viewMode, 
    setViewMode,
    deleteAccount,
    updateAccount
  } = useCoA();

  // Currency context and conversion
  const { selectedCurrency, formatCurrency } = useCurrency();
  const { 
    data: convertedAccounts, 
    isConverting, 
    hasMonetaryData,
    formatAmount 
  } = useCurrencyConversion(accounts, 'coa');
  
  const [openDialog, setOpenDialog] = useState(false);
  const [currentAccount, setCurrentAccount] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [selectedAccounts, setSelectedAccounts] = useState(new Set());
  const [showOnlySelected, setShowOnlySelected] = useState(false);
  const [sortBy, setSortBy] = useState('code');
  const [sortDirection, setSortDirection] = useState('asc');
  const [actionMenuAnchor, setActionMenuAnchor] = useState(null);
  const [coaViewMode, setCoaViewMode] = useState('progressive'); // 'progressive', 'workflow', 'traditional'
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  const handleTabChange = (_, newValue) => {
    setViewMode(newValue);
  };

  const handleCoaViewModeChange = (mode) => {
    setCoaViewMode(mode);
  };

  const handleWorkflowComplete = (workflowId, data) => {
    // Here you would process the workflow and create journal entries
    setSnackbar({
      open: true,
      message: 'Transaction recorded successfully!',
      severity: 'success'
    });
  };

  const handleEdit = (account) => {
    setCurrentAccount(account);
    setOpenDialog(true);
  };

  const handleCreate = () => {
    setCurrentAccount(null);
    setOpenDialog(true);
  };

  const handleDelete = async (account) => {
    if (window.confirm(`Are you sure you want to delete account "${account.code} - ${account.name}"?`)) {
      try {
        await deleteAccount(account.id);
      } catch (error) {
        console.error("Delete failed:", error);
      }
    }
  };

  const handleDialogClose = () => {
    setOpenDialog(false);
    setCurrentAccount(null);
  };

  // Account selection handlers
  const handleSelectAccount = (accountId, checked) => {
    const newSelected = new Set(selectedAccounts);
    if (checked) {
      newSelected.add(accountId);
    } else {
      newSelected.delete(accountId);
    }
    setSelectedAccounts(newSelected);
  };

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedAccounts(new Set(filteredAccounts.map(acc => acc.id)));
    } else {
      setSelectedAccounts(new Set());
    }
  };

  const handleToggleAccountActive = async (account) => {
    try {
      await updateAccount(account.id, { ...account, is_active: !account.is_active });
    } catch (error) {
      console.error("Failed to toggle account:", error);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedAccounts.size === 0) return;
    
    const confirmed = window.confirm(
      `Are you sure you want to delete ${selectedAccounts.size} selected accounts?`
    );
    
    if (confirmed) {
      try {
        for (const accountId of selectedAccounts) {
          await deleteAccount(accountId);
        }
        setSelectedAccounts(new Set());
      } catch (error) {
        console.error("Bulk delete failed:", error);
      }
    }
  };

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortDirection('asc');
    }
  };

  // Handle currency change with potential data conversion
  const handleCurrencyChange = async (oldCurrency, newCurrency) => {
    // Check if we have account data with balances
    return hasMonetaryData;
  };

  // Filtered and sorted accounts (use converted accounts)
  const filteredAccounts = useMemo(() => {
    let filtered = convertedAccounts || [];
    
    if (showOnlySelected && selectedAccounts.size > 0) {
      filtered = filtered.filter(account => selectedAccounts.has(account.id));
    }
    
    // Sort accounts
    filtered.sort((a, b) => {
      let aValue = a[sortBy] || '';
      let bValue = b[sortBy] || '';
      
      if (sortBy === 'code') {
        aValue = parseInt(aValue) || 0;
        bValue = parseInt(bValue) || 0;
      } else if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }
      
      if (sortDirection === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
    
    return filtered;
  }, [convertedAccounts, selectedAccounts, showOnlySelected, sortBy, sortDirection]);

  const isAllSelected = filteredAccounts.length > 0 && 
    filteredAccounts.every(account => selectedAccounts.has(account.id));
  const isIndeterminate = selectedAccounts.size > 0 && !isAllSelected;

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
      <CircularProgress />
    </Box>
  );



  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Empty state */}
      {(convertedAccounts || []).length === 0 && (
        <Card sx={{ mb: 3, textAlign: 'center', py: 4 }}>
          <CardContent>
            <LightbulbIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" gutterBottom>
              Welcome to EdonuOps Chart of Accounts!
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Build a world-class Chart of Accounts tailored to your business needs.
              Choose from industry templates or start from scratch.
            </Typography>
            <Grid container spacing={2} justifyContent="center" sx={{ mt: 2 }}>
              <Grid item>
                <Button 
                  variant="contained" 
                  size="large"
                  startIcon={<AddIcon />}
                  onClick={handleCreate}
                >
                  Add Your First Account
                </Button>
              </Grid>
              <Grid item>
                <Button 
                  variant="outlined" 
                  size="large"
                  startIcon={<SettingsIcon />}
                  onClick={() => {}}
                >
                  Import Template
                </Button>
              </Grid>
            </Grid>
            <Box sx={{ mt: 3 }}>
              <Chip label="AI-Powered" color="primary" sx={{ mr: 1 }} />
              <Chip label="Industry Templates" color="secondary" sx={{ mr: 1 }} />
              <Chip label="Fully Customizable" color="success" />
            </Box>
          </CardContent>
        </Card>
      )}
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Typography variant="h4" component="h1">
              Chart of Accounts
            </Typography>
            {isConverting && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={16} />
                <Typography variant="caption" color="text.secondary">
                  Converting to {selectedCurrency}...
                </Typography>
              </Box>
            )}
          </Box>
          {(convertedAccounts || []).length > 0 && (
            <Tabs value={coaViewMode} onChange={(_, newValue) => handleCoaViewModeChange(newValue)}>
              <Tab label="Progressive View" value="progressive" />
              <Tab label="Workflow View" value="workflow" />
              <Tab label="Table View" value="table" />
              <Tab label="Tree View" value="tree" />
            </Tabs>
          )}
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          {/* Currency Selector */}
          <CurrencySelector
            onCurrencyChange={handleCurrencyChange}
            size="small"
            showLabel={false}
          />
          <Button 
            variant="contained" 
            startIcon={<AddIcon />}
            onClick={handleCreate}
            size="large"
          >
            Add Account
          </Button>
        </Box>
      </Box>

      {(convertedAccounts || []).length > 0 && (
        coaViewMode === 'progressive' ? (
          <ProgressiveCoA 
            accounts={convertedAccounts || accounts}
            onAccountSelect={handleEdit}
            onModeChange={(mode) => {}}
          />
        ) : coaViewMode === 'workflow' ? (
          <WorkflowBasedUX 
            accounts={convertedAccounts || accounts}
            onWorkflowComplete={handleWorkflowComplete}
          />
        ) : coaViewMode === 'table' ? (
          <Paper sx={{ mt: 2 }}>
            {/* Toolbar with bulk actions */}
            <Toolbar sx={{ pl: 2, pr: 1, minHeight: '64px !important' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={showOnlySelected}
                      onChange={(e) => setShowOnlySelected(e.target.checked)}
                      color="primary"
                    />
                  }
                  label={`Show Only Selected (${selectedAccounts.size})`}
                />
                {selectedAccounts.size > 0 && (
                  <Chip 
                    label={`${selectedAccounts.size} selected`} 
                    color="primary" 
                    sx={{ ml: 2 }} 
                  />
                )}
              </Box>
              
              <Box sx={{ display: 'flex', gap: 1 }}>
                {selectedAccounts.size > 0 && (
                  <>
                    <Tooltip title="Bulk Delete">
                      <IconButton 
                        color="error" 
                        onClick={handleBulkDelete}
                        size="small"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </>
                )}
                <Tooltip title="More Actions">
                  <IconButton
                    onClick={(e) => setActionMenuAnchor(e.currentTarget)}
                    size="small"
                  >
                    <MoreVertIcon />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <Menu
                anchorEl={actionMenuAnchor}
                open={Boolean(actionMenuAnchor)}
                onClose={() => setActionMenuAnchor(null)}
              >
                <MenuItem onClick={() => {
                  setSelectedAccounts(new Set());
                  setActionMenuAnchor(null);
                }}>
                  Clear Selection
                </MenuItem>
                <MenuItem onClick={() => {
                  setShowOnlySelected(!showOnlySelected);
                  setActionMenuAnchor(null);
                }}>
                  {showOnlySelected ? 'Show All' : 'Show Selected Only'}
                </MenuItem>
              </Menu>
            </Toolbar>

            {/* Enhanced Table */}
            <TableContainer>
              <Table stickyHeader>
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox">
                      <Checkbox
                        indeterminate={isIndeterminate}
                        checked={isAllSelected}
                        onChange={(e) => handleSelectAll(e.target.checked)}
                        inputProps={{ 'aria-label': 'select all accounts' }}
                      />
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'code'}
                        direction={sortBy === 'code' ? sortDirection : 'asc'}
                        onClick={() => handleSort('code')}
                      >
                        Account Code
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'account_name'}
                        direction={sortBy === 'account_name' ? sortDirection : 'asc'}
                        onClick={() => handleSort('account_name')}
                      >
                        Account Name
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'account_type'}
                        direction={sortBy === 'account_type' ? sortDirection : 'asc'}
                        onClick={() => handleSort('account_type')}
                      >
                        Type
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'balance'}
                        direction={sortBy === 'balance' ? sortDirection : 'asc'}
                        onClick={() => handleSort('balance')}
                      >
                        Balance
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>Currency</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredAccounts.map((account) => {
                    const isSelected = selectedAccounts.has(account.id);
                    const accountType = account.account_type || account.type;
                    const accountName = account.account_name || account.name;
                    const balance = account.balance || 0;
                    
                    return (
                      <TableRow
                        key={account.id}
                        hover
                        selected={isSelected}
                        sx={{ 
                          cursor: 'pointer',
                          transition: 'none', // Remove transition to eliminate lag
                          '&:hover': { backgroundColor: 'rgba(0, 0, 0, 0.01)' }, // Extremely light hover
                          opacity: account.is_active === false ? 0.6 : 1
                        }}
                      >
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={isSelected}
                            onChange={(e) => handleSelectAccount(account.id, e.target.checked)}
                            inputProps={{ 'aria-labelledby': `account-${account.id}` }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontWeight="medium">
                            {account.code}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography 
                            variant="body2" 
                            id={`account-${account.id}`}
                            sx={{ 
                              maxWidth: 200, 
                              overflow: 'hidden', 
                              textOverflow: 'ellipsis' 
                            }}
                          >
                            {accountName}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={accountType} 
                            size="small"
                            color={
                              accountType === 'asset' ? 'success' :
                              accountType === 'liability' ? 'error' :
                              accountType === 'equity' ? 'info' :
                              accountType === 'revenue' ? 'primary' :
                              'warning'
                            }
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography 
                            variant="body2" 
                            color={balance >= 0 ? 'text.primary' : 'error.main'}
                            fontWeight="medium"
                          >
                            {formatAmount(balance)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {selectedCurrency}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Tooltip title={account.is_active === false ? 'Click to activate' : 'Click to deactivate'}>
                            <IconButton 
                              size="small"
                              onClick={() => handleToggleAccountActive(account)}
                              color={account.is_active === false ? 'error' : 'success'}
                            >
                              {account.is_active === false ? <VisibilityOffIcon /> : <VisibilityIcon />}
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                        <TableCell align="right">
                          <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'flex-end' }}>
                            <Tooltip title="Edit Account">
                              <IconButton 
                                size="small" 
                                onClick={() => handleEdit(account)}
                              >
                                <EditIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete Account">
                              <IconButton 
                                size="small" 
                                color="error"
                                onClick={() => handleDelete(account)}
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
            
            {filteredAccounts.length === 0 && (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography variant="body1" color="text.secondary">
                  {showOnlySelected ? 'No accounts selected' : 'No accounts found'}
                </Typography>
              </Box>
            )}
          </Paper>
        ) : coaViewMode === 'tree' ? (
          <CoATreeEnhanced 
            onSelect={handleEdit}
            selectedAccounts={selectedAccounts}
            onSelectAccount={handleSelectAccount}
          />
        ) : null
      )}

      <Dialog 
        open={openDialog} 
        onClose={handleDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {currentAccount ? 'Edit Account' : 'Create New Account'}
        </DialogTitle>
        <DialogContent>
          <CoAForm 
            selectedAccount={currentAccount}
            onDone={handleDialogClose}
          />
        </DialogContent>
      </Dialog>



      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
        message={snackbar.message}
      />
    </Box>
  );
};

const ChartOfAccounts = () => {
  return (
    <CoAProvider>
      <ChartOfAccountsContent />
    </CoAProvider>
  );
};

export default ChartOfAccounts;