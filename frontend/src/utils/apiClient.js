// In development, use full URL to backend; in production, use relative URLs
const isDevelopment = process.env.NODE_ENV === 'development' || !process.env.NODE_ENV;
const BASE_URL = process.env.REACT_APP_API_BASE_URL || process.env.REACT_APP_API_URL || 
                (isDevelopment ? process.env.REACT_APP_API_URL || '' : '');

const getHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
};

export const apiClient = {
  get: async (path) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Network error');
    }
    return response.json();
  },

  post: async (path, data) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(errorData.message || errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      error.response = { status: response.status, statusText: response.statusText, data: errorData };
      throw error;
    }
    return response.json();
  },

  put: async (path, data) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Network error');
    }
    return response.json();
  },

  patch: async (path, data) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Network error');
    }
    return response.json();
  },

  delete: async (path) => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: 'DELETE',
      headers: getHeaders(),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || 'Network error');
    }
    return response.json();
  },
};


