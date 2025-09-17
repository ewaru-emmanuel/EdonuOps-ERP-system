/**
 * Real-time Data Service for EdonuOps
 * Handles API calls and provides real-time updates to the UI
 */

import { getERPApiService } from './erpApiService';

class RealTimeDataService {
  constructor() {
    this.subscribers = new Map();
    this.cache = new Map();
    this.pollingIntervals = new Map();
  }

  // Check if API service is ready
  isApiServiceReady() {
    const apiService = getERPApiService();
    return apiService && apiService.apiClient;
  }

  // Wait for API service to be ready
  async waitForApiService(maxRetries = 10, delay = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      if (this.isApiServiceReady()) {
        return true;
      }
      console.log(`Waiting for API service... (${i + 1}/${maxRetries})`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    console.error('API service not initialized after maximum retries');
    return false;
  }

  // Subscribe to data updates
  subscribe(endpoint, callback) {
    if (!this.subscribers.has(endpoint)) {
      this.subscribers.set(endpoint, new Set());
    }
    this.subscribers.get(endpoint).add(callback);
    
    // Return unsubscribe function
    return () => {
      const callbacks = this.subscribers.get(endpoint);
      if (callbacks) {
        callbacks.delete(callback);
        if (callbacks.size === 0) {
          this.subscribers.delete(endpoint);
          this.stopPolling(endpoint);
        }
      }
    };
  }

  // Notify all subscribers of data updates
  notifySubscribers(endpoint, data) {
    const callbacks = this.subscribers.get(endpoint);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('Error in subscriber callback:', error);
        }
      });
    }
  }

  // Start polling for updates
  startPolling(endpoint, interval = 5000) {
    if (this.pollingIntervals.has(endpoint)) {
      return; // Already polling
    }

    const poll = async () => {
      try {
        const data = await this.fetchData(endpoint);
        this.cache.set(endpoint, data);
        this.notifySubscribers(endpoint, data);
      } catch (error) {
        console.error(`Error polling ${endpoint}:`, error);
      }
    };

    // Initial fetch
    poll();
    
    // Set up interval
    const intervalId = setInterval(poll, interval);
    this.pollingIntervals.set(endpoint, intervalId);
  }

  // Stop polling
  stopPolling(endpoint) {
    const intervalId = this.pollingIntervals.get(endpoint);
    if (intervalId) {
      clearInterval(intervalId);
      this.pollingIntervals.delete(endpoint);
    }
  }

  // Fetch data from API
  async fetchData(endpoint) {
    try {
      // Wait for API service to be ready
      const isReady = await this.waitForApiService();
      if (!isReady) {
        throw new Error('API service not available');
      }
      
      const apiService = getERPApiService();
      const response = await apiService.get(endpoint);
      return response.data || response; // Handle both response formats
    } catch (error) {
      console.error(`Error fetching ${endpoint}:`, error);
      throw error;
    }
  }

  // Get cached data
  getCachedData(endpoint) {
    return this.cache.get(endpoint);
  }

  // Create new item
  async create(endpoint, data) {
    try {
      // Wait for API service to be ready
      const isReady = await this.waitForApiService();
      if (!isReady) {
        throw new Error('API service not available');
      }
      
      // Debug: Log the endpoint and data
      console.log('Creating item at endpoint:', endpoint);
      console.log('Data being sent:', data);
      
      const apiService = getERPApiService();
      const response = await apiService.post(endpoint, data);
      const responseData = response.data || response;
      
      // Update cache and notify subscribers
      const currentData = this.cache.get(endpoint) || [];
      const updatedData = Array.isArray(currentData) ? [...currentData, responseData] : responseData;
      this.cache.set(endpoint, updatedData);
      this.notifySubscribers(endpoint, updatedData);
      
      return responseData;
    } catch (error) {
      console.error(`Error creating ${endpoint}:`, error);
      throw error;
    }
  }

  // Update existing item
  async update(endpoint, id, data) {
    try {
      // Wait for API service to be ready
      const isReady = await this.waitForApiService();
      if (!isReady) {
        throw new Error('API service not available');
      }
      
      const apiService = getERPApiService();
      const response = await apiService.put(`${endpoint}/${id}`, data);
      const responseData = response.data || response;
      
      // Update cache and notify subscribers
      const currentData = this.cache.get(endpoint) || [];
      if (Array.isArray(currentData)) {
        const updatedData = currentData.map(item => 
          item.id === id ? { ...item, ...responseData } : item
        );
        this.cache.set(endpoint, updatedData);
        this.notifySubscribers(endpoint, updatedData);
      }
      
      return responseData;
    } catch (error) {
      console.error(`Error updating ${endpoint}:`, error);
      throw error;
    }
  }

  // Delete item
  async delete(endpoint, id) {
    try {
      // Wait for API service to be ready
      const isReady = await this.waitForApiService();
      if (!isReady) {
        throw new Error('API service not available');
      }
      
      const apiService = getERPApiService();
      await apiService.delete(`${endpoint}/${id}`);
      
      // Update cache and notify subscribers
      const currentData = this.cache.get(endpoint) || [];
      if (Array.isArray(currentData)) {
        const updatedData = currentData.filter(item => item.id !== id);
        this.cache.set(endpoint, updatedData);
        this.notifySubscribers(endpoint, updatedData);
      }
      
      return true;
    } catch (error) {
      console.error(`Error deleting ${endpoint}:`, error);
      throw error;
    }
  }

  // Load data and start polling
  async loadData(endpoint, startPolling = true) {
    try {
      // Wait for API service to be ready
      const isReady = await this.waitForApiService();
      if (!isReady) {
        throw new Error('API service not available');
      }
      
      const data = await this.fetchData(endpoint);
      this.cache.set(endpoint, data);
      
      if (startPolling) {
        this.startPolling(endpoint);
      }
      
      return data;
    } catch (error) {
      console.error(`Error loading ${endpoint}:`, error);
      throw error;
    }
  }

  // Clear cache for specific endpoint
  clearCache(endpoint) {
    this.cache.delete(endpoint);
  }

  // Clear all cache
  clearAllCache() {
    this.cache.clear();
  }

  // Get all active endpoints
  getActiveEndpoints() {
    return Array.from(this.subscribers.keys());
  }

  // Stop all polling
  stopAllPolling() {
    this.pollingIntervals.forEach((intervalId) => {
      clearInterval(intervalId);
    });
    this.pollingIntervals.clear();
  }

  // Cleanup
  cleanup() {
    this.stopAllPolling();
    this.subscribers.clear();
    this.cache.clear();
  }
}

// Create singleton instance
const realTimeDataService = new RealTimeDataService();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  realTimeDataService.cleanup();
});

export default realTimeDataService;
