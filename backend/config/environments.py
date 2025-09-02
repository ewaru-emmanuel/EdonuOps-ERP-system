"""
Environment Configuration
Enterprise-grade environment management for different deployment scenarios
"""

import os
from typing import Dict, List, Any

class EnvironmentConfig:
    """Base environment configuration"""
    
    # CORS Configuration for different environments
    CORS_ORIGINS = {
        'development': [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3001'
        ],
        'staging': [
            'https://staging.edonuops.com',
            'https://staging-frontend.edonuops.com',
            'https://staging-admin.edonuops.com'
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
    
    # Database configurations
    DATABASE_CONFIGS = {
        'development': {
            'type': 'sqlite',
            'path': 'edonuops.db',
            'pool_size': 10,
            'max_overflow': 20
        },
        'staging': {
            'type': 'postgresql',
            'host': os.getenv('STAGING_DB_HOST', 'localhost'),
            'port': os.getenv('STAGING_DB_PORT', 5432),
            'database': os.getenv('STAGING_DB_NAME', 'edonuops_staging'),
            'username': os.getenv('STAGING_DB_USER', 'edonuops'),
            'password': os.getenv('STAGING_DB_PASSWORD', ''),
            'pool_size': 20,
            'max_overflow': 30
        },
        'production': {
            'type': 'postgresql',
            'host': os.getenv('PROD_DB_HOST', 'localhost'),
            'port': os.getenv('PROD_DB_PORT', 5432),
            'database': os.getenv('PROD_DB_NAME', 'edonuops_prod'),
            'username': os.getenv('PROD_DB_USER', 'edonuops'),
            'password': os.getenv('PROD_DB_PASSWORD', ''),
            'pool_size': 50,
            'max_overflow': 100
        }
    }
    
    # Redis configurations
    REDIS_CONFIGS = {
        'development': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'password': None
        },
        'staging': {
            'host': os.getenv('STAGING_REDIS_HOST', 'localhost'),
            'port': int(os.getenv('STAGING_REDIS_PORT', 6379)),
            'db': int(os.getenv('STAGING_REDIS_DB', 0)),
            'password': os.getenv('STAGING_REDIS_PASSWORD')
        },
        'production': {
            'host': os.getenv('PROD_REDIS_HOST', 'localhost'),
            'port': int(os.getenv('PROD_REDIS_PORT', 6379)),
            'db': int(os.getenv('PROD_REDIS_DB', 0)),
            'password': os.getenv('PROD_REDIS_PASSWORD')
        }
    }
    
    # Security configurations
    SECURITY_CONFIGS = {
        'development': {
            'jwt_secret': 'dev-secret-key-change-in-production',
            'jwt_expiration': 24 * 60 * 60,  # 24 hours
            'bcrypt_rounds': 12,
            'rate_limit': '1000/hour',
            'session_timeout': 3600
        },
        'staging': {
            'jwt_secret': os.getenv('STAGING_JWT_SECRET', 'staging-secret-key'),
            'jwt_expiration': 8 * 60 * 60,  # 8 hours
            'bcrypt_rounds': 14,
            'rate_limit': '5000/hour',
            'session_timeout': 7200
        },
        'production': {
            'jwt_secret': os.getenv('PROD_JWT_SECRET'),
            'jwt_expiration': 4 * 60 * 60,  # 4 hours
            'bcrypt_rounds': 16,
            'rate_limit': '10000/hour',
            'session_timeout': 3600
        }
    }
    
    # Logging configurations
    LOGGING_CONFIGS = {
        'development': {
            'level': 'DEBUG',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'logs/edonuops_dev.log',
            'max_size': '10MB',
            'backup_count': 5
        },
        'staging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'logs/edonuops_staging.log',
            'max_size': '50MB',
            'backup_count': 10
        },
        'production': {
            'level': 'WARNING',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'logs/edonuops_prod.log',
            'max_size': '100MB',
            'backup_count': 20
        }
    }
    
    # API configurations
    API_CONFIGS = {
        'development': {
            'host': 'localhost',
            'port': 5000,
            'debug': True,
            'reload': True,
            'workers': 1
        },
        'staging': {
            'host': '0.0.0.0',
            'port': int(os.getenv('STAGING_PORT', 5000)),
            'debug': False,
            'reload': False,
            'workers': 4
        },
        'production': {
            'host': '0.0.0.0',
            'port': int(os.getenv('PROD_PORT', 5000)),
            'debug': False,
            'reload': False,
            'workers': 8
        }
    }
    
    @classmethod
    def get_environment(cls) -> str:
        """Get current environment"""
        return os.getenv('FLASK_ENV', 'development')
    
    @classmethod
    def get_cors_origins(cls) -> List[str]:
        """Get CORS origins for current environment"""
        env = cls.get_environment()
        return cls.CORS_ORIGINS.get(env, cls.CORS_ORIGINS['development'])
    
    @classmethod
    def get_database_config(cls) -> Dict[str, Any]:
        """Get database configuration for current environment"""
        env = cls.get_environment()
        return cls.DATABASE_CONFIGS.get(env, cls.DATABASE_CONFIGS['development'])
    
    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """Get Redis configuration for current environment"""
        env = cls.get_environment()
        return cls.REDIS_CONFIGS.get(env, cls.REDIS_CONFIGS['development'])
    
    @classmethod
    def get_security_config(cls) -> Dict[str, Any]:
        """Get security configuration for current environment"""
        env = cls.get_environment()
        return cls.SECURITY_CONFIGS.get(env, cls.SECURITY_CONFIGS['development'])
    
    @classmethod
    def get_logging_config(cls) -> Dict[str, Any]:
        """Get logging configuration for current environment"""
        env = cls.get_environment()
        return cls.LOGGING_CONFIGS.get(env, cls.LOGGING_CONFIGS['development'])
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Get API configuration for current environment"""
        env = cls.get_environment()
        return cls.API_CONFIGS.get(env, cls.API_CONFIGS['development'])
    
    @classmethod
    def add_cors_origin(cls, origin: str, environment: str = None) -> None:
        """Add a new CORS origin for an environment"""
        env = environment or cls.get_environment()
        if env not in cls.CORS_ORIGINS:
            cls.CORS_ORIGINS[env] = []
        if origin not in cls.CORS_ORIGINS[env]:
            cls.CORS_ORIGINS[env].append(origin)
    
    @classmethod
    def remove_cors_origin(cls, origin: str, environment: str = None) -> None:
        """Remove a CORS origin for an environment"""
        env = environment or cls.get_environment()
        if env in cls.CORS_ORIGINS and origin in cls.CORS_ORIGINS[env]:
            cls.CORS_ORIGINS[env].remove(origin)

