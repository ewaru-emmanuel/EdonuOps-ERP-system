# Database Safety Guidelines

## ⚠️ **IMPORTANT: Database Protection**

This document outlines the safety measures implemented to prevent accidental data loss in the EdonuOps system.

## 🛡️ **Safety Measures Implemented**

### 1. **Removed Dangerous Scripts**
The following scripts that contained `db.drop_all()` have been **REMOVED**:
- ❌ `init_finance_db.py`
- ❌ `init_inventory_db.py` 
- ❌ `init_advanced_inventory_db.py`
- ❌ `migrations/reset_for_production.py`

### 2. **Secured Remaining Scripts**
- ✅ `init_database.py` - Safe (only uses `db.create_all()`)
- ✅ `modules/database.py` - Added safety checks to `drop_db()` function
- ✅ `run.py` - Enhanced with safety checks and user feedback

### 3. **Database Safety Utilities**
Created `database_safety.py` with the following features:
- 🔍 Safety checks before operations
- 💾 Backup creation functionality
- 📁 Database file listing
- ⚠️ Multiple confirmation prompts

## 🚨 **What NOT to Do**

### **NEVER run these commands:**
```bash
# These will DELETE ALL DATA:
python -c "from modules.database import drop_db; drop_db()"
python -c "from app import db; db.drop_all()"
```

### **NEVER create scripts with:**
```python
# This deletes everything:
db.drop_all()
```

## ✅ **Safe Operations**

### **Safe initialization:**
```bash
# This only creates missing tables:
python init_database.py
```

### **Safe startup:**
```bash
# This checks for existing data first:
python run.py
```

### **Create backups:**
```bash
# Create a backup before any major changes:
python database_safety.py backup
```

## 🔧 **Database Operations Guide**

### **For New Installation:**
1. Run `python init_database.py` to create tables and initial data
2. Start the server with `python run.py`

### **For Existing Installation:**
1. The server will automatically check and create missing tables
2. No manual intervention needed

### **For Development:**
1. Use `python database_safety.py backup` before making changes
2. Use `python database_safety.py list` to see database files
3. Use `python database_safety.py check` to verify safety

## 🆘 **Emergency Recovery**

### **If you accidentally lose data:**
1. Check for backup files in the backend directory
2. Look for files named `edonuops_backup_*.db`
3. Restore from the most recent backup

### **To restore from backup:**
```bash
# Stop the server first
# Then copy the backup file:
cp edonuops_backup_YYYYMMDD_HHMMSS.db edonuops.db
# Restart the server
```

## 📋 **Best Practices**

1. **Always create backups** before major changes
2. **Never run `db.drop_all()`** in production
3. **Test database changes** in a development environment first
4. **Use migrations** instead of dropping/recreating tables
5. **Monitor database file size** to detect unexpected changes

## 🔍 **Monitoring**

### **Check database status:**
```bash
python database_safety.py list
```

### **Verify safety:**
```bash
python database_safety.py check
```

### **Create backup:**
```bash
python database_safety.py backup
```

## 📞 **Support**

If you encounter any database issues:
1. Check this document first
2. Verify you haven't run any dangerous commands
3. Check for backup files
4. Contact the development team

---

**Remember: Prevention is better than recovery. Always backup before making changes!**
