import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';

const ComplianceAnalytics = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          📊 Compliance Analytics
        </Typography>
        <Typography variant="body2">
          Compliance analytics, risk assessment, and performance monitoring across all regulatory frameworks.
        </Typography>
      </Alert>
      <Chip label="Compliance Analytics - Coming Soon" color="primary" />
    </Box>
  );
};

export default ComplianceAnalytics;
