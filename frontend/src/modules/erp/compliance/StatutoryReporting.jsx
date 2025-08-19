import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';

const StatutoryReporting = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          📋 Statutory Reporting
        </Typography>
        <Typography variant="body2">
          Country-specific statutory reports and regulatory filings with automated compliance checks.
        </Typography>
      </Alert>
      <Chip label="Statutory Reporting - Coming Soon" color="primary" />
    </Box>
  );
};

export default StatutoryReporting;
