import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';
import { Assessment as AnalyticsIcon } from '@mui/icons-material';

const ManufacturingAnalytics = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          📊 Manufacturing Analytics
        </Typography>
        <Typography variant="body2">
          Manufacturing performance analytics, insights, and KPI tracking.
        </Typography>
      </Alert>
      <Chip label="Manufacturing Analytics - Coming Soon" color="primary" />
    </Box>
  );
};

export default ManufacturingAnalytics;
