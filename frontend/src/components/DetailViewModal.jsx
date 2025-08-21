import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
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
  if (!data) return null;

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
                secondary={
                  <Box component="span">
                    <Chip 
                      label={data.status || 'Active'} 
                      color={data.status === 'active' ? 'success' : 'default'}
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
                secondary={
                  <Box component="span">
                    <Chip 
                      label={data.is_active ? 'Active' : 'Inactive'} 
                      color={data.is_active ? 'success' : 'default'}
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
                secondary={
                  <Box component="span">
                    <Chip 
                      label={data.is_active ? 'Active' : 'Inactive'} 
                      color={data.is_active ? 'success' : 'default'}
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
                  <Box component="span">
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
                secondary={
                  <Box component="span">
                    <Chip
                      label={data.status || 'Active'}
                      color={data.status === 'active' ? 'success' : 'default'}
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
                  <Box component="span">
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
                secondary={
                  <Box component="span">
                    <Chip
                      label={data.is_active ? 'Active' : 'Inactive'}
                      color={data.is_active ? 'success' : 'default'}
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
                secondary={
                  <Box component="span">
                    <Chip
                      label={data.is_active ? 'Active' : 'Inactive'}
                      color={data.is_active ? 'success' : 'default'}
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
        {renderContent()}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} aria-label="close dialog">Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default DetailViewModal;
