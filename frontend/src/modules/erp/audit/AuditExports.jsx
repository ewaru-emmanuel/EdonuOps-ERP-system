import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert
} from '@mui/material';
import {
  Download as DownloadIcon,
  Schedule as ScheduleIcon,
  FileDownload as FileDownloadIcon,
  Description as DescriptionIcon,
  TableChart as TableChartIcon
} from '@mui/icons-material';

const AuditExports = () => {
  const [exportConfig, setExportConfig] = useState({
    format: 'CSV',
    dateRange: '7d',
    modules: [],
    severity: []
  });

  const [showSuccess, setShowSuccess] = useState(false);

  const exportHistory = [
    {
      id: 1,
      name: 'Security Audit Export',
      format: 'CSV',
      dateRange: 'Last 7 days',
      size: '2.4 MB',
      status: 'Completed',
      timestamp: '2024-01-15 14:30'
    },
    {
      id: 2,
      name: 'User Activity Report',
      format: 'PDF',
      dateRange: 'Last 30 days',
      size: '1.8 MB',
      status: 'Completed',
      timestamp: '2024-01-14 10:15'
    },
    {
      id: 3,
      name: 'Compliance Export',
      format: 'Excel',
      dateRange: 'Last 90 days',
      size: '5.2 MB',
      status: 'In Progress',
      timestamp: '2024-01-15 15:45'
    }
  ];

  const formatOptions = [
    { value: 'CSV', label: 'CSV', icon: <TableChartIcon /> },
    { value: 'Excel', label: 'Excel', icon: <TableChartIcon /> },
    { value: 'PDF', label: 'PDF', icon: <DescriptionIcon /> },
    { value: 'JSON', label: 'JSON', icon: <DescriptionIcon /> }
  ];

  const dateRangeOptions = [
    { value: '1d', label: 'Last 24 hours' },
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
    { value: '90d', label: 'Last 90 days' },
    { value: '1y', label: 'Last year' },
    { value: 'custom', label: 'Custom range' }
  ];

  const moduleOptions = ['Authentication', 'Finance', 'CRM', 'User Management', 'System', 'Inventory', 'Procurement'];
  const severityOptions = ['Critical', 'Warning', 'Error', 'Info'];

  const handleExport = () => {
    // Mock export functionality
    console.log('Exporting with config:', exportConfig);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  const handleDownload = (exportItem) => {
    // Mock download functionality
    console.log('Downloading:', exportItem.name);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed':
        return 'success';
      case 'In Progress':
        return 'warning';
      case 'Failed':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Audit Exports</Typography>
      
      {showSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Export request submitted successfully! You will be notified when it's ready.
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Export Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Export Configuration</Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Export Format</InputLabel>
                    <Select
                      value={exportConfig.format}
                      onChange={(e) => setExportConfig({ ...exportConfig, format: e.target.value })}
                      label="Export Format"
                    >
                      {formatOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          <Box display="flex" alignItems="center" gap={1}>
                            {option.icon}
                            {option.label}
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Date Range</InputLabel>
                    <Select
                      value={exportConfig.dateRange}
                      onChange={(e) => setExportConfig({ ...exportConfig, dateRange: e.target.value })}
                      label="Date Range"
                    >
                      {dateRangeOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Modules (Optional)</InputLabel>
                    <Select
                      multiple
                      value={exportConfig.modules}
                      onChange={(e) => setExportConfig({ ...exportConfig, modules: e.target.value })}
                      label="Modules (Optional)"
                      renderValue={(selected) => (
                        <Box display="flex" gap={0.5} flexWrap="wrap">
                          {selected.map((value) => (
                            <Chip key={value} label={value} size="small" />
                          ))}
                        </Box>
                      )}
                    >
                      {moduleOptions.map((option) => (
                        <MenuItem key={option} value={option}>
                          {option}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <FormControl fullWidth>
                    <InputLabel>Severity Levels (Optional)</InputLabel>
                    <Select
                      multiple
                      value={exportConfig.severity}
                      onChange={(e) => setExportConfig({ ...exportConfig, severity: e.target.value })}
                      label="Severity Levels (Optional)"
                      renderValue={(selected) => (
                        <Box display="flex" gap={0.5} flexWrap="wrap">
                          {selected.map((value) => (
                            <Chip key={value} label={value} size="small" />
                          ))}
                        </Box>
                      )}
                    >
                      {severityOptions.map((option) => (
                        <MenuItem key={option} value={option}>
                          {option}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12}>
                  <Button
                    variant="contained"
                    fullWidth
                    startIcon={<DownloadIcon />}
                    onClick={handleExport}
                    size="large"
                  >
                    Generate Export
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Export History */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Export History</Typography>
              
              <List>
                {exportHistory.map((item, index) => (
                  <React.Fragment key={item.id}>
                    <ListItem>
                      <ListItemIcon>
                        <FileDownloadIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={item.name}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="textSecondary">
                              {item.format} • {item.dateRange} • {item.size}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              {item.timestamp}
                            </Typography>
                          </Box>
                        }
                      />
                      <Box display="flex" alignItems="center" gap={1}>
                        <Chip
                          label={item.status}
                          color={getStatusColor(item.status)}
                          size="small"
                        />
                        {item.status === 'Completed' && (
                          <Button
                            size="small"
                            startIcon={<DownloadIcon />}
                            onClick={() => handleDownload(item)}
                          >
                            Download
                          </Button>
                        )}
                      </Box>
                    </ListItem>
                    {index < exportHistory.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Scheduled Exports */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Scheduled Exports</Typography>
                <Button
                  variant="outlined"
                  startIcon={<ScheduleIcon />}
                >
                  Schedule New Export
                </Button>
              </Box>
              
              <Typography color="textSecondary">
                No scheduled exports configured. Create a scheduled export to automatically generate reports at regular intervals.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AuditExports;



