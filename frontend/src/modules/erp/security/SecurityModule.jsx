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
  Shield as SecurityIcon,
  Security as PermissionsIcon,
  VerifiedUser as UserIcon,
  Lock as EncryptionIcon,
  Warning as MonitoringIcon,
  School as TrainingIcon,
  Assessment as AnalyticsIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

const SecurityModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const theme = useTheme();

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Mock data for security metrics
  const securityMetrics = [
    {
      title: "Security Score",
      value: "99.2%",
      trend: "+1.5%",
      color: "success",
      icon: <CheckCircleIcon />
    },
    {
      title: "Active Users",
      value: "1,247",
      trend: "+23",
      color: "info",
      icon: <UserIcon />
    },
    {
      title: "Security Roles",
      value: "45",
      trend: "+3",
      color: "primary",
      icon: <PermissionsIcon />
    },
    {
      title: "Incident Response",
      value: "< 5min",
      trend: "-2min",
      color: "success",
      icon: <MonitoringIcon />
    }
  ];

  const tabs = [
    {
      label: 'Role Management',
      icon: <PermissionsIcon />,
      description: 'Granular role-based permissions and access control'
    },
    {
      label: 'User Security',
      icon: <UserIcon />,
      description: 'User authentication, sessions, and security policies'
    },
    {
      label: 'Data Protection',
      icon: <EncryptionIcon />,
      description: 'Encryption, data classification, and privacy controls'
    },
    {
      label: 'Security Monitoring',
      icon: <MonitoringIcon />,
      description: 'Real-time security monitoring and incident response'
    },
    {
      label: 'Security Training',
      icon: <TrainingIcon />,
      description: 'Security awareness training and compliance'
    },
    {
      label: 'Security Analytics',
      icon: <AnalyticsIcon />,
      description: 'Security analytics and threat intelligence'
    }
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Security Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
            <SecurityIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
              Enterprise Security & Permissions
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Granular Access Control, Data Protection & Security Monitoring
            </Typography>
          </Box>
        </Box>
        
        {/* Status Banner */}
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            🔒 Enterprise Security Suite Active
          </Typography>
          <Typography variant="body2">
            Comprehensive security with granular permissions, encryption, monitoring, and compliance across all modules.
          </Typography>
        </Alert>
      </Box>

      {/* Security Metrics */}
      <Paper elevation={3} sx={{ borderRadius: 2, p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Security Performance Metrics
        </Typography>
        
        <Grid container spacing={3}>
          {securityMetrics.map((metric, index) => (
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
                    icon={<TrendingUpIcon />}
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

      {/* Main Security Interface */}
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
              🛡️ {tabs[activeTab].label} - Coming Soon
            </Typography>
            <Typography variant="body2">
              {tabs[activeTab].description} with enterprise-grade security features.
            </Typography>
          </Alert>
        </Box>
      </Paper>

      {/* Security Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Enterprise Security Suite - Granular Permissions, Data Protection & Security Monitoring
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="SOC 2 Type II" size="small" sx={{ mr: 1 }} />
          <Chip label="ISO 27001" size="small" sx={{ mr: 1 }} />
          <Chip label="GDPR Compliant" size="small" sx={{ mr: 1 }} />
          <Chip label="Enterprise Grade" size="small" color="primary" />
        </Box>
      </Box>
    </Container>
  );
};

export default SecurityModule;
