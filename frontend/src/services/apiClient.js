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
    return localStorage.getItem('access_token');
  }

  // Get headers with authentication
  getHeaders(customHeaders = {}) {
    const token = this.getAuthToken();
    return {
      ...this.defaultHeaders,
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...customHeaders
    };
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
    const headers = this.getHeaders(options.headers);

    return this.retryRequest(async () => {
      const response = await fetch(url, {
        method: 'GET',
        headers,
        ...options
      });

      if (!response.ok) {
        // Handle token expiration
        if (response.status === 401) {
          // Clear expired token and redirect to login
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    });
  }

  // Generic POST request
  async post(endpoint, data = null, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = this.getHeaders(options.headers);

    return this.retryRequest(async () => {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: data ? JSON.stringify(data) : null,
        ...options
      });

      if (!response.ok) {
        // Handle token expiration
        if (response.status === 401) {
          // Clear expired token and redirect to login
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    });
  }

  // Generic PUT request
  async put(endpoint, data = null, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = this.getHeaders(options.headers);

    return this.retryRequest(async () => {
      const response = await fetch(url, {
        method: 'PUT',
        headers,
        body: data ? JSON.stringify(data) : null,
        ...options
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    });
  }

  // Generic DELETE request
  async delete(endpoint, options = {}) {
    const url = buildApiUrl(endpoint);
    const headers = this.getHeaders(options.headers);

    return this.retryRequest(async () => {
      const response = await fetch(url, {
        method: 'DELETE',
        headers,
        ...options
      });

      if (!response.ok) {
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
      ...this.getHeaders(),
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

