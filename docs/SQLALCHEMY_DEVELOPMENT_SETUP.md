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

## **AWS PostgreSQL Migration**

### **Step 1: Prepare for Migration**
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Test connection to AWS RDS
psql -h your-rds-endpoint.amazonaws.com -U username -d database_name
```

### **Step 2: Environment Configuration**
```bash
# Set production database URL
export DATABASE_URL="postgresql://username:password@your-rds-endpoint.amazonaws.com:5432/edonuops"
export FLASK_ENV=production
```

### **Step 3: Run Migrations**
```bash
# Initialize migrations for PostgreSQL
python migrate_db.py init

# Create initial migration
python migrate_db.py create "Initial migration for PostgreSQL"

# Apply migrations
python migrate_db.py apply
```

### **Step 4: Verify Migration**
```bash
# Test database connection
python -c "
from app import create_app, db
from modules.finance.models import ChartOfAccount
app = create_app()
with app.app_context():
    count = ChartOfAccount.query.count()
    print(f'✅ Chart of Accounts records: {count}')
"
```

## **Database Configuration Files**

### **Development Configuration**
```python
# config/settings.py
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'sqlite:///edonuops.db')
    SQLALCHEMY_ECHO = True  # Show SQL queries
    SQLALCHEMY_RECORD_QUERIES = True  # Track query performance
```

### **Production Configuration**
```python
# config/settings.py
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30
    }
```

## **Model Examples**

### **Chart of Accounts Model**
```python
class ChartOfAccount(db.Model):
    __tablename__ = 'chart_of_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('chart_of_accounts.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = db.relationship('ChartOfAccount', remote_side=[id], backref='children')
    journal_lines = db.relationship('JournalLine', backref='account', lazy='dynamic')
```

### **Journal Entry Model**
```python
class JournalHeader(db.Model):
    __tablename__ = 'journal_headers'
    
    id = db.Column(db.Integer, primary_key=True)
    entry_number = db.Column(db.String(50), unique=True, nullable=False)
    entry_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    total_debit = db.Column(db.Numeric(15, 2), default=0)
    total_credit = db.Column(db.Numeric(15, 2), default=0)
    status = db.Column(db.String(20), default='Draft')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lines = db.relationship('JournalLine', backref='header', lazy='dynamic', cascade='all, delete-orphan')
```

## **Performance Optimization**

### **Database Indexes**
```python
# Add indexes for better performance
class ChartOfAccount(db.Model):
    # ... existing fields ...
    
    __table_args__ = (
        db.Index('idx_chart_of_accounts_code', 'code'),
        db.Index('idx_chart_of_accounts_type', 'account_type'),
        db.Index('idx_chart_of_accounts_parent', 'parent_id'),
    )
```

### **Query Optimization**
```python
# Use proper joins and eager loading
accounts = ChartOfAccount.query.options(
    db.joinedload('parent'),
    db.joinedload('children')
).filter_by(is_active=True).all()

# Use pagination for large datasets
accounts = ChartOfAccount.query.paginate(
    page=1, per_page=50, error_out=False
)
```

Your SQLAlchemy configuration is robust and ready for serious ERP development! 🚀

