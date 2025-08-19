import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Visibility as VisibilityIcon,
  AccessTime as AccessTimeIcon,
  Star as StarIcon
} from '@mui/icons-material';

const DashboardAnalytics = () => {
  const analyticsData = {
    totalViews: 1247,
    avgSessionTime: '8.5 min',
    mostViewed: 'Executive Dashboard',
    topPerformer: 'Sales Analytics',
    userEngagement: 78,
    dashboardEfficiency: 92
  };

  const popularDashboards = [
    { name: 'Executive Dashboard', views: 342, growth: 15 },
    { name: 'Sales Analytics', views: 298, growth: 8 },
    { name: 'Financial Overview', views: 245, growth: 12 },
    { name: 'HR Dashboard', views: 189, growth: -3 },
    { name: 'Inventory Management', views: 156, growth: 5 }
  ];

  const performanceMetrics = [
    { name: 'Load Time', value: 92, target: 95 },
    { name: 'User Satisfaction', value: 87, target: 90 },
    { name: 'Widget Performance', value: 94, target: 95 },
    { name: 'Data Accuracy', value: 98, target: 99 }
  ];

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Dashboard Analytics</Typography>
      
      {/* Key Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <VisibilityIcon color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary">Total Views</Typography>
              </Box>
              <Typography variant="h4">
                {analyticsData.totalViews.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <AccessTimeIcon color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary">Avg Session</Typography>
              </Box>
              <Typography variant="h4">
                {analyticsData.avgSessionTime}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary">Engagement</Typography>
              </Box>
              <Typography variant="h4">
                {analyticsData.userEngagement}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <StarIcon color="primary" sx={{ mr: 1 }} />
                <Typography color="textSecondary">Efficiency</Typography>
              </Box>
              <Typography variant="h4">
                {analyticsData.dashboardEfficiency}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Popular Dashboards */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Most Popular Dashboards</Typography>
              {popularDashboards.map((dashboard, index) => (
                <Box key={index} mb={2}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2">{dashboard.name}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      {dashboard.views} views
                    </Typography>
                  </Box>
                  <Box display="flex" alignItems="center">
                    <LinearProgress
                      variant="determinate"
                      value={(dashboard.views / popularDashboards[0].views) * 100}
                      sx={{ flexGrow: 1, mr: 1 }}
                    />
                    <Typography variant="body2" color={dashboard.growth >= 0 ? 'success.main' : 'error.main'}>
                      {dashboard.growth >= 0 ? '+' : ''}{dashboard.growth}%
                    </Typography>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Performance Metrics</Typography>
              {performanceMetrics.map((metric, index) => (
                <Box key={index} mb={2}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="body2">{metric.name}</Typography>
                    <Typography variant="body2" color="textSecondary">
                      {metric.value}% / {metric.target}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(metric.value / metric.target) * 100}
                    color={metric.value >= metric.target ? 'success' : 'warning'}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardAnalytics;


