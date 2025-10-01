import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography,
  Table, TableBody, TableCell, TableHead, TableRow, Paper, Alert, LinearProgress,
  IconButton, Tooltip, Chip, TextField, FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import {
  Upload, CheckCircle, Error, Warning, Delete, Edit, Save, Cancel
} from '@mui/icons-material';

const CSVImportDialog = ({ open, onClose, onImport, bankAccountId }) => {
  const [csvData, setCsvData] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [mapping, setMapping] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [previewData, setPreviewData] = useState([]);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const csv = e.target.result;
        const lines = csv.split('\n').filter(line => line.trim());
        
        if (lines.length < 2) {
          setError('CSV file must have at least a header row and one data row');
          setLoading(false);
          return;
        }

        // Parse headers
        const headerRow = lines[0].split(',').map(h => h.trim().toLowerCase());
        setHeaders(headerRow);

        // Parse data rows
        const dataRows = lines.slice(1).map((line, index) => {
          const values = line.split(',').map(v => v.trim());
          return {
            id: index,
            raw: values,
            date: values[0] || '',
            amount: parseFloat(values[1]) || 0,
            description: values[2] || '',
            reference: values[3] || '',
            status: 'pending'
          };
        });

        setCsvData(dataRows);
        setPreviewData(dataRows.slice(0, 10)); // Show first 10 rows for preview
        
        // Auto-map common column names
        const autoMapping = {};
        headerRow.forEach((header, index) => {
          if (header.includes('date')) autoMapping.date = index;
          if (header.includes('amount') || header.includes('value')) autoMapping.amount = index;
          if (header.includes('description') || header.includes('memo')) autoMapping.description = index;
          if (header.includes('reference') || header.includes('ref')) autoMapping.reference = index;
        });
        setMapping(autoMapping);

      } catch (err) {
        setError('Error parsing CSV file: ' + err.message);
      } finally {
        setLoading(false);
      }
    };

    reader.readAsText(file);
  };

  const handleMappingChange = (field, columnIndex) => {
    setMapping(prev => ({
      ...prev,
      [field]: columnIndex
    }));
  };

  const handleDataEdit = (id, field, value) => {
    setCsvData(prev => prev.map(row => 
      row.id === id ? { ...row, [field]: value } : row
    ));
    setPreviewData(prev => prev.map(row => 
      row.id === id ? { ...row, [field]: value } : row
    ));
  };

  const handleImport = () => {
    const processedData = csvData.map(row => ({
      bank_account_id: bankAccountId,
      transaction_date: row.date,
      amount: row.amount,
      description: row.description,
      reference: row.reference
    }));

    onImport(processedData);
    onClose();
  };

  const handleClose = () => {
    setCsvData([]);
    setHeaders([]);
    setMapping({});
    setPreviewData([]);
    setError(null);
    onClose();
  };

  const getColumnOptions = () => {
    return headers.map((header, index) => (
      <MenuItem key={index} value={index}>
        Column {index + 1}: {header}
      </MenuItem>
    ));
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <Upload color="primary" />
          <Typography variant="h6">Import Bank Statement CSV</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {csvData.length === 0 ? (
          <Box>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
              id="csv-upload"
            />
            <label htmlFor="csv-upload">
              <Button 
                variant="outlined" 
                component="span" 
                startIcon={<Upload />}
                fullWidth
                sx={{ py: 3 }}
              >
                Choose CSV File
              </Button>
            </label>
            <Typography variant="caption" display="block" color="text.secondary" sx={{ mt: 2, textAlign: 'center' }}>
              Expected format: Date, Amount, Description, Reference
            </Typography>
          </Box>
        ) : (
          <Box>
            <Typography variant="h6" gutterBottom>
              Column Mapping
            </Typography>
            <Box display="flex" gap={2} mb={3}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Date</InputLabel>
                <Select
                  value={mapping.date || ''}
                  onChange={(e) => handleMappingChange('date', e.target.value)}
                >
                  {getColumnOptions()}
                </Select>
              </FormControl>
              
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Amount</InputLabel>
                <Select
                  value={mapping.amount || ''}
                  onChange={(e) => handleMappingChange('amount', e.target.value)}
                >
                  {getColumnOptions()}
                </Select>
              </FormControl>
              
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Description</InputLabel>
                <Select
                  value={mapping.description || ''}
                  onChange={(e) => handleMappingChange('description', e.target.value)}
                >
                  {getColumnOptions()}
                </Select>
              </FormControl>
              
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <InputLabel>Reference</InputLabel>
                <Select
                  value={mapping.reference || ''}
                  onChange={(e) => handleMappingChange('reference', e.target.value)}
                >
                  {getColumnOptions()}
                </Select>
              </FormControl>
            </Box>

            <Typography variant="h6" gutterBottom>
              Data Preview ({csvData.length} transactions)
            </Typography>
            
            <Paper sx={{ maxHeight: 400, overflow: 'auto' }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Reference</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {previewData.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell>
                        <TextField
                          size="small"
                          value={row.date}
                          onChange={(e) => handleDataEdit(row.id, 'date', e.target.value)}
                          type="date"
                          InputLabelProps={{ shrink: true }}
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          value={row.amount}
                          onChange={(e) => handleDataEdit(row.id, 'amount', parseFloat(e.target.value) || 0)}
                          type="number"
                          InputProps={{ startAdornment: '$' }}
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          value={row.description}
                          onChange={(e) => handleDataEdit(row.id, 'description', e.target.value)}
                          fullWidth
                        />
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          value={row.reference}
                          onChange={(e) => handleDataEdit(row.id, 'reference', e.target.value)}
                        />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={row.status} 
                          size="small" 
                          color={row.status === 'pending' ? 'warning' : 'success'}
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Delete">
                          <IconButton 
                            size="small"
                            onClick={() => {
                              setCsvData(prev => prev.filter(r => r.id !== row.id));
                              setPreviewData(prev => prev.filter(r => r.id !== row.id));
                            }}
                          >
                            <Delete />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Paper>
            
            {csvData.length > 10 && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                Showing first 10 rows of {csvData.length} total transactions
              </Typography>
            )}
          </Box>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        {csvData.length > 0 && (
          <Button 
            variant="contained" 
            onClick={handleImport}
            startIcon={<CheckCircle />}
          >
            Import {csvData.length} Transactions
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CSVImportDialog;










