import React from 'react';
import {
  Box,
  Snackbar,
  Alert,
  IconButton,
  Typography,
  Fade,
  Slide,
  Chip,
  Tooltip,
  LinearProgress,
  Collapse
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  TrendingUp as TrendingUpIcon,
  Email as EmailIcon,
  DataUsage as DataUsageIcon,
  Mic as MicIcon,
  Undo as UndoIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useAINotifications } from '../hooks/useAINotifications';

// Icon mapping for notification types
const getNotificationIcon = (type, severity) => {
  const iconProps = { fontSize: 'small' };
  
  switch (type) {
    case 'lead_scored':
      return <PsychologyIcon {...iconProps} />;
    case 'task_suggested':
      return <AutoAwesomeIcon {...iconProps} />;
    case 'pipeline_moved':
      return <TrendingUpIcon {...iconProps} />;
    case 'email_insight':
      return <EmailIcon {...iconProps} />;
    case 'duplicate_found':
      return <DataUsageIcon {...iconProps} />;
    case 'transcription_ready':
      return <MicIcon {...iconProps} />;
    case 'ai_analysis_complete':
      return <CheckCircleIcon {...iconProps} />;
    default:
      switch (severity) {
        case 'success':
          return <CheckCircleIcon {...iconProps} />;
        case 'warning':
          return <WarningIcon {...iconProps} />;
        case 'error':
          return <ErrorIcon {...iconProps} />;
        default:
          return <InfoIcon {...iconProps} />;
      }
  }
};

// Individual notification component
const AINotification = ({ notification, onHide, onUndo }) => {
  const [expanded, setExpanded] = React.useState(false);
  const [showProgress, setShowProgress] = React.useState(notification.loading);

  React.useEffect(() => {
    if (notification.loading) {
      setShowProgress(true);
      // Simulate progress for loading notifications
      const timer = setTimeout(() => setShowProgress(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [notification.loading]);

  const handleUndo = () => {
    if (onUndo) {
      onUndo(notification.id, notification.undoCallback);
    }
  };

  const handleExpand = () => {
    setExpanded(!expanded);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'success':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  };

  return (
    <Slide direction="left" in={notification.visible} timeout={300}>
      <Box
        sx={{
          mb: 1,
          position: 'relative',
          '&:hover': {
            '& .notification-actions': {
              opacity: 1
            }
          }
        }}
      >
        <Alert
          severity={getSeverityColor(notification.severity)}
          icon={getNotificationIcon(notification.type, notification.severity)}
          action={
            <Box 
              className="notification-actions"
              sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 0.5,
                opacity: 0,
                transition: 'opacity 0.2s ease'
              }}
            >
              {notification.undoable && (
                <Tooltip title="Undo AI action">
                  <IconButton
                    size="small"
                    onClick={handleUndo}
                    sx={{ color: 'inherit' }}
                  >
                    <UndoIcon fontSize="small" />
                  </IconButton>
                </Tooltip>
              )}
              <Tooltip title="Dismiss">
                <IconButton
                  size="small"
                  onClick={() => onHide(notification.id)}
                  sx={{ color: 'inherit' }}
                >
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          }
          sx={{
            minWidth: 300,
            maxWidth: 400,
            '& .MuiAlert-message': {
              width: '100%'
            }
          }}
        >
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                {notification.title}
              </Typography>
              {notification.type && (
                <Chip
                  label={notification.type.replace('_', ' ')}
                  size="small"
                  variant="outlined"
                  sx={{ 
                    height: 20, 
                    fontSize: '0.7rem',
                    '& .MuiChip-label': { px: 1 }
                  }}
                />
              )}
            </Box>
            
            <Typography variant="body2" sx={{ mb: 1 }}>
              {notification.message}
            </Typography>

            {/* Loading Progress */}
            {showProgress && (
              <Box sx={{ mt: 1 }}>
                <LinearProgress 
                  sx={{ 
                    borderRadius: 1,
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(90deg, #2196F3, #21CBF3)'
                    }
                  }} 
                />
                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                  AI is working...
                </Typography>
              </Box>
            )}

            {/* Expandable Details */}
            {notification.details && (
              <Box>
                <IconButton
                  size="small"
                  onClick={handleExpand}
                  sx={{ 
                    p: 0, 
                    mt: 0.5,
                    '&:hover': { backgroundColor: 'transparent' }
                  }}
                >
                  <Typography variant="caption" color="primary">
                    {expanded ? 'Show less' : 'Show details'}
                  </Typography>
                </IconButton>
                
                <Collapse in={expanded} timeout="auto">
                  <Box sx={{ mt: 1, p: 1, backgroundColor: 'background.paper', borderRadius: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      {notification.details}
                    </Typography>
                  </Box>
                </Collapse>
              </Box>
            )}

            {/* Timestamp */}
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
              {new Date(notification.timestamp).toLocaleTimeString()}
            </Typography>
          </Box>
        </Alert>
      </Box>
    </Slide>
  );
};

// Main notification display component
const AINotificationDisplay = () => {
  const { notifications, hideNotification, undoAction, clearAll } = useAINotifications();
  const [position, setPosition] = React.useState({ vertical: 'top', horizontal: 'right' });

  // Auto-position notifications based on count
  React.useEffect(() => {
    if (notifications.length > 3) {
      setPosition({ vertical: 'bottom', horizontal: 'right' });
    } else {
      setPosition({ vertical: 'top', horizontal: 'right' });
    }
  }, [notifications.length]);

  return (
    <Box
      sx={{
        position: 'fixed',
        top: position.vertical === 'top' ? 16 : 'auto',
        bottom: position.vertical === 'bottom' ? 16 : 'auto',
        right: 16,
        zIndex: 9999,
        maxWidth: 420,
        maxHeight: '80vh',
        overflow: 'hidden',
        pointerEvents: 'none',
        '& > *': {
          pointerEvents: 'auto'
        }
      }}
    >
      {/* Clear All Button (only show when multiple notifications) */}
      {notifications.length > 1 && (
        <Box sx={{ mb: 1, display: 'flex', justifyContent: 'flex-end' }}>
          <Tooltip title="Clear all notifications">
            <IconButton
              size="small"
              onClick={clearAll}
              sx={{
                backgroundColor: 'background.paper',
                border: '1px solid',
                borderColor: 'divider',
                '&:hover': {
                  backgroundColor: 'action.hover'
                }
              }}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      )}

      {/* Notifications Stack */}
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
          maxHeight: '70vh',
          overflowY: 'auto',
          '&::-webkit-scrollbar': {
            width: 4
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'transparent'
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'rgba(0,0,0,0.2)',
            borderRadius: 2
          }
        }}
      >
        {notifications.map((notification) => (
          <AINotification
            key={notification.id}
            notification={notification}
            onHide={hideNotification}
            onUndo={undoAction}
          />
        ))}
      </Box>

      {/* Notification Count Badge */}
      {notifications.length > 0 && (
        <Box
          sx={{
            position: 'absolute',
            top: -8,
            right: -8,
            backgroundColor: 'primary.main',
            color: 'primary.contrastText',
            borderRadius: '50%',
            width: 24,
            height: 24,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.75rem',
            fontWeight: 600,
            border: '2px solid',
            borderColor: 'background.paper',
            animation: 'pulse 2s infinite'
          }}
        >
          {notifications.length}
        </Box>
      )}
    </Box>
  );
};

export default AINotificationDisplay;




