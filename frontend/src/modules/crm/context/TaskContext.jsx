import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { apiClient } from '../../../utils/apiClient.js';

// Task Context
const TaskContext = createContext();

// Action Types
const TASK_ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_TASKS: 'SET_TASKS',
  SET_SUBTASKS: 'SET_SUBTASKS',
  SET_TASK_TEMPLATES: 'SET_TASK_TEMPLATES',
  SET_TASK_CATEGORIES: 'SET_TASK_CATEGORIES',
  ADD_TASK: 'ADD_TASK',
  UPDATE_TASK: 'UPDATE_TASK',
  DELETE_TASK: 'DELETE_TASK',
  COMPLETE_TASK: 'COMPLETE_TASK',
  ADD_SUBTASK: 'ADD_SUBTASK',
  UPDATE_SUBTASK: 'UPDATE_SUBTASK',
  DELETE_SUBTASK: 'DELETE_SUBTASK',
  COMPLETE_SUBTASK: 'COMPLETE_SUBTASK',
  SET_TASK_FILTERS: 'SET_TASK_FILTERS',
  SET_TASK_SORT: 'SET_TASK_SORT',
  SET_TASK_VIEW: 'SET_TASK_VIEW',
  ASSIGN_TASK: 'ASSIGN_TASK',
  SET_TASK_PRIORITY: 'SET_TASK_PRIORITY',
  SET_TASK_DUE_DATE: 'SET_TASK_DUE_DATE',
  ADD_TASK_COMMENT: 'ADD_TASK_COMMENT',
  UPDATE_TASK_COMMENT: 'UPDATE_TASK_COMMENT',
  DELETE_TASK_COMMENT: 'DELETE_TASK_COMMENT',
  SET_RECURRING_TASK: 'SET_RECURRING_TASK',
  GENERATE_RECURRING_TASKS: 'GENERATE_RECURRING_TASKS'
};

// Initial State
const initialState = {
  // Data
  tasks: [],
  subtasks: [],
  taskTemplates: [],
  taskCategories: [],

  // UI State
  loading: {
    tasks: false,
    subtasks: false,
    templates: false,
    categories: false
  },
  errors: {},

  // Filters & Views
  filters: {
    status: 'all',
    priority: 'all',
    assignee: 'all',
    category: 'all',
    dueDate: 'all',
    contextType: 'all',
    contextId: null
  },
  sort: {
    field: 'due_date',
    direction: 'asc'
  },
  view: 'kanban', // kanban, list, calendar, gantt

  // Task Configuration
  priorities: [
    { id: 'low', name: 'Low', color: '#4caf50', icon: '🔵' },
    { id: 'medium', name: 'Medium', color: '#ff9800', icon: '🟡' },
    { id: 'high', name: 'High', color: '#f44336', icon: '🔴' },
    { id: 'urgent', name: 'Urgent', color: '#9c27b0', icon: '🚨' }
  ],

  statuses: [
    { id: 'todo', name: 'To Do', color: '#757575', icon: '📋' },
    { id: 'in_progress', name: 'In Progress', color: '#2196f3', icon: '⚡' },
    { id: 'review', name: 'Review', color: '#ff9800', icon: '👀' },
    { id: 'done', name: 'Done', color: '#4caf50', icon: '✅' },
    { id: 'cancelled', name: 'Cancelled', color: '#f44336', icon: '❌' }
  ],

  categories: [
    { id: 'sales', name: 'Sales', color: '#2196f3', icon: '💰' },
    { id: 'marketing', name: 'Marketing', color: '#4caf50', icon: '📢' },
    { id: 'support', name: 'Support', color: '#ff9800', icon: '🛠️' },
    { id: 'admin', name: 'Administrative', color: '#9c27b0', icon: '📊' },
    { id: 'follow_up', name: 'Follow Up', color: '#f44336', icon: '📞' },
    { id: 'meeting', name: 'Meeting', color: '#00bcd4', icon: '🤝' },
    { id: 'research', name: 'Research', color: '#795548', icon: '🔍' },
    { id: 'custom', name: 'Custom', color: '#607d8b', icon: '⚙️' }
  ],

  // Recurring Task Patterns
  recurringPatterns: [
    { id: 'daily', name: 'Daily', description: 'Every day' },
    { id: 'weekly', name: 'Weekly', description: 'Every week' },
    { id: 'biweekly', name: 'Bi-weekly', description: 'Every 2 weeks' },
    { id: 'monthly', name: 'Monthly', description: 'Every month' },
    { id: 'quarterly', name: 'Quarterly', description: 'Every 3 months' },
    { id: 'yearly', name: 'Yearly', description: 'Every year' },
    { id: 'custom', name: 'Custom', description: 'Custom interval' }
  ],

  // Context Types for Auto-Assignment
  contextTypes: [
    { id: 'contact', name: 'Contact', description: 'Tasks related to a specific contact' },
    { id: 'lead', name: 'Lead', description: 'Tasks related to a specific lead' },
    { id: 'opportunity', name: 'Opportunity', description: 'Tasks related to a specific opportunity' },
    { id: 'deal', name: 'Deal', description: 'Tasks related to a specific deal' },
    { id: 'account', name: 'Account', description: 'Tasks related to a specific account' },
    { id: 'project', name: 'Project', description: 'Tasks related to a specific project' },
    { id: 'campaign', name: 'Campaign', description: 'Tasks related to a specific campaign' }
  ]
};

