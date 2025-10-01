import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Chip,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  Divider
} from '@mui/material';
import {
  Analytics,
  Psychology,
  TrendingUp,
  Notifications,
  Schedule,
  CheckCircle,
  Warning,
  Error,
  Refresh,
  PlayArrow,
  Stop,
  Settings,
  Assessment,
  Insights
} from '@mui/icons-material';

const AIAnalyticsDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [insights, setInsights] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState('general');
  const [showInsightsDialog, setShowInsightsDialog] = useState(false);
  const [showWorkflowDialog, setShowWorkflowDialog] = useState(false);
  const [newWorkflow, setNewWorkflow] = useState({
    type: 'approval',
    data: {}
  });

  // Load initial data
  useEffect(() => {
    loadAlerts();
    loadWorkflows();
  }, []);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      
      // Load different types of alerts
      const [lowStockRes, overstockRes, paymentDueRes] = await Promise.all([
        fetch('/api/finance/workflows/alerts/low-stock'),
        fetch('/api/finance/workflows/alerts/overstock'),
        fetch('/api/finance/workflows/alerts/payment-due')
      ]);

      const lowStockData = await lowStockRes.json();
      const overstockData = await overstockRes.json();
      const paymentDueData = await paymentDueRes.json();

      const allAlerts = [
        ...(lowStockData.alerts || []),
        ...(overstockData.alerts || []),
        ...(paymentDueData.alerts || [])
      ];

      setAlerts(allAlerts);
    } catch (error) {
      console.error('Error loading alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadWorkflows = async () => {
    try {
      // In a real implementation, this would load from the database
      setWorkflows([]);
    } catch (error) {
      console.error('Error loading workflows:', error);
    }
  };

  const generateInsights = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/finance/ai/insights?type=${selectedAnalysis}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setInsights(data);
        setShowInsightsDialog(true);
      }
    } catch (error) {
      console.error('Error generating insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateInventoryInsights = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/finance/ai/inventory-insights');
      const data = await response.json();
      
      if (data.status === 'success') {
        setInsights(data);
        setShowInsightsDialog(true);
      }
    } catch (error) {
      console.error('Error generating inventory insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateMarketTrends = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/finance/ai/market-trends');
      const data = await response.json();
      
      if (data.status === 'success') {
        setInsights(data);
        setShowInsightsDialog(true);
      }
    } catch (error) {
      console.error('Error generating market trends:', error);
    } finally {
      setLoading(false);
    }
  };

  const runScheduledTasks = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/finance/workflows/run-scheduled', {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        // Refresh alerts after running tasks
        await loadAlerts();
      }
    } catch (error) {
      console.error('Error running scheduled tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const createWorkflow = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/finance/workflows/approval', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newWorkflow)
      });
      const data = await response.json();
      
      if (data.status === 'success') {
        setShowWorkflowDialog(false);
        setNewWorkflow({ type: 'approval', data: {} });
        await loadWorkflows();
      }
    } catch (error) {
      console.error('Error creating workflow:', error);
    } finally {
      setLoading(false);
    }
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'low_stock':
        return <Warning color="warning" />;
      case 'overstock':
        return <Error color="error" />;
      case 'payment_due':
        return <Notifications color="info" />;
      default:
        return <Notifications />;
    }
  };

  const getAlertColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" display="flex" alignItems="center" gap={1}>
          <Analytics />
          AI Analytics & Workflows
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadAlerts}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={runScheduledTasks}
          >
            Run Tasks
          </Button>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Grid container spacing={3}>
        {/* AI Analytics Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" display="flex" alignItems="center" gap={1} mb={2}>
                <Psychology />
                AI Analytics
              </Typography>
              
              <Box mb={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Analysis Type</InputLabel>
                  <Select
                    value={selectedAnalysis}
                    onChange={(e) => setSelectedAnalysis(e.target.value)}
                    label="Analysis Type"
                  >
                    <MenuItem value="general">General Financial</MenuItem>
                    <MenuItem value="performance">Performance Analysis</MenuItem>
                    <MenuItem value="risk">Risk Assessment</MenuItem>
                  </Select>
                </FormControl>
              </Box>

              <Box display="flex" flexDirection="column" gap={1}>
                <Button
                  variant="outlined"
                  startIcon={<Insights />}
                  onClick={generateInsights}
                  fullWidth
                >
                  Generate Financial Insights
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<Assessment />}
                  onClick={generateInventoryInsights}
                  fullWidth
                >
                  Inventory Insights
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<TrendingUp />}
                  onClick={generateMarketTrends}
                  fullWidth
                >
                  Market Trends
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflow Management Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" display="flex" alignItems="center" gap={1} mb={2}>
                <Schedule />
                Workflow Management
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={1}>
                <Button
                  variant="outlined"
                  startIcon={<Settings />}
                  onClick={() => setShowWorkflowDialog(true)}
                  fullWidth
                >
                  Create Workflow
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<Assessment />}
                  onClick={() => fetch('/api/finance/workflows/reports/daily')}
                  fullWidth
                >
                  Generate Daily Report
                </Button>
              </Box>

              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" mb={1}>
                Active Workflows: {workflows.length}
              </Typography>
              
              {workflows.map((workflow) => (
                <Box key={workflow.id} display="flex" alignItems="center" gap={1} mb={1}>
                  <Chip
                    label={workflow.status}
                    color={workflow.status === 'pending' ? 'warning' : 'success'}
                    size="small"
                  />
                  <Typography variant="body2">
                    {workflow.type} - {workflow.current_approver}
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Alerts Section */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" display="flex" alignItems="center" gap={1} mb={2}>
                <Notifications />
                Active Alerts ({alerts.length})
              </Typography>

              {alerts.length === 0 ? (
                <Alert severity="info">No active alerts at this time.</Alert>
              ) : (
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>Severity</TableCell>
                        <TableCell>Message</TableCell>
                        <TableCell>Created</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {alerts.slice(0, 10).map((alert, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              {getAlertIcon(alert.type)}
                              <Typography variant="body2">
                                {alert.type.replace('_', ' ').toUpperCase()}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={alert.severity}
                              color={getAlertColor(alert.severity)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" noWrap>
                              {alert.message}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {new Date(alert.created_at).toLocaleDateString()}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Tooltip title="Mark as resolved">
                              <IconButton size="small">
                                <CheckCircle />
                              </IconButton>
                            </Tooltip>
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
      </Grid>

      {/* Insights Dialog */}
      <Dialog
        open={showInsightsDialog}
        onClose={() => setShowInsightsDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <Psychology />
            AI Insights
          </Box>
        </DialogTitle>
        <DialogContent>
          {insights && (
            <Box>
              <Typography variant="h6" mb={2}>
                Analysis Results
              </Typography>
              
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  Generated at: {new Date(insights.generated_at).toLocaleString()}
                </Typography>
              </Alert>

              {insights.insights?.analysis && (
                <Box mb={2}>
                  <Typography variant="subtitle1" mb={1}>
                    AI Analysis:
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                    {insights.insights.analysis}
                  </Typography>
                </Box>
              )}

              {insights.insights?.key_metrics && (
                <Box mb={2}>
                  <Typography variant="subtitle1" mb={1}>
                    Key Metrics:
                  </Typography>
                  <Grid container spacing={2}>
                    {Object.entries(insights.insights.key_metrics).map(([key, value]) => (
                      <Grid item xs={6} key={key}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="caption" color="textSecondary">
                              {key.replace('_', ' ').toUpperCase()}
                            </Typography>
                            <Typography variant="h6">
                              {typeof value === 'number' ? value.toLocaleString() : value}
                            </Typography>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {insights.insights?.recommendations && insights.insights.recommendations.length > 0 && (
                <Box>
                  <Typography variant="subtitle1" mb={1}>
                    Recommendations:
                  </Typography>
                  <ul>
                    {insights.insights.recommendations.map((rec, index) => (
                      <li key={index}>
                        <Typography variant="body2">{rec}</Typography>
                      </li>
                    ))}
                  </ul>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowInsightsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Workflow Dialog */}
      <Dialog
        open={showWorkflowDialog}
        onClose={() => setShowWorkflowDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Create New Workflow</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            <FormControl fullWidth>
              <InputLabel>Workflow Type</InputLabel>
              <Select
                value={newWorkflow.type}
                onChange={(e) => setNewWorkflow({...newWorkflow, type: e.target.value})}
                label="Workflow Type"
              >
                <MenuItem value="approval">Approval Workflow</MenuItem>
                <MenuItem value="alert">Automated Alert</MenuItem>
                <MenuItem value="scheduled">Scheduled Task</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              label="Description"
              multiline
              rows={3}
              value={newWorkflow.data.description || ''}
              onChange={(e) => setNewWorkflow({
                ...newWorkflow,
                data: {...newWorkflow.data, description: e.target.value}
              })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowWorkflowDialog(false)}>Cancel</Button>
          <Button onClick={createWorkflow} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIAnalyticsDashboard;

