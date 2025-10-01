import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Paper, Table, TableBody, TableCell, TableHead, TableRow,
  List, ListItem, ListItemText, ListItemIcon, Chip, Alert, LinearProgress, Button, IconButton,
  Tooltip, Accordion, AccordionSummary, AccordionDetails, FormControl, InputLabel, Select, MenuItem,
  Tabs, Tab, Dialog, DialogTitle, DialogContent, DialogActions, TextField, DatePicker
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Assessment, AccountBalance, Sync, CompareArrows, Warning, Error,
  CheckCircle, Info, ExpandMore, Refresh, Download, Settings, FilterList, Timeline,
  AttachMoney, Schedule, Receipt, Description, TrendingFlat
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const AnalyticsDashboard = ({ isMobile = false }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [dateRange, setDateRange] = useState('30');
  const [trends, setTrends] = useState(null);
  const [accountPerformance, setAccountPerformance] = useState(null);
  const [discrepancyAnalysis, setDiscrepancyAnalysis] = useState(null);
  const [matchingEfficiency, setMatchingEfficiency] = useState(null);
  const [optimizationRecommendations, setOptimizationRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedAccount, setSelectedAccount] = useState('all');
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [selectedMetric, setSelectedMetric] = useState(null);

  // Data hooks
  const { data: reconciliationSessions, loading: sessionsLoading, refresh: refreshSessions } = useRealTimeData('/api/finance/reconciliation-sessions');
  const { data: bankAccounts, loading: accountsLoading } = useRealTimeData('/api/finance/bank-accounts');

  useEffect(() => {
    loadAnalytics();
  }, [dateRange, selectedAccount]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const [trendsRes, accountRes, discrepancyRes, matchingRes, recommendationsRes] = await Promise.all([
        apiClient.get(`/api/finance/analytics/trends?days=${dateRange}`),
        apiClient.get(`/api/finance/analytics/account-performance?account_id=${selectedAccount}`),
        apiClient.get(`/api/finance/analytics/discrepancy-analysis?days=${dateRange}`),
        apiClient.get(`/api/finance/analytics/matching-efficiency?days=${dateRange}`),
        apiClient.get('/api/finance/analytics/optimization-recommendations')
      ]);

      setTrends(trendsRes.data);
      setAccountPerformance(accountRes.data);
      setDiscrepancyAnalysis(discrepancyRes.data);
      setMatchingEfficiency(matchingRes.data);
      setOptimizationRecommendations(recommendationsRes.data.recommendations || []);

    } catch (err) {
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const renderTrendsChart = () => {
    if (!trends?.daily_reconciliations) return null;

    const data = trends.daily_reconciliations.map(item => ({
      date: item.date,
      total: item.count,
      completed: item.completed,
      pending: item.pending,
      discrepancies: item.discrepancies
    }));

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Reconciliation Trends
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <RechartsTooltip />
              <Line type="monotone" dataKey="total" stroke="#8884d8" strokeWidth={2} />
              <Line type="monotone" dataKey="completed" stroke="#82ca9d" strokeWidth={2} />
              <Line type="monotone" dataKey="pending" stroke="#ffc658" strokeWidth={2} />
              <Line type="monotone" dataKey="discrepancies" stroke="#ff7300" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  };

  const renderAccountPerformance = () => {
    if (!accountPerformance?.accounts) return null;

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Account Performance
          </Typography>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Account</TableCell>
                <TableCell>Completion Rate</TableCell>
                <TableCell>Match Rate</TableCell>
                <TableCell>Avg Difference</TableCell>
                <TableCell>Last Reconciliation</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {accountPerformance.accounts.map((account) => (
                <TableRow key={account.account_id}>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {account.account_name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {account.bank_name}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2">
                        {account.completion_rate}%
                      </Typography>
                      {account.completion_rate >= 80 ? (
                        <CheckCircle color="success" fontSize="small" />
                      ) : account.completion_rate >= 60 ? (
                        <Warning color="warning" fontSize="small" />
                      ) : (
                        <Error color="error" fontSize="small" />
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {account.match_rate}%
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography 
                      variant="body2" 
                      color={account.avg_difference === 0 ? 'success.main' : 'error.main'}
                    >
                      ${account.avg_difference.toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {account.last_reconciliation ? 
                        new Date(account.last_reconciliation).toLocaleDateString() : 
                        'Never'
                      }
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    );
  };

  const renderDiscrepancyAnalysis = () => {
    if (!discrepancyAnalysis?.statistics) return null;

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

    return (
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Discrepancy Statistics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="error.main">
                      {discrepancyAnalysis.statistics.total_discrepancies}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Discrepancies
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center">
                    <Typography variant="h4" color="warning.main">
                      ${discrepancyAnalysis.statistics.avg_discrepancy.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Average Discrepancy
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Common Discrepancy Amounts
              </Typography>
              {discrepancyAnalysis.common_amounts?.slice(0, 5).map((item, index) => (
                <Box key={index} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="body2">
                    ${item.difference.toLocaleString()}
                  </Typography>
                  <Chip 
                    label={item.frequency} 
                    size="small" 
                    color="primary"
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderMatchingEfficiency = () => {
    if (!matchingEfficiency?.overall_stats) return null;

    const data = matchingEfficiency.amount_ranges?.map(range => ({
      range: range.range,
      matchRate: range.match_rate,
      totalCount: range.total_count
    })) || [];

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Matching Efficiency by Amount Range
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <RechartsTooltip />
              <Bar dataKey="matchRate" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    );
  };

  const renderOptimizationRecommendations = () => {
    if (!optimizationRecommendations.length) return null;

    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Optimization Recommendations
          </Typography>
          <List>
            {optimizationRecommendations.map((rec, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {rec.priority === 'high' ? (
                    <Error color="error" />
                  ) : rec.priority === 'medium' ? (
                    <Warning color="warning" />
                  ) : (
                    <Info color="info" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={rec.title}
                  secondary={rec.description}
                />
                <Chip 
                  label={rec.priority} 
                  size="small"
                  color={rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warning' : 'default'}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    );
  };

  const renderSummaryCards = () => {
    if (!trends?.summary) return null;

    const summary = trends.summary;

    return (
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <AccountBalance />
                </Avatar>
                <Box>
                  <Typography variant="h4">{summary.total_reconciliations}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Reconciliations
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <CheckCircle />
                </Avatar>
                <Box>
                  <Typography variant="h4">{summary.completion_rate}%</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Completion Rate
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <AttachMoney />
                </Avatar>
                <Box>
                  <Typography variant="h4">${summary.avg_daily_volume.toLocaleString()}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg Daily Volume
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'error.main' }}>
                  <Error />
                </Avatar>
                <Box>
                  <Typography variant="h4">{summary.discrepancy_rate}%</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Discrepancy Rate
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  const renderFilters = () => (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Date Range</InputLabel>
            <Select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
            >
              <MenuItem value="7">Last 7 days</MenuItem>
              <MenuItem value="30">Last 30 days</MenuItem>
              <MenuItem value="90">Last 90 days</MenuItem>
              <MenuItem value="365">Last year</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Account</InputLabel>
            <Select
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
            >
              <MenuItem value="all">All Accounts</MenuItem>
              {bankAccounts?.map((account) => (
                <MenuItem key={account.id} value={account.id}>
                  {account.account_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <Button 
            variant="outlined" 
            startIcon={<Refresh />}
            onClick={loadAnalytics}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Typography variant="h4" gutterBottom>
        Reconciliation Analytics
      </Typography>

      {renderFilters()}
      {renderSummaryCards()}
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          {renderTrendsChart()}
        </Grid>
        
        <Grid item xs={12}>
          {renderAccountPerformance()}
        </Grid>
        
        <Grid item xs={12}>
          {renderDiscrepancyAnalysis()}
        </Grid>
        
        <Grid item xs={12}>
          {renderMatchingEfficiency()}
        </Grid>
        
        <Grid item xs={12}>
          {renderOptimizationRecommendations()}
        </Grid>
      </Grid>
    </Box>
  );
};

export default AnalyticsDashboard;












