import React from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';
import { Engineering as EquipmentIcon } from '@mui/icons-material';

const EquipmentMaintenance = () => {
  return (
    <Box>
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
          🔧 Equipment & Maintenance
        </Typography>
        <Typography variant="body2">
          Equipment tracking, preventive maintenance, and asset management.
        </Typography>
      </Alert>
      <Chip label="Equipment Maintenance - Coming Soon" color="primary" />
    </Box>
  );
};

export default EquipmentMaintenance;
