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
  Code as CodeIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as RunIcon
} from '@mui/icons-material';

const CodeCustomization = () => {
  const [scripts, setScripts] = useState([]);

  useEffect(() => {
    fetchScripts();
  }, []);

  const fetchScripts = async () => {
    // Mock scripts data
    const mockScripts = [
      {
        id: 1,
        name: 'Invoice Automation',
        description: 'Automated invoice processing script',
        language: 'Python',
        status: 'active',
        lastRun: '2024-03-15T10:30:00Z'
      },
      {
        id: 2,
        name: 'Data Export',
        description: 'Export data to external systems',
        language: 'JavaScript',
        status: 'draft',
        lastRun: null
      },
      {
        id: 3,
        name: 'Report Generator',
        description: 'Generate custom reports',
        language: 'Python',
        status: 'active',
        lastRun: '2024-03-14T15:45:00Z'
      }
    ];
    setScripts(mockScripts);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'draft': return 'warning';
      case 'inactive': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
          Code Customization
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ borderRadius: 2 }}
        >
          Create Script
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Scripts List */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Custom Scripts
              </Typography>
              
              <List>
                {scripts.map((script) => (
                  <ListItem
                    key={script.id}
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
                      <CodeIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                            {script.name}
                          </Typography>
                          <Chip
                            label={script.status.toUpperCase()}
                            color={getStatusColor(script.status)}
                            size="small"
                          />
                          <Chip
                            label={script.language}
                            color="primary"
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                            {script.description}
                          </Typography>
                          {script.lastRun && (
                            <Typography variant="caption" color="textSecondary">
                              Last run: {new Date(script.lastRun).toLocaleDateString()}
                            </Typography>
                          )}
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
                        <RunIcon />
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

        {/* Development Tools */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Development Tools
              </Typography>
              
              <Grid container spacing={2}>
                {[
                  { name: 'Code Editor', icon: '📝' },
                  { name: 'Debug Console', icon: '🐛' },
                  { name: 'API Testing', icon: '🔌' },
                  { name: 'Database Query', icon: '🗄️' },
                  { name: 'Log Viewer', icon: '📋' },
                  { name: 'Performance Monitor', icon: '⚡' }
                ].map((tool) => (
                  <Grid item xs={6} key={tool.name}>
                    <Card
                      variant="outlined"
                      sx={{
                        cursor: 'pointer',
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                    >
                      <CardContent sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="h4" sx={{ mb: 1 }}>
                          {tool.icon}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {tool.name}
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

export default CodeCustomization;
