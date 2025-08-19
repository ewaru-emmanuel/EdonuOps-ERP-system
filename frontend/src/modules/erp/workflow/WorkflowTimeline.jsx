import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Schedule as ScheduleIcon,
  PlayArrow as PlayIcon
} from '@mui/icons-material';

const WorkflowTimeline = () => {
  const [timelineData, setTimelineData] = useState([]);

  useEffect(() => {
    fetchTimelineData();
  }, []);

  const fetchTimelineData = async () => {
    // Mock timeline data
    const mockTimeline = [
      {
        id: 1,
        workflowName: 'Invoice Processing',
        step: 'Validate Invoice',
        status: 'completed',
        timestamp: '2024-03-15T10:30:00Z',
        duration: '2m 15s'
      },
      {
        id: 2,
        workflowName: 'Invoice Processing',
        step: 'Calculate Tax',
        status: 'completed',
        timestamp: '2024-03-15T10:32:15Z',
        duration: '1m 30s'
      },
      {
        id: 3,
        workflowName: 'Invoice Processing',
        step: 'Send Approval',
        status: 'running',
        timestamp: '2024-03-15T10:33:45Z',
        duration: 'Running...'
      },
      {
        id: 4,
        workflowName: 'Payment Follow-up',
        step: 'Check Payment Status',
        status: 'completed',
        timestamp: '2024-03-15T09:15:00Z',
        duration: '45s'
      },
      {
        id: 5,
        workflowName: 'Payment Follow-up',
        step: 'Send Reminder',
        status: 'completed',
        timestamp: '2024-03-15T09:15:45Z',
        duration: '2m 15s'
      }
    ];
    setTimelineData(mockTimeline);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckIcon color="success" />;
      case 'running': return <PlayIcon color="primary" />;
      case 'failed': return <ErrorIcon color="error" />;
      case 'pending': return <ScheduleIcon color="warning" />;
      default: return <ScheduleIcon color="default" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'failed': return 'error';
      case 'pending': return 'warning';
      default: return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Workflow Timeline
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Recent Workflow Executions
              </Typography>
              
              <Box>
                {timelineData.map((item, index) => (
                  <Box key={item.id}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Box sx={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        width: 40, 
                        height: 40, 
                        borderRadius: '50%',
                        bgcolor: `${getStatusColor(item.status)}.main`,
                        color: 'white',
                        mr: 2
                      }}>
                        {getStatusIcon(item.status)}
                      </Box>
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                            {item.workflowName}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            {new Date(item.timestamp).toLocaleTimeString()}
                          </Typography>
                        </Box>
                        <Typography variant="body2" color="textSecondary">
                          {item.step}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                          <Chip 
                            label={item.status} 
                            color={getStatusColor(item.status)} 
                            size="small" 
                            sx={{ mr: 1 }}
                          />
                          <Typography variant="caption" color="textSecondary">
                            Duration: {item.duration}
                          </Typography>
                        </Box>
                      </Box>
                    </Box>
                    {index < timelineData.length - 1 && <Divider sx={{ my: 2 }} />}
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 'bold' }}>
                Timeline Summary
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Total Executions Today
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                  45
                </Typography>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Average Execution Time
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                  3m 25s
                </Typography>
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" color="textSecondary" gutterBottom>
                  Success Rate
                </Typography>
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                  94.2%
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default WorkflowTimeline;



