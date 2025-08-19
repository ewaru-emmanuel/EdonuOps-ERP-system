import React from 'react';
import { Box, Paper, Typography, Button, Grid, Card, CardContent, Chip } from '@mui/material';
import { IntegrationInstructions, Email, CalendarToday, Notifications, CloudSync } from '@mui/icons-material';

const CRMIntegrations = () => {
  const integrations = [
    { name: 'Email Integration', status: 'connected', icon: Email, description: 'Sync emails and contacts' },
    { name: 'Calendar Sync', status: 'connected', icon: CalendarToday, description: 'Schedule meetings and events' },
    { name: 'Slack Notifications', status: 'available', icon: Notifications, description: 'Real-time notifications' },
    { name: 'Cloud Storage', status: 'available', icon: CloudSync, description: 'File and document sync' }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" fontWeight="bold" sx={{ mb: 3 }}>
        CRM Integrations
      </Typography>
      
      <Grid container spacing={3}>
        {integrations.map((integration) => (
          <Grid item xs={12} md={6} lg={3} key={integration.name}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <integration.icon sx={{ mr: 2, color: 'primary.main' }} />
                  <Box>
                    <Typography variant="h6" fontWeight="medium">
                      {integration.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {integration.description}
                    </Typography>
                  </Box>
                </Box>
                <Chip 
                  label={integration.status} 
                  color={integration.status === 'connected' ? 'success' : 'default'} 
                  size="small" 
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default CRMIntegrations;


