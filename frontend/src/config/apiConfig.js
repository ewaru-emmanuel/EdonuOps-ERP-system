/**
 * Centralized API Configuration
 * Enterprise-grade API configuration management
 */

// Environment-based API configuration
const API_CONFIG = {
  // Development environment
  development: {
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  },
  
  // Staging environment
  staging: {
    baseURL: process.env.REACT_APP_API_URL || 'https://staging-api.edonuops.com',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  },
  
  // Production environment
  production: {
    baseURL: process.env.REACT_APP_API_URL || 'https://api.edonuops.com',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  },
  
  // AWS environment
  aws: {
    baseURL: process.env.REACT_APP_API_URL || 'https://your-aws-api-domain.com',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  },
  
  // Azure environment
  azure: {
    baseURL: process.env.REACT_APP_API_URL || 'https://your-azure-api-domain.com',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  },
  
  // GCP environment
  gcp: {
    baseURL: process.env.REACT_APP_API_URL || 'https://your-gcp-api-domain.com',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  }
};

// Get current environment
const getCurrentEnvironment = () => {
  return process.env.NODE_ENV || 'development';
};

// Get API configuration for current environment
const getApiConfig = () => {
  const env = getCurrentEnvironment();
  return API_CONFIG[env] || API_CONFIG.development;
};

// API Endpoints - Centralized endpoint definitions
export const API_ENDPOINTS = {
  // Health and Status
  HEALTH: '/health',
  
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh'
  },
  
  // Inventory Management
  INVENTORY: {
    PRODUCTS: '/api/inventory/products',
    CATEGORIES: '/api/inventory/categories',
    WAREHOUSES: '/api/inventory/warehouses',
    STOCK_LEVELS: '/api/inventory/stock-levels',
    TRANSACTIONS: '/api/inventory/transactions',
    UOM: '/api/inventory/uom',
    WAREHOUSE_ZONES: '/api/inventory/warehouse-zones',
    WAREHOUSE_AISLES: '/api/inventory/warehouse-aisles',
    STOCK_TAKE: '/api/inventory/stock-take',
    TAKING: {
      COUNTS: '/api/inventory/taking/counts',
      EXPORT_TEMPLATE: '/api/inventory/taking/export-template',
      IMPORT_CSV: '/api/inventory/taking/import-csv'
    },
    DATA_INTEGRITY: {
      RECONCILIATION: '/api/inventory/data-integrity/reconciliation/run',
      CONCURRENCY_TEST: '/api/inventory/data-integrity/concurrency/test'
    },
    COMPLEXITY: {
      ONBOARDING_SETUP: '/api/inventory/complexity/onboarding/setup'
    }
  },
  
  // Finance Management
  FINANCE: {
    SETTINGS: {
      BASE_CURRENCY: '/api/finance/settings/base-currency'
    },
    EXCHANGE_RATES: '/api/finance/exchange-rates',
    CURRENCY: {
      CONVERT_ALL: '/api/finance/currency/convert-all'
    },
    VALUATION: {
      EXPOSURE: '/api/finance/valuation/exposure',
      PURCHASE: '/api/finance/valuation/purchase'
    },
    AR: '/finance/ar'
  },
  
  // Onboarding
  ONBOARDING: {
    DISCOVERY: {
      ANALYZE: '/api/onboarding/discovery/analyze'
    },
    CONFIGURATION: {
      MODULES: '/api/onboarding/configuration/modules'
    },
    QUICK_START: '/api/onboarding/quick-start'
  },
  
  // Admin APIs
  ADMIN: {
    CORS: {
      ORIGINS: '/api/admin/cors/origins',
      ENVIRONMENT: '/api/admin/cors/environment',
      QUICK_ADD: '/api/admin/cors/quick-add'
    }
  }
};

// Helper function to build full API URL
export const buildApiUrl = (endpoint) => {
  const config = getApiConfig();
  return `${config.baseURL}${endpoint}`;
};

// Helper function to get API configuration
export const getApiConfiguration = () => {
  return getApiConfig();
};

// Helper function to get current environment
export const getEnvironment = () => {
  return getCurrentEnvironment();
};

// Default export
export default {
  getApiConfig,
  getCurrentEnvironment,
  API_ENDPOINTS,
  buildApiUrl,
  getApiConfiguration,
  getEnvironment
};

