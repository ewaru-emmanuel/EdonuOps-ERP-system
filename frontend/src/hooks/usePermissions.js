import { useState, useEffect, useContext, createContext, useCallback } from 'react';
import { useAuth } from './useAuth';
import apiClient from '../services/apiClient';

// Create permissions context
const PermissionsContext = createContext(null);

export const PermissionsProvider = ({ children }) => {
  const [permissions, setPermissions] = useState([]);
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState(null);
  const { user, isAuthenticated, loading: authLoading } = useAuth();

  // Load user permissions from backend
  const loadUserPermissions = useCallback(async () => {
    if (authLoading) {
      return; // Wait for auth to finish loading
    }
    
    if (!isAuthenticated || !user) {
      setPermissions([]);
      setModules([]);
      setUserRole(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.get('/permissions/user/permissions');
      
      if (response && response.permissions) {
        setPermissions(response.permissions);
        setModules(response.modules || []);
        setUserRole(response.role);
      }
    } catch (error) {
      // Don't log error if it's just unauthorized (expected when not logged in)
      if (!error.message?.includes('401') && !error.message?.includes('UNAUTHORIZED')) {
        console.error('Failed to load user permissions:', error);
      }
      // Set default permissions for fallback
      setPermissions([]);
      setModules(['general']);
      setUserRole('user');
    } finally {
      setLoading(false);
    }
  }, [authLoading, isAuthenticated, user]);

  // Load permissions when user changes
  useEffect(() => {
    loadUserPermissions();
  }, [loadUserPermissions]);

  // Permission checking functions
  const hasPermission = (permissionName) => {
    if (!permissionName) return false;
    
    // Admin has all permissions
    if (userRole === 'admin') return true;
    
    // Check if user has specific permission
    return permissions.some(perm => perm.name === permissionName);
  };

  const hasModuleAccess = (moduleName) => {
    if (!moduleName) return false;
    
    // Admin has all module access
    if (userRole === 'admin') return true;
    
    // Check if user has access to module
    return modules.includes(moduleName);
  };

  const hasAnyPermission = (permissionNames) => {
    if (!Array.isArray(permissionNames)) return false;
    
    // Admin has all permissions
    if (userRole === 'admin') return true;
    
    // Check if user has any of the specified permissions
    return permissionNames.some(permName => hasPermission(permName));
  };

  const canPerformAction = (module, action, resource = null) => {
    // Construct permission name
    const permissionName = resource 
      ? `${module}.${action}.${resource}`
      : `${module}.${action}`;
    
    return hasPermission(permissionName) || hasPermission(`${module}.all`);
  };

  // Get user's accessible modules for navigation
  const getAccessibleModules = () => {
    const moduleList = [
      { name: 'general', label: 'Dashboard', required: 'general.dashboard.read' },
      { name: 'finance', label: 'Finance', required: 'finance.dashboard.read' },
      { name: 'inventory', label: 'Inventory', required: 'inventory.dashboard.read' },
      { name: 'sales', label: 'Sales', required: 'sales.customers.read' },
      { name: 'procurement', label: 'Procurement', required: 'procurement.vendors.read' },
      { name: 'system', label: 'Admin', required: 'system.users.read' }
    ];

    return moduleList.filter(module => 
      hasModuleAccess(module.name) || hasPermission(module.required)
    );
  };

  // Get user's role-based capabilities
  const getUserCapabilities = () => {
    const capabilities = {
      canManageUsers: hasPermission('system.users.create'),
      canManageRoles: hasPermission('system.roles.manage'),
      canAccessFinance: hasModuleAccess('finance'),
      canAccessInventory: hasModuleAccess('inventory'),
      canAccessSales: hasModuleAccess('sales'),
      canAccessProcurement: hasModuleAccess('procurement'),
      canCreateJournalEntries: hasPermission('finance.journal.create'),
      canApproveTransactions: hasAnyPermission(['finance.payments.approve', 'procurement.po.approve']),
      canViewReports: hasAnyPermission(['finance.reports.read', 'inventory.reports.read']),
      canManageProducts: hasPermission('inventory.products.create'),
      canManageCustomers: hasPermission('sales.customers.create'),
      canManageVendors: hasPermission('procurement.vendors.create'),
      isAdmin: userRole === 'admin',
      isManager: userRole === 'manager',
      isAccountant: userRole === 'accountant'
    };

    return capabilities;
  };

  const value = {
    permissions,
    modules,
    userRole,
    loading,
    hasPermission,
    hasModuleAccess,
    hasAnyPermission,
    canPerformAction,
    getAccessibleModules,
    getUserCapabilities,
    refreshPermissions: loadUserPermissions
  };

  return (
    <PermissionsContext.Provider value={value}>
      {children}
    </PermissionsContext.Provider>
  );
};

export const usePermissions = () => {
  const context = useContext(PermissionsContext);
  if (!context) {
    throw new Error('usePermissions must be used within a PermissionsProvider');
  }
  return context;
};

// Higher-order component for permission-based rendering
export const withPermission = (permissionName, fallbackComponent = null) => {
  return (WrappedComponent) => {
    return (props) => {
      const { hasPermission, loading } = usePermissions();
      
      if (loading) {
        return <div>Loading...</div>;
      }
      
      if (!hasPermission(permissionName)) {
        return fallbackComponent || <div>Access Denied</div>;
      }
      
      return <WrappedComponent {...props} />;
    };
  };
};

// Component for conditional rendering based on permissions
export const PermissionGate = ({ 
  permission, 
  module, 
  anyPermissions, 
  fallback = null, 
  children 
}) => {
  const { hasPermission, hasModuleAccess, hasAnyPermission, loading } = usePermissions();
  
  if (loading) {
    return fallback;
  }
  
  let hasAccess = false;
  
  if (permission) {
    hasAccess = hasPermission(permission);
  } else if (module) {
    hasAccess = hasModuleAccess(module);
  } else if (anyPermissions && Array.isArray(anyPermissions)) {
    hasAccess = hasAnyPermission(anyPermissions);
  }
  
  return hasAccess ? children : fallback;
};

export default usePermissions;
