import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Paper, Chip, 
  Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Alert, IconButton, Tooltip, Badge, LinearProgress,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  FormControl, InputLabel, Select, MenuItem, Accordion, AccordionSummary,
  AccordionDetails, List, ListItem, ListItemText, ListItemIcon
} from '@mui/material';
import {
  Security, CheckCircle, Error, Warning, Info, Refresh, 
  Schedule, Assessment, TrendingUp, TrendingDown, BugReport,
  DataUsage, Speed, Storage, Timeline, Build
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const DataIntegrityAdminPanel = () => {
  const [selectedDiscrepancy, setSelectedDiscrepancy] = useState(null);
  const [showDiscrepancyDetails, setShowDiscrepancyDetails] = useState(false);
  const [concurrencyTest, setConcurrencyTest] = useState({ product_id: '', location_id: '' });
  const [showConcurrencyDialog, setShowConcurrencyDialog] = useState(false);
  const [testResults, setTestResults] = useState(null);
  
  // Real-time data hooks
  const { data: healthCheck, loading: healthLoading } = useRealTimeData(
    '/api/inventory/data-integrity/health-check',
    60000 // 1 minute refresh
  );
  
  const { data: reconciliationData, loading: reconciliationLoading } = useRealTimeData(
    '/api/inventory/data-integrity/reconciliation',
    30000 // 30 seconds refresh
  );
  
  const { data: auditTrail, loading: auditLoading } = useRealTimeData(
    '/api/inventory/data-integrity/audit-trail',
    60000
  );
  
  const { data: backupStatus, loading: backupLoading } = useRealTimeData(
    '/api/inventory/data-integrity/backup-status',
    60000
  );

  // Real-time data from API
  const adminData = healthCheck || {
    last_check_time: new Date().toISOString(),
    is_running: false,
    check_results: {
      check_time: new Date().toISOString(),
      status: 'completed',
      discrepancies: [],
      summary: {
        total_stock_levels: 0,
        total_discrepancies: 0,
        high_severity: 0,
        medium_severity: 0,
        low_severity: 0,
        accuracy_rate: 100
      },
      recommendations: []
    },
    system_health: {
      total_products: 0,
      total_locations: 0,
      total_transactions: 0,
      recent_transactions_24h: 0,
      active_pick_lists: 0,
      recent_warehouse_activity_24h: 0,
      last_updated: new Date().toISOString()
    }
  };

  // Use real data from API
  const data = adminData;
  const discrepanciesData = reconciliationData || { discrepancies: [], total_count: 0, last_check: new Date().toISOString() };
  const recommendationsData = backupStatus || { recommendations: [], total_count: 0, last_check: new Date().toISOString() };

  const handleRunReconciliation = async () => {
    try {
      await apiClient.post('/inventory/data-integrity/reconciliation/run');
      // Refresh data after a short delay
      setTimeout(() => window.location.reload(), 2000);
    } catch (error) {
      console.error('Failed to run reconciliation:', error);
    }
  };

  const handleRunConcurrencyTest = async () => {
    try {
      const response = await apiClient.post('/inventory/data-integrity/concurrency/test', concurrencyTest);
      setTestResults(response);
      setShowConcurrencyDialog(false);
    } catch (error) {
      console.error('Failed to run concurrency test:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getRecommendationColor = (type) => {
    switch (type) {
      case 'urgent': return 'error';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'urgent': return <Error color="error" />;
      case 'warning': return <Warning color="warning" />;
      case 'info': return <Info color="info" />;
      default: return <Info color="primary" />;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
          <Security color="primary" />
          Data Integrity Admin Panel
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<Schedule />}
            onClick={handleRunReconciliation}
            disabled={data.is_running}
          >
            {data.is_running ? 'Running...' : 'Run Reconciliation'}
          </Button>
          <Button
            variant="outlined"
            startIcon={<BugReport />}
            onClick={() => setShowConcurrencyDialog(true)}
          >
            Concurrency Test
          </Button>
          <Tooltip title="Refresh Data">
            <IconButton>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* System Health Overview */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <DataUsage color="primary" />
                System Health
              </Typography>
              
                             {healthLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                      <Typography variant="h4" color="primary">{data.system_health?.total_products || 0}</Typography>
                      <Typography variant="caption">Total Products</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                      <Typography variant="h4" color="success.main">{data.system_health?.total_locations || 0}</Typography>
                      <Typography variant="caption">Total Locations</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                      <Typography variant="h4" color="info.main">{data.system_health?.recent_transactions_24h || 0}</Typography>
                      <Typography variant="caption">Transactions (24h)</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center', p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                      <Typography variant="h4" color="warning.main">{data.system_health?.active_pick_lists || 0}</Typography>
                      <Typography variant="caption">Active Pick Lists</Typography>
                    </Box>
                  </Grid>
                </Grid>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Reconciliation Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Assessment color="primary" />
                Reconciliation Status
              </Typography>
              
                             {reconciliationLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="body2">Last Check:</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {data.last_check_time ? new Date(data.last_check_time).toLocaleString() : 'Never'}
                    </Typography>
                  </Box>
                  
                  {data.check_results && (
                    <>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="body2">Accuracy Rate:</Typography>
                        <Typography variant="h6" color="success.main">
                          {data.check_results.summary?.accuracy_rate ? data.check_results.summary.accuracy_rate.toFixed(1) : '0.0'}%
                        </Typography>
                      </Box>
                      
                      <LinearProgress 
                        variant="determinate" 
                        value={data.check_results.summary?.accuracy_rate || 0} 
                        sx={{ height: 10, mb: 2 }}
                        color={data.check_results.summary?.accuracy_rate > 95 ? 'success' : 'warning'}
                      />
                      
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Chip 
                          label={`${data.check_results.summary?.high_severity || 0} High`} 
                          color="error" 
                          size="small" 
                        />
                        <Chip 
                          label={`${data.check_results.summary?.medium_severity || 0} Medium`} 
                          color="warning" 
                          size="small" 
                        />
                        <Chip 
                          label={`${data.check_results.summary?.low_severity || 0} Low`} 
                          color="info" 
                          size="small" 
                        />
                      </Box>
                    </>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Discrepancies Table */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Error color="error" />
                Stock Level Discrepancies
                <Badge badgeContent={discrepanciesData.total_count} color="error" sx={{ ml: 1 }} />
              </Typography>
              
                             {reconciliationLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Product</TableCell>
                        <TableCell>Location</TableCell>
                        <TableCell align="right">Expected</TableCell>
                        <TableCell align="right">Actual</TableCell>
                        <TableCell align="right">Variance</TableCell>
                        <TableCell align="center">Severity</TableCell>
                        <TableCell align="center">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {discrepanciesData.discrepancies?.map((discrepancy) => (
                        <TableRow key={`${discrepancy.product_id}-${discrepancy.location_id}`} hover>
                          <TableCell>{discrepancy.product_name}</TableCell>
                          <TableCell>{discrepancy.location_name}</TableCell>
                          <TableCell align="right">{discrepancy.expected_stock}</TableCell>
                          <TableCell align="right">{discrepancy.actual_stock}</TableCell>
                          <TableCell align="right">
                            <Typography 
                              variant="body2" 
                              color={discrepancy.variance > 0 ? 'success.main' : 'error.main'}
                            >
                              {discrepancy.variance > 0 ? '+' : ''}{discrepancy.variance ? discrepancy.variance.toFixed(2) : '0.00'}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip 
                              label={discrepancy.severity} 
                              color={getSeverityColor(discrepancy.severity)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="center">
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={() => {
                                setSelectedDiscrepancy(discrepancy);
                                setShowDiscrepancyDetails(true);
                              }}
                            >
                              Details
                            </Button>
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

        {/* Recommendations */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Info color="info" />
                Recommendations
                <Badge badgeContent={recommendationsData.total_count} color="info" sx={{ ml: 1 }} />
              </Typography>
              
                             {backupLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <List>
                  {recommendationsData.recommendations?.map((recommendation, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        {getRecommendationIcon(recommendation.type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                              {recommendation.message}
                            </Typography>
                            <Chip 
                              label={recommendation.type} 
                              color={getRecommendationColor(recommendation.type)}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={
                          <Typography variant="body2" color="text.secondary">
                            Action: {recommendation.action}
                          </Typography>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Discrepancy Details Dialog */}
      <Dialog 
        open={showDiscrepancyDetails} 
        onClose={() => setShowDiscrepancyDetails(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Discrepancy Details
        </DialogTitle>
        <DialogContent>
          {selectedDiscrepancy && (
            <Grid container spacing={3}>
              <Grid item xs={6}>
                <Typography variant="h6">Product</Typography>
                <Typography variant="body1">{selectedDiscrepancy.product_name}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="h6">Location</Typography>
                <Typography variant="body1">{selectedDiscrepancy.location_name}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="h6">Expected Stock</Typography>
                <Typography variant="h4" color="primary">{selectedDiscrepancy.expected_stock}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="h6">Actual Stock</Typography>
                <Typography variant="h4" color="error">{selectedDiscrepancy.actual_stock}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="h6">Variance</Typography>
                <Typography 
                  variant="h4" 
                  color={selectedDiscrepancy.variance > 0 ? 'success.main' : 'error.main'}
                >
                  {selectedDiscrepancy.variance > 0 ? '+' : ''}{selectedDiscrepancy.variance ? selectedDiscrepancy.variance.toFixed(2) : '0.00'}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="h6">Variance %</Typography>
                <Typography variant="h4" color="warning.main">
                  {selectedDiscrepancy.variance_percentage ? selectedDiscrepancy.variance_percentage.toFixed(1) : '0.0'}%
                </Typography>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDiscrepancyDetails(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Concurrency Test Dialog */}
      <Dialog 
        open={showConcurrencyDialog} 
        onClose={() => setShowConcurrencyDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Run Concurrency Test
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Product ID"
                type="number"
                value={concurrencyTest.product_id}
                onChange={(e) => setConcurrencyTest({ ...concurrencyTest, product_id: e.target.value })}
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Location ID"
                type="number"
                value={concurrencyTest.location_id}
                onChange={(e) => setConcurrencyTest({ ...concurrencyTest, location_id: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConcurrencyDialog(false)}>Cancel</Button>
          <Button 
            onClick={handleRunConcurrencyTest}
            variant="contained"
            disabled={!concurrencyTest.product_id || !concurrencyTest.location_id}
          >
            Run Test
          </Button>
        </DialogActions>
      </Dialog>

      {/* Test Results Dialog */}
      <Dialog 
        open={!!testResults} 
        onClose={() => setTestResults(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Concurrency Test Results
        </DialogTitle>
        <DialogContent>
          {testResults && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>Test Summary</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2">Status:</Typography>
                  <Chip 
                    label={testResults.status} 
                    color={testResults.status === 'completed' ? 'success' : 'error'}
                    sx={{ ml: 1 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">Stock Accuracy:</Typography>
                  <Chip 
                    label={testResults.stock_accuracy ? 'Pass' : 'Fail'} 
                    color={testResults.stock_accuracy ? 'success' : 'error'}
                    sx={{ ml: 1 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">Successful Picks:</Typography>
                  <Typography variant="h6" color="success.main">{testResults.successful_picks}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">Failed Picks:</Typography>
                  <Typography variant="h6" color="error">{testResults.failed_picks}</Typography>
                </Grid>
              </Grid>
              
              {testResults.recommendations && testResults.recommendations.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>Recommendations</Typography>
                  <List>
                    {testResults.recommendations.map((rec, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          {getRecommendationIcon(rec.type)}
                        </ListItemIcon>
                        <ListItemText
                          primary={rec.message}
                          secondary={rec.action}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestResults(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataIntegrityAdminPanel;

