import React, { useState } from 'react';
import {
  Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Button, Chip, IconButton, TextField, Card, CardContent, Grid,
  Alert, CircularProgress, Dialog, DialogTitle, DialogContent, DialogActions,
  FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';

const SmartAdjustments = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedAdjustment, setSelectedAdjustment] = useState(null);
  const { data: adjustments, loading, error, refresh } = useRealTimeData('/api/inventory/core/adjustments');
  const { data: products } = useRealTimeData('/api/inventory/core/products');

  const handleOpenDialog = (adjustment = null) => {
    setSelectedAdjustment(adjustment);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedAdjustment(null);
  };

  const getAdjustmentTypeChip = (type) => {
    switch (type) {
      case 'count':
        return <Chip label="Stock Count" color="primary" size="small" />;
      case 'adjustment':
        return <Chip label="Adjustment" color="warning" size="small" />;
      case 'correction':
        return <Chip label="Correction" color="error" size="small" />;
      default:
        return <Chip label={type} color="default" size="small" />;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Error loading adjustments: {error.message}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Stock Adjustments
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Count stock and make corrections to your inventory
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Adjustments
              </Typography>
              <Typography variant="h4">
                {adjustments?.length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'primary.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckCircleIcon sx={{ color: 'primary.main', mr: 1 }} />
                <Typography color="primary.main" gutterBottom>
                  Stock Counts
                </Typography>
              </Box>
              <Typography variant="h4" color="primary.main">
                {adjustments?.filter(a => a.type === 'count').length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'warning.50' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <WarningIcon sx={{ color: 'warning.main', mr: 1 }} />
                <Typography color="warning.main" gutterBottom>
                  Adjustments
                </Typography>
              </Box>
              <Typography variant="h4" color="warning.main">
                {adjustments?.filter(a => a.type === 'adjustment').length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ bgcolor: 'success.50' }}>
            <CardContent>
              <Typography color="success.main" gutterBottom>
                This Month
              </Typography>
              <Typography variant="h4" color="success.main">
                {adjustments?.filter(a => {
                  const date = new Date(a.created_at);
                  const now = new Date();
                  return date.getMonth() === now.getMonth() && date.getFullYear() === now.getFullYear();
                }).length || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, gap: 2, flexWrap: 'wrap' }}>
        <Typography variant="h5" component="h3" sx={{ fontWeight: 'bold' }}>Stock Adjustments</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          New Adjustment
        </Button>
      </Box>

      {/* Adjustments Table */}
      <TableContainer component={Paper} sx={{ width: '100%', overflowX: 'auto' }}>
        <Table sx={{ minWidth: 800 }}>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Product</TableCell>
              <TableCell>Type</TableCell>
              <TableCell align="right">Previous Qty</TableCell>
              <TableCell align="right">New Qty</TableCell>
              <TableCell align="right">Difference</TableCell>
              <TableCell>Reason</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {adjustments?.map((adjustment) => (
              <TableRow key={adjustment.id} hover>
                <TableCell>
                  {new Date(adjustment.created_at).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Typography variant="subtitle2">
                    {adjustment.product_name || 'Unknown Product'}
                  </Typography>
                </TableCell>
                <TableCell>
                  {getAdjustmentTypeChip(adjustment.type)}
                </TableCell>
                <TableCell align="right">
                  {adjustment.previous_quantity || 0}
                </TableCell>
                <TableCell align="right">
                  {adjustment.new_quantity || 0}
                </TableCell>
                <TableCell align="right">
                  <Typography 
                    variant="body2" 
                    color={adjustment.quantity_difference > 0 ? 'success.main' : 'error.main'}
                    fontWeight="bold"
                  >
                    {adjustment.quantity_difference > 0 ? '+' : ''}{adjustment.quantity_difference || 0}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {adjustment.reason || 'No reason provided'}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip 
                    label={adjustment.status || 'Completed'} 
                    color={adjustment.status === 'pending' ? 'warning' : 'success'} 
                    size="small" 
                  />
                </TableCell>
                <TableCell align="center">
                  <IconButton size="small" onClick={() => handleOpenDialog(adjustment)}>
                    <ViewIcon />
                  </IconButton>
                  <IconButton size="small" onClick={() => handleOpenDialog(adjustment)}>
                    <EditIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {(!adjustments || adjustments.length === 0) && (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No adjustments found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Create your first stock adjustment to get started
          </Typography>
        </Box>
      )}

      {/* Adjustment Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedAdjustment ? 'Edit Adjustment' : 'New Stock Adjustment'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Product</InputLabel>
                <Select
                  value={selectedAdjustment?.product_id || ''}
                  label="Product"
                  disabled={!!selectedAdjustment}
                >
                  {products?.map((product) => (
                    <MenuItem key={product.id} value={product.id}>
                      {product.name} ({product.sku || product.product_id})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Adjustment Type</InputLabel>
                <Select
                  value={selectedAdjustment?.type || 'count'}
                  label="Adjustment Type"
                >
                  <MenuItem value="count">Stock Count</MenuItem>
                  <MenuItem value="adjustment">Adjustment</MenuItem>
                  <MenuItem value="correction">Correction</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="New Quantity"
                type="number"
                value={selectedAdjustment?.new_quantity || ''}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Reason"
                value={selectedAdjustment?.reason || ''}
                placeholder="Why is this adjustment needed?"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button variant="contained" onClick={handleCloseDialog}>
            {selectedAdjustment ? 'Update' : 'Create'} Adjustment
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SmartAdjustments;
