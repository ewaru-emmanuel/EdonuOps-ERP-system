/**
 * Data Backup and Recovery Service
 * Provides comprehensive backup and recovery for user data
 */

import dataPersistence from './dataPersistence';

class DataBackupService {
  constructor() {
    this.backupPrefix = 'edonuops_backup_';
    this.maxBackups = 5; // Keep last 5 backups
  }

  /**
   * Create a complete backup of user data
   */
  async createUserBackup(userId) {
    try {
      console.log(`💾 Creating backup for user ${userId}...`);
      
      const backup = {
        userId,
        timestamp: new Date().toISOString(),
        version: '1.0',
        data: {}
      };
      
      // Get all user data keys
      const userDataKeys = dataPersistence.getUserDataKeys(userId);
      
      // Backup each data type
      for (const key of userDataKeys) {
        const dataType = key.replace(`edonuops_user_${userId}_`, '');
        const data = dataPersistence.loadUserData(userId, dataType);
        if (data) {
          backup.data[dataType] = data;
        }
      }
      
      // Save backup
      const backupKey = `${this.backupPrefix}${userId}_${Date.now()}`;
      localStorage.setItem(backupKey, JSON.stringify(backup));
      
      // Clean up old backups
      this.cleanupOldBackups(userId);
      
      console.log(`✅ Backup created: ${backupKey}`);
      return backupKey;
    } catch (error) {
      console.error(`❌ Failed to create backup for user ${userId}:`, error);
      return null;
    }
  }

  /**
   * Restore user data from backup
   */
  async restoreUserBackup(userId, backupKey) {
    try {
      console.log(`📥 Restoring backup ${backupKey} for user ${userId}...`);
      
      const backupData = localStorage.getItem(backupKey);
      if (!backupData) {
        throw new Error('Backup not found');
      }
      
      const backup = JSON.parse(backupData);
      
      // Restore each data type
      for (const [dataType, data] of Object.entries(backup.data)) {
        dataPersistence.saveUserData(userId, dataType, data);
        console.log(`📂 Restored ${dataType}`);
      }
      
      console.log(`✅ Backup restored successfully`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to restore backup:`, error);
      return false;
    }
  }

  /**
   * Get all backups for a user
   */
  getUserBackups(userId) {
    const backups = [];
    const prefix = `${this.backupPrefix}${userId}_`;
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(prefix)) {
        try {
          const backupData = localStorage.getItem(key);
          const backup = JSON.parse(backupData);
          backups.push({
            key,
            timestamp: backup.timestamp,
            dataTypes: Object.keys(backup.data),
            size: JSON.stringify(backup).length
          });
        } catch (error) {
          console.warn(`Invalid backup data for key ${key}`);
        }
      }
    }
    
    // Sort by timestamp (newest first)
    return backups.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  }

  /**
   * Clean up old backups
   */
  cleanupOldBackups(userId) {
    const backups = this.getUserBackups(userId);
    
    if (backups.length > this.maxBackups) {
      const backupsToDelete = backups.slice(this.maxBackups);
      
      backupsToDelete.forEach(backup => {
        localStorage.removeItem(backup.key);
        console.log(`🗑️ Deleted old backup: ${backup.key}`);
      });
    }
  }

  /**
   * Export user data
   */
  exportUserData(userId) {
    try {
      const exportData = {
        userId,
        timestamp: new Date().toISOString(),
        version: '1.0',
        data: dataPersistence.exportUserData(userId)
      };
      
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `edonuops_user_${userId}_backup_${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      console.log(`📤 User data exported for user ${userId}`);
      return true;
    } catch (error) {
      console.error(`❌ Failed to export user data:`, error);
      return false;
    }
  }

  /**
   * Import user data from file
   */
  async importUserData(userId, file) {
    try {
      const text = await file.text();
      const importData = JSON.parse(text);
      
      if (importData.userId !== userId) {
        throw new Error('User ID mismatch');
      }
      
      // Import the data
      const success = dataPersistence.importUserData(userId, importData.data);
      
      if (success) {
        console.log(`📥 User data imported for user ${userId}`);
        return true;
      } else {
        throw new Error('Import failed');
      }
    } catch (error) {
      console.error(`❌ Failed to import user data:`, error);
      return false;
    }
  }

  /**
   * Get backup statistics
   */
  getBackupStats(userId) {
    const backups = this.getUserBackups(userId);
    const totalSize = backups.reduce((sum, backup) => sum + backup.size, 0);
    
    return {
      totalBackups: backups.length,
      totalSize,
      oldestBackup: backups.length > 0 ? backups[backups.length - 1].timestamp : null,
      newestBackup: backups.length > 0 ? backups[0].timestamp : null
    };
  }

  /**
   * Auto-backup before critical operations
   */
  async autoBackup(userId) {
    try {
      const backupKey = await this.createUserBackup(userId);
      if (backupKey) {
        console.log(`🔄 Auto-backup created: ${backupKey}`);
        return backupKey;
      }
      return null;
    } catch (error) {
      console.error('Auto-backup failed:', error);
      return null;
    }
  }

  /**
   * Restore from most recent backup
   */
  async restoreLatestBackup(userId) {
    const backups = this.getUserBackups(userId);
    
    if (backups.length === 0) {
      console.warn('No backups found for user');
      return false;
    }
    
    const latestBackup = backups[0];
    return await this.restoreUserBackup(userId, latestBackup.key);
  }
}

// Create singleton instance
const dataBackup = new DataBackupService();

export default dataBackup;



