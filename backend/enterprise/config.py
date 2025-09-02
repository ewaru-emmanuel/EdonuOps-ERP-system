"""
Enterprise Configuration Management
SAP/Oracle-style enterprise configuration system
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

class EnterpriseConfig:
    """Enterprise configuration management system"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent / 'configs'
        self.config_path.mkdir(exist_ok=True)
        
        # Load configurations
        self.environment_config = self._load_config('environment.json')
        self.security_config = self._load_config('security.json')
        self.database_config = self._load_config('database.json')
        self.api_config = self._load_config('api.json')
        self.cors_config = self._load_config('cors.json')
    
    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration from file"""
        config_file = self.config_path / filename
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Return default configuration
            return self._get_default_config(filename)
    
    def _get_default_config(self, filename: str) -> Dict[str, Any]:
        """Get default configuration for file"""
        defaults = {
            'environment.json': {
                'current': 'development',
                'available': ['development', 'staging', 'production', 'aws', 'azure', 'gcp']
            },
            'security.json': {
                'jwt_secret': os.getenv('JWT_SECRET', 'default-secret-key'),
                'bcrypt_rounds': 12,
                'session_timeout': 3600,
                'rate_limit': '1000/hour'
            },
            'database.json': {
                'type': 'sqlite',
                'path': 'edonuops.db',
                'pool_size': 10,
                'max_overflow': 20
            },
            'api.json': {
                'host': 'localhost',
                'port': 5000,
                'debug': True,
                'workers': 1
            },
            'cors.json': {
                'development': [
                    'http://localhost:3000',
                    'http://127.0.0.1:3000'
                ],
                'production': [
                    'https://edonuops.com',
                    'https://www.edonuops.com'
                ]
            }
        }
        return defaults.get(filename, {})
    
    def save_config(self, config_type: str, data: Dict[str, Any]) -> bool:
        """Save configuration to file"""
        try:
            config_file = self.config_path / f'{config_type}.json'
            with open(config_file, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config {config_type}: {e}")
            return False
    
    def get_cors_origins(self, environment: Optional[str] = None) -> list:
        """Get CORS origins for environment"""
        env = environment or self.environment_config.get('current', 'development')
        return self.cors_config.get(env, self.cors_config.get('development', []))
    
    def add_cors_origin(self, origin: str, environment: Optional[str] = None) -> bool:
        """Add CORS origin for environment"""
        env = environment or self.environment_config.get('current', 'development')
        
        if env not in self.cors_config:
            self.cors_config[env] = []
        
        if origin not in self.cors_config[env]:
            self.cors_config[env].append(origin)
            return self.save_config('cors', self.cors_config)
        
        return True
    
    def remove_cors_origin(self, origin: str, environment: Optional[str] = None) -> bool:
        """Remove CORS origin for environment"""
        env = environment or self.environment_config.get('current', 'development')
        
        if env in self.cors_config and origin in self.cors_config[env]:
            self.cors_config[env].remove(origin)
            return self.save_config('cors', self.cors_config)
        
        return True
    
    def get_database_url(self) -> str:
        """Get database URL based on configuration"""
        db_config = self.database_config
        
        if db_config.get('type') == 'sqlite':
            return f"sqlite:///{db_config.get('path', 'edonuops.db')}"
        elif db_config.get('type') == 'postgresql':
            host = db_config.get('host', 'localhost')
            port = db_config.get('port', 5432)
            database = db_config.get('database', 'edonuops')
            username = db_config.get('username', 'edonuops')
            password = db_config.get('password', '')
            
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        return f"sqlite:///edonuops.db"
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return self.security_config
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return self.api_config
    
    def set_environment(self, environment: str) -> bool:
        """Set current environment"""
        self.environment_config['current'] = environment
        return self.save_config('environment', self.environment_config)
    
    def get_environment(self) -> str:
        """Get current environment"""
        return self.environment_config.get('current', 'development')

