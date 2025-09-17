// ERP API Service Class
class ERPApiService {
  constructor(apiClient) {
    this.apiClient = apiClient;
  }

  // Generic error handler
  handleError(error) {
    console.error('API Error:', error);
    throw new Error(error.message || 'An error occurred while fetching data');
  }

  // Generic API methods
  async get(endpoint) {
    try {
      if (!this.apiClient) {
        throw new Error('API client not initialized');
      }
      return await this.apiClient.get(endpoint);
    } catch (error) {
      this.handleError(error);
    }
  }

  async post(endpoint, data) {
    try {
      if (!this.apiClient) {
        throw new Error('API client not initialized');
      }
      
      // Debug: Log the API call details
      console.log('ERP API Service POST:', endpoint, data);
      
      return await this.apiClient.post(endpoint, data);
    } catch (error) {
      console.error('ERP API Service POST Error:', error);
      this.handleError(error);
    }
  }

  async put(endpoint, data) {
    try {
      if (!this.apiClient) {
        throw new Error('API client not initialized');
      }
      return await this.apiClient.put(endpoint, data);
    } catch (error) {
      this.handleError(error);
    }
  }

  async delete(endpoint) {
    try {
      if (!this.apiClient) {
        throw new Error('API client not initialized');
      }
      return await this.apiClient.delete(endpoint);
    } catch (error) {
      this.handleError(error);
    }
  }

  // Inventory Management APIs
  async getInventoryCategories() {
    return this.get('/api/inventory/categories');
  }

  async createInventoryCategory(categoryData) {
    return this.post('/api/inventory/categories', categoryData);
  }

  async updateInventoryCategory(id, categoryData) {
    return this.put(`/api/inventory/categories/${id}`, categoryData);
  }

  async deleteInventoryCategory(id) {
    return this.delete(`/api/inventory/categories/${id}`);
  }

  async getInventoryProducts() {
    return this.get('/api/inventory/products');
  }

  async createInventoryProduct(productData) {
    return this.post('/api/inventory/products', productData);
  }

  async updateInventoryProduct(id, productData) {
    return this.put(`/api/inventory/products/${id}`, productData);
  }

  async deleteInventoryProduct(id) {
    return this.delete(`/api/inventory/products/${id}`);
  }

  async getInventoryWarehouses() {
    return this.get('/api/inventory/warehouses');
  }

  async createInventoryWarehouse(warehouseData) {
    return this.post('/api/inventory/warehouses', warehouseData);
  }

  async updateInventoryWarehouse(id, warehouseData) {
    return this.put(`/api/inventory/warehouses/${id}`, warehouseData);
  }

  async deleteInventoryWarehouse(id) {
    return this.delete(`/api/inventory/warehouses/${id}`);
  }

  async getInventoryTransactions() {
    return this.get('/api/inventory/transactions');
  }

  async createInventoryTransaction(transactionData) {
    return this.post('/api/inventory/transactions', transactionData);
  }

  async getInventoryAnalytics() {
    return this.get('/api/inventory/analytics');
  }

  // Procurement APIs
  async getProcurementSuppliers() {
    return this.get('/api/procurement/suppliers');
  }

  async createProcurementSupplier(supplierData) {
    return this.post('/api/procurement/suppliers', supplierData);
  }

  async updateProcurementSupplier(id, supplierData) {
    return this.put(`/api/procurement/suppliers/${id}`, supplierData);
  }

  async deleteProcurementSupplier(id) {
    return this.delete(`/api/procurement/suppliers/${id}`);
  }

  async getProcurementPurchaseOrders() {
    return this.get('/api/procurement/purchase-orders');
  }

  async createProcurementPurchaseOrder(orderData) {
    return this.post('/api/procurement/purchase-orders', orderData);
  }

  async updateProcurementPurchaseOrder(id, orderData) {
    return this.put(`/api/procurement/purchase-orders/${id}`, orderData);
  }

  async deleteProcurementPurchaseOrder(id) {
    return this.delete(`/api/procurement/purchase-orders/${id}`);
  }

  async getProcurementAnalytics() {
    return this.get('/api/procurement/analytics');
  }

  // Manufacturing APIs
  async getManufacturingBOMs() {
    return this.get('/api/manufacturing/boms');
  }

