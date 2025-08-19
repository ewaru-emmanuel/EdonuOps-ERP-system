// frontend/src/hooks/useModuleAccess.jsx

import { useAuth } from './useAuth';

export const useModuleAccess = () => {
  const { user } = useAuth();

  // This is a placeholder. In a real application, you would
  // fetch user roles and permissions from the server.
  const permissions = {
    admin: ['finance', 'inventory', 'crm', 'manufacturing', 'vendor_portal', 'hr', 'ai', 'reporting'],
    user: ['crm', 'inventory'],
    vendor: ['vendor_portal'],
  };

  const hasAccess = (moduleName) => {
    if (!user) return false;
    const userPermissions = permissions[user.role] || [];
    return userPermissions.includes(moduleName);
  };

  return { hasAccess };
};