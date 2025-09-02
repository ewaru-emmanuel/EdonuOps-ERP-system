/**
 * API Call Standardization Script
 * This script helps identify and fix hardcoded localhost URLs in the frontend
 */

// Files that need to be updated with their hardcoded URLs
const filesToUpdate = [
  {
    file: 'frontend/src/components/OnboardingHub.jsx',
    replacements: [
      {
        old: "const response = await fetch('http://localhost:5000/api/onboarding/discovery/analyze', {",
        new: "const response = await apiClient.post('/api/onboarding/discovery/analyze', discoveryData);"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/onboarding/configuration/modules', {",
        new: "const response = await apiClient.post('/api/onboarding/configuration/modules', {"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/onboarding/quick-start', {",
        new: "const response = await apiClient.post('/api/onboarding/quick-start', {"
      }
    ],
    import: "import apiClient from '../services/apiClient';"
  },
  {
    file: 'frontend/src/modules/inventory/components/SmartProductManagement.jsx',
    replacements: [
      {
        old: "const response = await fetch('http://localhost:5000/api/inventory/products', {",
        new: "const response = await apiClient.post('/api/inventory/products', formData);"
      },
      {
        old: "const response = await fetch(`http://localhost:5000/api/inventory/products/${productToDelete.id}`, {",
        new: "const response = await apiClient.delete(`/api/inventory/products/${productToDelete.id}`);"
      },
      {
        old: "const response = await fetch(`http://localhost:5000/api/inventory/products/${selectedProduct.id}`, {",
        new: "const response = await apiClient.put(`/api/inventory/products/${selectedProduct.id}`, formData);"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/inventory/stock-levels', {",
        new: "const response = await apiClient.post('/api/inventory/stock-levels', {"
      }
    ],
    import: "import apiClient from '../../../services/apiClient';"
  },
  {
    file: 'frontend/src/components/GlobalCurrencySettings.jsx',
    replacements: [
      {
        old: "const response = await fetch('http://localhost:5000/api/finance/settings/base-currency');",
        new: "const response = await apiClient.get('/api/finance/settings/base-currency');"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/finance/exchange-rates');",
        new: "const response = await apiClient.get('/api/finance/exchange-rates');"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/finance/settings/base-currency', {",
        new: "const response = await apiClient.post('/api/finance/settings/base-currency', {"
      },
      {
        old: "await fetch('http://localhost:5000/api/finance/currency/convert-all', {",
        new: "await apiClient.post('/api/finance/currency/convert-all', {"
      }
    ],
    import: "import apiClient from '../services/apiClient';"
  },
  {
    file: 'frontend/src/modules/finance/components/MultiCurrencyValuation.jsx',
    replacements: [
      {
        old: "const response = await fetch('http://localhost:5000/api/finance/settings/base-currency');",
        new: "const response = await apiClient.get('/api/finance/settings/base-currency');"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/finance/valuation/exposure');",
        new: "const response = await apiClient.get('/api/finance/valuation/exposure');"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/finance/valuation/purchase', {",
        new: "const response = await apiClient.post('/api/finance/valuation/purchase', {"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/finance/settings/base-currency', {",
        new: "const response = await apiClient.post('/api/finance/settings/base-currency', {"
      }
    ],
    import: "import apiClient from '../../../services/apiClient';"
  },
  {
    file: 'frontend/src/modules/inventory/components/OnboardingWizard.jsx',
    replacements: [
      {
        old: "const response = await fetch('http://localhost:5000/api/inventory/complexity/onboarding/setup', {",
        new: "const response = await apiClient.post('/api/inventory/complexity/onboarding/setup', {"
      }
    ],
    import: "import apiClient from '../../../services/apiClient';"
  },
  {
    file: 'frontend/src/modules/inventory/components/InventoryTakingPopup.jsx',
    replacements: [
      {
        old: "const response = await fetch('http://localhost:5000/api/inventory/taking/counts', {",
        new: "const response = await apiClient.get('/api/inventory/taking/counts');"
      },
      {
        old: "const response = await fetch(`http://localhost:5000/api/inventory/taking/counts/${inventoryData.id || 'new'}/submit`, {",
        new: "const response = await apiClient.post(`/api/inventory/taking/counts/${inventoryData.id || 'new'}/submit`, {"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/inventory/taking/export-template');",
        new: "const response = await apiClient.get('/api/inventory/taking/export-template');"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/inventory/taking/import-csv', {",
        new: "const response = await apiClient.upload('/api/inventory/taking/import-csv', file);"
      }
    ],
    import: "import apiClient from '../../../services/apiClient';"
  },
  {
    file: 'frontend/src/modules/inventory/components/DataIntegrityAdminPanel.jsx',
    replacements: [
      {
        old: "const response = await fetch('http://localhost:5000/api/inventory/data-integrity/reconciliation/run', {",
        new: "const response = await apiClient.post('/api/inventory/data-integrity/reconciliation/run');"
      },
      {
        old: "const response = await fetch('http://localhost:5000/api/inventory/data-integrity/concurrency/test', {",
        new: "const response = await apiClient.post('/api/inventory/data-integrity/concurrency/test');"
      }
    ],
    import: "import apiClient from '../../../services/apiClient';"
  },
  {
    file: 'frontend/src/pages/Register.jsx',
    replacements: [
      {
        old: "const response = await fetch('http://127.0.0.1:5000/auth/register', {",
        new: "const response = await apiClient.post('/auth/register', {"
      }
    ],
    import: "import apiClient from '../services/apiClient';"
  },
  {
    file: 'frontend/src/components/indicators/BackendStatusChecker.jsx',
    replacements: [
      {
        old: "const healthResponse = await fetch('http://127.0.0.1:5000/health', {",
        new: "const healthResponse = await apiClient.get('/health');"
      },
      {
        old: "const financeResponse = await fetch('http://127.0.0.1:5000/finance/ar', {",
        new: "const financeResponse = await apiClient.get('/finance/ar');"
      },
      {
        old: "setMessage('Cannot connect to backend. Please ensure backend is running on http://127.0.0.1:5000');",
        new: "setMessage('Cannot connect to backend. Please ensure backend is running.');"
      }
    ],
    import: "import apiClient from '../../services/apiClient';"
  },
  {
    file: 'frontend/src/modules/finance/context/FinanceDataContext.jsx',
    replacements: [
      {
        old: "const healthCheck = await fetch('http://127.0.0.1:5000/health');",
        new: "const healthCheck = await apiClient.get('/health');"
      },
      {
        old: "throw new Error('Backend server not reachable. Please ensure backend is running on http://127.0.0.1:5000');",
        new: "throw new Error('Backend server not reachable. Please ensure backend is running.');"
      },
      {
        old: "errorMessage = 'Backend server not reachable. Please ensure backend is running on http://127.0.0.1:5000';",
        new: "errorMessage = 'Backend server not reachable. Please ensure backend is running.';"
      }
    ],
    import: "import apiClient from '../../../services/apiClient';"
  }
];

console.log('Files that need to be updated:');
filesToUpdate.forEach((file, index) => {
  console.log(`${index + 1}. ${file.file}`);
  console.log(`   Import: ${file.import}`);
  console.log(`   Replacements: ${file.replacements.length}`);
  file.replacements.forEach((replacement, repIndex) => {
    console.log(`     ${repIndex + 1}. ${replacement.old.substring(0, 50)}...`);
  });
  console.log('');
});

console.log('To fix these files:');
console.log('1. Add the import statement at the top of each file');
console.log('2. Replace the hardcoded fetch calls with apiClient methods');
console.log('3. Remove the method, headers, and body parameters from fetch calls');
console.log('4. Update response handling to work with the new API client');

