# Integration Framework for EdonuOps ERP
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class IntegrationConfig:
    """Configuration for integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get('api_key')
        self.api_secret = config.get('api_secret')
        self.base_url = config.get('base_url')
        self.webhook_url = config.get('webhook_url')
        self.timeout = config.get('timeout', 30)
        self.retry_attempts = config.get('retry_attempts', 3)

class IntegrationProvider(ABC):
    """Abstract base class for all integrations"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the service"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to the service"""
        pass
    
    @abstractmethod
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data with the service"""
        pass

class StripeIntegration(IntegrationProvider):
    """Stripe payment integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.stripe_api_key = config.api_key
    
    def authenticate(self) -> bool:
        """Authenticate with Stripe"""
        try:
            headers = {'Authorization': f'Bearer {self.stripe_api_key}'}
            response = self.session.get('https://api.stripe.com/v1/account', headers=headers)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Stripe authentication failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Stripe connection"""
        return self.authenticate()
    
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync payment data with Stripe"""
        try:
            if data.get('type') == 'payment':
                return self._process_payment(data)
            elif data.get('type') == 'refund':
                return self._process_refund(data)
            else:
                return {'error': 'Unsupported data type'}
        except Exception as e:
            logger.error(f"Stripe sync failed: {e}")
            return {'error': str(e)}
    
    def _process_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through Stripe"""
        try:
            headers = {'Authorization': f'Bearer {self.stripe_api_key}'}
            payment_data = {
                'amount': data.get('amount'),
                'currency': data.get('currency', 'usd'),
                'source': data.get('token'),
                'description': data.get('description')
            }
            
            response = self.session.post(
                'https://api.stripe.com/v1/charges',
                headers=headers,
                data=payment_data
            )
            
            if response.status_code == 200:
                return {'status': 'success', 'payment_id': response.json().get('id')}
            else:
                return {'error': 'Payment failed', 'details': response.text}
                
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            return {'error': str(e)}
    
    def _process_refund(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process refund through Stripe"""
        try:
            headers = {'Authorization': f'Bearer {self.stripe_api_key}'}
            refund_data = {
                'charge': data.get('payment_id'),
                'amount': data.get('amount')
            }
            
            response = self.session.post(
                'https://api.stripe.com/v1/refunds',
                headers=headers,
                data=refund_data
            )
            
            if response.status_code == 200:
                return {'status': 'success', 'refund_id': response.json().get('id')}
            else:
                return {'error': 'Refund failed', 'details': response.text}
                
        except Exception as e:
            logger.error(f"Refund processing failed: {e}")
            return {'error': str(e)}

class SalesforceIntegration(IntegrationProvider):
    """Salesforce CRM integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.access_token = None
    
    def authenticate(self) -> bool:
        """Authenticate with Salesforce"""
        try:
            auth_data = {
                'grant_type': 'password',
                'client_id': self.config.api_key,
                'client_secret': self.config.api_secret,
                'username': self.config.username,
                'password': self.config.password
            }
            
            response = self.session.post(
                'https://login.salesforce.com/services/oauth2/token',
                data=auth_data
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                self.access_token = auth_response.get('access_token')
                self.instance_url = auth_response.get('instance_url')
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Salesforce authentication failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Salesforce connection"""
        if not self.authenticate():
            return False
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = self.session.get(
                f'{self.instance_url}/services/data/v52.0/sobjects',
                headers=headers
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Salesforce connection test failed: {e}")
            return False
    
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data with Salesforce"""
        try:
            if not self.access_token:
                if not self.authenticate():
                    return {'error': 'Authentication failed'}
            
            object_type = data.get('object_type')
            operation = data.get('operation')
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            if operation == 'create':
                response = self.session.post(
                    f'{self.instance_url}/services/data/v52.0/sobjects/{object_type}',
                    headers=headers,
                    json=data.get('fields', {})
                )
            elif operation == 'update':
                record_id = data.get('record_id')
                response = self.session.patch(
                    f'{self.instance_url}/services/data/v52.0/sobjects/{object_type}/{record_id}',
                    headers=headers,
                    json=data.get('fields', {})
                )
            else:
                return {'error': 'Unsupported operation'}
            
            if response.status_code in [200, 201]:
                return {'status': 'success', 'result': response.json()}
            else:
                return {'error': 'Sync failed', 'details': response.text}
                
        except Exception as e:
            logger.error(f"Salesforce sync failed: {e}")
            return {'error': str(e)}

class QuickBooksIntegration(IntegrationProvider):
    """QuickBooks accounting integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.access_token = None
        self.realm_id = None
    
    def authenticate(self) -> bool:
        """Authenticate with QuickBooks"""
        try:
            # This would typically use OAuth 2.0 flow
            # For now, using mock authentication
            self.access_token = self.config.api_key
            self.realm_id = self.config.realm_id
            return True
        except Exception as e:
            logger.error(f"QuickBooks authentication failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test QuickBooks connection"""
        return self.authenticate()
    
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync accounting data with QuickBooks"""
        try:
            if not self.access_token:
                if not self.authenticate():
                    return {'error': 'Authentication failed'}
            
            entity_type = data.get('entity_type')
            operation = data.get('operation')
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            base_url = f'https://sandbox-quickbooks.api.intuit.com/v3/company/{self.realm_id}'
            
            if operation == 'create':
                response = self.session.post(
                    f'{base_url}/{entity_type}',
                    headers=headers,
                    json=data.get('entity', {})
                )
            elif operation == 'query':
                query = data.get('query')
                response = self.session.get(
                    f'{base_url}/query?query={query}',
                    headers=headers
                )
            else:
                return {'error': 'Unsupported operation'}
            
            if response.status_code in [200, 201]:
                return {'status': 'success', 'result': response.json()}
            else:
                return {'error': 'Sync failed', 'details': response.text}
                
        except Exception as e:
            logger.error(f"QuickBooks sync failed: {e}")
            return {'error': str(e)}

class EmailIntegration(IntegrationProvider):
    """Email service integration"""
    
    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.username = config.get('username')
        self.password = config.get('password')
    
    def authenticate(self) -> bool:
        """Authenticate with email service"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.quit()
            return True
        except Exception as e:
            logger.error(f"Email authentication failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test email connection"""
        return self.authenticate()
    
    def sync_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = data.get('to')
            msg['Subject'] = data.get('subject')
            
            body = data.get('body', '')
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            text = msg.as_string()
            server.sendmail(self.username, data.get('to'), text)
            server.quit()
            
            return {'status': 'success', 'message': 'Email sent successfully'}
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {'error': str(e)}

class IntegrationManager:
    """Manager for all integrations"""
    
    def __init__(self):
        self.integrations = {}
        self.sync_queue = []
    
    def register_integration(self, name: str, integration: IntegrationProvider) -> bool:
        """Register an integration"""
        try:
            self.integrations[name] = integration
            logger.info(f"Integration registered: {name}")
            return True
        except Exception as e:
            logger.error(f"Integration registration failed: {e}")
            return False
    
    def get_integration(self, name: str) -> Optional[IntegrationProvider]:
        """Get integration by name"""
        return self.integrations.get(name)
    
    def test_all_connections(self) -> Dict[str, bool]:
        """Test all integration connections"""
        results = {}
        for name, integration in self.integrations.items():
            try:
                results[name] = integration.test_connection()
            except Exception as e:
                logger.error(f"Connection test failed for {name}: {e}")
                results[name] = False
        return results
    
    def sync_data(self, integration_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data with specific integration"""
        try:
            integration = self.get_integration(integration_name)
            if not integration:
                return {'error': f'Integration {integration_name} not found'}
            
            return integration.sync_data(data)
        except Exception as e:
            logger.error(f"Data sync failed for {integration_name}: {e}")
            return {'error': str(e)}
    
    def queue_sync(self, integration_name: str, data: Dict[str, Any]) -> bool:
        """Queue data for sync"""
        try:
            self.sync_queue.append({
                'integration': integration_name,
                'data': data,
                'timestamp': datetime.utcnow()
            })
            return True
        except Exception as e:
            logger.error(f"Sync queuing failed: {e}")
            return False
    
    def process_sync_queue(self) -> Dict[str, Any]:
        """Process queued sync operations"""
        results = {'processed': 0, 'success': 0, 'failed': 0}
        
        while self.sync_queue:
            sync_item = self.sync_queue.pop(0)
            results['processed'] += 1
            
            try:
                result = self.sync_data(sync_item['integration'], sync_item['data'])
                if result.get('status') == 'success':
                    results['success'] += 1
                else:
                    results['failed'] += 1
            except Exception as e:
                logger.error(f"Queue processing failed: {e}")
                results['failed'] += 1
        
        return results

class DataSyncManager:
    """Manager for data synchronization between systems"""
    
    def __init__(self, integration_manager: IntegrationManager):
        self.integration_manager = integration_manager
        self.sync_mappings = {}
    
    def create_sync_mapping(self, source: str, target: str, mapping: Dict[str, str]) -> bool:
        """Create data mapping between systems"""
        try:
            mapping_id = f"{source}_to_{target}"
            self.sync_mappings[mapping_id] = {
                'source': source,
                'target': target,
                'mapping': mapping
            }
            return True
        except Exception as e:
            logger.error(f"Sync mapping creation failed: {e}")
            return False
    
    def sync_between_systems(self, source: str, target: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync data between two systems"""
        try:
            mapping_id = f"{source}_to_{target}"
            mapping = self.sync_mappings.get(mapping_id)
            
            if not mapping:
                return {'error': f'No mapping found for {source} to {target}'}
            
            # Transform data according to mapping
            transformed_data = self._transform_data(data, mapping['mapping'])
            
            # Sync to target system
            return self.integration_manager.sync_data(target, transformed_data)
            
        except Exception as e:
            logger.error(f"System sync failed: {e}")
            return {'error': str(e)}
    
    def _transform_data(self, data: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
        """Transform data according to mapping"""
        transformed = {}
        for source_field, target_field in mapping.items():
            if source_field in data:
                transformed[target_field] = data[source_field]
        return transformed

# Global integration manager
integration_manager = IntegrationManager()

# Register default integrations
def initialize_default_integrations():
    """Initialize default integrations"""
    try:
        # Stripe integration
        stripe_config = IntegrationConfig({
            'api_key': 'sk_test_...',
            'timeout': 30
        })
        stripe_integration = StripeIntegration(stripe_config)
        integration_manager.register_integration('stripe', stripe_integration)
        
        # Salesforce integration
        salesforce_config = IntegrationConfig({
            'api_key': 'client_id',
            'api_secret': 'client_secret',
            'username': 'username',
            'password': 'password'
        })
        salesforce_integration = SalesforceIntegration(salesforce_config)
        integration_manager.register_integration('salesforce', salesforce_integration)
        
        # QuickBooks integration
        quickbooks_config = IntegrationConfig({
            'api_key': 'access_token',
            'realm_id': 'realm_id'
        })
        quickbooks_integration = QuickBooksIntegration(quickbooks_config)
        integration_manager.register_integration('quickbooks', quickbooks_integration)
        
        # Email integration
        email_config = IntegrationConfig({
            'username': 'email@example.com',
            'password': 'password',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587
        })
        email_integration = EmailIntegration(email_config)
        integration_manager.register_integration('email', email_integration)
        
        logger.info("Default integrations initialized")
        
    except Exception as e:
        logger.error(f"Default integrations initialization failed: {e}")

# Initialize default integrations
initialize_default_integrations()
