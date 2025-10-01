import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button
} from '@mui/material';
import {
  People as PeopleIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

const AdminModule = () => {
  const adminFeatures = [
    {
      title: 'User Management',
      description: 'Manage users, roles, and permissions',
      icon: <PeopleIcon sx={{ fontSize: 40 }} />,
      color: '#1976d2'
    },
    {
      title: 'Security Settings',
      description: 'Configure security policies and access controls',
      icon: <SecurityIcon sx={{ fontSize: 40 }} />,
      color: '#d32f2f'
    },
    {
      title: 'System Configuration',
      description: 'System-wide settings and configurations',
      icon: <SettingsIcon sx={{ fontSize: 40 }} />,
      color: '#388e3c'
    },
    {
      title: 'Audit & Reports',
      description: 'System audit logs and administrative reports',
      icon: <AssessmentIcon sx={{ fontSize: 40 }} />,
      color: '#f57c00'
    }
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Administration
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Manage system settings, users, and administrative functions.
      </Typography>

      <Grid container spacing={3}>
        {adminFeatures.map((feature, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card 
              sx={{ 
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 3
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1, textAlign: 'center', p: 3 }}>
                <Box sx={{ color: feature.color, mb: 2 }}>
                  {feature.icon}
                </Box>
                <Typography variant="h6" gutterBottom>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {feature.description}
                </Typography>
                <Button 
                  variant="outlined" 
                  size="small"
                  sx={{ borderColor: feature.color, color: feature.color }}
                >
                  Access
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item>
            <Button variant="contained" color="primary">
              Create New User
            </Button>
          </Grid>
          <Grid item>
            <Button variant="contained" color="secondary">
              System Backup
            </Button>
          </Grid>
          <Grid item>
            <Button variant="outlined">
              View Audit Logs
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
};

export default AdminModule;







