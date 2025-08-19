import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { apiClient } from '../../../utils/apiClient.js';

// CRM Context
const CRMContext = createContext();

// Action Types
const CRM_ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_CONTACTS: 'SET_CONTACTS',
  SET_LEADS: 'SET_LEADS',
  SET_OPPORTUNITIES: 'SET_OPPORTUNITIES',
  SET_PIPELINES: 'SET_PIPELINES',
  SET_STAGES: 'SET_STAGES',
  SET_TASKS: 'SET_TASKS',
  SET_ACTIVITIES: 'SET_ACTIVITIES',
  SET_ANALYTICS: 'SET_ANALYTICS',
  SET_LEAD_INTAKES: 'SET_LEAD_INTAKES',
  SET_USERS: 'SET_USERS',
  ADD_CONTACT: 'ADD_CONTACT',
  UPDATE_CONTACT: 'UPDATE_CONTACT',
  DELETE_CONTACT: 'DELETE_CONTACT',
  ADD_LEAD: 'ADD_LEAD',
  UPDATE_LEAD: 'UPDATE_LEAD',
  DELETE_LEAD: 'DELETE_LEAD',
  ADD_OPPORTUNITY: 'ADD_OPPORTUNITY',
  UPDATE_OPPORTUNITY: 'UPDATE_OPPORTUNITY',
  DELETE_OPPORTUNITY: 'DELETE_OPPORTUNITY',
  MOVE_OPPORTUNITY: 'MOVE_OPPORTUNITY',
  ADD_TASK: 'ADD_TASK',
  UPDATE_TASK: 'UPDATE_TASK',
  DELETE_TASK: 'DELETE_TASK',
  ADD_ACTIVITY: 'ADD_ACTIVITY',
  UPDATE_ACTIVITY: 'UPDATE_ACTIVITY',
  DELETE_ACTIVITY: 'DELETE_ACTIVITY',
  ADD_LEAD_INTAKE: 'ADD_LEAD_INTAKE',
  UPDATE_LEAD_INTAKE: 'UPDATE_LEAD_INTAKE',
  SET_FILTERS: 'SET_FILTERS',
  SET_SORT: 'SET_SORT',
  SET_VIEW: 'SET_VIEW',
  REFRESH_DATA: 'REFRESH_DATA'
};

// Initial State
const initialState = {
  // Data
  contacts: [],
  leads: [],
  opportunities: [],
  pipelines: [],
  stages: [],
  tasks: [],
  activities: [],
  analytics: {},
  leadIntakes: [],
  users: [],

  // UI State
  loading: {
    contacts: false,
    leads: false,
    opportunities: false,
    pipelines: false,
    tasks: false,
    activities: false,
    analytics: false,
    leadIntakes: false,
    users: false
  },
  errors: {},

  // Filters & Views
  filters: {
    contacts: {},
    leads: {},
    opportunities: {},
    tasks: {},
    activities: {}
  },
  sort: {
    contacts: { field: 'name', direction: 'asc' },
    leads: { field: 'created_at', direction: 'desc' },
    opportunities: { field: 'value', direction: 'desc' },
    tasks: { field: 'due_date', direction: 'asc' }
  },
  view: {
    contacts: 'table',
    leads: 'table',
    opportunities: 'pipeline',
    tasks: 'kanban'
  },

  // Pipeline Configuration
  pipelineConfig: {
    defaultPipeline: 'sales',
    customPipelines: [],
    stageTemplates: {},
    automationRules: []
  }
};

