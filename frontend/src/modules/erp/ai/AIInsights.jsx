import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const AIInsights = () => {
  const [insights, setInsights] = useState([]);

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    // Mock insights data
    const mockInsights = [
      {
        id: 1,
        title: 'Sales Performance Alert',
        description: 'Your Q1 sales are 15% below target. Consider implementing targeted marketing campaigns.',
        type: 'warning',
        category: 'sales',
        priority: 'high',
        actionable: true
      },
      {
        id: 2,
        title: 'Inventory Optimization',
        description: 'Product A has 30% excess inventory. Consider promotional pricing or bundling.',
        type: 'info',
        category: 'inventory',
        priority: 'medium',
        actionable: true
      },
      {
        id: 3,
        title: 'Cash Flow Positive',
        description: 'Your cash flow has improved by 25% this month. Great job on receivables management!',
        type: 'success',
        category: 'finance',
        priority: 'low',
        actionable: false
      },
      {
        id: 4,
        title: 'Customer Retention Risk',
        description: '5 high-value customers haven\'t placed orders in 60 days. Time for re-engagement.',
        type: 'warning',
        category: 'crm',
        priority: 'high',
        actionable: true
      }
    ];
    setInsights(mockInsights);
  };

  const getInsightIcon = (type) => {
    switch (type) {
      case 'success': return <CheckIcon color="success" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'info': return <InfoIcon color="info" />;
      default: return <PsychologyIcon color="primary" />;
    }
  };

  const getInsightColor = (type) => {
    switch (type) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'info': return 'info';
      default: return 'primary';
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
        AI Business Insights
      </Typography>

      <Grid container spacing={3}>
        {/* Key Insights */}
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center' }}>
                <PsychologyIcon sx={{ mr: 1 }} />
                Recent Insights
              </Typography>
              
              <List>
                {insights.map((insight) => (
                  <ListItem
                    key={insight.id}
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
                      {getInsightIcon(insight.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box component="span" sx={{ fontWeight: 'bold', fontSize: '1rem' }}>
                            {insight.title}
                          </Box>
                          <Box component="span">
                            <Chip
                              label={insight.priority.toUpperCase()}
                              color={getPriorityColor(insight.priority)}
                              size="small"
                            />
                          </Box>
                          <Box component="span">
                            <Chip
                              label={insight.category.toUpperCase()}
                              color={getInsightColor(insight.type)}
                              size="small"
                              variant="outlined"
                            />
                          </Box>
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Box component="span" sx={{ display: 'block', fontSize: '0.875rem', color: 'textSecondary', mt: 1 }}>
                            {insight.description}
                          </Box>
                          {insight.actionable && (
                            <Box component="span" sx={{ display: 'block', mt: 1 }}>
                              <Button
                                variant="outlined"
                                size="small"
                              >
                                Take Action
                              </Button>
                            </Box>
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Insight Summary */}
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Insight Summary
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  High Priority Insights
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                  2
                </Typography>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Actionable Insights
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                  3
                </Typography>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Positive Trends
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                  1
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AIInsights;
