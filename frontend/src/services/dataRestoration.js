/**
 * Data Restoration Service
 * Ensures all user data is properly restored after login
 */

import dataPersistence from './dataPersistence';

class DataRestorationService {
  constructor() {
    this.restorationCallbacks = new Map();
  }

  /**
   * Register a restoration callback for a specific data type
   */
  registerRestorationCallback(dataType, callback) {
    this.restorationCallbacks.set(dataType, callback);
    console.log(`📝 Registered restoration callback for: ${dataType}`);
  }

  /**
   * Restore all user data after login
   */
  async restoreUserData(userId) {
    try {
      console.log(`🔄 Starting data restoration for user ${userId}...`);
      
      // Get all user data keys
      const userDataKeys = dataPersistence.getUserDataKeys(userId);
      console.log(`📊 Found ${userDataKeys.length} data items to restore`);
      
      // Restore each data type
      const restorationPromises = [];
      
      userDataKeys.forEach(key => {
        const dataType = key.replace(`edonuops_user_${userId}_`, '');
        const data = dataPersistence.loadUserData(userId, dataType);
        
        if (data) {
          console.log(`📂 Restoring ${dataType}...`);
          
          // Call registered restoration callback if available
          const callback = this.restorationCallbacks.get(dataType);
          if (callback) {
            restorationPromises.push(
              callback(data).catch(error => {
                console.error(`❌ Failed to restore ${dataType}:`, error);
              })
            );
          } else {
            // Default restoration - put data back in localStorage
            this.defaultRestoration(dataType, data);
          }
        }
      });
      
      // Wait for all restorations to complete
      await Promise.all(restorationPromises);
      
      console.log(`✅ Data restoration completed for user ${userId}`);
      return true;
    } catch (error) {
      console.error(`❌ Data restoration failed for user ${userId}:`, error);
      return false;
    }
  }

  /**
   * Default restoration - put data back in localStorage
   */
  defaultRestoration(dataType, data) {
    try {
      const key = `edonuops_${dataType}`;
      localStorage.setItem(key, JSON.stringify(data));
      console.log(`📂 Restored ${dataType} to localStorage`);
    } catch (error) {
      console.error(`❌ Failed to restore ${dataType} to localStorage:`, error);
    }
  }

  /**
   * Restore user preferences
   */
  async restoreUserPreferences(userId) {
    const preferences = dataPersistence.loadUserPreferences(userId);
    if (preferences) {
      localStorage.setItem('edonuops_user_preferences', JSON.stringify(preferences));
      console.log('📋 User preferences restored');
      return preferences;
    }
    return null;
  }

  /**
   * Restore user modules
   */
  async restoreUserModules(userId) {
    const modules = dataPersistence.loadUserModules(userId);
    if (modules) {
      localStorage.setItem('edonuops_user_modules', JSON.stringify(modules));
      console.log('🔧 User modules restored');
      return modules;
    }
    return null;
  }

  /**
   * Restore finance data
   */
  async restoreFinanceData(userId) {
    const financeDataTypes = ['gl_entries', 'accounts', 'invoices', 'bills', 'customers', 'vendors'];
    const restoredData = {};
    
    for (const dataType of financeDataTypes) {
      const data = dataPersistence.loadFinanceData(userId, dataType);
      if (data) {
        restoredData[dataType] = data;
        localStorage.setItem(`edonuops_finance_${dataType}`, JSON.stringify(data));
        console.log(`💰 Restored finance ${dataType}`);
      }
    }
    
    return restoredData;
  }

  /**
   * Restore CRM data
   */
  async restoreCRMData(userId) {
    const crmDataTypes = ['contacts', 'leads', 'opportunities', 'companies', 'activities'];
    const restoredData = {};
    
    for (const dataType of crmDataTypes) {
      const data = dataPersistence.loadCRMData(userId, dataType);
      if (data) {
        restoredData[dataType] = data;
        localStorage.setItem(`edonuops_crm_${dataType}`, JSON.stringify(data));
        console.log(`👥 Restored CRM ${dataType}`);
      }
    }
    
    return restoredData;
  }

  /**
   * Restore inventory data
   */
  async restoreInventoryData(userId) {
    const inventoryDataTypes = ['products', 'categories', 'warehouses', 'stock_levels', 'transactions'];
    const restoredData = {};
    
    for (const dataType of inventoryDataTypes) {
      const data = dataPersistence.loadInventoryData(userId, dataType);
      if (data) {
        restoredData[dataType] = data;
        localStorage.setItem(`edonuops_inventory_${dataType}`, JSON.stringify(data));
        console.log(`📦 Restored inventory ${dataType}`);
      }
    }
    
    return restoredData;
  }

  /**
   * Restore dashboard data
   */
  async restoreDashboardData(userId) {
    const dashboardData = dataPersistence.loadUserData(userId, 'dashboard');
    if (dashboardData) {
      localStorage.setItem('edonuops_dashboard', JSON.stringify(dashboardData));
      console.log('📊 Dashboard data restored');
      return dashboardData;
    }
    return null;
  }

  /**
   * Restore settings data
   */
  async restoreSettingsData(userId) {
    const settingsData = dataPersistence.loadUserData(userId, 'settings');
    if (settingsData) {
      localStorage.setItem('edonuops_settings', JSON.stringify(settingsData));
      console.log('⚙️ Settings data restored');
      return settingsData;
    }
    return null;
  }

  /**
   * Get restoration status
   */
  getRestorationStatus(userId) {
    const userDataKeys = dataPersistence.getUserDataKeys(userId);
    const status = {
      totalItems: userDataKeys.length,
      restoredItems: 0,
      failedItems: 0,
      dataTypes: []
    };
    
    userDataKeys.forEach(key => {
      const dataType = key.replace(`edonuops_user_${userId}_`, '');
      status.dataTypes.push(dataType);
      
      try {
        const data = dataPersistence.loadUserData(userId, dataType);
        if (data) {
          status.restoredItems++;
        } else {
          status.failedItems++;
        }
      } catch (error) {
        status.failedItems++;
      }
    });
    
    return status;
  }

  /**
   * Clear all restoration callbacks
   */
  clearCallbacks() {
    this.restorationCallbacks.clear();
    console.log('🗑️ Cleared all restoration callbacks');
  }
}

// Create singleton instance
const dataRestoration = new DataRestorationService();

export default dataRestoration;



