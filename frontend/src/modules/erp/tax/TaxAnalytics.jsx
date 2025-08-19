import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  TrendingUp as TrendingIcon,
  Assessment as AnalyticsIcon,
  ShowChart as ChartIcon
} from '@mui/icons-material';

const TaxAnalytics = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('12months');
  const [analyticsData, setAnalyticsData] = useState({
    totalTaxLiability: 1250000,
    taxEfficiency: 87.5,
    complianceRate: 95.2,
    averageProcessingTime: 3.2
  });

  const [taxTrends, setTaxTrends] = useState([]);

  useEffect(() => {
    fetchAnalyticsData();
  }, [selectedPeriod]);

  const fetchAnalyticsData = async () => {
    // Mock analytics data
    const mockTrends = [
      { month: 'Jan', sales: 85000, corporate: 120000, vat: 45000 },
      { month: 'Feb', sales: 92000, corporate: 125000, vat: 48000 },
      { month: 'Mar', sales: 88000, corporate: 118000, vat: 46000 },
      { month: 'Apr', sales: 95000, corporate: 130000, vat: 52000 },
      { month: 'May', sales: 102000, corporate: 135000, vat: 55000 },
      { month: 'Jun', sales: 98000, corporate: 128000, vat: 51000 },
      { month: 'Jul', sales: 105000, corporate: 140000, vat: 58000 },
      { month: 'Aug', sales: 112000, corporate: 145000, vat: 62000 },
      { month: 'Sep', sales: 108000, corporate: 142000, vat: 60000 },
      { month: 'Oct', sales: 115000, corporate: 150000, vat: 65000 },
      { month: 'Nov', sales: 122000, corporate: 155000, vat: 68000 },
      { month: 'Dec', sales: 118000, corporate: 152000, vat: 66000 }
    ];
    setTaxTrends(mockTrends);
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Tax Analytics & Insights
      </Typography>

      {/* Filters */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Analysis Period</InputLabel>
            <Select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              label="Analysis Period"
            >
              <MenuItem value="6months">Last 6 Months</MenuItem>
              <MenuItem value="12months">Last 12 Months</MenuItem>
              <MenuItem value="24months">Last 24 Months</MenuItem>
              <MenuItem value="custom">Custom Period</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <AnalyticsIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography color="textSecondary" gutterBottom>
                  Total Tax Liability
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                ${(analyticsData.totalTaxLiability / 1000000).toFixed(1)}M
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Current fiscal year
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingIcon sx={{ color: 'success.main', mr: 1 }} />
                <Typography color="textSecondary" gutterBottom>
                  Tax Efficiency
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {analyticsData.taxEfficiency}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Optimization score
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ChartIcon sx={{ color: 'info.main', mr: 1 }} />
                <Typography color="textSecondary" gutterBottom>
                  Compliance Rate
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                {analyticsData.complianceRate}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Filing accuracy
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <TrendingIcon sx={{ color: 'warning.main', mr: 1 }} />
                <Typography color="textSecondary" gutterBottom>
                  Processing Time
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                {analyticsData.averageProcessingTime} days
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Average filing time
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tax Trends Chart */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Tax Liability Trends
              </Typography>
              <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="textSecondary">
                  Chart visualization would be implemented here
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Tax Breakdown
              </Typography>
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Sales Tax
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                  ${taxTrends.reduce((sum, t) => sum + t.sales, 0).toLocaleString()}
                </Typography>
              </Box>
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Corporate Tax
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'secondary.main' }}>
                  ${taxTrends.reduce((sum, t) => sum + t.corporate, 0).toLocaleString()}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  VAT
                </Typography>
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                  ${taxTrends.reduce((sum, t) => sum + t.vat, 0).toLocaleString()}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TaxAnalytics;




