/**
 * Data Persistence Service
 * Ensures user data is never lost during logout/login cycles
 */

class DataPersistenceService {
  constructor() {
    this.userDataPrefix = 'edonuops_user_';
    this.globalDataPrefix = 'edonuops_global_';
    this.sessionDataPrefix = 'edonuops_session_';
  }

  /**
   * Save user-specific data
   */
  saveUserData(userId, dataType, data) {
    try {
      const key = `${this.userDataPrefix}${userId}_${dataType}`;
      const dataWithTimestamp = {
        data,
        timestamp: new Date().toISOString(),
        version: '1.0'
      };
      localStorage.setItem(key, JSON.stringify(dataWithTimestamp));
      console.log(`💾 Saved user data: ${dataType} for user ${userId}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to save user data ${dataType}:`, error);
      return false;
    }
  }

  /**
   * Load user-specific data
   */
  loadUserData(userId, dataType) {
    try {
      const key = `${this.userDataPrefix}${userId}_${dataType}`;
      const saved = localStorage.getItem(key);
      if (saved) {
        const parsed = JSON.parse(saved);
        console.log(`📂 Loaded user data: ${dataType} for user ${userId}`);
        return parsed.data;
      }
      return null;
    } catch (error) {
      console.error(`❌ Failed to load user data ${dataType}:`, error);
      return null;
    }
  }

  /**
   * Save global data (not user-specific)
   */
  saveGlobalData(dataType, data) {
    try {
      const key = `${this.globalDataPrefix}${dataType}`;
      const dataWithTimestamp = {
        data,
        timestamp: new Date().toISOString(),
        version: '1.0'
      };
      localStorage.setItem(key, JSON.stringify(dataWithTimestamp));
      console.log(`💾 Saved global data: ${dataType}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to save global data ${dataType}:`, error);
      return false;
    }
  }

  /**
   * Load global data
   */
  loadGlobalData(dataType) {
    try {
      const key = `${this.globalDataPrefix}${dataType}`;
      const saved = localStorage.getItem(key);
      if (saved) {
        const parsed = JSON.parse(saved);
        console.log(`📂 Loaded global data: ${dataType}`);
        return parsed.data;
      }
      return null;
    } catch (error) {
      console.error(`❌ Failed to load global data ${dataType}:`, error);
      return null;
    }
  }

  /**
   * Save session data (temporary)
   */
  saveSessionData(dataType, data) {
    try {
      const key = `${this.sessionDataPrefix}${dataType}`;
      const dataWithTimestamp = {
        data,
        timestamp: new Date().toISOString(),
        expires: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
      };
      localStorage.setItem(key, JSON.stringify(dataWithTimestamp));
      console.log(`💾 Saved session data: ${dataType}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to save session data ${dataType}:`, error);
      return false;
    }
  }

  /**
   * Load session data
   */
  loadSessionData(dataType) {
    try {
      const key = `${this.sessionDataPrefix}${dataType}`;
      const saved = localStorage.getItem(key);
      if (saved) {
        const parsed = JSON.parse(saved);
        // Check if data has expired
        if (parsed.expires && Date.now() > parsed.expires) {
          localStorage.removeItem(key);
          console.log(`⏰ Session data expired: ${dataType}`);
          return null;
        }
        console.log(`📂 Loaded session data: ${dataType}`);
        return parsed.data;
      }
      return null;
    } catch (error) {
      console.error(`❌ Failed to load session data ${dataType}:`, error);
      return null;
    }
  }

  /**
   * Save user preferences
   */
  saveUserPreferences(userId, preferences) {
    return this.saveUserData(userId, 'preferences', preferences);
  }

  /**
   * Load user preferences
   */
  loadUserPreferences(userId) {
    return this.loadUserData(userId, 'preferences');
  }

  /**
   * Save user modules
   */
  saveUserModules(userId, modules) {
    return this.saveUserData(userId, 'modules', modules);
  }

  /**
   * Load user modules
   */
  loadUserModules(userId) {
    return this.loadUserData(userId, 'modules');
  }

  /**
   * Save finance data
   */
  saveFinanceData(userId, dataType, data) {
    return this.saveUserData(userId, `finance_${dataType}`, data);
  }

  /**
   * Load finance data
   */
  loadFinanceData(userId, dataType) {
    return this.loadUserData(userId, `finance_${dataType}`);
  }

  /**
   * Save CRM data
   */
  saveCRMData(userId, dataType, data) {
    return this.saveUserData(userId, `crm_${dataType}`, data);
  }

  /**
   * Load CRM data
   */
  loadCRMData(userId, dataType) {
    return this.loadUserData(userId, `crm_${dataType}`);
  }

  /**
   * Save inventory data
   */
  saveInventoryData(userId, dataType, data) {
    return this.saveUserData(userId, `inventory_${dataType}`, data);
  }

  /**
   * Load inventory data
   */
  loadInventoryData(userId, dataType) {
    return this.loadUserData(userId, `inventory_${dataType}`);
  }

  /**
   * Get all user data keys
   */
  getUserDataKeys(userId) {
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(`${this.userDataPrefix}${userId}_`)) {
        keys.push(key);
      }
    }
    return keys;
  }

  /**
   * Clear user data
   */
  clearUserData(userId) {
    const keys = this.getUserDataKeys(userId);
    keys.forEach(key => localStorage.removeItem(key));
    console.log(`🗑️ Cleared all data for user ${userId}`);
  }

  /**
   * Export user data
   */
  exportUserData(userId) {
    const keys = this.getUserDataKeys(userId);
    const exportData = {};
    
    keys.forEach(key => {
      const data = localStorage.getItem(key);
      if (data) {
        const dataType = key.replace(`${this.userDataPrefix}${userId}_`, '');
        exportData[dataType] = JSON.parse(data);
      }
    });
    
    return exportData;
  }

  /**
   * Import user data
   */
  importUserData(userId, data) {
    try {
      Object.keys(data).forEach(dataType => {
        this.saveUserData(userId, dataType, data[dataType].data);
      });
      console.log(`📥 Imported data for user ${userId}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to import data for user ${userId}:`, error);
      return false;
    }
  }

  /**
   * Backup all data
   */
  backupAllData() {
    const backup = {};
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && (key.startsWith(this.userDataPrefix) || key.startsWith(this.globalDataPrefix))) {
        backup[key] = localStorage.getItem(key);
      }
    }
    return backup;
  }

  /**
   * Restore from backup
   */
  restoreFromBackup(backup) {
    try {
      Object.keys(backup).forEach(key => {
        localStorage.setItem(key, backup[key]);
      });
      console.log(`📥 Restored data from backup`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to restore from backup:`, error);
      return false;
    }
  }
}

// Create singleton instance
const dataPersistence = new DataPersistenceService();

export default dataPersistence;



