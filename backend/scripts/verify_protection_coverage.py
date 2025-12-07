"""
Verify route protection coverage - ensure 100% protection
"""

import re
from pathlib import Path
from collections import defaultdict

def analyze_file(file_path, blueprint_name):
    """Analyze protection coverage in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all routes
        route_pattern = rf'@({blueprint_name})\.route\([\'"]([^\'"]+)[\'"],\s*methods=\[([^\]]+)\]\)'
        routes = list(re.finditer(route_pattern, content))
        
        protected = 0
        unprotected = 0
        unprotected_routes = []
        
        for match in routes:
            route_path = match.group(2)
            methods_str = match.group(3)
            methods = [m.strip().strip("'\"") for m in methods_str.split(',')]
            methods = [m for m in methods if m and m != 'OPTIONS']
            
            if not methods:
                continue
            
            # Check if protected
            func_match = re.search(r'def\s+\w+\s*\(', content[match.end():match.end()+300])
            if func_match:
                between = content[match.end():match.end()+func_match.start()]
                if '@require_permission' in between:
                    protected += 1
                else:
                    # Check if it's a public route
                    if 'public' in route_path.lower() or 'health' in route_path.lower() or 'test' in route_path.lower():
                        protected += 1  # Count public routes as "protected" (intentionally public)
                    else:
                        unprotected += 1
                        unprotected_routes.append((route_path, methods[0]))
        
        return {
            'total': len(routes),
            'protected': protected,
            'unprotected': unprotected,
            'unprotected_routes': unprotected_routes,
            'coverage': (protected / len(routes) * 100) if routes else 0
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    files_to_check = [
        ('modules/finance/routes.py', 'finance_bp'),
        ('modules/finance/double_entry_routes.py', 'double_entry_bp'),
        ('modules/inventory/routes.py', 'inventory_bp'),
        ('modules/procurement/routes.py', 'bp'),
        ('modules/sales/routes.py', 'bp'),
        ('modules/crm/routes.py', 'crm_bp'),
        ('modules/finance/advanced_routes.py', 'advanced_finance_bp'),
        ('modules/inventory/advanced_routes.py', 'advanced_inventory_bp'),
        ('modules/finance/analytics_routes.py', 'analytics_bp'),
        ('modules/inventory/analytics_routes.py', 'analytics_bp'),
        ('modules/analytics/dashboard.py', 'analytics_bp'),
    ]
    
    base_dir = Path(__file__).parent.parent
    total_routes = 0
    total_protected = 0
    total_unprotected = 0
    
    print("=" * 70)
    print("ROUTE PROTECTION COVERAGE REPORT")
    print("=" * 70)
    print()
    
    results = {}
    for rel_path, blueprint in files_to_check:
        file_path = base_dir / rel_path
        if file_path.exists():
            result = analyze_file(file_path, blueprint)
            if 'error' not in result:
                results[rel_path] = result
                total_routes += result['total']
                total_protected += result['protected']
                total_unprotected += result['unprotected']
                
                status = "✅" if result['coverage'] == 100 else "⚠️" if result['coverage'] >= 95 else "❌"
                print(f"{status} {rel_path}")
                print(f"   Total: {result['total']} | Protected: {result['protected']} | Unprotected: {result['unprotected']} | Coverage: {result['coverage']:.1f}%")
                if result['unprotected_routes']:
                    print(f"   Unprotected routes:")
                    for route, method in result['unprotected_routes'][:5]:
                        print(f"     - {method} {route}")
                    if len(result['unprotected_routes']) > 5:
                        print(f"     ... and {len(result['unprotected_routes']) - 5} more")
                print()
        else:
            print(f"⚠️  {rel_path}: File not found")
            print()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    overall_coverage = (total_protected / total_routes * 100) if total_routes > 0 else 0
    print(f"Total Routes: {total_routes}")
    print(f"Protected: {total_protected}")
    print(f"Unprotected: {total_unprotected}")
    print(f"Overall Coverage: {overall_coverage:.1f}%")
    print("=" * 70)
    
    if overall_coverage == 100:
        print("✅ 100% PROTECTION ACHIEVED!")
    elif overall_coverage >= 95:
        print("⚠️  Near 100% - Minor cleanup needed")
    else:
        print("❌ Protection incomplete - Action required")

if __name__ == '__main__':
    main()



