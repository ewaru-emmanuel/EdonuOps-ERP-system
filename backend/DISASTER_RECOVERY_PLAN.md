# 🚨 Disaster Recovery Plan

## **Document Control**
- **Version**: 1.0
- **Last Updated**: 2025-11-27
- **Owner**: System Administrator
- **Review Frequency**: Quarterly

---

## **1. Recovery Objectives**

### **Recovery Time Objective (RTO)**
- **Target**: < 4 hours
- **Critical Systems**: < 2 hours
- **Non-Critical Systems**: < 8 hours

### **Recovery Point Objective (RPO)**
- **Target**: < 15 minutes
- **Maximum Data Loss**: 15 minutes of transactions
- **Backup Frequency**: 
  - Full Backup: Daily at 2:00 AM
  - Incremental Backup: Hourly

---

## **2. Backup Strategy**

### **Backup Types**

#### **Full Backup**
- **Frequency**: Daily at 2:00 AM UTC
- **Retention**: 30 days
- **Location**: Local + Offsite
- **Verification**: Automated integrity check

#### **Incremental Backup**
- **Frequency**: Hourly
- **Retention**: 7 days
- **Location**: Local + Offsite
- **Verification**: Automated integrity check

### **Backup Storage**

#### **Primary Storage (Local)**
- **Location**: `backend/backups/`
- **Retention**: 30 days
- **Cleanup**: Automated daily at 3:00 AM

#### **Offsite Storage**
- **Options**:
  - Amazon S3 (if `S3_BACKUP_BUCKET` configured)
  - Google Cloud Storage (if `GCS_BACKUP_BUCKET` configured)
  - Azure Blob Storage (if `AZURE_STORAGE_CONNECTION_STRING` configured)
  - Local offsite directory (for testing)
- **Retention**: 90 days
- **Versioning**: Enabled

### **Backup Verification**
- **Automated**: Every backup is verified immediately after creation
- **Manual Testing**: Monthly restore test to staging environment
- **Integrity Check**: SHA256 hash verification

---

## **3. Disaster Scenarios**

### **Scenario 1: Database Corruption**
**Symptoms**: Database errors, data inconsistencies

**Recovery Steps**:
1. Stop application immediately
2. Identify last known good backup
3. Restore from backup
4. Verify data integrity
5. Resume operations

**RTO**: 2 hours
**RPO**: 15 minutes (last hourly backup)

### **Scenario 2: Complete Server Failure**
**Symptoms**: Server unreachable, complete data loss

**Recovery Steps**:
1. Provision new server
2. Install application dependencies
3. Restore database from offsite backup
4. Verify application functionality
5. Resume operations

**RTO**: 4 hours
**RPO**: 15 minutes (last hourly backup)

### **Scenario 3: Data Center Outage**
**Symptoms**: Complete infrastructure failure

**Recovery Steps**:
1. Activate disaster recovery site
2. Restore from offsite backups
3. Update DNS/routing
4. Verify all systems
5. Resume operations

**RTO**: 6 hours
**RPO**: 15 minutes (last hourly backup)

### **Scenario 4: Ransomware/Data Breach**
**Symptoms**: Encrypted files, unauthorized access

**Recovery Steps**:
1. Isolate affected systems immediately
2. Assess damage scope
3. Restore from clean backup (before infection)
4. Patch security vulnerabilities
5. Resume operations with enhanced monitoring

**RTO**: 8 hours
**RPO**: 24 hours (restore to pre-infection state)

---

## **4. Recovery Procedures**

### **4.1 Database Restoration (SQLite)**

```bash
# 1. Stop application
systemctl stop edonuops

# 2. Identify backup
ls -lh backups/backup_full_*.db

# 3. Verify backup integrity
python -c "from services.automated_backup_service import backup_service; \
           backup_service.verify_backup('backup_id')"

# 4. Restore database
cp backups/backup_full_YYYYMMDD_HHMMSS.db edonuops.db

# 5. Verify restoration
python -c "import sqlite3; conn = sqlite3.connect('edonuops.db'); \
           conn.execute('SELECT 1'); conn.close()"

# 6. Restart application
systemctl start edonuops
```

### **4.2 Database Restoration (PostgreSQL)**

```bash
# 1. Stop application
systemctl stop edonuops

# 2. Identify backup
ls -lh backups/backup_full_*.sql

# 3. Restore database
pg_restore -h localhost -U postgres -d edonuops \
  backups/backup_full_YYYYMMDD_HHMMSS.sql

# 4. Verify restoration
psql -h localhost -U postgres -d edonuops -c "SELECT COUNT(*) FROM users;"

# 5. Restart application
systemctl start edonuops
```

### **4.3 Offsite Backup Restoration**

