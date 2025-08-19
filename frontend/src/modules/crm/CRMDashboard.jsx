import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Divider,
  LinearProgress,
  IconButton,
  Tooltip,
  Paper,
  Stack
} from '@mui/material';
import {
  TrendingUp,
  People,
  Assignment,
  AttachMoney,
  Schedule,
  Add,
  Visibility,
  Edit,
  Delete,
  Phone,
  Email,
  LocationOn,
  Business,
  CalendarToday,
  CheckCircle,
  Warning,
  Error,
  Info
} from '@mui/icons-material';
import { useCRM } from './context/CRMContext';
import { useTask } from './context/TaskContext';
import { useWorkflow } from './context/WorkflowContext';

const CRMDashboard = () => {
  const navigate = useNavigate();
  const { 
    contacts, 
    leads, 
    opportunities, 
    analytics, 
    loading,
    getOpportunitiesByStage 
  } = useCRM();
  
  const { 
    tasks, 
    getTasksDueToday, 
    getOverdueTasks,
    priorities,
    statuses 
  } = useTask();
  
  const { workflows, getActiveWorkflows } = useWorkflow();

  const [recentActivities, setRecentActivities] = useState([]);
  const [quickStats, setQuickStats] = useState({});

  // Navigation handlers
  const handleAddOpportunity = () => {
    navigate('/crm/pipeline');
  };

  const handleAddNewContact = () => {
    navigate('/crm/contacts');
  };

  const handleCreateOpportunity = () => {
    navigate('/crm/opportunities');
  };

  const handleCreateTask = () => {
    navigate('/crm/tasks');
  };

  const handleScheduleMeeting = () => {
    navigate('/crm/tasks');
  };

  // Calculate quick stats
  useEffect(() => {
    const stats = {
      totalContacts: (contacts || []).length,
      totalLeads: (leads || []).length,
      totalOpportunities: (opportunities || []).length,
      totalTasks: (tasks || []).length,
      activeWorkflows: getActiveWorkflows().length,
      overdueTasks: getOverdueTasks().length,
      tasksDueToday: getTasksDueToday().length,
      totalValue: (opportunities || []).reduce((sum, opp) => sum + (opp.value || 0), 0)
    };
    setQuickStats(stats);
  }, [contacts, leads, opportunities, tasks, workflows, getOverdueTasks, getTasksDueToday, getActiveWorkflows]);

  // Recent activities will be populated from real data
  useEffect(() => {
    setRecentActivities([]);
  }, []);

  const getStageColor = (stage) => {
    const colors = {
      'prospecting': '#ff9800',
      'qualification': '#2196f3',
      'proposal': '#9c27b0',
      'negotiation': '#f44336',
      'closed_won': '#4caf50',
      'closed_lost': '#757575'
    };
    return colors[stage] || '#757575';
  };

  const getPriorityColor = (priority) => {
    const priorityObj = priorities.find(p => p.id === priority);
    return priorityObj?.color || '#757575';
  };

  const getStatusColor = (status) => {
    const statusObj = statuses.find(s => s.id === status);
    return statusObj?.color || '#757575';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  };

  const getTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  };

  if (loading.analytics) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2 }}>Loading CRM Dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          CRM Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Overview of your customer relationships, sales pipeline, and team activities
        </Typography>
      </Box>

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Total Contacts
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {quickStats.totalContacts}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <People />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Active Leads
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {quickStats.totalLeads}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <TrendingUp />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Opportunities
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {quickStats.totalOpportunities}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <AttachMoney />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="text.secondary" gutterBottom>
                    Pipeline Value
                  </Typography>
                  <Typography variant="h4" fontWeight="bold">
                    {formatCurrency(quickStats.totalValue)}
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <Business />
                </Avatar>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Pipeline Overview */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
                <Typography variant="h6" fontWeight="bold">
                  Sales Pipeline
                </Typography>
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  size="small"
                  onClick={handleAddOpportunity}
                >
                  Add Opportunity
                </Button>
              </Box>

              <Grid container spacing={2}>
                {['prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won'].map((stage) => {
                  const stageOpportunities = getOpportunitiesByStage(stage);
                  const stageValue = stageOpportunities.reduce((sum, opp) => sum + (opp.value || 0), 0);
                  
                  return (
                    <Grid item xs={12} sm={6} md={4} key={stage}>
                      <Paper 
                        sx={{ 
                          p: 2, 
                          borderLeft: `4px solid ${getStageColor(stage)}`,
                          '&:hover': { boxShadow: 2, cursor: 'pointer' }
                        }}
                        onClick={() => navigate('/crm/pipeline')}
                      >
                        <Typography variant="subtitle2" fontWeight="bold" sx={{ textTransform: 'capitalize' }}>
                          {stage.replace('_', ' ')}
                        </Typography>
                        <Typography variant="h6" fontWeight="bold" sx={{ color: getStageColor(stage) }}>
                          {stageOpportunities.length}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {formatCurrency(stageValue)}
                        </Typography>
                      </Paper>
                    </Grid>
                  );
                })}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                Quick Actions
              </Typography>
              <Stack spacing={2}>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  fullWidth
                  size="large"
                  onClick={handleAddNewContact}
                >
                  Add New Contact
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<TrendingUp />}
                  fullWidth
                  size="large"
                  onClick={handleCreateOpportunity}
                >
                  Create Opportunity
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Assignment />}
                  fullWidth
                  size="large"
                  onClick={handleCreateTask}
                >
                  Create Task
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Schedule />}
                  fullWidth
                  size="large"
                  onClick={handleScheduleMeeting}
                >
                  Schedule Meeting
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activities */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">
                  Recent Activities
                </Typography>
                <Button
                  variant="text"
                  size="small"
                  onClick={() => navigate('/crm/analytics')}
                >
                  View All
                </Button>
              </Box>
              <List>
                {recentActivities.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem alignItems="flex-start">
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: `${activity.color}.light` }}>
                          {activity.icon}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={activity.title}
                        secondary={
                          <React.Fragment>
                            <Typography component="span" variant="body2" color="text.primary">
                              {activity.description}
                            </Typography>
                            <br />
                            <Typography component="span" variant="caption" color="text.secondary">
                              {getTimeAgo(activity.timestamp)}
                            </Typography>
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                    {index < recentActivities.length - 1 && <Divider variant="inset" component="li" />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Task Overview */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">
                  Task Overview
                </Typography>
                <Button
                  variant="text"
                  size="small"
                  onClick={() => navigate('/crm/tasks')}
                >
                  View All
                </Button>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Due Today</Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {quickStats.tasksDueToday}
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={(quickStats.tasksDueToday / Math.max(quickStats.totalTasks, 1)) * 100}
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="error">Overdue</Typography>
                  <Typography variant="body2" fontWeight="bold" color="error">
                    {quickStats.overdueTasks}
                  </Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={(quickStats.overdueTasks / Math.max(quickStats.totalTasks, 1)) * 100}
                  color="error"
                  sx={{ height: 8, borderRadius: 4 }}
                />
              </Box>

              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {statuses.map((status) => {
                  const statusTasks = tasks.filter(task => task.status === status.id);
                  return (
                    <Chip
                      key={status.id}
                      label={`${status.name} (${statusTasks.length})`}
                      size="small"
                      onClick={() => navigate('/crm/tasks')}
                      sx={{ 
                        bgcolor: `${status.color}20`,
                        color: status.color,
                        border: `1px solid ${status.color}40`,
                        cursor: 'pointer',
                        '&:hover': { opacity: 0.8 }
                      }}
                    />
                  );
                })}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Workflow Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" fontWeight="bold">
                  Active Workflows
                </Typography>
                <Button
                  variant="text"
                  size="small"
                  onClick={() => navigate('/crm/workflows')}
                >
                  View All
                </Button>
              </Box>
              <Grid container spacing={2}>
                {getActiveWorkflows().slice(0, 6).map((workflow) => (
                  <Grid item xs={12} sm={6} md={4} key={workflow.id}>
                    <Paper 
                      sx={{ 
                        p: 2, 
                        border: '1px solid #e0e0e0',
                        '&:hover': { boxShadow: 2, cursor: 'pointer' }
                      }}
                      onClick={() => navigate('/crm/workflows')}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {workflow.name}
                        </Typography>
                        <Chip 
                          label="Active" 
                          size="small" 
                          color="success" 
                          variant="outlined"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {workflow.trigger?.name || 'Custom Trigger'}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {workflow.actions?.length || 0} actions configured
                      </Typography>
                    </Paper>
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

export default CRMDashboard;

