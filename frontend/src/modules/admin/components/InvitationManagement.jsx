import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar,
  CircularProgress,
  Tooltip,
  Grid,
  Divider,
  Avatar,
  Badge,
  Tabs,
  Tab,
  FormControlLabel,
  Switch,
  InputAdornment,
  Menu,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Add as AddIcon,
  Email as EmailIcon,
  PersonAdd as PersonAddIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Send as SendIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Cancel as CancelIcon,
  Visibility as VisibilityIcon,
  ContentCopy as ContentCopyIcon,
  FilterList as FilterListIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  GroupAdd as GroupAddIcon,
  Analytics as AnalyticsIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import { apiClient } from '../../../utils/apiClient';

const InvitationManagement = () => {
  // State management
  const [invites, setInvites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [openCreateDialog, setOpenCreateDialog] = useState(false);
  const [openBulkDialog, setOpenBulkDialog] = useState(false);
  const [selectedInvites, setSelectedInvites] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterRole, setFilterRole] = useState('all');
  const [currentTab, setCurrentTab] = useState(0);
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedInvite, setSelectedInvite] = useState(null);

  // Form states
  const [inviteForm, setInviteForm] = useState({
    email: '',
    role: 'user',
    message: '',
    expires_days: 7
  });

  const [bulkForm, setBulkForm] = useState({
    emails: '',
    role: 'user',
    message: '',
    expires_days: 7
  });

  // Available roles
  const roles = [
    { value: 'user', label: 'User', description: 'Basic access to assigned modules' },
    { value: 'manager', label: 'Manager', description: 'Team management and reporting access' },
    { value: 'admin', label: 'Admin', description: 'Full tenant management access' },
    { value: 'superadmin', label: 'Super Admin', description: 'System-wide administrative access' }
  ];

  // Load invitations on component mount
  useEffect(() => {
    loadInvites();
  }, []);

  // Load invitations from API
  const loadInvites = async () => {
    setLoading(true);
    try {
      const response = await apiClient.get('/api/invites/list-invites');
      setInvites(response.data.invites || []);
    } catch (err) {
      setError('Failed to load invitations');
      console.error('Error loading invites:', err);
    } finally {
      setLoading(false);
    }
  };

  // Create single invitation
  const createInvite = async () => {
    setLoading(true);
    try {
      const response = await apiClient.post('/api/invites/create-invite', inviteForm);
      setSuccess('Invitation sent successfully!');
      setOpenCreateDialog(false);
      setInviteForm({ email: '', role: 'user', message: '', expires_days: 7 });
      loadInvites();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create invitation');
    } finally {
      setLoading(false);
    }
  };

  // Create bulk invitations
  const createBulkInvites = async () => {
    setLoading(true);
    try {
      const emails = bulkForm.emails.split('\n').filter(email => email.trim());
      const promises = emails.map(email => 
        apiClient.post('/api/invites/create-invite', {
          ...bulkForm,
          email: email.trim()
        })
      );
      
      await Promise.all(promises);
      setSuccess(`${emails.length} invitations sent successfully!`);
      setOpenBulkDialog(false);
      setBulkForm({ emails: '', role: 'user', message: '', expires_days: 7 });
      loadInvites();
    } catch (err) {
      setError('Failed to create bulk invitations');
    } finally {
      setLoading(false);
    }
  };

  // Cancel invitation
  const cancelInvite = async (inviteId) => {
    try {
      await apiClient.delete(`/api/invites/cancel-invite/${inviteId}`);
      setSuccess('Invitation cancelled successfully!');
      loadInvites();
    } catch (err) {
      setError('Failed to cancel invitation');
    }
  };

  // Resend invitation
  const resendInvite = async (inviteId) => {
    try {
      await apiClient.post(`/api/invites/resend-invite/${inviteId}`);
      setSuccess('Invitation resent successfully!');
      loadInvites();
    } catch (err) {
      setError('Failed to resend invitation');
    }
  };

  // Cleanup expired invitations
  const cleanupExpired = async () => {
    try {
      const response = await apiClient.post('/api/invites/cleanup-expired');
      setSuccess(response.data.message);
      loadInvites();
    } catch (err) {
      setError('Failed to cleanup expired invitations');
    }
  };

  // Copy invitation link
  const copyInviteLink = (token) => {
    const link = `${window.location.origin}/register?invite=${token}`;
    navigator.clipboard.writeText(link);
    setSuccess('Invitation link copied to clipboard!');
  };

  // Get status chip
  const getStatusChip = (invite) => {
    const now = new Date();
    const expiresAt = new Date(invite.expires_at);
    
    if (invite.used) {
      return <Chip icon={<CheckCircleIcon />} label="Used" color="success" size="small" />;
    } else if (expiresAt < now) {
      return <Chip icon={<CancelIcon />} label="Expired" color="error" size="small" />;
    } else {
      return <Chip icon={<ScheduleIcon />} label="Pending" color="warning" size="small" />;
    }
  };

  // Get role chip
  const getRoleChip = (roleName) => {
    const role = roles.find(r => r.value === roleName);
    const colors = {
      'superadmin': 'error',
      'admin': 'warning',
      'manager': 'info',
      'user': 'default'
    };
    return (
      <Chip 
        label={role?.label || roleName} 
        color={colors[roleName] || 'default'} 
        size="small" 
      />
    );
  };

  // Filter invitations
  const filteredInvites = invites.filter(invite => {
    const matchesSearch = invite.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         invite.invited_by?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || 
      (filterStatus === 'pending' && !invite.used && new Date(invite.expires_at) > new Date()) ||
      (filterStatus === 'used' && invite.used) ||
      (filterStatus === 'expired' && !invite.used && new Date(invite.expires_at) < new Date());
    
    const matchesRole = filterRole === 'all' || invite.role_name === filterRole;
    
    return matchesSearch && matchesStatus && matchesRole;
  });

  // Get invitation statistics
  const getStats = () => {
    const total = invites.length;
    const pending = invites.filter(i => !i.used && new Date(i.expires_at) > new Date()).length;
    const used = invites.filter(i => i.used).length;
    const expired = invites.filter(i => !i.used && new Date(i.expires_at) < new Date()).length;
    
    return { total, pending, used, expired };
  };

  const stats = getStats();

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Invitation Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Manage user invitations and track invitation status
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadInvites}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<GroupAddIcon />}
            onClick={() => setOpenBulkDialog(true)}
          >
            Bulk Invite
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenCreateDialog(true)}
          >
            Send Invitation
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <EmailIcon color="primary" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h6">{stats.total}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Invitations
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <ScheduleIcon color="warning" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h6">{stats.pending}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckCircleIcon color="success" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h6">{stats.used}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Accepted
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CancelIcon color="error" sx={{ mr: 2 }} />
                <Box>
                  <Typography variant="h6">{stats.expired}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Expired
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters and Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                placeholder="Search by email or inviter..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="all">All Status</MenuItem>
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="used">Used</MenuItem>
                  <MenuItem value="expired">Expired</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  value={filterRole}
                  onChange={(e) => setFilterRole(e.target.value)}
                  label="Role"
                >
                  <MenuItem value="all">All Roles</MenuItem>
                  {roles.map(role => (
                    <MenuItem key={role.value} value={role.value}>
                      {role.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<FilterListIcon />}
                onClick={() => {
                  setSearchTerm('');
                  setFilterStatus('all');
                  setFilterRole('all');
                }}
              >
                Clear Filters
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Invitations Table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Email</TableCell>
                  <TableCell>Role</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Invited By</TableCell>
                  <TableCell>Created</TableCell>
                  <TableCell>Expires</TableCell>
                  <TableCell>Message</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <CircularProgress />
                    </TableCell>
                  </TableRow>
                ) : filteredInvites.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center">
                      <Typography variant="body2" color="text.secondary">
                        No invitations found
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredInvites.map((invite) => (
                    <TableRow key={invite.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 2, width: 32, height: 32 }}>
                            <EmailIcon />
                          </Avatar>
                          <Typography variant="body2">{invite.email}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{getRoleChip(invite.role_name)}</TableCell>
                      <TableCell>{getStatusChip(invite)}</TableCell>
                      <TableCell>
                        <Typography variant="body2">{invite.invited_by}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {format(new Date(invite.created_at), 'MMM dd, yyyy')}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {format(new Date(invite.expires_at), 'MMM dd, yyyy')}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                          {invite.message || '-'}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="Copy Invitation Link">
                            <IconButton
                              size="small"
                              onClick={() => copyInviteLink(invite.token)}
                            >
                              <ContentCopyIcon />
                            </IconButton>
                          </Tooltip>
                          {!invite.used && new Date(invite.expires_at) > new Date() && (
                            <>
                              <Tooltip title="Resend Invitation">
                                <IconButton
                                  size="small"
                                  onClick={() => resendInvite(invite.id)}
                                >
                                  <SendIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Cancel Invitation">
                                <IconButton
                                  size="small"
                                  onClick={() => cancelInvite(invite.id)}
                                  color="error"
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </Tooltip>
                            </>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create Invitation Dialog */}
      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Send Invitation</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={inviteForm.email}
              onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
              margin="normal"
              required
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Role</InputLabel>
              <Select
                value={inviteForm.role}
                onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                label="Role"
              >
                {roles.map(role => (
                  <MenuItem key={role.value} value={role.value}>
                    <Box>
                      <Typography variant="body1">{role.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {role.description}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Personal Message (Optional)"
              multiline
              rows={3}
              value={inviteForm.message}
              onChange={(e) => setInviteForm({ ...inviteForm, message: e.target.value })}
              margin="normal"
              placeholder="Add a personal message to include in the invitation email..."
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Expires In</InputLabel>
              <Select
                value={inviteForm.expires_days}
                onChange={(e) => setInviteForm({ ...inviteForm, expires_days: e.target.value })}
                label="Expires In"
              >
                <MenuItem value={1}>1 Day</MenuItem>
                <MenuItem value={3}>3 Days</MenuItem>
                <MenuItem value={7}>7 Days</MenuItem>
                <MenuItem value={14}>14 Days</MenuItem>
                <MenuItem value={30}>30 Days</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>Cancel</Button>
          <Button 
            onClick={createInvite} 
            variant="contained" 
            disabled={loading || !inviteForm.email}
          >
            {loading ? <CircularProgress size={20} /> : 'Send Invitation'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Invitation Dialog */}
      <Dialog open={openBulkDialog} onClose={() => setOpenBulkDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Bulk Send Invitations</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <TextField
              fullWidth
              label="Email Addresses"
              multiline
              rows={6}
              value={bulkForm.emails}
              onChange={(e) => setBulkForm({ ...bulkForm, emails: e.target.value })}
              margin="normal"
              placeholder="Enter email addresses, one per line..."
              helperText="Enter one email address per line"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Role</InputLabel>
              <Select
                value={bulkForm.role}
                onChange={(e) => setBulkForm({ ...bulkForm, role: e.target.value })}
                label="Role"
              >
                {roles.map(role => (
                  <MenuItem key={role.value} value={role.value}>
                    <Box>
                      <Typography variant="body1">{role.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {role.description}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              fullWidth
              label="Personal Message (Optional)"
              multiline
              rows={3}
              value={bulkForm.message}
              onChange={(e) => setBulkForm({ ...bulkForm, message: e.target.value })}
              margin="normal"
              placeholder="Add a personal message to include in all invitation emails..."
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Expires In</InputLabel>
              <Select
                value={bulkForm.expires_days}
                onChange={(e) => setBulkForm({ ...bulkForm, expires_days: e.target.value })}
                label="Expires In"
              >
                <MenuItem value={1}>1 Day</MenuItem>
                <MenuItem value={3}>3 Days</MenuItem>
                <MenuItem value={7}>7 Days</MenuItem>
                <MenuItem value={14}>14 Days</MenuItem>
                <MenuItem value={30}>30 Days</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenBulkDialog(false)}>Cancel</Button>
          <Button 
            onClick={createBulkInvites} 
            variant="contained" 
            disabled={loading || !bulkForm.emails.trim()}
          >
            {loading ? <CircularProgress size={20} /> : 'Send Invitations'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Snackbars */}
      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
      >
        <Alert onClose={() => setSuccess(null)} severity="success">
          {success}
        </Alert>
      </Snackbar>
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default InvitationManagement;

