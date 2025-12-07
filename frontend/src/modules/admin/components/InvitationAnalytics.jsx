import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  InputAdornment,
  Divider,
  LinearProgress
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Email as EmailIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Cancel as CancelIcon,
  Analytics as AnalyticsIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon
} from '@mui/icons-material';
// import {
//   LineChart,
//   Line,
//   AreaChart,
//   Area,
//   XAxis,
//   YAxis,
//   CartesianGrid,
//   Tooltip,
//   ResponsiveContainer,
//   PieChart,
//   Pie,
//   Cell,
//   BarChart,
//   Bar
// } from 'recharts';
import { format, subDays, startOfDay, endOfDay } from 'date-fns';
import { apiClient } from '../../../utils/apiClient';

const InvitationAnalytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState('30');
  const [roleFilter, setRoleFilter] = useState('all');

  // Load analytics data
  useEffect(() => {
    loadAnalytics();
  }, [dateRange, roleFilter]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      // This would be a new endpoint for analytics
      const response = await apiClient.get('/api/invites/analytics', {
        params: { days: dateRange, role: roleFilter }
      });
      setAnalytics(response.data);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Error loading analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for demonstration (replace with real API call)
  const mockAnalytics = {
    overview: {
      totalInvites: 156,
      acceptedInvites: 89,
      pendingInvites: 45,
      expiredInvites: 22,
      acceptanceRate: 57.1,
      avgTimeToAccept: 2.3
    },
    trends: [
      { date: '2024-01-01', sent: 12, accepted: 8, pending: 4 },
      { date: '2024-01-02', sent: 15, accepted: 9, pending: 6 },
      { date: '2024-01-03', sent: 8, accepted: 6, pending: 2 },
      { date: '2024-01-04', sent: 20, accepted: 12, pending: 8 },
      { date: '2024-01-05', sent: 18, accepted: 11, pending: 7 },
      { date: '2024-01-06', sent: 14, accepted: 8, pending: 6 },
      { date: '2024-01-07', sent: 16, accepted: 10, pending: 6 }
    ],
    roleBreakdown: [
      { role: 'User', sent: 89, accepted: 52, rate: 58.4 },
      { role: 'Manager', sent: 34, accepted: 21, rate: 61.8 },
      { role: 'Admin', sent: 23, accepted: 12, rate: 52.2 },
      { role: 'Super Admin', sent: 10, accepted: 4, rate: 40.0 }
    ],
    topInviters: [
      { name: 'John Admin', invites: 45, accepted: 28, rate: 62.2 },
      { name: 'Jane Manager', invites: 32, accepted: 19, rate: 59.4 },
      { name: 'Mike Admin', invites: 28, accepted: 16, rate: 57.1 },
      { name: 'Sarah Manager', invites: 25, accepted: 14, rate: 56.0 }
    ],
    recentActivity: [
      { email: 'user1@company.com', role: 'User', status: 'Accepted', time: '2 hours ago' },
      { email: 'user2@company.com', role: 'Manager', status: 'Pending', time: '4 hours ago' },
      { email: 'user3@company.com', role: 'User', status: 'Expired', time: '1 day ago' },
      { email: 'user4@company.com', role: 'Admin', status: 'Accepted', time: '2 days ago' }
    ]
  };

  const data = analytics || mockAnalytics;

  // Colors for charts
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Accepted': return 'success';
      case 'Pending': return 'warning';
      case 'Expired': return 'error';
      default: return 'default';
    }
  };

  const getTrendIcon = (value, previousValue) => {
    if (value > previousValue) return <TrendingUpIcon color="success" />;
    if (value < previousValue) return <TrendingDownIcon color="error" />;
    return null;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Invitation Analytics
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Track invitation performance and user engagement
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Date Range</InputLabel>
            <Select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              label="Date Range"
            >
              <MenuItem value="7">Last 7 days</MenuItem>
              <MenuItem value="30">Last 30 days</MenuItem>
              <MenuItem value="90">Last 90 days</MenuItem>
              <MenuItem value="365">Last year</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Role</InputLabel>
            <Select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              label="Role"
            >
              <MenuItem value="all">All Roles</MenuItem>
              <MenuItem value="user">User</MenuItem>
              <MenuItem value="manager">Manager</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
              <MenuItem value="superadmin">Super Admin</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadAnalytics}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            disabled={loading}
          >
            Export
          </Button>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 3 }} />}

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6">{data.overview.totalInvites}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Invitations
                  </Typography>
                </Box>
                <EmailIcon color="primary" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6">{data.overview.acceptedInvites}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Accepted
                  </Typography>
                </Box>
                <CheckCircleIcon color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6">{data.overview.acceptanceRate}%</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Acceptance Rate
                  </Typography>
                </Box>
                <TrendingUpIcon color="success" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6">{data.overview.avgTimeToAccept} days</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Avg. Time to Accept
                  </Typography>
                </Box>
                <ScheduleIcon color="info" />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Invitation Trends */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Invitation Trends
              </Typography>
              <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="body1" color="text.secondary">
                  Chart visualization requires recharts dependency
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Role Breakdown */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Acceptance by Role
              </Typography>
              <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.50', borderRadius: 1 }}>
                <Typography variant="body1" color="text.secondary">
                  Chart visualization requires recharts dependency
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Analytics Row */}
      <Grid container spacing={3}>
        {/* Top Inviters */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Inviters
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell align="right">Invites</TableCell>
                      <TableCell align="right">Accepted</TableCell>
                      <TableCell align="right">Rate</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.topInviters.map((inviter, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2">{inviter.name}</Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">{inviter.invites}</Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">{inviter.accepted}</Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Chip 
                            label={`${inviter.rate}%`} 
                            color={inviter.rate > 60 ? 'success' : inviter.rate > 50 ? 'warning' : 'error'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Email</TableCell>
                      <TableCell>Role</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Time</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {data.recentActivity.map((activity, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" noWrap sx={{ maxWidth: 150 }}>
                            {activity.email}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip label={activity.role} size="small" />
                        </TableCell>
                        <TableCell>
                          <Chip 
                            label={activity.status} 
                            color={getStatusColor(activity.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {activity.time}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mt: 3 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default InvitationAnalytics;

