# PostgreSQL Migration Guide

This guide will help you migrate from SQLite to PostgreSQL for production use.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install psycopg2-binary
```

### 2. Set Up AWS RDS PostgreSQL

#### Option A: AWS RDS (Recommended)
1. Go to AWS RDS Console
2. Create a new PostgreSQL instance
3. Choose "Free tier" for development
4. Configure security groups to allow your IP
5. Note down the connection details

#### Option B: Local PostgreSQL
```bash
# Install PostgreSQL locally
# Windows: Download from postgresql.org
# macOS: brew install postgresql
# Linux: sudo apt-get install postgresql
```

### 3. Configure Environment Variables

Create a `.env` file in the backend directory:

```env
# AWS RDS PostgreSQL (replace with your details)
DATABASE_URL=postgresql://username:password@your-aws-endpoint:5432/edonuops_erp

# Development fallback (SQLite)
DEV_DATABASE_URL=sqlite:///edonuops.db

# Security keys (change these!)
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
```

### 4. Run Migration

```bash
# Install PostgreSQL dependencies
pip install psycopg2-binary

# Run the migration script
python migrate_to_postgresql.py
```

### 5. Test PostgreSQL

```bash
# Test PostgreSQL connection and functionality
python test_postgresql.py
```

### 6. Start Application

```bash
# Start Flask app with PostgreSQL
python run.py
```

## 📋 Detailed Steps

### AWS RDS Setup

1. **Create RDS Instance**
   - Engine: PostgreSQL
   - Template: Free tier
   - Instance: db.t3.micro
   - Storage: 20GB
   - Multi-AZ: No (for free tier)

2. **Configure Security**
   - VPC: Default VPC
   - Security Group: Allow port 5432 from your IP
   - Publicly Accessible: Yes (for development)

3. **Database Configuration**
   - Database name: `edonuops_erp`
   - Master username: `edonuops`
   - Master password: `your-secure-password`

4. **Connection String Format**
   ```
   postgresql://edonuops:your-password@your-endpoint:5432/edonuops_erp
   ```

### Migration Process

The migration script will:
1. ✅ Test connections to both databases
2. ✅ Create PostgreSQL schema with proper indexes
3. ✅ Migrate all data from SQLite
4. ✅ Verify migration success
5. ✅ Test sample queries

### Verification

After migration, verify:
- ✅ All tables exist in PostgreSQL
- ✅ Data counts match between databases
- ✅ API endpoints work correctly
- ✅ Performance is acceptable

## 🔧 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check AWS security groups
   - Verify connection string format
   - Ensure PostgreSQL is running

2. **Migration Errors**
   - Check data types compatibility
   - Verify foreign key constraints
   - Review error logs

3. **Performance Issues**
   - Check indexes are created
   - Monitor query execution plans
   - Consider connection pooling

### Performance Optimization

1. **Indexes** (automatically created)
   - Product SKU and Product ID
   - Category relationships
   - Active status filters

2. **Connection Pooling**
   - Configured in settings.py
   - Pool size: 20 connections
   - Recycle time: 1 hour

3. **Query Optimization**
   - Use proper WHERE clauses
   - Limit result sets
   - Use pagination for large datasets

## 🚀 Production Deployment

### Environment Variables
```env
# Production PostgreSQL
DATABASE_URL=postgresql://prod_user:prod_password@prod-endpoint:5432/edonuops_prod

# Security (use strong keys!)
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-key

# Performance
LOG_LEVEL=WARNING
DEBUG=False
```

### Scaling Considerations

1. **Database Scaling**
   - Upgrade RDS instance size
   - Enable Multi-AZ for high availability
   - Use read replicas for read-heavy workloads

2. **Application Scaling**
   - Use connection pooling
   - Implement caching (Redis)
   - Consider microservices architecture

3. **Monitoring**
   - Set up CloudWatch alerts
   - Monitor database performance
   - Track application metrics

## 📊 Benefits of PostgreSQL

✅ **Concurrent Users**: Handle thousands of simultaneous connections  
✅ **ACID Compliance**: Full transaction support  
✅ **Advanced Features**: JSON, full-text search, geospatial  
✅ **Scalability**: Terabytes of data efficiently  
✅ **Enterprise Features**: Replication, clustering, backup  
✅ **Multi-tenancy**: Better support for multiple organizations  
✅ **Performance**: Optimized for complex queries  
✅ **Security**: Row-level security, encryption  

## 🎯 Next Steps

1. ✅ Complete AWS RDS setup
2. ✅ Run migration script
3. ✅ Test all functionality
4. ✅ Deploy to production
5. ✅ Monitor performance
6. ✅ Scale as needed

Your application is now ready for enterprise-scale deployment! 🚀


