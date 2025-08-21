import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from flask import current_app
import hashlib
import hmac
import time
import base64

logger = logging.getLogger(__name__)

@dataclass
class IntegrationConfig:
    """Configuration for external system integration"""
    name: str
    base_url: str
    api_key: str
    api_secret: str = ""
    timeout: int = 30
    retry_attempts: int = 3
    rate_limit: int = 100  # requests per minute
    authentication_type: str = "api_key"  # api_key, oauth, basic, custom
    headers: Dict[str, str] = None
    webhook_url: str = ""
    webhook_secret: str = ""

class IntegrationProvider(ABC):
    """Abstract base class for integration providers"""
    
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = config.timeout
        self._setup_session()
    
    def _setup_session(self):
        """Setup session with authentication and headers"""
        if self.config.headers:
            self.session.headers.update(self.config.headers)
        
        if self.config.authentication_type == "api_key":
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.api_key}",
                "X-API-Key": self.config.api_key
            })
        elif self.config.authentication_type == "basic":
            import base64
            credentials = base64.b64encode(
                f"{self.config.api_key}:{self.config.api_secret}".encode()
            ).decode()
            self.session.headers.update({
                "Authorization": f"Basic {credentials}"
            })
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the external system"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to external system"""
        pass
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                    params: Dict = None) -> Optional[Dict]:
        """Make HTTP request to external system"""
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Integration request failed: {e}")
            return None

