import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Chip,
  Tooltip,
  IconButton,
  Snackbar,
  Alert,
  Fade,
  Slide,
  Zoom,
  Typography,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Paper,
  Card,
  CardContent,
  LinearProgress,
  CircularProgress
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  Undo as UndoIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Settings as SettingsIcon,
  HelpOutline as HelpIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  Email as EmailIcon,
  Mic as MicIcon
} from '@mui/icons-material';
import { keyframes } from '@mui/system';

// AI Animation Keyframes
const aiGlow = keyframes`
  0% { box-shadow: 0 0 5px rgba(33, 150, 243, 0.3); }
  50% { box-shadow: 0 0 20px rgba(33, 150, 243, 0.6), 0 0 30px rgba(33, 150, 243, 0.4); }
  100% { box-shadow: 0 0 5px rgba(33, 150, 243, 0.3); }
`;

const aiPulse = keyframes`
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
`;

const aiSlideIn = keyframes`
  0% { transform: translateX(-100%); opacity: 0; }
  100% { transform: translateX(0); opacity: 1; }
`;

// AI Status Badge Component
const AIStatusBadge = ({ status, message, onUndo, showUndo = false }) => {
  const [show, setShow] = useState(true);
  const [undoVisible, setUndoVisible] = useState(false);

  useEffect(() => {
    if (status === 'success' || status === 'info') {
      setUndoVisible(true);
      const timer = setTimeout(() => setUndoVisible(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  const getStatusConfig = () => {
    switch (status) {
      case 'processing':
        return { color: 'info', icon: <CircularProgress size={12} /> };
      case 'success':
        return { color: 'success', icon: <CheckCircleIcon fontSize="small" /> };
      case 'warning':
        return { color: 'warning', icon: <WarningIcon fontSize="small" /> };
      case 'ai':
        return { color: 'primary', icon: <PsychologyIcon fontSize="small" /> };
      default:
        return { color: 'default', icon: <InfoIcon fontSize="small" /> };
    }
  };

  const config = getStatusConfig();

  return (
    <Fade in={show} timeout={300}>
      <Box
        sx={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 1,
          p: 1,
          borderRadius: 2,
          backgroundColor: 'background.paper',
          border: `1px solid ${config.color === 'primary' ? 'primary.main' : `${config.color}.main`}`,
          animation: status === 'processing' ? `${aiPulse} 2s infinite` : 'none',
          boxShadow: status === 'ai' ? `0 0 10px rgba(33, 150, 243, 0.3)` : 'none'
        }}
      >
        {config.icon}
        <Typography variant="caption" color={`${config.color}.main`}>
          {message}
        </Typography>
        {showUndo && undoVisible && onUndo && (
          <Fade in={undoVisible} timeout={300}>
            <Tooltip title="Undo AI action">
              <IconButton size="small" onClick={onUndo} sx={{ ml: 1 }}>
                <UndoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Fade>
        )}
      </Box>
    </Fade>
  );
};

// AI-Enhanced Deal Card Component
const AIEnhancedDealCard = ({ deal, onUpdate, onUndo }) => {
  const [aiProcessing, setAiProcessing] = useState(false);
  const [aiStatus, setAiStatus] = useState(null);
  const [showAIBadge, setShowAIBadge] = useState(false);

  const handleAIAnalysis = async () => {
    setAiProcessing(true);
    setAiStatus({ status: 'processing', message: 'AI analyzing...' });
    
    // Simulate AI processing
    setTimeout(() => {
      setAiProcessing(false);
      setAiStatus({ 
        status: 'success', 
        message: 'Auto-moved to Proposal',
        showUndo: true 
      });
      setShowAIBadge(true);
      
      // Auto-hide badge after 3 seconds
      setTimeout(() => setShowAIBadge(false), 3000);
    }, 2000);
  };

  const handleUndo = () => {
    setAiStatus({ status: 'info', message: 'Action undone' });
    setTimeout(() => setAiStatus(null), 2000);
    if (onUndo) onUndo();
  };

  return (
    <Card
      sx={{
        position: 'relative',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4
        },
        animation: aiProcessing ? `${aiGlow} 2s infinite` : 'none'
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6">{deal.name}</Typography>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            <Chip 
              label={deal.stage} 
              color={deal.stage === 'proposal' ? 'success' : 'default'}
              size="small"
            />
            {deal.aiScore && (
              <Tooltip title="AI Lead Score">
                <Chip
                  icon={<PsychologyIcon />}
                  label={deal.aiScore}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              </Tooltip>
            )}
          </Box>
        </Box>

        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {deal.description}
        </Typography>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6" color="primary">
            ${deal.amount?.toLocaleString()}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="AI Analysis">
              <IconButton 
                size="small" 
                onClick={handleAIAnalysis}
                disabled={aiProcessing}
                sx={{
                  animation: aiProcessing ? `${aiPulse} 1s infinite` : 'none'
                }}
              >
                <PsychologyIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* AI Status Badge */}
        {aiStatus && (
          <Box sx={{ mt: 2 }}>
            <AIStatusBadge
              status={aiStatus.status}
              message={aiStatus.message}
              onUndo={aiStatus.showUndo ? handleUndo : null}
              showUndo={aiStatus.showUndo}
            />
          </Box>
        )}

        {/* AI Processing Indicator */}
        {aiProcessing && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress 
              sx={{ 
                borderRadius: 1,
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(90deg, #2196F3, #21CBF3)'
                }
              }} 
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              AI is analyzing deal progression...
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

// AI Task Suggestion Component
const AITaskSuggestion = ({ task, onAccept, onDismiss, onUndo }) => {
  const [accepted, setAccepted] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  const handleAccept = () => {
    setAccepted(true);
    if (onAccept) onAccept(task);
    
    // Show undo option briefly
    setTimeout(() => {
      if (onUndo) onUndo(task);
    }, 3000);
  };

  const handleDismiss = () => {
    setDismissed(true);
    if (onDismiss) onDismiss(task);
  };

  if (dismissed) return null;

  return (
    <Slide direction="right" in={!dismissed} timeout={300}>
      <Paper
        sx={{
          p: 2,
          mb: 1,
          border: '1px solid',
          borderColor: 'primary.main',
          backgroundColor: 'primary.50',
          animation: `${aiSlideIn} 0.5s ease-out`,
          '&:hover': {
            backgroundColor: 'primary.100'
          }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
          <Box sx={{ flex: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <AutoAwesomeIcon color="primary" fontSize="small" />
              <Typography variant="subtitle2" color="primary">
                AI Suggestion
              </Typography>
              <Chip 
                label={task.priority} 
                size="small" 
                color={task.priority === 'high' ? 'error' : task.priority === 'medium' ? 'warning' : 'default'}
              />
            </Box>
            <Typography variant="body2" sx={{ mb: 1 }}>
              {task.action}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Impact: {task.impact_score}% | Due: {task.due_date_suggestion}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Accept suggestion">
              <IconButton 
                size="small" 
                onClick={handleAccept}
                disabled={accepted}
                color="success"
              >
                <CheckCircleIcon fontSize="small" />
              </IconButton>
            </Tooltip>
            <Tooltip title="Dismiss">
              <IconButton size="small" onClick={handleDismiss}>
                ×
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        {accepted && (
          <Fade in={accepted} timeout={300}>
            <Box sx={{ mt: 1, p: 1, backgroundColor: 'success.50', borderRadius: 1 }}>
              <Typography variant="caption" color="success.main">
                ✓ Task added to your list
              </Typography>
            </Box>
          </Fade>
        )}
      </Paper>
    </Slide>
  );
};

// AI Settings Component
const AISettings = ({ settings, onUpdate }) => {
  const [localSettings, setLocalSettings] = useState(settings);

  const handleSettingChange = (key, value) => {
    const newSettings = { ...localSettings, [key]: value };
    setLocalSettings(newSettings);
    if (onUpdate) onUpdate(newSettings);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        AI Features
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure AI-powered features to enhance your CRM experience
      </Typography>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <FormControlLabel
          control={
            <Switch
              checked={localSettings.autoLeadScoring}
              onChange={(e) => handleSettingChange('autoLeadScoring', e.target.checked)}
              color="primary"
            />
          }
          label={
            <Box>
              <Typography variant="body2">Auto Lead Scoring</Typography>
              <Typography variant="caption" color="text.secondary">
                Automatically score leads based on behavioral data
              </Typography>
            </Box>
          }
        />

        <FormControlLabel
          control={
            <Switch
              checked={localSettings.autoTaskSuggestions}
              onChange={(e) => handleSettingChange('autoTaskSuggestions', e.target.checked)}
              color="primary"
            />
          }
          label={
            <Box>
              <Typography variant="body2">Smart Task Suggestions</Typography>
              <Typography variant="caption" color="text.secondary">
                AI suggests next actions based on communication patterns
              </Typography>
            </Box>
          }
        />

        <FormControlLabel
          control={
            <Switch
              checked={localSettings.autoPipelineMovement}
              onChange={(e) => handleSettingChange('autoPipelineMovement', e.target.checked)}
              color="primary"
            />
          }
          label={
            <Box>
              <Typography variant="body2">Auto Pipeline Movement</Typography>
              <Typography variant="caption" color="text.secondary">
                Automatically suggest stage progression based on deal activity
              </Typography>
            </Box>
          }
        />

        <FormControlLabel
          control={
            <Switch
              checked={localSettings.emailInsights}
              onChange={(e) => handleSettingChange('emailInsights', e.target.checked)}
              color="primary"
            />
          }
          label={
            <Box>
              <Typography variant="body2">Email Insights</Typography>
              <Typography variant="caption" color="text.secondary">
                Analyze email patterns and suggest optimal send times
              </Typography>
            </Box>
          }
        />

        <Divider sx={{ my: 2 }} />

        <Box>
          <Typography variant="subtitle2" gutterBottom>
            AI Sensitivity
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
            How aggressive should AI suggestions be?
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            {['Conservative', 'Balanced', 'Aggressive'].map((level) => (
              <Chip
                key={level}
                label={level}
                variant={localSettings.aiSensitivity === level.toLowerCase() ? 'filled' : 'outlined'}
                onClick={() => handleSettingChange('aiSensitivity', level.toLowerCase())}
                color="primary"
              />
            ))}
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

// Contextual Help Tooltip Component
const ContextualHelp = ({ children, helpText, feature }) => {
  const [showHelp, setShowHelp] = useState(false);

  return (
    <Box sx={{ position: 'relative', display: 'inline-block' }}>
      {children}
      <Tooltip
        title={
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              {feature}
            </Typography>
            <Typography variant="body2">
              {helpText}
            </Typography>
          </Box>
        }
        open={showHelp}
        onClose={() => setShowHelp(false)}
        placement="top"
        arrow
      >
        <IconButton
          size="small"
          onClick={() => setShowHelp(!showHelp)}
          sx={{
            position: 'absolute',
            top: -8,
            right: -8,
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
            '&:hover': {
              backgroundColor: 'action.hover'
            }
          }}
        >
          <HelpIcon fontSize="small" />
        </IconButton>
      </Tooltip>
    </Box>
  );
};

// Main AI Enhanced UI Component
const AIEnhancedUI = () => {
  const [aiSettings, setAISettings] = useState({
    autoLeadScoring: true,
    autoTaskSuggestions: true,
    autoPipelineMovement: false,
    emailInsights: true,
    aiSensitivity: 'balanced'
  });

  const [taskSuggestions, setTaskSuggestions] = useState([
    {
      id: 1,
      action: "Follow up on pricing discussion with John Smith",
      priority: "high",
      impact_score: 85,
      due_date_suggestion: "Today",
      reason: "Client showed strong interest in proposal"
    },
    {
      id: 2,
      action: "Schedule technical demo for ABC Corp",
      priority: "medium",
      impact_score: 70,
      due_date_suggestion: "This week",
      reason: "Lead has been actively researching our solution"
    }
  ]);

  const [deals] = useState([
    {
      id: 1,
      name: "Enterprise Software License",
      stage: "qualification",
      amount: 50000,
      aiScore: 85,
      description: "Large enterprise looking for comprehensive solution"
    },
    {
      id: 2,
      name: "SMB CRM Implementation",
      stage: "proposal",
      amount: 15000,
      aiScore: 92,
      description: "Small business ready to move forward"
    }
  ]);

  const handleTaskAccept = (task) => {
    console.log('Task accepted:', task);
    setTaskSuggestions(prev => prev.filter(t => t.id !== task.id));
  };

  const handleTaskDismiss = (task) => {
    console.log('Task dismissed:', task);
    setTaskSuggestions(prev => prev.filter(t => t.id !== task.id));
  };

  const handleTaskUndo = (task) => {
    console.log('Task undone:', task);
    setTaskSuggestions(prev => [...prev, task]);
  };

  const handleDealUndo = (dealId) => {
    console.log('Deal action undone:', dealId);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        AI-Enhanced CRM Interface
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Seamless AI integration with subtle visual cues and contextual feedback
      </Typography>

      {/* AI Task Suggestions */}
      {aiSettings.autoTaskSuggestions && taskSuggestions.length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            <ContextualHelp
              helpText="AI analyzes your communication patterns and suggests the most impactful next actions to move deals forward."
              feature="Smart Task Suggestions"
            >
              <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
                <AutoAwesomeIcon color="primary" />
                AI Suggestions
              </Box>
            </ContextualHelp>
          </Typography>
          {taskSuggestions.map((task) => (
            <AITaskSuggestion
              key={task.id}
              task={task}
              onAccept={handleTaskAccept}
              onDismiss={handleTaskDismiss}
              onUndo={handleTaskUndo}
            />
          ))}
        </Box>
      )}

      {/* AI-Enhanced Deal Cards */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          <ContextualHelp
            helpText="Deal cards show AI scores and can automatically suggest stage progression based on activity patterns."
            feature="AI-Enhanced Deals"
          >
            <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
              <TrendingUpIcon color="primary" />
              Deals
            </Box>
          </ContextualHelp>
        </Typography>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 2 }}>
          {deals.map((deal) => (
            <AIEnhancedDealCard
              key={deal.id}
              deal={deal}
              onUndo={() => handleDealUndo(deal.id)}
            />
          ))}
        </Box>
      </Box>

      {/* AI Settings */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          <ContextualHelp
            helpText="Configure AI features to match your workflow. All features are designed to enhance rather than replace your decision-making."
            feature="AI Configuration"
          >
            <Box sx={{ display: 'inline-flex', alignItems: 'center', gap: 1 }}>
              <SettingsIcon color="primary" />
              AI Settings
            </Box>
          </ContextualHelp>
        </Typography>
        <Paper elevation={1}>
          <AISettings settings={aiSettings} onUpdate={setAISettings} />
        </Paper>
      </Box>
    </Box>
  );
};

export default AIEnhancedUI;



