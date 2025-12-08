/**
 * Standardized API Client
 * Enterprise-grade API client with centralized configuration
 */

import { buildApiUrl, getApiConfiguration, API_ENDPOINTS } from '../config/apiConfig';

class ApiClient {
  constructor() {
    this.config = getApiConfiguration();
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  // Get auth token from localStorage
  getAuthToken() {
    // Check for sessionToken first (primary token storage from AuthContext)
    const sessionToken = localStorage.getItem('sessionToken');
    if (sessionToken) {
      console.log('🔑 Token found (sessionToken):', sessionToken.substring(0, 20) + '...');
      return sessionToken;
    }
    
    // Check for access_token (JWT token from login)
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      console.log('🔑 Token found (access_token):', accessToken.substring(0, 20) + '...');
      return accessToken;
    }
    
    // Check for our authentication system
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        const token = userData.token || userData.access_token || null;
        if (token) {
          console.log('🔑 Token found (user object):', token.substring(0, 20) + '...');
        }
        return token;
      } catch {
        return null;
      }
    }
    console.log('⚠️ No token found in localStorage');
    return null;
  }

  // Get headers with authentication and user context
  getHeaders(customHeaders = {}, endpoint = '') {
    const token = this.getAuthToken();
    const user = this.getUserContext();
    
    // Define public routes where X-User-ID should not be sent
    // These routes don't require authentication, so no user context exists
    const PUBLIC_ROUTES = [
      '/api/auth/register',
      '/api/auth/login',
      '/api/auth/verify-email',
      '/api/auth/resend-verification',
      '/api/auth/reset-password',
      '/api/auth/request-password-reset',
      '/api/auth/verify-token', // Public for token validation
      '/api/invites/validate-invite'
    ];
    
    // Check if endpoint is a public route
    const isPublicRoute = PUBLIC_ROUTES.some(route => endpoint.includes(route));
    
    const headers = {
      ...this.defaultHeaders,
      ...(token && { 'Authorization': `Bearer ${token}` }),
      // Only send X-User-ID if:
      // 1. User exists and has an ID (authenticated)
      // 2. Not a public route (public routes don't need user context)
      // 3. User ID is valid (not '1' as fallback - that's a security risk)
      ...(user && user.id && !isPublicRoute && user.id !== '1' && { 
        'X-User-ID': String(user.id || user.user_id) 
      }),
      ...customHeaders
    };
    
    console.log('🔍 API Client Headers:', {
      userId: user?.id || user?.user_id,
      xUserId: headers['X-User-ID'],
      hasToken: !!token
    });
    
    return headers;
  }

  // Get user context - check multiple sources for user ID
  getUserContext() {
    try {
      // First, try to get userId directly from localStorage
      const userId = localStorage.getItem('userId');
      if (userId) {
        return { id: parseInt(userId), user_id: parseInt(userId) };
      }
      
      // Second, try to get from user object in localStorage
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          const userData = JSON.parse(userStr);
          if (userData.id || userData.user_id) {
            const uid = userData.id || userData.user_id;
            return { id: parseInt(uid), user_id: parseInt(uid) };
          }
        } catch (e) {
          // Invalid JSON, continue
        }
      }
      
      return null;
    } catch {
      return null;
    }
  }

  // Clear authentication data
  clearAuth() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('sessionToken');
    localStorage.removeItem('userId');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('username');
    localStorage.removeItem('userRole');
    localStorage.removeItem('user');
  }

  // Refresh access token automatically
  async refreshToken() {
    try {
      const token = this.getAuthToken();
      if (!token) {
        console.log('⚠️ No token to refresh');
        return false;
      }

      const url = buildApiUrl('/api/auth/refresh');
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.access_token) {
          // Update token in localStorage
          localStorage.setItem('sessionToken', data.access_token);
          localStorage.setItem('access_token', data.access_token);
          console.log('✅ Token refreshed successfully');
          return true;
        }
      }
      
      console.log('⚠️ Token refresh failed:', response.status);
      return false;
    } catch (error) {
      console.log('⚠️ Token refresh error:', error);
      return false;
    }
  }

  // Handle 401 errors with automatic token refresh
  async handle401Error(response, retryRequestFn) {
    const token = this.getAuthToken();
    if (!token) {
      console.log('⚠️ 401 but no token was sent - user not logged in');
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    try {
      const responseClone = response.clone();
      const errorData = await responseClone.json();
      
      const message = (errorData.message || '').toLowerCase();
      const error = (errorData.error || '').toLowerCase();
      
      // Check if it's an expired token (not a permission error)
      const isExpiredToken = 
        message.includes('expired') ||
        message.includes('token has expired') ||
        (message.includes('unauthorized') && !message.includes('permission') && !message.includes('insufficient'));
      
      // Check if it's an invalid token
      const isInvalidToken = 
        message.includes('invalid token') ||
        message.includes('signature verification failed') ||
        message.includes('token could not be decoded') ||
        message.includes('missing authorization header');
      
      // Check if it's a permission error
      const isPermissionError = 
        message.includes('permission') ||
        message.includes('insufficient') ||
        error.includes('permission');
      
      // Try to refresh if token is expired
      if (isExpiredToken && !isPermissionError) {
        console.log('🔄 Token expired, attempting automatic refresh...');
        const refreshSuccess = await this.refreshToken();
        if (refreshSuccess) {
          console.log('✅ Token refreshed, retrying request...');
          // Retry the original request with new token
          return retryRequestFn();
        } else {
          console.log('❌ Token refresh failed, logging out');
          this.clearAuth();
          window.dispatchEvent(new CustomEvent('auth:logout'));
          throw new Error(`HTTP ${response.status}: Token expired and refresh failed`);
        }
      }
      
      // If invalid token, logout immediately
      if (isInvalidToken && !isPermissionError) {
        console.log('🔐 Invalid token detected, logging out:', errorData);
        this.clearAuth();
        window.dispatchEvent(new CustomEvent('auth:logout'));
        throw new Error(`HTTP ${response.status}: Invalid token`);
      }
      
      // SECURITY: Any 401 that's not a permission error means token is invalid
      // Clear session immediately to prevent stale tokens from persisting
      if (!isPermissionError) {
        console.log('🔐 401 error - token invalid or user deleted, clearing session:', errorData);
        this.clearAuth();
        window.dispatchEvent(new CustomEvent('auth:logout'));
        // Redirect to login page
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login';
        }
      }
      
      // Permission errors - don't logout, just throw
      if (isPermissionError) {
        console.log('⚠️ 401 error (permission denied):', errorData);
      }
      
      throw new Error(`HTTP ${response.status}: ${errorData.message || response.statusText}`);
      
    } catch (e) {
      // If we can't parse the error, assume token is invalid and clear session
      if (e.message && !e.message.includes('HTTP')) {
        console.log('⚠️ Could not parse 401 error - clearing session to be safe:', e);
        this.clearAuth();
        window.dispatchEvent(new CustomEvent('auth:logout'));
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          window.location.href = '/login';
        }
      }
      throw e;
    }
  }

  // Retry mechanism
  async retryRequest(requestFn, retries = this.config.retryAttempts) {
    for (let i = 0; i < retries; i++) {
      try {
        return await requestFn();
      } catch (error) {
        if (i === retries - 1) throw error;
        if (error.status === 401 || error.status === 403) throw error; // Don't retry auth errors
        await new Promise(resolve => setTimeout(resolve, this.config.retryDelay * (i + 1)));
      }
    }
  }

  // Generic GET request
  async get(endpoint, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = this.getHeaders(options.headers, endpoint);

    return this.retryRequest(async () => {
      const response = await fetch(url, {
        method: 'GET',
        headers,
        ...options
      });

      if (!response.ok) {
        if (response.status === 401) {
          // SECURITY: Always handle 401 by clearing invalid tokens
          return await this.handle401Error(response, () => this.get(endpoint, options));
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    });
  }

  // Generic POST request
  async post(endpoint, data = null, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = this.getHeaders(options.headers, endpoint);

    return this.retryRequest(async () => {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: data ? JSON.stringify(data) : null,
        ...options
      });

      if (!response.ok) {
        if (response.status === 401) {
          return await this.handle401Error(response, () => this.post(endpoint, data, options));
        }
        
        // Try to parse error response body
        let errorData = null;
        try {
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            errorData = await response.json();
          }
        } catch (e) {
          // If parsing fails, errorData remains null
        }
        
        // Create error with response data for proper handling
        const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
        error.status = response.status;
        error.response = {
          status: response.status,
          statusText: response.statusText,
          data: errorData
        };
        throw error;
      }

      return await response.json();
    });
  }

  // Generic PUT request
  async put(endpoint, data = null, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = this.getHeaders(options.headers, endpoint);

    return this.retryRequest(async () => {
      const response = await fetch(url, {
        method: 'PUT',
        headers,
        body: data ? JSON.stringify(data) : null,
        ...options
      });

      if (!response.ok) {
        if (response.status === 401) {
          return await this.handle401Error(response, () => this.put(endpoint, data, options));
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    });
  }

  // Generic DELETE request
  async delete(endpoint, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = this.getHeaders(options.headers, endpoint);

    return this.retryRequest(async () => {
      const response = await fetch(url, {
        method: 'DELETE',
        headers,
        ...options
      });

      if (!response.ok) {
        if (response.status === 401) {
          return await this.handle401Error(response, () => this.delete(endpoint, options));
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    });
  }

  // File upload
  async upload(endpoint, file, options = {}) {
    const url = buildApiUrl(endpoint);
    const formData = new FormData();
    formData.append('file', file);

    const headers = {
      ...this.getHeaders(options.headers, endpoint),
      ...options.headers
    };
    delete headers['Content-Type']; // Let browser set content-type for FormData

    return this.retryRequest(async () => {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
        ...options
      });

      if (!response.ok) {
        if (response.status === 401) {
          return await this.handle401Error(response, () => this.upload(endpoint, file, options));
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    });
  }

  // Health check
  async healthCheck() {
    return this.get(API_ENDPOINTS.HEALTH);
  }

  // Authentication methods
  async login(credentials) {
    return this.post(API_ENDPOINTS.AUTH.LOGIN, credentials);
  }

  async register(userData) {
    return this.post(API_ENDPOINTS.AUTH.REGISTER, userData);
  }

  async logout() {
    return this.post(API_ENDPOINTS.AUTH.LOGOUT);
  }

  // Inventory methods
  async getInventoryProducts() {
    return this.get(API_ENDPOINTS.INVENTORY.PRODUCTS);
  }

  async createInventoryProduct(productData) {
    return this.post(API_ENDPOINTS.INVENTORY.PRODUCTS, productData);
  }

  async updateInventoryProduct(id, productData) {
    return this.put(`${API_ENDPOINTS.INVENTORY.PRODUCTS}/${id}`, productData);
  }

  async deleteInventoryProduct(id) {
    return this.delete(`${API_ENDPOINTS.INVENTORY.PRODUCTS}/${id}`);
  }

  async getInventoryStockLevels() {
    return this.get(API_ENDPOINTS.INVENTORY.STOCK_LEVELS);
  }

  async getInventoryCategories() {
    return this.get(API_ENDPOINTS.INVENTORY.CATEGORIES);
  }

  async getInventoryUOM() {
    return this.get(API_ENDPOINTS.INVENTORY.UOM);
  }

  async createInventoryUOM(uomData) {
    return this.post(API_ENDPOINTS.INVENTORY.UOM, uomData);
  }

  async updateInventoryUOM(id, uomData) {
    return this.put(`${API_ENDPOINTS.INVENTORY.UOM}/${id}`, uomData);
  }

  async deleteInventoryUOM(id) {
    return this.delete(`${API_ENDPOINTS.INVENTORY.UOM}/${id}`);
  }

  async getWarehouseZones() {
    return this.get(API_ENDPOINTS.INVENTORY.WAREHOUSE_ZONES);
  }

  async createWarehouseZone(zoneData) {
    return this.post(API_ENDPOINTS.INVENTORY.WAREHOUSE_ZONES, zoneData);
  }

  async updateWarehouseZone(id, zoneData) {
    return this.put(`${API_ENDPOINTS.INVENTORY.WAREHOUSE_ZONES}/${id}`, zoneData);
  }

  async deleteWarehouseZone(id) {
    return this.delete(`${API_ENDPOINTS.INVENTORY.WAREHOUSE_ZONES}/${id}`);
  }

  async getWarehouseAisles() {
    return this.get(API_ENDPOINTS.INVENTORY.WAREHOUSE_AISLES);
  }

  async createWarehouseAisle(aisleData) {
    return this.post(API_ENDPOINTS.INVENTORY.WAREHOUSE_AISLES, aisleData);
  }

  async updateWarehouseAisle(id, aisleData) {
    return this.put(`${API_ENDPOINTS.INVENTORY.WAREHOUSE_AISLES}/${id}`, aisleData);
  }

  async deleteWarehouseAisle(id) {
    return this.delete(`${API_ENDPOINTS.INVENTORY.WAREHOUSE_AISLES}/${id}`);
  }

  // Stock taking methods
  async getInventoryCounts() {
    return this.get(API_ENDPOINTS.INVENTORY.TAKING.COUNTS);
  }

  async submitInventoryCount(countData) {
    return this.post(API_ENDPOINTS.INVENTORY.TAKING.COUNTS, countData);
  }

  async updateInventoryCount(id, countData) {
    return this.put(`${API_ENDPOINTS.INVENTORY.TAKING.COUNTS}/${id}`, countData);
  }

  async exportInventoryTemplate() {
    return this.get(API_ENDPOINTS.INVENTORY.TAKING.EXPORT_TEMPLATE);
  }

  async importInventoryCSV(file) {
    return this.upload(API_ENDPOINTS.INVENTORY.TAKING.IMPORT_CSV, file);
  }

  // Data integrity methods
  async runDataIntegrityReconciliation() {
    return this.post(API_ENDPOINTS.INVENTORY.DATA_INTEGRITY.RECONCILIATION);
  }

  async testDataIntegrityConcurrency() {
    return this.post(API_ENDPOINTS.INVENTORY.DATA_INTEGRITY.CONCURRENCY_TEST);
  }

  // Finance methods
  async getBaseCurrency() {
    return this.get(API_ENDPOINTS.FINANCE.SETTINGS.BASE_CURRENCY);
  }

  async setBaseCurrency(currencyData) {
    return this.post(API_ENDPOINTS.FINANCE.SETTINGS.BASE_CURRENCY, currencyData);
  }

  async getExchangeRates() {
    return this.get(API_ENDPOINTS.FINANCE.EXCHANGE_RATES);
  }

  async convertAllCurrencies() {
    return this.post(API_ENDPOINTS.FINANCE.CURRENCY.CONVERT_ALL);
  }

  async getValuationExposure() {
    return this.get(API_ENDPOINTS.FINANCE.VALUATION.EXPOSURE);
  }

  async calculatePurchaseValuation(valuationData) {
    return this.post(API_ENDPOINTS.FINANCE.VALUATION.PURCHASE, valuationData);
  }

  // Onboarding methods
  async analyzeBusinessNeeds(analysisData) {
    return this.post(API_ENDPOINTS.ONBOARDING.DISCOVERY.ANALYZE, analysisData);
  }

  async configureModules(moduleData) {
    return this.post(API_ENDPOINTS.ONBOARDING.CONFIGURATION.MODULES, moduleData);
  }

  async quickStart(setupData) {
    return this.post(API_ENDPOINTS.ONBOARDING.QUICK_START, setupData);
  }

  async setupInventoryComplexity(setupData) {
    return this.post(API_ENDPOINTS.INVENTORY.COMPLEXITY.ONBOARDING_SETUP, setupData);
  }

  // Admin methods
  // Centralized Settings API
  async getAllSettings() {
    return this.get('/api/core/settings');
  }

  async getSettingsSection(section) {
    return this.get(`/api/core/settings/${section}`);
  }

  async putSettingsSection(section, dataOrEnvelope) {
    return this.put(`/api/core/settings/${section}`, dataOrEnvelope);
  }

  // Existing admin endpoints
  async getCorsOrigins() {
    return this.get(API_ENDPOINTS.ADMIN.CORS.ORIGINS);
  }

  async addCorsOrigin(originData) {
    return this.post(API_ENDPOINTS.ADMIN.CORS.ORIGINS, originData);
  }

  async removeCorsOrigin(originData) {
    return this.delete(API_ENDPOINTS.ADMIN.CORS.ORIGINS, originData);
  }

  async getCurrentEnvironment() {
    return this.get(API_ENDPOINTS.ADMIN.CORS.ENVIRONMENT);
  }

  async setEnvironment(environmentData) {
    return this.post(API_ENDPOINTS.ADMIN.CORS.ENVIRONMENT, environmentData);
  }

  async quickAddCors(scenarioData) {
    return this.post(API_ENDPOINTS.ADMIN.CORS.QUICK_ADD, scenarioData);
  }
}

// Create singleton instance
const apiClient = new ApiClient();

// Export singleton instance
export default apiClient;

// Export class for testing
export { ApiClient };

