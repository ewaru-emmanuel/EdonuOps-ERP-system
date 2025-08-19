import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Paper,
  Container,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  Alert,
  LinearProgress,
  useTheme
} from '@mui/material';
import {
  Api as APIIcon,
  Code as DeveloperIcon,
  Store as MarketplaceIcon,
  Webhook as WebhookIcon,
  Description as DocumentationIcon,
  Cloud as SandboxIcon,
  TrendingUp as AnalyticsIcon,
  CheckCircle as CheckCircleIcon,
  Speed as PerformanceIcon
} from '@mui/icons-material';

const APIModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const theme = useTheme();

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Mock data for API metrics
  const apiMetrics = [
    {
      title: "API Calls",
      value: "2.4M",
      trend: "+15%",
      color: "primary",
      icon: <APIIcon />
    },
    {
      title: "Active Developers",
      value: "1,847",
      trend: "+89",
      color: "info",
      icon: <DeveloperIcon />
    },
    {
      title: "Marketplace Apps",
      value: "156",
      trend: "+12",
      color: "success",
      icon: <MarketplaceIcon />
    },
    {
      title: "API Uptime",
      value: "99.9%",
      trend: "+0.1%",
      color: "success",
      icon: <CheckCircleIcon />
    }
  ];

  const tabs = [
    {
      label: 'API Management',
      icon: <APIIcon />,
      description: 'API keys, endpoints, versioning, and rate limiting'
    },
    {
      label: 'Developer Portal',
      icon: <DeveloperIcon />,
      description: 'Developer accounts, documentation, and SDKs'
    },
    {
      label: 'Marketplace',
      icon: <MarketplaceIcon />,
      description: 'Third-party apps, integrations, and partner ecosystem'
    },
    {
      label: 'Webhooks',
      icon: <WebhookIcon />,
      description: 'Webhook management, delivery tracking, and event handling'
    },
    {
      label: 'Documentation',
      icon: <DocumentationIcon />,
      description: 'API documentation, guides, and interactive examples'
    },
    {
      label: 'Sandbox',
      icon: <SandboxIcon />,
      description: 'Developer sandbox environments and testing tools'
    },
    {
      label: 'Analytics',
      icon: <AnalyticsIcon />,
      description: 'API usage analytics, performance monitoring, and insights'
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* API Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
            <APIIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
              API Ecosystem & Developer Platform
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Comprehensive APIs, Developer Tools & Marketplace Ecosystem
            </Typography>
          </Box>
        </Box>
        
        {/* Status Banner */}
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            🔌 API Ecosystem Active
          </Typography>
          <Typography variant="body2">
            Complete developer platform with 100+ API endpoints, marketplace, webhooks, and comprehensive documentation.
          </Typography>
        </Alert>
      </Box>

      {/* API Metrics */}
      <Paper elevation={3} sx={{ borderRadius: 2, p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          <PerformanceIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          API Performance Metrics
        </Typography>
        
        <Grid container spacing={3}>
          {apiMetrics.map((metric, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card elevation={2}>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Avatar sx={{ bgcolor: `${metric.color}.main` }}>
                      {metric.icon}
                    </Avatar>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {metric.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {metric.title}
                      </Typography>
                    </Box>
                  </Box>
                  <Chip 
                    label={metric.trend} 
                    color={metric.color} 
                    size="small" 
                    icon={<PerformanceIcon />}
                  />
                  <LinearProgress 
                    variant="determinate" 
                    value={parseInt(metric.value)} 
                    sx={{ mt: 1 }} 
                    color={metric.color}
                  />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Main API Interface */}
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
          {/* Module Description */}
          <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>
              {tabs[activeTab].label}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {tabs[activeTab].description}
            </Typography>
          </Box>
          
          {/* Module Content */}
          <Alert severity="info">
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              🔌 {tabs[activeTab].label} - Coming Soon
            </Typography>
            <Typography variant="body2">
              {tabs[activeTab].description} with enterprise-grade API ecosystem features.
            </Typography>
          </Alert>
        </Box>
      </Paper>

      {/* API Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          API Ecosystem - Developer Platform, Marketplace & Integration Hub
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="REST APIs" size="small" sx={{ mr: 1 }} />
          <Chip label="GraphQL" size="small" sx={{ mr: 1 }} />
          <Chip label="Webhooks" size="small" sx={{ mr: 1 }} />
          <Chip label="Enterprise Grade" size="small" color="primary" />
        </Box>
      </Box>
    </Container>
  );
};

export default APIModule;
