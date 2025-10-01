import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField
} from '@mui/material';
import { useAuth } from '../context/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import apiClient from '../services/apiClient';

const PermissionTester = () => {
  const { user, isAuthenticated } = useAuth();
  const { permissions, loading: permissionsLoading } = usePermissions();
  const [testResults, setTestResults] = useState([]);
  const [selectedPermission, setSelectedPermission] = useState('');
  const [testEndpoint, setTestEndpoint] = useState('');
  const [testMethod, setTestMethod] = useState('GET');

  useEffect(() => {
    if (isAuthenticated && permissions.length > 0) {
      runPermissionTests();
    }
  }, [isAuthenticated, permissions]);

  const runPermissionTests = async () => {
    const results = [];
    
    // Test 1: Check if user has basic permissions
    results.push({
      test: 'User Authentication',
      result: isAuthenticated ? 'PASS' : 'FAIL',
      details: isAuthenticated ? 'User is authenticated' : 'User is not authenticated'
    });

    // Test 2: Check permissions loading
    results.push({
      test: 'Permissions Loading',
      result: !permissionsLoading ? 'PASS' : 'FAIL',
      details: !permissionsLoading ? 'Permissions loaded successfully' : 'Permissions still loading'
    });

    // Test 3: Check if user has any permissions
    results.push({
      test: 'User Permissions',
      result: permissions.length > 0 ? 'PASS' : 'FAIL',
      details: `User has ${permissions.length} permissions`
    });

    // Test 4: Test specific permission checks
    const testPermissions = [
      'user.read',
      'finance.read',
      'sales.read',
      'inventory.read',
      'hr.read',
      'admin.access'
    ];

    for (const perm of testPermissions) {
      const hasPermission = permissions.includes(perm);
      results.push({
        test: `Permission: ${perm}`,
        result: hasPermission ? 'PASS' : 'FAIL',
        details: hasPermission ? 'User has this permission' : 'User does not have this permission'
      });
    }

    setTestResults(results);
  };

  const testCustomEndpoint = async () => {
    if (!testEndpoint) {
      alert('Please enter an endpoint');
      return;
    }

    try {
      const response = await apiClient.request({
        method: testMethod,
        url: testEndpoint
      });
      
      setTestResults(prev => [...prev, {
        test: `Custom Test: ${testMethod} ${testEndpoint}`,
        result: 'PASS',
        details: `Status: ${response.status} - ${response.statusText}`
      }]);
    } catch (error) {
      setTestResults(prev => [...prev, {
        test: `Custom Test: ${testMethod} ${testEndpoint}`,
        result: 'FAIL',
        details: `Error: ${error.message}`
      }]);
    }
  };

  const getResultColor = (result) => {
    switch (result) {
      case 'PASS': return 'success';
      case 'FAIL': return 'error';
      default: return 'default';
    }
  };

  const getResultIcon = (result) => {
    switch (result) {
      case 'PASS': return '✅';
      case 'FAIL': return '❌';
      default: return '⚠️';
    }
  };

  if (!isAuthenticated) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">
          Please log in to test permissions
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Permission Tester
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Test user permissions and API access for debugging purposes.
      </Typography>

      <Grid container spacing={3}>
        {/* User Info */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Information
              </Typography>
              
              <List>
                <ListItem>
                  <ListItemText 
                    primary="Username" 
                    secondary={user?.username || 'N/A'} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Email" 
                    secondary={user?.email || 'N/A'} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="User ID" 
                    secondary={user?.id || 'N/A'} 
                  />
                </ListItem>
                <ListItem>
                  <ListItemText 
                    primary="Authentication Status" 
                    secondary={
                      <Chip 
                        label={isAuthenticated ? 'Authenticated' : 'Not Authenticated'} 
                        color={isAuthenticated ? 'success' : 'error'}
                        size="small"
                      />
                    }
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Permissions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                User Permissions
              </Typography>
              
              {permissionsLoading ? (
                <Typography>Loading permissions...</Typography>
              ) : (
                <Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {permissions.length} permissions found
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {permissions.map((permission, index) => (
                      <Chip
                        key={index}
                        label={permission}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Test Results */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Results
              </Typography>
              
              {testResults.length === 0 ? (
                <Typography color="text.secondary">
                  No tests run yet. Click "Run Tests" to start testing.
                </Typography>
              ) : (
                <List>
                  {testResults.map((result, index) => (
                    <ListItem key={index}>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <span>{getResultIcon(result.result)}</span>
                            <span>{result.test}</span>
                            <Chip
                              label={result.result}
                              color={getResultColor(result.result)}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={result.details}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
              
              <Box sx={{ mt: 2 }}>
                <Button 
                  variant="contained" 
                  onClick={runPermissionTests}
                  disabled={permissionsLoading}
                >
                  Run Tests
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Custom Endpoint Test */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Custom Endpoint Test
              </Typography>
              
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} sm={3}>
                  <FormControl fullWidth>
                    <InputLabel>Method</InputLabel>
                    <Select
                      value={testMethod}
                      onChange={(e) => setTestMethod(e.target.value)}
                      label="Method"
                    >
                      <MenuItem value="GET">GET</MenuItem>
                      <MenuItem value="POST">POST</MenuItem>
                      <MenuItem value="PUT">PUT</MenuItem>
                      <MenuItem value="DELETE">DELETE</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} sm={9}>
                  <TextField
                    fullWidth
                    label="Endpoint"
                    value={testEndpoint}
                    onChange={(e) => setTestEndpoint(e.target.value)}
                    placeholder="/api/finance/accounts/"
                  />
                </Grid>
              </Grid>
              
              <Button 
                variant="outlined" 
                onClick={testCustomEndpoint}
                disabled={!testEndpoint}
              >
                Test Endpoint
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PermissionTester;