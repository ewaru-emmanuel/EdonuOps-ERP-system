import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  CircularProgress,
  Snackbar
} from '@mui/material';
import {
  Save as SaveIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Lock as LockIcon,
  Security as SecurityIcon,
  Person as PersonIcon,
  Group as GroupIcon,
  Undo as UndoIcon
} from '@mui/icons-material';
import apiClient from '../../../services/apiClient';

const PermissionManagement = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  
  // Data states
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [users, setUsers] = useState([]);
  const [rolePermissions, setRolePermissions] = useState({});
  const [userRoles, setUserRoles] = useState({});
  
  // Dialog states
  const [roleDialogOpen, setRoleDialogOpen] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  const [newRoleName, setNewRoleName] = useState('');
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [roleToDelete, setRoleToDelete] = useState(null);
  
  // Undo state for Gmail-style delete
  const [undoSnackbar, setUndoSnackbar] = useState({ open: false, role: null, deletedRole: null });
  const [undoTimer, setUndoTimer] = useState(null);
  
  // Load data
  useEffect(() => {
    loadData();
  }, []);
  
  const loadData = async () => {
    try {
      setLoading(true);
      const [rolesRes, permissionsRes, usersRes] = await Promise.all([
        apiClient.get('/api/admin/roles'),
        apiClient.get('/api/core/permissions'),
        apiClient.get('/api/admin/users')
      ]);
      
      setRoles(rolesRes.roles || rolesRes.data?.roles || []);
      setPermissions(permissionsRes.permissions || permissionsRes.data?.permissions || []);
      setUsers(usersRes.users || usersRes.data?.users || []);
      
      // Load role-permission mappings
      const rolePermMap = {};
      const rolesList = rolesRes.roles || rolesRes.data?.roles || [];
      rolesList.forEach(role => {
        // Superadmin gets ALL permissions (the ruler, the queen, the president - no limit)
        if (role.role_name === 'superadmin') {
          // For superadmin, assign ALL permission IDs
          rolePermMap[role.id] = permissions.map(p => p.id);
        } else if (role.permissions && Array.isArray(role.permissions)) {
          // Extract permission IDs from role object for other roles
          rolePermMap[role.id] = role.permissions.map(p => typeof p === 'object' ? p.id : p);
        } else {
          rolePermMap[role.id] = [];
        }
      });
      setRolePermissions(rolePermMap);
      
      // Load user-role mappings
      const userRoleMap = {};
      usersRes.users?.forEach(user => {
        userRoleMap[user.id] = user.role_id;
      });
      setUserRoles(userRoleMap);
      
    } catch (err) {
      setError('Failed to load data: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };
  
  const handlePermissionToggle = async (roleId, permissionId) => {
    try {
      const currentPerms = rolePermissions[roleId] || [];
      const hasPermission = currentPerms.includes(permissionId);
      
      const updatedPerms = hasPermission
        ? currentPerms.filter(p => p !== permissionId)
        : [...currentPerms, permissionId];
      
      // Optimistic update
      setRolePermissions({
        ...rolePermissions,
        [roleId]: updatedPerms
      });
      
      // Save to backend - use permission IDs
      await apiClient.put(`/api/core/permissions/roles/${roleId}`, {
        permissions: updatedPerms
      });
      
      setSuccess('Permission updated successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to update permission: ' + (err.message || 'Unknown error'));
      // Revert optimistic update
      loadData();
    }
  };
  
  const handleRoleChange = async (userId, newRoleId) => {
    try {
      await apiClient.put(`/api/admin/users/${userId}`, {
        role_id: newRoleId
      });
      
      setUserRoles({
        ...userRoles,
        [userId]: newRoleId
      });
      
      setSuccess('User role updated successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to update user role: ' + (err.message || 'Unknown error'));
    }
  };
  
  const handleCreateRole = async () => {
    try {
      setSaving(true);
      const response = await apiClient.post('/api/core/permissions/roles', {
        name: newRoleName,
        description: `Role: ${newRoleName}`
      });
      
      setRoles([...roles, response.role]);
      setRolePermissions({
        ...rolePermissions,
        [response.role.id]: []
      });
      
      setNewRoleName('');
      setEditingRole(null);
      setRoleDialogOpen(false);
      setSuccess('Role created successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to create role: ' + (err.message || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };
  
  const handleUpdateRoleName = async () => {
    if (!editingRole) return;
    
    try {
      setSaving(true);
      const response = await apiClient.put(`/api/core/permissions/roles/${editingRole.id}`, {
        name: newRoleName,
        description: editingRole.description || `Role: ${newRoleName}`
      });
      
      // Update the role in the roles list
      setRoles(roles.map(r => 
        r.id === editingRole.id 
          ? { ...r, role_name: newRoleName, description: response.role.description }
          : r
      ));
      
      setNewRoleName('');
      setEditingRole(null);
      setRoleDialogOpen(false);
      setSuccess('Role updated successfully');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError('Failed to update role: ' + (err.message || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };
  
  const handleSaveRole = () => {
    if (editingRole) {
      handleUpdateRoleName();
    } else {
      handleCreateRole();
    }
  };
  
  // Only protect superadmin role (critical system role)
  // All other default roles (admin, manager, accountant, user) can be edited/deleted
  // as companies may want different names
  const PROTECTED_ROLES = ['superadmin'];
  
  const isProtectedRole = (roleName) => {
    return PROTECTED_ROLES.includes(roleName?.toLowerCase());
  };
  
  const handleDeleteClick = (role) => {
    setRoleToDelete(role);
    setDeleteConfirmOpen(true);
  };
  
  const handleDeleteConfirm = async () => {
    if (!roleToDelete) return;
    
    const roleId = roleToDelete.id;
    const roleName = roleToDelete.role_name;
    const deletedRole = { ...roleToDelete };
    
    // Optimistically remove from UI
    setRoles(roles.filter(r => r.id !== roleId));
    setDeleteConfirmOpen(false);
    
    // Show undo snackbar immediately (Gmail-style)
    setUndoSnackbar({
      open: true,
      role: roleName,
      deletedRole: deletedRole
    });
    
    // Schedule actual deletion after 5 seconds (undo window)
    const deleteTimer = setTimeout(async () => {
    try {
      await apiClient.delete(`/api/core/permissions/roles/${roleId}`);
        setUndoSnackbar({ open: false, role: null, deletedRole: null });
        setSuccess(`Role "${roleName}" deleted successfully`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
        // Revert on error
        setRoles([...roles, deletedRole].sort((a, b) => a.id - b.id));
      setError('Failed to delete role: ' + (err.message || 'Unknown error'));
        setUndoSnackbar({ open: false, role: null, deletedRole: null });
      }
    }, 5000);
    
    setUndoTimer(deleteTimer);
    setRoleToDelete(null);
  };
  
  const handleUndoDelete = () => {
    if (!undoSnackbar.deletedRole) return;
    
    // Clear the deletion timer
    if (undoTimer) {
      clearTimeout(undoTimer);
      setUndoTimer(null);
    }
    
    // Restore the role in the list
    setRoles([...roles, undoSnackbar.deletedRole].sort((a, b) => a.id - b.id));
    
    // Close snackbar
    setUndoSnackbar({ open: false, role: null, deletedRole: null });
    
    setSuccess('Delete cancelled');
    setTimeout(() => setSuccess(null), 3000);
  };
  
  // Group permissions by module
  const groupedPermissions = permissions.reduce((acc, perm) => {
    const [module] = perm.name.split('.');
    if (!acc[module]) acc[module] = [];
    acc[module].push(perm);
    return acc;
  }, {});
  
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Permission Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => {
            setEditingRole(null);
            setNewRoleName('');
            setRoleDialogOpen(true);
          }}
        >
          Create Role
        </Button>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}
      
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab icon={<GroupIcon />} label="Role Permissions" />
          <Tab icon={<PersonIcon />} label="User Roles" />
        </Tabs>
      </Paper>
      
      {tabValue === 0 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Permission</TableCell>
                {roles.map(role => (
                  <TableCell key={role.id} align="center">
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                      <Typography variant="subtitle2">{role.role_name}</Typography>
                        {role.role_name === 'superadmin' && (
                          <Chip 
                            label="ALL" 
                            size="small" 
                            color="primary" 
                            sx={{ 
                              height: 18, 
                              fontSize: '0.65rem',
                              fontWeight: 'bold',
                              bgcolor: 'primary.main',
                              color: 'white'
                            }} 
                          />
                        )}
                      </Box>
                      <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center', mt: 0.5 }}>
                        <Tooltip title={isProtectedRole(role.role_name) ? "Cannot edit superadmin role" : "Edit"}>
                          <span>
                            <IconButton 
                              size="small" 
                              onClick={() => {
                                if (!isProtectedRole(role.role_name)) {
                            setEditingRole(role);
                            setNewRoleName(role.role_name);
                            setRoleDialogOpen(true);
                                }
                              }}
                              disabled={isProtectedRole(role.role_name)}
                            >
                            <EditIcon fontSize="small" />
                          </IconButton>
                          </span>
                        </Tooltip>
                        <Tooltip title={isProtectedRole(role.role_name) ? "Cannot delete superadmin role" : "Delete"}>
                          <span>
                            <IconButton 
                              size="small" 
                              onClick={() => {
                                if (!isProtectedRole(role.role_name)) {
                                  handleDeleteClick(role);
                                }
                              }}
                              disabled={isProtectedRole(role.role_name)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </span>
                          </Tooltip>
                      </Box>
                    </Box>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {Object.entries(groupedPermissions).map(([module, modulePerms]) => (
                <React.Fragment key={module}>
                  <TableRow>
                    <TableCell colSpan={roles.length + 1}>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', textTransform: 'uppercase' }}>
                        {module}
                      </Typography>
                    </TableCell>
                  </TableRow>
                  {modulePerms.map(permission => (
                    <TableRow key={permission.id}>
                      <TableCell>
                        <Typography variant="body2">{permission.name}</Typography>
                        {permission.description && (
                          <Typography variant="caption" color="text.secondary">
                            {permission.description}
                          </Typography>
                        )}
                      </TableCell>
                      {roles.map(role => {
                        const isSuperadmin = role.role_name === 'superadmin';
                        const hasPermission = (rolePermissions[role.id] || []).includes(permission.id);
                        
                        return (
                        <TableCell key={role.id} align="center">
                            <Tooltip 
                              title={isSuperadmin ? "Superadmin has ALL permissions (no restrictions)" : ""}
                              placement="top"
                            >
                          <Checkbox
                                checked={isSuperadmin ? true : hasPermission}
                            onChange={() => handlePermissionToggle(role.id, permission.id)}
                                disabled={isSuperadmin}
                                sx={{
                                  '&.Mui-disabled': {
                                    color: 'primary.main',
                                    opacity: 0.7
                                  }
                                }}
                          />
                            </Tooltip>
                        </TableCell>
                        );
                      })}
                    </TableRow>
                  ))}
                </React.Fragment>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      
      {tabValue === 1 && (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Current Role</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map(user => (
                <TableRow key={user.id}>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>
                    <Chip
                      label={roles.find(r => r.id === userRoles[user.id])?.role_name || 'No Role'}
                      color="primary"
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <TextField
                      select
                      size="small"
                      value={userRoles[user.id] || ''}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      SelectProps={{
                        native: true
                      }}
                      sx={{ minWidth: 150 }}
                    >
                      <option value="">Select Role</option>
                      {roles.map(role => (
                        <option key={role.id} value={role.id}>
                          {role.role_name}
                        </option>
                      ))}
                    </TextField>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
      
      {/* Create/Edit Role Dialog */}
      <Dialog open={roleDialogOpen} onClose={() => setRoleDialogOpen(false)}>
        <DialogTitle>
          {editingRole ? 'Edit Role' : 'Create New Role'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Role Name"
            fullWidth
            variant="outlined"
            value={newRoleName}
            onChange={(e) => setNewRoleName(e.target.value)}
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setRoleDialogOpen(false);
            setEditingRole(null);
            setNewRoleName('');
          }}>Cancel</Button>
          <Button
            onClick={handleSaveRole}
            variant="contained"
            disabled={!newRoleName || saving}
            startIcon={saving ? <CircularProgress size={16} /> : <SaveIcon />}
          >
            {editingRole ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Delete Confirmation Dialog */}
      <Dialog 
        open={deleteConfirmOpen} 
        onClose={() => {
          setDeleteConfirmOpen(false);
          setRoleToDelete(null);
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Delete Role</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            Are you sure you want to delete the role <strong>"{roleToDelete?.role_name}"</strong>?
          </Alert>
          <Typography variant="body2" color="text.secondary">
            This action cannot be undone. If users are assigned to this role, you'll need to reassign them first.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => {
            setDeleteConfirmOpen(false);
            setRoleToDelete(null);
          }}>
            Cancel
          </Button>
          <Button
            onClick={handleDeleteConfirm}
            variant="contained"
            color="error"
            startIcon={<DeleteIcon />}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Gmail-style Undo Snackbar */}
      <Snackbar
        open={undoSnackbar.open}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
        autoHideDuration={5000}
        onClose={() => {
          setUndoSnackbar({ open: false, role: null, deletedRole: null });
          if (undoTimer) clearTimeout(undoTimer);
        }}
      >
        <Alert
          severity="info"
          action={
            <Button
              color="inherit"
              size="small"
              startIcon={<UndoIcon />}
              onClick={handleUndoDelete}
              sx={{ textTransform: 'none' }}
            >
              UNDO
            </Button>
          }
          sx={{ 
            minWidth: 300,
            '& .MuiAlert-action': {
              alignItems: 'center'
            }
          }}
        >
          Role "{undoSnackbar.role}" deleted
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default PermissionManagement;

