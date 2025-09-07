import React, { useState } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Tab, Tabs, Alert, Snackbar, LinearProgress, Tooltip, useMediaQuery, useTheme, TextField, FormControl, InputLabel, Select, MenuItem
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
  Email as EmailIcon
} from '@mui/icons-material';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';
import { apiClient } from '../../utils/apiClient';
import CRMPipeline from './CRMPipeline';
import CRMCommunicationHistory from './CRMCommunicationHistory';
import CRMCompanies from './CRMCompanies';

const CRMModule = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));
  
  const [activeTab, setActiveTab] = useState(0);
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
  const API_BASE = process.env.REACT_APP_API_BASE || process.env.REACT_APP_API_URL || 'http://localhost:5000';
  
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

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
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
    <Dialog open={leadFiltersOpen} onClose={() => setLeadFiltersOpen(false)} maxWidth="sm" fullWidth>
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
    <Dialog open={taskSaveDialogOpen} onClose={() => setTaskSaveDialogOpen(false)} maxWidth="xs" fullWidth>
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
    <Dialog open={leadSaveDialogOpen} onClose={() => setLeadSaveDialogOpen(false)} maxWidth="xs" fullWidth>
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

  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      <Typography variant={isMobile ? "h5" : "h4"} gutterBottom>
        Customer Relationship Management
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        <Button variant="outlined" onClick={() => handleExport('companies')}>Export Companies</Button>
        <Button variant="outlined" onClick={() => handleExport('activities')}>Export Activities</Button>
        <Button variant="outlined" onClick={() => setImportOpen(true)}>Import CSV</Button>
        <Button variant="contained" onClick={openMarketing}>Marketing (Email)</Button>
      </Box>

      {/* Metrics Cards */}
      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Contacts
              </Typography>
              <Typography variant={isMobile ? "h5" : "h4"}>
                {crmMetrics.totalContacts}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Leads
              </Typography>
              <Typography variant={isMobile ? "h5" : "h4"}>
                {crmMetrics.totalLeads}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Opportunities
              </Typography>
              <Typography variant={isMobile ? "h5" : "h4"}>
                {crmMetrics.totalOpportunities}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ p: { xs: 1.5, md: 2 } }}>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Pipeline Value
              </Typography>
              <Typography variant={isMobile ? "h5" : "h4"}>
                ${crmMetrics.totalValue ? crmMetrics.totalValue.toLocaleString() : ''}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Contacts" />
          <Tab label="Leads" />
          <Tab label="Opportunities" />
          <Tab label="Pipeline" />
          <Tab label="Companies" />
          <Tab label="Activities" />
          <Tab label="Tasks" />
          <Tab label="Tickets" />
          <Tab label="Reports" />
          <Tab label="Automations" />
          <Tab label="Knowledge Base" />
          <Tab label="Data Quality" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && renderContactsTab()}
      {activeTab === 1 && renderLeadsTab()}
      {activeTab === 2 && renderOpportunitiesTab()}
      {activeTab === 3 && renderPipelineTab()}
      {activeTab === 4 && (
        <Box>
          <CRMCompanies />
        </Box>
      )}
      {activeTab === 5 && (
        <Box>
          <CRMCommunicationHistory onOpenEntityDetail={openEntityDetail} />
        </Box>
      )}
      {activeTab === 6 && (
        <Box>
          {/* Tasks Tab */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Tasks</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Status</InputLabel>
                <Select value={taskFilters.status} label="Status" onChange={(e) => setTaskFilters({ ...taskFilters, status: e.target.value })}>
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="overdue">Overdue</MenuItem>
                </Select>
              </FormControl>
              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Type</InputLabel>
                <Select value={taskFilters.type} label="Type" onChange={(e) => setTaskFilters({ ...taskFilters, type: e.target.value })}>
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="task">Task</MenuItem>
                  <MenuItem value="follow_up">Follow Up</MenuItem>
                  <MenuItem value="call">Call</MenuItem>
                  <MenuItem value="email">Email</MenuItem>
                  <MenuItem value="meeting">Meeting</MenuItem>
                </Select>
              </FormControl>
              <FormControl size="small" sx={{ minWidth: 160 }}>
                <InputLabel>Saved Filters</InputLabel>
                <Select
                  label="Saved Filters"
                  value=""
                  onChange={(e) => applyTasksFilterPreset(e.target.value)}
                >
                  <MenuItem value="">Select preset</MenuItem>
                  {(savedTaskFilters || []).map((p) => (
                    <MenuItem key={p.name} value={p.name}>{p.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button variant="outlined" onClick={() => setTaskSaveDialogOpen(true)}>Save Filter</Button>
              <Button variant="outlined" onClick={() => { window.location.href = `${API_BASE}/api/crm/tasks/calendar.ics`; }}>Export Calendar (.ics)</Button>
              <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setEditingTask(null); setTaskDialogOpen(true); }}>Add Task</Button>
            </Box>
          </Box>

          {tasksLoading && <LinearProgress />}
          {tasksError && <Alert severity="error" sx={{ mb: 2 }}>{tasksError}</Alert>}

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Notes</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Due</TableCell>
                  <TableCell>Context</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(tasks || [])
                  .filter((t) => !taskFilters.status || (taskFilters.status === 'overdue' ? (t.status !== 'completed' && t.due_date && new Date(t.due_date) < new Date()) : t.status === taskFilters.status))
                  .filter((t) => !taskFilters.type || t.type === taskFilters.type)
                  .map((t, idx) => (
                    <TableRow key={t.id || `task-${idx}`}>
                      <TableCell>{t.notes}</TableCell>
                      <TableCell><Chip size="small" label={t.type} /></TableCell>
                      <TableCell>
                        <Chip size="small" label={t.status} color={t.status === 'completed' ? 'success' : (t.due_date && new Date(t.due_date) < new Date() ? 'warning' : 'default')} />
                      </TableCell>
                      <TableCell>{t.due_date ? new Date(t.due_date).toLocaleString() : ''}</TableCell>
                      <TableCell>
                        {t.contact_id && (
                          <Chip size="small" label={`Contact #${t.contact_id}`} clickable onClick={() => openEntityDetail('contact', t.contact_id)} sx={{ mr: 0.5 }} />
                        )}
                        {t.lead_id && (
                          <Chip size="small" label={`Lead #${t.lead_id}`} clickable onClick={() => openEntityDetail('lead', t.lead_id)} sx={{ mr: 0.5 }} />
                        )}
                        {t.opportunity_id && (
                          <Chip size="small" label={`Opportunity #${t.opportunity_id}`} clickable onClick={() => openEntityDetail('opportunity', t.opportunity_id)} />
                        )}
                      </TableCell>
                      <TableCell>
                        {t.status !== 'completed' && (
                          <Button size="small" color="success" onClick={() => updateTaskRT(t.id, { status: 'completed' })} sx={{ mr: 1 }}>Mark Done</Button>
                        )}
                        <Button size="small" onClick={() => { setEditingTask(t); setTaskDialogOpen(true); }} sx={{ mr: 1 }}>Edit</Button>
                        <Button size="small" color="error" onClick={() => deleteTaskRT(t.id)}>Delete</Button>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}
      {activeTab === 7 && (
        <Box>
          {/* Tickets Tab */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Tickets</Typography>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', flexWrap: 'wrap' }}>
              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Status</InputLabel>
                <Select value={ticketFilters.status} label="Status" onChange={(e) => setTicketFilters({ ...ticketFilters, status: e.target.value })}>
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="resolved">Resolved</MenuItem>
                  <MenuItem value="closed">Closed</MenuItem>
                </Select>
              </FormControl>
              <FormControl size="small" sx={{ minWidth: 140 }}>
                <InputLabel>Priority</InputLabel>
                <Select value={ticketFilters.priority} label="Priority" onChange={(e) => setTicketFilters({ ...ticketFilters, priority: e.target.value })}>
                  <MenuItem value="">All</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="urgent">Urgent</MenuItem>
                </Select>
              </FormControl>
              <TextField size="small" label="Category" value={ticketFilters.category} onChange={(e) => setTicketFilters({ ...ticketFilters, category: e.target.value })} />
              <FormControl size="small" sx={{ minWidth: 160 }}>
                <InputLabel>Saved Filters</InputLabel>
                <Select label="Saved Filters" value="" onChange={(e) => applyTicketsFilterPreset(e.target.value)}>
                  <MenuItem value="">Select preset</MenuItem>
                  {(savedTicketFilters || []).map((p) => (
                    <MenuItem key={p.name} value={p.name}>{p.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Button variant="outlined" onClick={() => setTicketSaveDialogOpen(true)}>Save Filter</Button>
              <Button
                variant="outlined"
                onClick={openSLASettings}
              >
                SLA Settings
              </Button>
              <Button
                variant="outlined"
                onClick={openAssignmentSettings}
              >
                Assignment
              </Button>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={openAddTicket}
              >
                Add Ticket
              </Button>
            </Box>
          </Box>

          {ticketsLoading && <LinearProgress />}

          {ticketsError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {ticketsError}
            </Alert>
          )}

          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Subject</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Priority</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Contact</TableCell>
                  <TableCell>Lead</TableCell>
                  <TableCell>Opportunity</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(tickets || [])
                  .filter((t) => !ticketFilters.status || t.status === ticketFilters.status)
                  .filter((t) => !ticketFilters.priority || t.priority === ticketFilters.priority)
                  .filter((t) => !ticketFilters.category || (t.category || '').toLowerCase().includes(ticketFilters.category.toLowerCase()))
                  .map((t, idx) => (
                  <TableRow key={t.id || `ticket-${idx}`}>
                    <TableCell>{t.subject}</TableCell>
                    <TableCell>
                      <Chip label={t.status} size="small" color={t.status === 'open' ? 'warning' : (t.status === 'resolved' || t.status === 'closed') ? 'success' : 'default'} />
                    </TableCell>
                    <TableCell>
                      <Chip label={t.priority} size="small" color={t.priority === 'urgent' ? 'error' : (t.priority === 'high' ? 'warning' : 'default')} />
                    </TableCell>
                    <TableCell>{t.category || ''}</TableCell>
                    <TableCell>
                      {t.contact_id && (
                        <Chip size="small" label={`Contact #${t.contact_id}`} clickable onClick={() => openEntityDetail('contact', t.contact_id)} />
                      )}
                    </TableCell>
                    <TableCell>
                      {t.lead_id && (
                        <Chip size="small" label={`Lead #${t.lead_id}`} clickable onClick={() => openEntityDetail('lead', t.lead_id)} />
                      )}
                    </TableCell>
                    <TableCell>
                      {t.opportunity_id && (
                        <Chip size="small" label={`Opportunity #${t.opportunity_id}`} clickable onClick={() => openEntityDetail('opportunity', t.opportunity_id)} />
                      )}
                    </TableCell>
                    <TableCell>{t.created_at ? new Date(t.created_at).toLocaleString() : ''}</TableCell>
                    <TableCell>
                      {(t.sla_first_response_breached || t.sla_resolve_breached) && (
                        <Chip size="small" color="error" label={t.sla_first_response_breached ? 'First Response SLA Breached' : 'Resolution SLA Breached'} sx={{ mr: 1 }} />
                      )}
                      <Tooltip title="Edit">
                        <IconButton onClick={() => openEditTicket(t)} size="small">
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton onClick={() => removeTicket(t)} color="error" size="small">
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
      )}

      {activeTab === 8 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>Reports</Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>Forecast</Typography>
                <Button size="small" onClick={fetchForecast}>Refresh</Button>
                {forecast && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2">Total: ${forecast.totalValue}</Typography>
                    <Typography variant="body2">Weighted: ${forecast.weightedValue}</Typography>
                    <Typography variant="subtitle2" sx={{ mt: 1 }}>Projections</Typography>
                    <Typography variant="caption">30d: ${forecast.projections?.next_30_days}</Typography><br />
                    <Typography variant="caption">60d: ${forecast.projections?.next_60_days}</Typography><br />
                    <Typography variant="caption">90d: ${forecast.projections?.next_90_days}</Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>Performance</Typography>
                <Button size="small" onClick={fetchPerformance}>Refresh</Button>
                {performance && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="subtitle2">By Team</Typography>
                    <pre style={{ margin: 0 }}>{JSON.stringify(performance.byTeam || {}, null, 2)}</pre>
                    <Typography variant="subtitle2" sx={{ mt: 1 }}>By Region</Typography>
                    <pre style={{ margin: 0 }}>{JSON.stringify(performance.byRegion || {}, null, 2)}</pre>
                  </Box>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>Funnel</Typography>
                <Button size="small" onClick={fetchFunnel}>Refresh</Button>
                {funnel && (
                  <Box sx={{ mt: 1 }}>
                    {(funnel.funnel || []).map((s) => (
                      <Box key={s.stage} sx={{ display: 'flex', justifyContent: 'space-between' }}>
                        <Typography variant="body2">{s.stage}</Typography>
                        <Chip size="small" label={s.count} />
                      </Box>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" gutterBottom>Stuck Deals</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TextField size="small" label="Days" type="number" value={stuck.days} onChange={(e) => setStuck({ ...stuck, days: Number(e.target.value || 30) })} sx={{ width: 120 }} />
                  <Button size="small" onClick={fetchStuck}>Refresh</Button>
                </Box>
                <Typography variant="caption">{stuck.count || 0} deals</Typography>
                <TableContainer component={Paper} sx={{ mt: 1 }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Name</TableCell>
                        <TableCell>Stage</TableCell>
                        <TableCell>Amount</TableCell>
                        <TableCell>Age (days)</TableCell>
                        <TableCell>Open</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {(stuck.deals || []).slice(0, 10).map((d) => (
                        <TableRow key={d.id}>
                          <TableCell>{d.name}</TableCell>
                          <TableCell>{d.stage}</TableCell>
                          <TableCell>${d.amount}</TableCell>
                          <TableCell><Chip size="small" label={d.ageDays} color={d.ageDays > stuck.days ? 'warning' : 'default'} /></TableCell>
                          <TableCell>
                            <Button size="small" onClick={() => openEntityDetail('opportunity', d.id)}>View</Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Box>
        </Box>
      )}

      {activeTab === 9 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>Automations</Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <Button variant="contained" onClick={() => openWorkflowBuilderUI(null)}>New Workflow</Button>
            <Button variant="outlined" onClick={fetchWorkflowsUI}>Refresh</Button>
          </Box>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Trigger</TableCell>
                  <TableCell>Active</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(workflowsUI || []).map((w) => (
                  <TableRow key={w.id}>
                    <TableCell>{w.name}</TableCell>
                    <TableCell>{w.trigger?.id || w.trigger?.name || ''}</TableCell>
                    <TableCell>
                      <Chip size="small" label={w.is_active ? 'Active' : 'Inactive'} color={w.is_active ? 'success' : 'default'} />
                    </TableCell>
                    <TableCell>
                      <Button size="small" onClick={() => toggleWorkflowUI(w.id)}>{w.is_active ? 'Disable' : 'Enable'}</Button>
                      <Button size="small" onClick={() => openWorkflowBuilderUI(w)}>Edit</Button>
                      <Button size="small" color="error" onClick={() => deleteWorkflowUI(w.id)}>Delete</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {activeTab === 10 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>Knowledge Base</Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <TextField size="small" placeholder="Search articles..." value={kbQuery} onChange={(e) => setKbQuery(e.target.value)} />
            <Button variant="outlined" onClick={fetchKB}>Search</Button>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => { setEditingArticle(null); setKbDialogOpen(true); }}>Add Article</Button>
          </Box>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Title</TableCell>
                  <TableCell>Tags</TableCell>
                  <TableCell>Updated</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(kbArticles || []).map((a) => (
                  <TableRow key={a.id}>
                    <TableCell>{a.title}</TableCell>
                    <TableCell>{a.tags}</TableCell>
                    <TableCell>{a.updated_at ? new Date(a.updated_at).toLocaleString() : ''}</TableCell>
                    <TableCell>
                      <Button size="small" onClick={() => { setEditingArticle(a); setKbForm({ title: a.title || '', content: a.content || '', tags: a.tags || '' }); setKbDialogOpen(true); }}>Edit</Button>
                      <Button size="small" color="error" onClick={() => deleteKB(a.id)}>Delete</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}
      {activeTab === 11 && (
        <Box>
          <Typography variant="h6" sx={{ mb: 2 }}>Data Quality</Typography>
          <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel>Entity</InputLabel>
              <Select value={dqEntity} label="Entity" onChange={(e) => setDqEntity(e.target.value)}>
                <MenuItem value="contacts">Contacts</MenuItem>
                <MenuItem value="leads">Leads</MenuItem>
                <MenuItem value="companies">Companies</MenuItem>
              </Select>
            </FormControl>
            <Button variant="outlined" onClick={fetchDuplicates}>Find Duplicates</Button>
          </Box>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Key</TableCell>
                  <TableCell>Records</TableCell>
                  <TableCell>Merge</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(dqGroups || []).map((g, gi) => (
                  <TableRow key={`dg-${gi}`}>
                    <TableCell>{g.key}</TableCell>
                    <TableCell>
                      {(g.records || []).map((r) => (
                        <Chip key={r.id} label={`#${r.id} ${r.name || r.email || ''}`} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                      ))}
                    </TableCell>
                    <TableCell>
                      {(g.records || []).length >= 2 && (
                        <Button size="small" variant="contained" onClick={() => mergePair(g.records[0].id, g.records[1].id)}>Merge first two</Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Box>
      )}

      {/* SLA & Assignment Controls inside Tickets tab actions */}

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>

      {/* Detail View Modal */}
      <DetailViewModal
        open={detailViewOpen}
        onClose={() => {
          setDetailViewOpen(false);
          setSelectedItem(null);
          setSelectedItemType('');
        }}
        data={selectedItem}
        type={selectedItemType}
        onEdit={(item) => {
          setDetailViewOpen(false);
          handleEdit(item, selectedItemType);
        }}
        title={`${selectedItemType ? selectedItemType.charAt(0).toUpperCase() + selectedItemType.slice(1) : 'Item'} Details`}
      />

      {renderLeadFiltersDialog()}
      {renderLeadSaveDialog()}
      {renderTaskSaveDialog()}
      {/* Import Dialog */}
      <Dialog open={importOpen} onClose={() => setImportOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Import CSV</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Entity</InputLabel>
              <Select value={importEntity} label="Entity" onChange={(e) => setImportEntity(e.target.value)}>
                <MenuItem value="contacts">Contacts</MenuItem>
                <MenuItem value="leads">Leads</MenuItem>
                <MenuItem value="companies">Companies</MenuItem>
                <MenuItem value="opportunities">Opportunities</MenuItem>
                <MenuItem value="activities">Activities</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Column Mapping (JSON: {csvColumn: field})"
              value={importMapping}
              onChange={(e) => setImportMapping(e.target.value)}
              fullWidth
            />
            <TextField
              label="Paste CSV Content"
              value={csvText}
              onChange={(e) => setCsvText(e.target.value)}
              fullWidth
              multiline
              rows={8}
              sx={{ gridColumn: '1 / -1' }}
            />
            <Box sx={{ gridColumn: '1 / -1', display: 'flex', gap: 1 }}>
              <Button variant="outlined" onClick={suggestMapping} disabled={aiMappingLoading}>
                {aiMappingLoading ? 'Suggesting…' : 'AI Suggest Mapping'}
              </Button>
              <Button variant="outlined" onClick={() => runImport(true)}>Validate (Dry Run)</Button>
              <Button variant="contained" color="success" onClick={() => runImport(false)}>Import</Button>
            </Box>
            {importSummary && (
              <Box sx={{ gridColumn: '1 / -1' }}>
                <Alert severity="info" sx={{ mb: 1 }}>
                  {`Rows: ${importSummary.totalRows}, Valid: ${importSummary.validRows}, Duplicates: ${importSummary.duplicateCount}, Errors: ${importSummary.errorCount}`}
                </Alert>
                <TableContainer component={Paper}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Row</TableCell>
                        <TableCell>Errors</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {(importErrors || []).slice(0, 20).map((er, i) => (
                        <TableRow key={`er-${i}`}>
                          <TableCell>{er.row}</TableCell>
                          <TableCell>{(er.errors || []).join(', ')}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setImportOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={ticketSaveDialogOpen} onClose={() => setTicketSaveDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Save Ticket Filter</DialogTitle>
        <DialogContent>
          <TextField autoFocus label="Preset Name" fullWidth value={ticketFilterName} onChange={(e) => setTicketFilterName(e.target.value)} sx={{ mt: 1 }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTicketSaveDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={saveTicketsFilterPreset} disabled={!ticketFilterName.trim()}>Save</Button>
        </DialogActions>
      </Dialog>
      {/* Contacts Filters */}
      <Dialog open={contactFiltersOpen} onClose={() => setContactFiltersOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Advanced Contact Filters</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <TextField
              label="Region"
              value={contactFilters.region}
              onChange={(e) => setContactFilters({ ...contactFilters, region: e.target.value })}
              fullWidth
            />
            <TextField
              label="Assigned Team"
              value={contactFilters.assignedTeam}
              onChange={(e) => setContactFilters({ ...contactFilters, assignedTeam: e.target.value })}
              fullWidth
            />
            <TextField
              label="Type"
              value={contactFilters.type}
              onChange={(e) => setContactFilters({ ...contactFilters, type: e.target.value })}
              fullWidth
            />
            <TextField
              label="Status"
              value={contactFilters.status}
              onChange={(e) => setContactFilters({ ...contactFilters, status: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setContactFilters({ region: '', assignedTeam: '', type: '', status: '' })}>Clear</Button>
          <Button variant="contained" onClick={() => setContactFiltersOpen(false)}>Apply</Button>
        </DialogActions>
      </Dialog>

      {/* Opportunities Filters */}
      <Dialog open={oppFiltersOpen} onClose={() => setOppFiltersOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Advanced Opportunity Filters</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <TextField
              label="Region"
              value={oppFilters.region}
              onChange={(e) => setOppFilters({ ...oppFilters, region: e.target.value })}
              fullWidth
            />
            <TextField
              label="Assigned Team"
              value={oppFilters.assignedTeam}
              onChange={(e) => setOppFilters({ ...oppFilters, assignedTeam: e.target.value })}
              fullWidth
            />
            <TextField
              label="Stage"
              value={oppFilters.stage}
              onChange={(e) => setOppFilters({ ...oppFilters, stage: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOppFilters({ region: '', assignedTeam: '', stage: '' })}>Clear</Button>
          <Button variant="contained" onClick={() => setOppFiltersOpen(false)}>Apply</Button>
        </DialogActions>
      </Dialog>
      <Dialog open={oppSaveDialogOpen} onClose={() => setOppSaveDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Save Opportunity Filter</DialogTitle>
        <DialogContent>
          <TextField autoFocus label="Preset Name" fullWidth value={oppFilterName} onChange={(e) => setOppFilterName(e.target.value)} sx={{ mt: 1 }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOppSaveDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={saveOppsFilterPreset} disabled={!oppFilterName.trim()}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Improved Form */}
      <ImprovedForm
        open={formOpen}
        onClose={() => {
          setFormOpen(false);
          setEditItem(null);
        }}
        onSave={handleSave}
        data={editItem}
        type={selectedItemType}
        title={selectedItemType ? selectedItemType.charAt(0).toUpperCase() + selectedItemType.slice(1) : 'Item'}
        loading={contactsLoading || leadsLoading || opportunitiesLoading}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>Confirm Delete</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this {selectedItemType}? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleConfirmDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Marketing (Email) Dialog */}
      <Dialog open={marketingOpen} onClose={() => setMarketingOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Email Marketing</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <Typography variant="subtitle2" sx={{ gridColumn: '1 / -1' }}>Sender Settings</Typography>
            <TextField
              label="From Email"
              value={sender.from_email}
              onChange={(e) => setSender({ ...sender, from_email: e.target.value })}
              fullWidth
            />
            <TextField
              label="From Name"
              value={sender.from_name}
              onChange={(e) => setSender({ ...sender, from_name: e.target.value })}
              fullWidth
            />
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Button variant="outlined" onClick={saveSender}>Save Sender</Button>
            </Box>

            <Typography variant="subtitle2" sx={{ gridColumn: '1 / -1', mt: 2 }}>Create Segment</Typography>
            <TextField
              label="Segment Name"
              value={segmentForm.name}
              onChange={(e) => setSegmentForm({ ...segmentForm, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Criteria (JSON)"
              value={segmentForm.criteria}
              onChange={(e) => setSegmentForm({ ...segmentForm, criteria: e.target.value })}
              fullWidth
            />
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Button variant="outlined" onClick={createSegment}>Add Segment</Button>
            </Box>

            <Typography variant="subtitle2" sx={{ gridColumn: '1 / -1', mt: 2 }}>Create Template</Typography>
            <TextField
              label="Template Name"
              value={templateForm.name}
              onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Subject"
              value={templateForm.subject}
              onChange={(e) => setTemplateForm({ ...templateForm, subject: e.target.value })}
              fullWidth
            />
            <TextField
              label="Body"
              value={templateForm.body}
              onChange={(e) => setTemplateForm({ ...templateForm, body: e.target.value })}
              fullWidth
              multiline
              rows={3}
              sx={{ gridColumn: '1 / -1' }}>
            </TextField>
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Button variant="outlined" onClick={createTemplate}>Add Template</Button>
            </Box>

            <Typography variant="subtitle2" sx={{ gridColumn: '1 / -1', mt: 2 }}>Create Campaign</Typography>
            <TextField
              label="Campaign Name"
              value={campaignForm.name}
              onChange={(e) => setCampaignForm({ ...campaignForm, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Segment ID"
              value={campaignForm.segment_id}
              onChange={(e) => setCampaignForm({ ...campaignForm, segment_id: e.target.value })}
              fullWidth
            />
            <TextField
              label="Template ID"
              value={campaignForm.template_id}
              onChange={(e) => setCampaignForm({ ...campaignForm, template_id: e.target.value })}
              fullWidth
            />
            <TextField
              label="Scheduled For (ISO)"
              value={campaignForm.scheduled_for}
              onChange={(e) => setCampaignForm({ ...campaignForm, scheduled_for: e.target.value })}
              fullWidth
            />
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Button variant="contained" onClick={createCampaign}>Create Campaign</Button>
            </Box>

            <Typography variant="subtitle2" sx={{ gridColumn: '1 / -1', mt: 2 }}>Drip Sequences</Typography>
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Typography variant="caption" color="text.secondary">Existing Sequences</Typography>
              <TableContainer component={Paper} sx={{ mt: 1 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Steps</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(sequences || []).map((s, idx) => (
                      <TableRow key={s.id || `seq-${idx}`}>
                        <TableCell>{s.name}</TableCell>
                        <TableCell>
                          <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{JSON.stringify(s.steps || [], null, 2)}</pre>
                        </TableCell>
                        <TableCell>{s.status || 'draft'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
            <Typography variant="subtitle2" sx={{ gridColumn: '1 / -1', mt: 2 }}>Create Sequence</Typography>
            <TextField
              label="Sequence Name"
              value={sequenceForm.name}
              onChange={(e) => setSequenceForm({ ...sequenceForm, name: e.target.value })}
              fullWidth
            />
            <TextField
              label="Steps (JSON array)"
              value={sequenceForm.steps}
              onChange={(e) => setSequenceForm({ ...sequenceForm, steps: e.target.value })}
              fullWidth
              multiline
              rows={4}
              sx={{ gridColumn: '1 / -1' }}
            />
            <Box sx={{ gridColumn: '1 / -1' }}>
              <Button variant="outlined" onClick={createSequence}>Add Sequence</Button>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMarketingOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Ticket Dialog */}
      <Dialog open={ticketDialogOpen} onClose={() => setTicketDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingTicket ? 'Edit Ticket' : 'Add Ticket'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <TextField
              label="Subject"
              value={ticketForm.subject}
              onChange={(e) => setTicketForm({ ...ticketForm, subject: e.target.value })}
              fullWidth
              sx={{ gridColumn: '1 / -1' }}
            />
            <TextField
              label="Description"
              value={ticketForm.description}
              onChange={(e) => setTicketForm({ ...ticketForm, description: e.target.value })}
              fullWidth
              multiline
              rows={3}
              sx={{ gridColumn: '1 / -1' }}
            />
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={ticketForm.status}
                label="Status"
                onChange={(e) => setTicketForm({ ...ticketForm, status: e.target.value })}
              >
                <MenuItem value="open">Open</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="resolved">Resolved</MenuItem>
                <MenuItem value="closed">Closed</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={ticketForm.priority}
                label="Priority"
                onChange={(e) => setTicketForm({ ...ticketForm, priority: e.target.value })}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="urgent">Urgent</MenuItem>
              </Select>
            </FormControl>
            <TextField label="Category" value={ticketForm.category} onChange={(e) => setTicketForm({ ...ticketForm, category: e.target.value })} fullWidth />
            <TextField label="Tags (comma-separated)" value={ticketForm.tags} onChange={(e) => setTicketForm({ ...ticketForm, tags: e.target.value })} fullWidth />
            <TextField label="Customer Email" value={ticketForm.customer_email} onChange={(e) => setTicketForm({ ...ticketForm, customer_email: e.target.value })} fullWidth />
            <TextField
              label="Contact ID"
              value={ticketForm.contact_id}
              onChange={(e) => setTicketForm({ ...ticketForm, contact_id: e.target.value })}
              fullWidth
            />
            <TextField
              label="Lead ID"
              value={ticketForm.lead_id}
              onChange={(e) => setTicketForm({ ...ticketForm, lead_id: e.target.value })}
              fullWidth
            />
            <TextField
              label="Opportunity ID"
              value={ticketForm.opportunity_id}
              onChange={(e) => setTicketForm({ ...ticketForm, opportunity_id: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTicketDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={saveTicket} disabled={!ticketForm.subject}>
            {editingTicket ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Task Dialog */}
      <Dialog open={taskDialogOpen} onClose={() => setTaskDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingTask ? 'Edit Task' : 'Add Task'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Type</InputLabel>
              <Select value={taskForm.type} label="Type" onChange={(e) => setTaskForm({ ...taskForm, type: e.target.value })}>
                <MenuItem value="task">Task</MenuItem>
                <MenuItem value="follow_up">Follow Up</MenuItem>
                <MenuItem value="call">Call</MenuItem>
                <MenuItem value="email">Email</MenuItem>
                <MenuItem value="meeting">Meeting</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select value={taskForm.status} label="Status" onChange={(e) => setTaskForm({ ...taskForm, status: e.target.value })}>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Due Date"
              type="datetime-local"
              value={taskForm.due_date}
              onChange={(e) => setTaskForm({ ...taskForm, due_date: e.target.value })}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
            <TextField
              label="Notes"
              value={taskForm.notes}
              onChange={(e) => setTaskForm({ ...taskForm, notes: e.target.value })}
              fullWidth
              multiline
              rows={3}
              sx={{ gridColumn: '1 / -1' }}
            />
            <TextField label="Contact ID" value={taskForm.contact_id} onChange={(e) => setTaskForm({ ...taskForm, contact_id: e.target.value })} fullWidth />
            <TextField label="Lead ID" value={taskForm.lead_id} onChange={(e) => setTaskForm({ ...taskForm, lead_id: e.target.value })} fullWidth />
            <TextField label="Opportunity ID" value={taskForm.opportunity_id} onChange={(e) => setTaskForm({ ...taskForm, opportunity_id: e.target.value })} fullWidth />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTaskDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            const payload = { ...taskForm };
            if (editingTask) {
              await updateTaskRT(editingTask.id, payload);
              showSnackbar('Task updated');
            } else {
              await createTaskRT(payload);
              showSnackbar('Task created');
            }
            setTaskDialogOpen(false);
            setEditingTask(null);
          }}>
            {editingTask ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* KB Article Dialog */}
      <Dialog open={kbDialogOpen} onClose={() => setKbDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingArticle ? 'Edit Article' : 'Add Article'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2, mt: 1 }}>
            <TextField label="Title" value={kbForm.title} onChange={(e) => setKbForm({ ...kbForm, title: e.target.value })} fullWidth />
            <TextField label="Tags (comma-separated)" value={kbForm.tags} onChange={(e) => setKbForm({ ...kbForm, tags: e.target.value })} fullWidth />
            <TextField label="Content" value={kbForm.content} onChange={(e) => setKbForm({ ...kbForm, content: e.target.value })} fullWidth multiline rows={6} />
            <FormControl fullWidth>
              <InputLabel shrink>Published</InputLabel>
              <Select value={kbForm.published ? 'yes' : 'no'} label="Published" onChange={(e) => setKbForm({ ...kbForm, published: e.target.value === 'yes' })}>
                <MenuItem value="no">No</MenuItem>
                <MenuItem value="yes">Yes</MenuItem>
              </Select>
            </FormControl>
            {!editingArticle && (
              <>
                <Typography variant="caption">Optional: upload attachment after creating</Typography>
                <input type="file" onChange={(e) => setKbFile(e.target.files?.[0] || null)} />
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setKbDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={async () => {
            if (editingArticle) {
              await saveKB();
            } else {
              const before = kbForm;
              await saveKB();
              // After creation, refetch and attach if file selected
              try { await fetchKB(); } catch {}
              if (kbFile) {
                // find most recent article matching title
                const created = (kbArticles || []).find(a => (a.title || '') === (before.title || ''));
                if (created?.id) { await uploadKBAttachment(created.id); await fetchKB(); }
              }
            }
          }} disabled={!kbForm.title.trim()}>{editingArticle ? 'Update' : 'Create'}</Button>
        </DialogActions>
      </Dialog>

      {/* SLA Policy Dialog */}
      <Dialog open={slaDialogOpen} onClose={() => setSlaDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>SLA Policy</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2, mt: 1 }}>
            <TextField
              label="First Response (minutes)"
              type="number"
              value={slaPolicy.first_response_minutes}
              onChange={(e) => setSlaPolicy({ ...slaPolicy, first_response_minutes: e.target.value })}
              fullWidth
            />
            <TextField
              label="Resolve (minutes)"
              type="number"
              value={slaPolicy.resolve_minutes}
              onChange={(e) => setSlaPolicy({ ...slaPolicy, resolve_minutes: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSlaDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={saveSlaPolicy}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Assignment Dialog */}
      <Dialog open={assignDialogOpen} onClose={() => setAssignDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Assignment Settings</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Strategy</InputLabel>
              <Select value={assignment.strategy} label="Strategy" onChange={(e) => setAssignment({ ...assignment, strategy: e.target.value })}>
                <MenuItem value="round_robin">Round Robin</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Agent IDs (comma-separated)"
              value={assignmentAgentsInput}
              onChange={(e) => setAssignmentAgentsInput(e.target.value)}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAssignDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={saveAssignment}>Save</Button>
        </DialogActions>
      </Dialog>

      {/* Workflow Builder Dialog */}
      <Dialog open={workflowBuilderOpen} onClose={() => setWorkflowBuilderOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingWorkflow ? 'Edit Workflow' : 'New Workflow'}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', gap: 2, mt: 1 }}>
            <TextField label="Name" value={builderData.name} onChange={(e) => setBuilderData({ ...builderData, name: e.target.value })} fullWidth />
            <TextField label="Trigger ID" value={builderData.trigger_id} onChange={(e) => setBuilderData({ ...builderData, trigger_id: e.target.value })} fullWidth />
            <TextField label="Actions (JSON array)" value={JSON.stringify(builderData.actions || [])} onChange={(e) => {
              try { setBuilderData({ ...builderData, actions: JSON.parse(e.target.value || '[]') }); } catch {}
            }} fullWidth multiline rows={3} />
            <TextField label="Conditions (JSON array)" value={JSON.stringify(builderData.conditions || [])} onChange={(e) => {
              try { setBuilderData({ ...builderData, conditions: JSON.parse(e.target.value || '[]') }); } catch {}
            }} fullWidth multiline rows={3} />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWorkflowBuilderOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={saveWorkflowUI} disabled={!builderData.name || !builderData.trigger_id}>Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CRMModule;
