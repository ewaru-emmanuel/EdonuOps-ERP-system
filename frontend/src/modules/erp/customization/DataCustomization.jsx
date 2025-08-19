import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { Add as AddIcon, Download as DownloadIcon, Upload as UploadIcon } from '@mui/icons-material';

const DataCustomization = () => {
  const [customFields, setCustomFields] = useState([
    { id: 1, name: 'Customer Priority', type: 'Select', entity: 'Customer', status: 'Active' },
    { id: 2, name: 'Product Category', type: 'Text', entity: 'Product', status: 'Active' },
    { id: 3, name: 'Order Source', type: 'Select', entity: 'Order', status: 'Inactive' }
  ]);

  const [openDialog, setOpenDialog] = useState(false);
  const [newField, setNewField] = useState({ name: '', type: '', entity: '' });

  const handleAddField = () => {
    if (newField.name && newField.type && newField.entity) {
      setCustomFields([...customFields, { ...newField, id: Date.now(), status: 'Active' }]);
      setNewField({ name: '', type: '', entity: '' });
      setOpenDialog(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Data Customization</Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Custom Fields</Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenDialog(true)}
                >
                  Add Field
                </Button>
              </Box>
              
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Field Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Entity</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {customFields.map((field) => (
                      <TableRow key={field.id}>
                        <TableCell>{field.name}</TableCell>
                        <TableCell>{field.type}</TableCell>
                        <TableCell>{field.entity}</TableCell>
                        <TableCell>
                          <Chip
                            label={field.status}
                            color={field.status === 'Active' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Data Import/Export</Typography>
              
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  fullWidth
                >
                  Export Customer Data
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  fullWidth
                >
                  Export Product Data
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  fullWidth
                >
                  Import Data
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Add Custom Field</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Field Name"
            value={newField.name}
            onChange={(e) => setNewField({ ...newField, name: e.target.value })}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Field Type</InputLabel>
            <Select
              value={newField.type}
              onChange={(e) => setNewField({ ...newField, type: e.target.value })}
            >
              <MenuItem value="Text">Text</MenuItem>
              <MenuItem value="Number">Number</MenuItem>
              <MenuItem value="Select">Select</MenuItem>
              <MenuItem value="Date">Date</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Entity</InputLabel>
            <Select
              value={newField.entity}
              onChange={(e) => setNewField({ ...newField, entity: e.target.value })}
            >
              <MenuItem value="Customer">Customer</MenuItem>
              <MenuItem value="Product">Product</MenuItem>
              <MenuItem value="Order">Order</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleAddField} variant="contained">Add Field</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataCustomization;


