import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  LinearProgress
} from '@mui/material';
import {
  AutoAwesome as AutoIcon,
  TrendingUp as TrendingIcon,
  PlayArrow as PlayIcon
} from '@mui/icons-material';

const AIAutomation = () => {
  const [automations, setAutomations] = useState([]);
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    fetchAutomationData();
  }, []);

  const fetchAutomationData = async () => {
    // Mock automation data
    const mockAutomations = [
      {
        id: 1,
        name: 'Invoice Processing Automation',
        description: 'Automatically process incoming invoices and route for approval',
        status: 'active',
        efficiency: 85,
        timeSaved: '2 hours/day',
        type: 'finance'
      },
      {
        id: 2,
        name: 'Inventory Reorder Automation',
        description: 'Automatically reorder items when stock levels are low',
        status: 'active',
        efficiency: 92,
        timeSaved: '1 hour/day',
        type: 'inventory'
      },
      {
        id: 3,
        name: 'Customer Follow-up Automation',
        description: 'Automated follow-up emails and reminders for customers',
        status: 'draft',
        efficiency: 0,
        timeSaved: '3 hours/day',
        type: 'crm'
      }
    ];

    const mockSuggestions = [
      {
        id: 1,
        title: 'Automate Expense Approval',
        description: 'Create automated approval workflows for expense reports',
        potentialSavings: '5 hours/week',
        priority: 'high',
        category: 'finance'
      },
      {
        id: 2,
        title: 'Sales Lead Scoring',
        description: 'Implement AI-powered lead scoring and prioritization',
        potentialSavings: '3 hours/week',
        priority: 'medium',
        category: 'sales'
      },
      {
        id: 3,
        title: 'Report Generation',
        description: 'Automate monthly and quarterly report generation',
        potentialSavings: '8 hours/month',
        priority: 'high',
        category: 'reporting'
      }
    ];

    setAutomations(mockAutomations);
    setSuggestions(mockSuggestions);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'success';
      case 'draft': return 'warning';
      case 'inactive': return 'error';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        AI-Powered Automation
      </Typography>

      <Grid container spacing={3}>
        {/* Active Automations */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <AutoIcon sx={{ mr: 1 }} />
                Active Automations
              </Typography>
              
              <List>
                {automations.map((automation) => (
                  <ListItem
                    key={automation.id}
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
                      <AutoIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box component="span" sx={{ fontWeight: 'bold', fontSize: '1rem' }}>
                            {automation.name}
                          </Box>
                          <Box component="span">
                            <Chip
                              label={automation.status.toUpperCase()}
                              color={getStatusColor(automation.status)}
                              size="small"
                            />
                          </Box>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Box component="span" sx={{ display: 'block', fontSize: '0.875rem', color: 'textSecondary', mt: 1 }}>
                            {automation.description}
                          </Box>
                          <Box sx={{ mt: 2 }}>
                            <Box component="span" sx={{ display: 'block', fontSize: '0.875rem', color: 'textSecondary', mb: 1 }}>
                              Efficiency: {automation.efficiency}%
                            </Box>
                            <LinearProgress
                              variant="determinate"
                              value={automation.efficiency}
                              sx={{ height: 6, borderRadius: 3 }}
                              color="success"
                            />
                          </Box>
                          <Box component="span" sx={{ display: 'block', fontSize: '0.75rem', color: 'textSecondary' }}>
                            Time saved: {automation.timeSaved}
                          </Box>
                        </Box>
                      }
                    />
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<PlayIcon />}
                    >
                      Manage
                    </Button>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* AI Suggestions */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <TrendingIcon sx={{ mr: 1 }} />
                AI Suggestions
              </Typography>
              
              <List>
                {suggestions.map((suggestion) => (
                  <ListItem
                    key={suggestion.id}
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
                      <TrendingIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box component="span" sx={{ fontWeight: 'bold', fontSize: '1rem' }}>
                            {suggestion.title}
                          </Box>
                          <Box component="span">
                            <Chip
                              label={suggestion.priority.toUpperCase()}
                              color={getPriorityColor(suggestion.priority)}
                              size="small"
                            />
                          </Box>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Box component="span" sx={{ display: 'block', fontSize: '0.875rem', color: 'textSecondary', mt: 1 }}>
                            {suggestion.description}
                          </Box>
                          <Typography variant="caption" color="success.main" sx={{ fontWeight: 'bold' }}>
                            Potential savings: {suggestion.potentialSavings}
                          </Typography>
                        </Box>
                      }
                    />
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<AutoIcon />}
                    >
                      Implement
                    </Button>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Automation Analytics */}
        <Grid item xs={12}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Automation Impact
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                      15
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Hours Saved/Week
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                      87%
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Average Efficiency
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                      12
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Active Automations
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                      8
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Pending Suggestions
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AIAutomation;
