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
  Extension as ExtensionIcon,
  Add as AddIcon,
  Settings as SettingsIcon,
  Delete as DeleteIcon,
  Update as UpdateIcon
} from '@mui/icons-material';

const ExtensionManagement = () => {
  const [extensions, setExtensions] = useState([]);

  useEffect(() => {
    fetchExtensions();
  }, []);

  const fetchExtensions = async () => {
    // Mock extensions data
    const mockExtensions = [
      {
        id: 1,
        name: 'Advanced Reporting',
        description: 'Enhanced reporting capabilities with custom charts',
        version: '1.2.0',
        status: 'installed',
        author: 'EdonuOps Team'
      },
      {
        id: 2,
        name: 'Email Integration',
        description: 'Seamless email integration with popular providers',
        version: '2.1.0',
        status: 'installed',
        author: 'EdonuOps Team'
      },
      {
        id: 3,
        name: 'Mobile App',
        description: 'Mobile application for field operations',
        version: '1.0.5',
        status: 'available',
        author: 'EdonuOps Team'
      }
    ];
    setExtensions(mockExtensions);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'installed': return 'success';
      case 'available': return 'primary';
      case 'updating': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
          Extension Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ borderRadius: 2 }}
        >
          Browse Marketplace
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Installed Extensions */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Installed Extensions
              </Typography>
              
              <List>
                {extensions.map((extension) => (
                  <ListItem
                    key={extension.id}
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
                      <ExtensionIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {extension.name}
                          </Typography>
                          <Chip
                            label={extension.status.toUpperCase()}
                            color={getStatusColor(extension.status)}
                            size="small"
                          />
                          <Chip
                            label={`v${extension.version}`}
                            color="primary"
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                            {extension.description}
                          </Typography>
                          <Typography variant="caption" color="textSecondary">
                            By {extension.author}
                          </Typography>
                        </Box>
                      }
                    />
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <IconButton
                        size="small"
                        sx={{ color: 'primary.main' }}
                      >
                        <SettingsIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        sx={{ color: 'info.main' }}
                      >
                        <UpdateIcon />
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

        {/* Extension Categories */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Extension Categories
              </Typography>
              
              <Grid container spacing={2}>
                {[
                  { name: 'Reporting', icon: '📊', count: 15 },
                  { name: 'Integration', icon: '🔌', count: 8 },
                  { name: 'Automation', icon: '⚡', count: 12 },
                  { name: 'Analytics', icon: '📈', count: 6 },
                  { name: 'Communication', icon: '💬', count: 10 },
                  { name: 'Security', icon: '🔒', count: 4 }
                ].map((category) => (
                  <Grid item xs={6} key={category.name}>
                    <Card
                      variant="outlined"
                      sx={{
                        cursor: 'pointer',
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                    >
                      <CardContent sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ mb: 1 }}>
                          {category.icon}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {category.name}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {category.count} extensions
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

export default ExtensionManagement;
