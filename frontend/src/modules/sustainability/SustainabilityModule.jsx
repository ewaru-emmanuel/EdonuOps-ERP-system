import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Tabs,
  Tab,
  Chip,
  Paper,
  Alert,
  LinearProgress,
  Avatar,
  Snackbar
} from '@mui/material';
import {
  Nature as NatureIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  People as PeopleIcon,
  Business as BusinessIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';

const SustainabilityModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [formOpen, setFormOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [formType, setFormType] = useState('');

  // Real-time data hooks
  const { 
    data: environmentalMetrics, 
    loading: environmentalLoading, 
    create: createEnvironmentalMetric,
    update: updateEnvironmentalMetric,
    remove: deleteEnvironmentalMetric
  } = useRealTimeData('/api/sustainability/environmental');

  const { 
    data: socialMetrics, 
    loading: socialLoading, 
    create: createSocialMetric,
    update: updateSocialMetric,
    remove: deleteSocialMetric
  } = useRealTimeData('/api/sustainability/social');

  const { 
    data: governanceMetrics, 
    loading: governanceLoading, 
    create: createGovernanceMetric,
    update: updateGovernanceMetric,
    remove: deleteGovernanceMetric
  } = useRealTimeData('/api/sustainability/governance');

  const { 
    data: esgReports, 
    loading: reportsLoading, 
    create: createESGReport,
    update: updateESGReport,
    remove: deleteESGReport
  } = useRealTimeData('/api/sustainability/reports');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleAdd = (type) => {
    setFormType(type);
    setSelectedItem(null);
    setFormOpen(true);
  };

  const handleEdit = (item, type) => {
    setFormType(type);
    setSelectedItem(item);
    setFormOpen(true);
  };

  const handleView = (item, type) => {
    setFormType(type);
    setSelectedItem(item);
    setDetailOpen(true);
  };

  const handleDelete = async (item, type) => {
    const confirmed = window.confirm(`Are you sure you want to delete this ${type}?`);
    if (confirmed) {
      try {
        let deleteFunction;
        switch (type) {
          case 'environmental':
            deleteFunction = deleteEnvironmentalMetric;
            break;
          case 'social':
            deleteFunction = deleteSocialMetric;
            break;
          case 'governance':
            deleteFunction = deleteGovernanceMetric;
            break;
          case 'report':
            deleteFunction = deleteESGReport;
            break;
          default:
            return;
        }
        await deleteFunction(item.id);
        showSnackbar(`${type.charAt(0).toUpperCase() + type.slice(1)} metric deleted successfully`);
      } catch (error) {
        showSnackbar(`Error deleting ${type} metric`, 'error');
      }
    }
  };

  // Calculate metrics from real data
  const sustainabilityMetrics = {
    carbonFootprint: environmentalMetrics?.find(m => m.metric_name === 'Carbon Footprint')?.value || 0,
    energyEfficiency: environmentalMetrics?.find(m => m.metric_name === 'Energy Efficiency')?.value || 0,
    wasteReduction: environmentalMetrics?.find(m => m.metric_name === 'Waste Reduction')?.value || 0,
    socialImpact: socialMetrics?.reduce((sum, m) => sum + (m.value || 0), 0) / (socialMetrics?.length || 1),
    governanceScore: governanceMetrics?.reduce((sum, m) => sum + (m.value || 0), 0) / (governanceMetrics?.length || 1),
    esgRating: esgReports?.length > 0 ? esgReports[0].esg_rating || 'N/A' : 'N/A'
  };

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Avatar sx={{ bgcolor: 'success.main', width: 56, height: 56 }}>
            <NatureIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
              Sustainability & ESG Management
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Track environmental, social, and governance metrics for sustainable business practices
            </Typography>
          </Box>
        </Box>
        
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            ✅ ESG Platform Operational
          </Typography>
          <Typography variant="body2">
            Your sustainability and ESG management system is fully operational with comprehensive tracking and reporting capabilities.
          </Typography>
        </Alert>
      </Box>

      {/* ESG Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="success.main" sx={{ fontWeight: 'bold' }}>
                    {sustainabilityMetrics.esgRating}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    ESG Rating
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <CheckCircleIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={85} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {sustainabilityMetrics.carbonFootprint}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Carbon Footprint (tons CO2)
                  </Typography>
                </Box>
                                 <Avatar sx={{ bgcolor: 'primary.main' }}>
                   <NatureIcon />
                 </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={65} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {sustainabilityMetrics.energyEfficiency}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Energy Efficiency
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <TrendingUpIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={sustainabilityMetrics.energyEfficiency} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {sustainabilityMetrics.wasteReduction}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Waste Reduction
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <AssessmentIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={sustainabilityMetrics.wasteReduction} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Interface */}
      <Paper elevation={3} sx={{ borderRadius: 2, overflow: 'hidden' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', bgcolor: 'background.paper' }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
                         <Tab label="Environmental" icon={<NatureIcon />} />
            <Tab label="Social" icon={<PeopleIcon />} />
            <Tab label="Governance" icon={<BusinessIcon />} />
            <Tab label="Reporting" icon={<AssessmentIcon />} />
          </Tabs>
        </Box>

        <Box sx={{ p: 3, minHeight: '60vh' }}>
          {/* Environmental Tab */}
          {activeTab === 0 && (
            <Box>
              <Typography variant="h5" gutterBottom>Environmental Metrics</Typography>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Track carbon emissions, energy consumption, waste management, and environmental impact metrics.
                </Typography>
              </Alert>
                             <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                 <Button
                   variant="contained"
                   onClick={() => handleAdd('environmental')}
                 >
                   Add Environmental Metric
                 </Button>
                 <Button
                   variant="outlined"
                   onClick={() => handleView(environmentalMetrics?.[0], 'environmental')}
                   disabled={!environmentalMetrics || environmentalMetrics.length === 0}
                 >
                   View Environmental Data
                 </Button>
               </Box>
            </Box>
          )}

          {/* Social Tab */}
          {activeTab === 1 && (
            <Box>
              <Typography variant="h5" gutterBottom>Social Impact</Typography>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Monitor social responsibility, community engagement, employee well-being, and diversity metrics.
                </Typography>
              </Alert>
                             <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                 <Button
                   variant="contained"
                   onClick={() => handleAdd('social')}
                 >
                   Add Social Metric
                 </Button>
                 <Button
                   variant="outlined"
                   onClick={() => handleView(socialMetrics?.[0], 'social')}
                   disabled={!socialMetrics || socialMetrics.length === 0}
                 >
                   View Social Data
                 </Button>
               </Box>
            </Box>
          )}

          {/* Governance Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h5" gutterBottom>Governance</Typography>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Track corporate governance, compliance, ethics, and board effectiveness metrics.
                </Typography>
              </Alert>
                             <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                 <Button
                   variant="contained"
                   onClick={() => handleAdd('governance')}
                 >
                   Add Governance Metric
                 </Button>
                 <Button
                   variant="outlined"
                   onClick={() => handleView(governanceMetrics?.[0], 'governance')}
                   disabled={!governanceMetrics || governanceMetrics.length === 0}
                 >
                   View Governance Data
                 </Button>
               </Box>
            </Box>
          )}

          {/* Reporting Tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h5" gutterBottom>ESG Reporting</Typography>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Generate comprehensive ESG reports, sustainability disclosures, and compliance documentation.
                </Typography>
              </Alert>
                             <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                 <Button
                   variant="contained"
                   onClick={() => handleAdd('report')}
                 >
                   Create ESG Report
                 </Button>
                 <Button
                   variant="outlined"
                   onClick={() => handleView(esgReports?.[0], 'report')}
                   disabled={!esgReports || esgReports.length === 0}
                 >
                   View ESG Reports
                 </Button>
               </Box>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          EdonuOps Sustainability & ESG - Comprehensive ESG Management Platform
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="Environmental Tracking" size="small" sx={{ mr: 1 }} />
          <Chip label="Social Impact" size="small" sx={{ mr: 1 }} />
          <Chip label="Governance Compliance" size="small" color="success" />
        </Box>
      </Box>

             {/* Form Modal */}
       <ImprovedForm
         open={formOpen}
         onClose={() => setFormOpen(false)}
         type={formType}
         data={selectedItem}
         onSubmit={async (formData) => {
           try {
             let createFunction, updateFunction;
             switch (formType) {
               case 'environmental':
                 createFunction = createEnvironmentalMetric;
                 updateFunction = updateEnvironmentalMetric;
                 break;
               case 'social':
                 createFunction = createSocialMetric;
                 updateFunction = updateSocialMetric;
                 break;
               case 'governance':
                 createFunction = createGovernanceMetric;
                 updateFunction = updateGovernanceMetric;
                 break;
               case 'report':
                 createFunction = createESGReport;
                 updateFunction = updateESGReport;
                 break;
               default:
                 return;
             }
             
             if (selectedItem) {
               await updateFunction(selectedItem.id, formData);
               showSnackbar(`${formType.charAt(0).toUpperCase() + formType.slice(1)} metric updated successfully`);
             } else {
               await createFunction(formData);
               showSnackbar(`${formType.charAt(0).toUpperCase() + formType.slice(1)} metric created successfully`);
             }
             setFormOpen(false);
           } catch (error) {
             showSnackbar(`Error ${selectedItem ? 'updating' : 'creating'} ${formType} metric`, 'error');
           }
         }}
       />

       {/* Detail View Modal */}
       <DetailViewModal
         open={detailOpen}
         onClose={() => setDetailOpen(false)}
         type={formType}
         data={selectedItem}
         onEdit={() => {
           setDetailOpen(false);
           setFormOpen(true);
         }}
       />

       {/* Snackbar for notifications */}
       <Snackbar
         open={snackbar.open}
         autoHideDuration={6000}
         onClose={() => setSnackbar({ ...snackbar, open: false })}
       >
         <Alert 
           onClose={() => setSnackbar({ ...snackbar, open: false })} 
           severity={snackbar.severity}
         >
           {snackbar.message}
         </Alert>
       </Snackbar>
     </Container>
   );
 };

export default SustainabilityModule;
