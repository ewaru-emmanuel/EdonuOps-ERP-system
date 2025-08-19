import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Alert,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';

const TaxRatesManagement = () => {
  const [taxRates, setTaxRates] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRate, setEditingRate] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    rate: '',
    type: 'sales',
    jurisdiction: '',
    effectiveDate: '',
    description: ''
  });

  const taxTypes = [
    { value: 'sales', label: 'Sales Tax' },
    { value: 'vat', label: 'VAT' },
    { value: 'gst', label: 'GST' },
    { value: 'income', label: 'Income Tax' },
    { value: 'corporate', label: 'Corporate Tax' },
    { value: 'excise', label: 'Excise Tax' },
    { value: 'customs', label: 'Customs Duty' }
  ];

  const jurisdictions = [
    'Federal',
    'State',
    'County',
    'City',
    'Municipal',
    'International'
  ];

  useEffect(() => {
    fetchTaxRates();
  }, []);

  const fetchTaxRates = async () => {
    try {
      // TODO: Replace with actual API call
      const mockRates = [
        {
          id: 1,
          name: 'California Sales Tax',
          rate: 7.25,
          type: 'sales',
          jurisdiction: 'State',
          effectiveDate: '2024-01-01',
          description: 'Standard California state sales tax',
          isActive: true
        },
        {
          id: 2,
          name: 'Federal Corporate Tax',
          rate: 21.0,
          type: 'corporate',
          jurisdiction: 'Federal',
          effectiveDate: '2018-01-01',
          description: 'Federal corporate income tax rate',
          isActive: true
        },
        {
          id: 3,
          name: 'New York City Sales Tax',
          rate: 8.875,
          type: 'sales',
          jurisdiction: 'City',
          effectiveDate: '2024-01-01',
          description: 'Combined NYC sales tax rate',
          isActive: true
        }
      ];
      setTaxRates(mockRates);
    } catch (error) {
      console.error('Error fetching tax rates:', error);
    }
  };

  const handleOpenDialog = (rate = null) => {
    if (rate) {
      setEditingRate(rate);
      setFormData({
        name: rate.name,
        rate: rate.rate.toString(),
        type: rate.type,
        jurisdiction: rate.jurisdiction,
        effectiveDate: rate.effectiveDate,
        description: rate.description
      });
    } else {
      setEditingRate(null);
      setFormData({
        name: '',
        rate: '',
        type: 'sales',
        jurisdiction: '',
        effectiveDate: '',
        description: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingRate(null);
    setFormData({
      name: '',
      rate: '',
      type: 'sales',
      jurisdiction: '',
      effectiveDate: '',
      description: ''
    });
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    try {
      if (editingRate) {
        // Update existing rate
        const updatedRates = taxRates.map(rate =>
          rate.id === editingRate.id
            ? { ...rate, ...formData, rate: parseFloat(formData.rate) }
            : rate
        );
        setTaxRates(updatedRates);
      } else {
        // Add new rate
        const newRate = {
          id: Date.now(),
          ...formData,
          rate: parseFloat(formData.rate),
          isActive: true
        };
        setTaxRates(prev => [...prev, newRate]);
      }
      handleCloseDialog();
    } catch (error) {
      console.error('Error saving tax rate:', error);
    }
  };

  const handleDelete = async (id) => {
    try {
      setTaxRates(prev => prev.filter(rate => rate.id !== id));
    } catch (error) {
      console.error('Error deleting tax rate:', error);
    }
  };

  const getTaxTypeColor = (type) => {
    const colors = {
      sales: 'primary',
      vat: 'secondary',
      gst: 'success',
      income: 'warning',
      corporate: 'error',
      excise: 'info',
      customs: 'default'
    };
    return colors[type] || 'default';
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2" sx={{ fontWeight: 'bold' }}>
          Tax Rates Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
          sx={{ borderRadius: 2 }}
        >
          Add Tax Rate
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Tax Rates
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold' }}>
                {taxRates.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Active Rates
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'success.main' }}>
                {taxRates.filter(rate => rate.isActive).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Sales Tax Rates
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                {taxRates.filter(rate => rate.type === 'sales').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Average Rate
              </Typography>
              <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color: 'info.main' }}>
                {(taxRates.reduce((sum, rate) => sum + rate.rate, 0) / taxRates.length || 0).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <TableContainer component={Paper} elevation={2}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: 'primary.main' }}>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Tax Name</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Rate (%)</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Type</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Jurisdiction</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Effective Date</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ color: 'white', fontWeight: 'bold' }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {taxRates.map((rate) => (
              <TableRow key={rate.id} hover>
                <TableCell>
                  <Box>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      {rate.name}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      {rate.description}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {rate.rate}%
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={taxTypes.find(t => t.value === rate.type)?.label || rate.type}
                    color={getTaxTypeColor(rate.type)}
                    size="small"
                    sx={{ textTransform: 'capitalize' }}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={rate.jurisdiction}
                    variant="outlined"
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    {new Date(rate.effectiveDate).toLocaleDateString()}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={rate.isActive ? 'Active' : 'Inactive'}
                    color={rate.isActive ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <IconButton
                      size="small"
                      onClick={() => handleOpenDialog(rate)}
                      sx={{ color: 'primary.main' }}
                    >
                      <EditIcon />
                    </IconButton>
                    <IconButton
                      size="small"
                      onClick={() => handleDelete(rate.id)}
                      sx={{ color: 'error.main' }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add/Edit Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingRate ? 'Edit Tax Rate' : 'Add New Tax Rate'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Tax Name"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Rate (%)"
                type="number"
                value={formData.rate}
                onChange={(e) => handleInputChange('rate', e.target.value)}
                required
                inputProps={{ step: 0.01, min: 0, max: 100 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Tax Type</InputLabel>
                <Select
                  value={formData.type}
                  onChange={(e) => handleInputChange('type', e.target.value)}
                  label="Tax Type"
                >
                  {taxTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Jurisdiction</InputLabel>
                <Select
                  value={formData.jurisdiction}
                  onChange={(e) => handleInputChange('jurisdiction', e.target.value)}
                  label="Jurisdiction"
                >
                  {jurisdictions.map((jurisdiction) => (
                    <MenuItem key={jurisdiction} value={jurisdiction}>
                      {jurisdiction}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Effective Date"
                type="date"
                value={formData.effectiveDate}
                onChange={(e) => handleInputChange('effectiveDate', e.target.value)}
                required
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={3}
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog} startIcon={<CancelIcon />}>
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            startIcon={<SaveIcon />}
            disabled={!formData.name || !formData.rate || !formData.jurisdiction}
          >
            {editingRate ? 'Update' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TaxRatesManagement;




