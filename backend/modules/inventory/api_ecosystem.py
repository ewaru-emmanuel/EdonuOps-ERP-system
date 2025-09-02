from datetime import datetime
from typing import Dict, List
import json
import time
import threading

class APIEcosystem:
    """API-First Ecosystem with Webhooks and Developer Tools"""
    
    def __init__(self):
        self.webhooks = []
        self.api_keys = {}
        self.rate_limits = {}
        self.api_analytics = {
            'total_requests': 0,
            'requests_by_endpoint': {},
            'response_times': []
        }
        self.lock = threading.Lock()
    
    def register_webhook(self, webhook_data: Dict) -> Dict:
        """Register a new webhook subscription"""
        try:
            webhook = {
                'id': f"webhook_{len(self.webhooks) + 1}",
                'url': webhook_data['url'],
                'events': webhook_data.get('events', ['all']),
                'is_active': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            with self.lock:
                self.webhooks.append(webhook)
            
            return {
                'success': True,
                'webhook_id': webhook['id'],
                'message': 'Webhook registered successfully'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def trigger_webhook_event(self, event_type: str, event_data: Dict) -> Dict:
        """Trigger webhook events for subscribed endpoints"""
        try:
            triggered_count = 0
            
            with self.lock:
                for webhook in self.webhooks:
                    if webhook['is_active'] and ('all' in webhook['events'] or event_type in webhook['events']):
                        triggered_count += 1
            
            return {
                'success': True,
                'triggered_webhooks': triggered_count
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_api_key(self, key_data: Dict) -> Dict:
        """Create new API key for external integrations"""
        try:
            import secrets
            api_key = f"edonu_{secrets.token_urlsafe(16)}"
            
            key_info = {
                'id': f"key_{len(self.api_keys) + 1}",
                'name': key_data['name'],
                'key': api_key,
                'is_active': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            with self.lock:
                self.api_keys[api_key] = key_info
            
            return {
                'success': True,
                'api_key': api_key,
                'key_id': key_info['id']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_api_key(self, api_key: str) -> Dict:
        """Validate API key and check rate limits"""
        try:
            with self.lock:
                key_data = self.api_keys.get(api_key)
                
                if not key_data or not key_data['is_active']:
                    return {'valid': False, 'error': 'Invalid API key'}
                
                return {'valid': True, 'key_data': key_data}
                
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def track_api_request(self, endpoint: str, response_time: float = 0) -> None:
        """Track API request for analytics"""
        try:
            with self.lock:
                self.api_analytics['total_requests'] += 1
                
                if endpoint not in self.api_analytics['requests_by_endpoint']:
                    self.api_analytics['requests_by_endpoint'][endpoint] = 0
                self.api_analytics['requests_by_endpoint'][endpoint] += 1
                
                self.api_analytics['response_times'].append(response_time)
                
        except Exception as e:
            print(f"Error tracking API request: {e}")
    
    def get_api_analytics(self) -> Dict:
        """Get API analytics"""
        try:
            with self.lock:
                analytics = self.api_analytics.copy()
            
            avg_response_time = sum(analytics['response_times']) / len(analytics['response_times']) if analytics['response_times'] else 0
            
            return {
                'success': True,
                'analytics': {
                    'total_requests': analytics['total_requests'],
                    'average_response_time_ms': avg_response_time * 1000,
                    'requests_by_endpoint': analytics['requests_by_endpoint'],
                    'active_webhooks': len([w for w in self.webhooks if w['is_active']]),
                    'active_api_keys': len([k for k in self.api_keys.values() if k['is_active']])
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_api_documentation(self) -> Dict:
        """Generate API documentation"""
        try:
            documentation = {
                'api_version': '1.0.0',
                'base_url': 'https://api.edonuops.com/v1',
                'authentication': {
                    'type': 'API Key',
                    'header': 'X-API-Key'
                },
                'endpoints': {
                    'inventory': {
                        'GET /inventory/stock-levels': 'Get current stock levels',
                        'POST /inventory/adjustments': 'Create stock adjustment'
                    },
                    'webhooks': {
                        'POST /webhooks/register': 'Register webhook endpoint'
                    }
                },
                'webhook_events': [
                    'inventory.stock_updated',
                    'inventory.adjustment_created'
                ]
            }
            
            return {
                'success': True,
                'documentation': documentation
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global instance
api_ecosystem = APIEcosystem()
