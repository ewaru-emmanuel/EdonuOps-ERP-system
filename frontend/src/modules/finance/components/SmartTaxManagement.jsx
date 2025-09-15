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
  Receipt as ReceiptIcon, LocalTaxi as TaxIcon, Assessment as AssessmentIcon, Gavel, Policy, Security as SecurityIcon,
  HomeRepairService, LocalShipping, Upload,
  VerifiedUser, Warning as WarningIcon, Error as ErrorIcon, CheckCircle as CheckCircleIcon, Schedule as ScheduleIcon,
  CalendarToday as CalendarIcon, Notifications as NotificationsIcon, Download as DownloadIcon, Upload as UploadIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const SmartTaxManagement = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectedTaxRecord, setSelectedTaxRecord] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [filingDialogOpen, setFilingDialogOpen] = useState(false);
  const [complianceDialogOpen, setComplianceDialogOpen] = useState(false);
  const [filterJurisdiction, setFilterJurisdiction] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('due_date');
  const [sortOrder, setSortOrder] = useState('asc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Data hooks
  const { data: taxRecords, loading: taxLoading, error: taxError } = useRealTimeData('/api/finance/tax-records');
  const { data: taxFilingHistory, loading: filingLoading, error: filingError } = useRealTimeData('/api/finance/tax-filing-history');
  const { data: complianceReports, loading: complianceLoading, error: complianceError } = useRealTimeData('/api/finance/compliance-reports');

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!taxRecords) return {};
    
    const totalTaxLiability = taxRecords.reduce((sum, record) => sum + (record.tax_amount || 0), 0);
    const paidTaxes = taxRecords.filter(record => record.status === 'paid').reduce((sum, record) => sum + (record.tax_amount || 0), 0);
    const pendingTaxes = taxRecords.filter(record => record.status === 'pending').reduce((sum, record) => sum + (record.tax_amount || 0), 0);
    const overdueTaxes = taxRecords.filter(record => record.status === 'overdue').reduce((sum, record) => sum + (record.tax_amount || 0), 0);
    
    const upcomingFiling = taxRecords.filter(record => {
      const dueDate = new Date(record.due_date);
      const today = new Date();
      const daysUntilDue = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
      return daysUntilDue > 0 && daysUntilDue <= 30;
    }).length;

    const complianceScore = taxRecords.filter(record => record.status === 'filed' || record.status === 'paid').length / taxRecords.length * 100;

    return {
      totalTaxLiability,
      paidTaxes,
      pendingTaxes,
      overdueTaxes,
      upcomingFiling,
      complianceScore
    };
  }, [taxRecords]);

  // Filter and sort tax records
  const filteredTaxRecords = useMemo(() => {
    if (!taxRecords) return [];
    
    let filtered = taxRecords.filter(record => {
      const matchesJurisdiction = filterJurisdiction === 'all' || record.jurisdiction === filterJurisdiction;
      const matchesStatus = filterStatus === 'all' || record.status === filterStatus;
      const matchesSearch = record.tax_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           record.jurisdiction.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           record.reference_number?.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesJurisdiction && matchesStatus && matchesSearch;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue = a[sortBy];
      let bValue = b[sortBy];
      
      if (sortBy === 'due_date') {
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
  }, [taxRecords, filterJurisdiction, filterStatus, searchTerm, sortBy, sortOrder]);

  const handleSort = (property) => {
    const isAsc = sortBy === property && sortOrder === 'asc';
    setSortOrder(isAsc ? 'desc' : 'asc');
    setSortBy(property);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid': return 'success';
      case 'pending': return 'warning';
      case 'overdue': return 'error';
      case 'filed': return 'info';
      case 'draft': return 'default';
      default: return 'default';
    }
  };

  const getTaxTypeIcon = (taxType) => {
    switch (taxType.toLowerCase()) {
      case 'vat': return <ReceiptIcon />;
      case 'gst': return <ReceiptIcon />;
      case 'sales tax': return <ReceiptIcon />;
      case 'income tax': return <AssessmentIcon />;
      case 'corporate tax': return <Business />;
      case 'property tax': return <HomeRepairService />;
      case 'excise tax': return <LocalShipping />;
      default: return <TaxIcon />;
    }
  };

  const getDaysUntilDue = (dueDate) => {
    const due = new Date(dueDate);
    const today = new Date();
    const days = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
    return days;
  };

  const renderTaxMetrics = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  ${(metrics.totalTaxLiability || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Total Tax Liability</Typography>
              </Box>
              <TaxIcon sx={{ fontSize: 40, opacity: 0.8 }} />
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
                  ${(metrics.paidTaxes || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Paid Taxes</Typography>
              </Box>
              <CheckCircle sx={{ fontSize: 40, opacity: 0.8 }} />
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
                  ${(metrics.pendingTaxes || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Pending Taxes</Typography>
              </Box>
              <Schedule sx={{ fontSize: 40, opacity: 0.8 }} />
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
                  ${(metrics.overdueTaxes || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Overdue Taxes</Typography>
              </Box>
              <Warning sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderTaxTable = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Tax Records</Typography>
          <Box display="flex" gap={1}>
            <TextField
              size="small"
              placeholder="Search taxes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Jurisdiction</InputLabel>
              <Select
                value={filterJurisdiction}
                onChange={(e) => setFilterJurisdiction(e.target.value)}
                label="Jurisdiction"
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="federal">Federal</MenuItem>
                <MenuItem value="state">State</MenuItem>
                <MenuItem value="local">Local</MenuItem>
                <MenuItem value="international">International</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                label="Status"
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="paid">Paid</MenuItem>
                <MenuItem value="overdue">Overdue</MenuItem>
                <MenuItem value="filed">Filed</MenuItem>
                <MenuItem value="draft">Draft</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>

        {taxLoading ? (
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
                        active={sortBy === 'tax_type'}
                        direction={sortBy === 'tax_type' ? sortOrder : 'asc'}
                        onClick={() => handleSort('tax_type')}
                      >
                        Tax Type
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>Jurisdiction</TableCell>
                    <TableCell>Reference</TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'tax_amount'}
                        direction={sortBy === 'tax_amount' ? sortOrder : 'asc'}
                        onClick={() => handleSort('tax_amount')}
                      >
                        Amount
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortBy === 'due_date'}
                        direction={sortBy === 'due_date' ? sortOrder : 'asc'}
                        onClick={() => handleSort('due_date')}
                      >
                        Due Date
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredTaxRecords
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((record) => {
                      const daysUntilDue = getDaysUntilDue(record.due_date);
                      return (
                        <TableRow key={record.id} hover>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                                {getTaxTypeIcon(record.tax_type)}
                              </Avatar>
                              <Box>
                                <Typography variant="body2" fontWeight="medium">
                                  {record.tax_type}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {record.tax_period}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={record.jurisdiction} 
                              size="small" 
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {record.reference_number}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight="medium">
                              ${(record.tax_amount || 0).toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box>
                              <Typography variant="body2">
                                {new Date(record.due_date).toLocaleDateString()}
                              </Typography>
                              {daysUntilDue < 0 && (
                                <Typography variant="caption" color="error">
                                  {Math.abs(daysUntilDue)} days overdue
                                </Typography>
                              )}
                              {daysUntilDue >= 0 && daysUntilDue <= 30 && (
                                <Typography variant="caption" color="warning.main">
                                  {daysUntilDue} days left
                                </Typography>
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={record.status} 
                              color={getStatusColor(record.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Box display="flex" gap={0.5}>
                              <Tooltip title="View Details">
                                <IconButton 
                                  size="small"
                                  onClick={() => {
                                    setSelectedTaxRecord(record);
                                    setDetailViewOpen(true);
                                  }}
                                >
                                  <Visibility fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Edit Tax Record">
                                <IconButton size="small">
                                  <Edit fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="File Tax Return">
                                <IconButton 
                                  size="small"
                                  onClick={() => setFilingDialogOpen(true)}
                                >
                                  <Upload fontSize="small" />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Compliance Check">
                                <IconButton 
                                  size="small"
                                  onClick={() => setComplianceDialogOpen(true)}
                                >
                                  <VerifiedUser fontSize="small" />
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
            
            <TablePagination
              component="div"
              count={filteredTaxRecords.length}
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

  const renderComplianceDashboard = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Compliance Dashboard</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box textAlign="center" p={2}>
              <Typography variant="h3" color="success.main">
                {metrics.complianceScore?.toFixed(1) || 0}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Compliance Score
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box textAlign="center" p={2}>
              <Typography variant="h3" color="warning.main">
                {metrics.upcomingFiling || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Upcoming Filings (30 days)
              </Typography>
            </Box>
          </Grid>
        </Grid>
        
        <Divider sx={{ my: 2 }} />
        
        <Typography variant="subtitle2" mb={1}>Recent Compliance Activities</Typography>
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
                  primary={report.tax_type}
                  secondary={
                    <span>
                      <span style={{ display: 'block', fontSize: '0.875rem' }}>
                        {report.description}
                      </span>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'rgba(0, 0, 0, 0.6)' }}>
                        {new Date(report.report_date).toLocaleDateString()}
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

  const renderFilingHistory = () => (
    <Card>
      <CardContent>
        <Typography variant="h6" mb={2}>Filing History</Typography>
        {filingLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={80} />
            ))}
          </Box>
        ) : (
          <List>
            {taxFilingHistory?.slice(0, 5).map((filing) => (
              <ListItem key={filing.id} divider>
                <ListItemIcon>
                  <Upload color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={filing.tax_type}
                  secondary={
                    <span>
                      <span style={{ display: 'block', fontSize: '0.875rem' }}>
                        Filed: {new Date(filing.filing_date).toLocaleDateString()}
                      </span>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'rgba(0, 0, 0, 0.6)' }}>
                        Reference: {filing.reference_number}
                      </span>
                    </span>
                  }
                />
                <Box display="flex" flexDirection="column" alignItems="flex-end">
                  <Typography variant="body2" fontWeight="medium">
                    ${(filing.amount || 0).toLocaleString()}
                  </Typography>
                  <Chip 
                    label={filing.status} 
                    color={filing.status === 'accepted' ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Tax Management
      </Typography>
      
      {renderTaxMetrics()}
      
      {/* Statutory Modules Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Statutory Compliance Modules
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <LocalTaxi color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="subtitle2">Income Tax</Typography>
                  <Chip label="Active" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Receipt color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="subtitle2">Sales Tax</Typography>
                  <Chip label="Active" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <Business color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="subtitle2">Payroll Tax</Typography>
                  <Chip label="Inactive" color="default" size="small" />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center' }}>
                  <AccountBalance color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography variant="subtitle2">Property Tax</Typography>
                  <Chip label="Active" color="success" size="small" />
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          {renderTaxTable()}
        </Grid>
        <Grid item xs={12} lg={4}>
          <Box display="flex" flexDirection="column" gap={3}>
            {renderComplianceDashboard()}
            {renderFilingHistory()}
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
          Tax Record Details - {selectedTaxRecord?.tax_type}
        </DialogTitle>
        <DialogContent>
          {selectedTaxRecord && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Tax Information</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Tax Type" 
                      secondary={selectedTaxRecord.tax_type} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Jurisdiction" 
                      secondary={selectedTaxRecord.jurisdiction} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Tax Period" 
                      secondary={selectedTaxRecord.tax_period} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Reference Number" 
                      secondary={selectedTaxRecord.reference_number} 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Financial Information</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText 
                      primary="Tax Amount" 
                      secondary={`$${(selectedTaxRecord.tax_amount || 0).toLocaleString()}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Due Date" 
                      secondary={new Date(selectedTaxRecord.due_date).toLocaleDateString()} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Status" 
                      secondary={selectedTaxRecord.status} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Days Until Due" 
                      secondary={getDaysUntilDue(selectedTaxRecord.due_date)} 
                    />
                  </ListItem>
                </List>
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

export default SmartTaxManagement;
