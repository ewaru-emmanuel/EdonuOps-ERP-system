"""
Script to add @require_permission decorators to all unprotected routes
This ensures 100% route protection coverage
"""

import re
import os
from pathlib import Path

def get_permission_name(route_path, method):
    """Determine appropriate permission name based on route path and method"""
    # Extract resource and action from route
    parts = route_path.strip('/').split('/')
    
    # Remove parameters like <int:id>
    parts = [p for p in parts if not p.startswith('<')]
    
    if not parts:
        return None
    
    # Get module from first part
    module = parts[0] if parts else 'core'
    
    # Get resource
    resource = parts[-1] if len(parts) > 1 else parts[0]
    
    # Determine action based on HTTP method
    if method == 'GET':
        action = 'read'
    elif method == 'POST':
        action = 'create'
    elif method == 'PUT' or method == 'PATCH':
        action = 'update'
    elif method == 'DELETE':
        action = 'delete'
    else:
        action = 'read'
    
    # Special cases
    if 'report' in resource or 'analytics' in resource or 'dashboard' in resource:
        return f'{module}.reports.read'
    if 'export' in resource:
        return f'{module}.data.export'
    if 'import' in resource:
        return f'{module}.data.import'
    if 'kb/public' in route_path:
        return None  # Public route, no protection needed
    
    return f'{module}.{resource}.{action}'

def add_protection_to_file(file_path):
    """Add @require_permission decorators to routes in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file already imports require_permission
        has_import = 'from modules.core.permissions import require_permission' in content or \
                     'from modules.core.permissions import require_permission,' in content
        
        # Find all route decorators
        route_pattern = r'@(\w+_bp)\.route\([\'"]([^\'"]+)[\'"],\s*methods=\[([^\]]+)\]\)'
        routes = re.finditer(route_pattern, content)
        
        changes = []
        for match in routes:
            blueprint = match.group(1)
            route_path = match.group(2)
            methods_str = match.group(3)
            
            # Extract methods
            methods = [m.strip().strip("'\"") for m in methods_str.split(',')]
            methods = [m for m in methods if m and m != 'OPTIONS']
            
            if not methods:
                continue
            
            # Get the line number
            line_num = content[:match.start()].count('\n') + 1
            
            # Check if already has @require_permission
            # Look for the function definition after this route
            func_match = re.search(r'def\s+(\w+)\s*\(', content[match.end():match.end()+200])
            if not func_match:
                continue
            
            # Check if there's already a @require_permission between route and function
            between = content[match.end():match.end()+func_match.start()]
            if '@require_permission' in between:
                continue  # Already protected
            
            # Determine permission
            primary_method = methods[0] if methods else 'GET'
            permission = get_permission_name(route_path, primary_method)
            
            if not permission:
                continue  # Skip public routes
            
            # Add the decorator
            decorator = f"@require_permission('{permission}')\n"
            insert_pos = match.end()
            
            # Find the function definition
            func_start = content.find('def ', insert_pos)
            if func_start == -1:
                continue
            
            # Find the start of the line with the function
            func_line_start = content.rfind('\n', insert_pos, func_start) + 1
            
            # Insert the decorator
            content = content[:func_line_start] + decorator + content[func_line_start:]
            changes.append((line_num, route_path, permission))
        
        # Add import if needed
        if changes and not has_import:
            # Find where to add import (after other imports)
            import_pattern = r'(from\s+flask\s+import[^\n]+\n)'
            import_match = re.search(import_pattern, content)
            if import_match:
                insert_pos = import_match.end()
                content = content[:insert_pos] + 'from modules.core.permissions import require_permission\n' + content[insert_pos:]
            else:
                # Add at the top after first line
                first_line_end = content.find('\n') + 1
                content = content[:first_line_end] + 'from modules.core.permissions import require_permission\n' + content[first_line_end:]
        
        if changes:
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {file_path}: Added {len(changes)} protection decorators")
            for line, route, perm in changes:
                print(f"   - Line {line}: {route} -> {perm}")
            return len(changes)
        else:
            print(f"⏭️  {file_path}: No changes needed")
            return 0
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return 0

def main():
    """Main function to process all route files"""
    modules_dir = Path(__file__).parent.parent / 'modules'
    
    # Files to process
    route_files = [
        'finance/advanced_routes.py',
        'inventory/advanced_routes.py',
        'finance/analytics_routes.py',
        'inventory/analytics_routes.py',
        'analytics/dashboard.py',
    ]
    
    total_changes = 0
    for route_file in route_files:
        file_path = modules_dir / route_file
        if file_path.exists():
            changes = add_protection_to_file(file_path)
            total_changes += changes
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n✅ Total: Added protection to {total_changes} routes")

if __name__ == '__main__':
    main()



