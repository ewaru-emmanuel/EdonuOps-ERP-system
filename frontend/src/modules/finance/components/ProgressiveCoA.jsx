import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Tooltip,
  IconButton,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Menu,
  Snackbar
} from '@mui/material';
import {
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Info as InfoIcon,
  Business as BusinessIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  MoreVert as MoreVertIcon,
  AccountBalance as AccountBalanceIcon,
  AttachMoney as AttachMoneyIcon
} from '@mui/icons-material';

const ProgressiveCoA = ({ accounts, onAccountSelect, onModeChange }) => {
  const [viewMode, setViewMode] = useState('basic'); // 'basic' or 'advanced'
  const [selectedIndustry, setSelectedIndustry] = useState('retail');
  const [showIndustrySelector, setShowIndustrySelector] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    assets: true,
    liabilities: true,
    equity: true,
    revenue: true,
    expenses: true
  });

  // Account management state
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [editingAccount, setEditingAccount] = useState(null);
  const [accountMenuAnchor, setAccountMenuAnchor] = useState(null);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Form state
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    category: '',
    type: '',
    description: '',
    isActive: true
  });

  const industries = [
    { id: 'retail', name: 'Retail Business', description: 'Inventory-heavy businesses' },
    { id: 'services', name: 'Services Business', description: 'Consulting, agencies, etc.' },
    { id: 'manufacturing', name: 'Manufacturing', description: 'Production businesses' },
    { id: 'freelancer', name: 'Freelancer', description: 'Solo entrepreneurs' }
  ];

  // Filter accounts based on view mode
  const filteredAccounts = (accounts || []).filter(account => {
    if (viewMode === 'basic') {
      return account.is_core !== false; // Show core accounts in basic mode
    }
    return true; // Show all accounts in advanced mode
  });

  // Group accounts by category
  const groupedAccounts = filteredAccounts.reduce((groups, account) => {
    const category = account.account_type ? account.account_type.toLowerCase() : 'unknown';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(account);
    return groups;
  }, {});

  const accountTypeConfig = {
    asset: { 
      label: 'Assets', 
      color: 'success', 
      icon: '💰',
      description: 'What your business owns'
    },
    liability: { 
      label: 'Liabilities', 
      color: 'error', 
      icon: '📋',
      description: 'What your business owes'
    },
    equity: { 
      label: 'Equity', 
      color: 'primary', 
      icon: '👤',
      description: 'Owner\'s stake in the business'
    },
    revenue: { 
      label: 'Revenue', 
      color: 'info', 
      icon: '📈',
      description: 'Money coming into your business'
    },
    expense: { 
      label: 'Expenses', 
      color: 'warning', 
      icon: '💸',
      description: 'Money going out of your business'
    }
  };

  const handleModeChange = (event) => {
    const newMode = event.target.checked ? 'advanced' : 'basic';
    setViewMode(newMode);
    onModeChange?.(newMode);
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const handleIndustryChange = (industryId) => {
    setSelectedIndustry(industryId);
    setShowIndustrySelector(false);
    // This would trigger a reload of accounts for the new industry
    // onIndustryChange?.(industryId);
  };

  const renderAccountItem = (account) => (
    <ListItem
      key={account.id}
      button
      onClick={() => onAccountSelect?.(account)}
      sx={{
        pl: 2,
        '&:hover': { backgroundColor: 'action.hover' }
      }}
    >
      <ListItemIcon>
        <AccountBalanceIcon color="primary" />
      </ListItemIcon>
      <ListItemText
        primary={account.name}
        secondary={
          <Box component="span" sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
            {account.required_tags?.map(tag => (
              <Chip
                key={tag}
                label={tag}
                size="small"
                variant="outlined"
                color="primary"
              />
            ))}
            {account.is_core === false && (
              <Chip
                label="Advanced"
                size="small"
                variant="outlined"
                color="secondary"
              />
            )}
          </Box>
        }
      />
      <Tooltip title={account.description || `${account.name} account`}>
        <IconButton size="small">
          <InfoIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </ListItem>
  );

  const renderAccountSection = (category, accounts) => {
    const config = accountTypeConfig[category] || {
      label: category.charAt(0).toUpperCase() + category.slice(1),
      color: 'default',
      icon: '📊',
      description: `${category} accounts`
    };
    const isExpanded = expandedSections[category];
    
    return (
      <Card key={category} sx={{ mb: 2 }}>
        <CardContent sx={{ p: 0 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              p: 2,
              cursor: 'pointer',
              '&:hover': { backgroundColor: 'action.hover' }
            }}
            onClick={() => toggleSection(category)}
          >
            <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="h6" component="span">
                <span>{config.icon}</span>
                {config.label}
              </Typography>
              <Chip
                label={accounts.length}
                size="small"
                color={config.color}
                variant="outlined"
              />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mr: 2 }}>
              {config.description}
            </Typography>
            {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </Box>
          
          {isExpanded && (
            <>
              <Divider />
              <List sx={{ maxHeight: 300, overflow: 'auto' }}>
                {accounts.map(renderAccountItem)}
              </List>
            </>
          )}
        </CardContent>
      </Card>
    );
  };

  // Show loading state if accounts are not loaded yet
  if (!accounts) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Loading Chart of Accounts...
        </Typography>
      </Box>
    );
  }

  // Show empty state if no accounts
  if (accounts.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No accounts found
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Start by adding your first account or importing from a template.
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header with Mode Toggle */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h5" component="h2">
              Chart of Accounts
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<BusinessIcon />}
                onClick={() => setShowIndustrySelector(true)}
              >
                {industries.find(i => i.id === selectedIndustry)?.name}
              </Button>
              <FormControlLabel
                control={
                  <Switch
                    checked={viewMode === 'advanced'}
                    onChange={handleModeChange}
                    color="primary"
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {viewMode === 'basic' ? <VisibilityIcon /> : <VisibilityOffIcon />}
                    {viewMode === 'basic' ? 'Basic Mode' : 'Advanced Mode'}
                  </Box>
                }
              />
            </Box>
          </Box>
          
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <strong>Basic Mode:</strong> Shows 30 core accounts essential for your business type.
              <br />
              <strong>Advanced Mode:</strong> Shows all accounts including specialized ones.
            </Typography>
          </Alert>
          
          <Typography variant="body2" color="text.secondary">
            {viewMode === 'basic' 
              ? `Showing ${filteredAccounts.length} core accounts for ${industries.find(i => i.id === selectedIndustry)?.name}`
              : `Showing all ${filteredAccounts.length} accounts`
            }
          </Typography>
        </CardContent>
      </Card>

      {/* Account Sections */}
      {Object.entries(groupedAccounts).map(([category, accounts]) => 
        renderAccountSection(category, accounts)
      )}

      {/* Industry Selector Dialog */}
      <Dialog 
        open={showIndustrySelector} 
        onClose={() => setShowIndustrySelector(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Select Business Type</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Choose the business type that best matches your company. This will customize your Chart of Accounts.
          </Typography>
          <List>
            {industries.map(industry => (
              <ListItem
                key={industry.id}
                button
                onClick={() => handleIndustryChange(industry.id)}
                selected={selectedIndustry === industry.id}
              >
                <ListItemText
                  primary={industry.name}
                  secondary={industry.description}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowIndustrySelector(false)}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProgressiveCoA;
