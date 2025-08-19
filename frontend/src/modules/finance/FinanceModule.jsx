import React, { useState } from 'react';
import {
  Box, Typography, Grid, Card, CardContent, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions, Tab, Tabs, Alert, Snackbar, LinearProgress, Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon
} from '@mui/icons-material';
import ImprovedForm from '../../components/ImprovedForm';
import DetailViewModal from '../../components/DetailViewModal';
import { useRealTimeData } from '../../hooks/useRealTimeData';

const FinanceModule = () => {
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
    data: accounts, 
    loading: accountsLoading, 
    error: accountsError,
    create: createAccount,
    update: updateAccount,
    remove: deleteAccount
  } = useRealTimeData('/api/finance/accounts');
  
  const { 
    data: journalEntries, 
    loading: journalEntriesLoading, 
    error: journalEntriesError,
    create: createJournalEntry,
    update: updateJournalEntry,
    remove: deleteJournalEntry
  } = useRealTimeData('/api/finance/journal-entries');

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
          case 'account':
            await updateAccount(editItem.id, formData);
            showSnackbar(`Account "${formData.name}" updated successfully`);
            break;
          case 'journal-entry':
            await updateJournalEntry(editItem.id, formData);
            showSnackbar(`Journal Entry "${formData.reference}" updated successfully`);
            break;
          default:
            break;
        }
      } else {
        switch (selectedItemType) {
          case 'account':
            await createAccount(formData);
            showSnackbar(`Account "${formData.name}" created successfully`);
            break;
          case 'journal-entry':
            await createJournalEntry(formData);
            showSnackbar(`Journal Entry "${formData.reference}" created successfully`);
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
        case 'account':
          await deleteAccount(deleteItem.id);
          showSnackbar(`Account "${deleteItem.name}" deleted successfully`);
          break;
        case 'journal-entry':
          await deleteJournalEntry(deleteItem.id);
          showSnackbar(`Journal Entry "${deleteItem.reference}" deleted successfully`);
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
  const financeMetrics = {
    totalAccounts: accounts?.length || 0,
    totalJournalEntries: journalEntries?.length || 0,
    totalDebits: journalEntries?.reduce((sum, entry) => sum + (entry?.total_debit || 0), 0) || 0,
    totalCredits: journalEntries?.reduce((sum, entry) => sum + (entry?.total_credit || 0), 0) || 0
  };

  const renderAccountsTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Chart of Accounts</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('account')}
        >
          Add Account
        </Button>
      </Box>

      {accountsLoading && <LinearProgress />}
      
      {accountsError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {accountsError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Code</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Parent</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {accounts.map((account) => (
              <TableRow key={account.id}>
                <TableCell>{account.code}</TableCell>
                <TableCell>{account.name}</TableCell>
                <TableCell>
                  <Chip
                    label={account.type || 'asset'}
                    color={account.type === 'asset' ? 'primary' : account.type === 'liability' ? 'error' : 'success'}
                    size="small"
                  />
                </TableCell>
                <TableCell>{account.parent_id || 'None'}</TableCell>
                <TableCell>
                  <Chip
                    label={account.is_active ? 'Active' : 'Inactive'}
                    color={account.is_active ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(account, 'account')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(account, 'account')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(account, 'account')} color="error" size="small">
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

  const renderJournalEntriesTab = () => (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Journal Entries</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleAdd('journal-entry')}
        >
          Add Journal Entry
        </Button>
      </Box>

      {journalEntriesLoading && <LinearProgress />}
      
      {journalEntriesError && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {journalEntriesError}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Reference</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Total Debit</TableCell>
              <TableCell>Total Credit</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {journalEntries.map((entry) => (
              <TableRow key={entry.id}>
                <TableCell>
                  {entry.entry_date ? new Date(entry.entry_date).toLocaleDateString() : 'N/A'}
                </TableCell>
                <TableCell>{entry.reference || 'N/A'}</TableCell>
                <TableCell>{entry.description || 'N/A'}</TableCell>
                <TableCell>
                  <Chip
                    label={entry.status || 'draft'}
                    color={entry.status === 'posted' ? 'success' : 'warning'}
                    size="small"
                  />
                </TableCell>
                <TableCell>${entry.total_debit || 0}</TableCell>
                <TableCell>${entry.total_credit || 0}</TableCell>
                <TableCell>
                  <Tooltip title="View Details">
                    <IconButton onClick={() => handleView(entry, 'journal-entry')} size="small">
                      <ViewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Edit">
                    <IconButton onClick={() => handleEdit(entry, 'journal-entry')} size="small">
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Delete">
                    <IconButton onClick={() => handleDelete(entry, 'journal-entry')} color="error" size="small">
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
        Financial Management
      </Typography>

      {/* Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Accounts
              </Typography>
              <Typography variant="h4">
                {financeMetrics.totalAccounts}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Journal Entries
              </Typography>
              <Typography variant="h4">
                {financeMetrics.totalJournalEntries}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Debits
              </Typography>
              <Typography variant="h4">
                ${financeMetrics.totalDebits.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Credits
              </Typography>
              <Typography variant="h4">
                ${financeMetrics.totalCredits.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Chart of Accounts" />
          <Tab label="Journal Entries" />
        </Tabs>
      </Box>

      {/* Tab Content */}
      {activeTab === 0 && renderAccountsTab()}
      {activeTab === 1 && renderJournalEntriesTab()}

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
        loading={accountsLoading || journalEntriesLoading}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog 
        open={deleteDialogOpen} 
        onClose={() => setDeleteDialogOpen(false)}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-content"
      >
        <DialogTitle id="delete-dialog-title">Confirm Delete</DialogTitle>
        <DialogContent id="delete-dialog-content">
          <Typography>
            Are you sure you want to delete this {selectedItemType}? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setDeleteDialogOpen(false)}
            aria-label="cancel delete"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmDelete} 
            color="error" 
            variant="contained"
            aria-label="confirm delete"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FinanceModule;