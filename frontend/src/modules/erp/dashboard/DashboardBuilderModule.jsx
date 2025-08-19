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
  Dashboard as DashboardIcon,
  Widgets as WidgetsIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon
} from '@mui/icons-material';

// Import sub-components
import DashboardBuilder from './DashboardBuilder';
import WidgetLibrary from './WidgetLibrary';
import DashboardTemplates from './DashboardTemplates';
import DashboardAnalytics from './DashboardAnalytics';
import DashboardHistory from './DashboardHistory';
import DashboardSettings from './DashboardSettings';

const DashboardBuilderModule = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const summaryData = {
    totalDashboards: 12,
    activeDashboards: 8,
    totalWidgets: 45,
    templatesAvailable: 15
  };

  const tabs = [
    {
      label: 'Dashboard Builder',
      icon: <DashboardIcon />,
      component: <DashboardBuilder />
    },
    {
      label: 'Widget Library',
      icon: <WidgetsIcon />,
      component: <WidgetLibrary />
    },
    {
      label: 'Templates',
      icon: <TimelineIcon />,
      component: <DashboardTemplates />
    },
    {
      label: 'Analytics',
      icon: <AssessmentIcon />,
      component: <DashboardAnalytics />
    },
    {
      label: 'History',
      icon: <HistoryIcon />,
      component: <DashboardHistory />
    },
    {
      label: 'Settings',
      icon: <SettingsIcon />,
      component: <DashboardSettings />
    }
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>Dashboard Builder</Typography>
      
      {/* Summary Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Dashboards
              </Typography>
              <Typography variant="h4">
                {summaryData.totalDashboards}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Dashboards
              </Typography>
              <Typography variant="h4">
                {summaryData.activeDashboards}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Widgets
              </Typography>
              <Typography variant="h4">
                {summaryData.totalWidgets}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Templates Available
              </Typography>
              <Typography variant="h4">
                {summaryData.templatesAvailable}
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

export default DashboardBuilderModule;


