import React, { useState } from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, Chip, IconButton, Card, CardContent, Grid, Alert, CircularProgress
} from '@mui/material';
import {
  LocalShipping as PickingIcon,
  CheckCircle as CompletedIcon,
  Schedule as PendingIcon,
  Assignment as PickListIcon
} from '@mui/icons-material';

const SmartPickingOperations = () => {
  const [loading] = useState(false);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Picking Operations
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage picking lists and optimize picking routes
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Pick Lists
              </Typography>
              <Typography variant="h4">
                24
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'success.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CompletedIcon sx={{ color: 'success.main', mr: 1 }} />
                <Typography color="success.main" gutterBottom>
                  Completed
                </Typography>
              </Box>
              <Typography variant="h4" color="success.main">
                18
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'warning.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <PendingIcon sx={{ color: 'warning.main', mr: 1 }} />
                <Typography color="warning.main" gutterBottom>
                  Pending
                </Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                6
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'info.50' }}>
            <CardContent>
              <Typography color="info.main" gutterBottom>
                Avg Pick Time
              </Typography>
              <Typography variant="h4" color="info.main">
                2.3 min
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">
          Pick Lists
        </Typography>
        <Button
          variant="contained"
          startIcon={<PickListIcon />}
        >
          Create Pick List
        </Button>
      </Box>

      {/* Pick Lists Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Pick List ID</TableCell>
              <TableCell>Order</TableCell>
              <TableCell>Items</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow hover>
              <TableCell>
                <Typography variant="subtitle2" fontWeight="bold">
                  PL-001
                </Typography>
              </TableCell>
              <TableCell>ORD-2024-001</TableCell>
              <TableCell>5 items</TableCell>
              <TableCell>
                <Chip label="High" color="error" size="small" />
              </TableCell>
              <TableCell>
                <Chip label="In Progress" color="warning" size="small" />
              </TableCell>
              <TableCell>2024-01-15 09:30</TableCell>
              <TableCell align="center">
                <Button size="small" variant="outlined">
                  Start Picking
                </Button>
              </TableCell>
            </TableRow>
            <TableRow hover>
              <TableCell>
                <Typography variant="subtitle2" fontWeight="bold">
                  PL-002
                </Typography>
              </TableCell>
              <TableCell>ORD-2024-002</TableCell>
              <TableCell>3 items</TableCell>
              <TableCell>
                <Chip label="Normal" color="primary" size="small" />
              </TableCell>
              <TableCell>
                <Chip label="Completed" color="success" size="small" />
              </TableCell>
              <TableCell>2024-01-15 08:15</TableCell>
              <TableCell align="center">
                <Button size="small" variant="outlined">
                  View Details
                </Button>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>

      <Box sx={{ textAlign: 'center', py: 4 }}>
        <PickingIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Picking Operations
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Advanced picking features with route optimization and barcode scanning
        </Typography>
      </Box>
    </Box>
  );
};

export default SmartPickingOperations;
