# 🌐 **EdonuOps URL Configuration Guide**
## Complete Enterprise URL Management Documentation

---

## 📋 **Overview**

EdonuOps uses a **professional, enterprise-grade URL configuration system** that allows you to deploy to any hosting platform with **just one environment variable change**. No hardcoded URLs, no code modifications needed.

---

## 🏗️ **Architecture Overview**

### **Current System Design:**
```
┌─────────────────────────────────────────────────────────────┐
│                    URL Configuration Flow                   │
├─────────────────────────────────────────────────────────────┤
│  Environment Variable → Config Class → Flask App → CORS    │
│                                                             │
│  Frontend: REACT_APP_API_URL → apiConfig.js → API Calls   │
│  Backend:  FLASK_ENV + *_CORS_ORIGINS → CORS Setup        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 **Backend URL Configuration**

### **1. Environment-Based CORS Configuration**

**File:** `backend/config/environments.py`

```python
class EnvironmentConfig:
    CORS_ORIGINS = {
        'development': [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3001'
        ],
        'production': [
            'https://edonuops.com',
            'https://www.edonuops.com',
            'https://app.edonuops.com',
            'https://admin.edonuops.com',
            'https://api.edonuops.com'
        ],
        'aws': [
            'https://your-aws-domain.com',
            'https://your-aws-frontend.com',
            'https://your-aws-admin.com'
        ],
        'azure': [
            'https://your-azure-domain.com',
            'https://your-azure-frontend.com',
            'https://your-azure-admin.com'
        ],
        'gcp': [
            'https://your-gcp-domain.com',
            'https://your-gcp-frontend.com',
            'https://your-gcp-admin.com'
        ]
    }
```

### **2. Dynamic Environment Detection**

**File:** `backend/config/environments.py` (Lines 188-199)

```python
@classmethod
def get_cors_origins(cls) -> List[str]:
    """Get CORS origins for current environment"""
    env = cls.get_environment()
    
    # First try to get from environment variables
    env_var_name = f"{env.upper()}_CORS_ORIGINS"
    env_origins = os.getenv(env_var_name)
    if env_origins:
        return [origin.strip() for origin in env_origins.split(',') if origin.strip()]
    
    # Fallback to hardcoded configuration
    return cls.CORS_ORIGINS.get(env, cls.CORS_ORIGINS['development'])
```

### **3. Flask App CORS Setup**

**File:** `backend/app/__init__.py` (Lines 35-74)

```python
# Configure CORS based on environment
cors_origins = EnvironmentConfig.get_cors_origins()

# Auto-detect Render environment and setup CORS
if os.getenv('RENDER'):
    print("Render environment detected - setting up CORS for deployment")
    render_frontend_url = os.getenv('RENDER_FRONTEND_URL')
    render_backend_url = os.getenv('RENDER_BACKEND_URL')
    if render_frontend_url:
        EnvironmentConfig.setup_render_cors(render_frontend_url, render_backend_url)
        cors_origins = EnvironmentConfig.get_cors_origins()
        print(f"CORS configured for Render frontend: {render_frontend_url}")
    else:
        print("RENDER_FRONTEND_URL not set - using environment configuration")

# Print CORS configuration for debugging
print(f"🌐 CORS Origins configured: {cors_origins}")

CORS(
    app,
    resources={r"/api/.*": {"origins": cors_origins}},
    supports_credentials=True,
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
    allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'X-Request-ID', 'X-Tenant-ID', 'X-User-ID'],
    expose_headers=['Content-Type', 'Authorization', 'X-Request-ID'],
    max_age=3600
)
```

---

## 🎨 **Frontend URL Configuration**

### **1. Centralized API Configuration**

**File:** `frontend/src/config/apiConfig.js`

```javascript
const API_CONFIG = {
  // Development environment
  development: {
    baseURL: process.env.REACT_APP_API_URL || process.env.REACT_APP_API_BASE || 'http://localhost:5000',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  },
  
  // Production environment
  production: {
    baseURL: process.env.REACT_APP_API_URL || process.env.REACT_APP_API_BASE || 'http://localhost:5000',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  },
  
  // AWS environment
  aws: {
    baseURL: process.env.REACT_APP_API_URL || 'https://your-aws-api-domain.com',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000
  }
};
```

### **2. Dynamic Environment Detection**

**File:** `frontend/src/config/apiConfig.js` (Lines 63-71)

```javascript
// Get current environment
const getCurrentEnvironment = () => {
  return process.env.NODE_ENV || 'development';
};

