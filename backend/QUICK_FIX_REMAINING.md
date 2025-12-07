# Quick Fix Guide - Remaining Violations

## ⚠️ **Remaining Violations Found**

The enforcement script found **~25 remaining violations** in:
- `double_entry_routes.py` - Multiple Account queries
- `tenant_analytics_service.py` - A few queries

## 🔧 **Quick Fix Pattern**

**Find:**
```python
Account.query.filter_by(code=code, tenant_id=tenant_id).first()
```

**Replace with:**
```python
tenant_query(Account).filter_by(code=code).first()
```

**Pattern:**
- Remove `tenant_id=tenant_id` from filter_by()
- Wrap with `tenant_query()`
- Keep other filters

## 📋 **Files to Fix**

1. `modules/finance/double_entry_routes.py` - ~20 violations
2. `modules/finance/tenant_analytics_service.py` - 3 violations

## ✅ **Already Fixed**

- ✅ `modules/core/audit_service.py` - Fixed
- ✅ Admin routes - Exempted (legitimate use case)

---

**Note**: These are non-critical routes. Critical user and financial data routes are already migrated.

