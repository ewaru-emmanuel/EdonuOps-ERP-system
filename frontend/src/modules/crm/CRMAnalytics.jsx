import React from 'react';
import { Box, Paper, Typography, Grid, Card, CardContent, Chip } from '@mui/material';
import { TrendingUp, TrendingDown, AttachMoney, People, Business, Schedule } from '@mui/icons-material';

const CRMAnalytics = () => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  const metrics = [
    { title: 'Total Revenue', value: formatCurrency(125000), icon: AttachMoney, color: 'success.main', trend: '+12%' },
    { title: 'Active Deals', value: '24', icon: Business, color: 'primary.main', trend: '+5%' },
    { title: 'Total Contacts', value: '156', icon: People, color: 'info.main', trend: '+8%' },
    { title: 'Win Rate', value: '68%', icon: TrendingUp, color: 'warning.main', trend: '+3%' }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>
        CRM Analytics
      </Typography>

      <Grid container spacing={3}>
        {metrics.map((metric) => (
          <Grid item xs={12} md={6} lg={3} key={metric.title}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <metric.icon sx={{ mr: 2, color: metric.color, fontSize: 32 }} />
                  <Box>
                    <Typography variant="h4" fontWeight="bold">
                      {metric.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {metric.title}
                    </Typography>
                  </Box>
                </Box>
                <Chip 
                  label={metric.trend} 
                  color="success" 
                  size="small" 
                  icon={<TrendingUp />}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" fontWeight="medium" gutterBottom>
          Pipeline Overview
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h5" color="info.main" fontWeight="bold">
                12
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Prospecting
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h5" color="warning.main" fontWeight="bold">
                8
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Qualification
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h5" color="error.main" fontWeight="bold">
                4
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Proposal
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={3}>
            <Box sx={{ textAlign: 'center', p: 2 }}>
              <Typography variant="h5" color="success.main" fontWeight="bold">
                16
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Won
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default CRMAnalytics;
