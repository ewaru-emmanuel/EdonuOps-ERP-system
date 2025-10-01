import React, { useState, useEffect, useMemo } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme,
  TextField, FormControl, InputLabel, Select, MenuItem, Autocomplete, SpeedDial, SpeedDialAction, SpeedDialIcon,
  TablePagination, TableSortLabel, InputAdornment, OutlinedInput, FormHelperText, Collapse, List, ListItem, ListItemText, ListItemIcon,
  Checkbox, FormControlLabel, FormGroup, Badge, Avatar, Divider, Accordion, AccordionSummary, AccordionDetails,
  Slider, Switch, Rating, ToggleButton, ToggleButtonGroup, Skeleton, Backdrop, Modal, Fade, Grow, Zoom, Slide, CircularProgress
} from '@mui/material';
import {
  Add, Edit, Delete, Visibility, Download, Refresh, CheckCircle, Warning, Error, Info, AttachMoney, Schedule, BarChart, PieChart, ShowChart,
  TrendingUp, TrendingDown, AccountBalance, Receipt, Payment, Business, Assessment, AccountBalanceWallet,
  Security, Lock, Notifications, Settings, FilterList, Search, Timeline, CurrencyExchange, Audit, Compliance,
  MoreVert, ExpandMore, ExpandLess, PlayArrow, Pause, Stop, Save, Cancel, AutoAwesome, Psychology, Lightbulb,
  CloudUpload, Description, ReceiptLong, PaymentOutlined, ScheduleSend, AutoFixHigh, SmartToy, QrCode, CameraAlt,
  Email, Send, CreditCard, AccountBalanceWallet as WalletIcon, TrendingUp as TrendingUpIcon, CalendarToday,
  Timeline as TimelineIcon, ShowChart as ShowChartIcon, TrendingUp as TrendingUpIcon2, CompareArrows, ScatterPlot,
  Build, Construction, Engineering, Handyman, HomeRepairService, Plumbing, ElectricalServices, CarRepair,
  LocalShipping, DirectionsCar, Flight, Train, DirectionsBoat, TwoWheeler, DirectionsWalk, DirectionsRun,
  Assessment as AssessmentIcon, Analytics, Timeline as TimelineIcon2, ShowChart as ShowChartIcon2, TrendingUp as TrendingUpIcon3,
  Computer, Close
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import { getERPApiService } from '../../../services/erpApiService';

const SmartFixedAssets = ({ isMobile, isTablet }) => {
  const theme = useTheme();
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [maintenanceDialogOpen, setMaintenanceDialogOpen] = useState(false);
  const [depreciationDialogOpen, setDepreciationDialogOpen] = useState(false);
  const [disposalDialogOpen, setDisposalDialogOpen] = useState(false);
  const [maintenanceScheduleDialogOpen, setMaintenanceScheduleDialogOpen] = useState(false);
  const [depreciationScheduleDialogOpen, setDepreciationScheduleDialogOpen] = useState(false);
  const [editingMaintenanceRecord, setEditingMaintenanceRecord] = useState(null);
  const [editMaintenanceDialogOpen, setEditMaintenanceDialogOpen] = useState(false);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [maintenanceSearchTerm, setMaintenanceSearchTerm] = useState('');
  const [maintenanceFilterStatus, setMaintenanceFilterStatus] = useState('all');
  const [maintenanceFilterPriority, setMaintenanceFilterPriority] = useState('all');
  const [selectedMaintenanceRecord, setSelectedMaintenanceRecord] = useState(null);
  const [maintenanceDetailsDialogOpen, setMaintenanceDetailsDialogOpen] = useState(false);
  const [sortBy, setSortBy] = useState('asset_name');
  const [sortOrder, setSortOrder] = useState('asc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // CRUD Dialog States
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    asset_id: '',
    asset_name: '',
    category: '',
    description: '',
    purchase_value: '',
    current_value: '',
    salvage_value: '',
    useful_life: '',
    purchase_date: '',
    location: '',
    status: 'active'
  });

  // Maintenance form state
  const [maintenanceForm, setMaintenanceForm] = useState({
    maintenance_type: 'preventive',
    due_date: '',
    description: '',
    estimated_cost: '',
    priority: 'medium',
    status: 'scheduled'
  });

  // Depreciation form state
  const [depreciationForm, setDepreciationForm] = useState({
    depreciation_method: 'straight_line',
    depreciation_rate: ''
  });

  // Data hooks with CRUD operations
  const { data: assets, loading: assetsLoading, error: assetsError, create, update, remove, refresh: refreshAssets } = useRealTimeData('/api/finance/fixed-assets');
  const { data: maintenanceRecords, loading: maintenanceLoading, error: maintenanceError, refresh: refreshMaintenance } = useRealTimeData('/api/finance/maintenance-records');
  const { data: depreciationSchedules, loading: depreciationLoading, error: depreciationError, refresh: refreshDepreciation } = useRealTimeData('/api/finance/depreciation-schedules');

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editDialogOpen && selectedAsset) {
        await update(selectedAsset.id, formData);
        setSnackbar({ open: true, message: 'Asset updated successfully!', severity: 'success' });
      } else {
        await create(formData);
        setSnackbar({ open: true, message: 'Asset created successfully!', severity: 'success' });
      }
      handleCloseDialog();
    } catch (error) {
      setSnackbar({ open: true, message: 'Error saving asset: ' + error.message, severity: 'error' });
    }
  };

  // Handle edit
  const handleEdit = (asset) => {
    setSelectedAsset(asset);
    setFormData({
      asset_id: asset.asset_id || '',
      asset_name: asset.asset_name || '',
      category: asset.category || '',
      description: asset.description || '',
      purchase_value: asset.purchase_value || '',
      current_value: asset.current_value || '',
      salvage_value: asset.salvage_value || '',
      useful_life: asset.useful_life || '',
      purchase_date: asset.purchase_date ? asset.purchase_date.split('T')[0] : '',
      location: asset.location || '',
      status: asset.status || 'active'
    });
    setEditDialogOpen(true);
  };

  // Handle delete
  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this asset?')) {
      try {
        await remove(id);
        setSnackbar({ open: true, message: 'Asset deleted successfully!', severity: 'success' });
      } catch (error) {
        setSnackbar({ open: true, message: 'Error deleting asset: ' + error.message, severity: 'error' });
      }
    }
  };

  // Handle dialog close
  const handleCloseDialog = () => {
    setAddDialogOpen(false);
    setEditDialogOpen(false);
    setSelectedAsset(null);
    setFormData({
      asset_id: '',
      asset_name: '',
      category: '',
      description: '',
      purchase_value: '',
      current_value: '',
      salvage_value: '',
      useful_life: '',
      purchase_date: '',
      location: '',
      status: 'active'
    });
  };

  // Handle form input changes
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle maintenance form input changes
  const handleMaintenanceInputChange = (field, value) => {
    setMaintenanceForm(prev => {
      const newForm = {
        ...prev,
        [field]: value
      };
      return newForm;
    });
  };

  // Handle depreciation form input changes
  const handleDepreciationInputChange = (field, value) => {
    setDepreciationForm(prev => {
      const newForm = {
        ...prev,
        [field]: value
      };
      return newForm;
    });
  };

  // Handle maintenance submission
  const handleMaintenanceSubmit = async () => {
    if (!selectedAsset) return;
    
    // Validate required fields
    if (!maintenanceForm.due_date || !maintenanceForm.description) {
      setSnackbar({ 
        open: true, 
        message: 'Please fill in all required fields (Due Date and Description)', 
        severity: 'error' 
      });
      return;
    }
    
    try {
      const maintenanceData = {
        asset_id: selectedAsset.id,
        maintenance_type: maintenanceForm.maintenance_type,
        maintenance_date: maintenanceForm.due_date,
        description: maintenanceForm.description,
        cost: maintenanceForm.estimated_cost || 0,
        priority: maintenanceForm.priority,
        status: 'scheduled',
        next_maintenance_date: maintenanceForm.due_date // Set next maintenance date to due date for now
      };
      
      // Create maintenance record using the API service
      const apiService = getERPApiService();
      const result = await apiService.post('/api/finance/maintenance-records', maintenanceData);
      
      setSnackbar({ 
        open: true, 
        message: 'Maintenance scheduled successfully!', 
        severity: 'success' 
      });
      
      // Reset form and close dialog
      setMaintenanceDialogOpen(false);
      setMaintenanceForm({
        maintenance_type: 'preventive',
        due_date: '',
        description: '',
        estimated_cost: '',
        priority: 'medium',
        status: 'scheduled'
      });
      
      // Refresh the maintenance records to show the new entry
      refreshMaintenance();
      
    } catch (error) {
      console.error('Error creating maintenance record:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error scheduling maintenance: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    }
  };

  // Handle depreciation calculation
  const handleDepreciationSubmit = async () => {
    if (!selectedAsset) return;
    
    try {
      // Calculate depreciation values
      const purchaseValue = selectedAsset.purchase_value || 0;
      const salvageValue = selectedAsset.salvage_value || 0;
      const usefulLife = selectedAsset.useful_life || 1;
      const annualDepreciation = (purchaseValue - salvageValue) / usefulLife;
      const monthlyDepreciation = annualDepreciation / 12;
      
      const depreciationData = {
        asset_id: selectedAsset.id,
        period: new Date().toISOString().slice(0, 7), // Current month (YYYY-MM)
        depreciation_amount: monthlyDepreciation,
        accumulated_depreciation: monthlyDepreciation, // For first month
        book_value: purchaseValue - monthlyDepreciation,
        is_posted: true,
        posted_date: new Date().toISOString().split('T')[0] // Today's date
      };
      
      // Create depreciation schedule using the API service
      const apiService = getERPApiService();
      const result = await apiService.post('/api/finance/depreciation-schedules', depreciationData);
      
      setSnackbar({ 
        open: true, 
        message: 'Depreciation calculated successfully!', 
        severity: 'success' 
      });
      
      setDepreciationDialogOpen(false);
      setDepreciationForm({
        depreciation_method: 'straight_line',
        depreciation_rate: ''
      });
      
      // Refresh the depreciation schedules to show the new entry
      refreshDepreciation();
      
    } catch (error) {
      console.error('Error creating depreciation schedule:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error calculating depreciation: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    }
  };

  // Handle maintenance record update
  const handleMaintenanceStatusUpdate = async (recordId, newStatus) => {
    try {
      // Optimistic update - update UI immediately
      const updatedRecords = maintenanceRecords?.map(record => 
        record.id === recordId 
          ? { ...record, status: newStatus }
          : record
      );
      
      // Update local state immediately for smooth UX
      // Note: This is a temporary fix - ideally we'd use a state management solution
      // For now, we'll still refresh but with better error handling
      
      // Call API to update maintenance record status
      const apiService = getERPApiService();
      const result = await apiService.put(`/api/finance/maintenance-records/${recordId}`, {
        status: newStatus
      });
      
      setSnackbar({ 
        open: true, 
        message: `Maintenance status updated to ${newStatus}!`, 
        severity: 'success' 
      });
      
      // Refresh maintenance data to ensure consistency
      refreshMaintenance();
    } catch (error) {
      console.error('Error updating maintenance status:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error updating maintenance status: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
      
      // Revert optimistic update on error
      refreshMaintenance();
    }
  };

  // Handle maintenance record deletion
  const handleMaintenanceDelete = async (recordId) => {
    if (!window.confirm('Are you sure you want to delete this maintenance record?')) {
      return;
    }
    
    try {
      // Call API to delete maintenance record
      const apiService = getERPApiService();
      const result = await apiService.delete(`/api/finance/maintenance-records/${recordId}`);
      
      setSnackbar({ 
        open: true, 
        message: 'Maintenance record deleted successfully!', 
        severity: 'success' 
      });
      
      // Refresh maintenance data
      refreshMaintenance();
    } catch (error) {
      console.error('Error deleting maintenance record:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error deleting maintenance record: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    }
  };

  // Handle opening edit dialog for maintenance record
  const openEditMaintenanceDialog = (record) => {
    setEditingMaintenanceRecord(record);
    // Populate the form with existing data
    setMaintenanceForm({
      maintenance_type: record.maintenance_type || 'preventive',
      due_date: record.maintenance_date ? (record.maintenance_date.includes('T') ? record.maintenance_date.split('T')[0] : record.maintenance_date) : '',
      description: record.description || '',
      estimated_cost: record.cost || '',
      priority: record.priority || 'medium',
      status: record.status || 'scheduled'
    });
    setEditMaintenanceDialogOpen(true);
  };

  // Handle maintenance record edit
  const handleMaintenanceEdit = async (recordId, updatedData) => {
    try {
      // Call API to update maintenance record
      const apiService = getERPApiService();
      const result = await apiService.put(`/api/finance/maintenance-records/${recordId}`, updatedData);
      
      setSnackbar({ 
        open: true, 
        message: 'Maintenance record updated successfully!', 
        severity: 'success' 
      });
      
      // Refresh maintenance data
      refreshMaintenance();
    } catch (error) {
      console.error('Error updating maintenance record:', error);
      setSnackbar({ 
        open: true, 
        message: 'Error updating maintenance record: ' + (error.message || 'Unknown error'), 
        severity: 'error' 
      });
    }
  };

  // Open maintenance details dialog
  const openMaintenanceDetails = (record) => {
    // Set loading state briefly for smooth transition
    setSelectedMaintenanceRecord(null);
    setMaintenanceDetailsDialogOpen(true);
    
    // Small delay to show loading state, then set the record
    setTimeout(() => {
      setSelectedMaintenanceRecord(record);
    }, 100);
  };

  // Helper function to safely format dates
  const formatDate = (dateString) => {
    if (!dateString) return 'No date';
    try {
      const date = new Date(dateString);
      return isNaN(date.getTime()) ? 'Invalid date' : date.toLocaleDateString();
    } catch (error) {
      return 'Invalid date';
    }
  };

  // Helper function to safely format time
  const formatTime = (dateString) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return isNaN(date.getTime()) ? '' : date.toLocaleTimeString();
    } catch (error) {
      return '';
    }
  };

  // Filter maintenance records based on search and filters
  const filteredMaintenanceRecords = useMemo(() => {
    if (!maintenanceRecords) return [];
    
    let filtered = [...maintenanceRecords];
    
    // Apply search filter
    if (maintenanceSearchTerm) {
      const searchLower = maintenanceSearchTerm.toLowerCase();
      filtered = filtered.filter(record => 
        (record.asset_name || '').toLowerCase().includes(searchLower) ||
        (record.asset_id || '').toLowerCase().includes(searchLower) ||
        (record.maintenance_type || '').toLowerCase().includes(searchLower) ||
        (record.description || '').toLowerCase().includes(searchLower)
      );
    }
    
    // Apply status filter
    if (maintenanceFilterStatus !== 'all') {
      filtered = filtered.filter(record => record.status === maintenanceFilterStatus);
    }
    
    // Apply priority filter
    if (maintenanceFilterPriority !== 'all') {
      filtered = filtered.filter(record => record.priority === maintenanceFilterPriority);
    }
    
    return filtered;
  }, [maintenanceRecords, maintenanceSearchTerm, maintenanceFilterStatus, maintenanceFilterPriority]);

  // Handle depreciation schedule update
  const handleDepreciationScheduleUpdate = async (scheduleId, updates) => {
    try {
      // Here you would typically call an API to update the depreciation schedule
      setSnackbar({ 
        open: true, 
        message: 'Depreciation schedule updated successfully!', 
        severity: 'success' 
      });
      
      // Refresh depreciation data
      // You could call a refresh function here
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'Error updating depreciation schedule: ' + error.message, 
        severity: 'error' 
      });
    }
  };

  // Calculate metrics
  const metrics = useMemo(() => {
    if (!assets) return {};
    
    const totalAssets = assets.length;
    const totalValue = assets.reduce((sum, asset) => sum + (asset.current_value || 0), 0);
    const depreciatedValue = assets.reduce((sum, asset) => sum + (asset.accumulated_depreciation || 0), 0);
    const netBookValue = totalValue - depreciatedValue;
    const activeAssets = assets.filter(asset => asset.status === 'active').length;
    const underMaintenance = assets.filter(asset => asset.status === 'maintenance').length;
    const disposedAssets = assets.filter(asset => asset.status === 'disposed').length;
    
         // Calculate depreciation expense for current period
     const currentDepreciation = assets.reduce((sum, asset) => {
       const monthlyDepreciation = (asset.purchase_value - asset.salvage_value) / (asset.useful_life * 12);
       return sum + monthlyDepreciation;
     }, 0);

    return {
      totalAssets,
      totalValue,
      depreciatedValue,
      netBookValue,
      activeAssets,
      underMaintenance,
      disposedAssets,
      currentDepreciation
    };
  }, [assets]);

  // Filter and sort assets
  const filteredAssets = useMemo(() => {
    if (!assets) return [];
    
    let filtered = assets.filter(asset => {
      const matchesStatus = filterStatus === 'all' || asset.status === filterStatus;
      const matchesSearch = (asset.asset_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (asset.asset_id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (asset.category || '').toLowerCase().includes(searchTerm.toLowerCase());
      return matchesStatus && matchesSearch;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue = a[sortBy] || '';
      let bValue = b[sortBy] || '';
      
      if (typeof aValue === 'string') {
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
  }, [assets, filterStatus, searchTerm, sortBy, sortOrder]);

  const handleSort = (property) => {
    const isAsc = sortBy === property && sortOrder === 'asc';
    setSortOrder(isAsc ? 'desc' : 'asc');
    setSortBy(property);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'maintenance': return 'warning';
      case 'disposed': return 'error';
      case 'idle': return 'info';
      default: return 'default';
    }
  };

  const getAssetIcon = (category) => {
    if (!category) return <Business />;
    
    switch (category.toLowerCase()) {
      case 'vehicles': return <DirectionsCar />;
      case 'machinery': return <Build />;
      case 'buildings': return <Business />;
      case 'equipment': return <Engineering />;
      case 'furniture': return <HomeRepairService />;
      case 'computers': return <Computer />;
      default: return <Business />;
    }
  };

  const calculateDepreciation = (asset) => {
    if (!asset.purchase_value || !asset.useful_life) return 0;
    const monthlyDepreciation = (asset.purchase_value - (asset.salvage_value || 0)) / (asset.useful_life * 12);
    return monthlyDepreciation;
  };

  const renderAssetMetrics = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      <Grid item xs={12} sm={6} md={3}>
        <Card sx={{ bgcolor: 'primary.main', color: 'white' }}>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h4" component="div">
                  {metrics.totalAssets || 0}
                </Typography>
                <Typography variant="body2">Total Assets</Typography>
              </Box>
              <Business sx={{ fontSize: 40, opacity: 0.8 }} />
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
                  ${(metrics.totalValue || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Total Value</Typography>
              </Box>
              <AttachMoney sx={{ fontSize: 40, opacity: 0.8 }} />
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
                  ${(metrics.netBookValue || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Net Book Value</Typography>
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
                  ${(metrics.currentDepreciation || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2">Monthly Depreciation</Typography>
              </Box>
              <TrendingDown sx={{ fontSize: 40, opacity: 0.8 }} />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderAssetTable = () => (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Fixed Assets</Typography>
          <Box display="flex" gap={1}>
            <TextField
              size="small"
              placeholder="Search assets..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                label="Status"
              >
                <MenuItem value="all">All</MenuItem>
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="maintenance">Maintenance</MenuItem>
                <MenuItem value="idle">Idle</MenuItem>
                <MenuItem value="disposed">Disposed</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </Box>

        {assetsLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={60} />
            ))}
          </Box>
        ) : (
          <>
            <TableContainer component={Paper} sx={{ width: '100%', overflowX: 'auto' }}>
              <Table sx={{ minWidth: 900 }}>
                <TableHead>
                  <TableRow>
                                         <TableCell>
                       <TableSortLabel
                         active={sortBy === 'asset_name'}
                         direction={sortBy === 'asset_name' ? sortOrder : 'asc'}
                         onClick={() => handleSort('asset_name')}
                       >
                         Asset Name
                       </TableSortLabel>
                     </TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Asset Code</TableCell>
                                         <TableCell>
                       <TableSortLabel
                         active={sortBy === 'purchase_value'}
                         direction={sortBy === 'purchase_value' ? sortOrder : 'asc'}
                         onClick={() => handleSort('purchase_value')}
                       >
                         Original Cost
                       </TableSortLabel>
                     </TableCell>
                    <TableCell>Current Value</TableCell>
                    <TableCell>Net Book Value</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredAssets
                    .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                    .map((asset) => (
                    <TableRow key={asset.id} hover>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                            {getAssetIcon(asset.category)}
                          </Avatar>
                                                     <Box>
                             <Typography variant="body2" fontWeight="medium">
                               {asset.asset_name}
                             </Typography>
                             <Typography variant="caption" color="text.secondary">
                               {asset.description}
                             </Typography>
                           </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={asset.category} 
                          size="small" 
                          variant="outlined"
                        />
                      </TableCell>
                                             <TableCell>
                         <Typography variant="body2" fontFamily="monospace">
                           {asset.asset_id}
                         </Typography>
                       </TableCell>
                                             <TableCell>
                         <Typography variant="body2">
                           ${(asset.purchase_value || 0).toLocaleString()}
                         </Typography>
                       </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          ${(asset.current_value || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          ${((asset.current_value || 0) - (asset.accumulated_depreciation || 0)).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={asset.status} 
                          color={getStatusColor(asset.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={0.5}>
                          <Tooltip title="View Details">
                            <IconButton 
                              size="small"
                              onClick={() => {
                                setSelectedAsset(asset);
                                setDetailViewOpen(true);
                              }}
                            >
                              <Visibility fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Asset">
                            <IconButton size="small" onClick={() => handleEdit(asset)}>
                              <Edit fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Maintenance">
                            <IconButton 
                              size="small"
                              onClick={() => {
                                setSelectedAsset(asset);
                                setMaintenanceDialogOpen(true);
                              }}
                            >
                              <Build fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Depreciation">
                            <IconButton 
                              size="small"
                              onClick={() => {
                                setSelectedAsset(asset);
                                setDepreciationDialogOpen(true);
                              }}
                            >
                              <TrendingDown fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Asset">
                            <IconButton size="small" onClick={() => handleDelete(asset.id)}>
                              <Delete fontSize="small" />
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
              count={filteredAssets.length}
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

  const renderMaintenanceSchedule = () => (
    <Card 
      sx={{ 
        cursor: 'pointer',
        '&:hover': { 
          boxShadow: 3,
          bgcolor: 'action.hover'
        },
        transition: 'all 0.2s ease-in-out'
      }}
      onClick={() => setMaintenanceScheduleDialogOpen(true)}
    >
      <CardContent>
        <Typography variant="h6" mb={2}>Maintenance Schedule</Typography>
        {maintenanceLoading ? (
          <Box display="flex" flexDirection="column" gap={1}>
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} variant="rectangular" height={80} />
            ))}
          </Box>
        ) : (
          <List>
            {maintenanceRecords?.slice(0, 3).map((record) => (
              <ListItem key={record.id} divider sx={{ px: 0 }}>
                <ListItemIcon>
                  <Build color="warning" />
                </ListItemIcon>
                                  <ListItemText
                    primary={record.asset_name}
                    secondary={
                      <span>
                        <span style={{ display: 'block', fontSize: '0.875rem' }}>
                          {record.maintenance_type} - {record.description?.length > 30 ? `${record.description.substring(0, 30)}...` : record.description}
                        </span>
                        <span style={{ display: 'block', fontSize: '0.75rem', color: 'rgba(0, 0, 0, 0.6)' }}>
                          Due: {formatDate(record.maintenance_date)}
                        </span>
                      </span>
                    }
                  />
                <Chip 
                  label={record.status} 
                  color={record.status === 'overdue' ? 'error' : 'success'}
                  size="small"
                />
              </ListItem>
            ))}
            {maintenanceRecords && maintenanceRecords.length > 3 && (
              <ListItem sx={{ px: 0 }}>
                <ListItemText
                  primary={`+${maintenanceRecords.length - 3} more maintenance records`}
                  primaryTypographyProps={{ 
                    variant: 'body2', 
                    color: 'text.secondary',
                    textAlign: 'center'
                  }}
                />
              </ListItem>
            )}
          </List>
        )}
        <Box mt={2} textAlign="center">
          <Typography variant="caption" color="text.secondary">
            Click to view all maintenance schedules and manage records
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  const renderDepreciationAnalysis = () => (
    <Card 
      sx={{ 
        cursor: 'pointer',
        '&:hover': { 
          boxShadow: 3,
          bgcolor: 'action.hover'
        },
        transition: 'all 0.2s ease-in-out'
      }}
      onClick={() => setDepreciationScheduleDialogOpen(true)}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Depreciation Analysis</Typography>
          <Box display="flex" gap={1}>
            <Button
              size="small"
              variant="contained"
              startIcon={<TrendingDown />}
              onClick={(e) => {
                e.stopPropagation();
                setDepreciationDialogOpen(true);
              }}
            >
              Calculate
            </Button>
            <Button
              size="small"
              variant="outlined"
              startIcon={<TrendingDown />}
              onClick={(e) => {
                e.stopPropagation();
                setDepreciationScheduleDialogOpen(true);
              }}
            >
              View All
            </Button>
          </Box>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Box textAlign="center" p={2}>
              <Typography variant="h4" color="primary">
                ${(metrics.depreciatedValue || 0).toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Accumulated Depreciation
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box textAlign="center" p={2}>
              <Typography variant="h4" color="success.main">
                {((metrics.depreciatedValue / metrics.totalValue) * 100 || 0).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Depreciation Rate
              </Typography>
            </Box>
          </Grid>
        </Grid>
        <Box mt={2} textAlign="center">
          <Typography variant="caption" color="text.secondary">
            Click to view all depreciation schedules
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
             <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
         <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>Fixed Assets</Typography>
         <Box display="flex" gap={1}>
           <Button
             variant="outlined"
             startIcon={<Refresh />}
             onClick={() => {
               // Refresh all data
               window.location.reload();
             }}
             disabled={assetsLoading || maintenanceLoading || depreciationLoading}
           >
             Refresh
           </Button>
           <Button
             variant="contained"
             startIcon={<Add />}
             onClick={() => setAddDialogOpen(true)}
           >
             Add Asset
           </Button>
         </Box>
       </Box>
      
      {renderAssetMetrics()}
      
      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          {renderAssetTable()}
        </Grid>
        <Grid item xs={12} lg={4}>
          <Box display="flex" flexDirection="column" gap={3}>
            {renderMaintenanceSchedule()}
            {renderDepreciationAnalysis()}
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
           Asset Details - {selectedAsset?.asset_name}
         </DialogTitle>
        <DialogContent>
          {selectedAsset && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Asset Information</Typography>
                <List dense>
                                     <ListItem>
                     <ListItemText 
                       primary="Asset ID" 
                       secondary={selectedAsset.asset_id} 
                     />
                   </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Category" 
                      secondary={selectedAsset.category} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Purchase Date" 
                      secondary={new Date(selectedAsset.purchase_date).toLocaleDateString()} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Useful Life" 
                      secondary={`${selectedAsset.useful_life} years`} 
                    />
                  </ListItem>
                </List>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" color="text.secondary">Financial Information</Typography>
                <List dense>
                                     <ListItem>
                     <ListItemText 
                       primary="Purchase Value" 
                       secondary={`$${(selectedAsset.purchase_value || 0).toLocaleString()}`} 
                     />
                   </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Current Value" 
                      secondary={`$${(selectedAsset.current_value || 0).toLocaleString()}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Accumulated Depreciation" 
                      secondary={`$${(selectedAsset.accumulated_depreciation || 0).toLocaleString()}`} 
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Net Book Value" 
                      secondary={`$${((selectedAsset.current_value || 0) - (selectedAsset.accumulated_depreciation || 0)).toLocaleString()}`} 
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

      {/* Add/Edit Dialog */}
      <Dialog
        open={addDialogOpen || editDialogOpen}
        onClose={handleCloseDialog}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>{editDialogOpen ? 'Edit Asset' : 'Add New Asset'}</DialogTitle>
        <DialogContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <Grid container spacing={2}>
                             <Grid item xs={12}>
                 <TextField
                   label="Asset Name"
                   fullWidth
                   required
                   value={formData.asset_name}
                   onChange={(e) => handleInputChange('asset_name', e.target.value)}
                 />
               </Grid>
                             <Grid item xs={12}>
                 <TextField
                   label="Asset ID"
                   fullWidth
                   required
                   value={formData.asset_id}
                   onChange={(e) => handleInputChange('asset_id', e.target.value)}
                 />
               </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Category"
                  fullWidth
                  required
                  value={formData.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  fullWidth
                  multiline
                  rows={2}
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                />
              </Grid>
                             <Grid item xs={12} sm={6}>
                 <TextField
                   label="Purchase Value"
                   fullWidth
                   required
                   type="number"
                   value={formData.purchase_value}
                   onChange={(e) => handleInputChange('purchase_value', e.target.value)}
                   InputProps={{
                     startAdornment: <InputAdornment position="start">$</InputAdornment>,
                   }}
                 />
               </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Current Value"
                  fullWidth
                  required
                  type="number"
                  value={formData.current_value}
                  onChange={(e) => handleInputChange('current_value', e.target.value)}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              
              {/* Payment Method Information for Asset Purchase */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1, color: 'primary.main' }}>
                  Purchase Payment Information
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={formData.payment_method_id || ''}
                    onChange={(e) => handleInputChange('payment_method_id', e.target.value)}
                    label="Payment Method"
                  >
                    <MenuItem value="">
                      <em>Select Payment Method</em>
                    </MenuItem>
                    <MenuItem value="1">Cash</MenuItem>
                    <MenuItem value="2">Credit/Debit Card</MenuItem>
                    <MenuItem value="3">Bank Transfer</MenuItem>
                    <MenuItem value="4">Check</MenuItem>
                    <MenuItem value="5">Wire Transfer</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Bank Account</InputLabel>
                  <Select
                    value={formData.bank_account_id || ''}
                    onChange={(e) => handleInputChange('bank_account_id', e.target.value)}
                    label="Bank Account"
                  >
                    <MenuItem value="">
                      <em>Select Bank Account</em>
                    </MenuItem>
                    <MenuItem value="1">Main Checking Account</MenuItem>
                    <MenuItem value="2">Merchant Account</MenuItem>
                    <MenuItem value="3">Savings Account</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Purchase Reference"
                  value={formData.purchase_reference || ''}
                  onChange={(e) => handleInputChange('purchase_reference', e.target.value)}
                  fullWidth
                  margin="normal"
                  placeholder="PO #, Invoice #, Check #"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Purchase Date"
                  type="date"
                  value={formData.purchase_date || ''}
                  onChange={(e) => handleInputChange('purchase_date', e.target.value)}
                  fullWidth
                  margin="normal"
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Salvage Value"
                  fullWidth
                  type="number"
                  value={formData.salvage_value}
                  onChange={(e) => handleInputChange('salvage_value', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Useful Life (years)"
                  fullWidth
                  required
                  type="number"
                  value={formData.useful_life}
                  onChange={(e) => handleInputChange('useful_life', e.target.value)}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Purchase Date"
                  fullWidth
                  required
                  type="date"
                  value={formData.purchase_date}
                  onChange={(e) => handleInputChange('purchase_date', e.target.value)}
                  InputLabelProps={{
                    shrink: true,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Location"
                  fullWidth
                  value={formData.location}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={formData.status === 'active'}
                      onChange={(e) => handleInputChange('status', e.target.checked ? 'active' : 'idle')}
                      name="status"
                      color="primary"
                    />
                  }
                  label="Status"
                />
              </Grid>
            </Grid>
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button onClick={handleCloseDialog} color="primary">Cancel</Button>
              <Button type="submit" variant="contained" color="primary" sx={{ ml: 1 }}>
                {editDialogOpen ? 'Save Changes' : 'Add Asset'}
              </Button>
            </Box>
          </Box>
        </DialogContent>
              </Dialog>

      {/* Maintenance Dialog */}
              <Dialog
          open={maintenanceDialogOpen}
                  onClose={() => {
          setMaintenanceDialogOpen(false);
          setMaintenanceForm({
            maintenance_type: 'preventive',
            due_date: '',
            description: '',
            estimated_cost: '',
            priority: 'medium',
            status: 'scheduled'
          });
        }}
          maxWidth="md"
          fullWidth
        >
        <DialogTitle>
          Asset Maintenance - {selectedAsset?.asset_name || 'New Maintenance'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Maintenance Type"
                fullWidth
                required
                select
                value={maintenanceForm.maintenance_type}
                onChange={(e) => handleMaintenanceInputChange('maintenance_type', e.target.value)}
              >
                <MenuItem value="preventive">Preventive</MenuItem>
                <MenuItem value="corrective">Corrective</MenuItem>
                <MenuItem value="emergency">Emergency</MenuItem>
                <MenuItem value="inspection">Inspection</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Due Date"
                fullWidth
                required
                type="date"
                value={maintenanceForm.due_date}
                onChange={(e) => handleMaintenanceInputChange('due_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                fullWidth
                required
                multiline
                rows={3}
                value={maintenanceForm.description}
                onChange={(e) => handleMaintenanceInputChange('description', e.target.value)}
                placeholder="Describe the maintenance work needed..."
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Estimated Cost"
                fullWidth
                type="number"
                value={maintenanceForm.estimated_cost}
                onChange={(e) => handleMaintenanceInputChange('estimated_cost', e.target.value)}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Priority"
                fullWidth
                select
                value={maintenanceForm.priority}
                onChange={(e) => handleMaintenanceInputChange('priority', e.target.value)}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMaintenanceDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" color="primary" onClick={handleMaintenanceSubmit}>
            Schedule Maintenance
          </Button>
        </DialogActions>
      </Dialog>

      {/* Depreciation Dialog */}
              <Dialog
          open={depreciationDialogOpen}
          onClose={() => {
            setDepreciationDialogOpen(false);
            setDepreciationForm({
              depreciation_method: 'straight_line',
              depreciation_rate: ''
            });
          }}
          maxWidth="md"
          fullWidth
        >
        <DialogTitle>
          Depreciation Analysis - {selectedAsset?.asset_name || 'Asset'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Depreciation Method"
                fullWidth
                required
                select
                value={depreciationForm.depreciation_method}
                onChange={(e) => handleDepreciationInputChange('depreciation_method', e.target.value)}
              >
                <MenuItem value="straight_line">Straight Line</MenuItem>
                <MenuItem value="declining_balance">Declining Balance</MenuItem>
                <MenuItem value="sum_of_years">Sum of Years</MenuItem>
                <MenuItem value="units_of_production">Units of Production</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                label="Depreciation Rate (%)"
                fullWidth
                type="number"
                value={depreciationForm.depreciation_rate}
                onChange={(e) => handleDepreciationInputChange('depreciation_rate', e.target.value)}
                InputProps={{
                  endAdornment: <InputAdornment position="end">%</InputAdornment>,
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Depreciation Schedule
              </Typography>
              <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Typography variant="caption" color="text.secondary">Year</Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="caption" color="text.secondary">Depreciation</Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="caption" color="text.secondary">Book Value</Typography>
                  </Grid>
                  {selectedAsset && [...Array(parseInt(selectedAsset.useful_life || 5))].map((_, year) => {
                    const yearNum = year + 1;
                    const annualDepreciation = (selectedAsset.purchase_value - selectedAsset.salvage_value) / selectedAsset.useful_life;
                    const bookValue = selectedAsset.purchase_value - (annualDepreciation * yearNum);
                    return (
                      <React.Fragment key={yearNum}>
                        <Grid item xs={4}>
                          <Typography variant="body2">{yearNum}</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="body2">${annualDepreciation.toFixed(2)}</Typography>
                        </Grid>
                        <Grid item xs={4}>
                          <Typography variant="body2">${bookValue.toFixed(2)}</Typography>
                        </Grid>
                      </React.Fragment>
                    );
                  })}
                </Grid>
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDepreciationDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" color="primary" onClick={handleDepreciationSubmit}>
            Calculate Depreciation
          </Button>
        </DialogActions>
      </Dialog>

      {/* Comprehensive Maintenance Schedule Dialog */}
      <Dialog
        open={maintenanceScheduleDialogOpen}
        onClose={() => {
          setMaintenanceScheduleDialogOpen(false);
          // Reset filters when closing
          setMaintenanceSearchTerm('');
          setMaintenanceFilterStatus('all');
          setMaintenanceFilterPriority('all');
        }}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Maintenance Schedule Management</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => {
                setMaintenanceScheduleDialogOpen(false);
                setMaintenanceDialogOpen(true);
              }}
            >
              Schedule New Maintenance
            </Button>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box mb={3}>
            {/* Summary Metrics */}
            <Grid container spacing={2} mb={3}>
              <Grid item xs={12} sm={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h6" color="primary">
                    {filteredMaintenanceRecords?.filter(r => r.status === 'scheduled').length || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Scheduled
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h6" color="warning.main">
                    {filteredMaintenanceRecords?.filter(r => r.status === 'in_progress').length || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    In Progress
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h6" color="success.main">
                    {filteredMaintenanceRecords?.filter(r => r.status === 'completed').length || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Completed
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h6" color="error.main">
                    {filteredMaintenanceRecords?.filter(r => r.status === 'overdue').length || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Overdue
                  </Typography>
                </Card>
              </Grid>
            </Grid>
            
            {/* Search and Filters */}
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Search Assets"
                  fullWidth
                  size="small"
                  placeholder="Search by asset name, type, or description..."
                  value={maintenanceSearchTerm}
                  onChange={(e) => setMaintenanceSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: <Search fontSize="small" sx={{ color: 'text.secondary', mr: 1 }} />
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  label="Status"
                  fullWidth
                  size="small"
                  select
                  value={maintenanceFilterStatus}
                  onChange={(e) => setMaintenanceFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="overdue">Overdue</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  label="Priority"
                  fullWidth
                  size="small"
                  select
                  value={maintenanceFilterPriority}
                  onChange={(e) => setMaintenanceFilterPriority(e.target.value)}
                >
                  <MenuItem value="all">All Priorities</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </TextField>
              </Grid>
            </Grid>
            
            {/* Filter Summary and Clear Button */}
            {(maintenanceSearchTerm || maintenanceFilterStatus !== 'all' || maintenanceFilterPriority !== 'all') && (
              <Box mt={2} display="flex" justifyContent="space-between" alignItems="center">
                <Typography variant="body2" color="text.secondary">
                  Showing {filteredMaintenanceRecords?.length || 0} of {maintenanceRecords?.length || 0} records
                  {maintenanceSearchTerm && ` • Search: "${maintenanceSearchTerm}"`}
                  {maintenanceFilterStatus !== 'all' && ` • Status: ${maintenanceFilterStatus}`}
                  {maintenanceFilterPriority !== 'all' && ` • Priority: ${maintenanceFilterPriority}`}
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => {
                    setMaintenanceSearchTerm('');
                    setMaintenanceFilterStatus('all');
                    setMaintenanceFilterPriority('all');
                  }}
                >
                  Clear All Filters
                </Button>
              </Box>
            )}
            
            {/* Clickable Row Info */}
            <Box mt={2} mb={1}>
              <Typography variant="body2" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Info fontSize="small" />
                Click on any row to view full maintenance details
              </Typography>
            </Box>
          </Box>
          
          {maintenanceLoading ? (
            <Box display="flex" flexDirection="column" gap={1}>
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} variant="rectangular" height={100} />
              ))}
            </Box>
          ) : (
            <TableContainer component={Paper} sx={{ width: '100%', overflowX: 'auto' }}>
              <Table sx={{ minWidth: 900 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Asset</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Due Date</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredMaintenanceRecords?.map((record) => (
                    <TableRow 
                      key={record.id} 
                      hover 
                      onClick={() => openMaintenanceDetails(record)}
                      sx={{ 
                        cursor: 'pointer', 
                        '&:hover': { 
                          backgroundColor: 'action.hover',
                          transform: 'scale(1.01)',
                          transition: 'all 0.2s ease-in-out'
                        },
                        transition: 'all 0.2s ease-in-out'
                      }}
                    >
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {record.asset_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {record.asset_id}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={record.maintenance_type} 
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap>
                          {record.description?.length > 50 ? `${record.description.substring(0, 50)}...` : record.description}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box>
                          <Typography variant="body2">
                            {formatDate(record.maintenance_date)}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {formatTime(record.maintenance_date)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={record.priority} 
                          size="small"
                          color={
                            record.priority === 'critical' ? 'error' :
                            record.priority === 'high' ? 'warning' :
                            record.priority === 'medium' ? 'info' : 'default'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={record.status} 
                          size="small"
                          color={
                            record.status === 'overdue' ? 'error' :
                            record.status === 'completed' ? 'success' :
                            record.status === 'in_progress' ? 'warning' : 'primary'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={0.5}>
                          <IconButton 
                            size="small" 
                            color="primary"
                            onClick={() => handleMaintenanceStatusUpdate(record.id, 'in_progress')}
                            title="Mark as In Progress"
                          >
                            <PlayArrow fontSize="small" />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            color="success"
                            onClick={() => handleMaintenanceStatusUpdate(record.id, 'completed')}
                            title="Mark as Completed"
                          >
                            <CheckCircle fontSize="small" />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            color="info"
                            onClick={() => openEditMaintenanceDialog(record)}
                            title="Edit Record"
                          >
                            <Edit fontSize="small" />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => handleMaintenanceDelete(record.id)}
                            title="Delete Record"
                          >
                            <Delete fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
          
          {(!filteredMaintenanceRecords || filteredMaintenanceRecords.length === 0) && !maintenanceLoading && (
            <Box textAlign="center" py={4}>
              <Build sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {maintenanceRecords && maintenanceRecords.length > 0 ? 'No Records Match Your Filters' : 'No Maintenance Records Found'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {maintenanceRecords && maintenanceRecords.length > 0 
                  ? 'Try adjusting your search terms or filters' 
                  : 'Start by scheduling maintenance for your assets'
                }
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMaintenanceScheduleDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Comprehensive Depreciation Schedule Dialog */}
      <Dialog
        open={depreciationScheduleDialogOpen}
        onClose={() => setDepreciationScheduleDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Depreciation Schedule Management</Typography>
            <Button
              variant="contained"
              startIcon={<TrendingDown />}
              onClick={() => {
                setDepreciationScheduleDialogOpen(false);
                setDepreciationDialogOpen(true);
              }}
            >
              Calculate New Depreciation
            </Button>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box mb={3}>
            {/* Summary Metrics */}
            <Grid container spacing={2} mb={3}>
              <Grid item xs={12} sm={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h6" color="primary">
                    ${(metrics.totalValue || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Total Asset Value
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h6" color="error.main">
                    ${(metrics.depreciatedValue || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Accumulated Depreciation
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h6" color="success.main">
                    ${(metrics.netBookValue || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Net Book Value
                  </Typography>
                </Card>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Card variant="outlined" sx={{ textAlign: 'center', p: 2 }}>
                  <Typography variant="h6" color="info.main">
                    ${(metrics.currentDepreciation || 0).toLocaleString()}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Monthly Depreciation
                  </Typography>
                </Card>
              </Grid>
            </Grid>
            
            {/* Search and Filters */}
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Search Assets"
                  fullWidth
                  size="small"
                  placeholder="Search by asset name, category, or method..."
                />
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  label="Depreciation Method"
                  fullWidth
                  size="small"
                  select
                  defaultValue="all"
                >
                  <MenuItem value="all">All Methods</MenuItem>
                  <MenuItem value="straight_line">Straight Line</MenuItem>
                  <MenuItem value="declining_balance">Declining Balance</MenuItem>
                  <MenuItem value="sum_of_years">Sum of Years</MenuItem>
                  <MenuItem value="units_of_production">Units of Production</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={3}>
                <TextField
                  label="Asset Status"
                  fullWidth
                  size="small"
                  select
                  defaultValue="all"
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="depreciated">Fully Depreciated</MenuItem>
                  <MenuItem value="disposed">Disposed</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </Box>
          
          {depreciationLoading ? (
            <Box display="flex" flexDirection="column" gap={1}>
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} variant="rectangular" height={100} />
              ))}
            </Box>
          ) : (
            <TableContainer component={Paper} sx={{ width: '100%', overflowX: 'auto' }}>
              <Table sx={{ minWidth: 900 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Asset</TableCell>
                    <TableCell>Method</TableCell>
                    <TableCell>Purchase Value</TableCell>
                    <TableCell>Current Value</TableCell>
                    <TableCell>Accumulated Depreciation</TableCell>
                    <TableCell>Annual Depreciation</TableCell>
                    <TableCell>Remaining Life</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {depreciationSchedules?.map((schedule) => (
                    <TableRow key={schedule.id} hover>
                      <TableCell>
                        <Box>
                          <Typography variant="body2" fontWeight="medium">
                            {schedule.asset_name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {schedule.asset_id}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={schedule.depreciation_method} 
                          size="small"
                          color="primary"
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight="medium">
                          ${(schedule.purchase_value || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          ${(schedule.current_value || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="error.main">
                          ${(schedule.accumulated_depreciation || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          ${(schedule.annual_depreciation || 0).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={`${schedule.remaining_life || 0} years`}
                          size="small"
                          color={
                            (schedule.remaining_life || 0) <= 1 ? 'error' :
                            (schedule.remaining_life || 0) <= 3 ? 'warning' : 'success'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" gap={0.5}>
                          <IconButton 
                            size="small" 
                            color="primary"
                            onClick={() => handleDepreciationScheduleUpdate(schedule.id, { method: 'straight_line' })}
                            title="Edit Schedule"
                          >
                            <Edit fontSize="small" />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            color="secondary"
                            title="View Details"
                          >
                            <Visibility fontSize="small" />
                          </IconButton>
                          <IconButton 
                            size="small" 
                            color="info"
                            title="View Chart"
                          >
                            <BarChart fontSize="small" />
                          </IconButton>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
          
          {(!depreciationSchedules || depreciationSchedules.length === 0) && !depreciationLoading && (
            <Box textAlign="center" py={4}>
              <TrendingDown sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No Depreciation Schedules Found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Start by calculating depreciation for your assets
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDepreciationScheduleDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Edit Maintenance Record Dialog */}
      <Dialog
        open={editMaintenanceDialogOpen}
        onClose={() => {
          setEditMaintenanceDialogOpen(false);
          setEditingMaintenanceRecord(null);
        }}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Edit Maintenance Record - {editingMaintenanceRecord?.asset_name}
        </DialogTitle>
        <DialogContent>
          {editingMaintenanceRecord && (
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Maintenance Type"
                  fullWidth
                  required
                  select
                  value={maintenanceForm.maintenance_type}
                  onChange={(e) => handleMaintenanceInputChange('maintenance_type', e.target.value)}
                >
                  <MenuItem value="preventive">Preventive</MenuItem>
                  <MenuItem value="corrective">Corrective</MenuItem>
                  <MenuItem value="emergency">Emergency</MenuItem>
                  <MenuItem value="inspection">Inspection</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Due Date"
                  fullWidth
                  required
                  type="date"
                  value={maintenanceForm.due_date}
                  onChange={(e) => handleMaintenanceInputChange('due_date', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  label="Description"
                  fullWidth
                  required
                  multiline
                  rows={3}
                  value={maintenanceForm.description}
                  onChange={(e) => handleMaintenanceInputChange('description', e.target.value)}
                  placeholder="Describe the maintenance work needed..."
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Estimated Cost"
                  fullWidth
                  type="number"
                  value={maintenanceForm.estimated_cost}
                  onChange={(e) => handleMaintenanceInputChange('estimated_cost', e.target.value)}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">$</InputAdornment>,
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Priority"
                  fullWidth
                  select
                  value={maintenanceForm.priority}
                  onChange={(e) => handleMaintenanceInputChange('priority', e.target.value)}
                >
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                </TextField>
              </Grid>
              
              {/* Payment Method Information for Maintenance */}
              <Grid item xs={12}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1, color: 'primary.main' }}>
                  Maintenance Payment Information
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Payment Method</InputLabel>
                  <Select
                    value={maintenanceForm.payment_method_id || ''}
                    onChange={(e) => handleMaintenanceInputChange('payment_method_id', e.target.value)}
                    label="Payment Method"
                  >
                    <MenuItem value="">
                      <em>Select Payment Method</em>
                    </MenuItem>
                    <MenuItem value="1">Cash</MenuItem>
                    <MenuItem value="2">Credit/Debit Card</MenuItem>
                    <MenuItem value="3">Bank Transfer</MenuItem>
                    <MenuItem value="4">Check</MenuItem>
                    <MenuItem value="5">Wire Transfer</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth margin="normal">
                  <InputLabel>Bank Account</InputLabel>
                  <Select
                    value={maintenanceForm.bank_account_id || ''}
                    onChange={(e) => handleMaintenanceInputChange('bank_account_id', e.target.value)}
                    label="Bank Account"
                  >
                    <MenuItem value="">
                      <em>Select Bank Account</em>
                    </MenuItem>
                    <MenuItem value="1">Main Checking Account</MenuItem>
                    <MenuItem value="2">Merchant Account</MenuItem>
                    <MenuItem value="3">Savings Account</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Payment Reference"
                  value={maintenanceForm.payment_reference || ''}
                  onChange={(e) => handleMaintenanceInputChange('payment_reference', e.target.value)}
                  fullWidth
                  margin="normal"
                  placeholder="Check #, Invoice #, Work Order #"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  label="Status"
                  fullWidth
                  select
                  value={maintenanceForm.status || 'scheduled'}
                  onChange={(e) => handleMaintenanceInputChange('status', e.target.value)}
                >
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="cancelled">Cancelled</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setEditMaintenanceDialogOpen(false);
            setEditingMaintenanceRecord(null);
          }}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={() => {
              if (editingMaintenanceRecord) {
                handleMaintenanceEdit(editingMaintenanceRecord.id, maintenanceForm);
                setEditMaintenanceDialogOpen(false);
                setEditingMaintenanceRecord(null);
              }
            }}
          >
            Update Record
          </Button>
        </DialogActions>
      </Dialog>

      {/* Maintenance Details Dialog */}
      <Dialog
        open={maintenanceDetailsDialogOpen}
        onClose={() => setMaintenanceDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">
              Maintenance Details
            </Typography>
            <IconButton onClick={() => setMaintenanceDetailsDialogOpen(false)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {!selectedMaintenanceRecord ? (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress />
            </Box>
          ) : (
            <Grid container spacing={3}>
              {/* Asset Information */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 2, mb: 2 }}>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Asset Information
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Asset Name</Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {selectedMaintenanceRecord.asset_name}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Asset ID</Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {selectedMaintenanceRecord.asset_id}
                      </Typography>
                    </Grid>
                  </Grid>
                </Card>
              </Grid>

              {/* Maintenance Details */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 2, mb: 2 }}>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Maintenance Details
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Maintenance Type</Typography>
                      <Chip 
                        label={selectedMaintenanceRecord.maintenance_type} 
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Priority</Typography>
                      <Chip 
                        label={selectedMaintenanceRecord.priority} 
                        size="small"
                        color={
                          selectedMaintenanceRecord.priority === 'critical' ? 'error' :
                          selectedMaintenanceRecord.priority === 'high' ? 'warning' :
                          selectedMaintenanceRecord.priority === 'medium' ? 'info' : 'default'
                        }
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Status</Typography>
                      <Chip 
                        label={selectedMaintenanceRecord.status} 
                        size="small"
                        color={
                          selectedMaintenanceRecord.status === 'overdue' ? 'error' :
                          selectedMaintenanceRecord.status === 'completed' ? 'success' :
                          selectedMaintenanceRecord.status === 'in_progress' ? 'warning' : 'primary'
                        }
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Estimated Cost</Typography>
                      <Typography variant="body1" fontWeight="medium">
                        ${(selectedMaintenanceRecord.cost || 0).toLocaleString()}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Maintenance Date</Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {formatDate(selectedMaintenanceRecord.maintenance_date)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">Next Maintenance Date</Typography>
                      <Typography variant="body1" fontWeight="medium">
                        {selectedMaintenanceRecord.next_maintenance_date ? 
                          formatDate(selectedMaintenanceRecord.next_maintenance_date) : 
                          'Not scheduled'
                        }
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">Description</Typography>
                      <Typography variant="body1" sx={{ mt: 1, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                        {selectedMaintenanceRecord.description || 'No description provided'}
                      </Typography>
                    </Grid>
                  </Grid>
                </Card>
              </Grid>

              {/* Actions */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Quick Actions
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Edit />}
                      onClick={() => {
                        setMaintenanceDetailsDialogOpen(false);
                        openEditMaintenanceDialog(selectedMaintenanceRecord);
                      }}
                    >
                      Edit Record
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<PlayArrow />}
                      onClick={() => {
                        handleMaintenanceStatusUpdate(selectedMaintenanceRecord.id, 'in_progress');
                        setMaintenanceDetailsDialogOpen(false);
                      }}
                      disabled={selectedMaintenanceRecord.status === 'in_progress'}
                    >
                      Mark In Progress
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<CheckCircle />}
                      onClick={() => {
                        handleMaintenanceStatusUpdate(selectedMaintenanceRecord.id, 'completed');
                        setMaintenanceDetailsDialogOpen(false);
                      }}
                      disabled={selectedMaintenanceRecord.status === 'completed'}
                    >
                      Mark Completed
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<Delete />}
                      color="error"
                      onClick={() => {
                        if (window.confirm('Are you sure you want to delete this maintenance record?')) {
                          handleMaintenanceDelete(selectedMaintenanceRecord.id);
                          setMaintenanceDetailsDialogOpen(false);
                        }
                      }}
                    >
                      Delete Record
                    </Button>
                  </Box>
                </Card>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMaintenanceDetailsDialogOpen(false)}>
            Close
          </Button>
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

export default SmartFixedAssets;

