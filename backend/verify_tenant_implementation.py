"""
Comprehensive Verification: Check all models for tenant_id and audit columns
"""

import sys
import os
import ast
import importlib.util
from pathlib import Path

# Models that should have tenant_id (company-wide data)
COMPANY_WIDE_MODELS = {
    # Finance
    'Account', 'JournalEntry', 'ChartOfAccounts', 'GeneralLedgerEntry', 
    'JournalHeader', 'CompanySettings', 'AccountsPayable', 'AccountsReceivable',
    'BankReconciliation', 'FinancialPeriod', 'TaxRecord', 'InvoiceLineItem',
    'FixedAsset', 'BudgetEntry', 'DepreciationSchedule', 'MaintenanceRecord',
    'APPayment', 'ARPayment', 'BankTransaction', 'BankStatement', 'FinancialReport',
    'KPI', 'PaymentMethod', 'BankAccount', 'PaymentTransaction', 'PartialPayment',
    'ReconciliationSession', 'AccountingPeriod', 'Currency', 'ExchangeRate',
    'CurrencyConversion', 'CostCenter', 'Department', 'Project', 'CostAllocation',
    'CostAllocationDetail',
    
    # Sales
    'Customer', 'Invoice', 'Payment', 'CustomerCommunication',
    
    # Procurement
    'Vendor', 'PurchaseOrder', 'PurchaseOrderItem', 'RFQ', 'RFQItem',
    'RFQInvitation', 'RFQResponse', 'RFQResponseItem', 'Contract', 'ContractDocument',
    'VendorDocument', 'VendorCommunication',
    
    # Inventory
    'Product', 'Category', 'Warehouse', 'BasicInventoryTransaction', 'StockMovement',
    'InventoryLevel', 'InventoryProduct', 'InventoryTransaction', 'InventoryUOM',
    'InventoryUOMConversion', 'ProductCategory', 'InventoryLocation', 'InventoryZone',
    'InventoryAisle', 'InventoryRack', 'InventoryLotBatch', 'InventorySerialNumber',
    'InventoryValuationSnapshot', 'InventoryAdjustmentEntry', 'InventoryCostLayer',
    'CostLayerTransaction', 'InventoryWarehouseActivity', 'InventoryStockLevel',
    'InventoryAdvancedLocation', 'InventoryAdvancedWarehouse', 'InventoryProductVariant',
    'InventoryPickerPerformance', 'DailyInventoryBalance', 'DailyInventoryTransactionSummary',
    'InventoryBasicLocation', 'InventorySimpleWarehouse', 'InventoryProductCategories',
    'InventorySuppliers', 'InventoryCustomers', 'InventoryAuditTrail', 'InventoryReports',
    'DailyInventoryCycleStatus', 'DailyInventoryCycleAuditLogs', 'InventorySystemConfig',
    
    # CRM
    'Contact', 'Company', 'Lead', 'Opportunity', 'Ticket', 'Communication', 'FollowUp',
    'TimeEntry', 'BehavioralEvent', 'LeadIntake', 'KnowledgeBaseArticle',
    'KnowledgeBaseAttachment', 'Pipeline',
    
    # Manufacturing
    'BillOfMaterials', 'BOMItem', 'ProductionOrder', 'WorkCenter', 'ProductionOperation',
    'MaterialRequirementsPlan', 'SupplyChainNode', 'SupplyChainLink', 'QualityControl',
    'MaintenanceSchedule', 'Equipment',
    
    # Workflow
    'WorkflowRule', 'WorkflowTemplate', 'WorkflowExecution', 'WorkflowAction',
    
    # Settings
    'SystemSetting',
}

# Models that are user-specific (should NOT have tenant_id)
USER_SPECIFIC_MODELS = {
    'User', 'UserPreferences', 'UserSession', 'PasswordHistory', 'AccountLockout',
    'TwoFactorAuth', 'Dashboard', 'DashboardWidget', 'WidgetTemplate', 'DashboardTemplate',
    'UserModules', 'AuditLog', 'LoginHistory', 'PermissionChange', 'SystemEvent',
}

# Models that are system/global (may or may not need tenant_id)
SYSTEM_MODELS = {
    'Role', 'Permission', 'RolePermission', 'PermissionChange', 'Tenant', 'UserTenant',
    'TenantModule', 'TenantSettings', 'SecurityPolicy', 'SecurityEvent',
}

