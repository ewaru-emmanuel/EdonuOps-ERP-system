"""
Complete protection for remaining routes to achieve 100% coverage
"""

import re
from pathlib import Path

def add_protection_to_file(file_path, blueprint_name, route_permissions):
    """Add protection to routes in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ensure import exists
        if 'from modules.core.permissions import require_permission' not in content:
            # Find first import
            import_match = re.search(r'(from\s+flask\s+import[^\n]+\n)', content)
            if import_match:
                content = content[:import_match.end()] + 'from modules.core.permissions import require_permission\n' + content[import_match.end():]
            else:
                first_line = content.find('\n') + 1
                content = content[:first_line] + 'from modules.core.permissions import require_permission\n' + content[first_line:]
        
        changes = 0
        lines = content.split('\n')
        new_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            
            # Check for route decorator
            route_match = re.search(rf'@({blueprint_name})\.route\([\'"]([^\'"]+)[\'"],\s*methods=\[([^\]]+)\]\)', line)
            if route_match:
                route_path = route_match.group(2)
                methods_str = route_match.group(3)
                methods = [m.strip().strip("'\"") for m in methods_str.split(',')]
                methods = [m for m in methods if m and m != 'OPTIONS']
                
                if methods:
                    # Look ahead for function definition
                    j = i + 1
                    while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith('#')):
                        new_lines.append(lines[j])
                        j += 1
                    
                    if j < len(lines) and lines[j].strip().startswith('def '):
                        # Check if already protected
                        has_protection = False
                        for k in range(i + 1, j):
                            if '@require_permission' in lines[k]:
                                has_protection = True
                                break
                        
                        if not has_protection:
                            # Get permission
                            permission = route_permissions.get(route_path)
                            if not permission:
                                # Try to determine from route
                                method = methods[0]
                                if 'GET' in methods:
                                    permission = route_permissions.get(f'{route_path}:GET')
                                elif 'POST' in methods:
                                    permission = route_permissions.get(f'{route_path}:POST')
                                elif 'PUT' in methods or 'PATCH' in methods:
                                    permission = route_permissions.get(f'{route_path}:PUT')
                                elif 'DELETE' in methods:
                                    permission = route_permissions.get(f'{route_path}:DELETE')
                            
                            if permission:
                                # Add decorator before function
                                indent = len(lines[j]) - len(lines[j].lstrip())
                                decorator = ' ' * indent + f"@require_permission('{permission}')\n"
                                new_lines.append(decorator)
                                changes += 1
                                print(f"   Added: {route_path} -> {permission}")
            
            i += 1
        
        if changes > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            return changes
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def main():
    base_dir = Path(__file__).parent.parent
    
    # Finance double_entry_routes
    print("Processing finance/double_entry_routes.py...")
    double_entry_perms = {
        '/accounts/default/preview': 'finance.accounts.read',
        '/validate-multi-currency': 'finance.journal.create',
    }
    file_path = base_dir / 'modules/finance/double_entry_routes.py'
    if file_path.exists():
        changes = add_protection_to_file(file_path, 'double_entry_bp', double_entry_perms)
        print(f"✅ Added {changes} protections")
    
    # Procurement routes
    print("\nProcessing procurement/routes.py...")
    procurement_perms = {
        '/vendors/<int:vendor_id>': 'procurement.vendors.read',
        '/vendors/<int:vendor_id>:PUT': 'procurement.vendors.update',
        '/vendors/<int:vendor_id>:DELETE': 'procurement.vendors.delete',
        '/vendors/<int:vendor_id>/performance': 'procurement.vendors.update',
        '/vendors/<int:vendor_id>/documents': 'procurement.vendors.read',
        '/vendors/<int:vendor_id>/documents:POST': 'procurement.vendors.update',
        '/vendors/<int:vendor_id>/documents/<int:doc_id>': 'procurement.vendors.delete',
        '/vendors/<int:vendor_id>/communications': 'procurement.vendors.read',
        '/vendors/<int:vendor_id>/communications:POST': 'procurement.vendors.update',
        '/purchase-orders': 'procurement.purchase_orders.read',
        '/purchase-orders:POST': 'procurement.purchase_orders.create',
        '/purchase-orders/<int:po_id>': 'procurement.purchase_orders.read',
        '/purchase-orders/<int:po_id>:PUT': 'procurement.purchase_orders.update',
        '/purchase-orders/<int:po_id>:DELETE': 'procurement.purchase_orders.delete',
        '/purchase-orders/<int:po_id>/approve': 'procurement.purchase_orders.approve',
        '/purchase-orders/<int:po_id>/receive': 'procurement.purchase_orders.update',
        '/purchase-orders/<int:po_id>/cancel': 'procurement.purchase_orders.update',
        '/purchase-orders/<int:po_id>/items': 'procurement.purchase_orders.read',
        '/purchase-orders/<int:po_id>/items:POST': 'procurement.purchase_orders.update',
        '/purchase-orders/<int:po_id>/items/<int:item_id>': 'procurement.purchase_orders.update',
        '/purchase-orders/<int:po_id>/items/<int:item_id>:DELETE': 'procurement.purchase_orders.update',
        '/purchase-orders/<int:po_id>/attachments': 'procurement.purchase_orders.read',
        '/purchase-orders/<int:po_id>/attachments:POST': 'procurement.purchase_orders.update',
        '/purchase-orders/<int:po_id>/attachments/<int:att_id>': 'procurement.purchase_orders.delete',
        '/rfqs': 'procurement.rfqs.read',
        '/rfqs:POST': 'procurement.rfqs.create',
        '/rfqs/<int:rfq_id>': 'procurement.rfqs.read',
        '/rfqs/<int:rfq_id>:PUT': 'procurement.rfqs.update',
        '/rfqs/<int:rfq_id>:DELETE': 'procurement.rfqs.delete',
        '/rfqs/<int:rfq_id>/responses': 'procurement.rfqs.read',
        '/rfqs/<int:rfq_id>/responses:POST': 'procurement.rfqs.create',
        '/contracts': 'procurement.contracts.read',
        '/contracts:POST': 'procurement.contracts.create',
        '/contracts/<int:contract_id>': 'procurement.contracts.read',
        '/contracts/<int:contract_id>:PUT': 'procurement.contracts.update',
        '/contracts/<int:contract_id>:DELETE': 'procurement.contracts.delete',
    }
    file_path = base_dir / 'modules/procurement/routes.py'
    if file_path.exists():
        changes = add_protection_to_file(file_path, 'bp', procurement_perms)
        print(f"✅ Added {changes} protections")
    
    # Finance analytics routes
    print("\nProcessing finance/analytics_routes.py...")
    analytics_perms = {
        '/matching-efficiency': 'finance.reports.read',
        '/optimization-recommendations': 'finance.reports.read',
        '/performance-metrics': 'finance.reports.read',
        '/bottlenecks': 'finance.reports.read',
        '/cache-stats': 'finance.reports.read',
        '/dashboard-summary': 'finance.reports.read',
        '/export-report': 'finance.reports.read',
        '/quick-actions': 'finance.reports.read',
    }
    file_path = base_dir / 'modules/finance/analytics_routes.py'
    if file_path.exists():
        changes = add_protection_to_file(file_path, 'analytics_bp', analytics_perms)
        print(f"✅ Added {changes} protections")
    
    print("\n✅ Complete!")

if __name__ == '__main__':
    main()



