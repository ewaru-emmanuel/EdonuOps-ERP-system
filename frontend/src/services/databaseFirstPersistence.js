/**
 * Database-First Data Persistence Service
 * All data is stored in the database, localStorage is only used for caching
 */

class DatabaseFirstPersistence {
  constructor() {
    this.cachePrefix = 'edonuops_cache_';
    this.cacheExpiry = 5 * 60 * 1000; // 5 minutes cache
  }

  /**
   * Save user data to database (primary storage)
   */
  async saveUserData(userId, dataType, data) {
    try {
      const { default: apiClient } = await import('./apiClient');
      
      const response = await apiClient.post('/api/user-data/save', {
        user_id: userId,
        data_type: dataType,
        data: data
      });
      
      if (response.data.success) {
        // Update cache
        this.updateCache(userId, dataType, data);
        console.log(`💾 Saved ${dataType} to database for user ${userId}`);
        return true;
      }
      return false;
    } catch (error) {
      console.error(`❌ Failed to save ${dataType} to database:`, error);
      return false;
    }
  }

  /**
   * Load user data from database (primary source)
   */
  async loadUserData(userId, dataType) {
    try {
      // Check cache first
      const cachedData = this.getFromCache(userId, dataType);
      if (cachedData) {
        console.log(`📂 Loaded ${dataType} from cache for user ${userId}`);
        return cachedData;
      }

      // Load from database
      const { default: apiClient } = await import('./apiClient');
      
      const response = await apiClient.get(`/api/user-data/load/${dataType}`, {
        params: { user_id: userId }
      });
      
      if (response.data.success && response.data.data) {
        // Update cache
        this.updateCache(userId, dataType, response.data.data);
        console.log(`📂 Loaded ${dataType} from database for user ${userId}`);
        return response.data.data;
      }
      
      return null;
    } catch (error) {
      console.error(`❌ Failed to load ${dataType} from database:`, error);
      return null;
    }
  }

  /**
   * Save user preferences to database
   */
  async saveUserPreferences(userId, preferences) {
    return await this.saveUserData(userId, 'preferences', preferences);
  }

  /**
   * Load user preferences from database
   */
  async loadUserPreferences(userId) {
    return await this.loadUserData(userId, 'preferences');
  }

  /**
   * Save user modules to database
   */
  async saveUserModules(userId, modules) {
    return await this.saveUserData(userId, 'modules', modules);
  }

  /**
   * Load user modules from database
   */
  async loadUserModules(userId) {
    return await this.loadUserData(userId, 'modules');
  }

  /**
   * Save finance data to database
   */
  async saveFinanceData(userId, dataType, data) {
    return await this.saveUserData(userId, `finance_${dataType}`, data);
  }

  /**
   * Load finance data from database
   */
  async loadFinanceData(userId, dataType) {
    return await this.loadUserData(userId, `finance_${dataType}`);
  }

  /**
   * Save CRM data to database
   */
  async saveCRMData(userId, dataType, data) {
    return await this.saveUserData(userId, `crm_${dataType}`, data);
  }

  /**
   * Load CRM data from database
   */
  async loadCRMData(userId, dataType) {
    return await this.loadUserData(userId, `crm_${dataType}`);
  }

  /**
   * Save inventory data to database
   */
  async saveInventoryData(userId, dataType, data) {
    return await this.saveUserData(userId, `inventory_${dataType}`, data);
  }

  /**
   * Load inventory data from database
   */
  async loadInventoryData(userId, dataType) {
    return await this.loadUserData(userId, `inventory_${dataType}`);
  }

  /**
   * Cache management
   */
  updateCache(userId, dataType, data) {
    const cacheKey = `${this.cachePrefix}${userId}_${dataType}`;
    const cacheData = {
      data,
      timestamp: Date.now(),
      expires: Date.now() + this.cacheExpiry
    };
    localStorage.setItem(cacheKey, JSON.stringify(cacheData));
  }

  getFromCache(userId, dataType) {
    const cacheKey = `${this.cachePrefix}${userId}_${dataType}`;
    try {
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const cacheData = JSON.parse(cached);
        if (Date.now() < cacheData.expires) {
          return cacheData.data;
        } else {
          localStorage.removeItem(cacheKey);
        }
      }
    } catch (error) {
      console.warn(`Cache error for ${dataType}:`, error);
    }
    return null;
  }

  /**
   * Clear cache for user
   */
  clearUserCache(userId) {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith(`${this.cachePrefix}${userId}_`)) {
        localStorage.removeItem(key);
      }
    });
    console.log(`🗑️ Cleared cache for user ${userId}`);
  }

  /**
   * Get all user data from database
   */
  async getAllUserData(userId) {
    try {
      const { default: apiClient } = await import('./apiClient');
      
      const response = await apiClient.get(`/api/user-data/all`, {
        params: { user_id: userId }
      });
      
      if (response.data.success) {
        return response.data.data;
      }
      return {};
    } catch (error) {
      console.error(`❌ Failed to load all user data:`, error);
      return {};
    }
  }

  /**
   * Export user data from database
   */
  async exportUserData(userId) {
    try {
      const { default: apiClient } = await import('./apiClient');
      
      const response = await apiClient.get(`/api/user-data/export`, {
        params: { user_id: userId }
      });
      
      if (response.data.success) {
        return response.data.data;
      }
      return null;
    } catch (error) {
      console.error(`❌ Failed to export user data:`, error);
      return null;
    }
  }

  /**
   * Import user data to database
   */
  async importUserData(userId, data) {
    try {
      const { default: apiClient } = await import('./apiClient');
      
      const response = await apiClient.post('/api/user-data/import', {
        user_id: userId,
        data: data
      });
      
      if (response.data.success) {
        // Clear cache to force reload
        this.clearUserCache(userId);
        console.log(`📥 Imported user data for user ${userId}`);
        return true;
      }
      return false;
    } catch (error) {
      console.error(`❌ Failed to import user data:`, error);
      return false;
    }
  }
}

// Create singleton instance
const databaseFirstPersistence = new DatabaseFirstPersistence();

export default databaseFirstPersistence;



