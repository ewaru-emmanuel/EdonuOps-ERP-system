# 🔧 API Standardization Guide

## **Overview**

This guide outlines the complete API standardization process to eliminate hardcoded localhost URLs and implement enterprise-grade API management.

## **🚨 Critical Issues Found**

### **Hardcoded URLs Detected:**

1. **OnboardingHub.jsx** - 3 hardcoded URLs
2. **SmartProductManagement.jsx** - 4 hardcoded URLs  
3. **GlobalCurrencySettings.jsx** - 4 hardcoded URLs
4. **MultiCurrencyValuation.jsx** - 4 hardcoded URLs
5. **OnboardingWizard.jsx** - 1 hardcoded URL
6. **InventoryTakingPopup.jsx** - 4 hardcoded URLs
7. **DataIntegrityAdminPanel.jsx** - 2 hardcoded URLs
8. **Register.jsx** - 1 hardcoded URL
9. **BackendStatusChecker.jsx** - 3 hardcoded URLs
10. **FinanceDataContext.jsx** - 3 hardcoded URLs

**Total: 29 hardcoded localhost URLs found!**

## **✅ Solution Implemented**

### **1. Centralized API Configuration**

**File:** `frontend/src/config/apiConfig.js`

```javascript
// Environment-based API configuration
const API_CONFIG = {
  development: {
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  },
  staging: {
    baseURL: process.env.REACT_APP_API_URL || 'https://staging-api.edonuops.com',
    // ...
  },
  production: {
    baseURL: process.env.REACT_APP_API_URL || 'https://api.edonuops.com',
    // ...
  },
  aws: {
    baseURL: process.env.REACT_APP_API_URL || 'https://your-aws-api-domain.com',
    // ...
  }
  // ... more environments
};
```

### **2. Standardized API Client**

**File:** `frontend/src/services/apiClient.js`

```javascript
class ApiClient {
  // Generic methods
  async get(endpoint, options = {})
  async post(endpoint, data = null, options = {})
  async put(endpoint, data = null, options = {})
  async delete(endpoint, options = {})
  async upload(endpoint, file, options = {})
  
  // Specific business methods
  async getInventoryProducts()
  async createInventoryProduct(productData)
  async updateInventoryProduct(id, productData)
  async deleteInventoryProduct(id)
  // ... and many more
}
```

### **3. Centralized Endpoint Definitions**

```javascript
export const API_ENDPOINTS = {
  HEALTH: '/health',
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    // ...
  },
  INVENTORY: {
    PRODUCTS: '/api/inventory/products',
    CATEGORIES: '/api/inventory/categories',
    // ...
  },
  FINANCE: {
    SETTINGS: {
      BASE_CURRENCY: '/api/finance/settings/base-currency'
    },
    // ...
  }
  // ... more endpoints
};
```

## **🔄 Migration Process**

### **Step 1: Add Import**

Add this import to each component:

```javascript
import apiClient from '../services/apiClient';
// or
import apiClient from '../../../services/apiClient';
// (adjust path based on file location)
```

### **Step 2: Replace Fetch Calls**

**Before:**
```javascript
const response = await fetch('http://localhost:5000/api/inventory/products', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(formData)
});
```

**After:**
```javascript
const response = await apiClient.createInventoryProduct(formData);
```

### **Step 3: Update Response Handling**

**Before:**
```javascript
if (response.ok) {
  const data = await response.json();
  // handle data
}
```

**After:**
```javascript
// Response is already parsed JSON
// handle response directly
```

## **📋 Files Requiring Updates**

### **High Priority (Core Components):**

1. **OnboardingHub.jsx**
   - Add: `import apiClient from '../services/apiClient';`
   - Replace 3 fetch calls with apiClient methods

2. **SmartProductManagement.jsx**
   - Add: `import apiClient from '../../../services/apiClient';`
   - Replace 4 fetch calls with apiClient methods

3. **GlobalCurrencySettings.jsx**
   - Add: `import apiClient from '../services/apiClient';`
   - Replace 4 fetch calls with apiClient methods

### **Medium Priority (Feature Components):**

4. **MultiCurrencyValuation.jsx**
5. **OnboardingWizard.jsx**
6. **InventoryTakingPopup.jsx**
7. **DataIntegrityAdminPanel.jsx**

### **Low Priority (Utility Components):**

8. **Register.jsx**
9. **BackendStatusChecker.jsx**
10. **FinanceDataContext.jsx**

## **🎯 Benefits of Standardization**

### **1. Environment Flexibility**
- Easy deployment to AWS, Azure, GCP
- Environment-specific configurations
- No code changes needed for deployment

### **2. Enterprise Features**
- Automatic retry mechanism
- Request/response logging
- Error handling standardization
- Authentication token management

### **3. Maintainability**
- Centralized endpoint management
- Consistent error handling
- Easy to add new endpoints
- Type safety and validation

### **4. Security**
- Environment-specific CORS
- Proper authentication headers
- Request validation
- Audit logging

## **🚀 Deployment Ready**

### **Environment Variables:**

```bash
# Development
REACT_APP_API_URL=http://localhost:5000

# Staging
REACT_APP_API_URL=https://staging-api.edonuops.com

# Production
REACT_APP_API_URL=https://api.edonuops.com

# AWS
REACT_APP_API_URL=https://your-aws-api-domain.com
```

### **CORS Management:**

Use the CORS management API to add new domains:

```bash
# Add AWS domain
curl -X POST http://your-api/api/admin/cors/origins \
  -d '{"origin": "https://your-aws-domain.com", "environment": "aws"}'

# Quick setup
curl -X POST http://your-api/api/admin/cors/quick-add \
  -d '{"scenario": "aws", "environment": "aws"}'
```

## **🔍 Testing Checklist**

### **Before Deployment:**
- [ ] All hardcoded URLs replaced
- [ ] API client imported in all components
- [ ] Response handling updated
- [ ] Error handling tested
- [ ] Authentication working
- [ ] CORS configured for target environment

### **After Deployment:**
- [ ] Health check endpoint responding
- [ ] All API calls working
- [ ] No console errors
- [ ] Authentication flow working
- [ ] Real-time updates functioning

## **📞 Support**

If you encounter issues during the migration:

1. Check the browser console for errors
2. Verify the API client is properly imported
3. Ensure the endpoint paths are correct
4. Test with the health check endpoint first
5. Use the CORS management API to add new domains

---

**This standardization ensures your application is enterprise-ready and can deploy anywhere without code changes!** 🚀

