import React, { useState } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  Paper
} from '@mui/material';
import {
  Security as SecurityIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon
} from '@mui/icons-material';

// Import sub-components
import AuditLogs from './AuditLogs';
import AuditTimeline from './AuditTimeline';
import AuditReports from './AuditReports';
import AuditFilters from './AuditFilters';
import AuditExports from './AuditExports';
import AuditSettings from './AuditSettings';

const AuditModule = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const summaryData = {
    totalLogs: 15420,
    criticalEvents: 23,
    securityAlerts: 8,
    complianceScore: 98
  };

  const tabs = [
    {
      label: 'Audit Logs',
      icon: <SecurityIcon />,
      component: <AuditLogs />
    },
    {
      label: 'Timeline',
      icon: <TimelineIcon />,
      component: <AuditTimeline />
    },
    {
      label: 'Reports',
      icon: <AssessmentIcon />,
      component: <AuditReports />
    },
    {
      label: 'Filters',
      icon: <FilterIcon />,
      component: <AuditFilters />
    },
    {
      label: 'Exports',
      icon: <DownloadIcon />,
      component: <AuditExports />
    },
    {
      label: 'Settings',
      icon: <SettingsIcon />,
      component: <AuditSettings />
    }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Audit Logs</Typography>
      
      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Logs
              </Typography>
              <Typography variant="h4">
                {summaryData.totalLogs.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Critical Events
              </Typography>
              <Typography variant="h4" color="error.main">
                {summaryData.criticalEvents}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Security Alerts
              </Typography>
              <Typography variant="h4" color="warning.main">
                {summaryData.securityAlerts}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Compliance Score
              </Typography>
              <Typography variant="h4" color="success.main">
                {summaryData.complianceScore}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          {tabs.map((tab, index) => (
            <Tab
              key={index}
              label={tab.label}
              icon={tab.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box>
        {tabs[activeTab].component}
      </Box>
    </Box>
  );
};

export default AuditModule;



