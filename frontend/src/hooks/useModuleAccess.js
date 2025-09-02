// frontend/src/hooks/useModuleAccess.js

import { useUserPreferences } from './useUserPreferences';

export const useModuleAccess = () => {
  const { isModuleEnabled, hasPreferences } = useUserPreferences();

  const canAccessModule = (moduleId) => {
    if (!hasPreferences) return true; // Allow access if no preferences set
    return isModuleEnabled(moduleId);
  };

  const requireModule = (moduleId) => {
    if (!canAccessModule(moduleId)) {
      throw new Error(`Module ${moduleId} is not enabled for this user`);
    }
  };

  const getModuleStatus = (moduleId) => {
    return {
      enabled: canAccessModule(moduleId),
      hasPreferences,
      moduleId
    };
  };

  return {
    canAccessModule,
    requireModule,
    isModuleEnabled,
    hasPreferences,
    getModuleStatus
  };
};