def check_model_file(file_path):
    """Check a single model file for tenant_id and created_by"""
    results = {
        'file': str(file_path),
        'models': [],
        'has_tenant_id': [],
        'missing_tenant_id': [],
        'has_audit': [],
        'missing_audit': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file
        tree = ast.parse(content, filename=str(file_path))
        
        # Find all class definitions that inherit from db.Model
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from db.Model
                bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
                if 'Model' in bases or any('Model' in str(base) for base in node.bases):
                    model_name = node.name
                    results['models'].append(model_name)
                    
                    # Check for tenant_id and audit columns
                    has_tenant_id = False
                    has_created_by = False
                    has_last_modified_by = False
                    
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if 'tenant_id' in target.id.lower():
                                        has_tenant_id = True
                                    if 'created_by' in target.id.lower():
                                        has_created_by = True
                                    if 'last_modified_by' in target.id.lower():
                                        has_last_modified_by = True
                    
                    # Determine if this model should have tenant_id
                    should_have_tenant = model_name in COMPANY_WIDE_MODELS
                    should_not_have_tenant = model_name in USER_SPECIFIC_MODELS
                    is_system = model_name in SYSTEM_MODELS
                    
                    if should_have_tenant:
                        if has_tenant_id:
                            results['has_tenant_id'].append(model_name)
                        else:
                            results['missing_tenant_id'].append(model_name)
                        
                        if has_created_by or has_last_modified_by:
                            results['has_audit'].append(model_name)
                        else:
                            results['missing_audit'].append(model_name)
                    elif should_not_have_tenant:
                        # User-specific models shouldn't have tenant_id
                        if has_tenant_id:
                            results['has_tenant_id'].append(f"{model_name} (SHOULD NOT HAVE)")
                    # System models are optional
                    
    except Exception as e:
        results['error'] = str(e)
    
    return results

def verify_all_models():
    """Verify all models across all modules"""
    print("🔍 VERIFYING TENANT_ID IMPLEMENTATION ACROSS ALL MODULES")
    print("=" * 70)
    
    modules_dir = Path('backend/modules')
    all_results = []
    
    # Find all model files
    model_files = list(modules_dir.rglob('models.py'))
    
    for model_file in sorted(model_files):
        print(f"\n📁 Checking: {model_file.relative_to('backend')}")
        result = check_model_file(model_file)
        all_results.append(result)
        
        if result.get('error'):
            print(f"   ❌ Error: {result['error']}")
            continue
        
        if result['models']:
            print(f"   📋 Found {len(result['models'])} models: {', '.join(result['models'])}")
        
        if result['missing_tenant_id']:
            print(f"   ⚠️  Missing tenant_id: {', '.join(result['missing_tenant_id'])}")
        
        if result['missing_audit']:
            print(f"   ⚠️  Missing audit columns: {', '.join(result['missing_audit'])}")
        
        if result['has_tenant_id'] and not result['missing_tenant_id']:
            print(f"   ✅ All company-wide models have tenant_id")
        
        if result['has_audit'] and not result['missing_audit']:
            print(f"   ✅ All company-wide models have audit columns")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    total_missing_tenant = sum(len(r['missing_tenant_id']) for r in all_results)
    total_missing_audit = sum(len(r['missing_audit']) for r in all_results)
    total_has_tenant = sum(len(r['has_tenant_id']) for r in all_results)
    total_has_audit = sum(len(r['has_audit']) for r in all_results)
    
    print(f"✅ Models with tenant_id: {total_has_tenant}")
    print(f"⚠️  Models missing tenant_id: {total_missing_tenant}")
    print(f"✅ Models with audit columns: {total_has_audit}")
    print(f"⚠️  Models missing audit columns: {total_missing_audit}")
    
    if total_missing_tenant == 0 and total_missing_audit == 0:
        print("\n🎉 ALL MODELS PROPERLY IMPLEMENTED!")
    else:
        print("\n⚠️  SOME MODELS NEED UPDATES:")
        for result in all_results:
            if result['missing_tenant_id'] or result['missing_audit']:
                print(f"\n   📁 {result['file']}")
                if result['missing_tenant_id']:
                    print(f"      Missing tenant_id: {', '.join(result['missing_tenant_id'])}")
                if result['missing_audit']:
                    print(f"      Missing audit: {', '.join(result['missing_audit'])}")
    
    return all_results

if __name__ == "__main__":
    verify_all_models()



