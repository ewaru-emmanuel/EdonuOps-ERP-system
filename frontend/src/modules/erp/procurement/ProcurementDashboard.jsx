import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Button,
  LinearProgress
} from '@mui/material';
import {
  Pending,
  CheckCircle,
  Warning,
  Add as AddIcon,
  Business,
  Description,
  AttachFile
} from '@mui/icons-material';

const ProcurementDashboard = () => {
  const showSnackbar = (message, severity = 'success') => {
    // For now, just log to console. In a real app, this would show a snackbar
    console.log(`${severity.toUpperCase()}: ${message}`);
  };
  
  const recentPOs = [
    {
      id: 'PO-001',
      vendor: 'Tech Supplies Co.',
      amount: 12500,
      status: 'pending',
      date: '2024-01-15'
    },
    {
      id: 'PO-002',
      vendor: 'Office Solutions',
      amount: 8500,
      status: 'approved',
      date: '2024-01-14'
    },
    {
      id: 'PO-003',
      vendor: 'Industrial Parts Ltd.',
      amount: 22000,
      status: 'rejected',
      date: '2024-01-13'
    },
    {
      id: 'PO-004',
      vendor: 'Global Electronics',
      amount: 15600,
      status: 'pending',
      date: '2024-01-12'
    }
  ];

  const pendingApprovals = [
    {
      id: 'PO-005',
      vendor: 'Software Solutions Inc.',
      amount: 8900,
      submittedBy: 'John Smith',
      submittedDate: '2024-01-15'
    },
    {
      id: 'PO-006',
      vendor: 'Hardware Plus',
      amount: 12300,
      submittedBy: 'Sarah Johnson',
      submittedDate: '2024-01-14'
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'success';
      case 'pending': return 'warning';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle color="success" />;
      case 'pending': return <Pending color="warning" />;
      case 'rejected': return <Warning color="error" />;
      default: return <Pending />;
    }
  };

  return (
    <Grid container spacing={3}>
      {/* Recent Purchase Orders */}
      <Grid item xs={12} lg={8}>
        <Card elevation={2}>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold' }}>
                Recent Purchase Orders
              </Typography>
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                size="small"
                onClick={() => showSnackbar('Create new purchase order form would open here')}
                sx={{ textTransform: 'none' }}
              >
                New PO
              </Button>
            </Box>
            
            <List sx={{ p: 0 }}>
              {recentPOs.map((po, index) => (
                <ListItem
                  key={po.id}
                  sx={{
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    '&:last-child': { mb: 0 }
                  }}
                >
                  <ListItemIcon>
                    {getStatusIcon(po.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>
                          {po.id}
                        </Box>
                        <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>
                          ${po.amount.toLocaleString()}
                        </Box>
                      </Box>
                    }
                    secondary={
                      <Box component="span" sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
                        {po.vendor}
                      </Box>
                    }
                  />
                  <Box sx={{ ml: 2 }}>
                    <Chip
                      label={po.status}
                      size="small"
                      color={getStatusColor(po.status)}
                      sx={{ textTransform: 'capitalize' }}
                    />
                  </Box>
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Pending Approvals */}
      <Grid item xs={12} lg={4}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 3 }}>
              Pending Approvals
            </Typography>
            
            <List sx={{ p: 0 }}>
              {pendingApprovals.map((approval, index) => (
                <ListItem
                  key={approval.id}
                  sx={{
                    border: '1px solid',
                    borderColor: 'warning.main',
                    borderRadius: 1,
                    mb: 2,
                    bgcolor: 'warning.50'
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem' }}>
                          {approval.id}
                        </Box>
                        <Box component="span" sx={{ fontWeight: 'bold', fontSize: '0.875rem', color: 'warning.main' }}>
                          ${approval.amount.toLocaleString()}
                        </Box>
                      </Box>
                    }
                    secondary={
                      <Box component="span" sx={{ fontSize: '0.875rem', color: 'text.secondary' }}>
                        {approval.vendor}
                      </Box>
                    }
                  />
                  <Box sx={{ ml: 2, display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <Box component="span" sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                      Submitted by {approval.submittedBy}
                    </Box>
                    <Box component="span" sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                      {approval.submittedDate}
                    </Box>
                  </Box>
                </ListItem>
              ))}
            </List>

            <Box sx={{ mt: 2 }}>
              <Button
                variant="contained"
                color="warning"
                fullWidth
                onClick={() => showSnackbar('Review all pending approvals would open here')}
                sx={{ textTransform: 'none' }}
              >
                Review All Pending
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Quick Actions */}
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 3 }}>
              Quick Actions
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  fullWidth
                  onClick={() => showSnackbar('Create purchase order form would open here')}
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Create PO
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<Business />}
                  fullWidth
                  onClick={() => showSnackbar('Add vendor form would open here')}
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Add Vendor
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<Description />}
                  fullWidth
                  onClick={() => showSnackbar('View procurement reports would open here')}
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  View Reports
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  startIcon={<AttachFile />}
                  fullWidth
                  onClick={() => showSnackbar('Upload documents dialog would open here')}
                  sx={{ 
                    textTransform: 'none', 
                    py: 2,
                    borderStyle: 'dashed',
                    borderWidth: 2
                  }}
                >
                  Upload Documents
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Grid>

      {/* Performance Metrics */}
      <Grid item xs={12} md={6}>
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" component="h3" sx={{ fontWeight: 'bold', mb: 3 }}>
              Performance Metrics
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Approval Rate</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>85%</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={85} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Average Processing Time</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>2.3 days</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={70} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Cost Savings</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>12.5%</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={75} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Vendor Satisfaction</Typography>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>4.2/5</Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={84} 
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default ProcurementDashboard;
