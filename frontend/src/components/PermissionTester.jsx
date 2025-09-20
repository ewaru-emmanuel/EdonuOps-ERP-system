import React, { useState } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Button, TextField, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Alert, Accordion, AccordionSummary, AccordionDetails, Divider
} from '@mui/material';
import { ExpandMore, Security, CheckCircle, Cancel, VpnKey } from '@mui/icons-material';
import { usePermissions } from '../hooks/usePermissions';
import PermissionGuard, { PermissionButton, RoleBadge } from './PermissionGuard';

const PermissionTester = () => {
  const { 
    permissions, 
    modules, 
    userRole, 
    hasPermission, 
    hasModuleAccess,
    getUserCapabilities,
    loading 
  } = usePermissions();
  
  const [testPermission, setTestPermission] = useState('');
  const [testModule, setTestModule] = useState('');
  
  const capabilities = getUserCapabilities();
  
  // Common permissions to test
  const commonPermissions = [
    'finance.journal.create',
    'finance.journal.read', 
    'finance.journal.update',
    'finance.journal.delete',
    'sales.customers.create',
    'inventory.products.create',
    'procurement.vendors.create',
    'system.users.create',
    'system.roles.manage'
  ];
  
  // Common modules to test
  const commonModules = [
    'general',
    'finance', 
    'inventory',
    'sales',
    'procurement',
    'system'
  ];

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography>Loading permissions...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Security color="primary" />
        Permission Testing Dashboard
      </Typography>
      
      {/* Current User Info */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Current User Status</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <RoleBadge showPermissionCount />
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Accessible Modules: {modules.join(', ') || 'None'}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Permission Testing */}
      <Grid container spacing={3}>
        {/* Test Specific Permission */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Test Specific Permission</Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  size="small"
                  label="Permission Name"
                  value={testPermission}
                  onChange={(e) => setTestPermission(e.target.value)}
                  placeholder="e.g., finance.journal.create"
                  fullWidth
                />
                <Button 
                  variant="outlined" 
                  onClick={() => {
                    const result = hasPermission(testPermission);
                    alert(`Permission "${testPermission}": ${result ? '✅ GRANTED' : '❌ DENIED'}`);
                  }}
                >
                  Test
                </Button>
              </Box>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Common Permissions:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {commonPermissions.map(perm => (
                  <Chip
                    key={perm}
                    label={perm}
                    size="small"
                    color={hasPermission(perm) ? 'success' : 'default'}
                    onClick={() => setTestPermission(perm)}
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Test Module Access */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Test Module Access</Typography>
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  size="small"
                  label="Module Name"
                  value={testModule}
                  onChange={(e) => setTestModule(e.target.value)}
                  placeholder="e.g., finance"
                  fullWidth
                />
                <Button 
                  variant="outlined"
                  onClick={() => {
                    const result = hasModuleAccess(testModule);
                    alert(`Module "${testModule}": ${result ? '✅ ACCESS GRANTED' : '❌ ACCESS DENIED'}`);
                  }}
                >
                  Test
                </Button>
              </Box>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Available Modules:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {commonModules.map(module => (
                  <Chip
                    key={module}
                    label={module}
                    size="small"
                    color={hasModuleAccess(module) ? 'success' : 'default'}
                    onClick={() => setTestModule(module)}
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* User Capabilities */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>User Capabilities</Typography>
          <Grid container spacing={2}>
            {Object.entries(capabilities).map(([capability, hasAccess]) => (
              <Grid item xs={12} sm={6} md={4} key={capability}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {hasAccess ? (
                    <CheckCircle color="success" fontSize="small" />
                  ) : (
                    <Cancel color="error" fontSize="small" />
                  )}
                  <Typography variant="body2">
                    {capability.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Permission Guard Examples */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Permission Guard Examples</Typography>
          
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Finance Operations</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <PermissionGuard permission="finance.journal.create">
                    <Alert severity="success">✅ You can create journal entries</Alert>
                  </PermissionGuard>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <PermissionGuard permission="finance.payments.approve">
                    <Alert severity="success">✅ You can approve payments</Alert>
                  </PermissionGuard>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Inventory Operations</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <PermissionGuard permission="inventory.products.create">
                    <Alert severity="success">✅ You can create products</Alert>
                  </PermissionGuard>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <PermissionGuard permission="inventory.stock.adjust">
                    <Alert severity="success">✅ You can adjust stock levels</Alert>
                  </PermissionGuard>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography>Administrative Operations</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <PermissionGuard permission="system.users.create">
                    <Alert severity="success">✅ You can manage users</Alert>
                  </PermissionGuard>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <PermissionGuard permission="system.roles.manage">
                    <Alert severity="success">✅ You can manage roles</Alert>
                  </PermissionGuard>
                </Grid>
              </Grid>
            </AccordionDetails>
          </Accordion>
        </CardContent>
      </Card>

      {/* Permission Buttons Examples */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Permission Button Examples</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            <PermissionButton permission="finance.journal.create" variant="contained">
              Create Journal Entry
            </PermissionButton>
            <PermissionButton permission="sales.customers.create" variant="outlined">
              Create Customer
            </PermissionButton>
            <PermissionButton permission="inventory.products.create" variant="outlined">
              Create Product
            </PermissionButton>
            <PermissionButton permission="system.users.create" variant="outlined" color="error">
              Manage Users
            </PermissionButton>
          </Box>
        </CardContent>
      </Card>

      {/* All Permissions Table */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>All User Permissions</Typography>
          <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 400 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>Permission</TableCell>
                  <TableCell>Module</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Resource</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {permissions.map((perm) => (
                  <TableRow key={perm.id}>
                    <TableCell>{perm.name}</TableCell>
                    <TableCell>
                      <Chip label={perm.module} size="small" color="primary" />
                    </TableCell>
                    <TableCell>{perm.action}</TableCell>
                    <TableCell>{perm.resource || 'N/A'}</TableCell>
                    <TableCell>
                      <Chip 
                        label="Granted" 
                        size="small" 
                        color="success" 
                        icon={<CheckCircle />} 
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PermissionTester;

