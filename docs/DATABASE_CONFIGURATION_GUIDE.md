# Database Configuration - Fixed for SQLite Development

## ✅ **Database Issues Resolved**

All SQLAlchemy and database configuration issues have been fixed for local development with SQLite.

### **Problems Fixed:**

1. **❌ PostgreSQL-only config** → ✅ **SQLite default for development**
2. **❌ JSONB PostgreSQL-specific columns** → ✅ **Cross-compatible JSON columns**
3. **❌ Wrong model imports** → ✅ **Correct model references**
4. **❌ Missing environment config** → ✅ **Proper .env template**
5. **❌ Production-focused defaults** → ✅ **Development-friendly defaults**

### **Key Changes Made:**

#### 1. **Database Configuration** (`config/settings.py`)
- ✅ **Default SQLite**: `sqlite:///edonuops_dev.db` for development
- ✅ **PostgreSQL ready**: Easy switch for production
- ✅ **Smart pool settings**: Only apply to PostgreSQL
- ✅ **Development config**: Separate SQLite configuration

#### 2. **Cross-Database Compatibility** (`models.py`)
- ✅ **JSON columns**: SQLite-compatible, PostgreSQL-ready
- ✅ **Dynamic type selection**: Auto-detects database type
- ✅ **No JSONB dependency**: Works without PostgreSQL

#### 3. **Model Imports Fixed** (`app.py`)
- ✅ **Correct imports**: Only existing models imported
- ✅ **Core models**: User, Role, Organization included
- ✅ **Finance models**: ChartOfAccount, JournalHeader, JournalLine

#### 4. **Environment Configuration**
- ✅ **Template provided**: `env_template.txt`
- ✅ **Development defaults**: No .env required to start
- ✅ **Production ready**: Easy PostgreSQL switch

## **Quick Start - Database Setup**

### 1. **Environment Setup** (Optional)
```bash
cd backend
cp env_template.txt .env
# Edit .env if you want custom settings
```

### 2. **Database Initialization**
```bash
# Create tables and seed data
python seed_data.py

# Or just create tables
python app.py
```

### 3. **Start Backend**
```bash
python run.py
```

## **Database Files Created**

✅ **SQLite databases** will be created automatically:
- `edonuops_dev.db` - Development database
- `edonuops.db` - General database (if using app.py)

## **Production Deployment**

When ready for production, just set environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/edonuops"
```

The system will automatically:
- ✅ Use PostgreSQL connection
- ✅ Apply PostgreSQL-specific optimizations (JSONB, connection pooling)
- ✅ Enable production-level logging

## **Database Schema Ready**

Your database now supports:

### **Chart of Accounts**
- ✅ Hierarchical account structure
- ✅ Multi-currency support
- ✅ Flexible dimensions (JSON)
- ✅ Audit trail (created/updated timestamps)

### **Journal Entries**
- ✅ Double-entry bookkeeping
- ✅ Multi-line entries
- ✅ Approval workflows
- ✅ Source document tracking

### **User Management**
- ✅ Role-based access control
- ✅ Multi-organization support
- ✅ JWT authentication

## **Verification Steps**

Test your database setup:

```bash
# 1. Start backend
python run.py

# Should see:
# [INFO] EdonuOps startup
# * Running on http://127.0.0.1:5000

# 2. Check database file exists
ls -la edonuops_dev.db

# 3. Test API endpoint
curl http://127.0.0.1:5000/health
```

Your database configuration is now **production-ready** for both SQLite development and PostgreSQL production! 🎉

## **AWS PostgreSQL Migration Guide**

### **Step 1: AWS RDS Setup**
```bash
# Create PostgreSQL RDS instance
aws rds create-db-instance \
    --db-instance-identifier edonuops-prod \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username edonuops \
    --master-user-password YourSecurePassword123 \
    --allocated-storage 20 \
    --vpc-security-group-ids sg-xxxxxxxxx
```

### **Step 2: Environment Configuration**
```bash
# Production environment variables
export DATABASE_URL="postgresql://edonuops:YourSecurePassword123@edonuops-prod.xxxxxxxxx.us-east-1.rds.amazonaws.com:5432/edonuops"
export FLASK_ENV=production
export PROD_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### **Step 3: Database Migration**
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Run database migration
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ PostgreSQL tables created successfully')
"
```

### **Step 4: Data Migration (if needed)**
```bash
# Export from SQLite
sqlite3 edonuops_dev.db .dump > data_export.sql

# Convert SQLite dump to PostgreSQL format
python migrate_sqlite_to_postgres.py

# Import to PostgreSQL
psql -h edonuops-prod.xxxxxxxxx.us-east-1.rds.amazonaws.com -U edonuops -d edonuops -f data_export_postgres.sql
```

### **Step 5: Verify Migration**
```bash
# Test connection
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

