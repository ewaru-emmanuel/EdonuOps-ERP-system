import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';

const QualityControl = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          ✅ Quality Control Management
        </Typography>
        <Typography variant="body2">
          Quality assurance, inspection management, and compliance tracking.
        </Typography>
      </Alert>
      <Chip label="Quality Control - Coming Soon" color="primary" />
    </Box>
  );
};

export default QualityControl;
