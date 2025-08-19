import { useState, useEffect, useCallback } from 'react';
import { useERPApi } from '../services/erpApiService';

// Custom hook for managing API data with loading states and error handling
export const useApiData = (apiMethod, dependencies = [], options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  
  const {
    autoRefresh = false,
    refreshInterval = 30000, // 30 seconds
    maxRetries = 3,
    retryDelay = 1000, // 1 second
    onSuccess,
    onError
  } = options;

  const erpApi = useERPApi();

  const fetchData = useCallback(async (isRetry = false) => {
    if (!isRetry) {
      setLoading(true);
      setError(null);
    }

    try {
      console.log(`🔄 Fetching data with method: ${apiMethod.name}`);
      
      const result = await apiMethod.call(erpApi, ...dependencies);
      
      console.log(`✅ Data fetched successfully:`, result);
      
      setData(result);
      setError(null);
      setRetryCount(0);
      
      if (onSuccess) {
        onSuccess(result);
      }
      
    } catch (err) {
      console.error(`❌ Error fetching data:`, err);
      
      const currentRetryCount = isRetry ? retryCount + 1 : 0;
      
      if (currentRetryCount < maxRetries) {
        console.log(`🔄 Retrying... Attempt ${currentRetryCount + 1}/${maxRetries}`);
        setRetryCount(currentRetryCount);
        
        setTimeout(() => {
          fetchData(true);
        }, retryDelay * (currentRetryCount + 1));
        
        return;
      }
      
      setError(err.message || 'An error occurred while fetching data');
      setLoading(false);
      
      if (onError) {
        onError(err);
      }
    } finally {
      if (!isRetry || retryCount >= maxRetries) {
        setLoading(false);
      }
    }
  }, [apiMethod, erpApi, ...dependencies, retryCount, maxRetries, retryDelay, onSuccess, onError]); // eslint-disable-line react-hooks/exhaustive-deps

  // Initial data fetch
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      console.log(`🔄 Auto-refreshing data...`);
      fetchData();
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchData]); // eslint-disable-line react-hooks/exhaustive-deps

  // Manual refresh function
  const refresh = useCallback(() => {
    console.log(`🔄 Manual refresh triggered`);
    fetchData();
  }, [fetchData]); // eslint-disable-line react-hooks/exhaustive-deps

  // Retry function
  const retry = useCallback(() => {
    console.log(`🔄 Manual retry triggered`);
    setRetryCount(0);
    fetchData();
  }, [fetchData]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    data,
    loading,
    error,
    retryCount,
    refresh,
    retry,
    setData // Allow manual data updates
  };
};