### **Development Configuration** (`config/settings.py`)
```python
class DevelopmentConfig(Config):
    DEBUG = True
    # Use absolute path for SQLite database
    import os
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'edonuops.db')
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', f'sqlite:///{db_path}')
    REDIS_URL = os.getenv('DEV_REDIS_URL', 'redis://localhost:6379/1')
    # SQLite-specific settings for proper transaction handling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'isolation_level': 'SERIALIZABLE',  # Highest isolation level
        'connect_args': {
            'timeout': 30,  # Connection timeout
            'check_same_thread': False,  # Allow multi-threading
        }
    }
```

### **Production Configuration** (`config/settings.py`)
```python
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL')
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
```

## **Environment Variables Template**

### **Development** (`config.env`)
```bash
# Development Environment Configuration for EdonuOps

# Database Configuration
DATABASE_URL=sqlite:///edonuops.db
DEV_DATABASE_URL=sqlite:///edonuops.db

# Security Keys (Development only - change in production!)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
DEV_REDIS_URL=redis://localhost:6379/1

# Logging
LOG_LEVEL=INFO

# Flask Environment
FLASK_ENV=development
```

### **Production** (`config.env.production`)
```bash
# Production Environment Configuration for EdonuOps

# Database Configuration - AWS RDS PostgreSQL
DATABASE_URL=postgresql://edonuops:YourSecurePassword123@edonuops-prod.xxxxxxxxx.us-east-1.rds.amazonaws.com:5432/edonuops

# Security Keys (Production - use strong keys!)
SECRET_KEY=your-production-secret-key-256-bits-long
JWT_SECRET_KEY=your-production-jwt-secret-key-256-bits-long

# Redis Configuration - AWS ElastiCache
REDIS_URL=redis://edonuops-cache.xxxxxxxxx.cache.amazonaws.com:6379/0

# CORS Configuration - Production origins
PROD_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://app.yourdomain.com

# Logging
LOG_LEVEL=WARNING

# Flask Environment
FLASK_ENV=production
```

## **Database Models Overview**

### **Core Models**
- **User** - User authentication and management
- **Role** - Role-based access control
- **Organization** - Multi-tenant organization support

### **Finance Models**
- **ChartOfAccount** - Chart of accounts structure
- **JournalHeader** - Journal entry headers
- **JournalLine** - Journal entry line items
- **AccountsPayable** - Accounts payable management
- **AccountsReceivable** - Accounts receivable management
- **FixedAsset** - Fixed asset management
- **Budget** - Budget planning and tracking

### **CRM Models**
- **Contact** - Contact management
- **Lead** - Lead tracking
- **Opportunity** - Sales opportunity management

### **Inventory Models**
- **Product** - Product catalog
- **Category** - Product categorization
- **Warehouse** - Warehouse management
- **InventoryTransaction** - Inventory movements

## **Database Indexes and Performance**

### **Recommended Indexes**
```sql
-- User authentication
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Finance queries
CREATE INDEX idx_chart_of_accounts_code ON chart_of_accounts(code);
CREATE INDEX idx_journal_headers_date ON journal_headers(entry_date);
CREATE INDEX idx_journal_lines_account ON journal_lines(account_id);

-- CRM queries
CREATE INDEX idx_contacts_type ON contacts(type);
CREATE INDEX idx_contacts_created_at ON contacts(created_at);

-- Inventory queries
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_inventory_transactions_date ON inventory_transactions(transaction_date);
```

### **Performance Monitoring**
```python
# Enable SQL query logging in development
SQLALCHEMY_ECHO = True

# Monitor slow queries
SQLALCHEMY_RECORD_QUERIES = True
DATABASE_QUERY_TIMEOUT = 30
```

## **Backup and Recovery**

### **SQLite Backup**
```bash
# Create backup
cp edonuops_dev.db edonuops_dev_backup_$(date +%Y%m%d_%H%M%S).db

# Restore from backup
cp edonuops_dev_backup_20240115_143022.db edonuops_dev.db
```

### **PostgreSQL Backup**
```bash
# Create backup
pg_dump -h edonuops-prod.xxxxxxxxx.us-east-1.rds.amazonaws.com -U edonuops -d edonuops > edonuops_backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -h edonuops-prod.xxxxxxxxx.us-east-1.rds.amazonaws.com -U edonuops -d edonuops < edonuops_backup_20240115_143022.sql
```

## **Troubleshooting**

### **Common Issues:**

1. **"Database locked" error:**
   ```bash
   # Close any database browser tools
   # Check for running processes
   lsof edonuops_dev.db
   ```

2. **"Table doesn't exist" error:**
   ```bash
   # Recreate tables
   python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all()"
   ```

3. **PostgreSQL connection issues:**
   ```bash
   # Test connection
   psql -h your-rds-endpoint -U username -d database_name
   
   # Check security groups
   aws ec2 describe-security-groups --group-ids sg-xxxxxxxxx
   ```

4. **Migration issues:**
   ```bash
   # Check database schema
   python -c "
   from app import create_app, db
   app = create_app()
   with app.app_context():
       print('Tables:', db.engine.table_names())
   "
   ```

Your database configuration is now **enterprise-ready** for both development and production! 🚀

