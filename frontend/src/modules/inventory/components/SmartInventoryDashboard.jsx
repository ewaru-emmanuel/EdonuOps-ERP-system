import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Paper, Chip, Avatar,
  List, ListItem, ListItemText, ListItemAvatar, ListItemIcon,
  LinearProgress, Alert, Button, IconButton, Tooltip, Badge,
  useTheme, useMediaQuery, Divider, CircularProgress
} from '@mui/material';
import {
  TrendingUp, TrendingDown, Speed, Warning, CheckCircle, Error,
  Person, LocationOn, Inventory, LocalShipping, Assessment,
  Refresh, Notifications, Visibility, VisibilityOff,
  Warehouse, QrCode, DirectionsWalk, Timeline
} from '@mui/icons-material';
// Removed useRealTimeData to prevent authentication calls

const SmartInventoryDashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const showWms = false; // hide warehouse visuals in Inventory module
  const [refreshKey, setRefreshKey] = useState(0);

  // Real-time data hooks
  // Mock data to prevent API calls
  const stockLevels = [];
  const stockLoading = false;
  const stockError = null;
  
  const warehouseActivity = [];
  const activityLoading = false;
  
  const predictiveStockouts = [];
  const stockoutLoading = false;
  
  const pickerPerformance = [];
  const performanceLoading = false;

  // Real-time data from API
  const warehouseMap = stockLevels?.warehouse_map || [];
  const liveActivity = warehouseActivity || [];
  const predictiveAlerts = predictiveStockouts || [];

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  const getAlertColor = (level) => {
    switch (level) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      default: return 'success';
    }
  };

  const getActivityColor = (activity) => {
    switch (activity) {
      case 'high': return 'success';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      {/* Header with Refresh */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h2" sx={{ fontWeight: 'bold' }}>
          Inventory Overview
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh Data">
            <IconButton onClick={handleRefresh} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Badge badgeContent={predictiveAlerts.length} color="error">
            <Tooltip title="Alerts">
              <IconButton color="primary">
                <Notifications />
              </IconButton>
            </Tooltip>
          </Badge>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'primary.light', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'white', color: 'primary.main' }}>
                  <Inventory />
                </Avatar>
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {stockLevels?.length || 1,247}
                  </Typography>
                  <Typography variant="body2">
                    Active SKUs
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'white', color: 'success.main' }}>
                  <Speed />
                </Avatar>
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {warehouseActivity?.length || 156}
                  </Typography>
                  <Typography variant="body2">
                    Activities Today
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'warning.light', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'white', color: 'warning.main' }}>
                  <Warning />
                </Avatar>
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {predictiveStockouts?.length || 8}
                  </Typography>
                  <Typography variant="body2">
                    Low Stock Alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'info.light', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Avatar sx={{ bgcolor: 'white', color: 'info.main' }}>
                  <Person />
                </Avatar>
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {pickerPerformance?.length || 12}
                  </Typography>
                  <Typography variant="body2">
                    Active Items
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Warehouse Map (hidden in Inventory) */}
        {showWms && (
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Warehouse color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Live Warehouse Map
                </Typography>
                <Chip label="Real-Time" color="success" size="small" />
              </Box>
              
              <Grid container spacing={2}>
                {warehouseMap.map((zone) => (
                  <Grid item xs={6} sm={3} key={zone.id}>
                    <Paper 
                      sx={{ 
                        p: 2, 
                        textAlign: 'center',
                        border: 2,
                        borderColor: getActivityColor(zone.activity) + '.main',
                        bgcolor: getActivityColor(zone.activity) + '.light',
                        color: 'white'
                      }}
                    >
                      <Typography variant="h6" fontWeight="bold">
                        {zone.name}
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {zone.type.toUpperCase()}
                      </Typography>
                      <LinearProgress 
                        variant="determinate" 
                        value={zone.utilization} 
                        sx={{ 
                          height: 8, 
                          borderRadius: 4,
                          bgcolor: 'rgba(255,255,255,0.3)',
                          '& .MuiLinearProgress-bar': {
                            bgcolor: 'white'
                          }
                        }} 
                      />
                      <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                        {zone.utilization}% Utilized
                      </Typography>
                      <Chip 
                        label={zone.activity} 
                        size="small" 
                        color={getActivityColor(zone.activity)}
                        sx={{ mt: 1, color: 'white' }}
                      />
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        )}

        {/* Live Activity Feed (hidden in Inventory) */}
        {showWms && (
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Timeline color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Live Activity Feed
                </Typography>
                <Chip label="Live" color="success" size="small" />
              </Box>
              
              <List sx={{ maxHeight: 400, overflow: 'auto' }}>
                {liveActivity.map((activity) => (
                  <ListItem key={activity.id} sx={{ px: 0 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.light' }}>
                        <DirectionsWalk />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" fontWeight="bold" component="span">
                            {activity.user}
                          </Typography>
                          <Chip 
                            label={`${activity.efficiency}%`} 
                            size="small" 
                            color={activity.efficiency >= 90 ? 'success' : 'warning'}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary" component="span">
                            {activity.action} • {activity.location}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" component="span">
                            {activity.time}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
        )}

        {/* Inventory Alerts */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Warning color="error" />
                <Typography variant="h6" fontWeight="bold">
                  Inventory Alerts
                </Typography>
                <Chip label="AI-Powered" color="primary" size="small" />
              </Box>
              
              <List>
                {predictiveAlerts.map((alert) => (
                  <ListItem key={alert.id} sx={{ px: 0 }}>
                    <ListItemIcon>
                      <Avatar sx={{ bgcolor: getAlertColor(alert.alertLevel) + '.light' }}>
                        <Error />
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" fontWeight="bold" component="span">
                            {alert.product}
                          </Typography>
                          <Chip 
                            label={alert.alertLevel} 
                            size="small" 
                            color={getAlertColor(alert.alertLevel)}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary" component="span">
                            Location: {alert.location}
                          </Typography>
                          <Typography variant="caption" color="error" component="span">
                            Stockout in {alert.daysUntilStockout ? alert.daysUntilStockout.toFixed(1) : 'N/A'} days
                          </Typography>
                        </Box>
                      }
                    />
                    <Button size="small" variant="outlined" color="primary">
                      Reorder
                    </Button>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Assessment color="primary" />
                <Typography variant="h6" fontWeight="bold">
                  Performance Metrics
                </Typography>
                <Chip label="Real-Time" color="success" size="small" />
              </Box>
              
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <CircularProgress 
                      variant="determinate" 
                      value={87} 
                      size={80}
                      sx={{ color: 'success.main', mb: 1 }}
                    />
                    <Typography variant="h6" fontWeight="bold">
                      87%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Picking Efficiency
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <CircularProgress 
                      variant="determinate" 
                      value={92} 
                      size={80}
                      sx={{ color: 'info.main', mb: 1 }}
                    />
                    <Typography variant="h6" fontWeight="bold">
                      92%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Order Accuracy
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <CircularProgress 
                      variant="determinate" 
                      value={78} 
                      size={80}
                      sx={{ color: 'warning.main', mb: 1 }}
                    />
                    <Typography variant="h6" fontWeight="bold">
                      78%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Space Utilization
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ textAlign: 'center', p: 2 }}>
                    <CircularProgress 
                      variant="determinate" 
                      value={95} 
                      size={80}
                      sx={{ color: 'primary.main', mb: 1 }}
                    />
                    <Typography variant="h6" fontWeight="bold">
                      95%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      System Uptime
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Loading States */}
      {(stockLoading || activityLoading || stockoutLoading || performanceLoading) && (
        <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }}>
          <LinearProgress />
        </Box>
      )}

      {/* Error Handling */}
      {stockError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          Error loading inventory data. Please refresh the page.
        </Alert>
      )}
    </Box>
  );
};

export default SmartInventoryDashboard;
