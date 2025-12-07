# EdonuOps ERP - Secure Environment Configuration Guide

## 🔒 SECURITY REQUIREMENTS

### 1. Environment Variables Setup

Create a `.env` file in the backend directory with the following structure:

```bash
# Application Environment
FLASK_ENV=development
DEBUG=False

# Security Configuration - GENERATE NEW SECRETS!
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
DEV_JWT_SECRET=your-dev-jwt-secret-change-this
STAGING_JWT_SECRET=your-staging-jwt-secret-change-this
PROD_JWT_SECRET=your-prod-jwt-secret-change-this

# Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_DB_PASSWORD@edonuerp-db.closysmuia9z.eu-north-1.rds.amazonaws.com:5432/postgres?sslmode=require
DB_HOST=edonuerp-db.closysmuia9z.eu-north-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=YOUR_DB_PASSWORD
DB_REGION=eu-north-1
DB_SSL_MODE=require

# AWS SES SMTP Configuration - YOUR CREDENTIALS HERE
AWS_REGION=eu-north-1
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_ACCESS_KEY
SES_SMTP_USER=YOUR_SES_SMTP_USERNAME
SES_SMTP_PASS=YOUR_SES_SMTP_PASSWORD
SES_FROM_EMAIL=info@edonuerp.com
SES_FROM_NAME=EdonuOps ERP

# Frontend Configuration
FRONTEND_URL=http://localhost:3000
DEV_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001

# Default Configuration
DEFAULT_TENANT_ID=default
DEFAULT_USER_ID=1
DEFAULT_ROLE=user
DEFAULT_PERMISSIONS=read,write

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 2. Required Values to Replace

Replace the following placeholders with your actual values:

- `YOUR_DB_PASSWORD` - Your PostgreSQL database password
- `YOUR_AWS_ACCESS_KEY_ID` - Your AWS Access Key ID
- `YOUR_AWS_SECRET_ACCESS_KEY` - Your AWS Secret Access Key
- `YOUR_SES_SMTP_USERNAME` - Your SES SMTP Username
- `YOUR_SES_SMTP_PASSWORD` - Your SES SMTP Password

### 3. Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use strong, unique secrets** for SECRET_KEY and JWT_SECRET_KEY
3. **Rotate credentials regularly** in production
4. **Use different credentials** for development, staging, and production
5. **Monitor access logs** for any unauthorized access attempts

### 4. Production Security

For production deployment:

1. **Use environment variables** from your hosting platform
2. **Enable encryption at rest** for sensitive data
3. **Use HTTPS** for all communications
4. **Implement rate limiting** to prevent abuse
5. **Regular security audits** and penetration testing

### 5. AWS SES Security

1. **Use IAM roles** instead of access keys when possible
2. **Limit permissions** to only what's needed for SES
3. **Enable CloudTrail** for API call logging
4. **Monitor SES usage** for unusual activity
5. **Use dedicated SMTP credentials** for email sending

## 🚨 CRITICAL SECURITY NOTES

- **NEVER** hardcode credentials in source code
- **ALWAYS** use environment variables for sensitive data
- **REGULARLY** rotate passwords and access keys
- **MONITOR** access logs and usage patterns
- **IMPLEMENT** proper access controls and permissions