  async createManufacturingBOM(bomData) {
    return this.post('/api/manufacturing/boms', bomData);
  }

  async updateManufacturingBOM(id, bomData) {
    return this.put(`/api/manufacturing/boms/${id}`, bomData);
  }

  async deleteManufacturingBOM(id) {
    return this.delete(`/api/manufacturing/boms/${id}`);
  }

  async getManufacturingProductionOrders() {
    return this.get('/api/manufacturing/production-orders');
  }

  async createManufacturingProductionOrder(orderData) {
    return this.post('/api/manufacturing/production-orders', orderData);
  }

  async updateManufacturingProductionOrder(id, orderData) {
    return this.put(`/api/manufacturing/production-orders/${id}`, orderData);
  }

  async deleteManufacturingProductionOrder(id) {
    return this.delete(`/api/manufacturing/production-orders/${id}`);
  }

  async getManufacturingWorkCenters() {
    return this.get('/api/manufacturing/work-centers');
  }

  async createManufacturingWorkCenter(workCenterData) {
    return this.post('/api/manufacturing/work-centers', workCenterData);
  }

  async updateManufacturingWorkCenter(id, workCenterData) {
    return this.put(`/api/manufacturing/work-centers/${id}`, workCenterData);
  }

  async deleteManufacturingWorkCenter(id) {
    return this.delete(`/api/manufacturing/work-centers/${id}`);
  }

  async getManufacturingAnalytics() {
    return this.get('/api/manufacturing/analytics');
  }

  // Compliance APIs
  async getComplianceFrameworks() {
    return this.get('/api/compliance/frameworks');
  }

  async createComplianceFramework(frameworkData) {
    return this.post('/api/compliance/frameworks', frameworkData);
  }

  async updateComplianceFramework(id, frameworkData) {
    return this.put(`/api/compliance/frameworks/${id}`, frameworkData);
  }

  async deleteComplianceFramework(id) {
    return this.delete(`/api/compliance/frameworks/${id}`);
  }

  async getComplianceLegalEntities() {
    return this.get('/api/compliance/legal-entities');
  }

  async createComplianceLegalEntity(entityData) {
    return this.post('/api/compliance/legal-entities', entityData);
  }

  async updateComplianceLegalEntity(id, entityData) {
    return this.put(`/api/compliance/legal-entities/${id}`, entityData);
  }

  async deleteComplianceLegalEntity(id) {
    return this.delete(`/api/compliance/legal-entities/${id}`);
  }

  async getComplianceFinancialStatements() {
    return this.get('/api/compliance/financial-statements');
  }

  async createComplianceFinancialStatement(statementData) {
    return this.post('/api/compliance/financial-statements', statementData);
  }

  async updateComplianceFinancialStatement(id, statementData) {
    return this.put(`/api/compliance/financial-statements/${id}`, statementData);
  }

  async deleteComplianceFinancialStatement(id) {
    return this.delete(`/api/compliance/financial-statements/${id}`);
  }

  async getComplianceAnalytics() {
    return this.get('/api/compliance/analytics');
  }

  // Security APIs
  async getSecurityRoles() {
    return this.get('/api/security/roles');
  }

  async createSecurityRole(roleData) {
    return this.post('/api/security/roles', roleData);
  }

  async updateSecurityRole(id, roleData) {
    return this.put(`/api/security/roles/${id}`, roleData);
  }

  async deleteSecurityRole(id) {
    return this.delete(`/api/security/roles/${id}`);
  }

  async getSecurityPermissions() {
    return this.get('/api/security/permissions');
  }

  async createSecurityPermission(permissionData) {
    return this.post('/api/security/permissions', permissionData);
  }

  async updateSecurityPermission(id, permissionData) {
    return this.put(`/api/security/permissions/${id}`, permissionData);
  }

  async deleteSecurityPermission(id) {
    return this.delete(`/api/security/permissions/${id}`);
  }

  async getSecurityUserRoles() {
    return this.get('/api/security/user-roles');
  }

  async createSecurityUserRole(userRoleData) {
    return this.post('/api/security/user-roles', userRoleData);
  }

