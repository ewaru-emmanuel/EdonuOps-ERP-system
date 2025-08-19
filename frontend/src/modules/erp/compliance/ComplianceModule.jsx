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
  CardActions,
  Button,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Badge,
  useTheme
} from '@mui/material';
import {
  Gavel as ComplianceIcon,
  Business as EntityIcon,
  Assessment as ReportingIcon,
  Calculate as TaxIcon,
  Security as AuditIcon,
  Timeline as ConsolidationIcon,
  Settings as SettingsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  LocationOn as LocationIcon,
  Speed as PerformanceIcon,
  Verified as VerifiedIcon,
  Flag as FlagIcon,
  Assignment as AssignmentIcon
} from '@mui/icons-material';

// Import sub-components
import RegulatoryFrameworks from './RegulatoryFrameworks';
import LegalEntities from './LegalEntities';
import FinancialStatements from './FinancialStatements';
import Consolidation from './Consolidation';
import StatutoryReporting from './StatutoryReporting';
import ComplianceChecks from './ComplianceChecks';
import ComplianceAnalytics from './ComplianceAnalytics';

const ComplianceModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const theme = useTheme();
  
  const showSnackbar = (message, severity = 'success') => {
    // For now, just log to console. In a real app, this would show a snackbar
    console.log(`${severity.toUpperCase()}: ${message}`);
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Mock data for compliance metrics
  const complianceMetrics = [
    {
      title: "Compliance Score",
      value: "98.5%",
      trend: "+2.1%",
      color: "success",
      icon: <VerifiedIcon />
    },
    {
      title: "Active Entities",
      value: "12",
      trend: "+1",
      color: "info",
      icon: <EntityIcon />
    },
    {
      title: "Regulatory Frameworks",
      value: "25+",
      trend: "+3",
      color: "primary",
      icon: <ComplianceIcon />
    },
    {
      title: "Audit Readiness",
      value: "100%",
      trend: "+0%",
      color: "success",
      icon: <AuditIcon />
    }
  ];

  // Mock data for compliance status
  const complianceStatus = [
    {
      entity: "EdonuOps US",
      country: "United States",
      frameworks: ["SOX", "GAAP", "IRS"],
      status: "Compliant",
      lastAudit: "2024-01-10",
      nextReview: "2024-04-15"
    },
    {
      entity: "EdonuOps EU",
      country: "Germany",
      frameworks: ["IFRS", "GDPR", "EU Tax"],
      status: "Compliant",
      lastAudit: "2024-01-05",
      nextReview: "2024-04-10"
    },
    {
      entity: "EdonuOps Asia",
      country: "Singapore",
      frameworks: ["SFRS", "MAS", "IRAS"],
      status: "Review Required",
      lastAudit: "2023-12-20",
      nextReview: "2024-03-15"
    }
  ];

  const tabs = [
    {
      label: 'Regulatory Frameworks',
      icon: <ComplianceIcon />,
      component: <RegulatoryFrameworks />,
      description: 'Manage global regulatory frameworks and compliance rules'
    },
    {
      label: 'Legal Entities',
      icon: <EntityIcon />,
      component: <LegalEntities />,
      description: 'Multi-entity management and organizational structure'
    },
    {
      label: 'Financial Statements',
      icon: <ReportingIcon />,
      component: <FinancialStatements />,
      description: 'Entity-level financial statements and reporting'
    },
    {
      label: 'Consolidation',
      icon: <ConsolidationIcon />,
      component: <Consolidation />,
      description: 'Multi-entity financial consolidation and elimination'
    },
    {
      label: 'Statutory Reporting',
      icon: <AssignmentIcon />,
      component: <StatutoryReporting />,
      description: 'Country-specific statutory reports and filings'
    },
    {
      label: 'Compliance Checks',
      icon: <CheckCircleIcon />,
      component: <ComplianceChecks />,
      description: 'Automated compliance validation and monitoring'
    },
    {
      label: 'Analytics',
      icon: <PerformanceIcon />,
      component: <ComplianceAnalytics />,
      description: 'Compliance analytics and risk assessment'
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Compliant': return 'success';
      case 'Review Required': return 'warning';
      case 'Non-Compliant': return 'error';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Compliance Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
            <ComplianceIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
              Global Compliance & Consolidation
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Multi-Entity Financial Consolidation, Regulatory Compliance & Statutory Reporting
            </Typography>
          </Box>
        </Box>
        
        {/* Status Banner */}
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            🌍 Global Compliance Suite Active
          </Typography>
          <Typography variant="body2">
            Complete multi-entity financial consolidation with regulatory compliance across 25+ countries and frameworks.
          </Typography>
        </Alert>
      </Box>

      {/* Compliance Metrics */}
      <Paper elevation={3} sx={{ borderRadius: 2, p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Compliance Performance Metrics
        </Typography>
        
        <Grid container spacing={3}>
          {complianceMetrics.map((metric, index) => (
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

      {/* Compliance Status Overview */}
      <Paper elevation={3} sx={{ borderRadius: 2, p: 3, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            <FlagIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Entity Compliance Status
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => showSnackbar('Add entity form would open here')}>
            Add Entity
          </Button>
        </Box>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Legal Entity</TableCell>
                <TableCell>Country</TableCell>
                <TableCell>Regulatory Frameworks</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Audit</TableCell>
                <TableCell>Next Review</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {complianceStatus.map((entity, index) => (
                <TableRow key={index}>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      {entity.entity}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LocationIcon fontSize="small" />
                      {entity.country}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box display="flex" gap={0.5} flexWrap="wrap">
                      {entity.frameworks.map((framework, idx) => (
                        <Chip 
                          key={idx}
                          label={framework} 
                          size="small" 
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={entity.status} 
                      color={getStatusColor(entity.status)} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{entity.lastAudit}</TableCell>
                  <TableCell>{entity.nextReview}</TableCell>
                  <TableCell>
                    <IconButton size="small" color="primary" onClick={() => showSnackbar(`View compliance details for ${entity.entity}`)}>
                      <ViewIcon />
                    </IconButton>
                    <IconButton size="small" color="primary" onClick={() => showSnackbar(`Edit compliance settings for ${entity.entity}`)}>
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Main Compliance Interface */}
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
          
          {/* Module Component */}
          {tabs[activeTab].component}
        </Box>
      </Paper>

      {/* Compliance Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Global Compliance Suite - Multi-Entity Financial Consolidation & Regulatory Compliance
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="SOX Compliant" size="small" sx={{ mr: 1 }} />
          <Chip label="IFRS Ready" size="small" sx={{ mr: 1 }} />
          <Chip label="GDPR Compliant" size="small" sx={{ mr: 1 }} />
          <Chip label="Enterprise Grade" size="small" color="primary" />
        </Box>
      </Box>
    </Container>
  );
};

export default ComplianceModule;
