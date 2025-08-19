import React, { useState } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Typography,
  Paper,
  Container,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Avatar,
  Alert,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  useTheme
} from '@mui/material';
import {
  Build as ManufacturingIcon,
  Inventory as InventoryIcon,
  Timeline as PlanningIcon,
  CheckCircle as QualityIcon,
  Engineering as EquipmentIcon,
  LocalShipping as SupplyChainIcon,
  Assessment as AnalyticsIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  Speed as PerformanceIcon
} from '@mui/icons-material';

// Import sub-components
import BOMManagement from './BOMManagement';
import ProductionPlanning from './ProductionPlanning';
import WorkCenterManagement from './WorkCenterManagement';
import QualityControl from './QualityControl';
import EquipmentMaintenance from './EquipmentMaintenance';
import SupplyChainManagement from './SupplyChainManagement';
import ManufacturingAnalytics from './ManufacturingAnalytics';

const ManufacturingModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const theme = useTheme();

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Mock data for manufacturing metrics
  const manufacturingMetrics = [
    {
      title: "Production Efficiency",
      value: "94.2%",
      trend: "+2.1%",
      color: "success",
      icon: <PerformanceIcon />
    },
    {
      title: "Quality Rate",
      value: "99.1%",
      trend: "+0.3%",
      color: "success",
      icon: <QualityIcon />
    },
    {
      title: "Equipment Uptime",
      value: "96.8%",
      trend: "+1.2%",
      color: "success",
      icon: <EquipmentIcon />
    },
    {
      title: "On-Time Delivery",
      value: "97.5%",
      trend: "+0.8%",
      color: "success",
      icon: <ScheduleIcon />
    }
  ];

  // Mock data for production orders
  const productionOrders = [
    {
      id: "PO-001",
      product: "Premium Widget",
      quantity: 1000,
      status: "In Progress",
      startDate: "2024-01-15",
      endDate: "2024-01-20",
      progress: 65,
      priority: "High"
    },
    {
      id: "PO-002",
      product: "Standard Component",
      quantity: 500,
      status: "Planned",
      startDate: "2024-01-22",
      endDate: "2024-01-25",
      progress: 0,
      priority: "Medium"
    },
    {
      id: "PO-003",
      product: "Custom Assembly",
      quantity: 200,
      status: "Completed",
      startDate: "2024-01-10",
      endDate: "2024-01-12",
      progress: 100,
      priority: "Low"
    }
  ];

  const tabs = [
    {
      label: 'Bill of Materials',
      icon: <InventoryIcon />,
      component: <BOMManagement />,
      description: 'Manage product structures and component relationships'
    },
    {
      label: 'Production Planning',
      icon: <PlanningIcon />,
      component: <ProductionPlanning />,
      description: 'MRP II planning and production scheduling'
    },
    {
      label: 'Work Centers',
      icon: <ManufacturingIcon />,
      component: <WorkCenterManagement />,
      description: 'Manage production work centers and capacity'
    },
    {
      label: 'Quality Control',
      icon: <QualityIcon />,
      component: <QualityControl />,
      description: 'Quality assurance and inspection management'
    },
    {
      label: 'Equipment & Maintenance',
      icon: <EquipmentIcon />,
      component: <EquipmentMaintenance />,
      description: 'Equipment tracking and preventive maintenance'
    },
    {
      label: 'Supply Chain',
      icon: <SupplyChainIcon />,
      component: <SupplyChainManagement />,
      description: 'Supply chain orchestration and logistics'
    },
    {
      label: 'Analytics',
      icon: <AnalyticsIcon />,
      component: <ManufacturingAnalytics />,
      description: 'Manufacturing performance analytics and insights'
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Completed': return 'success';
      case 'In Progress': return 'warning';
      case 'Planned': return 'info';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High': return 'error';
      case 'Medium': return 'warning';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 3 }}>
      {/* Manufacturing Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
            <ManufacturingIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
              Manufacturing & Supply Chain Management
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Advanced MRP II, Production Planning, Quality Control & Supply Chain Orchestration
            </Typography>
          </Box>
        </Box>
        
        {/* Status Banner */}
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            🏭 Advanced Manufacturing Suite Active
          </Typography>
          <Typography variant="body2">
            Complete manufacturing management with MRP II, quality control, equipment maintenance, and supply chain orchestration.
          </Typography>
        </Alert>
      </Box>

      {/* Manufacturing Metrics */}
      <Paper elevation={3} sx={{ borderRadius: 2, p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
          <TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Manufacturing Performance Metrics
        </Typography>
        
        <Grid container spacing={3}>
          {manufacturingMetrics.map((metric, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card elevation={2}>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={2} mb={2}>
                    <Avatar sx={{ bgcolor: `${metric.color}.main` }}>
                      {metric.icon}
                    </Avatar>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {metric.value}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {metric.title}
                      </Typography>
                    </Box>
                  </Box>
                  <Chip 
                    label={metric.trend} 
                    color={metric.color} 
                    size="small" 
                    icon={<TrendingUpIcon />}
                  />
                  <LinearProgress 
                    variant="determinate" 
                    value={parseInt(metric.value)} 
                    sx={{ mt: 1 }} 
                    color={metric.color}
                  />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {/* Production Orders Overview */}
      <Paper elevation={3} sx={{ borderRadius: 2, p: 3, mb: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            <ScheduleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Active Production Orders
          </Typography>
                     <Button variant="contained" startIcon={<AddIcon />} disabled>
             New Production Order
           </Button>
        </Box>
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Order ID</TableCell>
                <TableCell>Product</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Progress</TableCell>
                <TableCell>Priority</TableCell>
                <TableCell>Timeline</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {productionOrders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      {order.id}
                    </Typography>
                  </TableCell>
                  <TableCell>{order.product}</TableCell>
                  <TableCell>{order.quantity.toLocaleString()}</TableCell>
                  <TableCell>
                    <Chip 
                      label={order.status} 
                      color={getStatusColor(order.status)} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LinearProgress 
                        variant="determinate" 
                        value={order.progress} 
                        sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                      />
                      <Typography variant="body2">
                        {order.progress}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={order.priority} 
                      color={getPriorityColor(order.priority)} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {order.startDate} - {order.endDate}
                    </Typography>
                  </TableCell>
                                     <TableCell>
                     <IconButton size="small" color="primary" disabled>
                       <ViewIcon />
                     </IconButton>
                     <IconButton size="small" color="primary" disabled>
                       <EditIcon />
                     </IconButton>
                   </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Main Manufacturing Interface */}
      <Paper elevation={3} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                minHeight: 64,
                fontSize: '0.875rem',
                fontWeight: 500,
                textTransform: 'none',
                '&.Mui-selected': {
                  color: theme.palette.primary.main,
                  fontWeight: 600
                }
              }
            }}
          >
            {tabs.map((tab, index) => (
              <Tab
                key={index}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {tab.icon}
                    {tab.label}
                  </Box>
                }
                sx={{ minWidth: 'auto', px: 3 }}
              />
            ))}
          </Tabs>
        </Box>

        <Box sx={{ p: 3, minHeight: '60vh' }}>
          {/* Module Description */}
          <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
            <Typography variant="h6" gutterBottom>
              {tabs[activeTab].label}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {tabs[activeTab].description}
            </Typography>
          </Box>
          
          {/* Module Component */}
          {tabs[activeTab].component}
        </Box>
      </Paper>

      {/* Manufacturing Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          Advanced Manufacturing Suite - MRP II, Quality Control & Supply Chain Management
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="MRP II Certified" size="small" sx={{ mr: 1 }} />
          <Chip label="ISO 9001" size="small" sx={{ mr: 1 }} />
          <Chip label="Six Sigma Ready" size="small" sx={{ mr: 1 }} />
          <Chip label="Enterprise Grade" size="small" color="primary" />
        </Box>
      </Box>
    </Container>
  );
};

export default ManufacturingModule;
