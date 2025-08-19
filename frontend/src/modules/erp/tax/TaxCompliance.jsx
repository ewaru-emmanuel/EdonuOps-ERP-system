import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  LinearProgress,
  Button
} from '@mui/material';
import {
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  TrendingUp as TrendingIcon
} from '@mui/icons-material';

const TaxCompliance = () => {
  const [complianceData, setComplianceData] = useState({
    overallScore: 95,
    pendingIssues: 3,
    criticalIssues: 1,
    lastAudit: '2024-01-15',
    nextAudit: '2024-07-15'
  });

  const [complianceItems, setComplianceItems] = useState([]);

  useEffect(() => {
    fetchComplianceData();
  }, []);

  const fetchComplianceData = async () => {
    // Mock compliance data
    const mockItems = [
      {
        id: 1,
        title: 'Sales Tax Registration',
        status: 'compliant',
        description: 'All required sales tax registrations are current',
        lastUpdated: '2024-03-01',
        priority: 'high'
      },
      {
        id: 2,
        title: 'Quarterly Tax Filings',
        status: 'warning',
        description: 'Q1 2024 filing due in 15 days',
        lastUpdated: '2024-03-15',
        priority: 'critical'
      },
      {
        id: 3,
        title: 'Tax Rate Updates',
        status: 'compliant',
        description: 'All tax rates are up to date',
        lastUpdated: '2024-02-28',
        priority: 'medium'
      },
      {
        id: 4,
        title: 'Documentation Requirements',
        status: 'non-compliant',
        description: 'Missing supporting documentation for Q4 2023',
        lastUpdated: '2024-01-20',
        priority: 'high'
      }
    ];
    setComplianceItems(mockItems);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'compliant': return <CheckIcon color="success" />;
      case 'warning': return <WarningIcon color="warning" />;
      case 'non-compliant': return <ErrorIcon color="error" />;
      default: return <InfoIcon color="info" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'compliant': return 'success';
      case 'warning': return 'warning';
      case 'non-compliant': return 'error';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'default';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Tax Compliance Monitoring
      </Typography>

      {/* Compliance Score */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Overall Compliance Score
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h2" sx={{ fontWeight: 'bold', color: 'success.main', mr: 2 }}>
                  {complianceData.overallScore}%
                </Typography>
                <Box sx={{ flexGrow: 1 }}>
                  <LinearProgress
                    variant="determinate"
                    value={complianceData.overallScore}
                    sx={{ height: 8, borderRadius: 4 }}
                    color="success"
                  />
                </Box>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Last updated: {new Date(complianceData.lastAudit).toLocaleDateString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 'bold' }}>
                Compliance Summary
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography color="textSecondary" gutterBottom>
                    Pending Issues
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'warning.main' }}>
                    {complianceData.pendingIssues}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography color="textSecondary" gutterBottom>
                    Critical Issues
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'error.main' }}>
                    {complianceData.criticalIssues}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography color="textSecondary" gutterBottom>
                    Next Audit Date
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                    {new Date(complianceData.nextAudit).toLocaleDateString()}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Alerts */}
      {complianceData.criticalIssues > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
            Critical Compliance Issues Detected
          </Typography>
          <Typography variant="body2">
            {complianceData.criticalIssues} critical issue(s) require immediate attention.
          </Typography>
        </Alert>
      )}

      {complianceData.pendingIssues > 0 && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
            Pending Compliance Items
          </Typography>
          <Typography variant="body2">
            {complianceData.pendingIssues} item(s) need attention before next audit.
          </Typography>
        </Alert>
      )}

      {/* Compliance Items */}
      <Card elevation={2}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
            Compliance Requirements
          </Typography>
          
          <List>
            {complianceItems.map((item) => (
              <ListItem
                key={item.id}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 2,
                  '&:hover': {
                    bgcolor: 'action.hover'
                  }
                }}
              >
                <ListItemIcon>
                  {getStatusIcon(item.status)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        {item.title}
                      </Typography>
                      <Chip
                        label={item.status.toUpperCase()}
                        color={getStatusColor(item.status)}
                        size="small"
                      />
                      <Chip
                        label={item.priority.toUpperCase()}
                        color={getPriorityColor(item.priority)}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                        {item.description}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Last updated: {new Date(item.lastUpdated).toLocaleDateString()}
                      </Typography>
                    </Box>
                  }
                />
                <Button
                  variant="outlined"
                  size="small"
                  sx={{ ml: 2 }}
                >
                  Review
                </Button>
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    </Box>
  );
};

export default TaxCompliance;




