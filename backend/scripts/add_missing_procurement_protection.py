"""
Add missing protection to procurement routes
"""

import re
from pathlib import Path

def add_protection(file_path):
    """Add protection to routes missing it"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Route -> permission mapping
    protections = {
        r"@bp\.route\('/purchase-orders/<int:po_id>', methods=\['DELETE'": 'procurement.purchase_orders.delete',
        r"@bp\.route\('/purchase-orders/<int:po_id>/approve'": 'procurement.purchase_orders.approve',
        r"@bp\.route\('/purchase-orders/<int:po_id>/reject'": 'procurement.purchase_orders.approve',
        r"@bp\.route\('/purchase-orders/<int:po_id>/attachments'": 'procurement.purchase_orders.update',
        r"@bp\.route\('/purchase-orders/<int:po_id>/receive'": 'procurement.purchase_orders.update',
        r"@bp\.route\('/reporting/summary'": 'procurement.reports.read',
        r"@bp\.route\('/erp/export-po'": 'procurement.purchase_orders.read',
        r"@bp\.route\('/erp/update-po-status'": 'procurement.purchase_orders.update',
        r"@bp\.route\('/erp/pending-pos'": 'procurement.purchase_orders.read',
        r"@bp\.route\('/integration/gaps'": 'procurement.integration.read',
        r"@bp\.route\('/purchase-orders/map-item-product'": 'procurement.purchase_orders.update',
        r"@bp\.route\('/analytics'": 'procurement.reports.read',
        r"@bp\.route\('/rfqs', methods=\['GET'\]\)": 'procurement.rfqs.read',
        r"@bp\.route\('/rfqs', methods=\['POST'\]\)": 'procurement.rfqs.create',
        r"@bp\.route\('/rfqs/<int:rfq_id>', methods=\['GET'\]\)": 'procurement.rfqs.read',
        r"@bp\.route\('/rfqs/<int:rfq_id>', methods=\['PUT'\]\)": 'procurement.rfqs.update',
        r"@bp\.route\('/rfqs/<int:rfq_id>/invite'": 'procurement.rfqs.update',
        r"@bp\.route\('/rfqs/<int:rfq_id>/score'": 'procurement.rfqs.update',
        r"@bp\.route\('/rfqs/<int:rfq_id>/award'": 'procurement.rfqs.update',
        r"@bp\.route\('/contracts', methods=\['GET'\]\)": 'procurement.contracts.read',
        r"@bp\.route\('/contracts', methods=\['POST'\]\)": 'procurement.contracts.create',
        r"@bp\.route\('/contracts/<int:contract_id>', methods=\['PUT'\]\)": 'procurement.contracts.update',
        r"@bp\.route\('/contracts/<int:contract_id>', methods=\['DELETE'\]\)": 'procurement.contracts.delete',
        r"@bp\.route\('/contracts/<int:contract_id>/documents'": 'procurement.contracts.update',
    }
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    changes = 0
    
    while i < len(lines):
        line = lines[i]
        new_lines.append(line)
        
        # Check if this is a route that needs protection
        for pattern, permission in protections.items():
            if re.search(pattern, line):
                # Look ahead for function definition
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith('#')):
                    new_lines.append(lines[j])
                    j += 1
                
                if j < len(lines) and lines[j].strip().startswith('def '):
                    # Check if already protected
                    has_protection = any('@require_permission' in lines[k] for k in range(i + 1, j))
                    if not has_protection:
                        indent = len(lines[j]) - len(lines[j].lstrip())
                        decorator = ' ' * indent + f"@require_permission('{permission}')\n"
                        new_lines.append(decorator)
                        changes += 1
                        print(f"   Added: {line.strip()} -> {permission}")
        
        i += 1
    
    if changes > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        print(f"✅ Added {changes} protections")
    else:
        print("⏭️  No changes needed")
    
    return changes

if __name__ == '__main__':
    file_path = Path(__file__).parent.parent / 'modules/procurement/routes.py'
    add_protection(file_path)



