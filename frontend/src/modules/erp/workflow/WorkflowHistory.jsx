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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField
} from '@mui/material';
import {
  History as HistoryIcon,
  Visibility as ViewIcon,
  Download as DownloadIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';

const WorkflowHistory = () => {
  const [historyData, setHistoryData] = useState([]);
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedWorkflow, setSelectedWorkflow] = useState('all');

  useEffect(() => {
    fetchHistoryData();
  }, []);

  const fetchHistoryData = async () => {
    // Mock history data
    const mockHistory = [
      {
        id: 1,
        workflowName: 'Invoice Processing',
        status: 'completed',
        startTime: '2024-03-15T10:30:00Z',
        endTime: '2024-03-15T10:35:00Z',
        duration: '5m 0s',
        steps: 5,
        executedBy: 'System'
      },
      {
        id: 2,
        workflowName: 'Payment Follow-up',
        status: 'completed',
        startTime: '2024-03-15T09:15:00Z',
        endTime: '2024-03-15T09:18:00Z',
        duration: '3m 0s',
        steps: 3,
        executedBy: 'System'
      },
      {
        id: 3,
        workflowName: 'Inventory Alert',
        status: 'failed',
        startTime: '2024-03-15T08:45:00Z',
        endTime: '2024-03-15T08:47:00Z',
        duration: '2m 0s',
        steps: 2,
        executedBy: 'System'
      }
    ];
    setHistoryData(mockHistory);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'success';
      case 'failed': return 'error';
      case 'running': return 'primary';
      case 'cancelled': return 'warning';
      default: return 'default';
    }
  };

  const filteredHistory = historyData.filter(item => {
    if (selectedStatus !== 'all' && item.status !== selectedStatus) return false;
    if (selectedWorkflow !== 'all' && item.workflowName !== selectedWorkflow) return false;
    return true;
  });

  return (
    <Box>
      <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold', mb: 3 }}>
        Workflow History
      </Typography>

      {/* Filters */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              label="Status"
            >
              <MenuItem value="all">All Status</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
              <MenuItem value="running">Running</MenuItem>
              <MenuItem value="cancelled">Cancelled</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Workflow</InputLabel>
            <Select
              value={selectedWorkflow}
              onChange={(e) => setSelectedWorkflow(e.target.value)}
              label="Workflow"
            >
              <MenuItem value="all">All Workflows</MenuItem>
              <MenuItem value="Invoice Processing">Invoice Processing</MenuItem>
              <MenuItem value="Payment Follow-up">Payment Follow-up</MenuItem>
              <MenuItem value="Inventory Alert">Inventory Alert</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Search"
            placeholder="Search executions..."
          />
        </Grid>
      </Grid>

      <TableContainer component={Paper} elevation={2}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: 'primary.main' }}>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Workflow</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Start Time</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Duration</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Steps</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Executed By</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredHistory.map((item) => (
              <TableRow key={item.id} hover>
                <TableCell>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    {item.workflowName}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={item.status.toUpperCase()}
                    color={getStatusColor(item.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {new Date(item.startTime).toLocaleString()}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {item.duration}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {item.steps} steps
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="textSecondary">
                    {item.executedBy}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton size="small" sx={{ color: 'primary.main' }}>
                      <ViewIcon />
                    </IconButton>
                    <IconButton size="small" sx={{ color: 'success.main' }}>
                      <DownloadIcon />
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

export default WorkflowHistory;
