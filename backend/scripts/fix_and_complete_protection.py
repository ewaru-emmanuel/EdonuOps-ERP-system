"""
Fix permission names and complete route protection to 100%
"""

import re
from pathlib import Path

# Permission mapping based on route patterns
PERMISSION_MAP = {
    # Finance Advanced Routes
    r'/general-ledger.*GET': 'finance.journal.read',
    r'/general-ledger.*POST': 'finance.journal.create',
    r'/general-ledger.*PUT': 'finance.journal.update',
    r'/general-ledger.*DELETE': 'finance.journal.delete',
    r'/accounts-payable.*GET': 'finance.ap.read',
    r'/accounts-payable.*POST': 'finance.ap.create',
    r'/accounts-payable.*PUT': 'finance.ap.update',
    r'/accounts-payable.*DELETE': 'finance.ap.delete',
    r'/accounts-receivable.*GET': 'finance.ar.read',
    r'/accounts-receivable.*POST': 'finance.ar.create',
    r'/accounts-receivable.*PUT': 'finance.ar.update',
    r'/accounts-receivable.*DELETE': 'finance.ar.delete',
    r'/fixed-assets.*GET': 'finance.assets.read',
    r'/fixed-assets.*POST': 'finance.assets.create',
    r'/fixed-assets.*PUT': 'finance.assets.update',
    r'/fixed-assets.*DELETE': 'finance.assets.delete',
    r'/budgets.*GET': 'finance.budgets.read',
    r'/budgets.*POST': 'finance.budgets.create',
    r'/budgets.*PUT': 'finance.budgets.update',
    r'/budgets.*DELETE': 'finance.budgets.delete',
    r'/tax-records.*GET': 'finance.tax.read',
    r'/tax-records.*POST': 'finance.tax.create',
    r'/tax-records.*PUT': 'finance.tax.update',
    r'/tax-records.*DELETE': 'finance.tax.delete',
    r'/bank-reconciliations.*GET': 'finance.reconciliation.read',
    r'/bank-reconciliations.*POST': 'finance.reconciliation.create',
    r'/bank-reconciliations.*PUT': 'finance.reconciliation.update',
    r'/bank-reconciliations.*DELETE': 'finance.reconciliation.delete',
    r'/reports/.*GET': 'finance.reports.read',
    r'/maintenance-records.*GET': 'finance.assets.read',
    r'/maintenance-records.*POST': 'finance.assets.update',
    r'/maintenance-records.*PUT': 'finance.assets.update',
    r'/maintenance-records.*DELETE': 'finance.assets.delete',
    r'/accounts.*GET': 'finance.accounts.read',
    r'/accounts.*POST': 'finance.accounts.create',
    r'/journal-entries.*GET': 'finance.journal.read',
    r'/vendors.*GET': 'finance.vendors.read',
    r'/vendors.*POST': 'finance.vendors.create',
    r'/customers.*GET': 'finance.customers.read',
    r'/customers.*POST': 'finance.customers.create',
    r'/ap-payments.*GET': 'finance.payments.read',
    r'/ap-payments.*POST': 'finance.payments.create',
    r'/ar-payments.*GET': 'finance.payments.read',
    r'/ar-payments.*POST': 'finance.payments.create',
    r'/currencies.*GET': 'finance.currency.read',
    r'/currencies.*POST': 'finance.currency.create',
    r'/exchange-rates.*GET': 'finance.currency.read',
    r'/exchange-rates.*POST': 'finance.currency.create',
    r'/audit-trail.*GET': 'finance.audit.read',
    r'/depreciation-schedules.*GET': 'finance.assets.read',
    r'/depreciation-schedules.*POST': 'finance.assets.create',
    r'/invoice-line-items.*GET': 'finance.invoices.read',
    r'/invoice-line-items.*POST': 'finance.invoices.create',
    r'/financial-periods.*GET': 'finance.settings.read',
    r'/financial-periods.*POST': 'finance.settings.create',
    r'/tax-filing-history.*GET': 'finance.tax.read',
    r'/tax-filing-history.*POST': 'finance.tax.create',
    r'/compliance-reports.*GET': 'finance.reports.read',
    r'/compliance-reports.*POST': 'finance.reports.create',
    r'/user-activity.*GET': 'finance.audit.read',
    r'/user-activity.*POST': 'finance.audit.create',
    r'/bank-statements.*GET': 'finance.reconciliation.read',
    r'/bank-statements.*POST': 'finance.reconciliation.create',
    r'/ledger-entries.*GET': 'finance.journal.read',
    r'/profit-loss.*GET': 'finance.reports.read',
    r'/balance-sheet.*GET': 'finance.reports.read',
    r'/cash-flow.*GET': 'finance.reports.read',
    r'/kpis.*GET': 'finance.reports.read',
    r'/kpis.*POST': 'finance.reports.create',
    r'/dashboard-metrics.*GET': 'finance.reports.read',
    r'/financial-reports.*GET': 'finance.reports.read',
    r'/workflows/.*GET': 'finance.workflows.read',
    r'/workflows/.*POST': 'finance.workflows.create',
    r'/settings/.*GET': 'finance.settings.read',
    r'/settings/.*POST': 'finance.settings.update',
    r'/ai/.*GET': 'finance.reports.read',
    r'/summary.*GET': 'finance.reports.read',
    
    # Inventory Advanced Routes
    r'/uom.*GET': 'inventory.settings.read',
    r'/uom.*POST': 'inventory.settings.create',
    r'/uom.*PUT': 'inventory.settings.update',
    r'/uom.*DELETE': 'inventory.settings.delete',
    r'/uom-conversions.*GET': 'inventory.settings.read',
    r'/uom-conversions.*POST': 'inventory.settings.create',
    r'/categories.*GET': 'inventory.categories.read',
    r'/categories.*POST': 'inventory.categories.create',
    r'/categories.*PUT': 'inventory.categories.update',
    r'/categories.*DELETE': 'inventory.categories.delete',
    r'/products.*GET': 'inventory.products.read',
    r'/products.*POST': 'inventory.products.create',
    r'/products.*PUT': 'inventory.products.update',
    r'/products.*DELETE': 'inventory.products.delete',
    r'/stock-levels.*GET': 'inventory.stock.read',
    r'/stock-levels.*POST': 'inventory.stock.update',
    r'/stock-take.*POST': 'inventory.stock.update',
    r'/pick-lists.*GET': 'inventory.warehouses.read',
    r'/warehouse-activity.*GET': 'inventory.warehouses.read',
    r'/predictive-stockouts.*GET': 'inventory.reports.read',
    r'/picker-performance.*GET': 'inventory.reports.read',
    r'/warehouse-map.*GET': 'inventory.warehouses.read',
    r'/live-activity.*GET': 'inventory.warehouses.read',
    r'/warehouse-zones.*GET': 'inventory.warehouses.read',
    r'/warehouse-zones.*POST': 'inventory.warehouses.create',
    r'/warehouse-aisles.*GET': 'inventory.warehouses.read',
    r'/warehouse-aisles.*POST': 'inventory.warehouses.create',
    r'/warehouse-locations.*GET': 'inventory.warehouses.read',
    r'/warehouse-locations.*POST': 'inventory.warehouses.create',
    
    # Analytics Routes
    r'/trends.*GET': 'finance.reports.read',
    r'/account-performance.*GET': 'finance.reports.read',
    r'/discrepancy-analysis.*GET': 'finance.reports.read',
    r'/matching-efficiency.*GET': 'finance.reports.read',
    r'/optimization-recommendations.*GET': 'finance.reports.read',
    r'/performance-metrics.*GET': 'finance.reports.read',
    r'/bottlenecks.*GET': 'finance.reports.read',
    r'/cache-stats.*GET': 'finance.reports.read',
    r'/dashboard-summary.*GET': 'finance.reports.read',
    r'/export-report.*POST': 'finance.reports.read',
    r'/quick-actions.*GET': 'finance.reports.read',
    
    # Inventory Analytics
    r'/kpis.*GET': 'inventory.reports.read',
    r'/reports/stock-levels.*GET': 'inventory.reports.read',
    r'/reports/movement.*GET': 'inventory.reports.read',
    
    # Analytics Dashboard
    r'/sales_report.*GET': 'sales.reports.read',
    r'/inventory_report.*GET': 'inventory.reports.read',
}

