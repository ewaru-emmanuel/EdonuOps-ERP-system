import React, { useState } from 'react';
import {
  Box,
  Button,
  Menu,
  MenuItem,
  Typography,
  Avatar,
  Chip,
  Divider,
  ListItemIcon,
  ListItemText,
  Tooltip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Business,
  ExpandMore,
  Check,
  AdminPanelSettings,
  Person,
  SupervisorAccount,
  Visibility,
  Settings,
  Refresh
} from '@mui/icons-material';
import { useTenant } from '../contexts/TenantContext';

const TenantSwitcher = () => {
  const {
    currentTenant,
    userTenants,
    loading,
    error,
    switchTenant,
    refreshTenants,
    isMultiTenant,
    canSwitchTenants
  } = useTenant();

  const [anchorEl, setAnchorEl] = useState(null);
  const [switching, setSwitching] = useState(false);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleTenantSelect = async (tenantId) => {
    if (tenantId === currentTenant?.tenant_id) {
      handleClose();
      return;
    }

    try {
      setSwitching(true);
      await switchTenant(tenantId);
      handleClose();
    } catch (err) {
      console.error('Error switching tenant:', err);
    } finally {
      setSwitching(false);
    }
  };

  const handleRefresh = async () => {
    try {
      await refreshTenants();
    } catch (err) {
      console.error('Error refreshing tenants:', err);
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'admin':
        return <AdminPanelSettings fontSize="small" />;
      case 'manager':
        return <SupervisorAccount fontSize="small" />;
      case 'user':
        return <Person fontSize="small" />;
      default:
        return <Visibility fontSize="small" />;
    }
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin':
        return 'error';
      case 'manager':
        return 'warning';
      case 'user':
        return 'primary';
      default:
        return 'default';
    }
  };

  const getPlanColor = (plan) => {
    switch (plan) {
      case 'enterprise':
        return 'success';
      case 'premium':
        return 'info';
      case 'basic':
        return 'warning';
      case 'free':
        return 'default';
      default:
        return 'default';
    }
  };

  if (!currentTenant) {
    return (
      <Alert severity="warning" sx={{ mb: 2 }}>
        No tenant selected. Please contact your administrator.
      </Alert>
    );
  }

  return (
    <Box>
      <Tooltip title={canSwitchTenants ? "Switch tenant" : "Current tenant"}>
        <span>
          <Button
            onClick={handleClick}
            disabled={!canSwitchTenants}
            sx={{
              color: 'text.primary',
              textTransform: 'none',
              fontWeight: 500,
              minWidth: 200,
              justifyContent: 'space-between',
              '&:hover': {
                backgroundColor: canSwitchTenants ? 'action.hover' : 'transparent'
              }
            }}
          >
            <Box display="flex" alignItems="center" gap={1}>
              {/* Clean top bar - no chips or icons */}
            </Box>
          </Button>
        </span>
      </Tooltip>

      <Menu
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        PaperProps={{
          sx: { 
            minWidth: 300, 
            mt: 1,
            maxHeight: 400,
            overflow: 'auto'
          }
        }}
        transformOrigin={{ horizontal: 'left', vertical: 'top' }}
        anchorOrigin={{ horizontal: 'left', vertical: 'bottom' }}
      >
        {/* Header */}
        <Box sx={{ p: 2, pb: 1 }}>
          <Typography variant="h6" fontWeight="bold">
            Switch Tenant
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Select a different company to work with
          </Typography>
        </Box>

        <Divider />

        {/* Error Display */}
        {error && (
          <Box sx={{ p: 2 }}>
            <Alert severity="error" size="small">
              {error}
            </Alert>
          </Box>
        )}

        {/* Loading State */}
        {loading && (
          <Box sx={{ p: 2, textAlign: 'center' }}>
            <CircularProgress size={20} />
            <Typography variant="body2" sx={{ mt: 1 }}>
              Loading tenants...
            </Typography>
          </Box>
        )}

        {/* Tenant List */}
        {userTenants.map((tenant) => (
          <MenuItem
            key={tenant.tenant_id}
            onClick={() => handleTenantSelect(tenant.tenant_id)}
            disabled={switching}
            selected={tenant.tenant_id === currentTenant?.tenant_id}
            sx={{
              py: 1.5,
              px: 2,
              '&:hover': {
                backgroundColor: 'action.hover'
              }
            }}
          >
            <ListItemIcon>
              <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                <Business />
              </Avatar>
            </ListItemIcon>
            
            <ListItemText
              primary={
                <Box display="flex" alignItems="center" gap={1}>
                  <Typography variant="body2" fontWeight="bold">
                    {tenant.tenant_name}
                  </Typography>
                  {tenant.is_default && (
                    <Chip label="Default" size="small" color="primary" />
                  )}
                  {tenant.tenant_id === currentTenant?.tenant_id && (
                    <Check color="primary" fontSize="small" />
                  )}
                </Box>
              }
              secondary={
                <Box>
                  <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                    <Chip
                      label={tenant.tenant_plan}
                      size="small"
                      color={getPlanColor(tenant.tenant_plan)}
                      variant="outlined"
                    />
                    <Chip
                      label={tenant.role}
                      size="small"
                      color={getRoleColor(tenant.role)}
                      icon={getRoleIcon(tenant.role)}
                    />
                  </Box>
                  {tenant.tenant_domain && (
                    <Typography variant="caption" color="text.secondary">
                      {tenant.tenant_domain}
                    </Typography>
                  )}
                </Box>
              }
            />
          </MenuItem>
        ))}

        <Divider />

        {/* Actions */}
        <Box sx={{ p: 1 }}>
          <Button
            fullWidth
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading}
            size="small"
            sx={{ textTransform: 'none' }}
          >
            Refresh Tenants
          </Button>
        </Box>
      </Menu>
    </Box>
  );
};

export default TenantSwitcher;
