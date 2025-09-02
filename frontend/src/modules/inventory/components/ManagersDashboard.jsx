import React, { useState, useEffect, useMemo } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Paper, Chip, Avatar, 
  List, ListItem, ListItemText, ListItemAvatar, Divider, 
  CircularProgress, Alert, IconButton, Tooltip, Badge,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  LinearProgress, Button, Dialog, DialogTitle, DialogContent,
  DialogActions, TextField, MenuItem, FormControl, InputLabel, Select
} from '@mui/material';
import {
  LocationOn, Warning, TrendingUp, TrendingDown, 
  Person, Speed, CheckCircle, Error, Info,
  Refresh, Fullscreen, Settings, Notifications,
  LocalShipping, Inventory, Assessment, Timeline
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const ManagersDashboard = () => {
  const [selectedZone, setSelectedZone] = useState(null);
  const [showZoneDetails, setShowZoneDetails] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds
  
  // Real-time data hooks
  const { data: warehouseMap, loading: mapLoading, error: mapError } = useRealTimeData(
    '/api/inventory/manager/warehouse-map', 
    refreshInterval
  );
  
  const { data: predictiveAlerts, loading: alertsLoading } = useRealTimeData(
    '/api/inventory/manager/predictive-alerts',
    refreshInterval
  );
  
  const { data: pickerPerformance, loading: performanceLoading } = useRealTimeData(
    '/api/inventory/manager/picker-performance',
    refreshInterval
  );
  
  const { data: liveActivity, loading: activityLoading } = useRealTimeData(
    '/api/inventory/manager/live-activity',
    10000 // 10 seconds for live activity
  );

  // Real-time data from API
  const warehouseData = warehouseMap || { zones: [], total_pickers: 0, total_orders: 0, completed_today: 0, efficiency_avg: 0 };
  const alertsData = predictiveAlerts || [];
  const performanceData = pickerPerformance || [];
  const activityData = liveActivity || [];

  const getZoneColor = (utilization, status) => {
    if (status === 'congested') return '#f44336';
    if (status === 'low_activity') return '#9e9e9e';
    if (utilization > 80) return '#ff9800';
    if (utilization > 60) return '#4caf50';
    return '#2196f3';
  };

  const getAlertIcon = (type) => {
    switch (type) {
      case 'stockout': return <Inventory color="error" />;
      case 'congestion': return <LocalShipping color="warning" />;
      case 'efficiency': return <Assessment color="info" />;
      default: return <Info color="primary" />;
    }
  };

  const getAlertColor = (severity) => {
    switch (severity) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'break': return 'warning';
      case 'training': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          🏭 Manager's Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Refresh Data">
            <IconButton>
              <Refresh />
            </IconButton>
          </Tooltip>
          <Tooltip title="Full Screen">
            <IconButton>
              <Fullscreen />
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Live Warehouse Map */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: '600px' }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationOn color="primary" />
                Live Warehouse Map
              </Typography>
              
              {mapLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
                  <CircularProgress />
                </Box>
              ) : (
                <Box sx={{ position: 'relative', height: '500px', bgcolor: 'grey.100', borderRadius: 2, p: 2 }}>
                  {/* Warehouse Zones */}
                  <Grid container spacing={2} sx={{ height: '100%' }}>
                    {warehouseData.zones?.map((zone) => (
                      <Grid item xs={6} md={4} key={zone.id}>
                        <Paper
                          sx={{
                            p: 2,
                            height: '120px',
                            cursor: 'pointer',
                            border: 2,
                            borderColor: getZoneColor(zone.utilization, zone.status),
                            bgcolor: 'white',
                            '&:hover': {
                              bgcolor: 'grey.50',
                              transform: 'scale(1.02)',
                              transition: 'all 0.2s'
                            }
                          }}
                          onClick={() => {
                            setSelectedZone(zone);
                            setShowZoneDetails(true);
                          }}
                        >
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                            {zone.name}
                          </Typography>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="caption">Utilization:</Typography>
                            <Typography variant="caption" sx={{ fontWeight: 'bold' }}>
                              {zone.utilization}%
                            </Typography>
                          </Box>
                          <LinearProgress 
                            variant="determinate" 
                            value={zone.utilization} 
                            sx={{ 
                              height: 8, 
                              borderRadius: 4,
                              bgcolor: 'grey.200',
                              '& .MuiLinearProgress-bar': {
                                bgcolor: getZoneColor(zone.utilization, zone.status)
                              }
                            }} 
                          />
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                            <Chip 
                              label={`${zone.pickers} pickers`} 
                              size="small" 
                              color={zone.pickers > 0 ? 'primary' : 'default'}
                            />
                            <Chip 
                              label={`${zone.efficiency}%`} 
                              size="small" 
                              color={zone.efficiency > 90 ? 'success' : zone.efficiency > 80 ? 'warning' : 'error'}
                            />
                          </Box>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                  
                  {/* Summary Stats */}
                  <Box sx={{ 
                    position: 'absolute', 
                    bottom: 16, 
                    left: 16, 
                    right: 16,
                    bgcolor: 'rgba(255,255,255,0.9)',
                    p: 2,
                    borderRadius: 2,
                    display: 'flex',
                    justifyContent: 'space-around'
                  }}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h6" color="primary">{warehouseData.total_pickers}</Typography>
                      <Typography variant="caption">Active Pickers</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h6" color="success.main">{warehouseData.completed_today}</Typography>
                      <Typography variant="caption">Completed Today</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h6" color="info.main">{warehouseData.total_orders}</Typography>
                      <Typography variant="caption">Total Orders</Typography>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h6" color="warning.main">{warehouseData.efficiency_avg}%</Typography>
                      <Typography variant="caption">Avg Efficiency</Typography>
                    </Box>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column */}
        <Grid item xs={12} lg={4}>
          <Grid container spacing={3}>
            {/* Predictive Alerts Ticker */}
            <Grid item xs={12}>
              <Card sx={{ height: '300px' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Warning color="warning" />
                    Predictive Alerts
                    <Badge badgeContent={alertsData.length} color="error" sx={{ ml: 1 }} />
                  </Typography>
                  
                  {alertsLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
                      <CircularProgress />
                    </Box>
                  ) : (
                    <Box sx={{ height: '200px', overflow: 'auto' }}>
                      {alertsData.map((alert) => (
                        <Alert 
                          key={alert.id}
                          severity={getAlertColor(alert.severity)}
                          icon={getAlertIcon(alert.type)}
                          sx={{ mb: 1 }}
                        >
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {alert.type === 'stockout' && `${alert.product} - ${alert.days_until} days until stockout`}
                            {alert.type === 'congestion' && `Congestion at ${alert.location}: ${alert.reason}`}
                            {alert.type === 'efficiency' && `${alert.picker}: ${alert.metric}`}
                          </Typography>
                        </Alert>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Picker Performance Leaderboard */}
            <Grid item xs={12}>
              <Card sx={{ height: '280px' }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TrendingUp color="success" />
                    Picker Performance
                  </Typography>
                  
                  {performanceLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '180px' }}>
                      <CircularProgress />
                    </Box>
                  ) : (
                    <Box sx={{ height: '180px', overflow: 'auto' }}>
                      <TableContainer>
                        <Table size="small">
                          <TableHead>
                            <TableRow>
                              <TableCell>Picker</TableCell>
                              <TableCell align="right">Picks</TableCell>
                              <TableCell align="right">Efficiency</TableCell>
                              <TableCell align="center">Status</TableCell>
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {performanceData.slice(0, 5).map((picker) => (
                              <TableRow key={picker.id} hover>
                                <TableCell>
                                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                    <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                                      {picker.name ? picker.name.split(' ').map(n => n[0]).join('') : 'N/A'}
                                    </Avatar>
                                    <Typography variant="body2">{picker.name || 'Unknown'}</Typography>
                                  </Box>
                                </TableCell>
                                <TableCell align="right">
                                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                                    {picker.picks_today || 0}
                                  </Typography>
                                </TableCell>
                                <TableCell align="right">
                                  <Chip 
                                    label={`${picker.efficiency || 0}%`} 
                                    size="small" 
                                    color={(picker.efficiency || 0) > 90 ? 'success' : (picker.efficiency || 0) > 80 ? 'warning' : 'error'}
                                  />
                                </TableCell>
                                <TableCell align="center">
                                  <Chip 
                                    label={picker.status || 'unknown'} 
                                    size="small" 
                                    color={getStatusColor(picker.status || 'unknown')}
                                  />
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Live Activity Feed */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Timeline color="primary" />
                Live Activity Feed
              </Typography>
              
              {activityLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                  <CircularProgress />
                </Box>
              ) : (
                <List sx={{ maxHeight: '200px', overflow: 'auto' }}>
                  {activityData.map((activity, index) => (
                    <React.Fragment key={activity.id}>
                      <ListItem>
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: 'primary.main' }}>
                            <Person />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={`${activity.user || 'Unknown User'} - ${activity.time || 'Unknown Time'}`}
                          secondary={
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                              <span>
                                {activity.activity || 'Unknown Activity'} at {activity.location || 'Unknown Location'}
                              </span>
                              <Chip 
                                label={`${activity.efficiency || 0}%`} 
                                size="small" 
                                color={(activity.efficiency || 0) > 90 ? 'success' : 'warning'}
                              />
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < activityData.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Zone Details Dialog */}
      <Dialog 
        open={showZoneDetails} 
        onClose={() => setShowZoneDetails(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Zone Details: {selectedZone?.name}
        </DialogTitle>
        <DialogContent>
          {selectedZone && (
            <Grid container spacing={3}>
              <Grid item xs={6}>
                <Typography variant="h6">Utilization</Typography>
                <Typography variant="h4" color="primary">{selectedZone.utilization}%</Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={selectedZone.utilization} 
                  sx={{ height: 10, mt: 1 }}
                />
              </Grid>
              <Grid item xs={6}>
                <Typography variant="h6">Efficiency</Typography>
                <Typography variant="h4" color="success.main">{selectedZone.efficiency}%</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="h6">Active Pickers</Typography>
                <Typography variant="h4" color="info.main">{selectedZone.pickers}</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="h6">Status</Typography>
                <Chip 
                  label={selectedZone.status} 
                  color={selectedZone.status === 'active' ? 'success' : 'warning'}
                  sx={{ mt: 1 }}
                />
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowZoneDetails(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ManagersDashboard;

