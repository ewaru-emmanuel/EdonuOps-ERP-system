import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';

const Consolidation = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          🔗 Financial Consolidation
        </Typography>
        <Typography variant="body2">
          Multi-entity financial consolidation with elimination entries and intercompany transactions.
        </Typography>
      </Alert>
      <Chip label="Consolidation - Coming Soon" color="primary" />
    </Box>
  );
};

export default Consolidation;
