import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  TextField,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as VisibilityIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const AuditLogs = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState('All');
  const [moduleFilter, setModuleFilter] = useState('All');

  const auditLogs = [
    {
      id: 1,
      timestamp: '2024-01-15 14:30:25',
      user: 'john.doe@company.com',
      action: 'User Login',
      module: 'Authentication',
      severity: 'Info',
      details: 'Successful login from IP 192.168.1.100',
      ipAddress: '192.168.1.100'
    },
    {
      id: 2,
      timestamp: '2024-01-15 14:28:15',
      user: 'admin@company.com',
      action: 'Data Export',
      module: 'Finance',
      severity: 'Warning',
      details: 'Large dataset exported (10,000 records)',
      ipAddress: '192.168.1.50'
    },
    {
      id: 3,
      timestamp: '2024-01-15 14:25:42',
      user: 'jane.smith@company.com',
      action: 'Record Deleted',
      module: 'CRM',
      severity: 'Critical',
      details: 'Customer record permanently deleted',
      ipAddress: '192.168.1.75'
    },
    {
      id: 4,
      timestamp: '2024-01-15 14:20:18',
      user: 'mike.johnson@company.com',
      action: 'Permission Changed',
      module: 'User Management',
      severity: 'Warning',
      details: 'User role updated from Viewer to Editor',
      ipAddress: '192.168.1.25'
    },
    {
      id: 5,
      timestamp: '2024-01-15 14:15:33',
      user: 'system@company.com',
      action: 'System Backup',
      module: 'System',
      severity: 'Info',
      details: 'Automated backup completed successfully',
      ipAddress: '192.168.1.1'
    },
    {
      id: 6,
      timestamp: '2024-01-15 14:10:55',
      user: 'unknown@company.com',
      action: 'Failed Login',
      module: 'Authentication',
      severity: 'Error',
      details: 'Multiple failed login attempts detected',
      ipAddress: '203.0.113.45'
    }
  ];

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'Critical':
        return <ErrorIcon color="error" />;
      case 'Warning':
        return <WarningIcon color="warning" />;
      case 'Error':
        return <ErrorIcon color="error" />;
      case 'Info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

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

  const filteredLogs = auditLogs.filter(log => {
    const matchesSearch = log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         log.details.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === 'All' || log.severity === severityFilter;
    const matchesModule = moduleFilter === 'All' || log.module === moduleFilter;
    return matchesSearch && matchesSeverity && matchesModule;
  });

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Audit Logs</Typography>
      
      {/* Search and Filters */}
      <Box display="flex" gap={2} mb={3}>
        <TextField
          placeholder="Search logs..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
          sx={{ flexGrow: 1 }}
        />
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Severity</InputLabel>
          <Select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            label="Severity"
          >
            <MenuItem value="All">All</MenuItem>
            <MenuItem value="Critical">Critical</MenuItem>
            <MenuItem value="Warning">Warning</MenuItem>
            <MenuItem value="Error">Error</MenuItem>
            <MenuItem value="Info">Info</MenuItem>
          </Select>
        </FormControl>
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Module</InputLabel>
          <Select
            value={moduleFilter}
            onChange={(e) => setModuleFilter(e.target.value)}
            label="Module"
          >
            <MenuItem value="All">All</MenuItem>
            <MenuItem value="Authentication">Authentication</MenuItem>
            <MenuItem value="Finance">Finance</MenuItem>
            <MenuItem value="CRM">CRM</MenuItem>
            <MenuItem value="User Management">User Management</MenuItem>
            <MenuItem value="System">System</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Audit Logs Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Severity</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Module</TableCell>
                  <TableCell>Details</TableCell>
                  <TableCell>IP Address</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getSeverityIcon(log.severity)}
                        <Chip
                          label={log.severity}
                          color={getSeverityColor(log.severity)}
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {log.timestamp}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {log.user}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {log.action}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={log.module}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {log.details}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {log.ipAddress}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="View Details">
                        <IconButton size="small">
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {filteredLogs.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="textSecondary">
            No audit logs found matching your criteria.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default AuditLogs;