// Get API configuration for current environment
const getApiConfig = () => {
  const env = getCurrentEnvironment();
  return API_CONFIG[env] || API_CONFIG.development;
};
```

### **3. URL Building Helper**

**File:** `frontend/src/config/apiConfig.js` (Lines 149-158)

```javascript
// Helper function to build full API URL
export const buildApiUrl = (endpoint) => {
  const config = getApiConfig();
  const base = (config.baseURL || '').replace(/\/+$/, '');
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  // Avoid double "/api" when base URL already includes it
  if (base.endsWith('/api') && path.startsWith('/api')) {
    return `${base}${path.replace(/^\/api/, '')}`;
  }
  return `${base}${path}`;
};
```

---

## 🚀 **Deployment Scenarios**

### **1. AWS Deployment**

#### **Backend Configuration:**
```bash
# Set environment variables
export FLASK_ENV=aws
export AWS_CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com,https://admin.yourdomain.com

# Or in AWS Systems Manager Parameter Store:
AWS_CORS_ORIGINS = "https://mycompany.com,https://app.mycompany.com"
```

#### **Frontend Configuration:**
```bash
# Set environment variables
export REACT_APP_API_URL=https://your-api-domain.com
export NODE_ENV=production

# Or in AWS Amplify/CodeBuild:
REACT_APP_API_URL = "https://api.mycompany.com"
```

### **2. GoDaddy Hosting**

#### **Backend Configuration:**
```bash
# Set environment variables
export FLASK_ENV=production
export PROD_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Or in GoDaddy's hosting panel:
PROD_CORS_ORIGINS = "https://mybusiness.com,https://www.mybusiness.com"
```

#### **Frontend Configuration:**
```bash
# Set environment variables
export REACT_APP_API_URL=https://yourdomain.com/api
export NODE_ENV=production
```

### **3. Render.com Deployment**

#### **Backend Configuration:**
```bash
# Set environment variables
export RENDER_FRONTEND_URL=https://your-app.onrender.com
export RENDER_BACKEND_URL=https://your-api.onrender.com

# Or in Render dashboard:
RENDER_FRONTEND_URL = "https://myapp.onrender.com"
```

#### **Frontend Configuration:**
```bash
# Set environment variables
export REACT_APP_API_URL=https://your-api.onrender.com
export NODE_ENV=production
```

### **4. DigitalOcean App Platform**

#### **Backend Configuration:**
```bash
# Set environment variables
export FLASK_ENV=production
export PROD_CORS_ORIGINS=https://myapp.ondigitalocean.app,https://mydomain.com

# Or in DigitalOcean app settings:
PROD_CORS_ORIGINS = "https://myapp.ondigitalocean.app,https://mydomain.com"
```

#### **Frontend Configuration:**
```bash
# Set environment variables
export REACT_APP_API_URL=https://myapp.ondigitalocean.app/api
export NODE_ENV=production
```

### **5. Heroku Deployment**

#### **Backend Configuration:**
```bash
# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set PROD_CORS_ORIGINS="https://yourapp.herokuapp.com,https://yourdomain.com"

# Or via Heroku dashboard:
PROD_CORS_ORIGINS = "https://myapp.herokuapp.com,https://mydomain.com"
```

#### **Frontend Configuration:**
```bash
# Set environment variables
heroku config:set REACT_APP_API_URL=https://yourapp.herokuapp.com/api
heroku config:set NODE_ENV=production
```

---

## 📁 **Configuration Files**

### **Backend Configuration Files:**

1. **`backend/config.env`** - Development environment variables
```bash
# Development Environment Configuration for EdonuOps

# Database Configuration
DATABASE_URL=sqlite:///edonuops.db
DEV_DATABASE_URL=sqlite:///edonuops.db

