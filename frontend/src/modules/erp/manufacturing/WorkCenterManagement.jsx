import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';
import { Build as WorkCenterIcon } from '@mui/icons-material';

const WorkCenterManagement = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          🏭 Work Center Management
        </Typography>
        <Typography variant="body2">
          Manage production work centers, capacity planning, and resource allocation.
        </Typography>
      </Alert>
      <Chip label="Work Center Management - Coming Soon" color="primary" />
    </Box>
  );
};

export default WorkCenterManagement;
