import React, { useState, useEffect } from 'react';
import {
  Box, Container, Typography, Card, CardContent, Grid, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Chip, IconButton, Button, Dialog, DialogTitle, DialogContent, DialogActions, Alert, CircularProgress,
  Tabs, Tab, FormControl, InputLabel, Select, MenuItem, TextField, Chip as MuiChip
} from '@mui/material';
import {
  AdminPanelSettings, Visibility, Block, CheckCircle, Error, TrendingUp, People, Storage, Api,
  Download, Refresh, FilterList, Security, Assessment
} from '@mui/icons-material';
import apiClient from '../../services/apiClient';

const GlobalAdminPanel = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [tenants, setTenants] = useState([]);
  const [platformMetrics, setPlatformMetrics] = useState(null);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTenant, setSelectedTenant] = useState(null);
  const [tenantDetails, setTenantDetails] = useState(null);
  const [filters, setFilters] = useState({
    tenant_id: '',
    severity: '',
    days: 7
  });

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [tenantsRes, metricsRes] = await Promise.all([
        apiClient.get('/api/admin/tenants'),
        apiClient.get('/api/admin/platform-metrics')
      ]);
      
      setTenants(tenantsRes.tenants || []);
      setPlatformMetrics(metricsRes);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAuditLogs = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.tenant_id) params.append('tenant_id', filters.tenant_id);
      if (filters.severity) params.append('severity', filters.severity);
      if (filters.days) params.append('days', filters.days);
      
      const response = await apiClient.get(`/api/admin/audit-logs?${params}`);
      setAuditLogs(response.logs || []);
    } catch (error) {
      console.error('Failed to load audit logs:', error);
    }
  };

  const loadTenantDetails = async (tenantId) => {
    try {
      const response = await apiClient.get(`/api/admin/tenants/${tenantId}`);
      setTenantDetails(response);
      setSelectedTenant(tenantId);
    } catch (error) {
      console.error('Failed to load tenant details:', error);
    }
  };

  const suspendTenant = async (tenantId) => {
    try {
      await apiClient.post(`/api/admin/tenants/${tenantId}/suspend`);
      await loadDashboardData();
      alert('Tenant suspended successfully');
    } catch (error) {
      console.error('Failed to suspend tenant:', error);
      alert('Failed to suspend tenant');
    }
  };

  const activateTenant = async (tenantId) => {
    try {
      await apiClient.post(`/api/admin/tenants/${tenantId}/activate`);
      await loadDashboardData();
      alert('Tenant activated successfully');
    } catch (error) {
      console.error('Failed to activate tenant:', error);
      alert('Failed to activate tenant');
    }
  };

  const exportAuditLogs = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.tenant_id) params.append('tenant_id', filters.tenant_id);
      if (filters.days) params.append('days', filters.days);
      
      const response = await apiClient.get(`/api/admin/audit-logs/export?${params}`);
      
      // Create and download CSV
      const blob = new Blob([response.csv_data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `audit_logs_${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to export audit logs:', error);
      alert('Failed to export audit logs');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'suspended': return 'error';
      case 'inactive': return 'warning';
      default: return 'default';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'ERROR': return 'error';
      case 'WARNING': return 'warning';
      case 'INFO': return 'info';
      case 'CRITICAL': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <AdminPanelSettings color="primary" sx={{ fontSize: 40 }} />
          <Typography variant="h4" component="h1" fontWeight="bold">
            Global Admin Panel
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary">
          Monitor all tenants, usage statistics, and platform health
        </Typography>
      </Box>

      {/* Platform Metrics */}
      {platformMetrics && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <People color="primary" />
                  <Box>
                    <Typography variant="h4">{platformMetrics.today_metrics?.total_tenants || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">Total Tenants</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <TrendingUp color="success" />
                  <Box>
                    <Typography variant="h4">{platformMetrics.today_metrics?.active_tenants || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">Active Tenants</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Api color="info" />
                  <Box>
                    <Typography variant="h4">{platformMetrics.today_metrics?.total_api_calls || 0}</Typography>
                    <Typography variant="body2" color="text.secondary">API Calls Today</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Error color="error" />
                  <Box>
                    <Typography variant="h4">{platformMetrics.today_metrics?.error_rate?.toFixed(2) || 0}%</Typography>
                    <Typography variant="body2" color="text.secondary">Error Rate</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Tenants" icon={<People />} />
          <Tab label="Audit Logs" icon={<Security />} />
          <Tab label="Platform Metrics" icon={<Assessment />} />
        </Tabs>
      </Box>

      {/* Tenants Tab */}
      {activeTab === 0 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">All Tenants ({tenants.length})</Typography>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadDashboardData}
            >
              Refresh
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Tenant</TableCell>
                  <TableCell>Plan</TableCell>
                  <TableCell>Users</TableCell>
                  <TableCell>Modules</TableCell>
                  <TableCell>Activity</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tenants.map((tenant) => (
                  <TableRow key={tenant.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2">{tenant.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {tenant.domain}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip label={tenant.subscription_plan} size="small" />
                    </TableCell>
                    <TableCell>{tenant.user_count}</TableCell>
                    <TableCell>{tenant.module_count}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2">{tenant.recent_activity}</Typography>
                        <Typography variant="caption" color="text.secondary">(7d)</Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={tenant.status}
                        color={getStatusColor(tenant.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <IconButton
                          size="small"
                          onClick={() => loadTenantDetails(tenant.id)}
                        >
                          <Visibility />
                        </IconButton>
                        {tenant.status === 'active' ? (
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => suspendTenant(tenant.id)}
                          >
                            <Block />
                          </IconButton>
                        ) : (
                          <IconButton
                            size="small"
                            color="success"
                            onClick={() => activateTenant(tenant.id)}
                          >
                            <CheckCircle />
                          </IconButton>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Audit Logs Tab */}
      {activeTab === 1 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">Audit Logs</Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={exportAuditLogs}
              >
                Export CSV
              </Button>
              <Button
                variant="outlined"
                startIcon={<Refresh />}
                onClick={loadAuditLogs}
              >
                Refresh
              </Button>
            </Box>
          </Box>

          {/* Filters */}
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Tenant</InputLabel>
              <Select
                value={filters.tenant_id}
                onChange={(e) => setFilters({...filters, tenant_id: e.target.value})}
                label="Tenant"
              >
                <MenuItem value="">All Tenants</MenuItem>
                {tenants.map(tenant => (
                  <MenuItem key={tenant.id} value={tenant.id}>{tenant.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Severity</InputLabel>
              <Select
                value={filters.severity}
                onChange={(e) => setFilters({...filters, severity: e.target.value})}
                label="Severity"
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="INFO">Info</MenuItem>
                <MenuItem value="WARNING">Warning</MenuItem>
                <MenuItem value="ERROR">Error</MenuItem>
                <MenuItem value="CRITICAL">Critical</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Days</InputLabel>
              <Select
                value={filters.days}
                onChange={(e) => setFilters({...filters, days: e.target.value})}
                label="Days"
              >
                <MenuItem value={1}>1 Day</MenuItem>
                <MenuItem value={7}>7 Days</MenuItem>
                <MenuItem value={30}>30 Days</MenuItem>
              </Select>
            </FormControl>
            <Button
              variant="contained"
              startIcon={<FilterList />}
              onClick={loadAuditLogs}
            >
              Apply Filters
            </Button>
          </Box>

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Tenant</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Resource</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>Module</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {auditLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>
                      {new Date(log.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>{log.tenant_id}</TableCell>
                    <TableCell>{log.user_id}</TableCell>
                    <TableCell>{log.action}</TableCell>
                    <TableCell>{log.resource}</TableCell>
                    <TableCell>
                      <Chip
                        label={log.severity}
                        color={getSeverityColor(log.severity)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{log.module}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* Platform Metrics Tab */}
      {activeTab === 2 && platformMetrics && (
        <Box>
          <Typography variant="h6" sx={{ mb: 3 }}>Platform Health</Typography>
          
          {platformMetrics.recent_errors && platformMetrics.recent_errors.length > 0 && (
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="subtitle2">Recent Errors ({platformMetrics.recent_errors.length})</Typography>
              {platformMetrics.recent_errors.slice(0, 5).map((error, index) => (
                <Typography key={index} variant="body2">
                  {error.action} on {error.resource} - {error.timestamp}
                </Typography>
              ))}
            </Alert>
          )}

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Top Active Tenants</Typography>
                  {platformMetrics.top_tenants?.map((tenant, index) => (
                    <Box key={tenant.id} sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
                      <Typography variant="body2">{tenant.name}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {tenant.activity_count} actions
                      </Typography>
                    </Box>
                  ))}
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Platform Statistics</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Total Users:</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {platformMetrics.today_metrics?.total_users || 0}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Total Storage:</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {platformMetrics.today_metrics?.total_storage_gb?.toFixed(2) || 0} GB
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="body2">Error Rate:</Typography>
                      <Typography variant="body2" fontWeight="bold" color="error">
                        {platformMetrics.today_metrics?.error_rate?.toFixed(2) || 0}%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Box>
      )}

      {/* Tenant Details Dialog */}
      <Dialog
        open={!!selectedTenant}
        onClose={() => setSelectedTenant(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Tenant Details</DialogTitle>
        <DialogContent>
          {tenantDetails && (
            <Box>
              <Typography variant="h6" gutterBottom>{tenantDetails.tenant.name}</Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {tenantDetails.tenant.domain} • {tenantDetails.tenant.subscription_plan}
              </Typography>
              
              <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>Users ({tenantDetails.users.length})</Typography>
              {tenantDetails.users.map(user => (
                <Box key={user.id} sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
                  <Typography variant="body2">{user.username} ({user.email})</Typography>
                  <Chip label={user.role} size="small" />
                </Box>
              ))}
              
              <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>Modules ({tenantDetails.modules.length})</Typography>
              {tenantDetails.modules.map(module => (
                <Box key={module.name} sx={{ display: 'flex', justifyContent: 'space-between', py: 1 }}>
                  <Typography variant="body2">{module.name}</Typography>
                  <Chip 
                    label={module.enabled ? 'Enabled' : 'Disabled'} 
                    color={module.enabled ? 'success' : 'default'}
                    size="small" 
                  />
                </Box>
              ))}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedTenant(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default GlobalAdminPanel;












