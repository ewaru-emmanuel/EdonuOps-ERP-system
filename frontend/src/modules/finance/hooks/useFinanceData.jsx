import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../../App';

export const useFinanceData = (endpoint) => {
  const { apiClient } = useAuth();
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      console.log(`🔄 Fetching finance data: ${endpoint}`);
      
      const response = await apiClient.get(`/finance/${endpoint}`);
      console.log(`✅ Finance data received:`, response);
      
      // Handle paginated responses (like GL entries)
      if (response.data && Array.isArray(response.data)) {
        setData(response.data);
      } else if (response.pagination && Array.isArray(response.data)) {
        setData(response.data);
      } else if (Array.isArray(response)) {
        setData(response);
      } else {
        setData([]);
      }
      
      setError(null);
    } catch (err) {
      console.error(`❌ Finance data fetch failed for ${endpoint}:`, err);
      setError(err.message || 'Failed to fetch data');
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [apiClient, endpoint]);

  useEffect(() => {
    fetchData();
  }, [fetchData]); // ✅ now fetchData is stable

  return { data, loading, error, refresh: fetchData };
};
