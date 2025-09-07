import { useState, useEffect } from 'react';
import { useVisitorSession } from './useVisitorSession';

export const useUserPreferences = () => {
  const [userPreferences, setUserPreferences] = useState(null);
  const [selectedModules, setSelectedModules] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { visitorId, getVisitorData, setVisitorData, isLoading: sessionLoading } = useVisitorSession();

  useEffect(() => {
    if (sessionLoading || !visitorId) return;
    try {
      const stored = getVisitorData('user_preferences');
      if (stored) {
        setUserPreferences(stored);
        let modules = stored.selectedModules || [];
        // Auto-enable procurement if financials is enabled but procurement is missing
        if (modules.includes('financials') && !modules.includes('procurement')) {
          modules = [...modules, 'procurement'];
          const updated = { ...stored, selectedModules: modules };
          setVisitorData('user_preferences', updated);
          setUserPreferences(updated);
        }
        setSelectedModules(modules);
      }
    } catch (error) {
      console.error('Error loading user preferences:', error);
    } finally {
      setIsLoading(false);
    }
    // Only re-run when session is ready or visitor changes
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visitorId, sessionLoading]);

  const updatePreferences = (newPreferences) => {
    try {
      const updated = { ...userPreferences, ...newPreferences };
      setVisitorData('user_preferences', updated);
      setUserPreferences(updated);
      setSelectedModules(updated.selectedModules || []);
    } catch (error) {
      console.error('Error updating user preferences:', error);
    }
  };

  const isModuleEnabled = (moduleId) => {
    return selectedModules.includes(moduleId);
  };

  const getEnabledModules = () => {
    return selectedModules;
  };

  const hasPreferences = () => {
    return userPreferences !== null;
  };

  return {
    userPreferences,
    selectedModules,
    isLoading,
    updatePreferences,
    isModuleEnabled,
    getEnabledModules,
    hasPreferences
  };
};
