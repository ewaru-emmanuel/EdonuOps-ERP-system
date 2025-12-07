"""
Route Protection Analyzer
Identifies all routes and their protection status
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Tuple
import re

class RouteAnalyzer:
    """Analyze route protection across all modules"""
    
    def __init__(self):
        self.protected_routes = []
        self.unprotected_routes = []
        self.public_routes = []  # Routes that should be public (login, etc.)
        
    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analyze a single route file"""
        routes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Find all route decorators
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    route_info = self._analyze_function(node, content, file_path)
                    if route_info:
                        routes.append(route_info)
                        
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
        
        return routes
    
    def _analyze_function(self, node: ast.FunctionDef, content: str, file_path: Path) -> Dict:
        """Analyze a function for route decorators"""
        route_info = None
        
        # Check for route decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    # @bp.route(...) or @module_bp.route(...)
                    if decorator.func.attr == 'route':
                        route_info = self._extract_route_info(decorator, node, file_path)
        
        if route_info:
            # Check for protection decorators
            route_info['protected'] = self._has_protection(node, content)
            route_info['permission'] = self._get_permission(node, content)
            route_info['module'] = self._get_module_name(file_path)
        
        return route_info
    
    def _extract_route_info(self, decorator: ast.Call, node: ast.FunctionDef, file_path: Path) -> Dict:
        """Extract route information from decorator"""
        route_path = None
        methods = ['GET']  # Default
        
        # Get route path
        if decorator.args:
            if isinstance(decorator.args[0], ast.Constant):
                route_path = decorator.args[0].value
            elif isinstance(decorator.args[0], ast.Str):  # Python < 3.8
                route_path = decorator.args[0].s
        
        # Get HTTP methods
        for keyword in decorator.keywords:
            if keyword.arg == 'methods':
                if isinstance(keyword.value, ast.List):
                    methods = [el.value if isinstance(el, ast.Constant) else el.s 
                              for el in keyword.value.elts]
        
        if route_path:
            return {
                'function': node.name,
                'route': route_path,
                'methods': methods,
                'file': str(file_path),
                'line': node.lineno
            }
        
        return None
    
    def _has_protection(self, node: ast.FunctionDef, content: str) -> bool:
        """Check if function has protection decorators"""
        decorator_names = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorator_names.append(decorator.id)
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    decorator_names.append(decorator.func.id)
        
        # Check for protection decorators
        protection_keywords = [
            'require_permission', 'jwt_required', 'require_module_access',
            'require_any_permission', 'login_required'
        ]
        
        return any(keyword in decorator_names for keyword in protection_keywords)
    
    def _get_permission(self, node: ast.FunctionDef, content: str) -> str:
        """Extract permission name from decorator"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id == 'require_permission':
                        if decorator.args:
                            if isinstance(decorator.args[0], ast.Constant):
                                return decorator.args[0].value
                            elif isinstance(decorator.args[0], ast.Str):
                                return decorator.args[0].s
        
        return None
    
    def _get_module_name(self, file_path: Path) -> str:
        """Extract module name from file path"""
        parts = file_path.parts
        if 'modules' in parts:
            idx = parts.index('modules')
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return 'unknown'
    
    def analyze_all_routes(self, modules_dir: Path = None) -> Dict:
        """Analyze all route files"""
        if modules_dir is None:
            modules_dir = Path(__file__).parent.parent / 'modules'
        
        all_routes = []
        
        # Find all route files
        route_files = list(modules_dir.rglob('*_routes.py'))
        route_files.extend(modules_dir.rglob('routes.py'))
        
        for route_file in route_files:
            routes = self.analyze_file(route_file)
            all_routes.extend(routes)
        
        # Categorize routes
        for route in all_routes:
            if route['protected']:
                self.protected_routes.append(route)
            else:
                # Check if it's a public route (login, register, etc.)
                if any(public in route['route'] for public in ['/login', '/register', '/auth', '/public']):
                    self.public_routes.append(route)
                else:
                    self.unprotected_routes.append(route)
        
        return {
            'total': len(all_routes),
            'protected': len(self.protected_routes),
            'unprotected': len(self.unprotected_routes),
            'public': len(self.public_routes),
            'protection_coverage': round((len(self.protected_routes) / len(all_routes) * 100), 1) if all_routes else 0,
            'routes': all_routes
        }
    
    def generate_report(self, output_file: str = 'route_protection_report.md'):
        """Generate protection report"""
        report = []
        report.append("# Route Protection Analysis Report\n")
        report.append(f"Generated: {Path(__file__).stat().st_mtime}\n\n")
        
        report.append("## Summary\n")
        report.append(f"- **Total Routes**: {len(self.protected_routes) + len(self.unprotected_routes) + len(self.public_routes)}\n")
        report.append(f"- **Protected Routes**: {len(self.protected_routes)}\n")
        report.append(f"- **Unprotected Routes**: {len(self.unprotected_routes)}\n")
        report.append(f"- **Public Routes**: {len(self.public_routes)}\n")
        
        total = len(self.protected_routes) + len(self.unprotected_routes) + len(self.public_routes)
        if total > 0:
            coverage = (len(self.protected_routes) / total) * 100
            report.append(f"- **Protection Coverage**: {coverage:.1f}%\n\n")
        
        # Unprotected routes by module
        report.append("## Unprotected Routes by Module\n\n")
        by_module = {}
        for route in self.unprotected_routes:
            module = route['module']
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(route)
        
        for module, routes in sorted(by_module.items()):
            report.append(f"### {module.upper()} Module ({len(routes)} routes)\n\n")
            for route in routes:
                report.append(f"- `{route['methods'][0] if route['methods'] else 'GET'} {route['route']}` - `{route['function']}`\n")
                report.append(f"  - File: `{route['file']}`\n")
                report.append(f"  - Line: {route['line']}\n\n")
        
        # Write report
        with open(output_file, 'w') as f:
            f.write(''.join(report))
        
        print(f"✅ Report generated: {output_file}")

if __name__ == "__main__":
    analyzer = RouteAnalyzer()
    results = analyzer.analyze_all_routes()
    
    print("\n" + "="*70)
    print("ROUTE PROTECTION ANALYSIS")
    print("="*70)
    print(f"Total Routes: {results['total']}")
    print(f"Protected: {results['protected']}")
    print(f"Unprotected: {results['unprotected']}")
    print(f"Public: {results['public']}")
    print(f"Coverage: {results['protection_coverage']}%")
    print("="*70)
    
    analyzer.generate_report('route_protection_report.md')
    
    if results['unprotected'] > 0:
        print(f"\n⚠️  {results['unprotected']} routes need protection!")
        print("See route_protection_report.md for details")




