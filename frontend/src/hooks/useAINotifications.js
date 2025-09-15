import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../config/apiConfig';

// AI Notification Types
const AI_NOTIFICATION_TYPES = {
  LEAD_SCORED: 'lead_scored',
  TASK_SUGGESTED: 'task_suggested',
  PIPELINE_MOVED: 'pipeline_moved',
  EMAIL_INSIGHT: 'email_insight',
  DUPLICATE_FOUND: 'duplicate_found',
  TRANSCRIPTION_READY: 'transcription_ready',
  AI_ANALYSIS_COMPLETE: 'ai_analysis_complete'
};

// AI Notification Manager
class AINotificationManager {
  constructor() {
    this.notifications = [];
    this.listeners = [];
    this.maxNotifications = 5;
    this.autoHideDelay = 5000; // 5 seconds
  }

  // Add a new notification
  addNotification(notification) {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      timestamp: new Date(),
      ...notification,
      visible: true,
      undoable: notification.undoable || false
    };

    this.notifications.unshift(newNotification);
    
    // Keep only the latest notifications
    if (this.notifications.length > this.maxNotifications) {
      this.notifications = this.notifications.slice(0, this.maxNotifications);
    }

    this.notifyListeners();

    // Auto-hide after delay
    if (notification.autoHide !== false) {
      setTimeout(() => {
        this.hideNotification(id);
      }, this.autoHideDelay);
    }

    return id;
  }

  // Hide a notification
  hideNotification(id) {
    const index = this.notifications.findIndex(n => n.id === id);
    if (index !== -1) {
      this.notifications[index].visible = false;
      this.notifyListeners();

      // Remove after animation
      setTimeout(() => {
        this.notifications = this.notifications.filter(n => n.id !== id);
        this.notifyListeners();
      }, 300);
    }
  }

  // Undo an AI action
  undoAction(id, undoCallback) {
    const notification = this.notifications.find(n => n.id === id);
    if (notification && undoCallback) {
      undoCallback();
      this.addNotification({
        type: AI_NOTIFICATION_TYPES.AI_ANALYSIS_COMPLETE,
        title: 'Action Undone',
        message: 'AI action has been reversed',
        severity: 'info',
        icon: 'undo',
        autoHide: true
      });
    }
    this.hideNotification(id);
  }

  // Clear all notifications
  clearAll() {
    this.notifications = [];
    this.notifyListeners();
  }

  // Subscribe to notification changes
  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  // Notify all listeners
  notifyListeners() {
    this.listeners.forEach(listener => listener([...this.notifications]));
  }

  // Get current notifications
  getNotifications() {
    return [...this.notifications];
  }
}

// Global notification manager instance
const aiNotificationManager = new AINotificationManager();

// Custom hook for AI notifications
export const useAINotifications = () => {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const unsubscribe = aiNotificationManager.subscribe(setNotifications);
    return unsubscribe;
  }, []);

  const addNotification = useCallback((notification) => {
    return aiNotificationManager.addNotification(notification);
  }, []);

  const hideNotification = useCallback((id) => {
    aiNotificationManager.hideNotification(id);
  }, []);

  const undoAction = useCallback((id, undoCallback) => {
    aiNotificationManager.undoAction(id, undoCallback);
  }, []);

  const clearAll = useCallback(() => {
    aiNotificationManager.clearAll();
  }, []);

  return {
    notifications,
    addNotification,
    hideNotification,
    undoAction,
    clearAll
  };
};

