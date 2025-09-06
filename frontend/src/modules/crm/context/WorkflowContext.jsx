import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { apiClient } from '../../../utils/apiClient.js';

// Workflow Context
const WorkflowContext = createContext();

// Action Types
const WORKFLOW_ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_WORKFLOWS: 'SET_WORKFLOWS',
  SET_TRIGGERS: 'SET_TRIGGERS',
  SET_ACTIONS: 'SET_ACTIONS',
  SET_CONDITIONS: 'SET_CONDITIONS',
  SET_TEMPLATES: 'SET_TEMPLATES',
  ADD_WORKFLOW: 'ADD_WORKFLOW',
  UPDATE_WORKFLOW: 'UPDATE_WORKFLOW',
  DELETE_WORKFLOW: 'DELETE_WORKFLOW',
  TOGGLE_WORKFLOW: 'TOGGLE_WORKFLOW',
  SET_EXECUTION_HISTORY: 'SET_EXECUTION_HISTORY',
  SET_BUILDER_STATE: 'SET_BUILDER_STATE'
};

// Initial State
const initialState = {
  // Data
  workflows: [],
  triggers: [],
  actions: [],
  conditions: [],
  templates: [],
  executionHistory: [],

  // UI State
  loading: {
    workflows: false,
    triggers: false,
    actions: false,
    conditions: false,
    templates: false,
    executionHistory: false
  },
  errors: {},

  // Workflow Builder State
  builderState: {
    isOpen: false,
    currentWorkflow: null,
    selectedTrigger: null,
    selectedActions: [],
    selectedConditions: [],
    isEditing: false
  },

  // Available Triggers
  availableTriggers: [
    {
      id: 'contact_created',
      name: 'Contact Created',
      description: 'When a new contact is added',
      category: 'contacts',
      fields: ['contact_id', 'contact_name', 'contact_email', 'contact_phone']
    },
    {
      id: 'lead_created',
      name: 'Lead Created',
      description: 'When a new lead is added',
      category: 'leads',
      fields: ['lead_id', 'lead_name', 'lead_source', 'lead_status']
    },
    {
      id: 'opportunity_created',
      name: 'Opportunity Created',
      description: 'When a new opportunity is created',
      category: 'opportunities',
      fields: ['opportunity_id', 'opportunity_name', 'opportunity_value', 'opportunity_stage']
    },
    {
      id: 'opportunity_stage_changed',
      name: 'Opportunity Stage Changed',
      description: 'When an opportunity moves to a different stage',
      category: 'opportunities',
      fields: ['opportunity_id', 'old_stage', 'new_stage', 'opportunity_value']
    },
    {
      id: 'task_created',
      name: 'Task Created',
      description: 'When a new task is created',
      category: 'tasks',
      fields: ['task_id', 'task_title', 'task_priority', 'task_due_date', 'assigned_to']
    },
    {
      id: 'task_completed',
      name: 'Task Completed',
      description: 'When a task is marked as completed',
      category: 'tasks',
      fields: ['task_id', 'task_title', 'completed_by', 'completed_at']
    },
    {
      id: 'email_received',
      name: 'Email Received',
      description: 'When an email is received from a contact',
      category: 'communications',
      fields: ['email_id', 'from_email', 'subject', 'body', 'contact_id']
    },
    {
      id: 'activity_logged',
      name: 'Activity Logged',
      description: 'When an activity is logged',
      category: 'activities',
      fields: ['activity_id', 'activity_type', 'activity_description', 'contact_id']
    }
  ],

  // Available Actions
  availableActions: [
    {
      id: 'send_email',
      name: 'Send Email',
      description: 'Send an automated email',
      category: 'communications',
      configurable: true,
      fields: ['to', 'subject', 'body', 'template_id']
    },
    {
      id: 'create_task',
      name: 'Create Task',
      description: 'Create a new task',
      category: 'tasks',
      configurable: true,
      fields: ['title', 'description', 'due_date', 'priority', 'assigned_to']
    },
    {
      id: 'update_contact',
      name: 'Update Contact',
      description: 'Update contact information',
      category: 'contacts',
      configurable: true,
      fields: ['field', 'value']
    },
    {
      id: 'update_opportunity',
      name: 'Update Opportunity',
      description: 'Update opportunity information',
      category: 'opportunities',
      configurable: true,
      fields: ['field', 'value']
    },
    {
      id: 'add_note',
      name: 'Add Note',
      description: 'Add a note to a record',
      category: 'activities',
      configurable: true,
      fields: ['note_text', 'note_type']
    },
    {
      id: 'send_notification',
      name: 'Send Notification',
      description: 'Send an internal notification',
      category: 'notifications',
      configurable: true,
      fields: ['recipient', 'message', 'notification_type']
    },
    {
      id: 'create_activity',
      name: 'Create Activity',
      description: 'Log an activity',
      category: 'activities',
      configurable: true,
      fields: ['activity_type', 'description', 'duration']
    },
    {
      id: 'update_stage',
      name: 'Update Stage',
      description: 'Move record to different stage',
      category: 'pipeline',
      configurable: true,
      fields: ['new_stage']
    }
  ],

  // Available Conditions
  availableConditions: [
    {
      id: 'field_equals',
      name: 'Field Equals',
      description: 'Check if a field equals a specific value',
      operator: 'equals',
      fields: ['field', 'value']
    },
    {
      id: 'field_contains',
      name: 'Field Contains',
      description: 'Check if a field contains a specific value',
      operator: 'contains',
      fields: ['field', 'value']
    },
    {
      id: 'field_greater_than',
      name: 'Field Greater Than',
      description: 'Check if a field is greater than a value',
      operator: 'greater_than',
      fields: ['field', 'value']
    },
    {
      id: 'field_less_than',
      name: 'Field Less Than',
      description: 'Check if a field is less than a value',
      operator: 'less_than',
      fields: ['field', 'value']
    },
    {
      id: 'is_assigned_to',
      name: 'Is Assigned To',
      description: 'Check if record is assigned to specific user',
      operator: 'assigned_to',
      fields: ['user_id']
    },
    {
      id: 'has_tag',
      name: 'Has Tag',
      description: 'Check if record has a specific tag',
      operator: 'has_tag',
      fields: ['tag']
    },
    {
      id: 'is_in_stage',
      name: 'Is In Stage',
      description: 'Check if record is in a specific stage',
      operator: 'in_stage',
      fields: ['stage']
    }
  ]
};