// Reducer
const crmReducer = (state, action) => {
  switch (action.type) {
    case CRM_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: { ...state.loading, ...action.payload }
      };

    case CRM_ACTIONS.SET_ERROR:
      return {
        ...state,
        errors: { ...state.errors, ...action.payload }
      };

    case CRM_ACTIONS.SET_CONTACTS:
      return { ...state, contacts: action.payload };

    case CRM_ACTIONS.SET_LEADS:
      return { ...state, leads: action.payload };

    case CRM_ACTIONS.SET_OPPORTUNITIES:
      return { ...state, opportunities: action.payload };

    case CRM_ACTIONS.SET_PIPELINES:
      return { ...state, pipelines: action.payload };

    case CRM_ACTIONS.SET_STAGES:
      return { ...state, stages: action.payload };

    case CRM_ACTIONS.SET_TASKS:
      return { ...state, tasks: action.payload };

    case CRM_ACTIONS.SET_ACTIVITIES:
      return { ...state, activities: action.payload };

    case CRM_ACTIONS.SET_ANALYTICS:
      return { ...state, analytics: action.payload };

    case CRM_ACTIONS.SET_LEAD_INTAKES:
      return { ...state, leadIntakes: action.payload };

    case CRM_ACTIONS.SET_USERS:
      return { ...state, users: action.payload };

    case CRM_ACTIONS.ADD_LEAD_INTAKE:
      return {
        ...state,
        leadIntakes: [...state.leadIntakes, action.payload]
      };

    case CRM_ACTIONS.UPDATE_LEAD_INTAKE:
      return {
        ...state,
        leadIntakes: state.leadIntakes.map(intake =>
          intake.id === action.payload.id ? action.payload : intake
        )
      };

    case CRM_ACTIONS.ADD_CONTACT:
      return {
        ...state,
        contacts: [...state.contacts, action.payload]
      };

    case CRM_ACTIONS.UPDATE_CONTACT:
      return {
        ...state,
        contacts: state.contacts.map(contact =>
          contact.id === action.payload.id ? action.payload : contact
        )
      };

    case CRM_ACTIONS.DELETE_CONTACT:
      return {
        ...state,
        contacts: (state.contacts || []).filter(contact => contact.id !== action.payload)
      };

    case CRM_ACTIONS.ADD_LEAD:
      return {
        ...state,
        leads: [...state.leads, action.payload]
      };

    case CRM_ACTIONS.UPDATE_LEAD:
      return {
        ...state,
        leads: state.leads.map(lead =>
          lead.id === action.payload.id ? action.payload : lead
        )
      };

    case CRM_ACTIONS.DELETE_LEAD:
      return {
        ...state,
        leads: (state.leads || []).filter(lead => lead.id !== action.payload)
      };

    case CRM_ACTIONS.ADD_OPPORTUNITY:
      return {
        ...state,
        opportunities: [...state.opportunities, action.payload]
      };

    case CRM_ACTIONS.UPDATE_OPPORTUNITY:
      return {
        ...state,
        opportunities: state.opportunities.map(opp =>
          opp.id === action.payload.id ? action.payload : opp
        )
      };

    case CRM_ACTIONS.DELETE_OPPORTUNITY:
      return {
        ...state,
        opportunities: (state.opportunities || []).filter(opp => opp.id !== action.payload)
      };

    case CRM_ACTIONS.MOVE_OPPORTUNITY:
      return {
        ...state,
        opportunities: state.opportunities.map(opp =>
          opp.id === action.payload.id
            ? { ...opp, stage: action.payload.newStage, updated_at: new Date().toISOString() }
            : opp
        )
      };

    case CRM_ACTIONS.ADD_TASK:
      return {
        ...state,
        tasks: [...state.tasks, action.payload]
      };

    case CRM_ACTIONS.UPDATE_TASK:
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id ? action.payload : task
        )
      };

    case CRM_ACTIONS.DELETE_TASK:
      return {
        ...state,
        tasks: (state.tasks || []).filter(task => task.id !== action.payload)
      };

    case CRM_ACTIONS.SET_FILTERS:
      return {
        ...state,
        filters: { ...state.filters, ...action.payload }
      };

    case CRM_ACTIONS.SET_SORT:
      return {
        ...state,
        sort: { ...state.sort, ...action.payload }
      };

    case CRM_ACTIONS.SET_VIEW:
      return {
        ...state,
        view: { ...state.view, ...action.payload }
      };

    default:
      return state;
  }
};