// Reducer
const taskReducer = (state, action) => {
  switch (action.type) {
    case TASK_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: { ...state.loading, ...action.payload }
      };

    case TASK_ACTIONS.SET_ERROR:
      return {
        ...state,
        errors: { ...state.errors, ...action.payload }
      };

    case TASK_ACTIONS.SET_TASKS:
      return { ...state, tasks: action.payload };

    case TASK_ACTIONS.SET_SUBTASKS:
      return { ...state, subtasks: action.payload };

    case TASK_ACTIONS.SET_TASK_TEMPLATES:
      return { ...state, taskTemplates: action.payload };

    case TASK_ACTIONS.SET_TASK_CATEGORIES:
      return { ...state, taskCategories: action.payload };

    case TASK_ACTIONS.ADD_TASK:
      return {
        ...state,
        tasks: [...state.tasks, action.payload]
      };

    case TASK_ACTIONS.UPDATE_TASK:
      return {
        ...state,
        tasks: (state.tasks || []).map(task =>
          task.id === action.payload.id ? action.payload : task
        )
      };

    case TASK_ACTIONS.DELETE_TASK:
      return {
        ...state,
        tasks: (state.tasks || []).filter(task => task.id !== action.payload)
      };

    case TASK_ACTIONS.COMPLETE_TASK:
      return {
        ...state,
        tasks: (state.tasks || []).map(task =>
          task.id === action.payload.id
            ? { ...task, status: 'done', completed_at: new Date().toISOString() }
            : task
        )
      };

    case TASK_ACTIONS.ADD_SUBTASK:
      return {
        ...state,
        subtasks: [...state.subtasks, action.payload]
      };

    case TASK_ACTIONS.UPDATE_SUBTASK:
      return {
        ...state,
        subtasks: (state.subtasks || []).map(subtask =>
          subtask.id === action.payload.id ? action.payload : subtask
        )
      };

    case TASK_ACTIONS.DELETE_SUBTASK:
      return {
        ...state,
        subtasks: (state.subtasks || []).filter(subtask => subtask.id !== action.payload)
      };

    case TASK_ACTIONS.COMPLETE_SUBTASK:
      return {
        ...state,
        subtasks: (state.subtasks || []).map(subtask =>
          subtask.id === action.payload.id
            ? { ...subtask, status: 'done', completed_at: new Date().toISOString() }
            : subtask
        )
      };

    case TASK_ACTIONS.SET_TASK_FILTERS:
      return {
        ...state,
        filters: { ...state.filters, ...action.payload }
      };

    case TASK_ACTIONS.SET_TASK_SORT:
      return {
        ...state,
        sort: { ...state.sort, ...action.payload }
      };

    case TASK_ACTIONS.SET_TASK_VIEW:
      return {
        ...state,
        view: action.payload
      };

    case TASK_ACTIONS.ASSIGN_TASK:
      return {
        ...state,
        tasks: (state.tasks || []).map(task =>
          task.id === action.payload.taskId
            ? { ...task, assigned_to: action.payload.assigneeId }
            : task
        )
      };

    case TASK_ACTIONS.SET_TASK_PRIORITY:
      return {
        ...state,
        tasks: (state.tasks || []).map(task =>
          task.id === action.payload.taskId
            ? { ...task, priority: action.payload.priority }
            : task
        )
      };

    case TASK_ACTIONS.SET_TASK_DUE_DATE:
      return {
        ...state,
        tasks: (state.tasks || []).map(task =>
          task.id === action.payload.taskId
            ? { ...task, due_date: action.payload.dueDate }
            : task
        )
      };

    case TASK_ACTIONS.ADD_TASK_COMMENT:
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.taskId
            ? {
                ...task,
                comments: [...(task.comments || []), action.payload.comment]
              }
            : task
        )
      };

    case TASK_ACTIONS.UPDATE_TASK_COMMENT:
      return {
        ...state,
        tasks: (state.tasks || []).map(task =>
          task.id === action.payload.taskId
            ? {
                ...task,
                comments: (task.comments || [])?.map(comment =>
                  comment.id === action.payload.commentId
                    ? action.payload.comment
                    : comment
                ) || []
              }
            : task
        )
      };

    case TASK_ACTIONS.DELETE_TASK_COMMENT:
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.taskId
            ? {
                ...task,
                comments: task.comments?.filter(comment =>
                  comment.id !== action.payload.commentId
                ) || []
              }
            : task
        )
      };

    case TASK_ACTIONS.SET_RECURRING_TASK:
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.taskId
            ? { ...task, recurring: action.payload.recurringConfig }
            : task
        )
      };

    case TASK_ACTIONS.GENERATE_RECURRING_TASKS:
      return {
        ...state,
        tasks: [...state.tasks, ...action.payload]
      };

    default:
      return state;
  }
};

