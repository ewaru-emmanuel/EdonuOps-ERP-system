# Development Policy: Tenant Query Enforcement

## 🎯 **Policy Statement**

**All database queries that access tenant-specific data MUST use the `tenant_query()` helper function.**

This policy ensures:
- ✅ **Security**: Automatic tenant isolation prevents data leaks
- ✅ **Consistency**: Uniform query pattern across the codebase
- ✅ **Maintainability**: Single point of control for tenant filtering

---

## 📋 **Rules**

### **1. Required Pattern**

**✅ CORRECT:**
```python
from modules.core.tenant_query_helper import tenant_query

# Get users for current tenant
users = tenant_query(User).all()

# Get specific user
user = tenant_query(User).filter_by(id=user_id).first()

# Get accounts
accounts = tenant_query(Account).filter_by(is_active=True).all()
```

**❌ FORBIDDEN:**
```python
# Direct tenant_id filtering - SECURITY RISK
users = User.query.filter_by(tenant_id=tenant_id).all()
accounts = Account.query.filter(Account.tenant_id == tenant_id).all()
```

### **2. When to Use tenant_query()**

Use `tenant_query()` for **ALL** queries on models that have a `tenant_id` column:
- ✅ User queries
- ✅ Account queries
- ✅ Transaction queries
- ✅ Chart of Accounts queries
- ✅ General Ledger queries
- ✅ Any business data with `tenant_id`

### **3. Exceptions**

**Allowed patterns:**
- Getting tenant_id: `tenant_id = get_current_user_tenant_id()`
- Assigning tenant_id: `user.tenant_id = tenant_id`
- System tables without tenant_id (roles, permissions, etc.)
- Admin/global queries (explicitly marked)

---

## 🔧 **Implementation**

### **Helper Function**

```python
from modules.core.tenant_query_helper import tenant_query

# Automatically filters by current user's tenant_id
users = tenant_query(User).all()
```

### **How It Works**

1. Extracts `tenant_id` from current JWT token
2. Automatically adds `filter_by(tenant_id=tenant_id)` to query
3. Returns filtered query object
4. Prevents accidental cross-tenant data access

---

## ✅ **Enforcement**

### **Pre-commit Hook**

A pre-commit hook automatically checks for violations:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Manual check
python scripts/check_tenant_queries.py
```

### **Code Review Checklist**

Before merging PRs, verify:
- [ ] No direct `Model.query.filter_by(tenant_id=...)` calls
- [ ] All tenant-specific queries use `tenant_query()`
- [ ] Exceptions are documented and justified

---

## 🚨 **Violations**

**If you see this error:**
```
❌ TENANT QUERY ENFORCEMENT VIOLATIONS DETECTED
File: modules/finance/routes.py
Line 45: Direct tenant_id filtering detected
```

**Fix it:**
```python
# Before
users = User.query.filter_by(tenant_id=tenant_id).all()

# After
from modules.core.tenant_query_helper import tenant_query
users = tenant_query(User).all()
```

---

## 📚 **Examples**

### **Example 1: User Management**
```python
# ✅ CORRECT
from modules.core.tenant_query_helper import tenant_query

@route('/users')
def get_users():
    users = tenant_query(User).all()
    return jsonify([u.to_dict() for u in users])
```

### **Example 2: Account Queries**
```python
# ✅ CORRECT
accounts = tenant_query(Account).filter_by(is_active=True).order_by(Account.code).all()

# ❌ WRONG
tenant_id = get_current_user_tenant_id()
accounts = Account.query.filter_by(tenant_id=tenant_id, is_active=True).all()
```

### **Example 3: Complex Queries**
```python
# ✅ CORRECT
from modules.core.tenant_query_helper import tenant_query

# Start with tenant_query, then add filters
query = tenant_query(GeneralLedgerEntry)
query = query.filter(GeneralLedgerEntry.entry_date >= start_date)
query = query.filter(GeneralLedgerEntry.status == 'posted')
entries = query.all()
```

---

## 🎓 **Training**

**New developers must:**
1. Read this policy
2. Understand tenant isolation requirements
3. Use `tenant_query()` in all new code
4. Fix violations in existing code during refactoring

---

## 📝 **Migration Status**

- ✅ **Critical Routes**: Migrated (user_management, finance, onboarding)
- ⏳ **Remaining Routes**: In progress
- 📋 **Policy**: Active and enforced

---

## 🔗 **Related Files**

- `backend/modules/core/tenant_query_helper.py` - Helper implementation
- `backend/scripts/check_tenant_queries.py` - Enforcement script
- `backend/.pre-commit-config.yaml` - Pre-commit hook config

---

**Last Updated**: 2025-12-02  
**Status**: Active Enforcement