def get_permission_for_route(route_path, method):
    """Get correct permission name for a route"""
    method_str = method.upper()
    route_key = f"{route_path}.*{method_str}"
    
    for pattern, permission in PERMISSION_MAP.items():
        if re.match(pattern, route_key):
            return permission
    
    # Default fallback
    parts = route_path.strip('/').split('/')
    parts = [p for p in parts if not p.startswith('<')]
    if parts:
        module = parts[0]
        resource = parts[-1] if len(parts) > 1 else parts[0]
        action = 'read' if method == 'GET' else 'create' if method == 'POST' else 'update' if method in ['PUT', 'PATCH'] else 'delete'
        return f'{module}.{resource}.{action}'
    
    return None

def fix_file_protection(file_path, blueprint_name):
    """Fix and complete protection for a route file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Ensure import exists
        has_import = any('from modules.core.permissions import require_permission' in line for line in lines)
        if not has_import:
            # Find first import line
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    lines.insert(i, 'from modules.core.permissions import require_permission\n')
                    break
        
        # Process routes
        i = 0
        changes = []
        while i < len(lines):
            line = lines[i]
            
            # Find route decorator
            route_match = re.search(rf'@({blueprint_name})\.route\([\'"]([^\'"]+)[\'"],\s*methods=\[([^\]]+)\]\)', line)
            if route_match:
                route_path = route_match.group(2)
                methods_str = route_match.group(3)
                methods = [m.strip().strip("'\"") for m in methods_str.split(',')]
                methods = [m for m in methods if m and m != 'OPTIONS']
                
                if methods:
                    # Check if next non-empty line is a function definition
                    j = i + 1
                    while j < len(lines) and lines[j].strip() == '':
                        j += 1
                    
                    if j < len(lines) and lines[j].strip().startswith('def '):
                        # Check if there's already a @require_permission
                        has_protection = False
                        for k in range(i + 1, j):
                            if '@require_permission' in lines[k]:
                                has_protection = True
                                # Check if permission name is wrong
                                perm_match = re.search(r"@require_permission\(['\"]([^'\"]+)['\"]\)", lines[k])
                                if perm_match:
                                    old_perm = perm_match.group(1)
                                    new_perm = get_permission_for_route(route_path, methods[0])
                                    if new_perm and old_perm != new_perm:
                                        lines[k] = re.sub(
                                            r"@require_permission\(['\"][^'\"]+['\"]\)",
                                            f"@require_permission('{new_perm}')",
                                            lines[k]
                                        )
                                        changes.append(f"Fixed: {route_path} -> {new_perm}")
                                break
                        
                        if not has_protection:
                            # Add protection
                            permission = get_permission_for_route(route_path, methods[0])
                            if permission:
                                # Insert before function definition
                                indent = len(lines[j]) - len(lines[j].lstrip())
                                decorator = ' ' * indent + f"@require_permission('{permission}')\n"
                                lines.insert(j, decorator)
                                changes.append(f"Added: {route_path} -> {permission}")
                                j += 1
            
            i += 1
        
        if changes:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"✅ {file_path.name}: {len(changes)} changes")
            for change in changes[:5]:  # Show first 5
                print(f"   {change}")
            if len(changes) > 5:
                print(f"   ... and {len(changes) - 5} more")
            return len(changes)
        else:
            print(f"⏭️  {file_path.name}: Already complete")
            return 0
            
    except Exception as e:
        print(f"❌ Error: {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    files_to_process = [
        ('modules/finance/advanced_routes.py', 'advanced_finance_bp'),
        ('modules/inventory/advanced_routes.py', 'advanced_inventory_bp'),
        ('modules/finance/analytics_routes.py', 'analytics_bp'),
        ('modules/inventory/analytics_routes.py', 'analytics_bp'),
        ('modules/analytics/dashboard.py', 'analytics_bp'),
    ]
    
    base_dir = Path(__file__).parent.parent
    total = 0
    
    for rel_path, blueprint in files_to_process:
        file_path = base_dir / rel_path
        if file_path.exists():
            total += fix_file_protection(file_path, blueprint)
        else:
            print(f"⚠️  Not found: {file_path}")
    
    print(f"\n✅ Total changes: {total}")

if __name__ == '__main__':
    main()