// Reducer
const workflowReducer = (state, action) => {
  switch (action.type) {
    case WORKFLOW_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: { ...state.loading, ...action.payload }
      };

    case WORKFLOW_ACTIONS.SET_ERROR:
      return {
        ...state,
        errors: { ...state.errors, ...action.payload }
      };

    case WORKFLOW_ACTIONS.SET_WORKFLOWS:
      return { ...state, workflows: action.payload };

    case WORKFLOW_ACTIONS.SET_TRIGGERS:
      return { ...state, triggers: action.payload };

    case WORKFLOW_ACTIONS.SET_ACTIONS:
      return { ...state, actions: action.payload };

    case WORKFLOW_ACTIONS.SET_CONDITIONS:
      return { ...state, conditions: action.payload };

    case WORKFLOW_ACTIONS.SET_TEMPLATES:
      return { ...state, templates: action.payload };

    case WORKFLOW_ACTIONS.SET_EXECUTION_HISTORY:
      return { ...state, executionHistory: action.payload };

    case WORKFLOW_ACTIONS.ADD_WORKFLOW:
      return {
        ...state,
        workflows: [...state.workflows, action.payload]
      };

    case WORKFLOW_ACTIONS.UPDATE_WORKFLOW:
      return {
        ...state,
        workflows: (state.workflows || []).map(workflow =>
          workflow.id === action.payload.id ? action.payload : workflow
        )
      };

    case WORKFLOW_ACTIONS.DELETE_WORKFLOW:
      return {
        ...state,
        workflows: (state.workflows || []).filter(workflow => workflow.id !== action.payload)
      };

    case WORKFLOW_ACTIONS.TOGGLE_WORKFLOW:
      return {
        ...state,
        workflows: (state.workflows || []).map(workflow =>
          workflow.id === action.payload
            ? { ...workflow, is_active: !workflow.is_active }
            : workflow
        )
      };

    case WORKFLOW_ACTIONS.SET_BUILDER_STATE:
      return {
        ...state,
        builderState: { ...state.builderState, ...action.payload }
      };

    default:
      return state;
  }
};

