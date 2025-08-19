import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Assessment as AssessmentIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';

const AuditReports = () => {

  const reports = [
    {
      id: 1,
      name: 'Security Audit Report',
      description: 'Comprehensive security analysis and compliance check',
      type: 'Security',
      lastGenerated: '2024-01-15',
      status: 'Available',
      icon: <SecurityIcon />
    },
    {
      id: 2,
      name: 'User Activity Report',
      description: 'Detailed user activity and access patterns',
      type: 'Activity',
      lastGenerated: '2024-01-14',
      status: 'Available',
      icon: <VisibilityIcon />
    },
    {
      id: 3,
      name: 'Compliance Report',
      description: 'Regulatory compliance and audit trail summary',
      type: 'Compliance',
      lastGenerated: '2024-01-13',
      status: 'Pending',
      icon: <AssessmentIcon />
    },
    {
      id: 4,
      name: 'Risk Assessment Report',
      description: 'Security risk analysis and recommendations',
      type: 'Risk',
      lastGenerated: '2024-01-12',
      status: 'Available',
      icon: <WarningIcon />
    }
  ];

  const securityMetrics = {
    totalLogins: 1247,
    failedLogins: 23,
    suspiciousActivities: 8,
    complianceScore: 98,
    riskLevel: 'Low'
  };

  const topUsers = [
    { name: 'John Doe', activities: 156, lastActivity: '2 hours ago' },
    { name: 'Jane Smith', activities: 142, lastActivity: '4 hours ago' },
    { name: 'Mike Johnson', activities: 98, lastActivity: '6 hours ago' },
    { name: 'Sarah Wilson', activities: 87, lastActivity: '8 hours ago' }
  ];

  const handleGenerateReport = (report) => {
    // Mock report generation
    console.log('Generating report:', report.name);
  };

  const handleDownloadReport = (report) => {
    // Mock download functionality
    console.log('Downloading report:', report.name);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Audit Reports</Typography>
      
      <Grid container spacing={3}>
        {/* Security Metrics */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Security Overview</Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Typography color="textSecondary" gutterBottom>
                    Total Logins
                  </Typography>
                  <Typography variant="h4">
                    {securityMetrics.totalLogins.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography color="textSecondary" gutterBottom>
                    Failed Logins
                  </Typography>
                  <Typography variant="h4" color="error.main">
                    {securityMetrics.failedLogins}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography color="textSecondary" gutterBottom>
                    Suspicious Activities
                  </Typography>
                  <Typography variant="h4" color="warning.main">
                    {securityMetrics.suspiciousActivities}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Typography color="textSecondary" gutterBottom>
                    Compliance Score
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {securityMetrics.complianceScore}%
                  </Typography>
                </Grid>
              </Grid>
              
              <Box mt={2}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Risk Level: <Chip label={securityMetrics.riskLevel} color="success" size="small" />
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={securityMetrics.complianceScore}
                  color="success"
                  sx={{ mt: 1 }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Users */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Most Active Users</Typography>
              
              <List>
                {topUsers.map((user, index) => (
                  <ListItem key={index} disablePadding sx={{ mb: 1 }}>
                    <ListItemIcon>
                      <TrendingUpIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={user.name}
                      secondary={`${user.activities} activities • ${user.lastActivity}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Available Reports */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Available Reports</Typography>
              
              <Grid container spacing={2}>
                {reports.map((report) => (
                  <Grid item xs={12} sm={6} md={3} key={report.id}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box display="flex" alignItems="center" mb={2}>
                          <Box color="primary.main" mr={1}>
                            {report.icon}
                          </Box>
                          <Typography variant="h6" component="div">
                            {report.name}
                          </Typography>
                        </Box>
                        
                        <Typography color="textSecondary" gutterBottom>
                          {report.description}
                        </Typography>
                        
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                          <Chip
                            label={report.type}
                            size="small"
                            variant="outlined"
                          />
                          <Chip
                            label={report.status}
                            color={report.status === 'Available' ? 'success' : 'warning'}
                            size="small"
                          />
                        </Box>
                        
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          Last generated: {report.lastGenerated}
                        </Typography>
                        
                        <Box display="flex" gap={1}>
                          <Button
                            variant="outlined"
                            size="small"
                            onClick={() => handleGenerateReport(report)}
                            disabled={report.status === 'Pending'}
                          >
                            Generate
                          </Button>
                          <Button
                            variant="outlined"
                            size="small"
                            startIcon={<DownloadIcon />}
                            onClick={() => handleDownloadReport(report)}
                            disabled={report.status === 'Pending'}
                          >
                            Download
                          </Button>
                        </Box>
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

export default AuditReports;



