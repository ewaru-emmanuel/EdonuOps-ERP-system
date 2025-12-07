import { useCallback, useState } from 'react';
import { useTenant } from '../contexts/TenantContext';

// Helper function to check if token is valid
const isTokenValid = (token) => {
  if (!token) return false;
  
  try {
    // Basic JWT token validation (check if it's properly formatted)
    const parts = token.split('.');
    if (parts.length !== 3) return false;
    
    // Decode payload to check expiration
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    
    if (payload.exp && payload.exp < now) {
      console.warn('⚠️ Token has expired');
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('❌ Invalid token format:', error);
    return false;
  }
};

export const useTenantApi = () => {
  const { currentTenant } = useTenant();
  const [loading, setLoading] = useState(false);

  const apiCall = useCallback(async (endpoint, options = {}) => {
    const token = localStorage.getItem('access_token') || 'default-token';
    const tenantData = currentTenant || {
      tenant_id: process.env.REACT_APP_DEFAULT_TENANT_ID || 'default',
      user_id: process.env.REACT_APP_DEFAULT_USER_ID || ''
    };

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-Tenant-ID': tenantData.tenant_id,
      'X-User-ID': tenantData.user_id,
      ...options.headers
    };

    try {
      setLoading(true);
      
      // Construct full URL with backend base URL
      // In development, use full URL to backend; in production, use relative URLs
      const isDevelopment = process.env.NODE_ENV === 'development' || !process.env.NODE_ENV;
      const baseURL = process.env.REACT_APP_API_BASE_URL || process.env.REACT_APP_API_URL || 
                     (isDevelopment ? process.env.REACT_APP_API_URL || '' : '');
      const fullURL = endpoint.startsWith('http') ? endpoint : `${baseURL}${endpoint}`;
      
      console.log(`🌐 API Call: ${fullURL}`);
      console.log(`📋 Headers:`, headers);
      
      const response = await fetch(fullURL, {
        ...options,
        headers
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.error || `API call failed: ${response.statusText}`;
        
        // Log detailed error information for debugging
        console.error(`❌ API Error: ${response.status} ${response.statusText}`);
        console.error('Endpoint:', endpoint);
        console.error('Error data:', errorData);
        
        // Handle specific error cases
        if (response.status === 401) {
          console.warn('⚠️ API authentication failed - using fallback data');
          // Return empty data instead of blocking user
          return [];
        } else if (response.status === 403) {
          console.error('🚫 Access denied - insufficient permissions');
          throw new Error('Access denied. You do not have permission to perform this action.');
        } else if (response.status === 404) {
          console.error('🔍 Resource not found');
          throw new Error('Resource not found. Please check the endpoint.');
        } else {
          console.error('❌ API Error:', errorMessage);
          throw new Error(errorMessage);
        }
      }

      // Check if response is JSON before parsing
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        // Response is not JSON (likely HTML error page)
        const text = await response.text();
        console.error('❌ Non-JSON response received:', {
          status: response.status,
          statusText: response.statusText,
          contentType: contentType,
          response: text.substring(0, 200) + (text.length > 200 ? '...' : '')
        });
        
        if (response.status === 404) {
          throw new Error('API endpoint not found. Please check if the backend server is running and the endpoint exists.');
        } else if (response.status === 500) {
          throw new Error('Server error. Please check the backend logs.');
        } else {
          throw new Error(`Unexpected response format. Expected JSON but received ${contentType || 'unknown'}. Status: ${response.status}`);
        }
      }
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [currentTenant]);

  // Convenience methods for common HTTP methods
  const get = useCallback((endpoint, options = {}) => {
    return apiCall(endpoint, { ...options, method: 'GET' });
  }, [apiCall]);

  const post = useCallback((endpoint, data, options = {}) => {
    return apiCall(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }, [apiCall]);

  const put = useCallback((endpoint, data, options = {}) => {
    return apiCall(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }, [apiCall]);

  const del = useCallback((endpoint, options = {}) => {
    return apiCall(endpoint, { ...options, method: 'DELETE' });
  }, [apiCall]);

  return {
    apiCall,
    get,
    post,
    put,
    delete: del,
    loading
  };
};

// Hook for tenant-aware data fetching
export const useTenantData = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { get } = useTenantApi();

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await get(endpoint, options);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [endpoint, get, options]);

  const refresh = useCallback(() => {
    return fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    fetchData,
    refresh
  };
};

// Hook for tenant-aware CRUD operations
export const useTenantCrud = (baseEndpoint) => {
  const { get, post, put, delete: del } = useTenantApi();

  const create = useCallback(async (data) => {
    return await post(baseEndpoint, data);
  }, [baseEndpoint, post]);

  const read = useCallback(async (id) => {
    return await get(`${baseEndpoint}/${id}`);
  }, [baseEndpoint, get]);

  const update = useCallback(async (id, data) => {
    return await put(`${baseEndpoint}/${id}`, data);
  }, [baseEndpoint, put]);

  const remove = useCallback(async (id) => {
    return await del(`${baseEndpoint}/${id}`);
  }, [baseEndpoint, del]);

  const list = useCallback(async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `${baseEndpoint}?${queryString}` : baseEndpoint;
    return await get(endpoint);
  }, [baseEndpoint, get]);

  return {
    create,
    read,
    update,
    remove,
    list
  };
};