  async updateSecurityUserRole(id, userRoleData) {
    return this.put(`/api/security/user-roles/${id}`, userRoleData);
  }

  async deleteSecurityUserRole(id) {
    return this.delete(`/api/security/user-roles/${id}`);
  }

  async getSecurityAnalytics() {
    return this.get('/api/security/analytics');
  }

  // API Ecosystem APIs
  async getAPIEcosystemKeys() {
    return this.get('/api/ecosystem/api-keys');
  }

  async createAPIEcosystemKey(keyData) {
    return this.post('/api/ecosystem/api-keys', keyData);
  }

  async updateAPIEcosystemKey(id, keyData) {
    return this.put(`/api/ecosystem/api-keys/${id}`, keyData);
  }

  async deleteAPIEcosystemKey(id) {
    return this.delete(`/api/ecosystem/api-keys/${id}`);
  }

  async getAPIEcosystemCalls() {
    return this.get('/api/ecosystem/api-calls');
  }

  async getAPIEcosystemIntegrations() {
    return this.get('/api/ecosystem/integrations');
  }

  async createAPIEcosystemIntegration(integrationData) {
    return this.post('/api/ecosystem/integrations', integrationData);
  }

  async updateAPIEcosystemIntegration(id, integrationData) {
    return this.put(`/api/ecosystem/integrations/${id}`, integrationData);
  }

  async deleteAPIEcosystemIntegration(id) {
    return this.delete(`/api/ecosystem/integrations/${id}`);
  }

  async getAPIEcosystemMarketplaceApps() {
    return this.get('/api/ecosystem/marketplace-apps');
  }

  async createAPIEcosystemMarketplaceApp(appData) {
    return this.post('/api/ecosystem/marketplace-apps', appData);
  }

  async updateAPIEcosystemMarketplaceApp(id, appData) {
    return this.put(`/api/ecosystem/marketplace-apps/${id}`, appData);
  }

  async deleteAPIEcosystemMarketplaceApp(id) {
    return this.delete(`/api/ecosystem/marketplace-apps/${id}`);
  }

  async getAPIEcosystemAnalytics() {
    return this.get('/api/ecosystem/analytics');
  }

  // AI & Machine Learning APIs
  async getAIModels() {
    return this.get('/api/ai/models');
  }

  async createAIModel(modelData) {
    return this.post('/api/ai/models', modelData);
  }

  async updateAIModel(id, modelData) {
    return this.put(`/api/ai/models/${id}`, modelData);
  }

  async deleteAIModel(id) {
    return this.delete(`/api/ai/models/${id}`);
  }

  async getAIPredictions() {
    return this.get('/api/ai/predictions');
  }

  async createAIPrediction(predictionData) {
    return this.post('/api/ai/predictions', predictionData);
  }

  async getAIAnomalyDetections() {
    return this.get('/api/ai/anomaly-detections');
  }

  async createAIAnomalyDetection(anomalyData) {
    return this.post('/api/ai/anomaly-detections', anomalyData);
  }

  async getAIRPAWorkflows() {
    return this.get('/api/ai/rpa-workflows');
  }

  async createAIRPAWorkflow(workflowData) {
    return this.post('/api/ai/rpa-workflows', workflowData);
  }

  async updateAIRPAWorkflow(id, workflowData) {
    return this.put(`/api/ai/rpa-workflows/${id}`, workflowData);
  }

  async deleteAIRPAWorkflow(id) {
    return this.delete(`/api/ai/rpa-workflows/${id}`);
  }

  async getAIConversations() {
    return this.get('/api/ai/conversations');
  }

  async createAIConversation(conversationData) {
    return this.post('/api/ai/conversations', conversationData);
  }

  async getAIAnalytics() {
    return this.get('/api/ai/analytics');
  }

  // Tax Management APIs
  async getTaxRates() {
    return this.get('/api/tax/rates');
  }

  async createTaxRate(taxRateData) {
    return this.post('/api/tax/rates', taxRateData);
  }

  async updateTaxRate(id, taxRateData) {
    return this.put(`/api/tax/rates/${id}`, taxRateData);
  }

  async deleteTaxRate(id) {
    return this.delete(`/api/tax/rates/${id}`);
  }

  async getTaxCalculations() {
    return this.get('/api/tax/calculations');
  }

