import React from 'react';
import { usePermissions } from '../hooks/usePermissions';
import { Box, Alert, Typography, Button } from '@mui/material';
import { Lock, VpnKey } from '@mui/icons-material';

/**
 * Permission Guard Component
 * Conditionally renders content based on user permissions
 */
const PermissionGuard = ({ 
  permission, 
  module, 
  anyPermissions, 
  fallback, 
  showFallback = true,
  children 
}) => {
  const { 
    hasPermission, 
    hasModuleAccess, 
    hasAnyPermission, 
    loading, 
    userRole 
  } = usePermissions();
  
  // Show loading state
  if (loading) {
    return fallback || null;
  }
  
  // Determine access
  let hasAccess = false;
  let accessType = '';
  
  if (permission) {
    hasAccess = hasPermission(permission);
    accessType = `permission: ${permission}`;
  } else if (module) {
    hasAccess = hasModuleAccess(module);
    accessType = `module: ${module}`;
  } else if (anyPermissions && Array.isArray(anyPermissions)) {
    hasAccess = hasAnyPermission(anyPermissions);
    accessType = `any of: ${anyPermissions.join(', ')}`;
  }
  
  // Render content if user has access
  if (hasAccess) {
    return children;
  }
  
  // Render custom fallback if provided
  if (fallback) {
    return fallback;
  }
  
  // Render default fallback if showFallback is true
  if (showFallback) {
    return (
      <Alert 
        severity="warning" 
        icon={<Lock />}
        sx={{ 
          my: 1,
          '& .MuiAlert-message': { width: '100%' }
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
              Access Restricted
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Requires {accessType} | Current role: {userRole || 'unknown'}
            </Typography>
          </Box>
          <VpnKey color="action" />
        </Box>
      </Alert>
    );
  }
  
  // Don't render anything
  return null;
};

/**
 * Permission Button Component
 * Button that's disabled when user lacks permission
 */
export const PermissionButton = ({ 
  permission, 
  module, 
  anyPermissions, 
  children, 
  disabled = false,
  ...buttonProps 
}) => {
  const { hasPermission, hasModuleAccess, hasAnyPermission, userRole } = usePermissions();
  
  let hasAccess = false;
  let accessReason = '';
  
  if (permission) {
    hasAccess = hasPermission(permission);
    accessReason = `Requires permission: ${permission}`;
  } else if (module) {
    hasAccess = hasModuleAccess(module);
    accessReason = `Requires module access: ${module}`;
  } else if (anyPermissions && Array.isArray(anyPermissions)) {
    hasAccess = hasAnyPermission(anyPermissions);
    accessReason = `Requires any of: ${anyPermissions.join(', ')}`;
  }
  
  const isDisabled = disabled || !hasAccess;
  
  return (
    <Button
      {...buttonProps}
      disabled={isDisabled}
      title={!hasAccess ? `${accessReason} (Current role: ${userRole})` : buttonProps.title}
    >
      {children}
    </Button>
  );
};

/**
 * Role Badge Component
 * Shows user's current role with appropriate styling
 */
export const RoleBadge = ({ showPermissionCount = false }) => {
  const { userRole, permissions } = usePermissions();
  
  const roleColors = {
    'admin': 'error',
    'manager': 'warning', 
    'accountant': 'info',
    'inventory_manager': 'success',
    'sales_user': 'primary',
    'user': 'default'
  };
  
  const roleLabels = {
    'admin': 'Admin',
    'manager': 'Manager',
    'accountant': 'Accountant', 
    'inventory_manager': 'Inventory Manager',
    'sales_user': 'Sales User',
    'user': 'User'
  };
  
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Typography variant="body2" color="text.secondary">
        Role:
      </Typography>
      <Typography 
        variant="body2" 
        sx={{ 
          px: 1, 
          py: 0.5, 
          borderRadius: 1, 
          bgcolor: `${roleColors[userRole] || 'default'}.light`,
          color: `${roleColors[userRole] || 'default'}.contrastText`,
          fontWeight: 'medium'
        }}
      >
        {roleLabels[userRole] || userRole || 'Unknown'}
      </Typography>
      {showPermissionCount && (
        <Typography variant="caption" color="text.secondary">
          ({permissions.length} permissions)
        </Typography>
      )}
    </Box>
  );
};

export default PermissionGuard;