class StripeIntegration(IntegrationProvider):
    """Stripe payment integration"""
    
    def authenticate(self) -> bool:
        """Authenticate with Stripe"""
        try:
            response = self.make_request("GET", "/v1/account")
            return response is not None
        except Exception as e:
            logger.error(f"Stripe authentication failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Stripe connection"""
        return self.authenticate()
    
    def create_payment_intent(self, amount: int, currency: str = "usd", 
                            metadata: Dict = None) -> Optional[Dict]:
        """Create payment intent"""
        data = {
            "amount": amount,
            "currency": currency
        }
        if metadata:
            data["metadata"] = metadata
        
        return self.make_request("POST", "/v1/payment_intents", data)
    
    def create_customer(self, email: str, name: str = None, 
                       metadata: Dict = None) -> Optional[Dict]:
        """Create customer"""
        data = {"email": email}
        if name:
            data["name"] = name
        if metadata:
            data["metadata"] = metadata
        
        return self.make_request("POST", "/v1/customers", data)
    
    def process_webhook(self, payload: str, signature: str) -> Optional[Dict]:
        """Process Stripe webhook"""
        try:
            import stripe
            stripe.api_key = self.config.api_key
            event = stripe.Webhook.construct_event(
                payload, signature, self.config.webhook_secret
            )
            return event
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return None

class SalesforceIntegration(IntegrationProvider):
    """Salesforce CRM integration"""
    
    def authenticate(self) -> bool:
        """Authenticate with Salesforce"""
        try:
            auth_data = {
                "grant_type": "password",
                "client_id": self.config.api_key,
                "client_secret": self.config.api_secret,
                "username": self.config.username,
                "password": self.config.password
            }
            
            response = self.session.post(
                f"{self.config.base_url}/services/oauth2/token",
                data=auth_data
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.session.headers.update({
                "Authorization": f"Bearer {token_data['access_token']}"
            })
            
            return True
        except Exception as e:
            logger.error(f"Salesforce authentication failed: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Salesforce connection"""
        try:
            response = self.make_request("GET", "/services/data/v52.0/sobjects")
            return response is not None
        except Exception as e:
            logger.error(f"Salesforce connection test failed: {e}")
            return False
    
    def create_lead(self, lead_data: Dict) -> Optional[Dict]:
        """Create lead in Salesforce"""
        return self.make_request("POST", "/services/data/v52.0/sobjects/Lead", lead_data)
    
    def create_opportunity(self, opportunity_data: Dict) -> Optional[Dict]:
        """Create opportunity in Salesforce"""
        return self.make_request("POST", "/services/data/v52.0/sobjects/Opportunity", opportunity_data)
    
    def update_record(self, object_type: str, record_id: str, data: Dict) -> Optional[Dict]:
        """Update record in Salesforce"""
        return self.make_request("PATCH", f"/services/data/v52.0/sobjects/{object_type}/{record_id}", data)

class QuickBooksIntegration(IntegrationProvider):
    """QuickBooks accounting integration"""
    
    def authenticate(self) -> bool:
        """Authenticate with QuickBooks"""
        # OAuth 2.0 flow for QuickBooks
        return True
    
    def test_connection(self) -> bool:
        """Test QuickBooks connection"""
        try:
            response = self.make_request("GET", "/v3/company/me/companyinfo")
            return response is not None
        except Exception as e:
            logger.error(f"QuickBooks connection test failed: {e}")
            return False
    
    def create_invoice(self, invoice_data: Dict) -> Optional[Dict]:
        """Create invoice in QuickBooks"""
        return self.make_request("POST", "/v3/company/me/invoice", invoice_data)
    
    def create_customer(self, customer_data: Dict) -> Optional[Dict]:
        """Create customer in QuickBooks"""
        return self.make_request("POST", "/v3/company/me/customer", customer_data)
    
    def sync_transactions(self, start_date: str, end_date: str) -> Optional[List[Dict]]:
        """Sync transactions from QuickBooks"""
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        return self.make_request("GET", "/v3/company/me/reports/TransactionList", params=params)

class EmailIntegration(IntegrationProvider):
    """Email service integration (SendGrid, Mailgun, etc.)"""
    
    def authenticate(self) -> bool:
        """Authenticate with email service"""
        return True
    
    def test_connection(self) -> bool:
        """Test email service connection"""
        try:
            response = self.make_request("GET", "/v3/user/profile")
            return response is not None
        except Exception as e:
            logger.error(f"Email service connection test failed: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, content: str, 
                  from_email: str = None) -> Optional[Dict]:
        """Send email"""
        data = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email or self.config.from_email},
            "subject": subject,
            "content": [{"type": "text/html", "value": content}]
        }
        return self.make_request("POST", "/v3/mail/send", data)

class IntegrationManager:
    """Manager for all external integrations"""
    
    def __init__(self):
        self.integrations: Dict[str, IntegrationProvider] = {}
        self.webhook_handlers: Dict[str, Callable] = {}
        # Don't register integrations immediately - will do when needed
    
    def _get_config_value(self, key: str, default: str = "") -> str:
        """Get configuration value from Flask app context"""
        try:
            from flask import current_app
            return current_app.config.get(key, default)
        except RuntimeError:
            return default
    
    def _register_default_integrations(self):
        """Register default integrations"""
        # Stripe
        stripe_config = IntegrationConfig(
            name="stripe",
            base_url="https://api.stripe.com",
            api_key=self._get_config_value("STRIPE_SECRET_KEY", ""),
            authentication_type="api_key"
        )
        self.register_integration("stripe", StripeIntegration(stripe_config))
        
        # Salesforce
        salesforce_config = IntegrationConfig(
            name="salesforce",
            base_url="https://login.salesforce.com",
            api_key=self._get_config_value("SALESFORCE_CLIENT_ID", ""),
            api_secret=self._get_config_value("SALESFORCE_CLIENT_SECRET", ""),
            authentication_type="oauth"
        )
        self.register_integration("salesforce", SalesforceIntegration(salesforce_config))
        
        # QuickBooks
        quickbooks_config = IntegrationConfig(
            name="quickbooks",
            base_url="https://sandbox-accounts.platform.intuit.com",
            api_key=self._get_config_value("QUICKBOOKS_CLIENT_ID", ""),
            api_secret=self._get_config_value("QUICKBOOKS_CLIENT_SECRET", ""),
            authentication_type="oauth"
        )
        self.register_integration("quickbooks", QuickBooksIntegration(quickbooks_config))
        
        # Email (SendGrid)
        email_config = IntegrationConfig(
            name="sendgrid",
            base_url="https://api.sendgrid.com",
            api_key=self._get_config_value("SENDGRID_API_KEY", ""),
            authentication_type="api_key",
            from_email=self._get_config_value("FROM_EMAIL", "noreply@edonuops.com")
        )
        self.register_integration("email", EmailIntegration(email_config))
    
    def ensure_integrations_loaded(self):
        """Ensure default integrations are loaded"""
        if not self.integrations:
            self._register_default_integrations()
    
    def register_integration(self, name: str, provider: IntegrationProvider):
        """Register an integration provider"""
        self.integrations[name] = provider
        logger.info(f"Registered integration: {name}")
    
    def get_integration(self, name: str) -> Optional[IntegrationProvider]:
        """Get integration provider by name"""
        self.ensure_integrations_loaded()
        return self.integrations.get(name)
    
    def test_all_connections(self) -> Dict[str, bool]:
        """Test all integration connections"""
        self.ensure_integrations_loaded()
        results = {}
        for name, provider in self.integrations.items():
            try:
                results[name] = provider.test_connection()
            except Exception as e:
                logger.error(f"Connection test failed for {name}: {e}")
                results[name] = False
        return results
    
    def register_webhook_handler(self, integration_name: str, handler: Callable):
        """Register webhook handler for integration"""
        self.webhook_handlers[integration_name] = handler
        logger.info(f"Registered webhook handler for: {integration_name}")
    
    def process_webhook(self, integration_name: str, payload: str, 
                       signature: str = None) -> Optional[Dict]:
        """Process webhook from integration"""
        if integration_name not in self.webhook_handlers:
            logger.warning(f"No webhook handler for: {integration_name}")
            return None
        
        try:
            handler = self.webhook_handlers[integration_name]
            return handler(payload, signature)
        except Exception as e:
            logger.error(f"Webhook processing failed for {integration_name}: {e}")
            return None

# Data synchronization
class DataSyncManager:
    """Manager for data synchronization between systems"""
    
    def __init__(self, integration_manager: IntegrationManager):
        self.integration_manager = integration_manager
        self.sync_jobs: Dict[str, Dict] = {}
    
    def sync_customers(self, source_system: str, target_system: str) -> bool:
        """Sync customers between systems"""
        try:
            source = self.integration_manager.get_integration(source_system)
            target = self.integration_manager.get_integration(target_system)
            
            if not source or not target:
                return False
            
            # Get customers from source
            customers = source.get_customers()
            if not customers:
                return False
            
            # Sync to target
            for customer in customers:
                target.create_customer(customer)
            
            return True
        except Exception as e:
            logger.error(f"Customer sync failed: {e}")
            return False
    
    def sync_invoices(self, source_system: str, target_system: str) -> bool:
        """Sync invoices between systems"""
        try:
            source = self.integration_manager.get_integration(source_system)
            target = self.integration_manager.get_integration(target_system)
            
            if not source or not target:
                return False
            
            # Get invoices from source
            invoices = source.get_invoices()
            if not invoices:
                return False
            
            # Sync to target
            for invoice in invoices:
                target.create_invoice(invoice)
            
            return True
        except Exception as e:
            logger.error(f"Invoice sync failed: {e}")
            return False
    
    def schedule_sync(self, job_name: str, sync_function: Callable, 
                     schedule: str = "daily") -> bool:
        """Schedule a sync job"""
        try:
            self.sync_jobs[job_name] = {
                "function": sync_function,
                "schedule": schedule,
                "last_run": None,
                "next_run": self._calculate_next_run(schedule)
            }
            logger.info(f"Scheduled sync job: {job_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to schedule sync job: {e}")
            return False
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time for scheduled job"""
        now = datetime.utcnow()
        if schedule == "hourly":
            return now + timedelta(hours=1)
        elif schedule == "daily":
            return now + timedelta(days=1)
        elif schedule == "weekly":
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(days=1)

# Global integration instances
integration_manager = IntegrationManager()
data_sync_manager = DataSyncManager(integration_manager)

# Integration utilities
def get_integration(name: str) -> Optional[IntegrationProvider]:
    """Get integration by name"""
    return integration_manager.get_integration(name)

def test_integration_connection(name: str) -> bool:
    """Test integration connection"""
    integration = get_integration(name)
    if integration:
        return integration.test_connection()
    return False

def send_email(to_email: str, subject: str, content: str) -> bool:
    """Send email via integration"""
    email_integration = get_integration("email")
    if email_integration:
        result = email_integration.send_email(to_email, subject, content)
        return result is not None
    return False

def create_payment_intent(amount: int, currency: str = "usd") -> Optional[Dict]:
    """Create payment intent via Stripe"""
    stripe_integration = get_integration("stripe")
    if stripe_integration:
        return stripe_integration.create_payment_intent(amount, currency)
    return None
