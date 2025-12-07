import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30
    } if 'postgresql' in os.getenv('DATABASE_URL', '').lower() else {}
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_CACHE_TTL = 3600  # 1 hour default
    
    # Security Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
    # Industry Standard: 1 hour access tokens (SAP, Oracle, Microsoft standard)
    # Refresh tokens handle seamless re-authentication without user interruption
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour - Industry standard for ERP systems
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 7 days - Standard refresh token lifetime
    
    # API Configuration
    API_RATE_LIMIT = '1000 per hour'
    API_RATE_LIMIT_STORAGE_URL = REDIS_URL
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/edonuops.log'
    
    # Performance Configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Multi-tenancy Configuration
    TENANT_HEADER = 'X-Tenant-ID'
    DEFAULT_TENANT = 'default'
    
    # External Services
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # Monitoring Configuration
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    METRICS_PORT = int(os.getenv('METRICS_PORT', 9090))

class DevelopmentConfig(Config):
    DEBUG = True
    # Use PostgreSQL for development (AWS RDS)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '')
    REDIS_URL = os.getenv('DEV_REDIS_URL', 'redis://localhost:6379/1')
    
    # Development: Longer tokens for convenience during testing
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours (convenient for development)
    # PostgreSQL-specific settings for proper connection handling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20,
        'connect_args': {
            'sslmode': 'require'  # AWS RDS requires SSL
        }
    }

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    REDIS_URL = os.getenv('REDIS_URL')
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Production: Strict token expiration (industry standard)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour - Industry standard (SAP, Oracle, Microsoft)
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 7 days
    
    # Production logging
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', '')
    REDIS_URL = os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/2')
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}