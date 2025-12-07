"""
Script to update all finance routes from user_id to tenant_id
This updates the double_entry_routes.py file systematically
"""

import re

def update_route_file():
    file_path = 'backend/modules/finance/double_entry_routes.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern 1: Replace user_id header extraction with tenant_id
    content = re.sub(
        r'user_id = request\.headers\.get\(\'X-User-ID\'\)\s+if not user_id:\s+return jsonify\(\{"error": "User authentication required"\}\), 401\s+user_id_int = int\(user_id\)',
        '''# TENANT-CENTRIC: Get tenant_id and user_id
        tenant_id = get_current_user_tenant_id()
        user_id_int = get_current_user_id()
        
        if not tenant_id or not user_id_int:
            return jsonify({"error": "Tenant context and user authentication required"}), 403''',
        content
    )
    
    # Pattern 2: Replace Account.query.filter_by(user_id=...) with tenant_id
    content = re.sub(
        r'Account\.query\.filter_by\(([^)]*user_id[^)]*)\)',
        lambda m: m.group(0).replace('user_id', 'tenant_id').replace('user_id_int', 'tenant_id'),
        content
    )
    
    # Pattern 3: Replace JournalEntry.query.filter_by(user_id=...) with tenant_id
    content = re.sub(
        r'JournalEntry\.query\.filter_by\(([^)]*user_id[^)]*)\)',
        lambda m: m.group(0).replace('user_id', 'tenant_id').replace('user_id_int', 'tenant_id'),
        content
    )
    
    # Pattern 4: Replace Account.query.filter(Account.user_id == ...) with tenant_id
    content = re.sub(
        r'Account\.query\.filter\(\s*Account\.user_id\s*==\s*user_id_int\s*\)',
        'Account.query.filter(Account.tenant_id == tenant_id)',
        content
    )
    
    # Pattern 5: Replace JournalEntry.query.filter(JournalEntry.user_id == ...) with tenant_id
    content = re.sub(
        r'JournalEntry\.query\.filter\(\s*JournalEntry\.user_id\s*==\s*user_id_int\s*\)',
        'JournalEntry.query.filter(JournalEntry.tenant_id == tenant_id)',
        content
    )
    
    # Pattern 6: Replace account creation with tenant_id
    content = re.sub(
        r'account = Account\([^)]*user_id=user_id_int[^)]*\)',
        lambda m: m.group(0).replace('user_id=user_id_int', 'tenant_id=tenant_id, created_by=user_id_int'),
        content
    )
    
    # Pattern 7: Replace journal entry creation with tenant_id
    content = re.sub(
        r'journal_entry = JournalEntry\([^)]*user_id=user_id_int[^)]*\)',
        lambda m: m.group(0).replace('user_id=user_id_int', 'tenant_id=tenant_id, created_by=user_id_int'),
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Updated finance routes to use tenant_id")

if __name__ == "__main__":
    update_route_file()