// CRM Provider
export const CRMProvider = ({ children }) => {
  const [state, dispatch] = useReducer(crmReducer, initialState);

  // API Functions
  const fetchContacts = useCallback(async () => {
    dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { contacts: true } });
    try {
      const response = await apiClient.get('/crm/contacts');
      dispatch({ type: CRM_ACTIONS.SET_CONTACTS, payload: response.data });
    } catch (error) {
      dispatch({
        type: CRM_ACTIONS.SET_ERROR,
        payload: { contacts: error.message }
      });
    } finally {
      dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { contacts: false } });
    }
  }, []);

  const fetchLeads = useCallback(async () => {
    dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { leads: true } });
    try {
      const response = await apiClient.get('/crm/leads');
      dispatch({ type: CRM_ACTIONS.SET_LEADS, payload: response.data });
    } catch (error) {
      dispatch({
        type: CRM_ACTIONS.SET_ERROR,
        payload: { leads: error.message }
      });
    } finally {
      dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { leads: false } });
    }
  }, []);

  const fetchOpportunities = useCallback(async () => {
    dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { opportunities: true } });
    try {
      const response = await apiClient.get('/crm/opportunities');
      dispatch({ type: CRM_ACTIONS.SET_OPPORTUNITIES, payload: response.data });
    } catch (error) {
      dispatch({
        type: CRM_ACTIONS.SET_ERROR,
        payload: { opportunities: error.message }
      });
    } finally {
      dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { opportunities: false } });
    }
  }, []);

  const fetchPipelines = useCallback(async () => {
    dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { pipelines: true } });
    try {
      const response = await apiClient.get('/crm/pipelines');
      dispatch({ type: CRM_ACTIONS.SET_PIPELINES, payload: response.data });
    } catch (error) {
      dispatch({
        type: CRM_ACTIONS.SET_ERROR,
        payload: { pipelines: error.message }
      });
    } finally {
      dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { pipelines: false } });
    }
  }, []);

  const fetchTasks = useCallback(async () => {
    dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { tasks: true } });
    try {
      const response = await apiClient.get('/crm/tasks');
      dispatch({ type: CRM_ACTIONS.SET_TASKS, payload: response.data });
    } catch (error) {
      dispatch({
        type: CRM_ACTIONS.SET_ERROR,
        payload: { tasks: error.message }
      });
    } finally {
      dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { tasks: false } });
    }
  }, []);

  const fetchAnalytics = useCallback(async () => {
    dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { analytics: true } });
    try {
      const response = await apiClient.get('/crm/analytics');
      dispatch({ type: CRM_ACTIONS.SET_ANALYTICS, payload: response.data });
    } catch (error) {
      dispatch({
        type: CRM_ACTIONS.SET_ERROR,
        payload: { analytics: error.message }
      });
    } finally {
      dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { analytics: false } });
    }
  }, []);

  const fetchLeadIntakes = useCallback(async () => {
    dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { leadIntakes: true } });
    try {
      const response = await apiClient.get('/crm/lead-intake');
      dispatch({ type: CRM_ACTIONS.SET_LEAD_INTAKES, payload: response.data });
    } catch (error) {
      dispatch({
        type: CRM_ACTIONS.SET_ERROR,
        payload: { leadIntakes: error.message }
      });
    } finally {
      dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { leadIntakes: false } });
    }
  }, []);

  const fetchUsers = useCallback(async () => {
    dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { users: true } });
    try {
      const response = await apiClient.get('/crm/users');
      dispatch({ type: CRM_ACTIONS.SET_USERS, payload: response.data });
    } catch (error) {
      dispatch({
        type: CRM_ACTIONS.SET_ERROR,
        payload: { users: error.message }
      });
    } finally {
      dispatch({ type: CRM_ACTIONS.SET_LOADING, payload: { users: false } });
    }
  }, []);

  // CRUD Operations
  const createContact = useCallback(async (contactData) => {
    try {
      const response = await apiClient.post('/crm/contacts', contactData);
      dispatch({ type: CRM_ACTIONS.ADD_CONTACT, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const updateContact = useCallback(async (id, contactData) => {
    try {
      const response = await apiClient.put(`/crm/contacts/${id}`, contactData);
      dispatch({ type: CRM_ACTIONS.UPDATE_CONTACT, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const deleteContact = useCallback(async (id) => {
    try {
      await apiClient.delete(`/crm/contacts/${id}`);
      dispatch({ type: CRM_ACTIONS.DELETE_CONTACT, payload: id });
    } catch (error) {
      throw error;
    }
  }, []);

  const createLead = useCallback(async (leadData) => {
    try {
      const response = await apiClient.post('/crm/leads', leadData);
      dispatch({ type: CRM_ACTIONS.ADD_LEAD, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const updateLead = useCallback(async (id, leadData) => {
    try {
      const response = await apiClient.put(`/crm/leads/${id}`, leadData);
      dispatch({ type: CRM_ACTIONS.UPDATE_LEAD, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const deleteLead = useCallback(async (id) => {
    try {
      await apiClient.delete(`/crm/leads/${id}`);
      dispatch({ type: CRM_ACTIONS.DELETE_LEAD, payload: id });
    } catch (error) {
      throw error;
    }
  }, []);

  const createOpportunity = useCallback(async (opportunityData) => {
    try {
      const response = await apiClient.post('/crm/opportunities', opportunityData);
      dispatch({ type: CRM_ACTIONS.ADD_OPPORTUNITY, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const updateOpportunity = useCallback(async (id, opportunityData) => {
    try {
      const response = await apiClient.put(`/crm/opportunities/${id}`, opportunityData);
      dispatch({ type: CRM_ACTIONS.UPDATE_OPPORTUNITY, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const deleteOpportunity = useCallback(async (id) => {
    try {
      await apiClient.delete(`/crm/opportunities/${id}`);
      dispatch({ type: CRM_ACTIONS.DELETE_OPPORTUNITY, payload: id });
    } catch (error) {
      throw error;
    }
  }, []);

  const moveOpportunity = useCallback(async (id, newStage) => {
    try {
      const response = await apiClient.patch(`/crm/opportunities/${id}/move`, { stage: newStage });
      dispatch({ type: CRM_ACTIONS.MOVE_OPPORTUNITY, payload: { id, newStage } });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const createLeadIntake = useCallback(async (intakeData) => {
    try {
      const response = await apiClient.post('/crm/lead-intake', intakeData);
      dispatch({ type: CRM_ACTIONS.ADD_LEAD_INTAKE, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  const updateLeadIntake = useCallback(async (id, intakeData) => {
    try {
      const response = await apiClient.put(`/crm/lead-intake/${id}`, intakeData);
      dispatch({ type: CRM_ACTIONS.UPDATE_LEAD_INTAKE, payload: response.data });
      return response.data;
    } catch (error) {
      throw error;
    }
  }, []);

  // Utility Functions
  const getOpportunitiesByStage = useCallback((stage) => {
    return (state.opportunities || []).filter(opp => opp.stage === stage);
  }, [state.opportunities]);

  const getTasksByContext = useCallback((contextType, contextId) => {
    return (state.tasks || []).filter(task =>
      task.context_type === contextType && task.context_id === contextId
    );
  }, [state.tasks]);

  const getContactActivities = useCallback((contactId) => {
    return (state.activities || []).filter(activity => activity.contact_id === contactId);
  }, [state.activities]);

  const refreshAllData = useCallback(async () => {
    await Promise.all([
      fetchContacts(),
      fetchLeads(),
      fetchOpportunities(),
      fetchPipelines(),
      fetchTasks(),
      fetchAnalytics(),
      fetchLeadIntakes(),
      fetchUsers()
    ]);
  }, [fetchContacts, fetchLeads, fetchOpportunities, fetchPipelines, fetchTasks, fetchAnalytics, fetchLeadIntakes, fetchUsers]);

  // Initialize data on mount
  useEffect(() => {
    try {
      refreshAllData();
    } catch (error) {
      console.error('Error initializing CRM data:', error);
    }
  }, [refreshAllData]);

  const value = {
    // State
    ...state,
    contacts: state.contacts || [],
    leads: state.leads || [],
    opportunities: state.opportunities || [],
    pipelines: state.pipelines || [],
    stages: state.stages || [],
    tasks: state.tasks || [],
    activities: state.activities || [],
    analytics: state.analytics || {},
    leadIntakes: state.leadIntakes || [],
    users: state.users || [],

    // Actions
    fetchContacts,
    fetchLeads,
    fetchOpportunities,
    fetchPipelines,
    fetchLeadIntakes,
    fetchUsers,
    fetchTasks,
    fetchAnalytics,
    createContact,
    updateContact,
    deleteContact,
    createLead,
    updateLead,
    deleteLead,
    createOpportunity,
    updateOpportunity,
    deleteOpportunity,
    moveOpportunity,
    createLeadIntake,
    updateLeadIntake,
    refreshAllData,

    // Utility Functions
    getOpportunitiesByStage,
    getTasksByContext,
    getContactActivities,

    // UI Actions
    setFilters: (filters) => dispatch({ type: CRM_ACTIONS.SET_FILTERS, payload: filters }),
    setSort: (sort) => dispatch({ type: CRM_ACTIONS.SET_SORT, payload: sort }),
    setView: (view) => dispatch({ type: CRM_ACTIONS.SET_VIEW, payload: view })
  };

  return (
    <CRMContext.Provider value={value}>
      {children}
    </CRMContext.Provider>
  );
};

// Hook
export const useCRM = () => {
  const context = useContext(CRMContext);
  if (!context) {
    throw new Error('useCRM must be used within a CRMProvider');
  }
  return context;
};
