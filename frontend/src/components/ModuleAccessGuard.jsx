import React from 'react';
import { Box, Card, CardContent, Typography, Button, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useModuleAccess } from '../hooks/useModuleAccess';
import { Settings as SettingsIcon } from '@mui/icons-material';

const ModuleAccessGuard = ({ moduleId, children, fallback }) => {
  const { canAccessModule, hasPreferences } = useModuleAccess();
  const navigate = useNavigate();

  // If no preferences set, allow access (show all modules)
  if (!hasPreferences) {
    return children;
  }

  // If module is enabled, show the content
  if (canAccessModule(moduleId)) {
    return children;
  }

  // If module is disabled, show fallback or default message
  if (fallback) {
    return fallback;
  }

  // Default fallback UI
  return (
    <Box sx={{ p: 3, textAlign: 'center' }}>
      <Card elevation={2}>
        <CardContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Module Not Enabled
            </Typography>
            <Typography variant="body2">
              This module is not currently enabled in your account. 
              You can enable it through the onboarding process.
            </Typography>
          </Alert>
          
          <Button
            variant="contained"
            startIcon={<SettingsIcon />}
            onClick={() => navigate('/onboarding')}
            sx={{ mt: 2 }}
          >
            Enable Module
          </Button>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ModuleAccessGuard;
