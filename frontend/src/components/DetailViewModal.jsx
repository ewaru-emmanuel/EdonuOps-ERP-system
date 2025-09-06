import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  Box,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Paper,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Close as CloseIcon,
  Edit as EditIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  LocationOn as LocationIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  CalendarToday as CalendarIcon,
  AttachMoney as MoneyIcon,
  Category as CategoryIcon,
  Inventory as InventoryIcon,
  Warehouse as WarehouseIcon,
  Receipt as ReceiptIcon,
  Assessment as AssessmentIcon,
  Payment as PaymentIcon,
  School as SchoolIcon,
  TrendingUp as TrendingUpIcon,
  AccountBalance as AccountBalanceIcon
} from '@mui/icons-material';

const DetailViewModal = ({ 
  open, 
  onClose, 
  data, 
  type, 
  onEdit,
  title 
}) => {
  const hasData = Boolean(data);

  const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000/api';

  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');
  const [aiScore, setAiScore] = useState(null);
  const [aiReasons, setAiReasons] = useState([]);
  const [aiActions, setAiActions] = useState([]);
  const [dealItems, setDealItems] = useState([]);
  const [savingItems, setSavingItems] = useState(false);
  const [emailGenLoading, setEmailGenLoading] = useState(false);
  const [emailDraft, setEmailDraft] = useState(null);

  const fetchAiForLead = async () => {
    try {
      setAiLoading(true);
      setAiError('');
      setAiActions([]);

      // Score (lead only)
      if (type === 'lead') {
        const scoreRes = await fetch(`${API_BASE}/crm/ai/score-lead`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ lead: data })
        });
        const scoreJson = await scoreRes.json();
        setAiScore(typeof scoreJson.score === 'number' ? scoreJson.score : null);
        setAiReasons(Array.isArray(scoreJson.reasons) ? scoreJson.reasons : []);
      }

      // Next-best actions (lead or opportunity)
      const nbaRes = await fetch(`${API_BASE}/crm/ai/next-actions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entityType: type === 'opportunity' ? 'deal' : type, entity: data })
      });
      const nbaJson = await nbaRes.json();
      setAiActions(Array.isArray(nbaJson.actions) ? nbaJson.actions : []);
    } catch (e) {
      setAiError(e?.message || 'AI service unavailable');
    } finally {
      setAiLoading(false);
    }
  };

  useEffect(() => {
    if (open && hasData && (type === 'lead' || type === 'opportunity')) {
      fetchAiForLead();
    } else {
      setAiLoading(false);
      setAiError('');
      setAiScore(null);
      setAiReasons([]);
      setAiActions([]);
      setDealItems([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, type, hasData, data?.id]);

  useEffect(() => {
    if (type === 'opportunity' && data && Array.isArray(data.products)) {
      setDealItems(data.products);
    }
  }, [type, data]);

  const addDealItem = () => {
    setDealItems(prev => [...prev, { sku: '', name: '', quantity: 1, unit_price: 0 }]);
  };

  const updateDealItem = (idx, field, value) => {
    setDealItems(prev => prev.map((it, i) => i === idx ? { ...it, [field]: value } : it));
  };

  const removeDealItem = (idx) => {
    setDealItems(prev => prev.filter((_, i) => i !== idx));
  };

  const saveDealItems = async () => {
    if (type !== 'opportunity' || !data?.id) return;
    try {
      setSavingItems(true);
      const res = await fetch(`${API_BASE}/crm/opportunities/${data.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ products: dealItems })
      });
      await res.json();
      setSavingItems(false);
    } catch (e) {
      setSavingItems(false);
    }
  };

  const generateEmail = async (intent = 'follow_up') => {
    try {
      setEmailGenLoading(true);
      setEmailDraft(null);
      const res = await fetch(`${API_BASE}/crm/ai/generate-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent, context: { type, data } })
      });
      const json = await res.json();
      setEmailDraft({ subject: json.subject, body: json.body });
    } catch (e) {
      setEmailDraft({ subject: 'Follow up', body: 'Hello,\n\nFollowing up.\n\nBest regards,' });
    } finally {
      setEmailGenLoading(false);
    }
  };

  // Helper function to render status chip without DOM nesting issues
  const renderStatusChip = (status, isActive = null) => {
    const label = isActive !== null ? (isActive ? 'Active' : 'Inactive') : (status || 'Active');
    const color = isActive !== null ? (isActive ? 'success' : 'default') : 
                  (status === 'active' || status === 'Active' ? 'success' : 'default');
    
    return (
      <Box component="span" sx={{ display: 'flex', alignItems: 'center' }}>
        <Chip 
          label={label} 
          color={color}
          size="small"
        />
      </Box>
    );
  };

  const getIcon = (type) => {
    switch (type) {
      case 'employee': return <PersonIcon />;
      case 'product': return <InventoryIcon />;
      case 'category': return <CategoryIcon />;
      case 'warehouse': return <WarehouseIcon />;
      case 'payroll': return <PaymentIcon />;
      case 'recruitment': return <SchoolIcon />;
      case 'contact': return <PersonIcon />;
      case 'lead': return <BusinessIcon />;
      case 'opportunity': return <TrendingUpIcon />;
      case 'account': return <AccountBalanceIcon />;
      case 'journal-entry': return <ReceiptIcon />;
      default: return <BusinessIcon />;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return '';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const renderEmployeeDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Personal Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><PersonIcon /></ListItemIcon>
              <ListItemText 
                primary="Name" 
                secondary={data.name || data.first_name + ' ' + data.last_name} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><EmailIcon /></ListItemIcon>
              <ListItemText primary="Email" secondary={data.email || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><PhoneIcon /></ListItemIcon>
              <ListItemText primary="Phone" secondary={data.phone || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><LocationIcon /></ListItemIcon>
              <ListItemText primary="Address" secondary={data.address || ''} />
            </ListItem>
          </List>
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Employment Details</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Position" secondary={data.position || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Department" secondary={data.department || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText 
                primary="Hire Date" 
                secondary={formatDate(data.hire_date || data.created_at)} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><MoneyIcon /></ListItemIcon>
              <ListItemText 
                primary="Salary" 
                secondary={formatCurrency(data.salary)} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText 
                primary="Status" 
                secondary={renderStatusChip(data.status)} 
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderProductDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Product Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><InventoryIcon /></ListItemIcon>
              <ListItemText primary="SKU" secondary={data.sku || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Name" secondary={data.name || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><CategoryIcon /></ListItemIcon>
              <ListItemText primary="Category" secondary={data.category_name || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><InventoryIcon /></ListItemIcon>
              <ListItemText primary="Unit" secondary={data.unit || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><MoneyIcon /></ListItemIcon>
              <ListItemText 
                primary="Standard Cost" 
                secondary={formatCurrency(data.standard_cost)} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><MoneyIcon /></ListItemIcon>
              <ListItemText 
                primary="Current Cost" 
                secondary={formatCurrency(data.current_cost)} 
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Inventory Details</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><InventoryIcon /></ListItemIcon>
              <ListItemText 
                primary="Current Stock" 
                secondary={`${data.current_stock || 0} ${data.unit || 'units'}`} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><InventoryIcon /></ListItemIcon>
              <ListItemText 
                primary="Min Stock" 
                secondary={`${data.min_stock || 0} ${data.unit || 'units'}`} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><InventoryIcon /></ListItemIcon>
              <ListItemText 
                primary="Max Stock" 
                secondary={`${data.max_stock || 0} ${data.unit || 'units'}`} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText 
                primary="Status" 
                secondary={renderStatusChip(null, data.is_active)} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText 
                primary="Created" 
                secondary={formatDate(data.created_at)} 
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
      
      {data.description && (
        <Grid item xs={12}>
          <Paper elevation={1} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Description</Typography>
            <Typography variant="body2" color="text.secondary">
              {data.description}
            </Typography>
          </Paper>
        </Grid>
      )}
    </Grid>
  );

  const renderCategoryDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Category Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><CategoryIcon /></ListItemIcon>
              <ListItemText primary="Name" secondary={data.name || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Parent Category" secondary={data.parent_name || 'None'} />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText 
                primary="Status" 
                secondary={renderStatusChip(null, data.is_active)} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText 
                primary="Created" 
                secondary={formatDate(data.created_at)} 
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
      
      {data.description && (
        <Grid item xs={12} md={6}>
          <Paper elevation={1} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Description</Typography>
            <Typography variant="body2" color="text.secondary">
              {data.description}
            </Typography>
          </Paper>
        </Grid>
      )}
    </Grid>
  );

  const renderPayrollDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Payroll Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><PersonIcon /></ListItemIcon>
              <ListItemText primary="Employee" secondary={data.employee || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText primary="Period" secondary={data.period || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><MoneyIcon /></ListItemIcon>
              <ListItemText 
                primary="Gross Pay" 
                secondary={formatCurrency(data.grossPay)} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><MoneyIcon /></ListItemIcon>
              <ListItemText 
                primary="Net Pay" 
                secondary={formatCurrency(data.netPay)} 
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText 
                primary="Status" 
                secondary={
                  <Box component="span" sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip 
                      label={data.status || 'Pending'} 
                      color={data.status === 'Paid' ? 'success' : 'warning'}
                      size="small"
                    />
                  </Box>
                } 
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderContactDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Contact Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><PersonIcon /></ListItemIcon>
              <ListItemText
                primary="Name"
                secondary={`${data.first_name} ${data.last_name}`}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><EmailIcon /></ListItemIcon>
              <ListItemText primary="Email" secondary={data.email || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><PhoneIcon /></ListItemIcon>
              <ListItemText primary="Phone" secondary={data.phone || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Company" secondary={data.company || ''} />
            </ListItem>
          </List>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Contact Details</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Type" secondary={data.type || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText
                primary="Status"
                secondary={renderStatusChip(data.status)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText
                primary="Created"
                secondary={formatDate(data.created_at)}
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderLeadDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Lead Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><PersonIcon /></ListItemIcon>
              <ListItemText
                primary="Name"
                secondary={`${data.first_name} ${data.last_name}`}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><EmailIcon /></ListItemIcon>
              <ListItemText primary="Email" secondary={data.email || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><PhoneIcon /></ListItemIcon>
              <ListItemText primary="Phone" secondary={data.phone || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Company" secondary={data.company || ''} />
            </ListItem>
          </List>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Lead Details</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Source" secondary={data.source || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText
                primary="Status"
                secondary={
                  <Box component="span" sx={{ display: 'flex', alignItems: 'center' }}>
                    <Chip
                      label={data.status || 'New'}
                      color={data.status === 'new' ? 'warning' : 'success'}
                      size="small"
                    />
                  </Box>
                }
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText
                primary="Created"
                secondary={formatDate(data.created_at)}
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderOpportunityDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Opportunity Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Name" secondary={data.name || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><PersonIcon /></ListItemIcon>
              <ListItemText primary="Contact ID" secondary={data.contact_id || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><MoneyIcon /></ListItemIcon>
              <ListItemText
                primary="Amount"
                secondary={formatCurrency(data.amount)}
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Opportunity Details</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText primary="Stage" secondary={data.stage || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><TrendingUpIcon /></ListItemIcon>
              <ListItemText primary="Probability" secondary={`${data.probability || 0}%`} />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText
                primary="Expected Close Date"
                secondary={formatDate(data.expected_close_date)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText
                primary="Created"
                secondary={formatDate(data.created_at)}
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderAccountDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Account Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><AccountBalanceIcon /></ListItemIcon>
              <ListItemText primary="Code" secondary={data.code || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Name" secondary={data.name || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText primary="Type" secondary={data.type || ''} />
            </ListItem>
          </List>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Account Details</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><BusinessIcon /></ListItemIcon>
              <ListItemText primary="Parent Account" secondary={data.parent_id || 'None'} />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText
                primary="Status"
                secondary={renderStatusChip(null, data.is_active)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText
                primary="Created"
                secondary={formatDate(data.created_at)}
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderJournalEntryDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Journal Entry Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><ReceiptIcon /></ListItemIcon>
              <ListItemText primary="Reference" secondary={data.reference || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText
                primary="Entry Date"
                secondary={formatDate(data.entry_date)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText primary="Status" secondary={data.status || ''} />
            </ListItem>
          </List>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Financial Details</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><MoneyIcon /></ListItemIcon>
              <ListItemText
                primary="Total Debit"
                secondary={formatCurrency(data.total_debit)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><MoneyIcon /></ListItemIcon>
              <ListItemText
                primary="Total Credit"
                secondary={formatCurrency(data.total_credit)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText
                primary="Created"
                secondary={formatDate(data.created_at)}
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>

      {data.description && (
        <Grid item xs={12}>
          <Paper elevation={1} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Description</Typography>
            <Typography variant="body2" color="text.secondary">
              {data.description}
            </Typography>
          </Paper>
        </Grid>
      )}
    </Grid>
  );

  const renderWarehouseDetails = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Warehouse Information</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><WarehouseIcon /></ListItemIcon>
              <ListItemText primary="Name" secondary={data.name || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><LocationIcon /></ListItemIcon>
              <ListItemText primary="Location" secondary={data.location || ''} />
            </ListItem>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText primary="Capacity" secondary={data.capacity || ''} />
            </ListItem>
          </List>
        </Paper>
      </Grid>

      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Warehouse Details</Typography>
          <List dense>
            <ListItem>
              <ListItemIcon><AssessmentIcon /></ListItemIcon>
              <ListItemText
                primary="Status"
                secondary={renderStatusChip(null, data.is_active)}
              />
            </ListItem>
            <ListItem>
              <ListItemIcon><CalendarIcon /></ListItemIcon>
              <ListItemText
                primary="Created"
                secondary={formatDate(data.created_at)}
              />
            </ListItem>
          </List>
        </Paper>
      </Grid>
    </Grid>
  );

  const renderContent = () => {
    switch (type) {
      case 'employee':
        return renderEmployeeDetails();
      case 'product':
        return renderProductDetails();
      case 'category':
        return renderCategoryDetails();
      case 'payroll':
        return renderPayrollDetails();
      case 'contact':
        return renderContactDetails();
      case 'lead':
        return renderLeadDetails();
      case 'opportunity':
        return renderOpportunityDetails();
      case 'account':
        return renderAccountDetails();
      case 'journal-entry':
        return renderJournalEntryDetails();
      case 'warehouse':
        return renderWarehouseDetails();
      default:
        return (
          <Box>
            <Typography variant="body1">
              {JSON.stringify(data, null, 2)}
            </Typography>
          </Box>
        );
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="md"
      fullWidth
      aria-labelledby="detail-dialog-title"
      aria-describedby="detail-dialog-content"
    >
      <DialogTitle id="detail-dialog-title">
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1}>
            {getIcon(type)}
            <Typography variant="h6">
              {title || `${type ? type.charAt(0).toUpperCase() + type.slice(1) : 'Item'} Details`}
            </Typography>
          </Box>
          <Box>
            {onEdit && (
              <Tooltip title="Edit">
                <IconButton 
                  onClick={() => onEdit(data)} 
                  size="small"
                  aria-label="edit item"
                >
                  <EditIcon />
                </IconButton>
              </Tooltip>
            )}
            <Tooltip title="Close">
              <IconButton 
                onClick={onClose} 
                size="small"
                aria-label="close dialog"
              >
                <CloseIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers id="detail-dialog-content">
        {hasData ? renderContent() : (
          <Box>
            <Typography variant="body2" color="text.secondary">No data available.</Typography>
          </Box>
        )}

        {hasData && (type === 'lead' || type === 'opportunity') && (
          <Box sx={{ mt: 3 }}>
            <Paper elevation={1} sx={{ p: 2 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6">AI Insights</Typography>
                <Box>
                  <Button onClick={fetchAiForLead} disabled={aiLoading} variant="outlined" size="small" sx={{ mr: 1 }}>
                    {aiLoading ? 'Loading…' : 'Refresh'}
                  </Button>
                  <Button onClick={() => generateEmail('follow_up')} disabled={emailGenLoading} variant="contained" size="small">
                    {emailGenLoading ? 'Generating…' : 'Generate Email'}
                  </Button>
                </Box>
              </Box>

              {aiError && (
                <Typography variant="body2" color="error" sx={{ mb: 2 }}>{aiError}</Typography>
              )}

              {type === 'lead' && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Score</Typography>
                  <Chip 
                    label={aiScore !== null ? aiScore : (typeof data.score === 'number' ? data.score : '—')} 
                    color={
                      ((aiScore ?? data.score) >= 80) ? 'success' : ((aiScore ?? data.score) >= 50 ? 'info' : 'default')
                    }
                    size="small"
                  />
                </Box>
              )}

              {type === 'lead' && aiReasons?.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>Why this score</Typography>
                  <List dense>
                    {aiReasons.map((r, idx) => (
                      <ListItem key={`reason-${idx}`}>
                        <ListItemText primary={r} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {aiActions?.length > 0 && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>Suggested next actions</Typography>
                  <List dense>
                    {aiActions.map((a, idx) => (
                      <ListItem key={`nba-${idx}`}>
                        <ListItemText 
                          primary={a.title}
                          secondary={`${a.description}${typeof a.dueInDays === 'number' ? ` · Due in ${a.dueInDays} day(s)` : ''}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {emailDraft && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>Email Draft</Typography>
                  <TextField
                    label="Subject"
                    fullWidth
                    size="small"
                    value={emailDraft.subject || ''}
                    onChange={(e) => setEmailDraft({ ...emailDraft, subject: e.target.value })}
                    sx={{ mb: 1 }}
                  />
                  <TextField
                    label="Body"
                    fullWidth
                    multiline
                    minRows={6}
                    value={emailDraft.body || ''}
                    onChange={(e) => setEmailDraft({ ...emailDraft, body: e.target.value })}
                  />
                </Box>
              )}
            </Paper>
          </Box>
        )}

        {hasData && type === 'opportunity' && (
          <Box sx={{ mt: 3 }}>
            <Paper elevation={1} sx={{ p: 2 }}>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                <Typography variant="h6">Deal Line Items</Typography>
                <Box>
                  <Button onClick={addDealItem} variant="outlined" size="small" sx={{ mr: 1 }}>Add Item</Button>
                  <Button onClick={saveDealItems} disabled={savingItems} variant="contained" size="small">{savingItems ? 'Saving…' : 'Save'}</Button>
                </Box>
              </Box>
              <Box sx={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr 0.8fr 0.8fr 0.6fr', gap: 1 }}>
                <Typography variant="caption" color="text.secondary">SKU</Typography>
                <Typography variant="caption" color="text.secondary">Name</Typography>
                <Typography variant="caption" color="text.secondary">Qty</Typography>
                <Typography variant="caption" color="text.secondary">Unit Price</Typography>
                <Typography variant="caption" color="text.secondary">Actions</Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 1 }}>
                {dealItems.map((it, idx) => (
                  <Box key={`it-${idx}`} sx={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr 0.8fr 0.8fr 0.6fr', gap: 1 }}>
                    <TextField value={it.sku} size="small" onChange={(e) => updateDealItem(idx, 'sku', e.target.value)} />
                    <TextField value={it.name} size="small" onChange={(e) => updateDealItem(idx, 'name', e.target.value)} />
                    <TextField type="number" value={it.quantity} size="small" onChange={(e) => updateDealItem(idx, 'quantity', Number(e.target.value))} />
                    <TextField type="number" value={it.unit_price} size="small" onChange={(e) => updateDealItem(idx, 'unit_price', Number(e.target.value))} />
                    <Button color="error" size="small" onClick={() => removeDealItem(idx)}>Remove</Button>
                  </Box>
                ))}
                {dealItems.length === 0 && (
                  <Typography variant="body2" color="text.secondary">No items. Click Add Item.</Typography>
                )}
              </Box>
            </Paper>
          </Box>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} aria-label="close dialog">Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default DetailViewModal;
