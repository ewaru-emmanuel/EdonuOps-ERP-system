import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';

// Global cache to prevent multiple simultaneous API calls
let globalCache = {
  data: null,
  loading: false,
  promise: null,
  timestamp: 0,
  CACHE_DURATION: 30000 // 30 seconds
};

export const useUserPreferences = () => {
  const [userPreferences, setUserPreferences] = useState(null);
  const [selectedModules, setSelectedModules] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const { isAuthenticated, user } = useAuth();

  // Load preferences from backend with proper state management
  const loadUserPreferences = useCallback(async (forceRefresh = false) => {
    if (!isAuthenticated || !user) {
      setIsLoading(false);
      return;
    }

    // Check global cache first
    const now = Date.now();
    if (!forceRefresh && globalCache.data && (now - globalCache.timestamp) < globalCache.CACHE_DURATION) {
      console.log('📦 Using cached user preferences');
      setSelectedModules(globalCache.data.selectedModules || []);
      return;
    }

    // Prevent multiple simultaneous calls globally
    if (globalCache.loading) {
      console.log('🔄 Global loading in progress, waiting...');
      if (globalCache.promise) {
        try {
          const result = await globalCache.promise;
          setSelectedModules(result.selectedModules || []);
        } catch (error) {
          console.error('Error waiting for global cache:', error);
        }
      }
      return;
    }

    // Set global loading state
    globalCache.loading = true;
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
      
      // No caching - always fetch fresh data from database
      console.log('🔄 Fetching fresh data from database...');
      
      // Get user modules from backend
      console.log('🌐 Making API call to /api/dashboard/modules/user');
      const apiPromise = apiClient.get('/api/dashboard/modules/user');
      globalCache.promise = apiPromise;
      const response = await apiPromise;
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
        modules: userModules,
        lastUpdated: Date.now(),
        source: 'backend'
      };
      
      // No caching - data is always fresh from database
      
      console.log('🔧 Loading preferences from backend:', preferences);
      console.log('🎯 Setting selectedModules to:', moduleIds);
      setUserPreferences(preferences);
      setSelectedModules(moduleIds);
      setIsLoading(false);
      
      // Update global cache
      globalCache.data = { selectedModules: moduleIds };
      globalCache.timestamp = Date.now();
      globalCache.loading = false;
      globalCache.promise = null;
      
      // If no modules found, show warning and clear any stale cache
      if (moduleIds.length === 0) {
        console.warn('⚠️ No modules found for user. User may need to activate modules.');
        console.log('💡 Suggestion: Go to /onboarding to activate modules');
        
        // No localStorage cache to clear
      }
      
    } catch (error) {
      console.error('❌ Error loading preferences from backend:', error);
      
      // No fallbacks - strictly database-driven
      console.log('🔧 No modules found in database - user needs to complete onboarding');
      setUserPreferences({ selected_modules: [], source: 'database_empty' });
      setSelectedModules([]);
      setError(error);
      setIsLoading(false);
      
      // Update global cache
      globalCache.data = { selectedModules: [] };
      globalCache.timestamp = Date.now();
      globalCache.loading = false;
      globalCache.promise = null;
    }
  }, [isAuthenticated, user, isLoading]);

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

  // Force refresh preferences (cache invalidation)
  const refreshPreferences = useCallback(() => {
    console.log('🔄 Force refreshing user preferences...');
    loadUserPreferences(true);
  }, [loadUserPreferences]);

  // No cache to clear - always fresh from database
  const clearCache = useCallback(() => {
    console.log('🗑️ No cache to clear - data is always fresh from database');
  }, []);

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
    bulkActivateModules,
    refreshPreferences,
    clearCache
  };
};