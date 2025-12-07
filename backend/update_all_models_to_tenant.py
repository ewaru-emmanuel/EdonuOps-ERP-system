"""
Comprehensive Update: Add tenant_id to all company-wide models
This script updates model files to replace user_id with tenant_id + created_by
"""

import re
from pathlib import Path

# Files to update with their models
FILES_TO_UPDATE = {
    'modules/finance/advanced_models.py': [
        'ChartOfAccounts', 'GeneralLedgerEntry', 'JournalHeader', 'CompanySettings',
        'AccountsPayable', 'AccountsReceivable', 'BankReconciliation', 'FinancialPeriod',
        'TaxRecord', 'InvoiceLineItem', 'FixedAsset', 'BudgetEntry', 'DepreciationSchedule',
        'MaintenanceRecord', 'APPayment', 'ARPayment', 'BankTransaction', 'BankStatement',
        'FinancialReport', 'KPI', 'PostingRule'
    ],
    'modules/finance/currency_models.py': [
        'Currency', 'ExchangeRate', 'CurrencyConversion'
    ],
    'modules/finance/cost_center_models.py': [
        'CostCenter', 'Department', 'Project', 'CostAllocation', 'CostAllocationDetail'
    ],
    'modules/finance/payment_models.py': [
        'PaymentMethod', 'BankAccount', 'PaymentTransaction', 'PartialPayment',
        'ReconciliationSession', 'AccountingPeriod'
    ],
    'modules/crm/models.py': [
        'Contact', 'Company', 'Lead', 'Opportunity', 'Ticket', 'Communication',
        'FollowUp', 'TimeEntry', 'BehavioralEvent', 'LeadIntake', 'KnowledgeBaseArticle',
        'KnowledgeBaseAttachment', 'Pipeline'
    ],
    'modules/manufacturing/models.py': [
        'BillOfMaterials', 'BOMItem', 'ProductionOrder', 'WorkCenter', 'ProductionOperation',
        'MaterialRequirementsPlan', 'SupplyChainNode', 'SupplyChainLink', 'QualityControl',
        'MaintenanceSchedule', 'Equipment'
    ],
    'modules/workflow/models.py': [
        'WorkflowRule', 'WorkflowTemplate', 'WorkflowExecution', 'WorkflowAction'
    ],
    'modules/dashboard/models.py': [
        'WidgetTemplate', 'DashboardTemplate'  # Dashboard and DashboardWidget are user-specific
    ],
}

def update_model_file(file_path, models_to_update):
    """Update a model file to add tenant_id and created_by"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: Replace user_id = db.Column(...) with tenant_id + created_by
        # For models that should be company-wide
        for model_name in models_to_update:
            # Find the class definition
            pattern = rf'(class {model_name}\(db\.Model\):.*?)(    user_id = db\.Column\([^)]+\)[^\n]*)'
            
            def replace_user_id(match):
                class_def = match.group(1)
                user_id_line = match.group(2)
                
                # Replace user_id with tenant_id + created_by
                replacement = f"""{class_def}    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)"""
                
                return replacement
            
            content = re.sub(pattern, replace_user_id, content, flags=re.DOTALL)
            
            # Also handle Column(...) syntax (for cost_center_models.py)
            pattern2 = rf'(class {model_name}\(db\.Model\):.*?)(    user_id = Column\([^)]+\)[^\n]*)'
            
            def replace_user_id_column(match):
                class_def = match.group(1)
                user_id_line = match.group(2)
                
                replacement = f"""{class_def}    tenant_id = Column(String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)  # User who created (audit trail)"""
                
                return replacement
            
            content = re.sub(pattern2, replace_user_id_column, content, flags=re.DOTALL)
        
        # Pattern 2: Add tenant_id + created_by to models that don't have user_id but should
        # This is for models like ChartOfAccounts, BillOfMaterials, etc. that don't have any user_id
        for model_name in models_to_update:
            # Check if model already has tenant_id
            if f'class {model_name}' in content:
                if f'{model_name}' in content and 'tenant_id' not in content[content.find(f'class {model_name}'):content.find(f'class {model_name}') + 2000]:
                    # Find the created_at line and add tenant_id before it
                    pattern = rf'(class {model_name}\(db\.Model\):.*?)(    created_at = [^\n]+)'
                    
                    def add_tenant_id(match):
                        class_def = match.group(1)
                        created_at_line = match.group(2)
                        
                        replacement = f"""{class_def}    tenant_id = db.Column(db.String(50), nullable=False, index=True)  # Company/tenant identifier - company-wide
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User who created (audit trail)
{created_at_line}"""
                        
                        return replacement
                    
                    content = re.sub(pattern, add_tenant_id, content, flags=re.DOTALL)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"   ❌ Error updating {file_path}: {e}")
        return False

def update_all_models():
    """Update all model files"""
    print("🚀 UPDATING ALL MODELS TO USE TENANT_ID")
    print("=" * 70)
    
    updated_count = 0
    
    for file_path, models in FILES_TO_UPDATE.items():
        path = Path(file_path)
        if not path.exists():
            print(f"   ⏭️  File not found: {file_path}")
            continue
        
        print(f"\n📁 Updating: {path.name}")
        print(f"   Models: {', '.join(models)}")
        
        if update_model_file(file_path, models):
            print(f"   ✅ Updated {len(models)} models")
            updated_count += len(models)
        else:
            print(f"   ⏭️  No changes needed (or already updated)")
    
    print(f"\n✅ COMPLETE! Updated {updated_count} models across {len(FILES_TO_UPDATE)} files")
    return updated_count

if __name__ == "__main__":
    update_all_models()

