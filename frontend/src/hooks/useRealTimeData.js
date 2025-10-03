import { useState, useEffect, useCallback, useRef } from 'react';
import realTimeDataService from '../services/realTimeDataService';
import apiClient from '../services/apiClient';
import { useAuth } from '../context/AuthContext';

/**
 * Custom hook for real-time data management
 * @param {string} endpoint - API endpoint to fetch data from
 * @param {boolean} autoPoll - Whether to automatically poll for updates
 * @param {number} pollInterval - Polling interval in milliseconds
 * @returns {Object} - Data, loading state, error state, and CRUD functions
 */
export const useRealTimeData = (endpoint, autoPoll = true, pollInterval = 5000) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { isAuthenticated, loading: authLoading } = useAuth();
  
  // Use refs to avoid dependency issues
  const authRef = useRef({ isAuthenticated, authLoading });
  authRef.current = { isAuthenticated, authLoading };

  // Load initial data
  const loadData = useCallback(async () => {
    // Don't load data if not authenticated or still checking auth
    if (authRef.current.authLoading || !authRef.current.isAuthenticated) {
      console.log(`Skipping data load - authLoading: ${authRef.current.authLoading}, isAuthenticated: ${authRef.current.isAuthenticated}`);
      setLoading(false);
      setError(null);
      setData([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Use apiClient directly instead of waiting for ERP API service
      console.log(`Loading data from endpoint: ${endpoint}`);
      console.log(`Auth status - loading: ${authRef.current.authLoading}, authenticated: ${authRef.current.isAuthenticated}`);
      
      const result = await apiClient.get(endpoint);
      console.log(`Raw API response for ${endpoint}:`, result);
      
      // Handle different response structures
      let processedData;
      if (Array.isArray(result)) {
        processedData = result;
      } else if (result && typeof result === 'object') {
        // For object responses, return the object directly
        processedData = result;
      } else {
        processedData = [result];
      }
      
      console.log(`Processed data for ${endpoint}:`, processedData);
      setData(processedData);
    } catch (err) {
      setError(err.message || 'Failed to load data');
      console.error(`Error loading ${endpoint}:`, err);
    } finally {
      console.log(`Setting loading to false for ${endpoint}`);
      setLoading(false);
    }
  }, [endpoint]); // Only depend on endpoint

  // Subscribe to real-time updates and load data
  useEffect(() => {
    console.log(`useRealTimeData useEffect triggered for ${endpoint} - authLoading: ${authLoading}, isAuthenticated: ${isAuthenticated}`);
    
    // Don't do anything if auth is still loading
    if (authLoading) {
      console.log(`Auth still loading for ${endpoint}, skipping data load`);
      return;
    }

    // If not authenticated, clear data and return
    if (!isAuthenticated) {
      console.log(`Not authenticated for ${endpoint}, clearing data`);
      setLoading(false);
      setError(null);
      setData([]);
      return;
    }

    console.log(`Authenticated, proceeding with data load for ${endpoint}`);

    // Only proceed if authenticated
    const unsubscribe = realTimeDataService.subscribe(endpoint, (updatedData) => {
      setData(Array.isArray(updatedData) ? updatedData : [updatedData]);
      setError(null);
    });

    // Load initial data
    loadData();

    // Cleanup subscription on unmount
    return () => {
      unsubscribe();
    };
  }, [endpoint, loadData, authLoading, isAuthenticated]); // Add authLoading and isAuthenticated to dependencies

  // CRUD operations
  const create = useCallback(async (newData) => {
    try {
      setError(null);
      
      // Try realTimeDataService first
      try {
        const result = await realTimeDataService.create(endpoint, newData);
        return result;
      } catch (realtimeError) {
        console.warn('RealTimeDataService failed, trying direct API call:', realtimeError);
        
        // Fallback: Use apiClient directly
        console.log('Fallback: Making direct API call to:', endpoint);
        console.log('Fallback: Data being sent:', newData);
        const apiClient = await import('../services/apiClient');
        const response = await apiClient.default.post(endpoint, newData);
        console.log('Fallback: API response:', response);
        return response.data || response;
      }
    } catch (err) {
      setError(err.message || 'Failed to create item');
      throw err;
    }
  }, [endpoint]);

  const update = useCallback(async (id, updatedData) => {
    try {
      setError(null);
      
      // Try realTimeDataService first
      try {
        const result = await realTimeDataService.update(endpoint, id, updatedData);
        return result;
      } catch (realtimeError) {
        console.warn('RealTimeDataService failed, trying direct API call:', realtimeError);
        
        // Fallback: Use apiClient directly
        const apiClient = await import('../services/apiClient');
        const response = await apiClient.default.put(`${endpoint}/${id}`, updatedData);
        return response.data || response;
      }
    } catch (err) {
      setError(err.message || 'Failed to update item');
      throw err;
    }
  }, [endpoint]);

  const remove = useCallback(async (id) => {
    try {
      setError(null);
      
      // Try realTimeDataService first
      try {
        await realTimeDataService.delete(endpoint, id);
        return true;
      } catch (realtimeError) {
        console.warn('RealTimeDataService failed, trying direct API call:', realtimeError);
        
        // Fallback: Use apiClient directly
        const apiClient = await import('../services/apiClient');
        await apiClient.default.delete(`${endpoint}/${id}`);
        return true;
      }
    } catch (err) {
      setError(err.message || 'Failed to delete item');
      throw err;
    }
  }, [endpoint]);

  const refresh = useCallback(() => {
    loadData();
  }, [loadData]);

  return {
    data,
    loading,
    error,
    create,
    update,
    remove,
    refresh,
    setData
  };
};

/**
 * Custom hook for single item real-time data
 * @param {string} endpoint - API endpoint
 * @param {string|number} id - Item ID
 * @returns {Object} - Item data, loading state, error state, and update function
 */
export const useRealTimeItem = (endpoint, id) => {
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadItem = useCallback(async () => {
    if (!id) {
      setItem(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await realTimeDataService.fetchData(`${endpoint}/${id}`);
      setItem(result);
    } catch (err) {
      setError(err.message || 'Failed to load item');
      console.error(`Error loading ${endpoint}/${id}:`, err);
    } finally {
      setLoading(false);
    }
  }, [endpoint, id]);

  useEffect(() => {
    loadItem();
  }, [loadItem]);

  const updateItem = useCallback(async (updatedData) => {
    try {
      setError(null);
      const result = await realTimeDataService.update(endpoint, id, updatedData);
      setItem(result);
      return result;
    } catch (err) {
      setError(err.message || 'Failed to update item');
      throw err;
    }
  }, [endpoint, id]);

  return {
    item,
    loading,
    error,
    update: updateItem,
    refresh: loadItem
  };
};

/**
 * Custom hook for real-time data with filtering and pagination
 * @param {string} endpoint - API endpoint
 * @param {Object} filters - Filter parameters
 * @param {Object} pagination - Pagination parameters
 * @returns {Object} - Filtered data, loading state, error state, and filter functions
 */
export const useRealTimeDataWithFilters = (endpoint, initialFilters = {}, initialPagination = {}) => {
  const [filters, setFilters] = useState(initialFilters);
  const [pagination, setPagination] = useState(initialPagination);
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { data, loading: dataLoading, error: dataError } = useRealTimeData(endpoint);

  // Apply filters and pagination
  useEffect(() => {
    if (!data) return;

    try {
      let filtered = [...data];

      // Apply filters
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          filtered = filtered.filter(item => {
            const itemValue = item[key];
            if (typeof value === 'string') {
              return itemValue?.toLowerCase().includes(value.toLowerCase());
            }
            return itemValue === value;
          });
        }
      });

      // Apply pagination
      if (pagination.page && pagination.pageSize) {
        const startIndex = (pagination.page - 1) * pagination.pageSize;
        const endIndex = startIndex + pagination.pageSize;
        filtered = filtered.slice(startIndex, endIndex);
      }

      setFilteredData(filtered);
    } catch (err) {
      setError('Error applying filters');
    }
  }, [data, filters, pagination]);

  // Update loading and error states
  useEffect(() => {
    setLoading(dataLoading);
    setError(dataError);
  }, [dataLoading, dataError]);

  const updateFilters = useCallback((newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setPagination(prev => ({ ...prev, page: 1 })); // Reset to first page
  }, []);

  const updatePagination = useCallback((newPagination) => {
    setPagination(prev => ({ ...prev, ...newPagination }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters(initialFilters);
    setPagination(initialPagination);
  }, [initialFilters, initialPagination]);

  return {
    data: filteredData,
    loading,
    error,
    filters,
    pagination,
    updateFilters,
    updatePagination,
    clearFilters,
    totalCount: data?.length || 0
  };
};

export default useRealTimeData;
