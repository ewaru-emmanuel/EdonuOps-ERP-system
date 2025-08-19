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
  SmartToy as AIIcon,
  Chat as ChatIcon,
  AutoAwesome as AutoIcon,
  Psychology as PsychologyIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

// Import AI sub-components
import AIChat from './AIChat';
import AIAutomation from './AIAutomation';
import AIInsights from './AIInsights';
import AIAnalytics from './AIAnalytics';
import AISettings from './AISettings';

const AIModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [aiData, setAiData] = useState({
    totalInteractions: 0,
    automationCount: 0,
    insightsGenerated: 0,
    accuracy: 0
  });
  const theme = useTheme();

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  useEffect(() => {
    // Fetch AI summary data
    fetchAISummary();
  }, []);

  const fetchAISummary = async () => {
    try {
      // TODO: Replace with actual API call
      const mockData = {
        totalInteractions: 1250,
        automationCount: 45,
        insightsGenerated: 89,
        accuracy: 94.2
      };
      setAiData(mockData);
    } catch (error) {
      console.error('Error fetching AI summary:', error);
    }
  };

  const tabs = [
    {
      label: 'AI Chat',
      icon: <ChatIcon />,
      component: <AIChat />
    },
    {
      label: 'Automation',
      icon: <AutoIcon />,
      component: <AIAutomation />
    },
    {
      label: 'Insights',
      icon: <PsychologyIcon />,
      component: <AIInsights />
    },
    {
      label: 'Analytics',
      icon: <AnalyticsIcon />,
      component: <AIAnalytics />
    },
    {
      label: 'Settings',
      icon: <SettingsIcon />,
      component: <AISettings />
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          AI Co-Pilot System
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 3 }}>
          Intelligent automation, insights, and AI-powered assistance for your business
        </Typography>
      </Box>

      {/* AI Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Interactions
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                {aiData.totalInteractions.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                AI conversations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Automations
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {aiData.automationCount}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                AI-powered workflows
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Insights Generated
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                {aiData.insightsGenerated}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Smart recommendations
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                AI Accuracy
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {aiData.accuracy}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Response accuracy
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

export default AIModule;
