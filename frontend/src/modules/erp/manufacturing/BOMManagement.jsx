import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress
} from '@mui/material';
import {
  Inventory as InventoryIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  AccountTree as TreeIcon,
  AccountTree as BOMIcon,
  AttachMoney as CostIcon
} from '@mui/icons-material';

const BOMManagement = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedBOM, setSelectedBOM] = useState(null);
  
  const showSnackbar = (message, severity = 'success') => {
    // For now, just log to console. In a real app, this would show a snackbar
    console.log(`${severity.toUpperCase()}: ${message}`);
  };

  // Mock data for BOMs
  const boms = [
    {
      id: "BOM-001",
      name: "Premium Widget Assembly",
      product: "Premium Widget",
      version: "2.1",
      status: "Active",
      components: 15,
      totalCost: 245.50,
      lastUpdated: "2024-01-15",
      complexity: "High"
    },
    {
      id: "BOM-002",
      name: "Standard Component Kit",
      product: "Standard Component",
      version: "1.5",
      status: "Active",
      components: 8,
      totalCost: 89.25,
      lastUpdated: "2024-01-10",
      complexity: "Medium"
    },
    {
      id: "BOM-003",
      name: "Custom Assembly Package",
      product: "Custom Assembly",
      version: "1.0",
      status: "Draft",
      components: 12,
      totalCost: 156.75,
      lastUpdated: "2024-01-12",
      complexity: "High"
    }
  ];

  // Mock data for BOM components
  const bomComponents = [
    {
      id: "COMP-001",
      name: "Main Housing",
      partNumber: "MH-001",
      quantity: 1,
      unitCost: 45.00,
      supplier: "MetalWorks Inc",
      leadTime: 5,
      stock: 150
    },
    {
      id: "COMP-002",
      name: "Circuit Board",
      partNumber: "CB-002",
      quantity: 1,
      unitCost: 32.50,
      supplier: "ElectroTech",
      leadTime: 3,
      stock: 200
    },
    {
      id: "COMP-003",
      name: "Display Screen",
      partNumber: "DS-003",
      quantity: 1,
      unitCost: 28.00,
      supplier: "DisplayPro",
      leadTime: 7,
      stock: 75
    },
    {
      id: "COMP-004",
      name: "Battery Pack",
      partNumber: "BP-004",
      quantity: 1,
      unitCost: 18.75,
      supplier: "PowerCell",
      leadTime: 4,
      stock: 120
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return 'success';
      case 'Draft': return 'warning';
      case 'Deprecated': return 'error';
      default: return 'default';
    }
  };

  const getComplexityColor = (complexity) => {
    switch (complexity) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  const handleViewBOM = (bom) => {
    setSelectedBOM(bom);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedBOM(null);
  };

  return (
    <Box>
      {/* BOM Overview Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <BOMIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {boms.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active BOMs
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <InventoryIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    {bomComponents.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Components
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <CostIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    $491.50
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Cost
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <TreeIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                    3
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Versions
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* BOM List */}
      <Paper elevation={3} sx={{ borderRadius: 2, p: 3, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            <BOMIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Bill of Materials
          </Typography>
                     <Button variant="contained" startIcon={<AddIcon />} onClick={() => showSnackbar('Create new BOM form would open here')}>
             Create New BOM
           </Button>
        </Box>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>BOM ID</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Product</TableCell>
                <TableCell>Version</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Components</TableCell>
                <TableCell>Total Cost</TableCell>
                <TableCell>Complexity</TableCell>
                <TableCell>Last Updated</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {boms.map((bom) => (
                <TableRow key={bom.id}>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      {bom.id}
                    </Typography>
                  </TableCell>
                  <TableCell>{bom.name}</TableCell>
                  <TableCell>{bom.product}</TableCell>
                  <TableCell>{bom.version}</TableCell>
                  <TableCell>
                    <Chip 
                      label={bom.status} 
                      color={getStatusColor(bom.status)} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{bom.components}</TableCell>
                  <TableCell>${bom.totalCost.toFixed(2)}</TableCell>
                  <TableCell>
                    <Chip 
                      label={bom.complexity} 
                      color={getComplexityColor(bom.complexity)} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{bom.lastUpdated}</TableCell>
                  <TableCell>
                    <IconButton size="small" color="primary" onClick={() => handleViewBOM(bom)}>
                      <ViewIcon />
                    </IconButton>
                                         <IconButton size="small" color="primary" onClick={() => showSnackbar(`Edit BOM ${bom.id} form would open here`)}>
                       <EditIcon />
                     </IconButton>
                     <IconButton size="small" color="error" onClick={() => showSnackbar(`Delete BOM ${bom.id} confirmation dialog would open here`)}>
                       <DeleteIcon />
                     </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* BOM Components */}
      <Paper elevation={3} sx={{ borderRadius: 2, p: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          <InventoryIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          BOM Components Overview
        </Typography>
        
        <Grid container spacing={3}>
          {bomComponents.map((component) => (
            <Grid item xs={12} md={6} key={component.id}>
              <Card elevation={2}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                        {component.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Part: {component.partNumber}
                      </Typography>
                    </Box>
                    <Chip 
                      label={`Qty: ${component.quantity}`} 
                      color="primary" 
                      size="small" 
                    />
                  </Box>
                  
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Unit Cost
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                        ${component.unitCost.toFixed(2)}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Lead Time
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                        {component.leadTime} days
                      </Typography>
                    </Grid>
                  </Grid>
                  
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="body2" color="text.secondary">
                      Stock: {component.stock} units
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Supplier: {component.supplier}
                    </Typography>
                  </Box>
                  
                  <LinearProgress 
                    variant="determinate" 
                    value={(component.stock / 200) * 100} 
                    sx={{ mt: 1 }} 
                    color={component.stock < 50 ? 'error' : 'success'}
                  />
                </CardContent>
                                 <CardActions>
                   <Button size="small" startIcon={<EditIcon />} onClick={() => showSnackbar(`Edit component ${component.name} form would open here`)}>
                     Edit
                   </Button>
                   <Button size="small" startIcon={<ViewIcon />} onClick={() => showSnackbar(`View component ${component.name} details would open here`)}>
                     Details
                   </Button>
                 </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* BOM Detail Dialog */}
      <Dialog 
        open={openDialog} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <BOMIcon />
            <Typography variant="h6">
              {selectedBOM?.name} - BOM Details
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedBOM && (
            <Box>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    BOM ID
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                    {selectedBOM.id}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Version
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                    {selectedBOM.version}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip 
                    label={selectedBOM.status} 
                    color={getStatusColor(selectedBOM.status)} 
                    size="small" 
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Cost
                  </Typography>
                  <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                    ${selectedBOM.totalCost.toFixed(2)}
                  </Typography>
                </Grid>
              </Grid>
              
              <Typography variant="h6" gutterBottom>
                Components ({selectedBOM.components})
              </Typography>
              
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Component</TableCell>
                      <TableCell>Part Number</TableCell>
                      <TableCell>Quantity</TableCell>
                      <TableCell>Unit Cost</TableCell>
                      <TableCell>Total Cost</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {bomComponents.slice(0, 4).map((component) => (
                      <TableRow key={component.id}>
                        <TableCell>{component.name}</TableCell>
                        <TableCell>{component.partNumber}</TableCell>
                        <TableCell>{component.quantity}</TableCell>
                        <TableCell>${component.unitCost.toFixed(2)}</TableCell>
                        <TableCell>${(component.quantity * component.unitCost).toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
                 <DialogActions>
           <Button onClick={handleCloseDialog}>Close</Button>
           <Button variant="contained" startIcon={<EditIcon />} onClick={() => showSnackbar(`Edit BOM ${selectedBOM?.id} form would open here`)}>
             Edit BOM
           </Button>
         </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BOMManagement;