// Hook for CRUD operations
export const useApiCRUD = (apiMethods, dependencies = []) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const erpApi = useERPApi();

  const executeOperation = useCallback(async (operation, ...args) => {
    setLoading(true);
    setError(null);

    try {
      console.log(`🔄 Executing ${operation.name} operation`);
      
      const result = await operation.call(erpApi, ...args);
      
      console.log(`✅ ${operation.name} operation successful:`, result);
      
      return result;
      
    } catch (err) {
      console.error(`❌ ${operation.name} operation failed:`, err);
      setError(err.message || `An error occurred during ${operation.name}`);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [erpApi]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    loading,
    error,
    executeOperation,
    setError
  };
};

// Hook for real-time data with WebSocket support
export const useRealtimeData = (apiMethod, dependencies = [], wsEndpoint = null) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  
  const erpApi = useERPApi();

  // Initial data fetch
  useEffect(() => {
    const fetchInitialData = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await apiMethod.call(erpApi, ...dependencies);
        setData(result);
      } catch (err) {
        setError(err.message || 'An error occurred while fetching data');
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, [apiMethod, erpApi, ...dependencies]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!wsEndpoint) return;

    const ws = new WebSocket(`ws://127.0.0.1:5000/ws/${wsEndpoint}`);
    
    ws.onopen = () => {
      console.log(`🔌 WebSocket connected to ${wsEndpoint}`);
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const update = JSON.parse(event.data);
        console.log(`📡 WebSocket update received:`, update);
        
        // Update data based on the WebSocket message
        setData(prevData => {
          if (update.type === 'CREATE') {
            return [...(prevData || []), update.data];
          } else if (update.type === 'UPDATE') {
            return (prevData || []).map(item => 
              item.id === update.data.id ? update.data : item
            );
          } else if (update.type === 'DELETE') {
            return (prevData || []).filter(item => item.id !== update.data.id);
          } else if (update.type === 'REFRESH') {
            return update.data;
          }
          return prevData;
        });
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error(`❌ WebSocket error:`, error);
      setWsConnected(false);
    };

    ws.onclose = () => {
      console.log(`🔌 WebSocket disconnected from ${wsEndpoint}`);
      setWsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [wsEndpoint]);

  return {
    data,
    loading,
    error,
    wsConnected,
    setData
  };
};

// Hook for paginated data
export const usePaginatedData = (apiMethod, pageSize = 10, dependencies = []) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  
  const erpApi = useERPApi();

  const fetchPage = useCallback(async (pageNum = 1, append = false) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiMethod.call(erpApi, pageNum, pageSize, ...dependencies);
      
      if (append) {
        setData(prev => [...prev, ...(result.data || result)]);
      } else {
        setData(result.data || result);
      }
      
      setTotalCount(result.total || result.length || 0);
      setHasMore((result.data || result).length === pageSize);
      
    } catch (err) {
      setError(err.message || 'An error occurred while fetching data');
    } finally {
      setLoading(false);
    }
  }, [apiMethod, erpApi, pageSize, ...dependencies]);

  // Initial data fetch
  useEffect(() => {
    fetchPage(1, false);
  }, [fetchPage]);

  // Load next page
  const loadNextPage = useCallback(() => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchPage(nextPage, true);
    }
  }, [loading, hasMore, page, fetchPage]);

  // Refresh data
  const refresh = useCallback(() => {
    setPage(1);
    fetchPage(1, false);
  }, [fetchPage]);

  return {
    data,
    loading,
    error,
    page,
    hasMore,
    totalCount,
    loadNextPage,
    refresh,
    setData
  };
};

// Hook for search and filtering
export const useSearchableData = (apiMethod, dependencies = []) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({});
  const [sortBy, setSortBy] = useState(null);
  const [sortOrder, setSortOrder] = useState('asc');
  
  const erpApi = useERPApi();

  const search = useCallback(async (term = searchTerm, filterOptions = filters, sortOptions = { field: sortBy, order: sortOrder }) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiMethod.call(erpApi, {
        search: term,
        filters: filterOptions,
        sort: sortOptions,
        ...dependencies
      });
      
      setData(result.data || result);
      
    } catch (err) {
      setError(err.message || 'An error occurred while searching');
    } finally {
      setLoading(false);
    }
  }, [apiMethod, erpApi, searchTerm, filters, sortBy, sortOrder, ...dependencies]);

  // Debounced search effect
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (searchTerm || Object.keys(filters).length > 0) {
        search();
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, filters, sortBy, sortOrder, search]);

  const updateSearchTerm = useCallback((term) => {
    setSearchTerm(term);
  }, []);

  const updateFilters = useCallback((newFilters) => {
    setFilters(newFilters);
  }, []);

  const updateSort = useCallback((field, order = 'asc') => {
    setSortBy(field);
    setSortOrder(order);
  }, []);

  const clearSearch = useCallback(() => {
    setSearchTerm('');
    setFilters({});
    setSortBy(null);
    setSortOrder('asc');
  }, []);

  return {
    data,
    loading,
    error,
    searchTerm,
    filters,
    sortBy,
    sortOrder,
    updateSearchTerm,
    updateFilters,
    updateSort,
    clearSearch,
    search
  };
};
