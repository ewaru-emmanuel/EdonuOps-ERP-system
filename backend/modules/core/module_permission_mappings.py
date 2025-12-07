"""
Module-Permission Mapping Configuration
======================================

SECURITY: This file defines the explicit mapping between modules and their required permissions.
This is the source of truth for automatic permission assignment when modules are activated.

PRINCIPLE OF LEAST PRIVILEGE: Each module only grants the minimum permissions necessary for its function.
GRANULARITY: Permissions are defined at a granular level (e.g., finance.accounts.read, not just finance.*)

This configuration is:
- Version-controlled (in code)
- Centralized (single source of truth)
- Secure (no runtime modification)
- Auditable (clear mapping)
"""

# Module-Permission Mappings
# Format: module_id -> list of permission names
MODULE_PERMISSION_MAPPINGS = {
    'finance': [
        # Chart of Accounts
        'finance.accounts.read',
        'finance.accounts.create',
        'finance.accounts.update',
        'finance.accounts.delete',
        
        # Journal Entries
        'finance.journal.read',
        'finance.journal.create',
        'finance.journal.update',
        'finance.journal.delete',
        
        # General Ledger
        'finance.gl.read',
        'finance.gl.create',
        'finance.gl.update',
        'finance.gl.delete',
        
        # Accounts Payable
        'finance.ap.read',
        'finance.ap.create',
        'finance.ap.update',
        'finance.ap.delete',
        
        # Accounts Receivable
        'finance.ar.read',
        'finance.ar.create',
        'finance.ar.update',
        'finance.ar.delete',
        
        # Financial Reports
        'finance.reports.read',
        'finance.reports.create',
        
        # Reconciliation
        'finance.reconciliation.read',
        'finance.reconciliation.create',
        'finance.reconciliation.update',
        'finance.reconciliation.delete',
        
        # Assets
        'finance.assets.read',
        'finance.assets.create',
        'finance.assets.update',
        'finance.assets.delete',
        
        # Budgets
        'finance.budgets.read',
        'finance.budgets.create',
        'finance.budgets.update',
        'finance.budgets.delete',
        
        # Tax Management
        'finance.tax.read',
        'finance.tax.create',
        'finance.tax.update',
        'finance.tax.delete',
        
        # Currency
        'finance.currency.read',
        'finance.currency.create',
        
        # Payments
        'finance.payments.read',
        'finance.payments.create',
        
        # Vendors
        'finance.vendors.read',
        'finance.vendors.create',
        
        # Customers
        'finance.customers.read',
        'finance.customers.create',
        
        # Invoices
        'finance.invoices.read',
        'finance.invoices.create',
        
        # Settings
        'finance.settings.read',
        'finance.settings.create',
        
        # Workflows
        'finance.workflows.read',
        'finance.workflows.create',
        
        # Audit
        'finance.audit.read',
        'finance.audit.create',
    ],
    
    'crm': [
        'crm.contacts.read',
        'crm.contacts.create',
        'crm.contacts.update',
        'crm.contacts.delete',
        
        'crm.leads.read',
        'crm.leads.create',
        'crm.leads.update',
        'crm.leads.delete',
        
        'crm.opportunities.read',
        'crm.opportunities.create',
        'crm.opportunities.update',
        'crm.opportunities.delete',
        
        'crm.tickets.read',
        'crm.tickets.create',
        'crm.tickets.update',
        'crm.tickets.delete',
        
        'crm.companies.read',
        'crm.companies.create',
        'crm.companies.update',
        'crm.companies.delete',
        
        'crm.activities.read',
        'crm.activities.create',
        'crm.activities.update',
        'crm.activities.delete',
        
        'crm.tasks.read',
        'crm.tasks.create',
        'crm.tasks.update',
        'crm.tasks.delete',
        
        'crm.reports.read',
        'crm.automations.read',
        'crm.automations.create',
    ],
    
    'inventory': [
        'inventory.products.read',
        'inventory.products.create',
        'inventory.products.update',
        'inventory.products.delete',
        
        'inventory.categories.read',
        'inventory.categories.create',
        'inventory.categories.update',
        'inventory.categories.delete',
        
        'inventory.warehouses.read',
        'inventory.warehouses.create',
        'inventory.warehouses.update',
        'inventory.warehouses.delete',
        
        'inventory.stock.read',
        'inventory.stock.create',
        'inventory.stock.update',
        
        'inventory.transactions.read',
        'inventory.transactions.create',
        
        'inventory.reports.read',
        'inventory.settings.read',
        'inventory.settings.update',
    ],
    
    'procurement': [
        'procurement.vendors.read',
        'procurement.vendors.create',
        'procurement.vendors.update',
        'procurement.vendors.delete',
        
        'procurement.purchase_orders.read',
        'procurement.purchase_orders.create',
        'procurement.purchase_orders.update',
        'procurement.purchase_orders.delete',
        
        'procurement.receiving.read',
        'procurement.receiving.create',
        
        'procurement.invoicing.read',
        'procurement.invoicing.create',
        
        'procurement.contracts.read',
        'procurement.contracts.create',
        'procurement.contracts.update',
        'procurement.contracts.delete',
        
        'procurement.integration.read',
        'procurement.reports.read',
    ],
    
    'hr': [
        'hr.employees.read',
        'hr.employees.create',
        'hr.employees.update',
        'hr.employees.delete',
        
        'hr.payroll.read',
        'hr.payroll.create',
        'hr.payroll.update',
        
        'hr.recruitment.read',
        'hr.recruitment.create',
        
        'hr.benefits.read',
        'hr.benefits.create',
        'hr.benefits.update',
        
        'hr.time_tracking.read',
        'hr.time_tracking.create',
        
        'hr.reports.read',
    ],
    
    'analytics': [
        'analytics.dashboards.read',
        'analytics.dashboards.create',
        'analytics.dashboards.update',
        'analytics.dashboards.delete',
        
        'analytics.reports.read',
        'analytics.reports.create',
        
        'analytics.kpis.read',
        'analytics.kpis.create',
        'analytics.kpis.update',
        
        'analytics.forecasting.read',
        'analytics.forecasting.create',
        
        'analytics.visualization.read',
        'analytics.visualization.create',
    ],
}

