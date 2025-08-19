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
  MenuItem
} from '@mui/material';
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';

const DashboardHistory = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('All');

  const historyData = [
    {
      id: 1,
      dashboard: 'Executive Dashboard',
      action: 'Modified',
      user: 'John Doe',
      timestamp: '2024-01-15 14:30',
      details: 'Added new KPI widget',
      type: 'Edit'
    },
    {
      id: 2,
      dashboard: 'Sales Analytics',
      action: 'Created',
      user: 'Jane Smith',
      timestamp: '2024-01-15 11:15',
      details: 'New dashboard created from template',
      type: 'Create'
    },
    {
      id: 3,
      dashboard: 'Financial Overview',
      action: 'Viewed',
      user: 'Mike Johnson',
      timestamp: '2024-01-15 09:45',
      details: 'Dashboard accessed',
      type: 'View'
    },
    {
      id: 4,
      dashboard: 'HR Dashboard',
      action: 'Deleted',
      user: 'Sarah Wilson',
      timestamp: '2024-01-14 16:20',
      details: 'Dashboard removed',
      type: 'Delete'
    },
    {
      id: 5,
      dashboard: 'Inventory Management',
      action: 'Modified',
      user: 'Tom Brown',
      timestamp: '2024-01-14 13:10',
      details: 'Updated widget configuration',
      type: 'Edit'
    },
    {
      id: 6,
      dashboard: 'Executive Dashboard',
      action: 'Viewed',
      user: 'Lisa Davis',
      timestamp: '2024-01-14 10:30',
      details: 'Dashboard accessed',
      type: 'View'
    }
  ];

  const getActionIcon = (type) => {
    switch (type) {
      case 'Edit':
        return <EditIcon fontSize="small" />;
      case 'Create':
        return <AddIcon fontSize="small" />;
      case 'Delete':
        return <DeleteIcon fontSize="small" />;
      case 'View':
        return <VisibilityIcon fontSize="small" />;
      default:
        return null;
    }
  };

  const getActionColor = (type) => {
    switch (type) {
      case 'Edit':
        return 'warning';
      case 'Create':
        return 'success';
      case 'Delete':
        return 'error';
      case 'View':
        return 'info';
      default:
        return 'default';
    }
  };

  const filteredHistory = historyData.filter(item => {
    const matchesSearch = item.dashboard.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.details.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === 'All' || item.type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Dashboard History</Typography>
      
      {/* Search and Filter */}
      <Box display="flex" gap={2} mb={3}>
        <TextField
          placeholder="Search history..."
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
          <InputLabel>Action Type</InputLabel>
          <Select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            label="Action Type"
          >
            <MenuItem value="All">All</MenuItem>
            <MenuItem value="Create">Create</MenuItem>
            <MenuItem value="Edit">Edit</MenuItem>
            <MenuItem value="Delete">Delete</MenuItem>
            <MenuItem value="View">View</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* History Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Action</TableCell>
                  <TableCell>Dashboard</TableCell>
                  <TableCell>User</TableCell>
                  <TableCell>Details</TableCell>
                  <TableCell>Timestamp</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredHistory.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        {getActionIcon(item.type)}
                        <Chip
                          label={item.action}
                          color={getActionColor(item.type)}
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="medium">
                        {item.dashboard}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {item.user}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {item.details}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="textSecondary">
                        {item.timestamp}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {filteredHistory.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography color="textSecondary">
            No history records found matching your criteria.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default DashboardHistory;