// Workflow Provider
export const WorkflowProvider = ({ children }) => {
  const [state, dispatch] = useReducer(workflowReducer, initialState);

  // API Functions
  const fetchWorkflows = useCallback(async () => {
    dispatch({ type: WORKFLOW_ACTIONS.SET_LOADING, payload: { workflows: true } });
    try {
      const response = await apiClient.get('/api/crm/workflows');
      dispatch({ type: WORKFLOW_ACTIONS.SET_WORKFLOWS, payload: response.data });
    } catch (error) {
      dispatch({
        type: WORKFLOW_ACTIONS.SET_ERROR,
        payload: { workflows: error.message }
      });
    } finally {
      dispatch({ type: WORKFLOW_ACTIONS.SET_LOADING, payload: { workflows: false } });
    }
  }, []);

  const fetchExecutionHistory = useCallback(async () => {
    dispatch({ type: WORKFLOW_ACTIONS.SET_LOADING, payload: { executionHistory: true } });
    try {
      const response = await apiClient.get('/api/crm/workflows/execution-history');
      dispatch({ type: WORKFLOW_ACTIONS.SET_EXECUTION_HISTORY, payload: response.data });
    } catch (error) {
      dispatch({
        type: WORKFLOW_ACTIONS.SET_ERROR,
        payload: { executionHistory: error.message }
      });
    } finally {
      dispatch({ type: WORKFLOW_ACTIONS.SET_LOADING, payload: { executionHistory: false } });
    }
  }, []);

  // CRUD Operations
  const createWorkflow = useCallback(async (workflowData) => {
    try {
      const response = await apiClient.post('/api/crm/workflows', workflowData);
      dispatch({ type: WORKFLOW_ACTIONS.ADD_WORKFLOW, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const updateWorkflow = useCallback(async (id, workflowData) => {
    try {
      const response = await apiClient.put(`/api/crm/workflows/${id}`, workflowData);
      dispatch({ type: WORKFLOW_ACTIONS.UPDATE_WORKFLOW, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const deleteWorkflow = useCallback(async (id) => {
    try {
      await apiClient.delete(`/api/crm/workflows/${id}`);
      dispatch({ type: WORKFLOW_ACTIONS.DELETE_WORKFLOW, payload: id });
    } catch (error) {
      throw error;
    }
  }, []);

  const toggleWorkflow = useCallback(async (id) => {
    try {
      const response = await apiClient.patch(`/api/crm/workflows/${id}/toggle`);
      dispatch({ type: WORKFLOW_ACTIONS.TOGGLE_WORKFLOW, payload: id });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  // Workflow Builder Functions
  const openWorkflowBuilder = useCallback((workflow = null) => {
    dispatch({
      type: WORKFLOW_ACTIONS.SET_BUILDER_STATE,
      payload: {
        isOpen: true,
        currentWorkflow: workflow,
        isEditing: !!workflow,
        selectedTrigger: workflow?.trigger || null,
        selectedActions: workflow?.actions || [],
        selectedConditions: workflow?.conditions || []
      }
    });
  }, []);

  const closeWorkflowBuilder = useCallback(() => {
    dispatch({
      type: WORKFLOW_ACTIONS.SET_BUILDER_STATE,
      payload: {
        isOpen: false,
        currentWorkflow: null,
        isEditing: false,
        selectedTrigger: null,
        selectedActions: [],
        selectedConditions: []
      }
    });
  }, []);

  const setSelectedTrigger = useCallback((trigger) => {
    dispatch({
      type: WORKFLOW_ACTIONS.SET_BUILDER_STATE,
      payload: { selectedTrigger: trigger }
    });
  }, []);

  const addAction = useCallback((action) => {
    dispatch({
      type: WORKFLOW_ACTIONS.SET_BUILDER_STATE,
      payload: {
        selectedActions: [...state.builderState.selectedActions, action]
      }
    });
  }, [state.builderState.selectedActions]);

  const removeAction = useCallback((actionIndex) => {
            const newActions = (state.builderState?.selectedActions || []).filter((_, index) => index !== actionIndex);
    dispatch({
      type: WORKFLOW_ACTIONS.SET_BUILDER_STATE,
      payload: { selectedActions: newActions }
    });
  }, [state.builderState.selectedActions]);

  const addCondition = useCallback((condition) => {
    dispatch({
      type: WORKFLOW_ACTIONS.SET_BUILDER_STATE,
      payload: {
        selectedConditions: [...(state.builderState?.selectedConditions || []), condition]
      }
    });
  }, [state.builderState?.selectedConditions]);

  const removeCondition = useCallback((conditionIndex) => {
    const newConditions = (state.builderState?.selectedConditions || []).filter((_, index) => index !== conditionIndex);
    dispatch({
      type: WORKFLOW_ACTIONS.SET_BUILDER_STATE,
      payload: { selectedConditions: newConditions }
    });
  }, [state.builderState?.selectedConditions]);

  // Utility Functions
  const getWorkflowById = useCallback((id) => {
    return (state.workflows || []).find(workflow => workflow.id === id);
  }, [state.workflows]);

  const getActiveWorkflows = useCallback(() => {
    return (state.workflows || []).filter(workflow => workflow.is_active);
  }, [state.workflows]);

  const getWorkflowsByTrigger = useCallback((triggerId) => {
    return (state.workflows || []).filter(workflow =>
      workflow.trigger?.id === triggerId && workflow.is_active
    );
  }, [state.workflows]);

  const validateWorkflow = useCallback((workflow) => {
    const errors = [];

    if (!workflow.name) {
      errors.push('Workflow name is required');
    }

    if (!workflow.trigger) {
      errors.push('Trigger is required');
    }

    if (!workflow.actions || workflow.actions.length === 0) {
      errors.push('At least one action is required');
    }

    return errors;
  }, []);

  // Initialize data on mount
  useEffect(() => {
    fetchWorkflows();
    fetchExecutionHistory();
  }, [fetchWorkflows, fetchExecutionHistory]);

  const value = {
    // State
    ...state,
    workflows: state.workflows || [],
    executionHistory: state.executionHistory || [],
    availableTriggers: state.availableTriggers || [],
    availableActions: state.availableActions || [],
    availableConditions: state.availableConditions || [],
    builderState: state.builderState || {},

    // Actions
    fetchWorkflows,
    fetchExecutionHistory,
    createWorkflow,
    updateWorkflow,
    deleteWorkflow,
    toggleWorkflow,

    // Builder Functions
    openWorkflowBuilder,
    closeWorkflowBuilder,
    setSelectedTrigger,
    addAction,
    removeAction,
    addCondition,
    removeCondition,

    // Utility Functions
    getWorkflowById,
    getActiveWorkflows,
    getWorkflowsByTrigger,
    validateWorkflow
  };

  return (
    <WorkflowContext.Provider value={value}>
      {children}
    </WorkflowContext.Provider>
  );
};

// Hook
export const useWorkflow = () => {
  const context = useContext(WorkflowContext);
  if (!context) {
    throw new Error('useWorkflow must be used within a WorkflowProvider');
  }
  return context;
};
