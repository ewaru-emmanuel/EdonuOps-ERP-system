import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  TextField,
  InputAdornment,
  IconButton
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  Timeline as TimelineIcon,
  TableChart as TableChartIcon,
  ShowChart as ShowChartIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

const WidgetLibrary = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  const widgets = [
    {
      id: 1,
      name: 'Bar Chart',
      description: 'Display data in vertical or horizontal bars',
      category: 'Charts',
      icon: <BarChartIcon />,
      usage: 15
    },
    {
      id: 2,
      name: 'Pie Chart',
      description: 'Show data as proportional segments',
      category: 'Charts',
      icon: <PieChartIcon />,
      usage: 8
    },
    {
      id: 3,
      name: 'Line Chart',
      description: 'Display trends over time',
      category: 'Charts',
      icon: <TimelineIcon />,
      usage: 12
    },
    {
      id: 4,
      name: 'Data Table',
      description: 'Display data in tabular format',
      category: 'Tables',
      icon: <TableChartIcon />,
      usage: 20
    },
    {
      id: 5,
      name: 'Area Chart',
      description: 'Show data trends with filled areas',
      category: 'Charts',
      icon: <ShowChartIcon />,
      usage: 6
    },
    {
      id: 6,
      name: 'KPI Card',
      description: 'Display key performance indicators',
      category: 'Metrics',
      icon: <AssessmentIcon />,
      usage: 25
    }
  ];

  const categories = ['All', 'Charts', 'Tables', 'Metrics'];

  const filteredWidgets = widgets.filter(widget => {
    const matchesSearch = widget.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         widget.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || widget.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleAddWidget = (widget) => {
    // Mock function - would integrate with dashboard builder
    console.log('Adding widget:', widget.name);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Widget Library</Typography>
      
      {/* Search and Filter */}
      <Box display="flex" gap={2} mb={3}>
        <TextField
          placeholder="Search widgets..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1 }}
        />
        <Box display="flex" gap={1}>
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
      </Box>

      {/* Widgets Grid */}
      <Grid container spacing={3}>
        {filteredWidgets.map((widget) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={widget.id}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Box color="primary.main" mr={1}>
                    {widget.icon}
                  </Box>
                  <Typography variant="h6" component="div">
                    {widget.name}
                  </Typography>
                </Box>
                
                <Typography color="textSecondary" gutterBottom>
                  {widget.description}
                </Typography>
                
                <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
                  <Chip
                    label={widget.category}
                    size="small"
                    variant="outlined"
                  />
                  <Typography variant="body2" color="textSecondary">
                    Used {widget.usage} times
                  </Typography>
                </Box>
                
                <Button
                  variant="outlined"
                  fullWidth
                  sx={{ mt: 2 }}
                  startIcon={<AddIcon />}
                  onClick={() => handleAddWidget(widget)}
                >
                  Add to Dashboard
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredWidgets.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="textSecondary">
            No widgets found matching your criteria.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default WidgetLibrary;


