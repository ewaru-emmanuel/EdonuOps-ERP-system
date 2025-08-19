import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  CardMedia,
  CardActions
} from '@mui/material';
import {
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  AccountBalance as AccountBalanceIcon,
  People as PeopleIcon,
  Inventory as InventoryIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

const DashboardTemplates = () => {
  const [selectedCategory, setSelectedCategory] = useState('All');

  const templates = [
    {
      id: 1,
      name: 'Executive Dashboard',
      description: 'High-level overview for executives and managers',
      category: 'Executive',
      widgets: 8,
      icon: <BusinessIcon />,
      color: '#1976d2'
    },
    {
      id: 2,
      name: 'Sales Analytics',
      description: 'Comprehensive sales performance tracking',
      category: 'Sales',
      widgets: 12,
      icon: <TrendingUpIcon />,
      color: '#2e7d32'
    },
    {
      id: 3,
      name: 'Financial Overview',
      description: 'Financial metrics and reporting dashboard',
      category: 'Finance',
      widgets: 10,
      icon: <AccountBalanceIcon />,
      color: '#ed6c02'
    },
    {
      id: 4,
      name: 'HR Dashboard',
      description: 'Human resources and employee management',
      category: 'HR',
      widgets: 6,
      icon: <PeopleIcon />,
      color: '#9c27b0'
    },
    {
      id: 5,
      name: 'Inventory Management',
      description: 'Stock levels and inventory tracking',
      category: 'Operations',
      widgets: 9,
      icon: <InventoryIcon />,
      color: '#d32f2f'
    },
    {
      id: 6,
      name: 'Performance Metrics',
      description: 'Key performance indicators and analytics',
      category: 'Analytics',
      widgets: 15,
      icon: <AssessmentIcon />,
      color: '#7b1fa2'
    }
  ];

  const categories = ['All', 'Executive', 'Sales', 'Finance', 'HR', 'Operations', 'Analytics'];

  const filteredTemplates = templates.filter(template => 
    selectedCategory === 'All' || template.category === selectedCategory
  );

  const handleUseTemplate = (template) => {
    // Mock function - would create a new dashboard from template
    console.log('Using template:', template.name);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Dashboard Templates</Typography>
      
      {/* Category Filter */}
      <Box display="flex" gap={1} mb={3} flexWrap="wrap">
        {categories.map((category) => (
          <Chip
            key={category}
            label={category}
            onClick={() => setSelectedCategory(category)}
            color={selectedCategory === category ? 'primary' : 'default'}
            variant={selectedCategory === category ? 'filled' : 'outlined'}
          />
        ))}
      </Box>

      {/* Templates Grid */}
      <Grid container spacing={3}>
        {filteredTemplates.map((template) => (
          <Grid item xs={12} sm={6} md={4} key={template.id}>
            <Card>
              <CardMedia
                component="div"
                sx={{
                  height: 120,
                  backgroundColor: template.color,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white'
                }}
              >
                <Box fontSize={48}>
                  {template.icon}
                </Box>
              </CardMedia>
              
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {template.name}
                </Typography>
                
                <Typography color="textSecondary" gutterBottom>
                  {template.description}
                </Typography>
                
                <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                  <Chip
                    label={template.category}
                    size="small"
                    variant="outlined"
                  />
                  <Typography variant="body2" color="textSecondary">
                    {template.widgets} widgets
                  </Typography>
                </Box>
              </CardContent>
              
              <CardActions>
                <Button
                  variant="contained"
                  fullWidth
                  onClick={() => handleUseTemplate(template)}
                >
                  Use Template
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredTemplates.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="textSecondary">
            No templates found in this category.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default DashboardTemplates;