# Permission definitions with metadata
# Format: permission_name -> {module, action, resource, description}
PERMISSION_DEFINITIONS = {
    # Finance permissions
    'finance.accounts.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'accounts',
        'description': 'View chart of accounts and account details'
    },
    'finance.accounts.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'accounts',
        'description': 'Create new accounts in chart of accounts'
    },
    'finance.accounts.update': {
        'module': 'finance',
        'action': 'update',
        'resource': 'accounts',
        'description': 'Update existing accounts'
    },
    'finance.accounts.delete': {
        'module': 'finance',
        'action': 'delete',
        'resource': 'accounts',
        'description': 'Delete accounts from chart of accounts'
    },
    'finance.journal.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'journal',
        'description': 'View journal entries'
    },
    'finance.journal.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'journal',
        'description': 'Create new journal entries'
    },
    'finance.journal.update': {
        'module': 'finance',
        'action': 'update',
        'resource': 'journal',
        'description': 'Update existing journal entries'
    },
    'finance.journal.delete': {
        'module': 'finance',
        'action': 'delete',
        'resource': 'journal',
        'description': 'Delete journal entries'
    },
    'finance.gl.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'general_ledger',
        'description': 'View general ledger entries'
    },
    'finance.gl.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'general_ledger',
        'description': 'Create general ledger entries'
    },
    'finance.gl.update': {
        'module': 'finance',
        'action': 'update',
        'resource': 'general_ledger',
        'description': 'Update general ledger entries'
    },
    'finance.gl.delete': {
        'module': 'finance',
        'action': 'delete',
        'resource': 'general_ledger',
        'description': 'Delete general ledger entries'
    },
    'finance.ap.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'accounts_payable',
        'description': 'View accounts payable'
    },
    'finance.ap.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'accounts_payable',
        'description': 'Create accounts payable entries'
    },
    'finance.ap.update': {
        'module': 'finance',
        'action': 'update',
        'resource': 'accounts_payable',
        'description': 'Update accounts payable entries'
    },
    'finance.ap.delete': {
        'module': 'finance',
        'action': 'delete',
        'resource': 'accounts_payable',
        'description': 'Delete accounts payable entries'
    },
    'finance.ar.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'accounts_receivable',
        'description': 'View accounts receivable'
    },
    'finance.ar.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'accounts_receivable',
        'description': 'Create accounts receivable entries'
    },
    'finance.ar.update': {
        'module': 'finance',
        'action': 'update',
        'resource': 'accounts_receivable',
        'description': 'Update accounts receivable entries'
    },
    'finance.ar.delete': {
        'module': 'finance',
        'action': 'delete',
        'resource': 'accounts_receivable',
        'description': 'Delete accounts receivable entries'
    },
    'finance.reports.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'reports',
        'description': 'View financial reports'
    },
    'finance.reports.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'reports',
        'description': 'Create financial reports'
    },
    'finance.reconciliation.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'reconciliation',
        'description': 'View bank reconciliation sessions'
    },
    'finance.reconciliation.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'reconciliation',
        'description': 'Create bank reconciliation sessions'
    },
    'finance.reconciliation.update': {
        'module': 'finance',
        'action': 'update',
        'resource': 'reconciliation',
        'description': 'Update bank reconciliation sessions'
    },
    'finance.reconciliation.delete': {
        'module': 'finance',
        'action': 'delete',
        'resource': 'reconciliation',
        'description': 'Delete bank reconciliation sessions'
    },
    'finance.assets.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'assets',
        'description': 'View fixed assets'
    },
    'finance.assets.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'assets',
        'description': 'Create fixed asset records'
    },
    'finance.assets.update': {
        'module': 'finance',
        'action': 'update',
        'resource': 'assets',
        'description': 'Update fixed asset records'
    },
    'finance.assets.delete': {
        'module': 'finance',
        'action': 'delete',
        'resource': 'assets',
        'description': 'Delete fixed asset records'
    },
    'finance.budgets.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'budgets',
        'description': 'View budgets'
    },
    'finance.budgets.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'budgets',
        'description': 'Create budgets'
    },
    'finance.budgets.update': {
        'module': 'finance',
        'action': 'update',
        'resource': 'budgets',
        'description': 'Update budgets'
    },
    'finance.budgets.delete': {
        'module': 'finance',
        'action': 'delete',
        'resource': 'budgets',
        'description': 'Delete budgets'
    },
    'finance.tax.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'tax',
        'description': 'View tax settings and calculations'
    },
    'finance.tax.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'tax',
        'description': 'Create tax settings'
    },
    'finance.tax.update': {
        'module': 'finance',
        'action': 'update',
        'resource': 'tax',
        'description': 'Update tax settings'
    },
    'finance.tax.delete': {
        'module': 'finance',
        'action': 'delete',
        'resource': 'tax',
        'description': 'Delete tax settings'
    },
    'finance.currency.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'currency',
        'description': 'View currency settings and exchange rates'
    },
    'finance.currency.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'currency',
        'description': 'Create currency settings'
    },
    'finance.payments.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'payments',
        'description': 'View payment records'
    },
    'finance.payments.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'payments',
        'description': 'Create payment records'
    },
    'finance.vendors.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'vendors',
        'description': 'View vendor information'
    },
    'finance.vendors.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'vendors',
        'description': 'Create vendor records'
    },
    'finance.customers.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'customers',
        'description': 'View customer information'
    },
    'finance.customers.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'customers',
        'description': 'Create customer records'
    },
    'finance.invoices.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'invoices',
        'description': 'View invoices'
    },
    'finance.invoices.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'invoices',
        'description': 'Create invoices'
    },
    'finance.settings.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'settings',
        'description': 'View finance module settings'
    },
    'finance.settings.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'settings',
        'description': 'Create finance module settings'
    },
    'finance.workflows.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'workflows',
        'description': 'View finance workflows'
    },
    'finance.workflows.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'workflows',
        'description': 'Create finance workflows'
    },
    'finance.audit.read': {
        'module': 'finance',
        'action': 'read',
        'resource': 'audit',
        'description': 'View finance audit logs'
    },
    'finance.audit.create': {
        'module': 'finance',
        'action': 'create',
        'resource': 'audit',
        'description': 'Create finance audit entries'
    },
    
    # CRM permissions
    'crm.contacts.read': {
        'module': 'crm',
        'action': 'read',
        'resource': 'contacts',
        'description': 'View contacts'
    },
    'crm.contacts.create': {
        'module': 'crm',
        'action': 'create',
        'resource': 'contacts',
        'description': 'Create contacts'
    },
    'crm.contacts.update': {
        'module': 'crm',
        'action': 'update',
        'resource': 'contacts',
        'description': 'Update contacts'
    },
    'crm.contacts.delete': {
        'module': 'crm',
        'action': 'delete',
        'resource': 'contacts',
        'description': 'Delete contacts'
    },
    'crm.leads.read': {
        'module': 'crm',
        'action': 'read',
        'resource': 'leads',
        'description': 'View leads'
    },
    'crm.leads.create': {
        'module': 'crm',
        'action': 'create',
        'resource': 'leads',
        'description': 'Create leads'
    },
    'crm.leads.update': {
        'module': 'crm',
        'action': 'update',
        'resource': 'leads',
        'description': 'Update leads'
    },
    'crm.leads.delete': {
        'module': 'crm',
        'action': 'delete',
        'resource': 'leads',
        'description': 'Delete leads'
    },
    'crm.opportunities.read': {
        'module': 'crm',
        'action': 'read',
        'resource': 'opportunities',
        'description': 'View opportunities'
    },
    'crm.opportunities.create': {
        'module': 'crm',
        'action': 'create',
        'resource': 'opportunities',
        'description': 'Create opportunities'
    },
    'crm.opportunities.update': {
        'module': 'crm',
        'action': 'update',
        'resource': 'opportunities',
        'description': 'Update opportunities'
    },
    'crm.opportunities.delete': {
        'module': 'crm',
        'action': 'delete',
        'resource': 'opportunities',
        'description': 'Delete opportunities'
    },
    'crm.tickets.read': {
        'module': 'crm',
        'action': 'read',
        'resource': 'tickets',
        'description': 'View support tickets'
    },
    'crm.tickets.create': {
        'module': 'crm',
        'action': 'create',
        'resource': 'tickets',
        'description': 'Create support tickets'
    },
    'crm.tickets.update': {
        'module': 'crm',
        'action': 'update',
        'resource': 'tickets',
        'description': 'Update support tickets'
    },
    'crm.tickets.delete': {
        'module': 'crm',
        'action': 'delete',
        'resource': 'tickets',
        'description': 'Delete support tickets'
    },
    'crm.companies.read': {
        'module': 'crm',
        'action': 'read',
        'resource': 'companies',
        'description': 'View companies'
    },
    'crm.companies.create': {
        'module': 'crm',
        'action': 'create',
        'resource': 'companies',
        'description': 'Create companies'
    },
    'crm.companies.update': {
        'module': 'crm',
        'action': 'update',
        'resource': 'companies',
        'description': 'Update companies'
    },
    'crm.companies.delete': {
        'module': 'crm',
        'action': 'delete',
        'resource': 'companies',
        'description': 'Delete companies'
    },
    'crm.activities.read': {
        'module': 'crm',
        'action': 'read',
        'resource': 'activities',
        'description': 'View activities'
    },
    'crm.activities.create': {
        'module': 'crm',
        'action': 'create',
        'resource': 'activities',
        'description': 'Create activities'
    },
    'crm.activities.update': {
        'module': 'crm',
        'action': 'update',
        'resource': 'activities',
        'description': 'Update activities'
    },
    'crm.activities.delete': {
        'module': 'crm',
        'action': 'delete',
        'resource': 'activities',
        'description': 'Delete activities'
    },
    'crm.tasks.read': {
        'module': 'crm',
        'action': 'read',
        'resource': 'tasks',
        'description': 'View tasks'
    },
    'crm.tasks.create': {
        'module': 'crm',
        'action': 'create',
        'resource': 'tasks',
        'description': 'Create tasks'
    },
    'crm.tasks.update': {
        'module': 'crm',
        'action': 'update',
        'resource': 'tasks',
        'description': 'Update tasks'
    },
    'crm.tasks.delete': {
        'module': 'crm',
        'action': 'delete',
        'resource': 'tasks',
        'description': 'Delete tasks'
    },
    'crm.reports.read': {
        'module': 'crm',
        'action': 'read',
        'resource': 'reports',
        'description': 'View CRM reports'
    },
    'crm.automations.read': {
        'module': 'crm',
        'action': 'read',
        'resource': 'automations',
        'description': 'View CRM automations'
    },
    'crm.automations.create': {
        'module': 'crm',
        'action': 'create',
        'resource': 'automations',
        'description': 'Create CRM automations'
    },
    
    # Inventory permissions
    'inventory.products.read': {
        'module': 'inventory',
        'action': 'read',
        'resource': 'products',
        'description': 'View products'
    },
    'inventory.products.create': {
        'module': 'inventory',
        'action': 'create',
        'resource': 'products',
        'description': 'Create products'
    },
    'inventory.products.update': {
        'module': 'inventory',
        'action': 'update',
        'resource': 'products',
        'description': 'Update products'
    },
    'inventory.products.delete': {
        'module': 'inventory',
        'action': 'delete',
        'resource': 'products',
        'description': 'Delete products'
    },
    'inventory.categories.read': {
        'module': 'inventory',
        'action': 'read',
        'resource': 'categories',
        'description': 'View product categories'
    },
    'inventory.categories.create': {
        'module': 'inventory',
        'action': 'create',
        'resource': 'categories',
        'description': 'Create product categories'
    },
    'inventory.categories.update': {
        'module': 'inventory',
        'action': 'update',
        'resource': 'categories',
        'description': 'Update product categories'
    },
    'inventory.categories.delete': {
        'module': 'inventory',
        'action': 'delete',
        'resource': 'categories',
        'description': 'Delete product categories'
    },
    'inventory.warehouses.read': {
        'module': 'inventory',
        'action': 'read',
        'resource': 'warehouses',
        'description': 'View warehouses'
    },
    'inventory.warehouses.create': {
        'module': 'inventory',
        'action': 'create',
        'resource': 'warehouses',
        'description': 'Create warehouses'
    },
    'inventory.warehouses.update': {
        'module': 'inventory',
        'action': 'update',
        'resource': 'warehouses',
        'description': 'Update warehouses'
    },
    'inventory.warehouses.delete': {
        'module': 'inventory',
        'action': 'delete',
        'resource': 'warehouses',
        'description': 'Delete warehouses'
    },
    'inventory.stock.read': {
        'module': 'inventory',
        'action': 'read',
        'resource': 'stock',
        'description': 'View stock levels'
    },
    'inventory.stock.create': {
        'module': 'inventory',
        'action': 'create',
        'resource': 'stock',
        'description': 'Create stock adjustments'
    },
    'inventory.stock.update': {
        'module': 'inventory',
        'action': 'update',
        'resource': 'stock',
        'description': 'Update stock levels'
    },
    'inventory.transactions.read': {
        'module': 'inventory',
        'action': 'read',
        'resource': 'transactions',
        'description': 'View inventory transactions'
    },
    'inventory.transactions.create': {
        'module': 'inventory',
        'action': 'create',
        'resource': 'transactions',
        'description': 'Create inventory transactions'
    },
    'inventory.reports.read': {
        'module': 'inventory',
        'action': 'read',
        'resource': 'reports',
        'description': 'View inventory reports'
    },
    'inventory.settings.read': {
        'module': 'inventory',
        'action': 'read',
        'resource': 'settings',
        'description': 'View inventory settings'
    },
    'inventory.settings.update': {
        'module': 'inventory',
        'action': 'update',
        'resource': 'settings',
        'description': 'Update inventory settings'
    },
    
    # Procurement permissions
    'procurement.vendors.read': {
        'module': 'procurement',
        'action': 'read',
        'resource': 'vendors',
        'description': 'View vendors'
    },
    'procurement.vendors.create': {
        'module': 'procurement',
        'action': 'create',
        'resource': 'vendors',
        'description': 'Create vendors'
    },
    'procurement.vendors.update': {
        'module': 'procurement',
        'action': 'update',
        'resource': 'vendors',
        'description': 'Update vendors'
    },
    'procurement.vendors.delete': {
        'module': 'procurement',
        'action': 'delete',
        'resource': 'vendors',
        'description': 'Delete vendors'
    },
    'procurement.purchase_orders.read': {
        'module': 'procurement',
        'action': 'read',
        'resource': 'purchase_orders',
        'description': 'View purchase orders'
    },
    'procurement.purchase_orders.create': {
        'module': 'procurement',
        'action': 'create',
        'resource': 'purchase_orders',
        'description': 'Create purchase orders'
    },
    'procurement.purchase_orders.update': {
        'module': 'procurement',
        'action': 'update',
        'resource': 'purchase_orders',
        'description': 'Update purchase orders'
    },
    'procurement.purchase_orders.delete': {
        'module': 'procurement',
        'action': 'delete',
        'resource': 'purchase_orders',
        'description': 'Delete purchase orders'
    },
    'procurement.receiving.read': {
        'module': 'procurement',
        'action': 'read',
        'resource': 'receiving',
        'description': 'View receiving records'
    },
    'procurement.receiving.create': {
        'module': 'procurement',
        'action': 'create',
        'resource': 'receiving',
        'description': 'Create receiving records'
    },
    'procurement.invoicing.read': {
        'module': 'procurement',
        'action': 'read',
        'resource': 'invoicing',
        'description': 'View procurement invoices'
    },
    'procurement.invoicing.create': {
        'module': 'procurement',
        'action': 'create',
        'resource': 'invoicing',
        'description': 'Create procurement invoices'
    },
    'procurement.contracts.read': {
        'module': 'procurement',
        'action': 'read',
        'resource': 'contracts',
        'description': 'View contracts'
    },
    'procurement.contracts.create': {
        'module': 'procurement',
        'action': 'create',
        'resource': 'contracts',
        'description': 'Create contracts'
    },
    'procurement.contracts.update': {
        'module': 'procurement',
        'action': 'update',
        'resource': 'contracts',
        'description': 'Update contracts'
    },
    'procurement.contracts.delete': {
        'module': 'procurement',
        'action': 'delete',
        'resource': 'contracts',
        'description': 'Delete contracts'
    },
    'procurement.integration.read': {
        'module': 'procurement',
        'action': 'read',
        'resource': 'integration',
        'description': 'View procurement integration settings'
    },
    'procurement.reports.read': {
        'module': 'procurement',
        'action': 'read',
        'resource': 'reports',
        'description': 'View procurement reports'
    },
    
    # HR permissions
    'hr.employees.read': {
        'module': 'hr',
        'action': 'read',
        'resource': 'employees',
        'description': 'View employees'
    },
    'hr.employees.create': {
        'module': 'hr',
        'action': 'create',
        'resource': 'employees',
        'description': 'Create employee records'
    },
    'hr.employees.update': {
        'module': 'hr',
        'action': 'update',
        'resource': 'employees',
        'description': 'Update employee records'
    },
    'hr.employees.delete': {
        'module': 'hr',
        'action': 'delete',
        'resource': 'employees',
        'description': 'Delete employee records'
    },
    'hr.payroll.read': {
        'module': 'hr',
        'action': 'read',
        'resource': 'payroll',
        'description': 'View payroll information'
    },
    'hr.payroll.create': {
        'module': 'hr',
        'action': 'create',
        'resource': 'payroll',
        'description': 'Create payroll records'
    },
    'hr.payroll.update': {
        'module': 'hr',
        'action': 'update',
        'resource': 'payroll',
        'description': 'Update payroll records'
    },
    'hr.recruitment.read': {
        'module': 'hr',
        'action': 'read',
        'resource': 'recruitment',
        'description': 'View recruitment information'
    },
    'hr.recruitment.create': {
        'module': 'hr',
        'action': 'create',
        'resource': 'recruitment',
        'description': 'Create recruitment records'
    },
    'hr.benefits.read': {
        'module': 'hr',
        'action': 'read',
        'resource': 'benefits',
        'description': 'View benefits information'
    },
    'hr.benefits.create': {
        'module': 'hr',
        'action': 'create',
        'resource': 'benefits',
        'description': 'Create benefits records'
    },
    'hr.benefits.update': {
        'module': 'hr',
        'action': 'update',
        'resource': 'benefits',
        'description': 'Update benefits records'
    },
    'hr.time_tracking.read': {
        'module': 'hr',
        'action': 'read',
        'resource': 'time_tracking',
        'description': 'View time tracking records'
    },
    'hr.time_tracking.create': {
        'module': 'hr',
        'action': 'create',
        'resource': 'time_tracking',
        'description': 'Create time tracking records'
    },
    'hr.reports.read': {
        'module': 'hr',
        'action': 'read',
        'resource': 'reports',
        'description': 'View HR reports'
    },
    
    # Analytics permissions
    'analytics.dashboards.read': {
        'module': 'analytics',
        'action': 'read',
        'resource': 'dashboards',
        'description': 'View analytics dashboards'
    },
    'analytics.dashboards.create': {
        'module': 'analytics',
        'action': 'create',
        'resource': 'dashboards',
        'description': 'Create analytics dashboards'
    },
    'analytics.dashboards.update': {
        'module': 'analytics',
        'action': 'update',
        'resource': 'dashboards',
        'description': 'Update analytics dashboards'
    },
    'analytics.dashboards.delete': {
        'module': 'analytics',
        'action': 'delete',
        'resource': 'dashboards',
        'description': 'Delete analytics dashboards'
    },
    'analytics.reports.read': {
        'module': 'analytics',
        'action': 'read',
        'resource': 'reports',
        'description': 'View analytics reports'
    },
    'analytics.reports.create': {
        'module': 'analytics',
        'action': 'create',
        'resource': 'reports',
        'description': 'Create analytics reports'
    },
    'analytics.kpis.read': {
        'module': 'analytics',
        'action': 'read',
        'resource': 'kpis',
        'description': 'View KPIs'
    },
    'analytics.kpis.create': {
        'module': 'analytics',
        'action': 'create',
        'resource': 'kpis',
        'description': 'Create KPIs'
    },
    'analytics.kpis.update': {
        'module': 'analytics',
        'action': 'update',
        'resource': 'kpis',
        'description': 'Update KPIs'
    },
    'analytics.forecasting.read': {
        'module': 'analytics',
        'action': 'read',
        'resource': 'forecasting',
        'description': 'View forecasting data'
    },
    'analytics.forecasting.create': {
        'module': 'analytics',
        'action': 'create',
        'resource': 'forecasting',
        'description': 'Create forecasting models'
    },
    'analytics.visualization.read': {
        'module': 'analytics',
        'action': 'read',
        'resource': 'visualization',
        'description': 'View data visualizations'
    },
    'analytics.visualization.create': {
        'module': 'analytics',
        'action': 'create',
        'resource': 'visualization',
        'description': 'Create data visualizations'
    },
}

def get_module_permissions(module_id):
    """
    Get list of permissions for a module
    
    SECURITY: Input validation - only allow known module IDs
    """
    if module_id not in MODULE_PERMISSION_MAPPINGS:
        return []
    return MODULE_PERMISSION_MAPPINGS[module_id]

def get_all_permissions():
    """
    Get all permission definitions
    
    Returns: dict of permission_name -> permission_definition
    """
    return PERMISSION_DEFINITIONS

def validate_module_id(module_id):
    """
    Validate that module_id is a known module
    
    SECURITY: Prevents injection attacks by only allowing known modules
    """
    return module_id in MODULE_PERMISSION_MAPPINGS

