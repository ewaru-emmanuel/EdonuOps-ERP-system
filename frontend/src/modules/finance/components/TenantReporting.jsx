import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  DatePicker,
  LocalizationProvider,
  AdapterDateFns
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Business as BusinessIcon,
  AccountBalance as AccountBalanceIcon,
  People as PeopleIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  Notifications as NotificationsIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { DatePicker as MuiDatePicker } from '@mui/x-date-pickers/DatePicker';
import { useTenant } from '../../../contexts/TenantContext';
import { useTenantApi } from '../../../hooks/useTenantApi';

const TenantReporting = () => {
  const { currentTenant, hasModuleAccess } = useTenant();
  const { get, post, loading } = useTenantApi();
  
  const [reports, setReports] = useState([]);
  const [reportTypes, setReportTypes] = useState([
    { value: 'comprehensive', label: 'Comprehensive Report' },
    { value: 'finance', label: 'Finance Report' },
    { value: 'usage', label: 'Usage Report' },
    { value: 'performance', label: 'Performance Report' },
    { value: 'trends', label: 'Trends Report' }
  ]);
  const [selectedReportType, setSelectedReportType] = useState('comprehensive');
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    end: new Date()
  });
  const [generatedReports, setGeneratedReports] = useState([]);
  const [loadingReports, setLoadingReports] = useState(false);
  const [error, setError] = useState(null);
  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    if (currentTenant) {
      loadReports();
    }
  }, [currentTenant]);

  const loadReports = async () => {
    try {
      setLoadingReports(true);
      setError(null);
      
      // Load available reports
      const reportsData = await get('/api/analytics/tenant/overview');
      setReports(reportsData);
      
    } catch (err) {
      console.error('Error loading reports:', err);
      setError('Failed to load reports');
    } finally {
      setLoadingReports(false);
    }
  };

  const generateReport = async () => {
    try {
      setLoadingReports(true);
      setError(null);
      
      const reportData = await get(`/api/analytics/tenant/report?type=${selectedReportType}`);
      
      const newReport = {
        id: Date.now(),
        type: selectedReportType,
        title: reportTypes.find(r => r.value === selectedReportType)?.label || 'Report',
        data: reportData,
        generatedAt: new Date().toISOString(),
        dateRange: dateRange
      };
      
      setGeneratedReports(prev => [newReport, ...prev]);
      setReportDialogOpen(true);
      setSelectedReport(newReport);
      
    } catch (err) {
      console.error('Error generating report:', err);
      setError('Failed to generate report');
    } finally {
      setLoadingReports(false);
    }
  };

  const exportReport = async (report) => {
    try {
      // Simulate report export
      const csvContent = generateCSVContent(report);
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${report.title}_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
      
    } catch (err) {
      console.error('Error exporting report:', err);
      setError('Failed to export report');
    }
  };

  const generateCSVContent = (report) => {
    // Simple CSV generation for demo
    const headers = ['Metric', 'Value', 'Date'];
    const rows = [
      ['Report Type', report.type, report.generatedAt],
      ['Tenant', currentTenant?.tenant_name || 'N/A', report.generatedAt],
      ['Generated At', report.generatedAt, report.generatedAt]
    ];
    
    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

  const getReportIcon = (type) => {
    switch (type) {
      case 'comprehensive':
        return <AssessmentIcon color="primary" />;
      case 'finance':
        return <AccountBalanceIcon color="success" />;
      case 'usage':
        return <PeopleIcon color="info" />;
      case 'performance':
        return <SpeedIcon color="warning" />;
      case 'trends':
        return <TrendingUpIcon color="secondary" />;
      default:
        return <AssessmentIcon color="action" />;
    }
  };

  const getReportColor = (type) => {
    switch (type) {
      case 'comprehensive':
        return 'primary';
      case 'finance':
        return 'success';
      case 'usage':
        return 'info';
      case 'performance':
        return 'warning';
      case 'trends':
        return 'secondary';
      default:
        return 'default';
    }
  };

  if (loadingReports) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          Tenant Reporting
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Generate comprehensive reports and analytics for {currentTenant?.tenant_name}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Report Generator */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <AssessmentIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Generate Report
                </Typography>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Report Type</InputLabel>
                  <Select
                    value={selectedReportType}
                    onChange={(e) => setSelectedReportType(e.target.value)}
                    label="Report Type"
                  >
                    {reportTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {type.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                
                <LocalizationProvider dateAdapter={AdapterDateFns}>
                  <MuiDatePicker
                    label="Start Date"
                    value={dateRange.start}
                    onChange={(date) => setDateRange(prev => ({ ...prev, start: date }))}
                    renderInput={(params) => <TextField {...params} fullWidth sx={{ mb: 2 }} />}
                  />
                  
                  <MuiDatePicker
                    label="End Date"
                    value={dateRange.end}
                    onChange={(date) => setDateRange(prev => ({ ...prev, end: date }))}
                    renderInput={(params) => <TextField {...params} fullWidth sx={{ mb: 2 }} />}
                  />
                </LocalizationProvider>
              </Box>
              
              <Button
                variant="contained"
                fullWidth
                onClick={generateReport}
                disabled={loadingReports}
                startIcon={<AssessmentIcon />}
              >
                {loadingReports ? 'Generating...' : 'Generate Report'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        {/* Generated Reports */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <DownloadIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Generated Reports
                </Typography>
                <Box sx={{ flexGrow: 1 }} />
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={loadReports}
                  disabled={loadingReports}
                >
                  Refresh
                </Button>
              </Box>
              
              {generatedReports.length === 0 ? (
                <Box textAlign="center" py={4}>
                  <AssessmentIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Reports Generated
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Generate your first report to see it here
                  </Typography>
                </Box>
              ) : (
                <TableContainer component={Paper}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Report</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Generated</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {generatedReports.map((report) => (
                        <TableRow key={report.id}>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={2}>
                              {getReportIcon(report.type)}
                              <Box>
                                <Typography variant="body2" fontWeight="medium">
                                  {report.title}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {report.type}
                                </Typography>
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={report.type}
                              size="small"
                              color={getReportColor(report.type)}
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {new Date(report.generatedAt).toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Box display="flex" gap={1}>
                              <Tooltip title="View Report">
                                <IconButton
                                  size="small"
                                  onClick={() => {
                                    setSelectedReport(report);
                                    setReportDialogOpen(true);
                                  }}
                                >
                                  <AssessmentIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Export Report">
                                <IconButton
                                  size="small"
                                  onClick={() => exportReport(report)}
                                >
                                  <DownloadIcon />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Report Preview */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={3}>
                <TrendingUpIcon color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Report Preview
                </Typography>
              </Box>
              
              {selectedReport ? (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    {selectedReport.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Generated: {new Date(selectedReport.generatedAt).toLocaleString()}
                  </Typography>
                  
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2">
                      Report data would be displayed here in a formatted view.
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Box textAlign="center" py={4}>
                  <AssessmentIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Report Selected
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Generate a report to see the preview
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Report Dialog */}
      <Dialog
        open={reportDialogOpen}
        onClose={() => setReportDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            {selectedReport && getReportIcon(selectedReport.type)}
            <Typography variant="h6">
              {selectedReport?.title || 'Report'}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedReport && (
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Generated: {new Date(selectedReport.generatedAt).toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Type: {selectedReport.type}
              </Typography>
              
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Report data would be displayed here in a detailed view.
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReportDialogOpen(false)}>
            Close
          </Button>
          <Button
            variant="contained"
            startIcon={<DownloadIcon />}
            onClick={() => selectedReport && exportReport(selectedReport)}
          >
            Export
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TenantReporting;












