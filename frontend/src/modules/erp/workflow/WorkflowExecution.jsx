import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Button,
  LinearProgress
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Visibility as ViewIcon,
  Pause as PauseIcon
} from '@mui/icons-material';

const WorkflowExecution = () => {
  const [executions, setExecutions] = useState([]);

  useEffect(() => {
    fetchExecutions();
  }, []);

  const fetchExecutions = async () => {
    // Mock execution data
    const mockExecutions = [
      {
        id: 1,
        workflowName: 'Invoice Processing',
        status: 'running',
        startTime: '2024-03-15T10:30:00Z',
        endTime: null,
        progress: 75,
        steps: 5,
        currentStep: 4
      },
      {
        id: 2,
        workflowName: 'Payment Follow-up',
        status: 'completed',
        startTime: '2024-03-15T09:15:00Z',
        endTime: '2024-03-15T09:18:00Z',
        progress: 100,
        steps: 3,
        currentStep: 3
      },
      {
        id: 3,
        workflowName: 'Inventory Alert',
        status: 'failed',
        startTime: '2024-03-15T08:45:00Z',
        endTime: '2024-03-15T08:47:00Z',
        progress: 40,
        steps: 2,
        currentStep: 1
      }
    ];
    setExecutions(mockExecutions);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'primary';
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'paused': return 'warning';
      default: return 'default';
    }
  };

  const handleStartExecution = (id) => {
    // TODO: Start workflow execution
    console.log('Starting execution:', id);
  };

  const handleStopExecution = (id) => {
    // TODO: Stop workflow execution
    console.log('Stopping execution:', id);
  };

  const formatDuration = (startTime, endTime) => {
    if (!endTime) return 'Running...';
    const start = new Date(startTime);
    const end = new Date(endTime);
    const diff = end - start;
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  return (
    <Box>
      <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Workflow Execution Monitor
      </Typography>

      <TableContainer component={Paper} elevation={2}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: 'primary.main' }}>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Workflow</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Progress</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Start Time</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Duration</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {executions.map((execution) => (
              <TableRow key={execution.id} hover>
                <TableCell>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    {execution.workflowName}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Step {execution.currentStep} of {execution.steps}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={execution.status.toUpperCase()}
                    color={getStatusColor(execution.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ width: '100%', mr: 1 }}>
                    <LinearProgress
                      variant="determinate"
                      value={execution.progress}
                      sx={{ height: 8, borderRadius: 4 }}
                      color={getStatusColor(execution.status)}
                    />
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {execution.progress}%
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {new Date(execution.startTime).toLocaleTimeString()}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {formatDuration(execution.startTime, execution.endTime)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {execution.status === 'running' && (
                      <>
                        <IconButton size="small" sx={{ color: 'warning.main' }}>
                          <PauseIcon />
                        </IconButton>
                        <IconButton 
                          size="small" 
                          sx={{ color: 'error.main' }}
                          onClick={() => handleStopExecution(execution.id)}
                        >
                          <StopIcon />
                        </IconButton>
                      </>
                    )}
                    {execution.status === 'paused' && (
                      <IconButton 
                        size="small" 
                        sx={{ color: 'success.main' }}
                        onClick={() => handleStartExecution(execution.id)}
                      >
                        <PlayIcon />
                      </IconButton>
                    )}
                    <IconButton size="small" sx={{ color: 'primary.main' }}>
                      <ViewIcon />
                    </IconButton>
                    <IconButton size="small" sx={{ color: 'info.main' }}>
                      <RefreshIcon />
                    </IconButton>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default WorkflowExecution;