  async createTaxCalculation(calculationData) {
    return this.post('/api/tax/calculations', calculationData);
  }

  async getTaxAnalytics() {
    return this.get('/api/tax/analytics');
  }

  // Workflow Automation APIs
  async getWorkflowTemplates() {
    return this.get('/api/workflow/templates');
  }

  async createWorkflowTemplate(templateData) {
    return this.post('/api/workflow/templates', templateData);
  }

  async updateWorkflowTemplate(id, templateData) {
    return this.put(`/api/workflow/templates/${id}`, templateData);
  }

  async deleteWorkflowTemplate(id) {
    return this.delete(`/api/workflow/templates/${id}`);
  }

  async getWorkflowExecutions() {
    return this.get('/api/workflow/executions');
  }

  async createWorkflowExecution(executionData) {
    return this.post('/api/workflow/executions', executionData);
  }

  async getWorkflowAnalytics() {
    return this.get('/api/workflow/analytics');
  }

  // Customization APIs
  async getCustomizationFields() {
    return this.get('/api/customization/fields');
  }

  async createCustomizationField(fieldData) {
    return this.post('/api/customization/fields', fieldData);
  }

  async updateCustomizationField(id, fieldData) {
    return this.put(`/api/customization/fields/${id}`, fieldData);
  }

  async deleteCustomizationField(id) {
    return this.delete(`/api/customization/fields/${id}`);
  }

  async getCustomizationTemplates() {
    return this.get('/api/customization/templates');
  }

  async createCustomizationTemplate(templateData) {
    return this.post('/api/customization/templates', templateData);
  }

  async updateCustomizationTemplate(id, templateData) {
    return this.put(`/api/customization/templates/${id}`, templateData);
  }

  async deleteCustomizationTemplate(id) {
    return this.delete(`/api/customization/templates/${id}`);
  }

  async getCustomizationAnalytics() {
    return this.get('/api/customization/analytics');
  }

  // Dashboard Builder APIs
  async getDashboardWidgets() {
    return this.get('/api/dashboard/widgets');
  }

  async createDashboardWidget(widgetData) {
    return this.post('/api/dashboard/widgets', widgetData);
  }

  async updateDashboardWidget(id, widgetData) {
    return this.put(`/api/dashboard/widgets/${id}`, widgetData);
  }

  async deleteDashboardWidget(id) {
    return this.delete(`/api/dashboard/widgets/${id}`);
  }

  async getDashboardLayouts() {
    return this.get('/api/dashboard/layouts');
  }

  async createDashboardLayout(layoutData) {
    return this.post('/api/dashboard/layouts', layoutData);
  }

  async updateDashboardLayout(id, layoutData) {
    return this.put(`/api/dashboard/layouts/${id}`, layoutData);
  }

  async deleteDashboardLayout(id) {
    return this.delete(`/api/dashboard/layouts/${id}`);
  }

  async getDashboardAnalytics() {
    return this.get('/api/dashboard/analytics');
  }

  // Audit Logs APIs
  async getAuditLogs() {
    return this.get('/api/audit/logs');
  }

  async getAuditLogsByUser(userId) {
    return this.get(`/api/audit/logs/user/${userId}`);
  }

  async getAuditLogsByModule(module) {
    return this.get(`/api/audit/logs/module/${module}`);
  }

  async getAuditLogsByDateRange(startDate, endDate) {
    return this.get(`/api/audit/logs/date-range?start=${startDate}&end=${endDate}`);
  }

  async getAuditAnalytics() {
    return this.get('/api/audit/analytics');
  }

  // System Health Check
  async getSystemHealth() {
    return this.get('/health');
  }

  // ERP Dashboard Summary
  async getERPDashboardSummary() {
    return this.get('/api/erp/dashboard-summary');
  }
}

// Create singleton instance
const erpApiServiceInstance = new ERPApiService(null);

// Function to initialize the API service with the apiClient
export const initializeERPApiService = (apiClient) => {
  erpApiServiceInstance.apiClient = apiClient;
};

// Function to get ERP API Service instance
export const getERPApiService = () => {
  return erpApiServiceInstance;
};

// Export the singleton instance as default
export default erpApiServiceInstance;
