import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';

const FinancialStatements = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          📊 Financial Statements
        </Typography>
        <Typography variant="body2">
          Entity-level financial statements and reporting with multi-currency support.
        </Typography>
      </Alert>
      <Chip label="Financial Statements - Coming Soon" color="primary" />
    </Box>
  );
};

export default FinancialStatements;
