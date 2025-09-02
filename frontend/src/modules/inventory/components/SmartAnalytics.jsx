import React, { useState } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Paper, Chip, Avatar,
  Button, IconButton, Tooltip, Alert, LinearProgress, Badge, Tabs, Tab,
  List, ListItem, ListItemText, ListItemAvatar, ListItemIcon,
  useTheme, useMediaQuery, CircularProgress
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Speed, Warning, CheckCircle, Error,
  Analytics, Assessment, Timeline, Insights, Psychology,
  Refresh, Notifications, Visibility, VisibilityOff,
  Warehouse, QrCode, DirectionsWalk, Timeline as TimelineIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const SmartAnalytics = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const [activeTab, setActiveTab] = useState(0);

  // Real-time data hooks
  const { data: kpis, loading: kpisLoading } = useRealTimeData('/api/inventory/analytics/kpis');
  const { data: trends, loading: trendsLoading } = useRealTimeData('/api/inventory/analytics/trends');
  const { data: stockLevels, loading: stockLoading } = useRealTimeData('/api/inventory/analytics/reports/stock-levels');
  const { data: movementData, loading: movementLoading } = useRealTimeData('/api/inventory/analytics/reports/movement');

  // Real-time data from API
  const predictiveInsights = kpis || [];
  const trendAnalysis = trends || [];

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing': return <TrendingUp color="success" />;
      case 'declining': return <TrendingDown color="error" />;
      case 'stable': return <TimelineIcon color="info" />;
      default: return <TimelineIcon />;
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold' }}>
          🤖 AI-Powered Analytics & Insights
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Psychology />}
            sx={{ fontWeight: 'bold' }}
          >
            AI Insights
          </Button>
          <Button
            variant="contained"
            startIcon={<Analytics />}
            sx={{ fontWeight: 'bold' }}
          >
            Generate Report
          </Button>
        </Box>
      </Box>

      {/* Analytics Tabs */}
      <Paper sx={{ width: '100%', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant={isMobile ? "scrollable" : "fullWidth"}
          scrollButtons={isMobile ? "auto" : false}
        >
          <Tab label="AI Insights" />
          <Tab label="Predictive Analytics" />
          <Tab label="Performance Trends" />
          <Tab label="Operational Intelligence" />
        </Tabs>
      </Paper>

      {/* AI Insights Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Psychology color="primary" />
                  <Typography variant="h6" fontWeight="bold">
                    AI-Powered Insights
                  </Typography>
                  <Chip label="Real-Time" color="success" size="small" />
                </Box>
                
                <List>
                  {predictiveInsights.map((insight) => (
                    <ListItem key={insight.id} sx={{ px: 0, mb: 2 }}>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: getImpactColor(insight.impact) + '.light' }}>
                          {insight.type === 'stockout' ? <Warning /> :
                           insight.type === 'performance' ? <Speed /> : <Assessment />}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={
                          <Typography variant="body1" fontWeight="bold" component="span">
                            {insight.type === 'stockout' ? insight.product :
                             insight.type === 'performance' ? insight.user : insight.location}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {insight.type === 'stockout' ? insight.prediction :
                               insight.type === 'performance' ? insight.metric : insight.metric}
                            </Typography>
                            <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                              💡 {insight.recommendation}
                            </Typography>
                          </Box>
                        }
                      />
                      <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
                        <Chip 
                          label={insight.impact} 
                          size="small" 
                          color={getImpactColor(insight.impact)}
                        />
                        <Chip 
                          label={`${insight.confidence}% confidence`} 
                          size="small" 
                          variant="outlined"
                        />
                      </Box>
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} lg={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  🎯 AI Confidence Score
                </Typography>
                
                <Box sx={{ textAlign: 'center', mb: 3 }}>
                  <CircularProgress 
                    variant="determinate" 
                    value={92} 
                    size={120}
                    sx={{ color: 'success.main', mb: 2 }}
                  />
                  <Typography variant="h4" fontWeight="bold">
                    92%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Overall AI Confidence
                  </Typography>
                </Box>
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Model Performance
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CheckCircle color="success" />
                    <Typography variant="body2">Stockout Prediction: 95%</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CheckCircle color="success" />
                    <Typography variant="body2">Performance Analysis: 88%</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CheckCircle color="success" />
                    <Typography variant="body2">Utilization Forecast: 92%</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Predictive Analytics Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  📈 Demand Forecasting
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Next 30 Days Prediction
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <TrendingUp color="success" />
                    <Typography variant="body2">Laptop Pro X1: +15% demand increase</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <TrendingDown color="error" />
                    <Typography variant="body2">Wireless Mouse: -8% demand decrease</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TimelineIcon color="info" />
                    <Typography variant="body2">USB Cable: Stable demand</Typography>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="primary" fontWeight="bold">
                  🎯 Recommendation: Increase Laptop Pro X1 inventory by 20%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  🔮 Predictive Stockouts
                </Typography>
                
                <List>
                  {predictiveInsights.filter(i => i.type === 'stockout').map((insight) => (
                    <ListItem key={insight.id} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Warning color="error" />
                      </ListItemIcon>
                      <ListItemText
                        primary={insight.product}
                        secondary={
                          <Typography variant="body2" color="text.secondary">
                            Location: {insight.location}
                          </Typography>
                        }
                      />
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, ml: 2 }}>
                        <Typography variant="body2" color="error">
                          {insight.prediction}
                        </Typography>
                      </Box>
                      <Chip 
                        label={insight.impact} 
                        size="small" 
                        color={getImpactColor(insight.impact)}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Performance Trends Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  📊 Performance Trends (Last 6 Months)
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" fontWeight="bold" color="primary.main">
                        {trendAnalysis.length > 0 ? trendAnalysis[trendAnalysis.length - 1].total_items_picked || 0 : 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Monthly Picks
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mt: 1 }}>
                        <TrendingUp color="success" />
                        <Typography variant="caption" color="success.main">
                          +8.5% vs last month
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" fontWeight="bold" color="success.main">
                        {trendAnalysis.length > 0 ? trendAnalysis[trendAnalysis.length - 1].items_per_hour || 0 : 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Picking Efficiency
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mt: 1 }}>
                        <TrendingUp color="success" />
                        <Typography variant="caption" color="success.main">
                          +2.2% vs last month
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Box sx={{ textAlign: 'center', p: 2 }}>
                      <Typography variant="h4" fontWeight="bold" color="info.main">
                        {trendAnalysis.length > 0 ? ((trendAnalysis[trendAnalysis.length - 1].performance_vs_average || 0) ? (trendAnalysis[trendAnalysis.length - 1].performance_vs_average || 0).toFixed(1) : '0.0') : '0.0'}%
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Order Accuracy
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mt: 1 }}>
                        <TrendingUp color="success" />
                        <Typography variant="caption" color="success.main">
                          +1.0% vs last month
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Operational Intelligence Tab */}
      {activeTab === 3 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  🧠 Operational Intelligence
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Key Insights
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Insights color="primary" />
                    <Typography variant="body2">
                      Peak picking hours: 9-11 AM and 2-4 PM
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Insights color="primary" />
                    <Typography variant="body2">
                      Zone A has highest activity density
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Insights color="primary" />
                    <Typography variant="body2">
                      Monday and Friday are busiest days
                    </Typography>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="primary" fontWeight="bold">
                  🎯 Optimization: Consider staggered shifts to balance workload
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" fontWeight="bold" gutterBottom>
                  📱 Mobile WMS Analytics
                </Typography>
                
                <Box sx={{ mb: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Device Performance
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CheckCircle color="success" />
                    <Typography variant="body2">MD-001: 95% uptime, 12.5 picks/hour</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CheckCircle color="success" />
                    <Typography variant="body2">MD-002: 92% uptime, 10.2 picks/hour</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Warning color="warning" />
                    <Typography variant="body2">MD-003: 78% uptime, 8.1 picks/hour</Typography>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="warning" fontWeight="bold">
                  ⚠️ Recommendation: Replace MD-003 battery or device
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Loading States */}
      {(kpisLoading || trendsLoading || stockLoading || movementLoading) && (
        <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }}>
          <LinearProgress />
        </Box>
      )}
    </Box>
  );
};

export default SmartAnalytics;