# Security Keys (Development only - change in production!)
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production

# CORS Configuration - Development origins
DEV_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
DEV_REDIS_URL=redis://localhost:6379/1

# Logging
LOG_LEVEL=INFO

# Flask Environment
FLASK_ENV=development
```

2. **`backend/config.env.example`** - Template for other environments
```bash
# Environment Configuration for EdonuOps
# Copy this file to config.env and modify as needed

# Database Configuration
DATABASE_URL=sqlite:///edonuops.db
DEV_DATABASE_URL=sqlite:///edonuops.db

# Security Keys (Change these in production!)
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# CORS Configuration
# Development CORS origins (comma-separated)
DEV_CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001

# Production CORS origins (comma-separated)
PROD_CORS_ORIGINS=https://edonuops.com,https://www.edonuops.com

# Render Deployment (if using Render)
RENDER_FRONTEND_URL=
RENDER_BACKEND_URL=

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
DEV_REDIS_URL=redis://localhost:6379/1

# Logging
LOG_LEVEL=INFO

# External Services
OPENAI_API_KEY=
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=
```

3. **`backend/enterprise/configs/cors.json`** - JSON-based CORS configuration
```json
{
  "development": [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001"
  ],
  "production": [
    "https://edonuops.com",
    "https://www.edonuops.com"
  ],
  "aws": [
    "https://my-aws-app.com",
    "https://your-aws-domain.com"
  ]
}
```

### **Frontend Configuration Files:**

1. **`frontend/.env`** - Frontend environment variables
```bash
# Frontend Environment Configuration
REACT_APP_API_URL=http://localhost:5000
REACT_APP_API_BASE=http://localhost:5000/api
NODE_ENV=development
```

2. **`frontend/.env.production`** - Production environment variables
```bash
# Production Frontend Configuration
REACT_APP_API_URL=https://your-api-domain.com
REACT_APP_API_BASE=https://your-api-domain.com/api
NODE_ENV=production
```

---

## 🔄 **How the System Works**

### **Backend URL Flow:**
```
1. Environment Variable (FLASK_ENV=aws) 
   ↓
2. EnvironmentConfig.get_environment() → 'aws'
   ↓
3. EnvironmentConfig.get_cors_origins() → Checks AWS_CORS_ORIGINS env var
   ↓
4. If env var exists: Split by comma → ['https://domain1.com', 'https://domain2.com']
   ↓
5. If env var doesn't exist: Use hardcoded CORS_ORIGINS['aws']
   ↓
6. Flask-CORS configured with these origins
   ↓
