import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  FormControlLabel,
  Slider,
  Chip,
  Button,
  Divider,
  Alert,
  Tooltip,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  TrendingUp as TrendingUpIcon,
  Email as EmailIcon,
  Mic as MicIcon,
  DataUsage as DataUsageIcon,
  Settings as SettingsIcon,
  HelpOutline as HelpIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import { apiClient } from '../config/apiConfig';

const AIGlobalSettings = ({ onSettingsChange }) => {
  const [settings, setSettings] = useState({
    // Core AI Features
    autoLeadScoring: true,
    autoTaskSuggestions: true,
    autoPipelineMovement: false,
    emailInsights: true,
    transcriptionAnalysis: true,
    duplicateDetection: true,
    
    // AI Behavior
    aiSensitivity: 50, // 0-100 scale
    autoApplySuggestions: false,
    showAIIndicators: true,
    enableNotifications: true,
    
    // Advanced Settings
    aiModel: 'gpt-4o-mini',
    maxSuggestionsPerDay: 20,
    confidenceThreshold: 70,
    
    // Privacy & Data
    shareDataForImprovement: false,
    storeBehavioralData: true,
    anonymizeData: true
  });

  const [expandedSections, setExpandedSections] = useState({
    core: true,
    behavior: false,
    advanced: false,
    privacy: false
  });

  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  // Load settings from backend
  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await apiClient.get('/api/core/settings/ai');
      if (response.data) {
        setSettings(prev => ({ ...prev, ...response.data }));
      }
    } catch (error) {
      console.log('AI settings not found, using defaults');
    }
  };

  const saveSettings = async (newSettings) => {
    setLoading(true);
    try {
      await apiClient.put('/api/core/settings/ai', newSettings);
      setSaveStatus({ type: 'success', message: 'AI settings saved successfully' });
      if (onSettingsChange) onSettingsChange(newSettings);
    } catch (error) {
      setSaveStatus({ type: 'error', message: 'Failed to save AI settings' });
    } finally {
      setLoading(false);
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const handleSettingChange = (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    saveSettings(newSettings);
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const resetToDefaults = () => {
    const defaultSettings = {
      autoLeadScoring: true,
      autoTaskSuggestions: true,
      autoPipelineMovement: false,
      emailInsights: true,
      transcriptionAnalysis: true,
      duplicateDetection: true,
      aiSensitivity: 50,
      autoApplySuggestions: false,
      showAIIndicators: true,
      enableNotifications: true,
      aiModel: 'gpt-4o-mini',
      maxSuggestionsPerDay: 20,
      confidenceThreshold: 70,
      shareDataForImprovement: false,
      storeBehavioralData: true,
      anonymizeData: true
    };
    setSettings(defaultSettings);
    saveSettings(defaultSettings);
  };

  const getSensitivityLabel = (value) => {
    if (value < 30) return 'Conservative';
    if (value < 70) return 'Balanced';
    return 'Aggressive';
  };

  const getSensitivityColor = (value) => {
    if (value < 30) return 'success';
    if (value < 70) return 'warning';
    return 'error';
  };

  const SettingItem = ({ 
    icon, 
    title, 
    description, 
    control, 
    helpText,
    warning = false 
  }) => (
    <ListItem sx={{ px: 0 }}>
      <ListItemIcon>
        {icon}
      </ListItemIcon>
      <ListItemText
        primary={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body1">{title}</Typography>
            {warning && <WarningIcon color="warning" fontSize="small" />}
            {helpText && (
              <Tooltip title={helpText}>
                <HelpIcon fontSize="small" color="action" />
              </Tooltip>
            )}
          </Box>
        }
        secondary={description}
      />
      <ListItemSecondaryAction>
        {control}
      </ListItemSecondaryAction>
    </ListItem>
  );

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <PsychologyIcon color="primary" sx={{ fontSize: 32 }} />
        <Box>
          <Typography variant="h5">AI Features</Typography>
          <Typography variant="body2" color="text.secondary">
            Configure AI-powered features to enhance your CRM experience
          </Typography>
        </Box>
      </Box>

      {/* Save Status */}
      {saveStatus && (
        <Alert 
          severity={saveStatus.type} 
          sx={{ mb: 3 }}
          onClose={() => setSaveStatus(null)}
        >
          {saveStatus.message}
        </Alert>
      )}

      {/* Core AI Features */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              cursor: 'pointer',
              mb: expandedSections.core ? 2 : 0
            }}
            onClick={() => toggleSection('core')}
          >
            <Typography variant="h6">Core AI Features</Typography>
            {expandedSections.core ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </Box>
          
          <Collapse in={expandedSections.core}>
            <List>
              <SettingItem
                icon={<PsychologyIcon color="primary" />}
                title="Auto Lead Scoring"
                description="Automatically score leads based on behavioral data and engagement patterns"
                control={
                  <Switch
                    checked={settings.autoLeadScoring}
                    onChange={(e) => handleSettingChange('autoLeadScoring', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="AI analyzes email opens, website visits, and response times to provide accurate lead scores"
              />
              
              <SettingItem
                icon={<AutoAwesomeIcon color="primary" />}
                title="Smart Task Suggestions"
                description="AI suggests next actions based on communication history and deal stage"
                control={
                  <Switch
                    checked={settings.autoTaskSuggestions}
                    onChange={(e) => handleSettingChange('autoTaskSuggestions', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="Get personalized task recommendations to move deals forward more effectively"
              />
              
              <SettingItem
                icon={<TrendingUpIcon color="primary" />}
                title="Auto Pipeline Movement"
                description="Suggest when deals should move to the next stage based on activity patterns"
                control={
                  <Switch
                    checked={settings.autoPipelineMovement}
                    onChange={(e) => handleSettingChange('autoPipelineMovement', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="AI analyzes deal progression and suggests optimal stage transitions"
                warning={true}
              />
              
              <SettingItem
                icon={<EmailIcon color="primary" />}
                title="Email Insights"
                description="Analyze email patterns and suggest optimal send times"
                control={
                  <Switch
                    checked={settings.emailInsights}
                    onChange={(e) => handleSettingChange('emailInsights', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="Get smart recommendations for when to send emails for maximum engagement"
              />
              
              <SettingItem
                icon={<MicIcon color="primary" />}
                title="Meeting Transcription"
                description="Automatically transcribe and analyze meeting conversations"
                control={
                  <Switch
                    checked={settings.transcriptionAnalysis}
                    onChange={(e) => handleSettingChange('transcriptionAnalysis', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="AI extracts action items, sentiment, and key insights from meeting recordings"
              />
              
              <SettingItem
                icon={<DataUsageIcon color="primary" />}
                title="Duplicate Detection"
                description="Automatically detect and suggest fixes for duplicate records"
                control={
                  <Switch
                    checked={settings.duplicateDetection}
                    onChange={(e) => handleSettingChange('duplicateDetection', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="Keep your CRM data clean with AI-powered duplicate detection and merge suggestions"
              />
            </List>
          </Collapse>
        </CardContent>
      </Card>

      {/* AI Behavior */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              cursor: 'pointer',
              mb: expandedSections.behavior ? 2 : 0
            }}
            onClick={() => toggleSection('behavior')}
          >
            <Typography variant="h6">AI Behavior</Typography>
            {expandedSections.behavior ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </Box>
          
          <Collapse in={expandedSections.behavior}>
            <List>
              <SettingItem
                icon={<SettingsIcon color="primary" />}
                title="AI Sensitivity"
                description={`How aggressive should AI suggestions be? (${getSensitivityLabel(settings.aiSensitivity)})`}
                control={
                  <Box sx={{ width: 120, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Slider
                      value={settings.aiSensitivity}
                      onChange={(e, value) => handleSettingChange('aiSensitivity', value)}
                      min={0}
                      max={100}
                      step={10}
                      color="primary"
                      sx={{ flex: 1 }}
                    />
                    <Chip 
                      label={settings.aiSensitivity} 
                      size="small" 
                      color={getSensitivityColor(settings.aiSensitivity)}
                    />
                  </Box>
                }
                helpText="Lower values = more conservative suggestions, Higher values = more aggressive recommendations"
              />
              
              <SettingItem
                icon={<AutoAwesomeIcon color="primary" />}
                title="Auto-Apply Suggestions"
                description="Automatically apply AI suggestions without confirmation"
                control={
                  <Switch
                    checked={settings.autoApplySuggestions}
                    onChange={(e) => handleSettingChange('autoApplySuggestions', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="Enable this to let AI make changes automatically (recommended for experienced users only)"
                warning={true}
              />
              
              <SettingItem
                icon={<InfoIcon color="primary" />}
                title="Show AI Indicators"
                description="Display visual indicators when AI is working or has made suggestions"
                control={
                  <Switch
                    checked={settings.showAIIndicators}
                    onChange={(e) => handleSettingChange('showAIIndicators', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="Subtle visual cues help you understand when AI is active"
              />
              
              <SettingItem
                icon={<CheckCircleIcon color="primary" />}
                title="Enable Notifications"
                description="Receive notifications for AI actions and suggestions"
                control={
                  <Switch
                    checked={settings.enableNotifications}
                    onChange={(e) => handleSettingChange('enableNotifications', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="Get contextual notifications about AI activities and suggestions"
              />
            </List>
          </Collapse>
        </CardContent>
      </Card>

      {/* Advanced Settings */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              cursor: 'pointer',
              mb: expandedSections.advanced ? 2 : 0
            }}
            onClick={() => toggleSection('advanced')}
          >
            <Typography variant="h6">Advanced Settings</Typography>
            {expandedSections.advanced ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </Box>
          
          <Collapse in={expandedSections.advanced}>
            <List>
              <SettingItem
                icon={<PsychologyIcon color="primary" />}
                title="AI Model"
                description="Choose the AI model for analysis (gpt-4o-mini recommended for best balance)"
                control={
                  <Chip 
                    label={settings.aiModel} 
                    color="primary" 
                    variant="outlined"
                  />
                }
                helpText="Different models offer varying levels of accuracy and speed"
              />
              
              <SettingItem
                icon={<AutoAwesomeIcon color="primary" />}
                title="Max Suggestions Per Day"
                description="Limit the number of AI suggestions to avoid overwhelming users"
                control={
                  <Box sx={{ width: 100 }}>
                    <Slider
                      value={settings.maxSuggestionsPerDay}
                      onChange={(e, value) => handleSettingChange('maxSuggestionsPerDay', value)}
                      min={5}
                      max={50}
                      step={5}
                      color="primary"
                    />
                    <Typography variant="caption" color="text.secondary">
                      {settings.maxSuggestionsPerDay} per day
                    </Typography>
                  </Box>
                }
                helpText="Prevents AI from generating too many suggestions that might overwhelm users"
              />
              
              <SettingItem
                icon={<CheckCircleIcon color="primary" />}
                title="Confidence Threshold"
                description="Only show suggestions above this confidence level"
                control={
                  <Box sx={{ width: 100 }}>
                    <Slider
                      value={settings.confidenceThreshold}
                      onChange={(e, value) => handleSettingChange('confidenceThreshold', value)}
                      min={50}
                      max={95}
                      step={5}
                      color="primary"
                    />
                    <Typography variant="caption" color="text.secondary">
                      {settings.confidenceThreshold}%
                    </Typography>
                  </Box>
                }
                helpText="Higher values = more confident suggestions only, Lower values = more suggestions"
              />
            </List>
          </Collapse>
        </CardContent>
      </Card>

      {/* Privacy & Data */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'space-between',
              cursor: 'pointer',
              mb: expandedSections.privacy ? 2 : 0
            }}
            onClick={() => toggleSection('privacy')}
          >
            <Typography variant="h6">Privacy & Data</Typography>
            {expandedSections.privacy ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </Box>
          
          <Collapse in={expandedSections.privacy}>
            <List>
              <SettingItem
                icon={<DataUsageIcon color="primary" />}
                title="Store Behavioral Data"
                description="Keep behavioral data to improve AI accuracy over time"
                control={
                  <Switch
                    checked={settings.storeBehavioralData}
                    onChange={(e) => handleSettingChange('storeBehavioralData', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="Behavioral data helps AI provide more accurate suggestions"
              />
              
              <SettingItem
                icon={<InfoIcon color="primary" />}
                title="Anonymize Data"
                description="Remove personally identifiable information from AI analysis"
                control={
                  <Switch
                    checked={settings.anonymizeData}
                    onChange={(e) => handleSettingChange('anonymizeData', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="Protects privacy while maintaining AI functionality"
              />
              
              <SettingItem
                icon={<SettingsIcon color="primary" />}
                title="Share Data for Improvement"
                description="Allow anonymous data sharing to improve AI models"
                control={
                  <Switch
                    checked={settings.shareDataForImprovement}
                    onChange={(e) => handleSettingChange('shareDataForImprovement', e.target.checked)}
                    color="primary"
                  />
                }
                helpText="Help improve AI for all users (data is anonymized and aggregated)"
              />
            </List>
          </Collapse>
        </CardContent>
      </Card>

      {/* Actions */}
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          onClick={resetToDefaults}
          disabled={loading}
        >
          Reset to Defaults
        </Button>
        <Button
          variant="contained"
          onClick={() => saveSettings(settings)}
          disabled={loading}
          startIcon={<CheckCircleIcon />}
        >
          Save Settings
        </Button>
      </Box>
    </Box>
  );
};

export default AIGlobalSettings;