// AI Service Integration
export const useAIService = () => {
  const { addNotification } = useAINotifications();

  // Lead scoring with notification
  const scoreLead = useCallback(async (leadData) => {
    const notificationId = addNotification({
      type: AI_NOTIFICATION_TYPES.LEAD_SCORED,
      title: 'AI Analyzing Lead',
      message: 'Calculating score and insights...',
      severity: 'info',
      icon: 'psychology',
      loading: true
    });

    try {
      const response = await apiClient.post('/crm/ai/score-lead', {
        lead: leadData.lead,
        behavioral_data: leadData.behavioral_data
      });

      // Update notification with results
      addNotification({
        type: AI_NOTIFICATION_TYPES.LEAD_SCORED,
        title: 'Lead Scored',
        message: `Score: ${response.data.score}/100 - ${response.data.explanation}`,
        severity: response.data.score > 70 ? 'success' : response.data.score > 40 ? 'warning' : 'error',
        icon: 'psychology',
        undoable: true,
        undoCallback: () => {
          // Undo lead scoring logic here
          console.log('Undoing lead score update');
        }
      });

      return response.data;
    } catch (error) {
      addNotification({
        type: AI_NOTIFICATION_TYPES.LEAD_SCORED,
        title: 'Scoring Failed',
        message: 'Unable to analyze lead at this time',
        severity: 'error',
        icon: 'error'
      });
      throw error;
    }
  }, [addNotification]);

  // Task suggestions with notification
  const suggestTasks = useCallback(async (entityData) => {
    const notificationId = addNotification({
      type: AI_NOTIFICATION_TYPES.TASK_SUGGESTED,
      title: 'Generating Task Suggestions',
      message: 'AI is analyzing communication patterns...',
      severity: 'info',
      icon: 'auto_awesome',
      loading: true
    });

    try {
      const response = await apiClient.post('/crm/ai/suggest-tasks', entityData);

      addNotification({
        type: AI_NOTIFICATION_TYPES.TASK_SUGGESTED,
        title: 'Tasks Suggested',
        message: `Found ${response.data.tasks.length} actionable tasks`,
        severity: 'success',
        icon: 'auto_awesome',
        undoable: true,
        undoCallback: () => {
          // Undo task suggestions logic here
          console.log('Undoing task suggestions');
        }
      });

      return response.data;
    } catch (error) {
      addNotification({
        type: AI_NOTIFICATION_TYPES.TASK_SUGGESTED,
        title: 'Suggestion Failed',
        message: 'Unable to generate task suggestions',
        severity: 'error',
        icon: 'error'
      });
      throw error;
    }
  }, [addNotification]);

  // Pipeline movement with notification
  const analyzePipelineMovement = useCallback(async (opportunityId) => {
    const notificationId = addNotification({
      type: AI_NOTIFICATION_TYPES.PIPELINE_MOVED,
      title: 'Analyzing Pipeline',
      message: 'Evaluating deal progression...',
      severity: 'info',
      icon: 'trending_up',
      loading: true
    });

    try {
      const response = await apiClient.post('/crm/ai/pipeline-insights', {
        opportunity_id: opportunityId
      });

      const shouldMove = response.data.should_move_stage;
      addNotification({
        type: AI_NOTIFICATION_TYPES.PIPELINE_MOVED,
        title: shouldMove ? 'Stage Movement Suggested' : 'No Movement Needed',
        message: shouldMove 
          ? `Consider moving to next stage: ${response.data.recommended_actions[0] || 'Review recommended actions'}`
          : 'Deal is progressing normally in current stage',
        severity: shouldMove ? 'success' : 'info',
        icon: 'trending_up',
        undoable: shouldMove,
        undoCallback: () => {
          // Undo pipeline movement logic here
          console.log('Undoing pipeline movement');
        }
      });

      return response.data;
    } catch (error) {
      addNotification({
        type: AI_NOTIFICATION_TYPES.PIPELINE_MOVED,
        title: 'Analysis Failed',
        message: 'Unable to analyze pipeline movement',
        severity: 'error',
        icon: 'error'
      });
      throw error;
    }
  }, [addNotification]);

  // Email sync with notification
  const syncEmails = useCallback(async (provider = 'gmail') => {
    const notificationId = addNotification({
      type: AI_NOTIFICATION_TYPES.EMAIL_INSIGHT,
      title: 'Syncing Emails',
      message: `Connecting to ${provider}...`,
      severity: 'info',
      icon: 'email',
      loading: true
    });

    try {
      const response = await apiClient.post('/crm/email/sync', {
        provider,
        max_emails: 50
      });

      addNotification({
        type: AI_NOTIFICATION_TYPES.EMAIL_INSIGHT,
        title: 'Emails Synced',
        message: `Fetched ${response.data.fetched} emails with smart send time suggestions`,
        severity: 'success',
        icon: 'email',
        undoable: false
      });

      return response.data;
    } catch (error) {
      addNotification({
        type: AI_NOTIFICATION_TYPES.EMAIL_INSIGHT,
        title: 'Sync Failed',
        message: 'Unable to sync emails at this time',
        severity: 'error',
        icon: 'error'
      });
      throw error;
    }
  }, [addNotification]);

  // Transcription with notification
  const transcribeMeeting = useCallback(async (audioData) => {
    const notificationId = addNotification({
      type: AI_NOTIFICATION_TYPES.TRANSCRIPTION_READY,
      title: 'Processing Meeting',
      message: 'Transcribing and analyzing conversation...',
      severity: 'info',
      icon: 'mic',
      loading: true
    });

    try {
      const response = await apiClient.post('/crm/ai/transcribe-meeting', audioData);

      addNotification({
        type: AI_NOTIFICATION_TYPES.TRANSCRIPTION_READY,
        title: 'Transcription Complete',
        message: `Meeting analyzed with ${response.data.analysis.action_items?.length || 0} action items identified`,
        severity: 'success',
        icon: 'mic',
        undoable: true,
        undoCallback: () => {
          // Undo transcription logic here
          console.log('Undoing transcription analysis');
        }
      });

      return response.data;
    } catch (error) {
      addNotification({
        type: AI_NOTIFICATION_TYPES.TRANSCRIPTION_READY,
        title: 'Transcription Failed',
        message: 'Unable to process meeting audio',
        severity: 'error',
        icon: 'error'
      });
      throw error;
    }
  }, [addNotification]);

  // Duplicate detection with notification
  const checkDuplicates = useCallback(async () => {
    const notificationId = addNotification({
      type: AI_NOTIFICATION_TYPES.DUPLICATE_FOUND,
      title: 'Scanning for Duplicates',
      message: 'Analyzing contact and lead data...',
      severity: 'info',
      icon: 'data_usage',
      loading: true
    });

    try {
      const response = await apiClient.get('/crm/data-validation/duplicates');

      const totalDuplicates = response.data.summary.total_duplicates;
      addNotification({
        type: AI_NOTIFICATION_TYPES.DUPLICATE_FOUND,
        title: 'Duplicate Scan Complete',
        message: totalDuplicates > 0 
          ? `Found ${totalDuplicates} potential duplicates`
          : 'No duplicates found - data looks clean!',
        severity: totalDuplicates > 0 ? 'warning' : 'success',
        icon: 'data_usage',
        undoable: false
      });

      return response.data;
    } catch (error) {
      addNotification({
        type: AI_NOTIFICATION_TYPES.DUPLICATE_FOUND,
        title: 'Scan Failed',
        message: 'Unable to check for duplicates',
        severity: 'error',
        icon: 'error'
      });
      throw error;
    }
  }, [addNotification]);

  return {
    scoreLead,
    suggestTasks,
    analyzePipelineMovement,
    syncEmails,
    transcribeMeeting,
    checkDuplicates
  };
};

export { AI_NOTIFICATION_TYPES };




