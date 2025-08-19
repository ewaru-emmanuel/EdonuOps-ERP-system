import React, { useState } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Tab, Tabs, Alert, Snackbar, LinearProgress, Tooltip
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

const CRMModule = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  
  // Form and dialog states
  const [formOpen, setFormOpen] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteItem, setDeleteItem] = useState(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedItemType, setSelectedItemType] = useState('');

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

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
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

  const handleSave = async (formData) => {
    try {
      if (editItem) {
        switch (selectedItemType) {
          case 'contact':
            await updateContact(editItem.id, formData);
            showSnackbar(`Contact "${formData.first_name} ${formData.last_name}" updated successfully`);
            break;
          case 'lead':
            await updateLead(editItem.id, formData);
            showSnackbar(`Lead "${formData.first_name} ${formData.last_name}" updated successfully`);
            break;
          case 'opportunity':
            await updateOpportunity(editItem.id, formData);
            showSnackbar(`Opportunity "${formData.name}" updated successfully`);
            break;
          default:
            break;
        }
      } else {
        switch (selectedItemType) {
          case 'contact':
            await createContact(formData);
            showSnackbar(`Contact "${formData.first_name} ${formData.last_name}" created successfully`);
            break;
          case 'lead':
            await createLead(formData);
            showSnackbar(`Lead "${formData.first_name} ${formData.last_name}" created successfully`);
            break;
          case 'opportunity':
            await createOpportunity(formData);
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
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('contact')}
        >
          Add Contact
        </Button>
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
            {contacts.map((contact) => (
              <TableRow key={contact.id}>
                <TableCell>{`${contact.first_name} ${contact.last_name}`}</TableCell>
                <TableCell>{contact.email || 'N/A'}</TableCell>
                <TableCell>{contact.phone || 'N/A'}</TableCell>
                <TableCell>{contact.company || 'N/A'}</TableCell>
                <TableCell>
                  <Chip
                    label={contact.type || 'customer'}
                    color={contact.type === 'customer' ? 'primary' : 'secondary'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={contact.status || 'active'}
                    color={contact.status === 'active' ? 'success' : 'default'}
                    size="small"
                  />
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
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('lead')}
        >
          Add Lead
        </Button>
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
              <TableCell>Source</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {leads.map((lead) => (
              <TableRow key={lead.id}>
                <TableCell>{`${lead.first_name} ${lead.last_name}`}</TableCell>
                <TableCell>{lead.email || 'N/A'}</TableCell>
                <TableCell>{lead.phone || 'N/A'}</TableCell>
                <TableCell>{lead.company || 'N/A'}</TableCell>
                <TableCell>
                  <Chip
                    label={lead.source || 'website'}
                    color="info"
                    size="small"
                  />
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

  const renderOpportunitiesTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Opportunities</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('opportunity')}
        >
          Add Opportunity
        </Button>
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
            {opportunities.map((opportunity) => (
              <TableRow key={opportunity.id}>
                <TableCell>{opportunity.name}</TableCell>
                <TableCell>{opportunity.contact_id || 'N/A'}</TableCell>
                <TableCell>${opportunity.amount || 0}</TableCell>
                <TableCell>
                  <Chip
                    label={opportunity.stage || 'prospecting'}
                    color={opportunity.stage === 'closed' ? 'success' : 'primary'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{opportunity.probability || 0}%</TableCell>
                <TableCell>
                  {opportunity.expected_close_date ? new Date(opportunity.expected_close_date).toLocaleDateString() : 'N/A'}
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

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Customer Relationship Management
      </Typography>

      {/* Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Contacts
              </Typography>
              <Typography variant="h4">
                {crmMetrics.totalContacts}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Leads
              </Typography>
              <Typography variant="h4">
                {crmMetrics.totalLeads}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Opportunities
              </Typography>
              <Typography variant="h4">
                {crmMetrics.totalOpportunities}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pipeline Value
              </Typography>
              <Typography variant="h4">
                ${crmMetrics.totalValue.toLocaleString()}
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
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && renderContactsTab()}
      {activeTab === 1 && renderLeadsTab()}
      {activeTab === 2 && renderOpportunitiesTab()}

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
        title={`${selectedItemType.charAt(0).toUpperCase() + selectedItemType.slice(1)} Details`}
      />

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
        title={selectedItemType.charAt(0).toUpperCase() + selectedItemType.slice(1)}
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
    </Box>
  );
};

export default CRMModule;
