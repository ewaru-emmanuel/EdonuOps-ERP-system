#!/usr/bin/env python3
"""
Pre-commit hook to enforce tenant_query() usage
Checks for direct Model.query.filter_by(tenant_id=...) patterns
"""

import re
import sys
from pathlib import Path

# Patterns that should trigger warnings
FORBIDDEN_PATTERNS = [
    # Direct tenant_id filtering
    (r'\.query\.filter_by\([^)]*tenant_id\s*=', 
     'Direct tenant_id filtering detected. Use tenant_query() helper instead.'),
    
    (r'\.query\.filter\([^)]*tenant_id\s*==', 
     'Direct tenant_id filtering detected. Use tenant_query() helper instead.'),
    
    (r'\.query\.filter\([^)]*\.tenant_id\s*==', 
     'Direct tenant_id filtering detected. Use tenant_query() helper instead.'),
]

# Patterns that are allowed (exceptions)
ALLOWED_PATTERNS = [
    r'tenant_query\(',  # Our helper function
    r'get_current_user_tenant_id\(',  # Getting tenant_id is OK
    r'tenant_id\s*=\s*get_current_user_tenant_id',  # Assignment is OK
    r'#.*tenant_id',  # Comments
    r'""".*tenant_id.*"""',  # Docstrings
    r"'''.*tenant_id.*'''",  # Docstrings
    r'from.*tenant',  # Imports
    r'import.*tenant',  # Imports
]

# Files/directories to skip
SKIP_PATTERNS = [
    '__pycache__',
    '.pyc',
    'venv/',
    'env/',
    'migrations/',
    'scripts/check_tenant_queries.py',  # Don't check this file
    'tenant_query_helper.py',  # Helper itself
    'tenant_aware_query.py',  # Helper itself
    'tenant_models.py',  # Models
    'tenant_helpers.py',  # Helpers
    'global_admin_routes.py',  # Admin routes (exempt - query by specific tenant_id for management)
    'tenant_management_routes.py',  # Admin routes (exempt - query by specific tenant_id for management)
    'tenant_creation_routes.py',  # Admin routes (exempt - query by specific tenant_id for management)
    'tenant_analytics_service.py',  # Analytics queries by specific tenant_id (legitimate admin operation)
]

def is_allowed_line(line):
    """Check if line matches allowed patterns"""
    for pattern in ALLOWED_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False

def check_file(file_path):
    """Check a single file for forbidden patterns"""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            # Skip allowed lines
            if is_allowed_line(line):
                continue
                
            # Check for forbidden patterns
            for pattern, message in FORBIDDEN_PATTERNS:
                if re.search(pattern, line):
                    errors.append({
                        'file': str(file_path),
                        'line': line_num,
                        'message': message,
                        'code': line.strip()
                    })
                    break  # Only report once per line
                    
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        
    return errors

def should_skip_file(file_path):
    """Check if file should be skipped"""
    path_str = str(file_path)
    for pattern in SKIP_PATTERNS:
        if pattern in path_str:
            return True
    return False

def main():
    """Main function"""
    # Get files from git or scan directory
    if len(sys.argv) > 1:
        # Files passed as arguments (from pre-commit hook)
        files = [Path(f) for f in sys.argv[1:]]
    else:
        # Scan all Python files in backend/modules
        backend_path = Path(__file__).parent.parent
        modules_path = backend_path / 'modules'
        files = list(modules_path.rglob('*.py'))
    
    all_errors = []
    
    for file_path in files:
        if should_skip_file(file_path):
            continue
            
        if not file_path.exists():
            continue
            
        errors = check_file(file_path)
        all_errors.extend(errors)
    
    if all_errors:
        print("\n❌ TENANT QUERY ENFORCEMENT VIOLATIONS DETECTED\n")
        print("=" * 80)
        
        for error in all_errors:
            print(f"\nFile: {error['file']}")
            print(f"Line {error['line']}: {error['message']}")
            print(f"Code: {error['code']}")
            print(f"\nFix: Replace with tenant_query({error['code'].split('.')[0]})")
        
        print("\n" + "=" * 80)
        print("\n💡 All tenant-specific queries must use tenant_query() helper")
        print("   Example: tenant_query(User).filter_by(id=user_id).first()")
        print("\n")
        
        return 1
    
    print("✅ All tenant queries use tenant_query() helper")
    return 0

if __name__ == '__main__':
    sys.exit(main())