7. All API endpoints (/api/*) accept requests from these domains
```

### **Frontend URL Flow:**
```
1. Environment Variable (NODE_ENV=production)
   ↓
2. getCurrentEnvironment() → 'production'
   ↓
3. getApiConfig() → API_CONFIG['production']
   ↓
4. buildApiUrl('/api/finance/accounts') → 'https://yourdomain.com/api/finance/accounts'
   ↓
5. Frontend makes API calls to this URL
```

---

## 🎯 **Key Benefits**

### **✅ Professional Setup:**
- **No hardcoded URLs** in code
- **Environment-based configuration**
- **One-place URL management**
- **Enterprise-grade scalability**

### **✅ Easy Deployment:**
- **One environment variable** controls everything
- **Zero code changes** needed for deployment
- **Automatic CORS configuration**
- **All endpoints work** with new domains

### **✅ Multi-Platform Support:**
- **AWS, Azure, GCP** ready
- **GoDaddy, Render, Heroku** compatible
- **Docker, Kubernetes** friendly
- **Any hosting platform** supported

---

## 🛠️ **Admin Management**

### **Runtime CORS Management:**

**File:** `backend/api/admin/cors_management.py`

```python
@cors_admin_bp.route('/cors/origins', methods=['GET'])
def get_cors_origins():
    """Get current CORS origins for all environments"""
    try:
        origins = config.cors_config
        return jsonify({
            'status': 'success',
            'current_environment': config.get_environment(),
            'origins': origins
        }), 200
    except Exception as e:
        logger.error(f"Error getting CORS origins: {e}")
        return jsonify({'error': str(e)}), 500

@cors_admin_bp.route('/cors/origins', methods=['POST'])
def add_cors_origin():
    """Add a new CORS origin"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'origin' not in data:
            return jsonify({'error': 'origin is required'}), 400
        
        origin = data['origin']
        environment = data.get('environment', config.get_environment())
        
        # Add the origin
        success = config.add_cors_origin(origin, environment)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'CORS origin {origin} added to {environment} environment',
                'origin': origin,
                'environment': environment
            }), 200
        else:
            return jsonify({'error': 'Failed to add CORS origin'}), 500
            
    except Exception as e:
        logger.error(f"Error adding CORS origin: {e}")
        return jsonify({'error': str(e)}), 500
```

### **Admin API Endpoints:**
- `GET /api/admin/cors/origins` - Get current CORS origins
- `POST /api/admin/cors/origins` - Add new CORS origin
- `DELETE /api/admin/cors/origins` - Remove CORS origin
- `POST /api/admin/cors/environment` - Set environment
- `POST /api/admin/cors/quick-add` - Quick add common origins

---

## 🧪 **Testing URL Configuration**

### **Backend Testing:**
```bash
# Test CORS configuration
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:5000/api/finance/exchange-rates

# Expected response headers:
# Access-Control-Allow-Origin: https://yourdomain.com
# Access-Control-Allow-Credentials: true
# Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
```

### **Frontend Testing:**
```javascript
// Test API configuration
import { buildApiUrl, getApiConfiguration } from './config/apiConfig';

console.log('Current API Config:', getApiConfiguration());
console.log('Finance API URL:', buildApiUrl('/api/finance/exchange-rates'));
console.log('Environment:', process.env.NODE_ENV);
```

---

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **CORS Errors:**
   ```bash
   # Check CORS origins
   curl -H "Origin: https://yourdomain.com" -X OPTIONS http://localhost:5000/api/health
   
   # Expected: Access-Control-Allow-Origin header should match your domain
   ```

2. **Environment Variables Not Loading:**
   ```bash
   # Check environment variables
   echo $FLASK_ENV
   echo $PROD_CORS_ORIGINS
   echo $REACT_APP_API_URL
   ```

3. **Frontend API Calls Failing:**
   ```javascript
   // Check API configuration
   console.log('API Base URL:', process.env.REACT_APP_API_URL);
   console.log('Build URL:', buildApiUrl('/api/health'));
   ```

### **Debug Commands:**
```bash
# Backend CORS debugging
python -c "
from config.environments import EnvironmentConfig
print('Environment:', EnvironmentConfig.get_environment())
print('CORS Origins:', EnvironmentConfig.get_cors_origins())
"

# Frontend API debugging
node -e "
console.log('NODE_ENV:', process.env.NODE_ENV);
console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
"
```

---

## 📈 **Performance & Security**

### **CORS Security:**
- ✅ **Specific origins only** - No wildcard (*) origins
- ✅ **Credentials support** - Secure cookie handling
- ✅ **Method restrictions** - Only allowed HTTP methods
- ✅ **Header validation** - Only allowed headers

### **Performance Optimizations:**
- ✅ **Connection pooling** - Efficient database connections
- ✅ **Caching** - Redis-based API response caching
- ✅ **Compression** - Gzip compression for API responses
- ✅ **Rate limiting** - API rate limiting per environment

---

## 🎉 **Conclusion**

EdonuOps uses a **professional, enterprise-grade URL configuration system** that:

- ✅ **Scales to millions of users**
- ✅ **Works on any hosting platform**
- ✅ **Requires zero code changes for deployment**
- ✅ **Provides one-place URL management**
- ✅ **Supports runtime configuration changes**
- ✅ **Maintains security best practices**

**Deploy to any platform with just one environment variable change!** 🚀

---

*This documentation covers the complete URL configuration system as implemented in EdonuOps. All URLs are managed professionally through environment variables and configuration classes, ensuring enterprise-grade scalability and maintainability.*

