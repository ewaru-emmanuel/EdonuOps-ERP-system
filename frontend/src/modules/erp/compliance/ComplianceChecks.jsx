import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';

const ComplianceChecks = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          ✅ Compliance Checks
        </Typography>
        <Typography variant="body2">
          Automated compliance validation, monitoring, and risk assessment across all entities.
        </Typography>
      </Alert>
      <Chip label="Compliance Checks - Coming Soon" color="primary" />
    </Box>
  );
};

export default ComplianceChecks;
