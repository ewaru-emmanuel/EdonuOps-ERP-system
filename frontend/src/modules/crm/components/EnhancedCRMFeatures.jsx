import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  Email as EmailIcon,
  Mic as MicIcon,
  Schedule as ScheduleIcon,
  DataUsage as DataIcon,
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { apiClient } from '../../../config/apiConfig';

const EnhancedCRMFeatures = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [aiInsights, setAiInsights] = useState(null);
  const [behavioralData, setBehavioralData] = useState(null);
  const [emailSyncStatus, setEmailSyncStatus] = useState(null);
  const [transcriptionResult, setTranscriptionResult] = useState(null);
  const [timeAnalytics, setTimeAnalytics] = useState(null);
  const [duplicateData, setDuplicateData] = useState(null);
  const [dashboardWidgets, setDashboardWidgets] = useState(null);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  // Enhanced AI Lead Scoring
  const testAIScoring = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/crm/ai/score-lead', {
        lead: {
          first_name: 'John',
          last_name: 'Smith',
          email: 'john.smith@company.com',
          company: 'Tech Corp',
          source: 'website',
          status: 'new'
        },
        behavioral_data: {
          email_opens: 3,
          website_visits: 5,
          response_time: 'same_day',
          engagement_score: 75
        }
      });
      
      setAiInsights(response.data);
    } catch (error) {
      console.error('AI scoring failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // AI Task Suggestions
  const getAITaskSuggestions = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/crm/ai/suggest-tasks', {
        entity_type: 'lead',
        entity_id: 1,
        context: {
          recent_emails: 2,
          last_call: '2024-01-15',
          meeting_scheduled: true
        }
      });
      
      setAiInsights(prev => ({
        ...prev,
        taskSuggestions: response.data.tasks
      }));
    } catch (error) {
      console.error('Task suggestions failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Enhanced Email Sync
  const testEmailSync = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/crm/email/sync', {
        provider: 'gmail',
        folder: 'INBOX',
        max_emails: 10
      });
      
      setEmailSyncStatus(response.data);
    } catch (error) {
      console.error('Email sync failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Real-time Transcription
  const testTranscription = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/crm/ai/transcribe-meeting', {
        audio_data: 'base64_encoded_audio_data',
        meeting_type: 'sales_call',
        participants: ['John Smith', 'Sales Rep'],
        lead_id: 1
      });
      
      setTranscriptionResult(response.data);
    } catch (error) {
      console.error('Transcription failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Time Analytics
  const getTimeAnalytics = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/crm/analytics/time-per-client');
      setTimeAnalytics(response.data);
    } catch (error) {
      console.error('Time analytics failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Data Validation
  const checkDuplicates = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/crm/data-validation/duplicates');
      setDuplicateData(response.data);
    } catch (error) {
      console.error('Duplicate check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Dashboard Widgets
  const getDashboardWidgets = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/crm/dashboard/widgets');
      setDashboardWidgets(response.data);
    } catch (error) {
      console.error('Dashboard widgets failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`enhanced-crm-tabpanel-${index}`}
      aria-labelledby={`enhanced-crm-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Box sx={{ width: '100%' }}>
      <Typography variant="h4" gutterBottom>
        Enhanced CRM Features
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Advanced AI-powered CRM capabilities for modern sales teams
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={handleTabChange} aria-label="enhanced crm features">
          <Tab label="AI Lead Scoring" icon={<PsychologyIcon />} />
          <Tab label="Email Sync" icon={<EmailIcon />} />
          <Tab label="Transcription" icon={<MicIcon />} />
          <Tab label="Time Analytics" icon={<ScheduleIcon />} />
          <Tab label="Data Validation" icon={<DataIcon />} />
          <Tab label="Dashboard" icon={<DashboardIcon />} />
        </Tabs>
      </Box>

      {/* AI Lead Scoring Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Enhanced AI Lead Scoring
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  AI-powered lead scoring with explainability, behavioral insights, and next best actions
                </Typography>
                <Button
                  variant="contained"
                  onClick={testAIScoring}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <PsychologyIcon />}
                  sx={{ mb: 2 }}
                >
                  Test AI Scoring
                </Button>
                <Button
                  variant="outlined"
                  onClick={getAITaskSuggestions}
                  disabled={loading}
                  startIcon={<CheckCircleIcon />}
                  sx={{ ml: 2, mb: 2 }}
                >
                  Get Task Suggestions
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            {aiInsights && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    AI Analysis Results
                  </Typography>
                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={`Score: ${aiInsights.score}/100`}
                      color={aiInsights.score > 70 ? 'success' : aiInsights.score > 40 ? 'warning' : 'error'}
                      sx={{ mr: 1 }}
                    />
                    <Chip
                      label={`Confidence: ${aiInsights.confidence}%`}
                      color="info"
                    />
                  </Box>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Explanation:</strong> {aiInsights.explanation}
                  </Typography>
                  {aiInsights.behavioral_insights && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Behavioral Insights:
                      </Typography>
                      <List dense>
                        {aiInsights.behavioral_insights.map((insight, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              <InfoIcon color="primary" />
                            </ListItemIcon>
                            <ListItemText primary={insight} />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                  {aiInsights.taskSuggestions && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Suggested Tasks:
                      </Typography>
                      <List dense>
                        {aiInsights.taskSuggestions.map((task, index) => (
                          <ListItem key={index}>
                            <ListItemIcon>
                              <CheckCircleIcon color="success" />
                            </ListItemIcon>
                            <ListItemText 
                              primary={task.action}
                              secondary={`Priority: ${task.priority} | Impact: ${task.impact_score}%`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Email Sync Tab */}
      <TabPanel value={activeTab} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Enhanced Email Sync
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Gmail/Outlook integration with activity tracking and smart send time suggestions
                </Typography>
                <Button
                  variant="contained"
                  onClick={testEmailSync}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <EmailIcon />}
                >
                  Test Email Sync
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            {emailSyncStatus && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Email Sync Results
                  </Typography>
                  <Alert severity="success" sx={{ mb: 2 }}>
                    {emailSyncStatus.message}
                  </Alert>
                  <Typography variant="body2">
                    <strong>Provider:</strong> {emailSyncStatus.provider}<br />
                    <strong>Emails Fetched:</strong> {emailSyncStatus.fetched}<br />
                    <strong>Activity Events:</strong> {emailSyncStatus.activity_events?.length || 0}
                  </Typography>
                  {emailSyncStatus.smart_send_times && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Smart Send Times:
                      </Typography>
                      <List dense>
                        {emailSyncStatus.smart_send_times.map((time, index) => (
                          <ListItem key={index}>
                            <ListItemText 
                              primary={`${time.time} on ${time.day}`}
                              secondary={`${time.reason} (${time.confidence_score}% confidence)`}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Transcription Tab */}
      <TabPanel value={activeTab} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Real-time Transcription
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  AI-powered meeting transcription with summaries and action points
                </Typography>
                <Button
                  variant="contained"
                  onClick={testTranscription}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <MicIcon />}
                >
                  Test Transcription
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            {transcriptionResult && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Transcription Analysis
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    <strong>Meeting Type:</strong> {transcriptionResult.meeting_type}<br />
                    <strong>Duration:</strong> {transcriptionResult.duration_minutes} minutes
                  </Typography>
                  {transcriptionResult.analysis && (
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        AI Analysis:
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        <strong>Summary:</strong> {transcriptionResult.analysis.summary}
                      </Typography>
                      {transcriptionResult.analysis.action_items && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Action Items:
                          </Typography>
                          <List dense>
                            {transcriptionResult.analysis.action_items.map((item, index) => (
                              <ListItem key={index}>
                                <ListItemIcon>
                                  <CheckCircleIcon color="primary" />
                                </ListItemIcon>
                                <ListItemText 
                                  primary={item.action}
                                  secondary={`Priority: ${item.priority} | Due: ${item.deadline}`}
                                />
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Time Analytics Tab */}
      <TabPanel value={activeTab} index={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Time Analytics
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Time spent per client analytics linked to sales outcomes
                </Typography>
                <Button
                  variant="contained"
                  onClick={getTimeAnalytics}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <ScheduleIcon />}
                >
                  Get Time Analytics
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            {timeAnalytics && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Time Analytics Summary
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={6}>
                      <Typography variant="h4" color="primary">
                        {timeAnalytics.summary.total_time_hours}
                      </Typography>
                      <Typography variant="body2">Total Hours</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="h4" color="success">
                        ${timeAnalytics.summary.total_billable_amount}
                      </Typography>
                      <Typography variant="body2">Billable Amount</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="h4" color="info">
                        {timeAnalytics.summary.won_deals}
                      </Typography>
                      <Typography variant="body2">Won Deals</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="h4" color="warning">
                        ${timeAnalytics.summary.roi_per_hour}
                      </Typography>
                      <Typography variant="body2">ROI per Hour</Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Data Validation Tab */}
      <TabPanel value={activeTab} index={4}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Data Validation
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Duplicate detection, fuzzy matching, and auto-clean suggestions
                </Typography>
                <Button
                  variant="contained"
                  onClick={checkDuplicates}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <DataIcon />}
                >
                  Check for Duplicates
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            {duplicateData && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Duplicate Analysis
                  </Typography>
                  <Alert 
                    severity={duplicateData.summary.total_duplicates > 0 ? 'warning' : 'success'} 
                    sx={{ mb: 2 }}
                  >
                    {duplicateData.summary.total_duplicates} duplicates found
                  </Alert>
                  <Typography variant="body2">
                    <strong>Contact Duplicates:</strong> {duplicateData.summary.total_contact_duplicates}<br />
                    <strong>Lead Duplicates:</strong> {duplicateData.summary.total_lead_duplicates}
                  </Typography>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>

      {/* Dashboard Tab */}
      <TabPanel value={activeTab} index={5}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Customizable Dashboard
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Drag-and-drop dashboard widgets with real-time data
                </Typography>
                <Button
                  variant="contained"
                  onClick={getDashboardWidgets}
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <DashboardIcon />}
                >
                  Load Dashboard Widgets
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            {dashboardWidgets && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Available Widgets
                  </Typography>
                  <List dense>
                    {dashboardWidgets.available_widgets.map((widget, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <TrendingUpIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={widget.name}
                          secondary={widget.description}
                        />
                        <Chip 
                          label={widget.category} 
                          size="small" 
                          color="secondary"
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            )}
          </Grid>
        </Grid>
      </TabPanel>
    </Box>
  );
};

export default EnhancedCRMFeatures;



