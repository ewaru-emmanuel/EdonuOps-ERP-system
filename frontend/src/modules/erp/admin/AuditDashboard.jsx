import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Button, TextField, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Alert, Tabs, Tab, FormControl, InputLabel, Select, MenuItem, IconButton,
  Dialog, DialogTitle, DialogContent, DialogActions, Tooltip, Badge
} from '@mui/material';
import {
  Security, History, Login, PersonAdd, Edit, Delete, Download, Refresh,
  Search, FilterList, Visibility, Warning, CheckCircle, Cancel, Timeline
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const AuditDashboard = () => {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    user: '',
    module: '',
    action: '',
    entityType: ''
  });
  const [securitySummary, setSecuritySummary] = useState(null);
  const [auditStats, setAuditStats] = useState(null);

  // Fetch security summary
  const { data: securityData, loading: securityLoading, error: securityError } = useRealTimeData(
    '/audit/security-summary?days=30',
    'audit-security-summary'
  );

  // Fetch audit statistics
  const { data: statsData, loading: statsLoading, error: statsError } = useRealTimeData(
    '/audit/audit-stats?days=30',
    'audit-stats'
  );

  useEffect(() => {
    if (securityData) {
      setSecuritySummary(securityData);
    }
  }, [securityData]);

  useEffect(() => {
    if (statsData) {
      setAuditStats(statsData);
    }
  }, [statsData]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      startDate: '',
      endDate: '',
      user: '',
      module: '',
      action: '',
      entityType: ''
    });
  };

  const exportAuditLogs = async () => {
    try {
      setLoading(true);
      const response = await apiClient.post('/audit/export-audit-logs', filters);
      
      if (response.success) {
        // Convert to CSV and download
        const csvContent = convertToCSV(response.data);
        downloadCSV(csvContent, `audit-logs-${new Date().toISOString().split('T')[0]}.csv`);
      }
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const convertToCSV = (data) => {
    if (!data || data.length === 0) return '';
    
    const headers = Object.keys(data[0]);
    const csvHeaders = headers.join(',');
    
    const csvRows = data.map(row => 
      headers.map(header => {
        const value = row[header];
        if (typeof value === 'object') {
          return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
        }
        return `"${value || ''}"`;
      }).join(',')
    );
    
    return [csvHeaders, ...csvRows].join('\n');
  };

  const downloadCSV = (content, filename) => {
    const blob = new Blob([content], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return 'error';
      case 'ERROR': return 'error';
      case 'WARNING': return 'warning';
      case 'INFO': return 'info';
      case 'SUCCESS': return 'success';
      default: return 'default';
    }
  };

  const getActionIcon = (action) => {
    switch (action?.toUpperCase()) {
      case 'CREATE': return <PersonAdd />;
      case 'UPDATE': return <Edit />;
      case 'DELETE': return <Delete />;
      case 'LOGIN': return <Login />;
      case 'LOGOUT': return <Security />;
      default: return <Timeline />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Security color="primary" />
        Audit Trail Dashboard
      </Typography>

      {/* Error Display */}
      {(securityError || statsError) && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="subtitle2">Audit system is initializing...</Typography>
          <Typography variant="body2">
            Some audit features may not be available yet. The system is setting up audit trail infrastructure.
          </Typography>
          {securityError && <Typography variant="caption">Security Summary: {securityError}</Typography>}
          {statsError && <Typography variant="caption">Statistics: {statsError}</Typography>}
        </Alert>
      )}

      {/* Security Summary Cards */}
      {securitySummary && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle color="success" />
                  <Typography variant="h6">{securitySummary.successful_logins}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Successful Logins
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Cancel color="error" />
                  <Typography variant="h6">{securitySummary.failed_logins}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Failed Logins
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Warning color="warning" />
                  <Typography variant="h6">{securitySummary.suspicious_activities}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Suspicious Activities
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Edit color="info" />
                  <Typography variant="h6">{securitySummary.permission_changes}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Permission Changes
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Filter Section */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Filters</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                label="Start Date"
                type="date"
                value={filters.startDate}
                onChange={(e) => handleFilterChange('startDate', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                label="End Date"
                type="date"
                value={filters.endDate}
                onChange={(e) => handleFilterChange('endDate', e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                size="small"
                label="User"
                value={filters.user}
                onChange={(e) => handleFilterChange('user', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Module</InputLabel>
                <Select
                  value={filters.module}
                  label="Module"
                  onChange={(e) => handleFilterChange('module', e.target.value)}
                >
                  <MenuItem value="">All Modules</MenuItem>
                  <MenuItem value="finance">Finance</MenuItem>
                  <MenuItem value="inventory">Inventory</MenuItem>
                  <MenuItem value="sales">Sales</MenuItem>
                  <MenuItem value="procurement">Procurement</MenuItem>
                  <MenuItem value="system">System</MenuItem>
                  <MenuItem value="auth">Authentication</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Action</InputLabel>
                <Select
                  value={filters.action}
                  label="Action"
                  onChange={(e) => handleFilterChange('action', e.target.value)}
                >
                  <MenuItem value="">All Actions</MenuItem>
                  <MenuItem value="CREATE">Create</MenuItem>
                  <MenuItem value="UPDATE">Update</MenuItem>
                  <MenuItem value="DELETE">Delete</MenuItem>
                  <MenuItem value="LOGIN">Login</MenuItem>
                  <MenuItem value="LOGOUT">Logout</MenuItem>
                  <MenuItem value="APPROVE">Approve</MenuItem>
                  <MenuItem value="REJECT">Reject</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', height: '100%' }}>
                <Button
                  variant="outlined"
                  startIcon={<Search />}
                  onClick={() => {/* Apply filters */}}
                >
                  Search
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Refresh />}
                  onClick={clearFilters}
                >
                  Clear
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs for different audit views */}
      <Card>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tab} onChange={(e, v) => setTab(v)}>
            <Tab 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Timeline />
                  Audit Logs
                </Box>
              } 
            />
            <Tab 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Login />
                  Login History
                </Box>
              } 
            />
            <Tab 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Security />
                  Permission Changes
                </Box>
              } 
            />
            <Tab 
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Warning />
                  System Events
                </Box>
              } 
            />
          </Tabs>
        </Box>

        <CardContent>
          {/* Export and Actions */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              {tab === 0 && 'Audit Logs'}
              {tab === 1 && 'Login History'}
              {tab === 2 && 'Permission Changes'}
              {tab === 3 && 'System Events'}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={exportAuditLogs}
                disabled={loading}
              >
                Export
              </Button>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={() => {/* Refresh data */}}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          {/* Placeholder for audit data tables */}
          <Alert severity="info">
            Audit data tables will be implemented with real-time data fetching.
            This dashboard provides the foundation for comprehensive audit trail monitoring.
          </Alert>

          {/* Statistics Display */}
          {auditStats && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="h6" gutterBottom>Activity Statistics (Last 30 Days)</Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Top Modules by Activity:</Typography>
                  {auditStats.module_stats?.slice(0, 5).map((stat, index) => (
                    <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">{stat.module}</Typography>
                      <Chip label={stat.count} size="small" />
                    </Box>
                  ))}
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2">Most Active Users:</Typography>
                  {auditStats.top_users?.slice(0, 5).map((user, index) => (
                    <Box key={index} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">{user.username}</Typography>
                      <Chip label={user.count} size="small" />
                    </Box>
                  ))}
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default AuditDashboard;
