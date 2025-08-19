import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Core Flask Settings
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32))
    PROPAGATE_EXCEPTIONS = True
    JSON_SORT_KEYS = False  # Maintain JSON field order

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///edonuops.db"  # Default to SQLite for local development
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        # SQLite doesn't need pool settings, but PostgreSQL will use them
        "pool_size": 20 if "postgresql" in os.environ.get("DATABASE_URL", "") else None,
        "max_overflow": 30 if "postgresql" in os.environ.get("DATABASE_URL", "") else None
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", os.urandom(32))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"
    JWT_COOKIE_CSRF_PROTECT = True

    # Finance Module Specific
    FINANCE = {
        "DEFAULT_CURRENCY": os.environ.get("DEFAULT_CURRENCY", "USD"),
        "ALLOWED_BOOK_TYPES": ["general", "tax", "management"],
        "MAX_JOURNAL_LINES": 100,
        "AUTO_RECONCILE": os.environ.get("AUTO_RECONCILE", "true").lower() == "true"
    }

    # CORS Settings
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")

    # WebSocket Configuration
    SOCKETIO_MESSAGE_QUEUE = os.environ.get(
        "SOCKETIO_MESSAGE_QUEUE",
        "redis://localhost:6379/0"
    )

    # Logging Configuration
    LOGGING = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/edonuops.log",
                "maxBytes": 1024 * 1024 * 10,  # 10MB
                "backupCount": 5,
                "formatter": "default"
            }
        },
        "root": {
            "level": os.environ.get("LOG_LEVEL", "INFO"),
            "handlers": ["console", "file"]
        }
    }

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Show SQL queries in console
    JWT_COOKIE_SECURE = False
    
    # SQLAlchemy Development Settings
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL", 
        "sqlite:///edonuops_dev.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True  # For query debugging
    
    # Development-specific engine options
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "echo": True,  # Additional SQL logging
    }

class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    JWT_COOKIE_DOMAIN = os.environ.get("JWT_COOKIE_DOMAIN")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"