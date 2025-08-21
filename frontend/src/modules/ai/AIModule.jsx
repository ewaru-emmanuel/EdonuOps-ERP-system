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
  Psychology as PsychologyIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  Chat as ChatIcon,
  Lightbulb as LightbulbIcon,
  Analytics as AnalyticsIcon,
  AutoGraph as AutoGraphIcon
} from '@mui/icons-material';
import { AIErrorDialog } from '../../components/CommonForms';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';

const AIModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [aiErrorOpen, setAiErrorOpen] = useState(false);
  const [aiFeature, setAiFeature] = useState('');
  const [formOpen, setFormOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [formType, setFormType] = useState('');

  // Real-time data hooks
  const { 
    data: predictions, 
    loading: predictionsLoading, 
    create: createPrediction,
    update: updatePrediction,
    remove: deletePrediction
  } = useRealTimeData('/api/ai/predictions');

  const { 
    data: insights, 
    loading: insightsLoading, 
    create: createInsight,
    update: updateInsight,
    remove: deleteInsight
  } = useRealTimeData('/api/ai/insights');

  const { 
    data: recommendations, 
    loading: recommendationsLoading, 
    create: createRecommendation,
    update: updateRecommendation,
    remove: deleteRecommendation
  } = useRealTimeData('/api/ai/recommendations');

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleAIError = (feature) => {
    setAiFeature(feature);
    setAiErrorOpen(true);
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
          case 'prediction':
            deleteFunction = deletePrediction;
            break;
          case 'insight':
            deleteFunction = deleteInsight;
            break;
          case 'recommendation':
            deleteFunction = deleteRecommendation;
            break;
          default:
            return;
        }
        await deleteFunction(item.id);
                 showSnackbar(`${type ? type.charAt(0).toUpperCase() + type.slice(1) : 'Item'} deleted successfully`);
      } catch (error) {
        showSnackbar(`Error deleting ${type}`, 'error');
      }
    }
  };

  // Calculate metrics from real data
  const aiMetrics = {
    predictionsAccuracy: predictions?.reduce((sum, p) => sum + (p.accuracy || 0), 0) / (predictions?.length || 1),
    insightsGenerated: insights?.length || 0,
    recommendationsImplemented: recommendations?.filter(r => r.implementation_status === 'Completed').length || 0,
    timeSaved: recommendations?.length * 2 || 0 // Estimate 2 hours saved per recommendation
  };

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
            <PsychologyIcon />
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
              AI Co-Pilot & Strategic Intelligence
            </Typography>
            <Typography variant="h6" color="text.secondary">
              Predictive intelligence, EPM platform & chat-based business intelligence
            </Typography>
          </Box>
        </Box>
        
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
                          Ready to generate your first AI insights
          </Typography>
          <Typography variant="body2">
            Your AI platform is fully operational with predictive analytics, automated insights, and intelligent recommendations.
          </Typography>
        </Alert>
      </Box>

      {/* AI Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {aiMetrics.predictionsAccuracy}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Prediction Accuracy
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <AutoGraphIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={aiMetrics.predictionsAccuracy} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {aiMetrics.insightsGenerated}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Insights Generated
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <LightbulbIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={75} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {aiMetrics.recommendationsImplemented}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Recommendations Implemented
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <TrendingUpIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={60} sx={{ mt: 2 }} />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" color="primary" sx={{ fontWeight: 'bold' }}>
                    {aiMetrics.timeSaved}h
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Time Saved (Weekly)
                  </Typography>
                </Box>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <AnalyticsIcon />
                </Avatar>
              </Box>
              <LinearProgress variant="determinate" value={80} sx={{ mt: 2 }} />
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
            <Tab label="Predictions" icon={<AutoGraphIcon />} />
            <Tab label="Insights" icon={<LightbulbIcon />} />
            <Tab label="Chat BI" icon={<ChatIcon />} />
            <Tab label="EPM Platform" icon={<AssessmentIcon />} />
          </Tabs>
        </Box>

        <Box sx={{ p: 3, minHeight: '60vh' }}>
          {/* Predictions Tab */}
          {activeTab === 0 && (
            <Box>
              <Typography variant="h5" gutterBottom>Predictive Analytics</Typography>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  AI-powered predictive analytics for sales forecasting, customer behavior analysis, and operational optimization.
                </Typography>
              </Alert>
                             <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                 <Button
                   variant="contained"
                   onClick={() => handleAdd('prediction')}
                 >
                   Add Prediction
                 </Button>
                 <Button
                   variant="outlined"
                   onClick={() => handleView(predictions?.[0], 'prediction')}
                   disabled={!predictions || predictions.length === 0}
                 >
                   View Predictions
                 </Button>
               </Box>
            </Box>
          )}

          {/* Insights Tab */}
          {activeTab === 1 && (
            <Box>
              <Typography variant="h5" gutterBottom>AI-Generated Insights</Typography>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Automated insights and recommendations based on your business data and performance metrics.
                </Typography>
              </Alert>
                             <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                 <Button
                   variant="contained"
                   onClick={() => handleAdd('insight')}
                 >
                   Add Insight
                 </Button>
                 <Button
                   variant="outlined"
                   onClick={() => handleView(insights?.[0], 'insight')}
                   disabled={!insights || insights.length === 0}
                 >
                   View Insights
                 </Button>
               </Box>
            </Box>
          )}

          {/* Chat BI Tab */}
          {activeTab === 2 && (
            <Box>
              <Typography variant="h5" gutterBottom>Chat-Based Business Intelligence</Typography>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Ask questions about your business data in natural language and get instant insights and visualizations.
                </Typography>
              </Alert>
                             <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                 <Button
                   variant="contained"
                   onClick={() => handleAdd('recommendation')}
                 >
                   Add Recommendation
                 </Button>
                 <Button
                   variant="outlined"
                   onClick={() => handleView(recommendations?.[0], 'recommendation')}
                   disabled={!recommendations || recommendations.length === 0}
                 >
                   View Recommendations
                 </Button>
               </Box>
            </Box>
          )}

          {/* EPM Platform Tab */}
          {activeTab === 3 && (
            <Box>
              <Typography variant="h5" gutterBottom>Enterprise Performance Management</Typography>
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  Advanced budgeting, forecasting, and performance management with AI-powered insights and automated reporting.
                </Typography>
              </Alert>
                             <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                 <Button
                   variant="contained"
                   onClick={() => handleAdd('prediction')}
                 >
                   Add EPM Data
                 </Button>
                 <Button
                   variant="outlined"
                   onClick={() => handleView(predictions?.[0], 'prediction')}
                   disabled={!predictions || predictions.length === 0}
                 >
                   View EPM Data
                 </Button>
               </Box>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Footer */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          EdonuOps AI Intelligence - Strategic Decision Support Platform
        </Typography>
        <Box sx={{ mt: 1 }}>
          <Chip label="Predictive Analytics" size="small" sx={{ mr: 1 }} />
          <Chip label="Automated Insights" size="small" sx={{ mr: 1 }} />
          <Chip label="Chat BI" size="small" color="primary" />
        </Box>
      </Box>

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
               case 'prediction':
                 createFunction = createPrediction;
                 updateFunction = updatePrediction;
                 break;
               case 'insight':
                 createFunction = createInsight;
                 updateFunction = updateInsight;
                 break;
               case 'recommendation':
                 createFunction = createRecommendation;
                 updateFunction = updateRecommendation;
                 break;
               default:
                 return;
             }
             
             if (selectedItem) {
               await updateFunction(selectedItem.id, formData);
               showSnackbar(`${formType ? formType.charAt(0).toUpperCase() + formType.slice(1) : 'Item'} updated successfully`);
             } else {
               await createFunction(formData);
               showSnackbar(`${formType ? formType.charAt(0).toUpperCase() + formType.slice(1) : 'Item'} created successfully`);
             }
             setFormOpen(false);
           } catch (error) {
             showSnackbar(`Error ${selectedItem ? 'updating' : 'creating'} ${formType}`, 'error');
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

       {/* AI Error Dialog */}
       <AIErrorDialog
         open={aiErrorOpen}
         onClose={() => setAiErrorOpen(false)}
         feature={aiFeature}
       />
     </Container>
   );
 };

export default AIModule;