// Task Provider
export const TaskProvider = ({ children }) => {
  const [state, dispatch] = useReducer(taskReducer, initialState);

  // API Functions
  const fetchTasks = useCallback(async () => {
    dispatch({ type: TASK_ACTIONS.SET_LOADING, payload: { tasks: true } });
    try {
      const response = await apiClient.get('/api/crm/tasks');
      dispatch({ type: TASK_ACTIONS.SET_TASKS, payload: response.data });
    } catch (error) {
      dispatch({
        type: TASK_ACTIONS.SET_ERROR,
        payload: { tasks: error.message }
      });
    } finally {
      dispatch({ type: TASK_ACTIONS.SET_LOADING, payload: { tasks: false } });
    }
  }, []);

  const fetchSubtasks = useCallback(async () => {
    dispatch({ type: TASK_ACTIONS.SET_LOADING, payload: { subtasks: true } });
    try {
      const response = await apiClient.get('/api/crm/tasks/subtasks');
      dispatch({ type: TASK_ACTIONS.SET_SUBTASKS, payload: response.data });
    } catch (error) {
      dispatch({
        type: TASK_ACTIONS.SET_ERROR,
        payload: { subtasks: error.message }
      });
    } finally {
      dispatch({ type: TASK_ACTIONS.SET_LOADING, payload: { subtasks: false } });
    }
  }, []);

  const fetchTaskTemplates = useCallback(async () => {
    dispatch({ type: TASK_ACTIONS.SET_LOADING, payload: { templates: true } });
    try {
      const response = await apiClient.get('/api/crm/tasks/templates');
      dispatch({ type: TASK_ACTIONS.SET_TASK_TEMPLATES, payload: response.data });
    } catch (error) {
      dispatch({
        type: TASK_ACTIONS.SET_ERROR,
        payload: { templates: error.message }
      });
    } finally {
      dispatch({ type: TASK_ACTIONS.SET_LOADING, payload: { templates: false } });
    }
  }, []);

  // CRUD Operations
  const createTask = useCallback(async (taskData) => {
    try {
      const response = await apiClient.post('/api/crm/tasks', taskData);
      dispatch({ type: TASK_ACTIONS.ADD_TASK, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const updateTask = useCallback(async (id, taskData) => {
    try {
      const response = await apiClient.put(`/api/crm/tasks/${id}`, taskData);
      dispatch({ type: TASK_ACTIONS.UPDATE_TASK, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const deleteTask = useCallback(async (id) => {
    try {
      await apiClient.delete(`/api/crm/tasks/${id}`);
      dispatch({ type: TASK_ACTIONS.DELETE_TASK, payload: id });
    } catch (error) {
      throw error;
    }
  }, []);

  const completeTask = useCallback(async (id) => {
    try {
      const response = await apiClient.patch(`/api/crm/tasks/${id}/complete`);
      dispatch({ type: TASK_ACTIONS.COMPLETE_TASK, payload: { id } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const createSubtask = useCallback(async (subtaskData) => {
    try {
      const response = await apiClient.post('/api/crm/tasks/subtasks', subtaskData);
      dispatch({ type: TASK_ACTIONS.ADD_SUBTASK, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const updateSubtask = useCallback(async (id, subtaskData) => {
    try {
      const response = await apiClient.put(`/api/crm/tasks/subtasks/${id}`, subtaskData);
      dispatch({ type: TASK_ACTIONS.UPDATE_SUBTASK, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const deleteSubtask = useCallback(async (id) => {
    try {
      await apiClient.delete(`/api/crm/tasks/subtasks/${id}`);
      dispatch({ type: TASK_ACTIONS.DELETE_SUBTASK, payload: id });
    } catch (error) {
      throw error;
    }
  }, []);

  const completeSubtask = useCallback(async (id) => {
    try {
      const response = await apiClient.patch(`/api/crm/tasks/subtasks/${id}/complete`);
      dispatch({ type: TASK_ACTIONS.COMPLETE_SUBTASK, payload: { id } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  // Task Management Functions
  const assignTask = useCallback(async (taskId, assigneeId) => {
    try {
      const response = await apiClient.patch(`/api/crm/tasks/${taskId}/assign`, { assignee_id: assigneeId });
      dispatch({ type: TASK_ACTIONS.ASSIGN_TASK, payload: { taskId, assigneeId } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const setTaskPriority = useCallback(async (taskId, priority) => {
    try {
      const response = await apiClient.patch(`/api/crm/tasks/${taskId}/priority`, { priority });
      dispatch({ type: TASK_ACTIONS.SET_TASK_PRIORITY, payload: { taskId, priority } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const setTaskDueDate = useCallback(async (taskId, dueDate) => {
    try {
      const response = await apiClient.patch(`/api/crm/tasks/${taskId}/due-date`, { due_date: dueDate });
      dispatch({ type: TASK_ACTIONS.SET_TASK_DUE_DATE, payload: { taskId, dueDate } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const addTaskComment = useCallback(async (taskId, comment) => {
    try {
      const response = await apiClient.post(`/api/crm/tasks/${taskId}/comments`, comment);
      dispatch({ type: TASK_ACTIONS.ADD_TASK_COMMENT, payload: { taskId, comment: response.data } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const updateTaskComment = useCallback(async (taskId, commentId, comment) => {
    try {
      const response = await apiClient.put(`/api/crm/tasks/${taskId}/comments/${commentId}`, comment);
      dispatch({ type: TASK_ACTIONS.UPDATE_TASK_COMMENT, payload: { taskId, commentId, comment: response.data } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const deleteTaskComment = useCallback(async (taskId, commentId) => {
    try {
      const response = await apiClient.delete(`/api/crm/tasks/${taskId}/comments/${commentId}`);
      dispatch({ type: TASK_ACTIONS.DELETE_TASK_COMMENT, payload: { taskId, commentId } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  // Recurring Task Functions
  const setRecurringTask = useCallback(async (taskId, recurringConfig) => {
    try {
      const response = await apiClient.patch(`/api/crm/tasks/${taskId}/recurring`, recurringConfig);
      dispatch({ type: TASK_ACTIONS.SET_RECURRING_TASK, payload: { taskId, recurringConfig } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const generateRecurringTasks = useCallback(async () => {
    try {
      const response = await apiClient.post('/api/crm/tasks/generate-recurring');
      dispatch({ type: TASK_ACTIONS.GENERATE_RECURRING_TASKS, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  // Utility Functions
  const getTasksByStatus = useCallback((status) => {
    return (state.tasks || []).filter(task => task.status === status);
  }, [state.tasks]);

  const getTasksByAssignee = useCallback((assigneeId) => {
    return (state.tasks || []).filter(task => task.assigned_to === assigneeId);
  }, [state.tasks]);

  const getTasksByContext = useCallback((contextType, contextId) => {
    return (state.tasks || []).filter(task =>
      task.context_type === contextType && task.context_id === contextId
    );
  }, [state.tasks]);

  const getSubtasksByParent = useCallback((parentTaskId) => {
    return (state.subtasks || []).filter(subtask => subtask.parent_task_id === parentTaskId);
  }, [state.subtasks]);

  const getOverdueTasks = useCallback(() => {
    const now = new Date();
    return (state.tasks || []).filter(task =>
      task.due_date && new Date(task.due_date) < now && task.status !== 'done'
    );
  }, [state.tasks]);

  const getTasksDueToday = useCallback(() => {
    const today = new Date().toISOString().split('T')[0];
    return (state.tasks || []).filter(task =>
      task.due_date && task.due_date.split('T')[0] === today && task.status !== 'done'
    );
  }, [state.tasks]);

  const getTasksDueThisWeek = useCallback(() => {
    const now = new Date();
    const endOfWeek = new Date(now);
    endOfWeek.setDate(now.getDate() + 7);

    return (state.tasks || []).filter(task =>
      task.due_date &&
      new Date(task.due_date) <= endOfWeek &&
      new Date(task.due_date) >= now &&
      task.status !== 'done'
    );
  }, [state.tasks]);

  const getTaskById = useCallback((id) => {
    return (state.tasks || []).find(task => task.id === id);
  }, [state.tasks]);

  const getSubtaskById = useCallback((id) => {
    return (state.subtasks || []).find(subtask => subtask.id === id);
  }, [state.subtasks]);

  // Initialize data on mount
  useEffect(() => {
    fetchTasks();
    fetchSubtasks();
    fetchTaskTemplates();
  }, [fetchTasks, fetchSubtasks, fetchTaskTemplates]);

  const value = {
    // State
    ...state,
    tasks: state.tasks || [],
    subtasks: state.subtasks || [],
    taskTemplates: state.taskTemplates || [],
    priorities: state.priorities || [],
    statuses: state.statuses || [],
    categories: state.categories || [],
    recurringPatterns: state.recurringPatterns || [],
    contextTypes: state.contextTypes || [],

    // Actions
    fetchTasks,
    fetchSubtasks,
    fetchTaskTemplates,
    createTask,
    updateTask,
    deleteTask,
    completeTask,
    createSubtask,
    updateSubtask,
    deleteSubtask,
    completeSubtask,
    assignTask,
    setTaskPriority,
    setTaskDueDate,
    addTaskComment,
    updateTaskComment,
    deleteTaskComment,
    setRecurringTask,
    generateRecurringTasks,

    // Utility Functions
    getTasksByStatus,
    getTasksByAssignee,
    getTasksByContext,
    getSubtasksByParent,
    getOverdueTasks,
    getTasksDueToday,
    getTasksDueThisWeek,
    getTaskById,
    getSubtaskById,

    // UI Actions
    setFilters: (filters) => dispatch({ type: TASK_ACTIONS.SET_TASK_FILTERS, payload: filters }),
    setSort: (sort) => dispatch({ type: TASK_ACTIONS.SET_TASK_SORT, payload: sort }),
    setView: (view) => dispatch({ type: TASK_ACTIONS.SET_TASK_VIEW, payload: view })
  };

  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  );
};

// Hook
export const useTask = () => {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error('useTask must be used within a TaskProvider');
  }
  return context;
};
