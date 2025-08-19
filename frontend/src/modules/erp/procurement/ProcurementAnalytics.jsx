import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Divider
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  BarChart,
  PieChart,
  Timeline,
  Download,
  FilterList
} from '@mui/icons-material';

const ProcurementAnalytics = () => {
  const showSnackbar = (message, severity = 'success') => {
    // For now, just log to console. In a real app, this would show a snackbar
    console.log(`${severity.toUpperCase()}: ${message}`);
  };
  
  const monthlyData = [
    { month: 'Jan', value: 45000, change: 12.5 },
    { month: 'Feb', value: 52000, change: 15.6 },
    { month: 'Mar', value: 48000, change: -7.7 },
    { month: 'Apr', value: 61000, change: 27.1 },
    { month: 'May', value: 55000, change: -9.8 },
    { month: 'Jun', value: 67000, change: 21.8 }
  ];

  const vendorPerformance = [
    {
      vendor: 'Tech Supplies Co.',
      total_spent: 125000,
      orders: 45,
      avg_delivery: 2.3,
      satisfaction: 4.2
    },
    {
      vendor: 'Office Solutions',
      total_spent: 89000,
      orders: 32,
      avg_delivery: 1.8,
      satisfaction: 4.5
    },
    {
      vendor: 'Industrial Parts Ltd.',
      total_spent: 67000,
      orders: 18,
      avg_delivery: 3.1,
      satisfaction: 3.8
    },
    {
      vendor: 'Global Electronics',
      total_spent: 156000,
      orders: 28,
      avg_delivery: 2.7,
      satisfaction: 4.1
    }
  ];

  const categorySpending = [
    { category: 'Electronics', amount: 85000, percentage: 35 },
    { category: 'Office Supplies', amount: 65000, percentage: 27 },
    { category: 'Industrial Parts', amount: 45000, percentage: 19 },
    { category: 'Software', amount: 25000, percentage: 10 },
    { category: 'Services', amount: 15000, percentage: 6 },
    { category: 'Other', amount: 5000, percentage: 3 }
  ];

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>
          Procurement Analytics
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<FilterList />}
            onClick={() => showSnackbar('Filter options would open here')}
            sx={{ textTransform: 'none' }}
          >
            Filter
          </Button>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={() => showSnackbar('Export report would start download')}
            sx={{ textTransform: 'none' }}
          >
            Export Report
          </Button>
        </Box>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TrendingUp color="success" />
                <Typography variant="body2" color="text.secondary">
                  Total Spend (YTD)
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                $328,000
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp fontSize="small" color="success" />
                <Typography variant="body2" color="success.main">
                  +15.2% vs last year
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <BarChart color="primary" />
                <Typography variant="body2" color="text.secondary">
                  Average PO Value
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                $12,450
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp fontSize="small" color="success" />
                <Typography variant="body2" color="success.main">
                  +8.7% vs last year
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <Timeline color="warning" />
                <Typography variant="body2" color="text.secondary">
                  Processing Time
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                2.3 days
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingDown fontSize="small" color="success" />
                <Typography variant="body2" color="success.main">
                  -12.5% vs last year
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <PieChart color="info" />
                <Typography variant="body2" color="text.secondary">
                  Cost Savings
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 1 }}>
                12.5%
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp fontSize="small" color="success" />
                <Typography variant="body2" color="success.main">
                  +3.2% vs last year
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Monthly Trend Chart */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} lg={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
                Monthly Procurement Spend Trend
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                {monthlyData.map((data, index) => (
                  <Box key={data.month} sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {data.month}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          ${data.value.toLocaleString()}
                        </Typography>
                        <Chip
                          label={`${data.change > 0 ? '+' : ''}${data.change}%`}
                          size="small"
                          color={data.change > 0 ? 'success' : 'error'}
                          sx={{ fontSize: '0.75rem' }}
                        />
                      </Box>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={(data.value / 67000) * 100}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Category Spending */}
        <Grid item xs={12} lg={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
                Spending by Category
              </Typography>
              
              {categorySpending.map((category, index) => (
                <Box key={category.category} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      {category.category}
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      ${category.amount.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <LinearProgress
                      variant="determinate"
                      value={category.percentage}
                      sx={{ flexGrow: 1, height: 6, borderRadius: 3 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {category.percentage}%
                    </Typography>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Vendor Performance */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" component="h4" sx={{ fontWeight: 'bold', mb: 3 }}>
            Vendor Performance Analysis
          </Typography>
          
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell sx={{ fontWeight: 'bold' }}>Vendor</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Total Spent</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Orders</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Avg Delivery (days)</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Satisfaction</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Performance</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {vendorPerformance.map((vendor, index) => (
                  <TableRow key={vendor.vendor} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        {vendor.vendor}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                        ${vendor.total_spent.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {vendor.orders}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {vendor.avg_delivery}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {vendor.satisfaction}/5
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={(vendor.satisfaction / 5) * 100}
                          sx={{ width: 60, height: 6, borderRadius: 3 }}
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={vendor.satisfaction >= 4 ? 'Excellent' : vendor.satisfaction >= 3.5 ? 'Good' : 'Fair'}
                        size="small"
                        color={vendor.satisfaction >= 4 ? 'success' : vendor.satisfaction >= 3.5 ? 'warning' : 'error'}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ProcurementAnalytics;
