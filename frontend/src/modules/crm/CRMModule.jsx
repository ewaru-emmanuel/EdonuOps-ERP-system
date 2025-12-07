import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme, TextField, FormControl, InputLabel, Select, MenuItem
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Person as PersonIcon,
  Business as BusinessIcon,
  TrendingUp as TrendingUpIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  Menu as MenuIcon,
  Assessment as AssessmentIcon,
  People as PeopleIcon,
  Work as WorkIcon,
  Timeline as TimelineIcon,
  Assignment as AssignmentIcon,
  Support as SupportIcon,
  BarChart as BarChartIcon,
  AutoAwesome as AutoAwesomeIcon,
  School as SchoolIcon,
  DataObject as DataObjectIcon
} from '@mui/icons-material';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';
import { apiClient } from '../../utils/apiClient';
import CRMPipeline from './CRMPipeline';
import CRMCommunicationHistory from './CRMCommunicationHistory';
import CRMCompanies from './CRMCompanies';

const CRMModule = () => {
  const [searchParams] = useSearchParams();
  const feature = searchParams.get('feature') || 'contacts';
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [leadFiltersOpen, setLeadFiltersOpen] = useState(false);
  const [leadFilters, setLeadFilters] = useState({ minScore: '', region: '', assignedTeam: '' });
  const [savedLeadFilters, setSavedLeadFilters] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('crm_saved_filters_leads') || '[]');
    } catch { return []; }
  });
  const [leadFilterName, setLeadFilterName] = useState('');
  const [leadSaveDialogOpen, setLeadSaveDialogOpen] = useState(false);
  const [contactFiltersOpen, setContactFiltersOpen] = useState(false);
  const [contactFilters, setContactFilters] = useState({ region: '', assignedTeam: '', type: '', status: '' });
  const [oppFiltersOpen, setOppFiltersOpen] = useState(false);
  const [oppFilters, setOppFilters] = useState({ region: '', assignedTeam: '', stage: '' });
  const [savedOppFilters, setSavedOppFilters] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('crm_saved_filters_opps') || '[]');
    } catch { return []; }
  });
  const [oppFilterName, setOppFilterName] = useState('');
  const [oppSaveDialogOpen, setOppSaveDialogOpen] = useState(false);
  const [marketingOpen, setMarketingOpen] = useState(false);
  const [sender, setSender] = useState({ from_email: '', from_name: '' });
  const [segmentForm, setSegmentForm] = useState({ name: '', criteria: '' });
  const [templateForm, setTemplateForm] = useState({ name: '', subject: '', body: '' });
  const [campaignForm, setCampaignForm] = useState({ name: '', segment_id: '', template_id: '', scheduled_for: '' });
  const [ticketDialogOpen, setTicketDialogOpen] = useState(false);
  const [editingTicket, setEditingTicket] = useState(null);
  const [ticketForm, setTicketForm] = useState({ subject: '', description: '', status: 'open', priority: 'medium', category: '', tags: '', customer_email: '', contact_id: '', lead_id: '', opportunity_id: '' });
  const [sequences, setSequences] = useState([]);
  const [sequenceForm, setSequenceForm] = useState({ name: '', steps: '' });
  const [importOpen, setImportOpen] = useState(false);
  const [importEntity, setImportEntity] = useState('contacts');
  const [importMapping, setImportMapping] = useState('');
  const [csvText, setCsvText] = useState('');
  const [importSummary, setImportSummary] = useState(null);
  const [importErrors, setImportErrors] = useState([]);
  const [aiMappingLoading, setAiMappingLoading] = useState(false);
  const [forecast, setForecast] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [funnel, setFunnel] = useState(null);
  const [stuck, setStuck] = useState({ days: 30, deals: [], count: 0 });
  const [workflowsUI, setWorkflowsUI] = useState([]);
  const [workflowBuilderOpen, setWorkflowBuilderOpen] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState(null);
  const [builderData, setBuilderData] = useState({ name: '', trigger_id: '', actions: [], conditions: [] });
  const [schedules, setSchedules] = useState([]);
  const [scheduleForm, setScheduleForm] = useState({ name: '', cron: '0 9 * * *', workflow_id: '' });
  const [dqEntity, setDqEntity] = useState('contacts');
  const [dqGroups, setDqGroups] = useState([]);
  const [slaDialogOpen, setSlaDialogOpen] = useState(false);
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [slaPolicy, setSlaPolicy] = useState({ first_response_minutes: 60, resolve_minutes: 1440 });
  const [assignment, setAssignment] = useState({ strategy: 'round_robin', agents: [] });
  const [assignmentAgentsInput, setAssignmentAgentsInput] = useState('');
  const [taskDialogOpen, setTaskDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [taskForm, setTaskForm] = useState({ type: 'task', notes: '', due_date: '', status: 'pending', contact_id: '', lead_id: '', opportunity_id: '' });
  const [taskFilters, setTaskFilters] = useState({ status: '', type: '' });
  const [savedTaskFilters, setSavedTaskFilters] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('crm_saved_filters_tasks') || '[]');
    } catch { return []; }
  });
  const [taskFilterName, setTaskFilterName] = useState('');
  const [taskSaveDialogOpen, setTaskSaveDialogOpen] = useState(false);
  const [kbArticles, setKbArticles] = useState([]);
  const [kbQuery, setKbQuery] = useState('');
  const [kbDialogOpen, setKbDialogOpen] = useState(false);
  const [editingArticle, setEditingArticle] = useState(null);
  const [kbForm, setKbForm] = useState({ title: '', content: '', tags: '', published: false });
  const [kbFile, setKbFile] = useState(null);
  const [ticketFilters, setTicketFilters] = useState({ status: '', priority: '', category: '' });
  const [savedTicketFilters, setSavedTicketFilters] = useState(() => {
    try { return JSON.parse(localStorage.getItem('crm_saved_filters_tickets') || '[]'); } catch { return []; }
  });
  const [ticketFilterName, setTicketFilterName] = useState('');
  const [ticketSaveDialogOpen, setTicketSaveDialogOpen] = useState(false);
  // In development, use full URL to backend; in production, use relative URLs
  const isDevelopment = process.env.NODE_ENV === 'development' || !process.env.NODE_ENV;
  const API_BASE = process.env.REACT_APP_API_BASE || process.env.REACT_APP_API_URL || 
                  (isDevelopment ? process.env.REACT_APP_API_URL || '' : '');
  
  // Form and dialog states
  const [formOpen, setFormOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteItem, setDeleteItem] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedItemType, setSelectedItemType] = useState('');

  // Load companies to map company name -> company_id on save
  const {
    data: companies,
  } = useRealTimeData('/api/crm/companies');

  // Real-time data hooks
  const { 
    data: contacts, 
    loading: contactsLoading, 
    error: contactsError,
    create: createContact,
    update: updateContact,
    remove: deleteContact
  } = useRealTimeData('/api/crm/contacts');
  
  const { 
    data: leads, 
    loading: leadsLoading, 
    error: leadsError,
    create: createLead,
    update: updateLead,
    remove: deleteLead
  } = useRealTimeData('/api/crm/leads');
  
  const { 
    data: opportunities, 
    loading: opportunitiesLoading, 
    error: opportunitiesError,
    create: createOpportunity,
    update: updateOpportunity,
    remove: deleteOpportunity
  } = useRealTimeData('/api/crm/opportunities');
  const {
    data: tickets,
    loading: ticketsLoading,
    error: ticketsError,
    create: createTicket,
    update: updateTicket,
    remove: deleteTicket
  } = useRealTimeData('/api/crm/tickets');

  const {
    data: tasks,
    loading: tasksLoading,
    error: tasksError,
    create: createTaskRT,
    update: updateTaskRT,
    remove: deleteTaskRT
  } = useRealTimeData('/api/crm/tasks');

  // CRM features configuration
  const crmFeatures = [
    { id: 'contacts', label: 'Contacts', icon: <PersonIcon /> },
    { id: 'leads', label: 'Leads', icon: <PeopleIcon /> },
    { id: 'opportunities', label: 'Opportunities', icon: <TrendingUpIcon /> },
    { id: 'pipeline', label: 'Pipeline', icon: <TimelineIcon /> },
    { id: 'companies', label: 'Companies', icon: <BusinessIcon /> },
    { id: 'activities', label: 'Activities', icon: <AssignmentIcon /> },
    { id: 'tasks', label: 'Tasks', icon: <AssignmentIcon /> },
    { id: 'tickets', label: 'Tickets', icon: <SupportIcon /> },
    { id: 'reports', label: 'Reports', icon: <BarChartIcon /> },
    { id: 'automations', label: 'Automations', icon: <AutoAwesomeIcon /> },
    { id: 'knowledge-base', label: 'Knowledge Base', icon: <SchoolIcon /> },
    { id: 'data-quality', label: 'Data Quality', icon: <DataObjectIcon /> }
  ];

  const renderFeature = () => {
    switch (feature) {
      case 'contacts':
        return renderContactsTab();
      case 'leads':
        return renderLeadsTab();
      case 'opportunities':
        return renderOpportunitiesTab();
      case 'pipeline':
        return renderPipelineTab();
      case 'companies':
        return <CRMCompanies />;
      case 'activities':
        return <CRMCommunicationHistory onOpenEntityDetail={openEntityDetail} />;
      case 'tasks':
        return renderTasksTab();
      case 'tickets':
        return renderTicketsTab();
      case 'reports':
        return renderReportsTab();
      case 'automations':
        return renderAutomationsTab();
      case 'knowledge-base':
        return renderKnowledgeBaseTab();
      case 'data-quality':
        return renderDataQualityTab();
      default:
        return renderContactsTab();
    }
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };
  const handleExport = async (entity) => {
    try {
      const url = `${API_BASE}/api/crm/exports/${entity}`;
      const res = await fetch(url, { method: 'GET' });
      if (!res.ok) throw new Error(`Export failed (${res.status})`);
      const blob = await res.blob();
      const link = document.createElement('a');
      const dlUrl = window.URL.createObjectURL(blob);
      link.href = dlUrl;
      link.download = `crm_${entity}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(dlUrl);
    } catch (e) {
      showSnackbar(e.message || 'Export failed', 'error');
    }
  };

  const openMarketing = async () => {
    try {
      const current = await apiClient.get('/api/crm/marketing/sender');
      setSender({ from_email: current.from_email || '', from_name: current.from_name || '' });
    } catch {
      setSender({ from_email: '', from_name: '' });
    }
    try {
      const list = await apiClient.get('/api/crm/marketing/sequences');
      setSequences(Array.isArray(list) ? list : (list?.data || []));
    } catch {
      setSequences([]);
    }
    setMarketingOpen(true);
  };

  const saveSender = async () => {
    try {
      await apiClient.post('/api/crm/marketing/sender', sender);
      showSnackbar('Sender updated');
    } catch (e) {
      showSnackbar(e.message || 'Failed to save sender', 'error');
    }
  };

  const createSegment = async () => {
    try {
      const payload = { name: segmentForm.name, criteria: segmentForm.criteria ? JSON.parse(segmentForm.criteria) : {} };
      await apiClient.post('/api/crm/marketing/segments', payload);
      setSegmentForm({ name: '', criteria: '' });
      showSnackbar('Segment created');
    } catch (e) {
      showSnackbar(e.message || 'Failed to create segment', 'error');
    }
  };

  const createTemplate = async () => {
    try {
      await apiClient.post('/api/crm/marketing/templates', templateForm);
      setTemplateForm({ name: '', subject: '', body: '' });
      showSnackbar('Template created');
    } catch (e) {
      showSnackbar(e.message || 'Failed to create template', 'error');
    }
  };

  const createCampaign = async () => {
    try {
      await apiClient.post('/api/crm/marketing/campaigns', campaignForm);
      setCampaignForm({ name: '', segment_id: '', template_id: '', scheduled_for: '' });
      showSnackbar('Campaign created');
    } catch (e) {
      showSnackbar(e.message || 'Failed to create campaign', 'error');
    }
  };
  const createSequence = async () => {
    try {
      const payload = {
        name: sequenceForm.name,
        steps: sequenceForm.steps ? JSON.parse(sequenceForm.steps) : []
      };
      const res = await apiClient.post('/api/crm/marketing/sequences', payload);
      const created = res?.data || res;
      setSequences([...(Array.isArray(sequences) ? sequences : []), created]);
      setSequenceForm({ name: '', steps: '' });
      showSnackbar('Sequence created');
    } catch (e) {
      showSnackbar(e.message || 'Failed to create sequence (ensure valid JSON steps)', 'error');
    }
  };
  const fetchKB = async () => {
    try {
      const qs = kbQuery ? `?q=${encodeURIComponent(kbQuery)}` : '';
      const res = await fetch(`${API_BASE}/api/crm/kb/articles${qs}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setKbArticles(data);
    } catch (e) {
      showSnackbar(e.message || 'Failed to load articles', 'error');
    }
  };
  const saveKB = async () => {
    try {
      if (editingArticle) {
        const res = await fetch(`${API_BASE}/api/crm/kb/articles/${editingArticle.id}`, {
          method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(kbForm)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed');
        showSnackbar('Article updated');
      } else {
        const res = await fetch(`${API_BASE}/api/crm/kb/articles`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(kbForm)
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed');
        showSnackbar('Article created');
      }
      setKbDialogOpen(false);
      setEditingArticle(null);
      setKbForm({ title: '', content: '', tags: '' });
      await fetchKB();
    } catch (e) {
      showSnackbar(e.message || 'Failed to save article', 'error');
    }
  };
  const deleteKB = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/kb/articles/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      showSnackbar('Article deleted');
      await fetchKB();
    } catch (e) {
      showSnackbar(e.message || 'Failed to delete article', 'error');
    }
  };
  const uploadKBAttachment = async (articleId) => {
    if (!kbFile) return;
    try {
      const form = new FormData();
      form.append('file', kbFile);
      const res = await fetch(`${API_BASE}/api/crm/kb/articles/${articleId}/attachments`, { method: 'POST', body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      showSnackbar('Attachment uploaded');
      setKbFile(null);
    } catch (e) {
      showSnackbar(e.message || 'Failed to upload attachment', 'error');
    }
  };
  const runImport = async (dryRun = true) => {
    try {
      if (!csvText.trim()) {
        showSnackbar('Please paste CSV content', 'warning');
        return;
      }
      let mappingObj = null;
      if (importMapping && importMapping.trim()) {
        try {
          mappingObj = JSON.parse(importMapping);
        } catch (e) {
          showSnackbar('Invalid mapping JSON', 'error');
          return;
        }
      }
      const res = await fetch(`${API_BASE}/api/crm/imports/${importEntity}?dry_run=${dryRun ? 'true' : 'false'}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ csv: csvText, mapping: mappingObj })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Import failed');
      if (dryRun) {
        setImportSummary(data.summary);
        setImportErrors(data.summary ? data.summary.errors || [] : []);
        showSnackbar('Validation complete');
      } else {
        setImportSummary(data.summary);
        setImportErrors(data.writeErrors || []);
        showSnackbar('Import completed');
      }
    } catch (e) {
      showSnackbar(e.message || 'Import failed', 'error');
    }
  };

  const suggestMapping = async () => {
    try {
      if (!csvText.trim()) {
        showSnackbar('Paste CSV first', 'warning');
        return;
      }
      // Take headers from first CSV line
      const firstLine = csvText.trim().split(/\r?\n/)[0] || '';
      const headers = firstLine.split(',').map(h => h.trim()).filter(Boolean);
      if (headers.length === 0) {
        showSnackbar('Could not detect headers', 'error');
        return;
      }
      setAiMappingLoading(true);
      const res = await fetch(`${API_BASE}/api/crm/ai/suggest-mapping`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entity: importEntity, headers })
      });
      const data = await res.json();
      const mapping = (data && data.mapping) ? data.mapping : {};
      setImportMapping(JSON.stringify(mapping, null, 2));
      showSnackbar('Suggested mapping generated');
    } catch (e) {
      showSnackbar(e.message || 'Failed to suggest mapping', 'error');
    } finally {
      setAiMappingLoading(false);
    }
  };

  const fetchForecast = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/reports/forecast`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setForecast(data);
    } catch (e) {
      showSnackbar(e.message || 'Failed to load forecast', 'error');
    }
  };

  const fetchPerformance = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/reports/performance`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setPerformance(data);
    } catch (e) {
      showSnackbar(e.message || 'Failed to load performance', 'error');
    }
  };

  const fetchFunnel = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/reports/funnel`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setFunnel(data);
    } catch (e) {
      showSnackbar(e.message || 'Failed to load funnel', 'error');
    }
  };

  const fetchStuck = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/reports/stuck?days=${stuck.days}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setStuck({ ...stuck, ...data });
    } catch (e) {
      showSnackbar(e.message || 'Failed to load stuck deals', 'error');
    }
  };

  const fetchWorkflowsUI = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/workflows`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setWorkflowsUI(data);
    } catch (e) {
      showSnackbar(e.message || 'Failed to load workflows', 'error');
    }
  };

  const toggleWorkflowUI = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/workflows/${id}/toggle`, { method: 'PATCH' });
      await res.json();
      await fetchWorkflowsUI();
      showSnackbar('Workflow toggled');
    } catch (e) {
      showSnackbar(e.message || 'Failed to toggle workflow', 'error');
    }
  };

  const deleteWorkflowUI = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/workflows/${id}`, { method: 'DELETE' });
      await res.json();
      await fetchWorkflowsUI();
      showSnackbar('Workflow deleted');
    } catch (e) {
      showSnackbar(e.message || 'Failed to delete workflow', 'error');
    }
  };

  const openWorkflowBuilderUI = (wf) => {
    setEditingWorkflow(wf);
    setBuilderData(wf ? { name: wf.name || '', trigger_id: wf.trigger?.id || '', actions: wf.actions || [], conditions: wf.conditions || [] } : { name: '', trigger_id: '', actions: [], conditions: [] });
    setWorkflowBuilderOpen(true);
  };

  const saveWorkflowUI = async () => {
    try {
      const payload = { name: builderData.name, trigger: { id: builderData.trigger_id }, actions: builderData.actions, conditions: builderData.conditions };
      if (editingWorkflow) {
        const res = await fetch(`${API_BASE}/api/crm/workflows/${editingWorkflow.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        await res.json();
      } else {
        const res = await fetch(`${API_BASE}/api/crm/workflows`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        await res.json();
      }
      setWorkflowBuilderOpen(false);
      setEditingWorkflow(null);
      await fetchWorkflowsUI();
      showSnackbar('Workflow saved');
    } catch (e) {
      showSnackbar(e.message || 'Failed to save workflow', 'error');
    }
  };

  const fetchSchedules = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/workflows/schedules`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setSchedules(data);
    } catch (e) {
      showSnackbar(e.message || 'Failed to load schedules', 'error');
    }
  };

  const createSchedule = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/workflows/schedules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scheduleForm)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      await fetchSchedules();
      setScheduleForm({ name: '', cron: '0 9 * * *', workflow_id: '' });
      showSnackbar('Schedule created');
    } catch (e) {
      showSnackbar(e.message || 'Failed to create schedule', 'error');
    }
  };

  const fetchDuplicates = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/data-quality/duplicates?entity=${dqEntity}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setDqGroups(data.groups || []);
      showSnackbar(`Found ${data.groupCount || 0} duplicate groups`);
    } catch (e) {
      showSnackbar(e.message || 'Failed to fetch duplicates', 'error');
    }
  };

  const mergePair = async (targetId, sourceId) => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/data-quality/merge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entity: dqEntity, target_id: targetId, source_id: sourceId })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      showSnackbar('Merged successfully');
      await fetchDuplicates();
    } catch (e) {
      showSnackbar(e.message || 'Failed to merge', 'error');
    }
  };

  const openSLASettings = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/tickets/sla-policy`);
      const data = await res.json();
      if (res.ok) setSlaPolicy({
        first_response_minutes: Number(data.first_response_minutes || 60),
        resolve_minutes: Number(data.resolve_minutes || 1440)
      });
    } catch {}
    setSlaDialogOpen(true);
  };

  const saveSlaPolicy = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/tickets/sla-policy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(slaPolicy)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      showSnackbar('SLA policy saved');
      setSlaDialogOpen(false);
    } catch (e) {
      showSnackbar(e.message || 'Failed to save SLA policy', 'error');
    }
  };

  const openAssignmentSettings = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/crm/tickets/assignment`);
      const data = await res.json();
      if (res.ok) {
        setAssignment({ strategy: data.strategy || 'round_robin', agents: data.agents || [] });
        setAssignmentAgentsInput((data.agents || []).join(','));
      }
    } catch {}
    setAssignDialogOpen(true);
  };

  const saveAssignment = async () => {
    try {
      const agentsArr = assignmentAgentsInput
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean)
        .map((s) => Number(s))
        .filter((n) => !Number.isNaN(n));
      const res = await fetch(`${API_BASE}/api/crm/tickets/assignment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy: assignment.strategy, agents: agentsArr })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      showSnackbar('Assignment saved');
      setAssignDialogOpen(false);
    } catch (e) {
      showSnackbar(e.message || 'Failed to save assignment', 'error');
    }
  };

  const saveLeadsFilterPreset = () => {
    const name = (leadFilterName || '').trim();
    if (!name) return;
    const next = [...savedLeadFilters.filter(f => f.name !== name), { name, value: leadFilters }];
    setSavedLeadFilters(next);
    try { localStorage.setItem('crm_saved_filters_leads', JSON.stringify(next)); } catch {}
    setLeadSaveDialogOpen(false);
    setLeadFilterName('');
    showSnackbar('Lead filter saved');
  };

  const applyLeadsFilterPreset = (name) => {
    const f = (savedLeadFilters || []).find(x => x.name === name);
    if (f) setLeadFilters(f.value || { minScore: '', region: '', assignedTeam: '' });
  };

  const saveTasksFilterPreset = () => {
    const name = (taskFilterName || '').trim();
    if (!name) return;
    const next = [...savedTaskFilters.filter(f => f.name !== name), { name, value: taskFilters }];
    setSavedTaskFilters(next);
    try { localStorage.setItem('crm_saved_filters_tasks', JSON.stringify(next)); } catch {}
    setTaskSaveDialogOpen(false);
    setTaskFilterName('');
    showSnackbar('Task filter saved');
  };

  const applyTasksFilterPreset = (name) => {
    const f = (savedTaskFilters || []).find(x => x.name === name);
    if (f) setTaskFilters(f.value || { status: '', type: '' });
  };
  const saveOppsFilterPreset = () => {
    const name = (oppFilterName || '').trim();
    if (!name) return;
    const next = [...savedOppFilters.filter(f => f.name !== name), { name, value: oppFilters }];
    setSavedOppFilters(next);
    try { localStorage.setItem('crm_saved_filters_opps', JSON.stringify(next)); } catch {}
    setOppSaveDialogOpen(false);
    setOppFilterName('');
    showSnackbar('Opportunity filter saved');
  };
  const applyOppsFilterPreset = (name) => {
    const f = (savedOppFilters || []).find(x => x.name === name);
    if (f) setOppFilters(f.value || { region: '', assignedTeam: '', stage: '' });
  };
  const saveTicketsFilterPreset = () => {
    const name = (ticketFilterName || '').trim();
    if (!name) return;
    const next = [...savedTicketFilters.filter(f => f.name !== name), { name, value: ticketFilters }];
    setSavedTicketFilters(next);
    try { localStorage.setItem('crm_saved_filters_tickets', JSON.stringify(next)); } catch {}
    setTicketSaveDialogOpen(false);
    setTicketFilterName('');
    showSnackbar('Ticket filter saved');
  };
  const applyTicketsFilterPreset = (name) => {
    const f = (savedTicketFilters || []).find(x => x.name === name);
    if (f) setTicketFilters(f.value || { status: '', priority: '', category: '' });
  };
  const openAddTicket = () => {
    setEditingTicket(null);
    setTicketForm({ subject: '', description: '', status: 'open', priority: 'medium', category: '', tags: '', customer_email: '', contact_id: '', lead_id: '', opportunity_id: '' });
    setTicketDialogOpen(true);
  };
  const openEditTicket = (t) => {
    setEditingTicket(t);
    setTicketForm({
      subject: t.subject || '',
      description: t.description || '',
      status: t.status || 'open',
      priority: t.priority || 'medium',
      contact_id: t.contact_id || '',
      lead_id: t.lead_id || '',
      opportunity_id: t.opportunity_id || ''
    });
    setTicketDialogOpen(true);
  };
  const saveTicket = async () => {
    try {
      const payload = {
        ...ticketForm,
        contact_id: ticketForm.contact_id || null,
        lead_id: ticketForm.lead_id || null,
        opportunity_id: ticketForm.opportunity_id || null
      };
      if (editingTicket) {
        await updateTicket(editingTicket.id, payload);
        showSnackbar('Ticket updated');
      } else {
        await createTicket(payload);
        showSnackbar('Ticket created');
      }
      setTicketDialogOpen(false);
      setEditingTicket(null);
    } catch (e) {
      showSnackbar(e.message || 'Failed to save ticket', 'error');
    }
  };
  const removeTicket = async (t) => {
    try {
      await deleteTicket(t.id);
      showSnackbar('Ticket deleted');
    } catch (e) {
      showSnackbar(e.message || 'Failed to delete ticket', 'error');
    }
  };


  const handleAdd = (type) => {
    setEditItem(null);
    setSelectedItemType(type);
    setFormOpen(true);
  };

  const handleEdit = (item, type) => {
    setEditItem(item);
    setSelectedItemType(type);
    setFormOpen(true);
  };

  const handleDelete = (item, type) => {
    setDeleteItem(item);
    setSelectedItemType(type);
    setDeleteDialogOpen(true);
  };

  const handleView = (item, type) => {
    setSelectedItem(item);
    setSelectedItemType(type);
    setDetailViewOpen(true);
  };

  const openEntityDetail = (type, id) => {
    if (!id) return;
    let item = null;
    switch (type) {
      case 'contact':
        item = (contacts || []).find((c) => c.id === id);
        break;
      case 'lead':
        item = (leads || []).find((l) => l.id === id);
        break;
      case 'opportunity':
        item = (opportunities || []).find((o) => o.id === id);
        break;
      case 'company':
        item = (companies || []).find((c) => c.id === id);
        break;
      default:
        break;
    }
    if (item) {
      handleView(item, type);
    } else {
      showSnackbar('Record not found in current list', 'warning');
    }
  };

  const handleSave = async (formData) => {
    try {
      const mapCompanyId = (data) => {
        try {
          const name = (data?.company || '').trim();
          if (!name || !Array.isArray(companies)) return data;
          const match = companies.find(c => (c.name || '').trim().toLowerCase() === name.toLowerCase());
          if (match) {
            return { ...data, company_id: match.id };
          }
          return data;
        } catch {
          return data;
        }
      };

      if (editItem) {
        switch (selectedItemType) {
          case 'contact':
            await updateContact(editItem.id, mapCompanyId(formData));
            showSnackbar(`Contact "${formData.first_name} ${formData.last_name}" updated successfully`);
            break;
          case 'lead':
            await updateLead(editItem.id, formData);
            showSnackbar(`Lead "${formData.first_name} ${formData.last_name}" updated successfully`);
            break;
          case 'opportunity':
            await updateOpportunity(editItem.id, mapCompanyId(formData));
            showSnackbar(`Opportunity "${formData.name}" updated successfully`);
            break;
          default:
            break;
        }
      } else {
        switch (selectedItemType) {
          case 'contact':
            await createContact(mapCompanyId(formData));
            showSnackbar(`Contact "${formData.first_name} ${formData.last_name}" created successfully`);
            break;
          case 'lead':
            await createLead(formData);
            showSnackbar(`Lead "${formData.first_name} ${formData.last_name}" created successfully`);
            break;
          case 'opportunity':
            await createOpportunity(mapCompanyId(formData));
            showSnackbar(`Opportunity "${formData.name}" created successfully`);
            break;
          default:
            break;
        }
      }
      setFormOpen(false);
      setEditItem(null);
    } catch (error) {
      showSnackbar(`Failed to save ${selectedItemType}: ${error.message}`, 'error');
    }
  };

  const handleConfirmDelete = async () => {
    try {
      switch (selectedItemType) {
        case 'contact':
          await deleteContact(deleteItem.id);
          showSnackbar(`Contact "${deleteItem.first_name} ${deleteItem.last_name}" deleted successfully`);
          break;
        case 'lead':
          await deleteLead(deleteItem.id);
          showSnackbar(`Lead "${deleteItem.first_name} ${deleteItem.last_name}" deleted successfully`);
          break;
        case 'opportunity':
          await deleteOpportunity(deleteItem.id);
          showSnackbar(`Opportunity "${deleteItem.name}" deleted successfully`);
          break;
        default:
          break;
      }
      setDeleteDialogOpen(false);
      setDeleteItem(null);
    } catch (error) {
      showSnackbar(`Failed to delete ${selectedItemType}: ${error.message}`, 'error');
    }
  };

  const handleMarkWon = async (opportunity) => {
    try {
      await apiClient.post(`/api/crm/deals/${opportunity.id}/win`, {});
      await updateOpportunity(opportunity.id, { stage: 'closed_won' });
      showSnackbar(`Opportunity "${opportunity.name}" marked as Won. Draft invoice created.`);
    } catch (error) {
      showSnackbar(`Failed to mark as won: ${error.message}`, 'error');
    }
  };

  // Calculate metrics from real data
  const crmMetrics = {
    totalContacts: contacts.length,
    totalLeads: leads.length,
    totalOpportunities: opportunities.length,
    totalValue: opportunities.reduce((sum, opp) => sum + (opp.amount || 0), 0),
    conversionRate: leads.length > 0 ? (opportunities.length / leads.length) * 100 : 0
  };

  const renderContactsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Contacts</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" onClick={() => handleExport('contacts')}>Export</Button>
          <Button variant="outlined" onClick={() => setContactFiltersOpen(true)}>
            Filters
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('contact')}
          >
            Add Contact
          </Button>
        </Box>
      </Box>

      {contactsLoading && <LinearProgress />}
      
      {contactsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {contactsError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Company</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {contacts
              .filter((c) => {
                const regionOk = contactFilters.region ? ((c.region || '').toLowerCase() === contactFilters.region.toLowerCase()) : true;
                const teamOk = contactFilters.assignedTeam ? ((c.assigned_team || '').toLowerCase() === contactFilters.assignedTeam.toLowerCase()) : true;
                const typeOk = contactFilters.type ? ((c.type || '').toLowerCase() === contactFilters.type.toLowerCase()) : true;
                const statusOk = contactFilters.status ? ((c.status || '').toLowerCase() === contactFilters.status.toLowerCase()) : true;
                return regionOk && teamOk && typeOk && statusOk;
              })
              .map((contact, index) => (
              <TableRow key={contact.id || `contact-${index}`}>
                <TableCell>{contact.first_name && contact.last_name ? `${contact.first_name} ${contact.last_name}` : ''}</TableCell>
                <TableCell>{contact.email || ''}</TableCell>
                <TableCell>{contact.phone || ''}</TableCell>
                <TableCell>{contact.company || ''}</TableCell>
                <TableCell>
                  {contact.type && (
                    <Chip
                      label={contact.type}
                      color={contact.type === 'customer' ? 'primary' : 'secondary'}
                      size="small"
                    />
                  )}
                </TableCell>
                <TableCell>
                  {contact.status && (
                    <Chip
                      label={contact.status}
                      color={contact.status === 'active' ? 'success' : 'default'}
                      size="small"
                    />
                  )}
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(contact, 'contact')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(contact, 'contact')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(contact, 'contact')} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderLeadsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Leads</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" onClick={() => handleExport('leads')}>Export</Button>
          <Button
            variant="outlined"
            onClick={() => setLeadFiltersOpen(true)}
          >
            Filters
          </Button>
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Saved Filters</InputLabel>
            <Select
              label="Saved Filters"
              value=""
              onChange={(e) => applyLeadsFilterPreset(e.target.value)}
            >
              <MenuItem value="">Select preset</MenuItem>
              {(savedLeadFilters || []).map((p) => (
                <MenuItem key={p.name} value={p.name}>{p.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="outlined" onClick={() => setLeadSaveDialogOpen(true)}>Save Filter</Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('lead')}
          >
            Add Lead
          </Button>
        </Box>
      </Box>

      {leadsLoading && <LinearProgress />}
      
      {leadsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {leadsError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Phone</TableCell>
              <TableCell>Company</TableCell>
              <TableCell>Score</TableCell>
              <TableCell>Source</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {leads
              .filter((lead) => {
                const scoreOk = leadFilters.minScore !== '' ? (Number(lead.score || 0) >= Number(leadFilters.minScore)) : true;
                const regionOk = leadFilters.region ? ((lead.region || '').toLowerCase() === leadFilters.region.toLowerCase()) : true;
                const teamOk = leadFilters.assignedTeam ? ((lead.assigned_team || '').toLowerCase() === leadFilters.assignedTeam.toLowerCase()) : true;
                return scoreOk && regionOk && teamOk;
              })
              .map((lead, index) => (
              <TableRow key={lead.id || `lead-${index}`}>
                <TableCell>{lead.first_name && lead.last_name ? `${lead.first_name} ${lead.last_name}` : ''}</TableCell>
                <TableCell>{lead.email || ''}</TableCell>
                <TableCell>{lead.phone || ''}</TableCell>
                <TableCell>{lead.company || ''}</TableCell>
                <TableCell>
                  <Chip 
                    label={typeof lead.score === 'number' ? lead.score : '—'}
                    color={lead.score >= 80 ? 'success' : (lead.score >= 50 ? 'info' : 'default')}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {lead.source && (
                    <Chip
                      label={lead.source}
                      color="info"
                      size="small"
                    />
                  )}
                </TableCell>
                <TableCell>
                  <Chip
                    label={lead.status || 'new'}
                    color={lead.status === 'new' ? 'warning' : 'success'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(lead, 'lead')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(lead, 'lead')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(lead, 'lead')} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderLeadFiltersDialog = () => (
    <Dialog open={leadFiltersOpen} onClose={() => setLeadFiltersOpen(false)} maxWidth="sm" fullWidth fullScreen={typeof window !== 'undefined' ? window.matchMedia('(max-width:600px)').matches : false}>
      <DialogTitle>Advanced Lead Filters</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
          <TextField
            label="Min Score"
            type="number"
            value={leadFilters.minScore}
            onChange={(e) => setLeadFilters({ ...leadFilters, minScore: e.target.value })}
            fullWidth
          />
          <TextField
            label="Region"
            value={leadFilters.region}
            onChange={(e) => setLeadFilters({ ...leadFilters, region: e.target.value })}
            fullWidth
          />
          <TextField
            label="Assigned Team"
            value={leadFilters.assignedTeam}
            onChange={(e) => setLeadFilters({ ...leadFilters, assignedTeam: e.target.value })}
            fullWidth
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setLeadFilters({ minScore: '', region: '', assignedTeam: '' })}>Clear</Button>
        <Button variant="contained" onClick={() => setLeadFiltersOpen(false)}>Apply</Button>
      </DialogActions>
    </Dialog>
  );
  const renderTaskSaveDialog = () => (
    <Dialog open={taskSaveDialogOpen} onClose={() => setTaskSaveDialogOpen(false)} maxWidth="xs" fullWidth fullScreen={typeof window !== 'undefined' ? window.matchMedia('(max-width:600px)').matches : false}>
      <DialogTitle>Save Task Filter</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          label="Preset Name"
          fullWidth
          value={taskFilterName}
          onChange={(e) => setTaskFilterName(e.target.value)}
          sx={{ mt: 1 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setTaskSaveDialogOpen(false)}>Cancel</Button>
        <Button variant="contained" onClick={saveTasksFilterPreset} disabled={!taskFilterName.trim()}>Save</Button>
      </DialogActions>
    </Dialog>
  );

  const renderLeadSaveDialog = () => (
    <Dialog open={leadSaveDialogOpen} onClose={() => setLeadSaveDialogOpen(false)} maxWidth="xs" fullWidth fullScreen={typeof window !== 'undefined' ? window.matchMedia('(max-width:600px)').matches : false}>
      <DialogTitle>Save Lead Filter</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          label="Preset Name"
          fullWidth
          value={leadFilterName}
          onChange={(e) => setLeadFilterName(e.target.value)}
          sx={{ mt: 1 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setLeadSaveDialogOpen(false)}>Cancel</Button>
        <Button variant="contained" onClick={saveLeadsFilterPreset} disabled={!leadFilterName.trim()}>Save</Button>
      </DialogActions>
    </Dialog>
  );

  const renderOpportunitiesTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Opportunities</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" onClick={() => handleExport('opportunities')}>Export</Button>
          <Button variant="outlined" onClick={() => setOppFiltersOpen(true)}>
            Filters
          </Button>
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <InputLabel>Saved Filters</InputLabel>
            <Select label="Saved Filters" value="" onChange={(e) => applyOppsFilterPreset(e.target.value)}>
              <MenuItem value="">Select preset</MenuItem>
              {(savedOppFilters || []).map((p) => (
                <MenuItem key={p.name} value={p.name}>{p.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <Button variant="outlined" onClick={() => setOppSaveDialogOpen(true)}>Save Filter</Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleAdd('opportunity')}
          >
            Add Opportunity
          </Button>
        </Box>
      </Box>

      {opportunitiesLoading && <LinearProgress />}
      
      {opportunitiesError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {opportunitiesError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Stage</TableCell>
              <TableCell>Probability</TableCell>
              <TableCell>Close Date</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {opportunities
              .filter((o) => {
                const regionOk = oppFilters.region ? ((o.region || '').toLowerCase() === oppFilters.region.toLowerCase()) : true;
                const teamOk = oppFilters.assignedTeam ? ((o.assigned_team || '').toLowerCase() === oppFilters.assignedTeam.toLowerCase()) : true;
                const stageOk = oppFilters.stage ? ((o.stage || '').toLowerCase() === oppFilters.stage.toLowerCase()) : true;
                return regionOk && teamOk && stageOk;
              })
              .map((opportunity, index) => (
              <TableRow key={opportunity.id || `opportunity-${index}`}>
                <TableCell>{opportunity.name || ''}</TableCell>
                <TableCell>
                  {opportunity.contact_id && (
                    <Chip size="small" label={`Contact #${opportunity.contact_id}`} clickable onClick={() => openEntityDetail('contact', opportunity.contact_id)} sx={{ mr: 0.5 }} />
                  )}
                  {opportunity.company_id && (
                    <Chip size="small" label={`Company #${opportunity.company_id}`} clickable onClick={() => openEntityDetail('company', opportunity.company_id)} />
                  )}
                </TableCell>
                <TableCell>${opportunity.amount || ''}</TableCell>
                <TableCell>
                  {opportunity.stage && (
                    <Chip
                      label={opportunity.stage}
                      color={opportunity.stage === 'closed' ? 'success' : 'primary'}
                      size="small"
                    />
                  )}
                </TableCell>
                <TableCell>{opportunity.probability ? `${opportunity.probability}%` : ''}</TableCell>
                <TableCell>
                  {opportunity.expected_close_date ? new Date(opportunity.expected_close_date).toLocaleDateString() : ''}
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(opportunity, 'opportunity')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(opportunity, 'opportunity')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  {opportunity.stage !== 'closed_won' && opportunity.stage !== 'closed_lost' && (
                    <Tooltip title="Mark as Won">
                      <Button 
                        onClick={() => handleMarkWon(opportunity)} 
                        color="success" 
                        variant="contained" 
                        size="small"
                        sx={{ mr: 1 }}
                      >
                        Mark Won
                      </Button>
                    </Tooltip>
                  )}
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(opportunity, 'opportunity')} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderPipelineTab = () => (
    <Box>
      <CRMPipeline />
    </Box>
  );

  // Missing handler functions
  const handleDeleteTask = async (taskId) => {
    try {
      await deleteTaskRT(taskId);
      showSnackbar('Task deleted successfully');
    } catch (error) {
      showSnackbar('Failed to delete task', 'error');
    }
  };

  const handleDeleteTicket = async (ticketId) => {
    try {
      await deleteTicket(ticketId);
      showSnackbar('Ticket deleted successfully');
    } catch (error) {
      showSnackbar('Failed to delete ticket', 'error');
    }
  };

  const generateForecast = async () => {
    try {
      await fetchForecast();
      showSnackbar('Forecast generated successfully');
    } catch (error) {
      showSnackbar('Failed to generate forecast', 'error');
    }
  };

  const generatePerformance = async () => {
    try {
      await fetchPerformance();
      showSnackbar('Performance report generated successfully');
    } catch (error) {
      showSnackbar('Failed to generate performance report', 'error');
    }
  };

  const checkDataQuality = async () => {
    try {
      await fetchDuplicates();
      showSnackbar('Data quality check completed');
    } catch (error) {
      showSnackbar('Failed to check data quality', 'error');
    }
  };

  // Helper functions for rendering tabs
  const renderTasksTab = () => (
    <Box>
      {/* Tasks Tab */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Tasks</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setEditingTask(null); setTaskForm({ type: 'task', notes: '', due_date: '', status: 'pending', contact_id: '', lead_id: '', opportunity_id: '' }); setTaskDialogOpen(true); }}>
          Add Task
        </Button>
      </Box>
      {/* Task filters */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        <Button variant="outlined" onClick={() => setTaskFilters({ status: '', type: '' })}>Clear Filters</Button>
        <Button variant="outlined" onClick={() => setTaskSaveDialogOpen(true)}>Save Filter</Button>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Status</InputLabel>
          <Select value={taskFilters.status} onChange={(e) => setTaskFilters({ ...taskFilters, status: e.target.value })} label="Status">
            <MenuItem value="">All</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="in_progress">In Progress</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
            <MenuItem value="cancelled">Cancelled</MenuItem>
          </Select>
        </FormControl>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Type</InputLabel>
          <Select value={taskFilters.type} onChange={(e) => setTaskFilters({ ...taskFilters, type: e.target.value })} label="Type">
            <MenuItem value="">All</MenuItem>
            <MenuItem value="task">Task</MenuItem>
            <MenuItem value="call">Call</MenuItem>
            <MenuItem value="email">Email</MenuItem>
            <MenuItem value="meeting">Meeting</MenuItem>
            <MenuItem value="follow_up">Follow Up</MenuItem>
          </Select>
        </FormControl>
      </Box>
      {/* Tasks table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Type</TableCell>
              <TableCell>Notes</TableCell>
              <TableCell>Due Date</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Contact</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tasks?.filter(task => {
              if (taskFilters.status && task.status !== taskFilters.status) return false;
              if (taskFilters.type && task.type !== taskFilters.type) return false;
              return true;
            }).map((task, index) => (
              <TableRow key={task.id || `task-${index}`}>
                <TableCell>
                  <Chip label={task.type || 'task'} size="small" color="primary" />
                </TableCell>
                <TableCell>{task.notes || ''}</TableCell>
                <TableCell>{task.due_date ? new Date(task.due_date).toLocaleDateString() : ''}</TableCell>
                <TableCell>
                  <Chip
                    label={task.status || 'pending'}
                    color={task.status === 'completed' ? 'success' : task.status === 'in_progress' ? 'warning' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{task.contact_id || ''}</TableCell>
                <TableCell>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => { setEditingTask(task); setTaskForm(task); setTaskDialogOpen(true); }} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDeleteTask(task.id)} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderTicketsTab = () => (
    <Box>
      {/* Tickets Tab */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Tickets</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="outlined" onClick={() => setSlaDialogOpen(true)}>SLA Policy</Button>
          <Button variant="outlined" onClick={() => setAssignDialogOpen(true)}>Assignment</Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setEditingTicket(null); setTicketForm({ subject: '', description: '', status: 'open', priority: 'medium', category: '', tags: '', customer_email: '', contact_id: '', lead_id: '', opportunity_id: '' }); setTicketDialogOpen(true); }}>
            Add Ticket
          </Button>
        </Box>
      </Box>
      {/* Tickets table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Subject</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Category</TableCell>
              <TableCell>Customer</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tickets?.map((ticket, index) => (
              <TableRow key={ticket.id || `ticket-${index}`}>
                <TableCell>{ticket.subject || ''}</TableCell>
                <TableCell>
                  <Chip
                    label={ticket.status || 'open'}
                    color={ticket.status === 'closed' ? 'success' : ticket.status === 'in_progress' ? 'warning' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={ticket.priority || 'medium'}
                    color={ticket.priority === 'high' ? 'error' : ticket.priority === 'low' ? 'success' : 'warning'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{ticket.category || ''}</TableCell>
                <TableCell>{ticket.customer_email || ''}</TableCell>
                <TableCell>{ticket.created_at ? new Date(ticket.created_at).toLocaleDateString() : ''}</TableCell>
                <TableCell>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => { setEditingTicket(ticket); setTicketForm(ticket); setTicketDialogOpen(true); }} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDeleteTicket(ticket.id)} color="error" size="small">
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );

  const renderReportsTab = () => (
    <Box>
      <Typography variant="h6" sx={{ mb: 2 }}>Reports</Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Sales Forecast</Typography>
              {forecast ? (
                <Box>
                  <Typography variant="h4" color="primary">${forecast.total.toLocaleString()}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Expected revenue for next quarter
                  </Typography>
                </Box>
              ) : (
                <Button variant="outlined" onClick={generateForecast}>Generate Forecast</Button>
              )}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>Performance Metrics</Typography>
              {performance ? (
                <Box>
                  <Typography variant="h4" color="success.main">{performance.conversion_rate}%</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Lead to opportunity conversion rate
                  </Typography>
                </Box>
              ) : (
                <Button variant="outlined" onClick={generatePerformance}>Generate Performance</Button>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const renderAutomationsTab = () => (
    <Box>
      <Typography variant="h6" sx={{ mb: 2 }}>Automations</Typography>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Button variant="contained" onClick={() => setWorkflowBuilderOpen(true)}>Create Workflow</Button>
      </Box>
      <Grid container spacing={2}>
        {workflowsUI.map((workflow, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h6">{workflow.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Trigger: {workflow.trigger}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Actions: {workflow.actions.length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderKnowledgeBaseTab = () => (
    <Box>
      <Typography variant="h6" sx={{ mb: 2 }}>Knowledge Base</Typography>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <TextField
          placeholder="Search articles..."
          value={kbQuery}
          onChange={(e) => setKbQuery(e.target.value)}
          size="small"
          sx={{ flexGrow: 1 }}
        />
        <Button variant="contained" onClick={() => { setEditingArticle(null); setKbForm({ title: '', content: '', tags: '', published: false }); setKbDialogOpen(true); }}>
          Add Article
        </Button>
      </Box>
      <Grid container spacing={2}>
        {kbArticles.filter(article => 
          kbQuery === '' || 
          article.title.toLowerCase().includes(kbQuery.toLowerCase()) ||
          article.content.toLowerCase().includes(kbQuery.toLowerCase())
        ).map((article, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h6">{article.title}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  {article.content.substring(0, 100)}...
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button size="small" onClick={() => { setEditingArticle(article); setKbForm(article); setKbDialogOpen(true); }}>Edit</Button>
                  <Button size="small" color="error" onClick={() => setKbArticles(kbArticles.filter((_, i) => i !== index))}>Delete</Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderDataQualityTab = () => (
    <Box>
      <Typography variant="h6" sx={{ mb: 2 }}>Data Quality</Typography>
      <FormControl sx={{ mb: 2, minWidth: 200 }}>
        <InputLabel>Entity</InputLabel>
        <Select value={dqEntity} onChange={(e) => setDqEntity(e.target.value)} label="Entity">
          <MenuItem value="contacts">Contacts</MenuItem>
          <MenuItem value="leads">Leads</MenuItem>
          <MenuItem value="opportunities">Opportunities</MenuItem>
        </Select>
      </FormControl>
      <Button variant="contained" onClick={checkDataQuality} sx={{ mb: 2 }}>Check Data Quality</Button>
      {dqGroups.length > 0 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 1 }}>Duplicate Groups</Typography>
          {dqGroups.map((group, index) => (
            <Card key={index} sx={{ mb: 1 }}>
              <CardContent>
                <Typography variant="subtitle1">Group {index + 1} ({group.length} items)</Typography>
                {group.map((item, itemIndex) => (
                  <Typography key={itemIndex} variant="body2">
                    {item.name || item.email || item.id}
                  </Typography>
                ))}
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );

  return (
    <Box sx={{ width: '100%', height: '100%', p: 2 }}>
      {renderFeature()}
    </Box>
  );
};

export default CRMModule;
