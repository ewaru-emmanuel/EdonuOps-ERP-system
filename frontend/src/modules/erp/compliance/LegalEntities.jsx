import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';

const LegalEntities = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          🏢 Legal Entities Management
        </Typography>
        <Typography variant="body2">
          Multi-entity management and organizational structure across global operations.
        </Typography>
      </Alert>
      <Chip label="Legal Entities - Coming Soon" color="primary" />
    </Box>
  );
};

export default LegalEntities;
