import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Alert,
  Snackbar,
  Badge,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  ListItemButton,
  Collapse
} from '@mui/material';
import {
  Add,
  CheckCircle,
  Schedule,
  Warning,
  Person,
  Business,
  TrendingUp,
  CalendarToday,
  ExpandMore,
  Web,
  Description,
  Settings,
  Link,
  ContentCopy,
  CloudUpload,
  Download,
  FileUpload,
  Error,
  Info,
  History
} from '@mui/icons-material';
import { useCRM } from './context/CRMContext';
import apiClient from '../../../utils/apiClient';

const CRMLeadIntake = () => {
  const { leadIntakes, users, createLeadIntake, updateLeadIntake } = useCRM();
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingIntake, setEditingIntake] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [activeTab, setActiveTab] = useState(0);
  const [showWebhookInfo, setShowWebhookInfo] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [importHistory, setImportHistory] = useState([]);
  const [showImportHistory, setShowImportHistory] = useState(false);

  const [formData, setFormData] = useState({
    source: 'Website',
    name: '',
    email: '',
    phone: '',
    company: '',
    message: '',
    assigned_to: ''
  });

  const intakeSources = [
    { value: 'Website', label: 'Website Form', icon: <Web />, color: 'primary' },
    { value: 'Microsoft Forms', label: 'Microsoft Forms', icon: <Description />, color: 'info' },
    { value: 'Puzzel Agent', label: 'Puzzel Agent', icon: <Person />, color: 'success' },
    { value: 'Manual', label: 'Manual Entry', icon: <Add />, color: 'warning' }
  ];

  const getSourceIcon = (source) => {
    const intakeSource = intakeSources.find(s => s.value === source);
    return intakeSource ? intakeSource.icon : <Add />;
  };

  const getSourceColor = (source) => {
    const intakeSource = intakeSources.find(s => s.value === source);
    return intakeSource ? intakeSource.color : 'default';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'new': return 'warning';
      case 'processed': return 'info';
      case 'converted': return 'success';
      default: return 'default';
    }
  };

  const getUserName = (userId) => {
    const user = users?.find(u => u.id === userId);
    return user ? user.username : 'Unassigned';
  };

  const handleOpenDialog = (intake = null) => {
    if (intake) {
      setEditingIntake(intake);
      setFormData({
        source: intake.source || 'Website',
        name: intake.form_data?.name || '',
        email: intake.form_data?.email || '',
        phone: intake.form_data?.phone || '',
        company: intake.form_data?.company || '',
        message: intake.form_data?.message || '',
        assigned_to: intake.assigned_to || ''
      });
    } else {
      setEditingIntake(null);
      setFormData({
        source: 'Website',
        name: '',
        email: '',
        phone: '',
        company: '',
        message: '',
        assigned_to: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingIntake(null);
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async () => {
    try {
      const submitData = {
        source: formData.source,
        form_data: {
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
          company: formData.company,
          message: formData.message
        },
        assigned_to: formData.assigned_to
      };

      if (editingIntake) {
        await updateLeadIntake(editingIntake.id, submitData);
        setSnackbar({ open: true, message: 'Lead intake updated successfully!', severity: 'success' });
      } else {
        await createLeadIntake(submitData);
        setSnackbar({ open: true, message: 'Lead intake created successfully!', severity: 'success' });
      }
      handleCloseDialog();
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  const handleProcessIntake = async (intake) => {
    try {
      await updateLeadIntake(intake.id, { ...intake, status: 'processed' });
      setSnackbar({ open: true, message: 'Lead intake processed!', severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  const handleConvertIntake = async (intake) => {
    try {
      await updateLeadIntake(intake.id, { ...intake, status: 'converted' });
      setSnackbar({ open: true, message: 'Lead intake converted to lead!', severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: `Error: ${error.message}`, severity: 'error' });
    }
  };

  // File Upload Functions
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);

    setUploadProgress(0);
    setUploadStatus('uploading');

    try {
      const response = await apiClient.post('/crm/upload-leads', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        },
      });

      setUploadStatus('success');
      setSnackbar({ 
        open: true, 
        message: `Successfully imported ${response.data.processed_count} leads!`, 
        severity: 'success' 
      });
      
      // Refresh lead intakes
      // This would typically trigger a refresh of the lead intakes data
      
    } catch (error) {
      setUploadStatus('error');
      setSnackbar({ 
        open: true, 
        message: `Upload failed: ${error.response?.data?.error || error.message}`, 
        severity: 'error' 
      });
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await apiClient.get('/crm/upload-template');
      const blob = new Blob([response.data.template], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'lead_import_template.csv';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setSnackbar({ 
        open: true, 
        message: 'Template downloaded successfully!', 
        severity: 'success' 
      });
    } catch (error) {
      setSnackbar({ 
        open: true, 
        message: 'Failed to download template', 
        severity: 'error' 
      });
    }
  };

  const loadImportHistory = async () => {
    try {
      const response = await apiClient.get('/crm/bulk-import-status');
      setImportHistory(response.data.recent_imports);
    } catch (error) {
      console.error('Failed to load import history:', error);
    }
  };

  const newIntakes = leadIntakes?.filter(i => i.status === 'new') || [];
  const processedIntakes = leadIntakes?.filter(i => i.status === 'processed') || [];
  const convertedIntakes = leadIntakes?.filter(i => i.status === 'converted') || [];

  const renderIntakeCard = (intake) => {
    return (
      <Card key={intake.id} sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getSourceIcon(intake.source)}
              <Typography variant="h6" fontWeight="medium">
                {intake.form_data?.name || 'Unnamed Lead'}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip 
                label={intake.source} 
                color={getSourceColor(intake.source)}
                size="small"
              />
              <Chip 
                label={intake.status} 
                color={getStatusColor(intake.status)}
                size="small"
              />
            </Box>
          </Box>

          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                <strong>Email:</strong> {intake.form_data?.email || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Phone:</strong> {intake.form_data?.phone || 'N/A'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                <strong>Company:</strong> {intake.form_data?.company || 'N/A'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Assigned to:</strong> {getUserName(intake.assigned_to)}
              </Typography>
            </Grid>
          </Grid>

          {intake.form_data?.message && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              <strong>Message:</strong> {intake.form_data.message}
            </Typography>
          )}

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="caption" color="text.secondary">
              Received: {new Date(intake.created_at).toLocaleString()}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {intake.status === 'new' && (
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => handleProcessIntake(intake)}
                >
                  Process
                </Button>
              )}
              {intake.status === 'processed' && (
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => handleConvertIntake(intake)}
                >
                  Convert to Lead
                </Button>
              )}
              <Button
                size="small"
                variant="outlined"
                onClick={() => handleOpenDialog(intake)}
              >
                Edit
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    );
  };

  const webhookUrl = `${window.location.origin}/api/crm/lead-intake`;
  const webhookExample = {
    "source": "Website",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "company": "Example Corp",
    "message": "Interested in your services"
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" fontWeight="bold" color="primary">
            Lead Intake Management
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Manage leads from external forms and automatic intake
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<History />}
            onClick={() => {
              setShowImportHistory(!showImportHistory);
              if (!showImportHistory) loadImportHistory();
            }}
          >
            Import History
          </Button>
          <Button
            variant="outlined"
            startIcon={<CloudUpload />}
            onClick={() => setShowUploadDialog(true)}
          >
            Upload File
          </Button>
          <Button
            variant="outlined"
            startIcon={<Settings />}
            onClick={() => setShowWebhookInfo(!showWebhookInfo)}
          >
            Webhook Info
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenDialog()}
            sx={{ borderRadius: 2 }}
          >
            Manual Entry
          </Button>
        </Box>
      </Box>

      {/* Webhook Information */}
      {showWebhookInfo && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" fontWeight="medium" gutterBottom>
            Webhook Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Use this webhook URL to automatically create leads from external forms:
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <TextField
              value={webhookUrl}
              fullWidth
              size="small"
              InputProps={{ readOnly: true }}
            />
            <IconButton
              onClick={() => {
                navigator.clipboard.writeText(webhookUrl);
                setSnackbar({ open: true, message: 'Webhook URL copied!', severity: 'success' });
              }}
            >
              <ContentCopy />
            </IconButton>
          </Box>

          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle2">Example Webhook Payload</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ backgroundColor: 'grey.100', p: 2, borderRadius: 1 }}>
                <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace' }}>
                  {JSON.stringify(webhookExample, null, 2)}
                </Typography>
              </Box>
            </AccordionDetails>
          </Accordion>

          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Supported Sources:
            </Typography>
            <Grid container spacing={1}>
              {intakeSources.map(source => (
                <Grid item key={source.value}>
                  <Chip 
                    label={source.label} 
                    color={source.color}
                    size="small"
                    icon={source.icon}
                  />
                </Grid>
              ))}
            </Grid>
          </Box>
        </Paper>
      )}

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Badge badgeContent={newIntakes.length} color="warning">
                <Add sx={{ fontSize: 40, color: 'warning.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 1 }}>
                New Intakes
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {newIntakes.length} pending
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Badge badgeContent={processedIntakes.length} color="info">
                <Schedule sx={{ fontSize: 40, color: 'info.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 1 }}>
                Processed
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {processedIntakes.length} ready to convert
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Badge badgeContent={convertedIntakes.length} color="success">
                <CheckCircle sx={{ fontSize: 40, color: 'success.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 1 }}>
                Converted
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {convertedIntakes.length} leads created
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Badge badgeContent={leadIntakes?.length || 0} color="primary">
                <Person sx={{ fontSize: 40, color: 'primary.main' }} />
              </Badge>
              <Typography variant="h6" sx={{ mt: 1 }}>
                Total
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {leadIntakes?.length || 0} total intakes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab 
            label={
              <Badge badgeContent={newIntakes.length} color="warning">
                <span>New</span>
              </Badge>
            } 
          />
          <Tab 
            label={
              <Badge badgeContent={processedIntakes.length} color="info">
                <span>Processed</span>
              </Badge>
            } 
          />
          <Tab 
            label={
              <Badge badgeContent={convertedIntakes.length} color="success">
                <span>Converted</span>
              </Badge>
            } 
          />
        </Tabs>
      </Paper>

      {/* Intake Lists */}
      <Box>
        {activeTab === 0 && (
          <Box>
            {newIntakes.length > 0 ? (
              newIntakes.map(renderIntakeCard)
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No new lead intakes
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  New form submissions will appear here
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {activeTab === 1 && (
          <Box>
            {processedIntakes.length > 0 ? (
              processedIntakes.map(renderIntakeCard)
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No processed intakes
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Process new intakes to see them here
                </Typography>
              </Box>
            )}
          </Box>
        )}

        {activeTab === 2 && (
          <Box>
            {convertedIntakes.length > 0 ? (
              convertedIntakes.map(renderIntakeCard)
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No converted intakes
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Convert processed intakes to create leads
                </Typography>
              </Box>
            )}
          </Box>
        )}
      </Box>

      {/* File Upload Dialog */}
      <Dialog open={showUploadDialog} onClose={() => setShowUploadDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CloudUpload />
            Upload Lead File
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Upload CSV or Excel files to import leads in bulk. Download the template below for the correct format.
            </Typography>
            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={downloadTemplate}
              size="small"
            >
              Download Template
            </Button>
          </Box>

          {/* Drag & Drop Area */}
          <Box
            sx={{
              border: '2px dashed',
              borderColor: dragActive ? 'primary.main' : 'grey.300',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              backgroundColor: dragActive ? 'primary.50' : 'grey.50',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input').click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            
            {selectedFile ? (
              <Box>
                <FileUpload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {selectedFile.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </Typography>
              </Box>
            ) : (
              <Box>
                <CloudUpload sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Drag & drop your file here
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  or click to browse
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  Supports CSV, Excel (.xlsx, .xls)
                </Typography>
              </Box>
            )}
          </Box>

          {/* Upload Progress */}
          {uploadStatus === 'uploading' && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" gutterBottom>
                Uploading... {uploadProgress}%
              </Typography>
              <LinearProgress variant="determinate" value={uploadProgress} />
            </Box>
          )}

          {/* Upload Status */}
          {uploadStatus === 'success' && (
            <Alert severity="success" sx={{ mt: 2 }}>
              File uploaded successfully!
            </Alert>
          )}

          {uploadStatus === 'error' && (
            <Alert severity="error" sx={{ mt: 2 }}>
              Upload failed. Please try again.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUploadDialog(false)}>Cancel</Button>
          <Button
            onClick={handleFileUpload}
            variant="contained"
            disabled={!selectedFile || uploadStatus === 'uploading'}
          >
            Upload & Import
          </Button>
        </DialogActions>
      </Dialog>

      {/* Import History Dialog */}
      <Dialog open={showImportHistory} onClose={() => setShowImportHistory(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <History />
            Import History
          </Box>
        </DialogTitle>
        <DialogContent>
          <List>
            {importHistory.map((import_job) => (
              <ListItem key={import_job.id} divider>
                <ListItemIcon>
                  {import_job.status === 'completed' ? (
                    <CheckCircle color="success" />
                  ) : import_job.status === 'processing' ? (
                    <Schedule color="info" />
                  ) : (
                    <Error color="error" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={import_job.filename}
                  secondary={
                    <Box>
                      <Typography variant="body2">
                        Status: {import_job.status}
                      </Typography>
                      <Typography variant="body2">
                        Processed: {import_job.processed} leads
                      </Typography>
                      {import_job.errors > 0 && (
                        <Typography variant="body2" color="error">
                          Errors: {import_job.errors}
                        </Typography>
                      )}
                      <Typography variant="caption" color="text.secondary">
                        {new Date(import_job.created_at).toLocaleString()}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowImportHistory(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Add/Edit Intake Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingIntake ? 'Edit Lead Intake' : 'Manual Lead Entry'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 1 }}>
            <FormControl fullWidth>
              <InputLabel>Source</InputLabel>
              <Select
                value={formData.source}
                label="Source"
                onChange={(e) => handleInputChange('source', e.target.value)}
              >
                {intakeSources.map(source => (
                  <MenuItem key={source.value} value={source.value}>
                    {source.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Assign To</InputLabel>
              <Select
                value={formData.assigned_to}
                label="Assign To"
                onChange={(e) => handleInputChange('assigned_to', e.target.value)}
              >
                <MenuItem value="">Auto-assign</MenuItem>
                {users?.map(user => (
                  <MenuItem key={user.id} value={user.id}>
                    {user.username} ({user.role})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="Name"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              fullWidth
              required
            />

            <TextField
              label="Email"
              type="email"
              value={formData.email}
              onChange={(e) => handleInputChange('email', e.target.value)}
              fullWidth
              required
            />

            <TextField
              label="Phone"
              value={formData.phone}
              onChange={(e) => handleInputChange('phone', e.target.value)}
              fullWidth
            />

            <TextField
              label="Company"
              value={formData.company}
              onChange={(e) => handleInputChange('company', e.target.value)}
              fullWidth
            />

            <TextField
              label="Message/Notes"
              value={formData.message}
              onChange={(e) => handleInputChange('message', e.target.value)}
              fullWidth
              multiline
              rows={4}
              sx={{ gridColumn: '1 / -1' }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button 
            onClick={handleSubmit} 
            variant="contained"
            disabled={!formData.name || !formData.email}
          >
            {editingIntake ? 'Update' : 'Create Intake'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          severity={snackbar.severity}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default CRMLeadIntake;
