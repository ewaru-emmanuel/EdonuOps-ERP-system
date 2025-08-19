import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Alert
} from '@mui/material';
import {
  Timeline as PlanningIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon
} from '@mui/icons-material';

const ProductionPlanning = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          🎯 MRP II Production Planning
        </Typography>
        <Typography variant="body2">
          Advanced Material Requirements Planning with production scheduling, capacity planning, and demand forecasting.
        </Typography>
      </Alert>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <PlanningIcon color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Production Schedule
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Manage production orders, scheduling, and capacity planning with advanced MRP II algorithms.
              </Typography>
              <Button variant="contained" startIcon={<ScheduleIcon />}>
                View Schedule
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2} mb={2}>
                <TrendingUpIcon color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                  Demand Forecasting
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                AI-powered demand forecasting and inventory optimization for efficient production planning.
              </Typography>
              <Button variant="contained" startIcon={<TrendingUpIcon />}>
                Forecast Demand
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper elevation={3} sx={{ borderRadius: 2, p: 3, mt: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold' }}>
          Production Planning Features
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Chip label="MRP II Planning" color="primary" sx={{ mb: 1 }} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Chip label="Capacity Planning" color="primary" sx={{ mb: 1 }} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Chip label="Demand Forecasting" color="primary" sx={{ mb: 1 }} />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Chip label="Production Scheduling" color="primary" sx={{ mb: 1 }} />
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default ProductionPlanning;
