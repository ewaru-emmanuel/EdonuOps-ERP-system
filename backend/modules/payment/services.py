"""
Payment Services for EdonuOps
Handles all payment-related functionality including Stripe integration
"""

import os
import stripe
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PaymentService:
    """Secure payment service for EdonuOps"""
    
    def __init__(self):
        """Initialize payment service with secure API key loading"""
        self.stripe_public_key = self._load_stripe_public_key()
        self.stripe_secret_key = self._load_stripe_secret_key()
        
        if self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
        else:
            logger.warning("Stripe API key not found. Payment features will be disabled.")
    
    def _load_stripe_public_key(self) -> Optional[str]:
        """Securely load Stripe public key from environment variables"""
        try:
            public_key = os.getenv('STRIPE_PUBLIC_KEY')
            if not public_key:
                logger.error("STRIPE_PUBLIC_KEY not found in environment variables")
                return None
            return public_key
        except Exception as e:
            logger.error(f"Error loading Stripe public key: {e}")
            return None
    
    def _load_stripe_secret_key(self) -> Optional[str]:
        """Securely load Stripe secret key from environment variables"""
        try:
            secret_key = os.getenv('STRIPE_SECRET_KEY')
            if not secret_key:
                logger.error("STRIPE_SECRET_KEY not found in environment variables")
                return None
            return secret_key
        except Exception as e:
            logger.error(f"Error loading Stripe secret key: {e}")
            return None
    
    def create_payment_intent(self, amount: int, currency: str = 'usd', metadata: Dict = None) -> Dict[str, Any]:
        """Create a payment intent for subscription or one-time payment"""
        if not self.stripe_secret_key:
            return {
                "error": "Payment service not configured",
                "message": "Stripe API key not available. Please configure the API key in your environment variables."
            }
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency=currency,
                metadata=metadata or {},
                automatic_payment_methods={
                    'enabled': True,
                }
            )
            
            return {
                "success": True,
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": intent.amount,
                "currency": intent.currency,
                "status": intent.status
            }
            
        except stripe.error.AuthenticationError:
            return {
                "error": "Authentication failed",
                "message": "Invalid Stripe API key. Please check your Stripe configuration."
            }
        except stripe.error.RateLimitError:
            return {
                "error": "Rate limit exceeded",
                "message": "Stripe API rate limit exceeded. Please try again later."
            }
        except stripe.error.APIError as e:
            return {
                "error": "API error",
                "message": f"Stripe API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error in payment service: {e}")
            return {
                "error": "Service error",
                "message": "An unexpected error occurred. Please try again."
            }
    
    def create_subscription(self, customer_id: str, price_id: str, metadata: Dict = None) -> Dict[str, Any]:
        """Create a subscription for a customer"""
        if not self.stripe_secret_key:
            return {
                "error": "Payment service not configured",
                "message": "Stripe API key not available."
            }
        
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                metadata=metadata or {},
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent']
            )
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret if subscription.latest_invoice.payment_intent else None
            }
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return {
                "error": "Subscription creation failed",
                "message": str(e)
            }
    
    def create_customer(self, email: str, name: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """Create a Stripe customer"""
        if not self.stripe_secret_key:
            return {
                "error": "Payment service not configured",
                "message": "Stripe API key not available."
            }
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            return {
                "success": True,
                "customer_id": customer.id,
                "email": customer.email,
                "name": customer.name
            }
            
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return {
                "error": "Customer creation failed",
                "message": str(e)
            }
    
    def get_subscription_plans(self) -> Dict[str, Any]:
        """Get available subscription plans"""
        if not self.stripe_secret_key:
            return {
                "error": "Payment service not configured",
                "message": "Stripe API key not available."
            }
        
        try:
            prices = stripe.Price.list(
                active=True,
                expand=['data.product']
            )
            
            plans = []
            for price in prices.data:
                plans.append({
                    "id": price.id,
                    "product_id": price.product.id,
                    "product_name": price.product.name,
                    "product_description": price.product.description,
                    "unit_amount": price.unit_amount,
                    "currency": price.currency,
                    "recurring": price.recurring,
                    "metadata": price.metadata
                })
            
            return {
                "success": True,
                "plans": plans
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription plans: {e}")
            return {
                "error": "Failed to get plans",
                "message": str(e)
            }
    
    def is_available(self) -> bool:
        """Check if payment service is available"""
        return self.stripe_secret_key is not None
    
    def get_public_key(self) -> Optional[str]:
        """Get Stripe public key for frontend"""
        return self.stripe_public_key

# Global payment service instance
payment_service = PaymentService()
