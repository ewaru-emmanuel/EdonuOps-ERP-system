"""Check which routes are protected and which are not"""
import os
import sys
import re
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def check_backend_routes():
    """Check backend routes for protection"""
    print('='*80)
    print('BACKEND ROUTE PROTECTION AUDIT')
    print('='*80 + '\n')
    
    unprotected_routes = []
    protected_routes = []
    public_routes = []
    
    # Files to check
    route_files = list(backend_path.rglob('*_routes.py')) + \
                  list(backend_path.rglob('*routes.py')) + \
                  list(backend_path.rglob('auth*.py'))
    
    for file_path in route_files:
        if '__pycache__' in str(file_path):
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                # Find route definitions
                route_match = re.search(r'@\w+\.route\(["\']([^"\']+)["\']', line)
                if route_match:
                    route_path = route_match.group(1)
                    
                    # Check next few lines for decorators
                    has_jwt = False
                    has_permission = False
                    has_auth = False
                    
                    # Check current line and next 5 lines
                    check_lines = lines[i:i+6]
                    for check_line in check_lines:
                        if '@jwt_required' in check_line:
                            has_jwt = True
                        if '@require_permission' in check_line:
                            has_permission = True
                        if '@require_auth' in check_line:
                            has_auth = True
                    
                    # Also check lines before (decorators can be on previous lines)
                    if i > 0:
                        for j in range(max(0, i-5), i):
                            if '@jwt_required' in lines[j]:
                                has_jwt = True
                            if '@require_permission' in lines[j]:
                                has_permission = True
                            if '@require_auth' in lines[j]:
                                has_auth = True
                    
                    # Determine if route is public (auth/login/register routes)
                    is_public = any(public in route_path.lower() for public in [
                        '/login', '/register', '/auth/login', '/auth/register',
                        '/verify-email', '/reset-password', '/health', '/test'
                    ])
                    
                    is_protected = has_jwt or has_permission or has_auth
                    
                    route_info = {
                        'file': str(file_path.relative_to(backend_path)),
                        'route': route_path,
                        'line': i+1
                    }
                    
                    if is_public:
                        public_routes.append(route_info)
                    elif is_protected:
                        protected_routes.append(route_info)
                    else:
                        unprotected_routes.append(route_info)
        
        except Exception as e:
            print(f'⚠️  Error checking {file_path}: {e}')
    
    # Print results
    print(f'✅ PROTECTED ROUTES: {len(protected_routes)}')
    print(f'🌐 PUBLIC ROUTES: {len(public_routes)}')
    print(f'❌ UNPROTECTED ROUTES: {len(unprotected_routes)}\n')
    
    if unprotected_routes:
        print('❌ UNPROTECTED ROUTES (NEED AUTHENTICATION):')
        print('-' * 80)
        for route in unprotected_routes[:20]:  # Show first 20
            print(f'   {route["route"]}')
            print(f'      File: {route["file"]}:{route["line"]}')
        if len(unprotected_routes) > 20:
            print(f'   ... and {len(unprotected_routes) - 20} more')
        print()
    
    if public_routes:
        print('🌐 PUBLIC ROUTES (OK - No auth needed):')
        print('-' * 80)
        for route in public_routes[:10]:  # Show first 10
            print(f'   {route["route"]}')
        if len(public_routes) > 10:
            print(f'   ... and {len(public_routes) - 10} more')
        print()
    
    return unprotected_routes

def check_frontend_routes():
    """Check frontend routes for protection"""
    print('\n' + '='*80)
    print('FRONTEND ROUTE PROTECTION AUDIT')
    print('='*80 + '\n')
    
    frontend_path = backend_path.parent / 'frontend' / 'src'
    app_file = frontend_path / 'App.jsx'
    
    if not app_file.exists():
        print('⚠️  App.jsx not found')
        return
    
    content = app_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    protected = []
    public = []
    unprotected = []
    
    for i, line in enumerate(lines):
        if '<Route path=' in line:
            # Extract route path
            path_match = re.search(r'path=["\']([^"\']+)["\']', line)
            if path_match:
                route_path = path_match.match.group(1)
                
                # Check if route uses SimpleProtectedRoute or ProtectedRoute
                # Look at current line and next few lines
                route_section = '\n'.join(lines[i:i+3])
                
                is_protected = 'SimpleProtectedRoute' in route_section or \
                              'ProtectedRoute' in route_section
                
                is_public = route_path in ['/', '/login', '/register', '/register/invite',
                                          '/verify-email', '/reset-password']
                
                if is_public:
                    public.append(route_path)
                elif is_protected:
                    protected.append(route_path)
                else:
                    unprotected.append(route_path)
    
    print(f'✅ PROTECTED ROUTES: {len(protected)}')
    for route in protected:
        print(f'   ✅ {route}')
    
    print(f'\n🌐 PUBLIC ROUTES: {len(public)}')
    for route in public:
        print(f'   🌐 {route}')
    
    if unprotected:
        print(f'\n❌ UNPROTECTED ROUTES: {len(unprotected)}')
        for route in unprotected:
            print(f'   ❌ {route}')
    else:
        print('\n✅ All frontend routes are protected!')
    
    return unprotected

if __name__ == '__main__':
    print('\n' + '='*80)
    print('COMPREHENSIVE ROUTE PROTECTION AUDIT')
    print('='*80 + '\n')
    
    backend_unprotected = check_backend_routes()
    frontend_unprotected = check_frontend_routes()
    
    print('\n' + '='*80)
    print('SUMMARY')
    print('='*80)
    
    if backend_unprotected or frontend_unprotected:
        print('❌ ISSUES FOUND:')
        if backend_unprotected:
            print(f'   - {len(backend_unprotected)} unprotected backend routes')
        if frontend_unprotected:
            print(f'   - {len(frontend_unprotected)} unprotected frontend routes')
        print('\n⚠️  Action required: Add authentication to unprotected routes')
    else:
        print('✅ All routes are properly protected!')

