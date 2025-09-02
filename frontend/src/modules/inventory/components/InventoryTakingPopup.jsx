import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Select, MenuItem,
  FormControl, InputLabel, Grid, Typography, Box, Chip, IconButton, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, Alert, Switch,
  FormControlLabel, InputAdornment, Tooltip
} from '@mui/material';
import {
  Add as AddIcon, Delete as DeleteIcon, Save as SaveIcon, Send as SendIcon,
  Download as DownloadIcon, Upload as UploadIcon, QrCodeScanner as ScannerIcon,
  Inventory as InventoryIcon
} from '@mui/icons-material';
import apiClient from '../../../services/apiClient';
// Date picker imports removed - using standard HTML date inputs instead

const InventoryTakingPopup = ({ open, onClose, onSave }) => {
  // Removed activeTab state as it's not being used
  const [inventoryData, setInventoryData] = useState({
    id: '',
    warehouse: '',
    inventoryDate: new Date(),
    countingMethod: 'full_count',
    counterName: '',
    inventoryReason: 'regular',
    freezeInventory: false,
    cycleCountGroup: '',
    generalNotes: '',
    items: []
  });

  const [newItem, setNewItem] = useState({
    itemCode: '',
    itemName: '',
    uom: '',
    systemQuantity: 0,
    countedQuantity: 0,
    variance: 0,
    variancePercentage: 0,
    batchLotNumber: '',
    serialNumber: '',
    locationBin: '',
    unitCost: 0,
    itemStatus: 'good',
    expiryDate: null,
    manufacturingDate: null,
    itemRemarks: '',
    attachment: null
  });

  const [scanningMode, setScanningMode] = useState(false);
  const [showSystemQuantity, setShowSystemQuantity] = useState(true);
  // Removed unused state variables: showVarianceAlerts, setShowVarianceAlerts, showReconciliation, setShowReconciliation

  // Enhanced status options
  const itemStatusOptions = [
    { value: 'good', label: 'Good', color: 'success' },
    { value: 'near_expiry', label: 'Near Expiry', color: 'warning' },
    { value: 'expired', label: 'Expired', color: 'error' },
    { value: 'damaged', label: 'Damaged', color: 'error' },
    { value: 'quarantine', label: 'Quarantine', color: 'warning' },
    { value: 'obsolete', label: 'Obsolete', color: 'default' },
    { value: 'recalled', label: 'Recalled', color: 'error' }
  ];

  // Counting methods
  const countingMethods = [
    { value: 'full_count', label: 'Full Count' },
    { value: 'cycle_count', label: 'Cycle Count' },
    { value: 'blind_count', label: 'Blind Count' },
    { value: 'spot_check', label: 'Spot Check' },
    { value: 'expiry_focused', label: 'Expiry-Focused Count' },
    { value: 'condition_check', label: 'Condition Check' }
  ];

  // Inventory reasons
  const inventoryReasons = [
    { value: 'regular', label: 'Regular' },
    { value: 'audit', label: 'Audit' },
    { value: 'damage', label: 'Damage Assessment' },
    { value: 'shrinkage', label: 'Shrinkage Investigation' },
    { value: 'expiry', label: 'Expiry Management' },
    { value: 'quality', label: 'Quality Control' }
  ];

  // Mock warehouses
  const warehouses = [
    { id: 'WH001', name: 'Main Warehouse' },
    { id: 'WH002', name: 'Secondary Warehouse' },
    { id: 'WH003', name: 'Cold Storage' },
    { id: 'WH004', name: 'Hazardous Materials' }
  ];

  // Mock items for demo - removed unused variable

  useEffect(() => {
    if (open) {
      // Generate unique ID
      setInventoryData(prev => ({
        ...prev,
        id: `INV-${Date.now()}`
      }));
    }
  }, [open]);

  const handleAddItem = () => {
    if (newItem.itemCode && newItem.countedQuantity >= 0) {
      const item = {
        ...newItem,
        id: `ITEM-${Date.now()}`,
        variance: newItem.countedQuantity - newItem.systemQuantity,
        variancePercentage: newItem.systemQuantity > 0 
          ? ((newItem.countedQuantity - newItem.systemQuantity) / newItem.systemQuantity * 100)
          : 0
      };

      setInventoryData(prev => ({
        ...prev,
        items: [...prev.items, item]
      }));

      // Reset new item form
      setNewItem({
        itemCode: '',
        itemName: '',
        uom: '',
        systemQuantity: 0,
        countedQuantity: 0,
        variance: 0,
        variancePercentage: 0,
        batchLotNumber: '',
        serialNumber: '',
        locationBin: '',
        unitCost: 0,
        itemStatus: 'good',
        expiryDate: null,
        manufacturingDate: null,
        itemRemarks: '',
        attachment: null
      });
    }
  };

  const handleRemoveItem = (itemId) => {
    setInventoryData(prev => ({
      ...prev,
      items: prev.items.filter(item => item.id !== itemId)
    }));
  };

  const handleItemChange = (itemId, field, value) => {
    setInventoryData(prev => ({
      ...prev,
      items: prev.items.map(item => {
        if (item.id === itemId) {
          const updatedItem = { ...item, [field]: value };
          
          // Recalculate variance if quantity changed
          if (field === 'countedQuantity') {
            updatedItem.variance = value - updatedItem.systemQuantity;
            updatedItem.variancePercentage = updatedItem.systemQuantity > 0 
              ? ((value - updatedItem.systemQuantity) / updatedItem.systemQuantity * 100)
              : 0;
          }
          
          return updatedItem;
        }
        return item;
      })
    }));
  };

  const handleSaveDraft = async () => {
    try {
      const result = await apiClient.post('/inventory/taking/counts', inventoryData);
      console.log('Draft saved:', result);
      alert('Draft saved successfully!');
    } catch (error) {
      console.error('Error saving draft:', error);
      alert('Failed to save draft. Please try again.');
    }
  };

  const handleSubmitCount = async () => {
    if (inventoryData.items.length === 0) {
      alert('Please add at least one item to the count');
      return;
    }
    
    try {
      const result = await apiClient.post(`/inventory/taking/counts/${inventoryData.id || 'new'}/submit`, inventoryData);
      console.log('Count submitted:', result);
      alert('Inventory count submitted successfully!');
      onSave(inventoryData);
      onClose();
    } catch (error) {
      console.error('Error submitting count:', error);
      alert('Failed to submit count. Please try again.');
    }
  };

  const handleExportTemplate = async () => {
    try {
      const response = await apiClient.get('/inventory/taking/export-template');
      const blob = new Blob([response], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'inventory_count_template.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting template:', error);
      alert('Failed to download template. Please try again.');
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
              const response = await apiClient.upload('/inventory/taking/import-csv', file);
        
        const result = response;
          console.log('CSV imported:', result);
          
          // Add imported items to the inventory data
          if (result.imported_items && result.imported_items.length > 0) {
            const importedItems = result.imported_items.map(item => ({
              ...item,
              id: `ITEM-${Date.now()}-${Math.random()}`,
              systemQuantity: 0,
              variance: item.countedQuantity,
              variancePercentage: 0
            }));
            
            setInventoryData(prev => ({
              ...prev,
              items: [...prev.items, ...importedItems]
            }));
            
            alert(`Successfully imported ${result.total_imported} items`);
          }
        // Response is already parsed JSON from apiClient
      } catch (error) {
        console.error('Error importing CSV:', error);
        alert('Failed to import CSV file');
      }
    }
  };

  const getStatusColor = (status) => {
    const statusOption = itemStatusOptions.find(option => option.value === status);
    return statusOption ? statusOption.color : 'default';
  };

  const getVarianceColor = (variance) => {
    if (Math.abs(variance) === 0) return 'success';
    if (Math.abs(variance) <= 5) return 'warning';
    return 'error';
  };

  const calculateSummary = () => {
    const items = inventoryData.items;
    return {
      totalItems: items.length,
      totalCounted: items.reduce((sum, item) => sum + item.countedQuantity, 0),
      totalSystem: items.reduce((sum, item) => sum + item.systemQuantity, 0),
      totalVariance: items.reduce((sum, item) => sum + item.variance, 0),
      itemsWithVariance: items.filter(item => item.variance !== 0).length,
      expiredItems: items.filter(item => item.itemStatus === 'expired').length,
      nearExpiryItems: items.filter(item => item.itemStatus === 'near_expiry').length
    };
  };

  const summary = calculateSummary();

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xl" fullWidth>
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            <InventoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Inventory Taking - {inventoryData.id}
          </Typography>
          <Box>
            <Chip 
              label={inventoryData.countingMethod.replace('_', ' ').toUpperCase()} 
              color="primary" 
              size="small" 
            />
            {inventoryData.freezeInventory && (
              <Chip 
                label="FROZEN" 
                color="warning" 
                size="small" 
                sx={{ ml: 1 }}
              />
            )}
          </Box>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth size="small" sx={{ mb: 2 }}>
                <InputLabel>Warehouse / Location</InputLabel>
                <Select
                  value={inventoryData.warehouse}
                  onChange={(e) => setInventoryData(prev => ({ ...prev, warehouse: e.target.value }))}
                >
                  {warehouses.map(warehouse => (
                    <MenuItem key={warehouse.id} value={warehouse.id}>
                      {warehouse.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                label="Inventory Date"
                type="date"
                value={inventoryData.inventoryDate ? inventoryData.inventoryDate.toISOString().split('T')[0] : ''}
                onChange={(e) => setInventoryData(prev => ({ ...prev, inventoryDate: new Date(e.target.value) }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Counting Method</InputLabel>
                <Select
                  value={inventoryData.countingMethod}
                  onChange={(e) => setInventoryData(prev => ({ ...prev, countingMethod: e.target.value }))}
                >
                  {countingMethods.map(method => (
                    <MenuItem key={method.value} value={method.value}>
                      {method.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                label="Counter Name"
                value={inventoryData.counterName}
                onChange={(e) => setInventoryData(prev => ({ ...prev, counterName: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth size="small">
                <InputLabel>Inventory Reason</InputLabel>
                <Select
                  value={inventoryData.inventoryReason}
                  onChange={(e) => setInventoryData(prev => ({ ...prev, inventoryReason: e.target.value }))}
                >
                  {inventoryReasons.map(reason => (
                    <MenuItem key={reason.value} value={reason.value}>
                      {reason.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                size="small"
                label="Cycle Count Group"
                value={inventoryData.cycleCountGroup}
                onChange={(e) => setInventoryData(prev => ({ ...prev, cycleCountGroup: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={inventoryData.freezeInventory}
                    onChange={(e) => setInventoryData(prev => ({ ...prev, freezeInventory: e.target.checked }))}
                  />
                }
                label="Freeze Inventory During Count"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="General Notes"
                value={inventoryData.generalNotes}
                onChange={(e) => setInventoryData(prev => ({ ...prev, generalNotes: e.target.value }))}
              />
            </Grid>
          </Grid>
        </Box>

        {/* Summary Cards */}
        <Box sx={{ mb: 3 }}>
          <Grid container spacing={2}>
            <Grid item xs={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="primary">{summary.totalItems}</Typography>
                <Typography variant="body2">Total Items</Typography>
              </Paper>
            </Grid>
            <Grid item xs={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="success.main">{summary.totalCounted}</Typography>
                <Typography variant="body2">Counted Qty</Typography>
              </Paper>
            </Grid>
            <Grid item xs={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="warning.main">{summary.itemsWithVariance}</Typography>
                <Typography variant="body2">With Variance</Typography>
              </Paper>
            </Grid>
            <Grid item xs={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="h6" color="error.main">{summary.expiredItems}</Typography>
                <Typography variant="body2">Expired Items</Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>

        {/* Item Entry Section */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Item Entry
            <FormControlLabel
              control={
                <Switch
                  checked={showSystemQuantity}
                  onChange={(e) => setShowSystemQuantity(e.target.checked)}
                />
              }
              label="Show System Quantity"
              sx={{ ml: 2 }}
            />
          </Typography>

          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                size="small"
                label="Item Code"
                value={newItem.itemCode}
                onChange={(e) => setNewItem(prev => ({ ...prev, itemCode: e.target.value }))}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <Tooltip title="Scan Barcode">
                        <IconButton size="small" onClick={() => setScanningMode(!scanningMode)}>
                          <ScannerIcon />
                        </IconButton>
                      </Tooltip>
                    </InputAdornment>
                  )
                }}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                size="small"
                label="Counted Quantity"
                type="number"
                value={newItem.countedQuantity}
                onChange={(e) => setNewItem(prev => ({ ...prev, countedQuantity: parseFloat(e.target.value) || 0 }))}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                size="small"
                label="Batch/Lot Number"
                value={newItem.batchLotNumber}
                onChange={(e) => setNewItem(prev => ({ ...prev, batchLotNumber: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <TextField
                fullWidth
                size="small"
                label="Serial Number"
                value={newItem.serialNumber}
                onChange={(e) => setNewItem(prev => ({ ...prev, serialNumber: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={2}>
              <FormControl fullWidth size="small">
                <InputLabel>Item Status</InputLabel>
                <Select
                  value={newItem.itemStatus}
                  onChange={(e) => setNewItem(prev => ({ ...prev, itemStatus: e.target.value }))}
                >
                  {itemStatusOptions.map(status => (
                    <MenuItem key={status.value} value={status.value}>
                      {status.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={handleAddItem}
                fullWidth
              >
                Add Item
              </Button>
            </Grid>
          </Grid>

          {/* Advanced Fields */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Expiry Date"
                type="date"
                value={newItem.expiryDate ? newItem.expiryDate.toISOString().split('T')[0] : ''}
                onChange={(e) => setNewItem(prev => ({ ...prev, expiryDate: e.target.value ? new Date(e.target.value) : null }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Manufacturing Date"
                type="date"
                value={newItem.manufacturingDate ? newItem.manufacturingDate.toISOString().split('T')[0] : ''}
                onChange={(e) => setNewItem(prev => ({ ...prev, manufacturingDate: e.target.value ? new Date(e.target.value) : null }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Location/Bin"
                value={newItem.locationBin}
                onChange={(e) => setNewItem(prev => ({ ...prev, locationBin: e.target.value }))}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField
                fullWidth
                size="small"
                label="Unit Cost"
                type="number"
                value={newItem.unitCost}
                onChange={(e) => setNewItem(prev => ({ ...prev, unitCost: parseFloat(e.target.value) || 0 }))}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>
                }}
              />
            </Grid>
          </Grid>

          <TextField
            fullWidth
            multiline
            rows={2}
            label="Item Remarks"
            value={newItem.itemRemarks}
            onChange={(e) => setNewItem(prev => ({ ...prev, itemRemarks: e.target.value }))}
          />
        </Box>

        {/* Items Table */}
        <TableContainer component={Paper} sx={{ mb: 3 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Item Code</TableCell>
                <TableCell>Item Name</TableCell>
                <TableCell>UoM</TableCell>
                {showSystemQuantity && <TableCell>System Qty</TableCell>}
                <TableCell>Counted Qty</TableCell>
                <TableCell>Variance</TableCell>
                <TableCell>Batch/Lot</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Expiry Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {inventoryData.items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.itemCode}</TableCell>
                  <TableCell>{item.itemName}</TableCell>
                  <TableCell>{item.uom}</TableCell>
                  {showSystemQuantity && <TableCell>{item.systemQuantity}</TableCell>}
                  <TableCell>
                    <TextField
                      size="small"
                      type="number"
                      value={item.countedQuantity}
                      onChange={(e) => handleItemChange(item.id, 'countedQuantity', parseFloat(e.target.value) || 0)}
                      sx={{ width: 80 }}
                    />
                  </TableCell>
                  <TableCell>
                                         <Chip
                       label={`${item.variance} (${item.variancePercentage ? item.variancePercentage.toFixed(1) : '0.0'}%)`}
                       color={getVarianceColor(item.variance)}
                       size="small"
                     />
                  </TableCell>
                  <TableCell>{item.batchLotNumber}</TableCell>
                  <TableCell>
                    <Chip
                      label={itemStatusOptions.find(s => s.value === item.itemStatus)?.label}
                      color={getStatusColor(item.itemStatus)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {item.expiryDate && (
                      <Chip
                        label={new Date(item.expiryDate).toLocaleDateString()}
                        color={new Date(item.expiryDate) < new Date() ? 'error' : 'default'}
                        size="small"
                      />
                    )}
                  </TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleRemoveItem(item.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Alerts */}
        {summary.expiredItems > 0 && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {summary.expiredItems} items are expired and need immediate attention.
          </Alert>
        )}
        {summary.nearExpiryItems > 0 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            {summary.nearExpiryItems} items are near expiry date.
          </Alert>
        )}
        {summary.itemsWithVariance > 0 && (
          <Alert severity="info" sx={{ mb: 2 }}>
            {summary.itemsWithVariance} items have variances that need review.
          </Alert>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button
          startIcon={<DownloadIcon />}
          onClick={handleExportTemplate}
        >
          Export Template
        </Button>
        <Button
          startIcon={<UploadIcon />}
          component="label"
        >
          Import CSV
          <input
            type="file"
            hidden
            accept=".csv"
            onChange={handleFileUpload}
          />
        </Button>
        <Button
          startIcon={<SaveIcon />}
          onClick={handleSaveDraft}
          variant="outlined"
        >
          Save Draft
        </Button>
        <Button
          startIcon={<SendIcon />}
          onClick={handleSubmitCount}
          variant="contained"
          color="primary"
        >
          Submit Count
        </Button>
        <Button onClick={onClose}>
          Cancel
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default InventoryTakingPopup;
