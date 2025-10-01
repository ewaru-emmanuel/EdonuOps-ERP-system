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
  Security as SecurityIcon, VerifiedUser, Warning as WarningIcon, Error as ErrorIcon, CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon, CalendarToday as CalendarIcon, Notifications as NotificationsIcon, Download as DownloadIcon,
  History, TrackChanges, Timeline as TimelineIcon2, ShowChart as ShowChartIcon2, TrendingUp as TrendingUpIcon3,
  Person, Computer, Lock as LockIcon, Visibility as VisibilityIcon, Edit as EditIcon, Delete as DeleteIcon,
  Add as AddIcon, Save as SaveIcon, Cancel as CancelIcon, Refresh as RefreshIcon, FilterList as FilterListIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const SmartAuditTrail = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectedAuditRecord, setSelectedAuditRecord] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [filterUser, setFilterUser] = useState('all');
  const [filterAction, setFilterAction] = useState('all');
  const [filterModule, setFilterModule] = useState('all');
  const [filterPaymentMethod, setFilterPaymentMethod] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('timestamp');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [dateRange, setDateRange] = useState('last_7_days');

  // Data hooks
  const { data: auditTrail, loading: auditLoading, error: auditError } = useRealTimeData('/api/finance/audit-trail');
  const { data: userActivity, loading: userLoading, error: userError } = useRealTimeData('/api/finance/user-activity');
  const { data: complianceReports, loading: complianceLoading, error: complianceError } = useRealTimeData('/api/finance/compliance-audit');
  const { data: paymentMethods, loading: paymentMethodsLoading } = useRealTimeData('/api/finance/payment-methods');

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!auditTrail) return {};
    
    const totalRecords = auditTrail.length;
    const todayRecords = auditTrail.filter(record => {
      const today = new Date().toDateString();
      return new Date(record.timestamp).toDateString() === today;
    }).length;
    
    const userActions = auditTrail.reduce((acc, record) => {
      acc[record.user_id] = (acc[record.user_id] || 0) + 1;
      return acc;
    }, {});
    
    const mostActiveUser = Object.keys(userActions).reduce((a, b) => 
      userActions[a] > userActions[b] ? a : b, '');
    
    const criticalActions = auditTrail.filter(record => 
      ['delete', 'modify', 'approve', 'reject'].includes(record.action_type)
    ).length;

    return {
      totalRecords,
      todayRecords,
      mostActiveUser,
      criticalActions
    };
  }, [auditTrail]);

  // Filter and sort audit records
  const filteredAuditTrail = useMemo(() => {
    if (!auditTrail) return [];
    
    let filtered = auditTrail.filter(record => {
      const matchesUser = filterUser === 'all' || record.user_id === filterUser;
      const matchesAction = filterAction === 'all' || record.action_type === filterAction;
      const matchesModule = filterModule === 'all' || record.module === filterModule;
      const matchesPaymentMethod = filterPaymentMethod === 'all' || 
        (record.changes && record.changes.includes(filterPaymentMethod)) ||
        (record.description?.toLowerCase() || '').includes(filterPaymentMethod.toLowerCase());
      const matchesSearch = (record.description?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                           (record.user_name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
                           (record.ip_address || '').includes(searchTerm) ||
                           (record.payment_method?.toLowerCase() || '').includes(searchTerm.toLowerCase());
      return matchesUser && matchesAction && matchesModule && matchesPaymentMethod && matchesSearch;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue = a[sortBy] || '';
      let bValue = b[sortBy] || '';
      
      if (sortBy === 'timestamp') {
        aValue = new Date(aValue);
        bValue = new Date(bValue);
      } else if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [auditTrail, filterUser, filterAction, filterModule, filterPaymentMethod, searchTerm, sortBy, sortOrder]);

  const handleSort = (property) => {
    const isAsc = sortBy === property && sortOrder === 'asc';
    setSortOrder(isAsc ? 'desc' : 'asc');
    setSortBy(property);
  };

  const getActionColor = (actionType) => {
    switch (actionType) {
      case 'create': return 'success';
      case 'update': return 'info';
      case 'delete': return 'error';
      case 'view': return 'default';
      case 'approve': return 'success';
      case 'reject': return 'error';
      case 'login': return 'primary';
      case 'logout': return 'default';
      default: return 'default';
    }
  };

  const getActionIcon = (actionType) => {
    switch (actionType) {
      case 'create': return <AddIcon />;
      case 'update': return <EditIcon />;
      case 'delete': return <DeleteIcon />;
      case 'view': return <VisibilityIcon />;
      case 'approve': return <CheckCircleIcon />;
      case 'reject': return <ErrorIcon />;
      case 'login': return <LockIcon />;
      case 'logout': return <LockIcon />;
      default: return <Info />;
    }
  };

  const getSeverityLevel = (actionType) => {
    switch (actionType) {
      case 'delete': return 'high';
      case 'approve': return 'medium';
      case 'reject': return 'medium';
      case 'modify': return 'medium';
      default: return 'low';
    }
  };

  const renderAuditMetrics = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  {metrics.totalRecords || 0}
                </Typography>
                <Typography variant="body2">Total Audit Records</Typography>
              </Box>
              <History sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'success.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  {metrics.todayRecords || 0}
                </Typography>
                <Typography variant="body2">Today's Activities</Typography>
              </Box>
              <ScheduleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'warning.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  {metrics.criticalActions || 0}
                </Typography>
                <Typography variant="body2">Critical Actions</Typography>
              </Box>
              <WarningIcon sx={{ fontSize: 40, opacity: 0.8 }} />
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
                  {auditTrail?.filter(record => record.action_type === 'login').length || 0}
                </Typography>
                <Typography variant="body2">Active Sessions</Typography>
              </Box>
              <SecurityIcon sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderAuditTable = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Audit Trail</Typography>
          <Box display="flex" gap={1}>
            <TextField
              size="small"
              placeholder="Search audit records..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>User</InputLabel>
              <Select
                value={filterUser}
                onChange={(e) => setFilterUser(e.target.value)}
                label="User"
              >
                <MenuItem value="all">All Users</MenuItem>
                <MenuItem value="admin">Admin</MenuItem>
                <MenuItem value="manager">Manager</MenuItem>
                <MenuItem value="accountant">Accountant</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Action</InputLabel>
              <Select
                value={filterAction}
                onChange={(e) => setFilterAction(e.target.value)}
                label="Action"
              >
                <MenuItem value="all">All Actions</MenuItem>
                <MenuItem value="create">Create</MenuItem>
                <MenuItem value="update">Update</MenuItem>
                <MenuItem value="delete">Delete</MenuItem>
                <MenuItem value="view">View</MenuItem>
                <MenuItem value="approve">Approve</MenuItem>
                <MenuItem value="reject">Reject</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Module</InputLabel>
              <Select
                value={filterModule}
                onChange={(e) => setFilterModule(e.target.value)}
                label="Module"
              >
                <MenuItem value="all">All Modules</MenuItem>
                <MenuItem value="general_ledger">General Ledger</MenuItem>
                <MenuItem value="accounts_payable">Accounts Payable</MenuItem>
                <MenuItem value="accounts_receivable">Accounts Receivable</MenuItem>
                <MenuItem value="fixed_assets">Fixed Assets</MenuItem>
                <MenuItem value="tax_management">Tax Management</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>

        {auditLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={60} />
            ))}
          </Box>
        ) : (
          <>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'timestamp'}
                        direction={sortBy === 'timestamp' ? sortOrder : 'asc'}
                        onClick={() => handleSort('timestamp')}
                      >
                        Timestamp
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>User</TableCell>
                    <TableCell>Action</TableCell>
                    <TableCell>Module</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>IP Address</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredAuditTrail
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((record) => (
                    <TableRow key={record.id} hover>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">
                            {new Date(record.timestamp).toLocaleDateString()}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {new Date(record.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                            {record.user_name?.charAt(0) || 'U'}
                          </Avatar>
                          <Typography variant="body2">
                            {record.user_name || 'Unknown User'}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={record.action_type} 
                          color={getActionColor(record.action_type)}
                          size="small"
                          icon={getActionIcon(record.action_type)}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={record.module} 
                          size="small" 
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ maxWidth: 200 }}>
                          {record.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace" fontSize="0.75rem">
                          {record.ip_address}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={getSeverityLevel(record.action_type)} 
                          color={getSeverityLevel(record.action_type) === 'high' ? 'error' : 
                                 getSeverityLevel(record.action_type) === 'medium' ? 'warning' : 'success'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={0.5}>
                          <Tooltip title="View Details">
                            <IconButton 
                              size="small"
                              onClick={() => {
                                setSelectedAuditRecord(record);
                                setDetailViewOpen(true);
                              }}
                            >
                              <Visibility fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Export Record">
                            <IconButton size="small">
                              <Download fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            
            <TablePagination
              component="div"
              count={filteredAuditTrail.length}
              page={page}
              onPageChange={(e, newPage) => setPage(newPage)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
            />
          </>
        )}
      </CardContent>
    </Card>
  );

  const renderUserActivity = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>User Activity Summary</Typography>
        {userLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={80} />
            ))}
          </Box>
        ) : (
          <List>
            {userActivity?.slice(0, 5).map((activity) => (
              <ListItem key={activity.id} divider>
                <ListItemIcon>
                  <Avatar sx={{ bgcolor: 'primary.main' }}>
                    {activity.user_name?.charAt(0) || 'U'}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={activity.user_name}
                  secondary={
                    <span>
                      <span style={{ display: 'block', fontSize: '0.875rem' }}>
                        Last activity: {new Date(activity.last_activity).toLocaleString()}
                      </span>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'rgba(0, 0, 0, 0.6)' }}>
                        {activity.action_count} actions today
                      </span>
                    </span>
                  }
                />
                <Chip 
                  label={activity.status} 
                  color={activity.status === 'active' ? 'success' : 'default'}
                  size="small"
                />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );

  const renderComplianceSummary = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Compliance Summary</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box textAlign="center" p={2}>
              <Typography variant="h4" color="success.main">
                {complianceReports?.filter(report => report.status === 'compliant').length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Compliant Records
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box textAlign="center" p={2}>
              <Typography variant="h4" color="warning.main">
                {complianceReports?.filter(report => report.status === 'review_required').length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Review Required
              </Typography>
            </Box>
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="subtitle2" mb={1}>Recent Compliance Checks</Typography>
        {complianceLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={60} />
            ))}
          </Box>
        ) : (
          <List dense>
            {complianceReports?.slice(0, 5).map((report) => (
              <ListItem key={report.id} divider>
                <ListItemIcon>
                  <VerifiedUser color={report.status === 'compliant' ? 'success' : 'warning'} />
                </ListItemIcon>
                <ListItemText
                  primary={report.check_type}
                  secondary={
                    <span>
                      <span style={{ display: 'block', fontSize: '0.875rem' }}>
                        {report.description}
                      </span>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'rgba(0, 0, 0, 0.6)' }}>
                        {new Date(report.check_date).toLocaleDateString()}
                      </span>
                    </span>
                  }
                />
                <Chip 
                  label={report.status} 
                  color={report.status === 'compliant' ? 'success' : 'warning'}
                  size="small"
                />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );

  const renderAuditActions = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Audit Actions</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Download />}
              onClick={() => setSnackbar({ open: true, message: 'Exporting audit trail...', severity: 'info' })}
            >
              Export Audit Trail
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<TrackChanges />}
              onClick={() => setSnackbar({ open: true, message: 'Generating compliance report...', severity: 'info' })}
            >
              Compliance Report
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Security />}
              onClick={() => setSnackbar({ open: true, message: 'Running security audit...', severity: 'info' })}
            >
              Security Audit
            </Button>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<Timeline />}
              onClick={() => setSnackbar({ open: true, message: 'Generating activity timeline...', severity: 'info' })}
            >
              Activity Timeline
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Audit Trail & Compliance
      </Typography>
      
      {renderAuditMetrics()}
      
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          {renderAuditTable()}
        </Grid>
        <Grid item xs={12} lg={4}>
          <Box display="flex" flexDirection="column" gap={3}>
            {renderUserActivity()}
            {renderComplianceSummary()}
            {renderAuditActions()}
          </Box>
        </Grid>
      </Grid>

      {/* Detail View Modal */}
      <Dialog 
        open={detailViewOpen} 
        onClose={() => setDetailViewOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Audit Record Details
        </DialogTitle>
        <DialogContent>
          {selectedAuditRecord && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Record Information</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Timestamp" 
                      secondary={new Date(selectedAuditRecord.timestamp).toLocaleString()} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="User" 
                      secondary={selectedAuditRecord.user_name} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Action Type" 
                      secondary={selectedAuditRecord.action_type} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Module" 
                      secondary={selectedAuditRecord.module} 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Technical Details</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="IP Address" 
                      secondary={selectedAuditRecord.ip_address} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="User Agent" 
                      secondary={selectedAuditRecord.user_agent || 'Not available'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Session ID" 
                      secondary={selectedAuditRecord.session_id || 'Not available'} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Severity" 
                      secondary={getSeverityLevel(selectedAuditRecord.action_type)} 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="subtitle2" color="text.secondary">Description</Typography>
                <Typography variant="body2" sx={{ mt: 1, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  {selectedAuditRecord.description}
                </Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailViewOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

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

export default SmartAuditTrail;

