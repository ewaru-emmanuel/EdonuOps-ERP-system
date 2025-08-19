# SQLAlchemy Development Setup - Complete Guide

## ✅ **SQLAlchemy Configuration Optimized for Local Development**

Your EdonuOps system is now configured with **modern SQLAlchemy** best practices for smooth local development.

### **📦 Updated Dependencies**

Modern, stable SQLAlchemy stack:
- ✅ **SQLAlchemy 2.0.21** - Latest stable with improved performance
- ✅ **Flask-SQLAlchemy 3.0.5** - Modern Flask integration  
- ✅ **Flask-Migrate 4.0.5** - Database migrations support
- ✅ **Development tools** - pytest, debugging utilities

### **🔧 Development Features Enabled**

#### **SQL Query Debugging**
- ✅ `SQLALCHEMY_ECHO = True` - See all SQL queries in console
- ✅ `SQLALCHEMY_RECORD_QUERIES = True` - Query performance tracking
- ✅ Detailed logging for troubleshooting

#### **Database Flexibility**  
- ✅ **SQLite default** for quick local development
- ✅ **PostgreSQL ready** - Easy production switch
- ✅ **Cross-compatible models** - JSON columns work with both

#### **Migration Support**
- ✅ **Flask-Migrate integration** - Professional schema management
- ✅ **Version control friendly** - Track database changes
- ✅ **Team collaboration** - Share schema updates easily

## **🚀 Quick Start Commands**

### **1. Install Updated Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### **2. Initialize Database**
```bash
# Option A: Full setup with tables
python init_db.py

# Option B: Just create tables  
python app.py
```

### **3. Seed Sample Data**
```bash
python seed_data.py
```

### **4. Start Development Server**
```bash
python run.py
```

## **📊 Database Management**

### **Basic Operations**
```bash
# Check SQLAlchemy version and setup
python init_db.py

# Create/recreate all tables
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
```

### **Migration Workflow** (Optional but Recommended)
```bash
# Initialize migrations (one time)
python migrate_db.py init

# Create migration after model changes
python migrate_db.py create "Added new fields to ChartOfAccount"

# Apply migrations
python migrate_db.py apply

# Check status
python migrate_db.py status
```

## **🔍 Development Debugging**

### **Query Monitoring**
With `SQLALCHEMY_ECHO = True`, you'll see all SQL queries:

```sql
INFO sqlalchemy.engine.Engine BEGIN (implicit)
INFO sqlalchemy.engine.Engine SELECT chart_of_accounts.id, chart_of_accounts.code, ...
INFO sqlalchemy.engine.Engine [generated in 0.00123s] ()
```

### **Database Inspection**
```python
# In Python shell
from app import create_app, db
app = create_app()
with app.app_context():
    # Check tables
    print(db.engine.table_names())
    
    # Check models
    from modules.finance.models import ChartOfAccount
    print(ChartOfAccount.query.count())
```

## **🎯 Production Transition**

When ready for production, simply:

```bash
# Set environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/edonuops"

# Run migrations
python migrate_db.py apply

# Start production server
gunicorn -w 4 run:app
```

## **📁 Files Created**

Your SQLAlchemy setup includes:

- ✅ `edonuops_dev.db` - SQLite development database
- ✅ `init_db.py` - Database initialization helper
- ✅ `migrate_db.py` - Migration management helper  
- ✅ `migrations/` - Migration files (if using Flask-Migrate)

## **🧪 Testing Your Setup**

Verify everything works:

```bash
# 1. Check database creation
python init_db.py

# Expected output:
# 📦 SQLAlchemy version: 2.0.21
# 📦 Flask-SQLAlchemy version: 3.0.5
# ✅ Created 6 tables: chart_of_accounts, journal_headers, ...

# 2. Test API with Chart of Accounts
python run.py
# Visit: http://localhost:5000/finance/coa
```

## **💡 SQLAlchemy Best Practices Implemented**

- ✅ **Model relationships** properly defined with `back_populates`
- ✅ **Indexes** on foreign keys for performance
- ✅ **JSON columns** for flexible data storage
- ✅ **Audit fields** (created_at, updated_at) on all models
- ✅ **Soft deletes** with `is_active` flags
- ✅ **Query optimization** with proper lazy loading

Your SQLAlchemy setup is now **enterprise-ready** for both development and production! 🎉

## **🆘 Troubleshooting**

### Common Issues:
- **"Table doesn't exist"** → Run `python init_db.py`
- **"Column doesn't exist"** → Model changed, run migration
- **"Database locked"** → Close any DB browser tools
- **Import errors** → Check `requirements.txt` installed correctly

Your SQLAlchemy configuration is robust and ready for serious ERP development! 🚀