```bash
# From S3
aws s3 cp s3://backup-bucket/backups/backup_full_YYYYMMDD_HHMMSS.db \
  backups/restored_backup.db

# From GCS
gsutil cp gs://backup-bucket/backups/backup_full_YYYYMMDD_HHMMSS.db \
  backups/restored_backup.db

# From Azure
az storage blob download --container-name backups \
  --name backup_full_YYYYMMDD_HHMMSS.db \
  --file backups/restored_backup.db
```

---

## **5. Testing & Validation**

### **Monthly DR Drill**
- **Schedule**: First Saturday of each month
- **Procedure**:
  1. Restore latest backup to staging environment
  2. Verify all data is present
  3. Test critical workflows
  4. Document any issues
  5. Update DR plan if needed

### **Quarterly Full DR Test**
- **Schedule**: Quarterly
- **Procedure**:
  1. Simulate complete failure
  2. Execute full recovery procedure
  3. Measure actual RTO/RPO
  4. Document lessons learned
  5. Update procedures

---

## **6. Monitoring & Alerts**

### **Backup Monitoring**
- **Success/Failure Alerts**: Email/SMS on backup failure
- **Storage Alerts**: Alert when backup storage > 80% full
- **Verification Alerts**: Alert on backup verification failure

### **Health Checks**
- **Daily**: Automated backup verification
- **Weekly**: Backup storage cleanup
- **Monthly**: DR drill execution

---

## **7. Contact Information**

### **Emergency Contacts**
- **System Administrator**: [Your Contact]
- **Database Administrator**: [DBA Contact]
- **Cloud Provider Support**: [Provider Contact]
- **Backup Service Support**: [Service Contact]

### **Escalation Path**
1. **Level 1**: System Administrator (0-2 hours)
2. **Level 2**: Database Administrator (2-4 hours)
3. **Level 3**: Cloud Provider Support (4+ hours)

---

## **8. Post-Recovery Procedures**

### **After Successful Recovery**
1. ✅ Verify all systems operational
2. ✅ Notify stakeholders of recovery
3. ✅ Document recovery timeline
4. ✅ Analyze root cause
5. ✅ Implement preventive measures
6. ✅ Update DR plan if needed

### **Recovery Documentation**
- **Incident Report**: Document what happened
- **Recovery Timeline**: Document recovery steps and timing
- **Lessons Learned**: Document improvements needed
- **Root Cause Analysis**: Document why it happened

---

## **9. Backup Service Configuration**

### **Environment Variables**
```bash
# Backup Configuration
BACKUP_DIR=backups
BACKUP_RETENTION_DAYS=30

# Offsite Storage (choose one)
OFFSITE_STORAGE_TYPE=s3  # or gcs, azure, local, none

# S3 Configuration
S3_BACKUP_BUCKET=your-backup-bucket
S3_BACKUP_PREFIX=backups/

# GCS Configuration
GCS_BACKUP_BUCKET=your-backup-bucket
GCS_BACKUP_PREFIX=backups/

# Azure Configuration
AZURE_STORAGE_CONNECTION_STRING=your-connection-string
AZURE_BACKUP_CONTAINER=backups
```

### **Scheduled Tasks**
```bash
# Cron job for automated backups
0 2 * * * /path/to/backend/scripts/backup_cron.sh

# Or use systemd timer
systemctl enable backup-scheduler.service
systemctl start backup-scheduler.service
```

---

## **10. Recovery Checklist**

### **Pre-Recovery**
- [ ] Identify disaster type
- [ ] Assess damage scope
- [ ] Notify stakeholders
- [ ] Activate DR team

### **During Recovery**
- [ ] Stop affected systems
- [ ] Identify last good backup
- [ ] Verify backup integrity
- [ ] Restore database
- [ ] Verify data integrity
- [ ] Test critical functions
- [ ] Resume operations

### **Post-Recovery**
- [ ] Verify all systems operational
- [ ] Monitor for issues
- [ ] Document recovery
- [ ] Analyze root cause
- [ ] Update procedures

---

## **11. Appendices**

### **A. Backup File Naming Convention**
- Format: `backup_{type}_{YYYYMMDD_HHMMSS}.{ext}`
- Example: `backup_full_20251127_020000.db`
- Types: `full`, `incremental`

### **B. Backup Metadata**
- Location: `backups/backup_metadata.json`
- Contains: Backup list, verification status, offsite sync status

### **C. Recovery Time Estimates**
- Database Restore: 30-60 minutes
- Application Restart: 5-10 minutes
- Verification: 15-30 minutes
- **Total**: 50-100 minutes

---

**This plan should be reviewed and updated quarterly or after any significant system changes.**




