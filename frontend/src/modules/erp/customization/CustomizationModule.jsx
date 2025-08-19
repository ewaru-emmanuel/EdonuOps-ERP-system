import React, { useState, useEffect } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Paper,
  Container,
  useTheme,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Alert
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Palette as ThemeIcon,
  Dashboard as DashboardIcon,
  Code as CodeIcon,
  Extension as ExtensionIcon,
  Storage as StorageIcon
} from '@mui/icons-material';

// Import customization sub-components
import ThemeCustomization from './ThemeCustomization';
import DashboardCustomization from './DashboardCustomization';
import CodeCustomization from './CodeCustomization';
import ExtensionManagement from './ExtensionManagement';
import DataCustomization from './DataCustomization';

const CustomizationModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [customizationData, setCustomizationData] = useState({
    activeThemes: 0,
    customDashboards: 0,
    extensions: 0,
    customFields: 0
  });
  const theme = useTheme();

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  useEffect(() => {
    // Fetch customization summary data
    fetchCustomizationSummary();
  }, []);

  const fetchCustomizationSummary = async () => {
    try {
      // TODO: Replace with actual API call
      const mockData = {
        activeThemes: 3,
        customDashboards: 8,
        extensions: 12,
        customFields: 25
      };
      setCustomizationData(mockData);
    } catch (error) {
      console.error('Error fetching customization summary:', error);
    }
  };

  const tabs = [
    {
      label: 'Theme Customization',
      icon: <ThemeIcon />,
      component: <ThemeCustomization />
    },
    {
      label: 'Dashboard Builder',
      icon: <DashboardIcon />,
      component: <DashboardCustomization />
    },
    {
      label: 'Code Customization',
      icon: <CodeIcon />,
      component: <CodeCustomization />
    },
    {
      label: 'Extensions',
      icon: <ExtensionIcon />,
      component: <ExtensionManagement />
    },
    {
      label: 'Data Customization',
      icon: <StorageIcon />,
      component: <DataCustomization />
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          System Customization
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
          Customize themes, dashboards, and system behavior to match your business needs
        </Typography>
      </Box>

      {/* Customization Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Themes
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                {customizationData.activeThemes}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Custom themes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Custom Dashboards
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {customizationData.customDashboards}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                User dashboards
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Extensions
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                {customizationData.extensions}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Installed extensions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Custom Fields
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                {customizationData.customFields}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Custom data fields
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper elevation={3} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                minHeight: 64,
                fontSize: '0.875rem',
                fontWeight: 500,
                textTransform: 'none',
                '&.Mui-selected': {
                  color: theme.palette.primary.main,
                  fontWeight: 600
                }
              }
            }}
          >
            {tabs.map((tab, index) => (
              <Tab
                key={index}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {tab.icon}
                    {tab.label}
                  </Box>
                }
                sx={{ minWidth: 'auto', px: 3 }}
              />
            ))}
          </Tabs>
        </Box>

        <Box sx={{ p: 3, minHeight: '60vh' }}>
          {tabs[activeTab].component}
        </Box>
      </Paper>
    </Container>
  );
};

export default CustomizationModule;
