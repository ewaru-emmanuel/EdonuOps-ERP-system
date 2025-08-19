import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Widgets as WidgetIcon
} from '@mui/icons-material';

const DashboardCustomization = () => {
  const [dashboards, setDashboards] = useState([]);

  useEffect(() => {
    fetchDashboards();
  }, []);

  const fetchDashboards = async () => {
    // Mock dashboards data
    const mockDashboards = [
      {
        id: 1,
        name: 'Executive Dashboard',
        description: 'High-level overview for executives',
        widgets: 8,
        isDefault: true,
        lastModified: '2024-03-15T10:30:00Z'
      },
      {
        id: 2,
        name: 'Sales Dashboard',
        description: 'Sales performance and metrics',
        widgets: 6,
        isDefault: false,
        lastModified: '2024-03-14T15:45:00Z'
      },
      {
        id: 3,
        name: 'Finance Dashboard',
        description: 'Financial metrics and reports',
        widgets: 5,
        isDefault: false,
        lastModified: '2024-03-13T09:20:00Z'
      }
    ];
    setDashboards(mockDashboards);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
          Dashboard Builder
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ borderRadius: 2 }}
        >
          Create Dashboard
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Dashboard List */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Custom Dashboards
              </Typography>
              
              <List>
                {dashboards.map((dashboard) => (
                  <ListItem
                    key={dashboard.id}
                    sx={{
                      border: 1,
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 2,
                      '&:hover': {
                        bgcolor: 'action.hover'
                      }
                    }}
                  >
                    <ListItemIcon>
                      <DashboardIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {dashboard.name}
                          </Typography>
                          {dashboard.isDefault && (
                            <Chip label="DEFAULT" color="success" size="small" />
                          )}
                          <Chip
                            label={`${dashboard.widgets} widgets`}
                            color="primary"
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                            {dashboard.description}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            Last modified: {new Date(dashboard.lastModified).toLocaleDateString()}
                          </Typography>
                        </Box>
                      }
                    />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="small"
                        sx={{ color: 'primary.main' }}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        sx={{ color: 'success.main' }}
                      >
                        <WidgetIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        sx={{ color: 'error.main' }}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Available Widgets */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Available Widgets
              </Typography>
              
              <Grid container spacing={2}>
                {[
                  { name: 'Chart Widget', icon: '📊' },
                  { name: 'Metric Card', icon: '📈' },
                  { name: 'Data Table', icon: '📋' },
                  { name: 'Gauge Chart', icon: '🎯' },
                  { name: 'Progress Bar', icon: '📊' },
                  { name: 'Calendar', icon: '📅' }
                ].map((widget) => (
                  <Grid item xs={6} key={widget.name}>
                    <Card
                      variant="outlined"
                      sx={{
                        cursor: 'pointer',
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                    >
                      <CardContent sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ mb: 1 }}>
                          {widget.icon}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {widget.name}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardCustomization;
