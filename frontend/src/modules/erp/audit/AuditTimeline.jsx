import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Person as PersonIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

const AuditTimeline = () => {
  const [timeRange, setTimeRange] = useState('24h');

  const timelineEvents = [
    {
      id: 1,
      timestamp: '14:30',
      date: '2024-01-15',
      user: 'John Doe',
      action: 'User Login',
      module: 'Authentication',
      severity: 'Info',
      details: 'Successful login from IP 192.168.1.100',
      icon: <PersonIcon />
    },
    {
      id: 2,
      timestamp: '14:28',
      date: '2024-01-15',
      user: 'Admin',
      action: 'Data Export',
      module: 'Finance',
      severity: 'Warning',
      details: 'Large dataset exported (10,000 records)',
      icon: <WarningIcon />
    },
    {
      id: 3,
      timestamp: '14:25',
      date: '2024-01-15',
      user: 'Jane Smith',
      action: 'Record Deleted',
      module: 'CRM',
      severity: 'Critical',
      details: 'Customer record permanently deleted',
      icon: <ErrorIcon />
    },
    {
      id: 4,
      timestamp: '14:20',
      date: '2024-01-15',
      user: 'Mike Johnson',
      action: 'Permission Changed',
      module: 'User Management',
      severity: 'Warning',
      details: 'User role updated from Viewer to Editor',
      icon: <SettingsIcon />
    },
    {
      id: 5,
      timestamp: '14:15',
      date: '2024-01-15',
      user: 'System',
      action: 'System Backup',
      module: 'System',
      severity: 'Info',
      details: 'Automated backup completed successfully',
      icon: <InfoIcon />
    },
    {
      id: 6,
      timestamp: '14:10',
      date: '2024-01-15',
      user: 'Unknown',
      action: 'Failed Login',
      module: 'Authentication',
      severity: 'Error',
      details: 'Multiple failed login attempts detected',
      icon: <SecurityIcon />
    }
  ];

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'Critical':
        return 'error';
      case 'Warning':
        return 'warning';
      case 'Error':
        return 'error';
      case 'Info':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">Audit Timeline</Typography>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            label="Time Range"
          >
            <MenuItem value="1h">Last Hour</MenuItem>
            <MenuItem value="24h">Last 24 Hours</MenuItem>
            <MenuItem value="7d">Last 7 Days</MenuItem>
            <MenuItem value="30d">Last 30 Days</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Card>
        <CardContent>
          <Box>
            {timelineEvents.map((event, index) => (
              <Box key={event.id}>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    width: 40, 
                    height: 40, 
                    borderRadius: '50%',
                    bgcolor: `${getSeverityColor(event.severity)}.main`,
                    color: 'white',
                    mr: 2,
                    mt: 0.5
                  }}>
                    {event.icon}
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Box>
                        <Box display="flex" alignItems="center" gap={1} mb={1}>
                          <Typography variant="h6" component="span">
                            {event.action}
                          </Typography>
                          <Chip
                            label={event.severity}
                            color={getSeverityColor(event.severity)}
                            size="small"
                          />
                        </Box>
                        
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          <strong>User:</strong> {event.user}
                        </Typography>
                        
                        <Typography variant="body2" color="textSecondary" gutterBottom>
                          <strong>Module:</strong> {event.module}
                        </Typography>
                        
                        <Typography variant="body2" color="textSecondary">
                          {event.details}
                        </Typography>
                      </Box>
                      <Box sx={{ textAlign: 'right' }}>
                        <Typography variant="body2" fontWeight="medium">
                          {event.timestamp}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {event.date}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Box>
                {index < timelineEvents.length - 1 && <Divider sx={{ my: 2 }} />}
              </Box>
            ))}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AuditTimeline;

