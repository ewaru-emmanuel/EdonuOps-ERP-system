import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

export const useUserPreferences = () => {
  const [userPreferences, setUserPreferences] = useState(null);
  const [selectedModules, setSelectedModules] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const { isAuthenticated, user } = useAuth();

  // Load preferences from backend
  const loadUserPreferences = useCallback(async () => {
    if (!isAuthenticated || !user) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Import apiClient dynamically to avoid circular imports
      const { default: apiClient } = await import('../services/apiClient');
      
      console.log('🔄 Loading user modules from backend...');
      
      // Check user context from individual localStorage items (database-first approach)
      const userId = localStorage.getItem('userId');
      const userEmail = localStorage.getItem('userEmail');
      console.log('👤 User context:', {
        hasUserId: !!userId,
        hasEmail: !!userEmail,
        userId: userId,
        userEmail: userEmail
      });
      
      // Get user modules from backend
      console.log('🌐 Making API call to /api/dashboard/modules/user');
      const response = await apiClient.get('/api/dashboard/modules/user');
      console.log('🌐 API Response:', {
        response,
        isArray: Array.isArray(response),
        dataType: typeof response,
        length: Array.isArray(response) ? response.length : 0
      });
      // apiClient.get() returns the JSON directly, not wrapped in {data: ...}
      const userModules = Array.isArray(response) ? response : [];
      
      console.log('📊 Backend response:', {
        status: response.status,
        dataLength: userModules.length,
        modules: userModules.map(m => ({ id: m.id, name: m.name, active: m.is_active }))
      });
      
      // Extract module IDs
      const moduleIds = userModules.map(module => module.id);
      
      const preferences = {
        selected_modules: moduleIds,
        modules: userModules
      };
      
      console.log('🔧 Loading preferences from backend:', preferences);
      setUserPreferences(preferences);
      setSelectedModules(moduleIds);
      setIsLoading(false);
      
      // If no modules found, show warning
      if (moduleIds.length === 0) {
        console.warn('⚠️ No modules found for user. User may need to activate modules.');
        console.log('💡 Suggestion: Go to /onboarding to activate modules');
      }
      
    } catch (error) {
      console.error('❌ Error loading preferences from backend:', error);
      
      // Fallback to localStorage if backend fails
      try {
        const savedPreferences = localStorage.getItem('edonuops_user_preferences');
        if (savedPreferences) {
          const preferences = JSON.parse(savedPreferences);
          console.log('🔧 Fallback: Loading preferences from localStorage:', preferences);
          setUserPreferences(preferences);
          setSelectedModules(preferences.selected_modules || []);
          setIsLoading(false);
          return;
        }
      } catch (localError) {
        console.error('Error loading from localStorage fallback:', localError);
      }
      
      // Final fallback to defaults
      const defaultPreferences = {
        selected_modules: ['finance', 'crm', 'inventory', 'procurement']
      };
      
      console.log('🔧 Using default preferences:', defaultPreferences);
      setUserPreferences(defaultPreferences);
      setSelectedModules(defaultPreferences.selected_modules);
      setIsLoading(false);
    }
  }, [isAuthenticated, user]);

  // Load preferences when user changes
  useEffect(() => {
    loadUserPreferences();
  }, [loadUserPreferences]);

  // Listen for user data restoration events
  useEffect(() => {
    const handleUserDataRestored = () => {
      console.log('🔄 User data restored, reloading preferences...');
      loadUserPreferences();
    };

    const handleReloadPreferences = () => {
      console.log('🔄 Reloading user preferences...');
      loadUserPreferences();
    };

    // Listen for data restoration events
    window.addEventListener('userDataRestored', handleUserDataRestored);
    window.addEventListener('reloadUserPreferences', handleReloadPreferences);

    return () => {
      window.removeEventListener('userDataRestored', handleUserDataRestored);
      window.removeEventListener('reloadUserPreferences', handleReloadPreferences);
    };
  }, [loadUserPreferences]);

  // Check if user has preferences
  const hasPreferences = userPreferences !== null || selectedModules.length > 0;

  // Check if a module is enabled
  const isModuleEnabled = (moduleId) => {
    return selectedModules.includes(moduleId);
  };

  // Update preferences
  const updatePreferences = async (newPreferences) => {
    try {
      setUserPreferences(newPreferences);
      if (newPreferences.selected_modules) {
        setSelectedModules(newPreferences.selected_modules);
      }
      return { success: true };
    } catch (error) {
      setError(error.message);
      return { success: false, error: error.message };
    }
  };

  // Activate a module
  const activateModule = async (moduleId, permissions = null) => {
    try {
      const { default: apiClient } = await import('../services/apiClient');
      
      const response = await apiClient.post('/api/dashboard/modules/activate', {
        module_id: moduleId,
        permissions: permissions
      });
      
      if (response.data) {
        // Reload preferences to get updated modules
        await loadUserPreferences();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error activating module:', error);
      setError(error.message);
      return false;
    }
  };

  // Deactivate a module
  const deactivateModule = async (moduleId) => {
    try {
      const { default: apiClient } = await import('../services/apiClient');
      
      const response = await apiClient.post('/api/dashboard/modules/deactivate', {
        module_id: moduleId
      });
      
      if (response.data) {
        // Reload preferences to get updated modules
        await loadUserPreferences();
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error deactivating module:', error);
      setError(error.message);
      return false;
    }
  };

  // Bulk activate modules
  const bulkActivateModules = async (moduleIds, permissions = {}) => {
    try {
      const { default: apiClient } = await import('../services/apiClient');
      
      const response = await apiClient.post('/api/dashboard/modules/bulk-activate', {
        module_ids: moduleIds,
        permissions: permissions
      });
      
      if (response.data) {
        // Reload preferences to get updated modules
        await loadUserPreferences();
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('Error bulk activating modules:', error);
      setError(error.message);
      return null;
    }
  };

  return {
    userPreferences,
    selectedModules,
    isLoading,
    error,
    hasPreferences,
    isModuleEnabled,
    updatePreferences,
    activateModule,
    deactivateModule,
    bulkActivateModules
  };
};