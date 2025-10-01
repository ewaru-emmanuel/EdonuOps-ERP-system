import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const TenantContext = createContext();

export const TenantProvider = ({ children }) => {
  const [currentTenant, setCurrentTenant] = useState(null);
  const [userTenants, setUserTenants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load user tenants on mount
  useEffect(() => {
    loadUserTenants();
  }, []);

  const loadUserTenants = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // For now, create a default tenant setup
      // In a real implementation, this would come from the API
      const defaultTenantData = {
        tenant_id: 'default_tenant',
        tenant_plan: 'enterprise',
        role: 'admin',
        is_default: true,
        user_id: 'user_1'
      };
      
      // Simple approach: If user is logged in, they have access to all modules
      // This matches the natural onboarding flow where users select what they want
      defaultTenantData.modules = [
        { module_name: 'finance', enabled: true },
        { module_name: 'inventory', enabled: true },
        { module_name: 'crm', enabled: true },
        { module_name: 'sales', enabled: true }
      ];
      
      setUserTenants([defaultTenantData]);

      // Set default tenant if none is selected
      if (!currentTenant) {
        setCurrentTenant(defaultTenantData);
        localStorage.setItem('currentTenant', JSON.stringify(defaultTenantData));
      }

    } catch (err) {
      console.error('Error loading user tenants:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [currentTenant]);

  const switchTenant = useCallback(async (tenantId) => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      // Switch tenant on backend
      const response = await fetch(`/api/tenant/switch-tenant/${tenantId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to switch tenant: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Find the tenant in userTenants
      const tenant = userTenants.find(t => t.tenant_id === tenantId);
      if (tenant) {
        setCurrentTenant(tenant);
        localStorage.setItem('currentTenant', JSON.stringify(tenant));
        console.log(`Switched to ${tenant.tenant_name}`);
      }

      return data;
    } catch (err) {
      console.error('Error switching tenant:', err);
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [userTenants]);

  const refreshTenants = useCallback(() => {
    loadUserTenants();
  }, [loadUserTenants]);

  const getTenantInfo = useCallback(async () => {
    if (!currentTenant) return null;

    try {
      const token = localStorage.getItem('token');
      if (!token) return null;

      const response = await fetch('/api/finance/tenant-info', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': currentTenant.tenant_id,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to load tenant info: ${response.statusText}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error loading tenant info:', err);
      return null;
    }
  }, [currentTenant]);

  const getTenantModules = useCallback(async () => {
    if (!currentTenant) return [];

    try {
      const token = localStorage.getItem('token');
      if (!token) return [];

      const response = await fetch('/api/finance/tenant-modules', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Tenant-ID': currentTenant.tenant_id,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to load tenant modules: ${response.statusText}`);
      }

      return await response.json();
    } catch (err) {
      console.error('Error loading tenant modules:', err);
      return [];
    }
  }, [currentTenant]);

  const hasModuleAccess = useCallback((moduleName) => {
    if (!currentTenant) return false;
    return currentTenant.modules?.some(module => 
      module.module_name === moduleName && module.enabled
    ) || false;
  }, [currentTenant]);

  const hasPermission = useCallback((permission) => {
    if (!currentTenant) return false;
    return currentTenant.permissions?.includes(permission) || false;
  }, [currentTenant]);

  const hasRole = useCallback((role) => {
    if (!currentTenant) return false;
    return currentTenant.role === role || currentTenant.role === 'admin';
  }, [currentTenant]);

  // Load current tenant from localStorage on mount
  useEffect(() => {
    const savedTenant = localStorage.getItem('currentTenant');
    if (savedTenant && !currentTenant) {
      try {
        const tenant = JSON.parse(savedTenant);
        setCurrentTenant(tenant);
      } catch (err) {
        console.error('Error parsing saved tenant:', err);
        localStorage.removeItem('currentTenant');
      }
    }
  }, [currentTenant]);

  const value = {
    // State
    currentTenant,
    userTenants,
    loading,
    error,
    
    // Actions
    switchTenant,
    refreshTenants,
    getTenantInfo,
    getTenantModules,
    
    // Helpers
    hasModuleAccess,
    hasPermission,
    hasRole,
    
    // Computed
    isMultiTenant: userTenants.length > 1,
    canSwitchTenants: userTenants.length > 1,
    currentTenantId: currentTenant?.tenant_id,
    currentTenantName: currentTenant?.tenant_name,
    currentTenantPlan: currentTenant?.tenant_plan,
    currentUserRole: currentTenant?.role
  };

  return (
    <TenantContext.Provider value={value}>
      {children}
    </TenantContext.Provider>
  );
};

export const useTenant = () => {
  const context = useContext(TenantContext);
  if (!context) {
    throw new Error('useTenant must be used within a TenantProvider');
  }
  return context;
};

// Higher-order component for tenant-aware components
export const withTenant = (WrappedComponent) => {
  return function TenantAwareComponent(props) {
    const tenant = useTenant();
    return <WrappedComponent {...props} tenant={tenant} />;
  };
};

// Hook for tenant-aware API calls
export const useTenantApi = () => {
  const { currentTenant } = useTenant();

  const apiCall = useCallback(async (endpoint, options = {}) => {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    if (!currentTenant) {
      throw new Error('No tenant selected');
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': currentTenant.tenant_id,
      'X-User-ID': currentTenant.user_id || 'user',
      ...options.headers
    };

    const response = await fetch(endpoint, {
      ...options,
      headers
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `API call failed: ${response.statusText}`);
    }

    return response.json();
  }, [currentTenant]);

  return { apiCall };
};
