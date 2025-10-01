"""
Tenant Isolation Tests
Test that tenant data is properly isolated and secure
"""

import pytest
import json
from datetime import datetime
from app import create_app, db
from modules.core.tenant_models import Tenant, UserTenant, TenantModule
from modules.finance.advanced_models import ChartOfAccounts, GeneralLedgerEntry
from modules.finance.payment_models import BankAccount

class TestTenantIsolation:
    """Test tenant isolation and security"""
    
    @pytest.fixture
    def app(self):
        """Create test app"""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def setup_tenants(self, app):
        """Setup test tenants and data"""
        with app.app_context():
            # Create two tenants
            tenant_a = Tenant(
                id='tenant_a',
                name='Company A',
                domain='companya.com',
                subscription_plan='enterprise',
                status='active'
            )
            tenant_b = Tenant(
                id='tenant_b', 
                name='Company B',
                domain='companyb.com',
                subscription_plan='basic',
                status='active'
            )
            
            db.session.add(tenant_a)
            db.session.add(tenant_b)
            db.session.commit()
            
            # Create user-tenant relationships
            user_tenant_a = UserTenant(
                user_id='user_1',
                tenant_id='tenant_a',
                role='admin',
                is_default=True
            )
            user_tenant_b = UserTenant(
                user_id='user_2',
                tenant_id='tenant_b',
                role='admin',
                is_default=True
            )
            
            db.session.add(user_tenant_a)
            db.session.add(user_tenant_b)
            db.session.commit()
            
            # Create test data for each tenant
            # Tenant A data
            account_a = ChartOfAccounts(
                tenant_id='tenant_a',
                account_code='1000',
                account_name='Cash Account A',
                account_type='Asset',
                is_active=True
            )
            gl_entry_a = GeneralLedgerEntry(
                tenant_id='tenant_a',
                account_id=1,
                entry_date=datetime.now().date(),
                reference='TEST-A-001',
                description='Test entry for tenant A',
                debit_amount=1000.0,
                credit_amount=0.0,
                status='posted'
            )
            bank_account_a = BankAccount(
                tenant_id='tenant_a',
                account_name='Main Checking A',
                account_number='1234567890',
                bank_name='Bank A',
                current_balance=5000.0
            )
            
            # Tenant B data
            account_b = ChartOfAccounts(
                tenant_id='tenant_b',
                account_code='1000',
                account_name='Cash Account B',
                account_type='Asset',
                is_active=True
            )
            gl_entry_b = GeneralLedgerEntry(
                tenant_id='tenant_b',
                account_id=2,
                entry_date=datetime.now().date(),
                reference='TEST-B-001',
                description='Test entry for tenant B',
                debit_amount=2000.0,
                credit_amount=0.0,
                status='posted'
            )
            bank_account_b = BankAccount(
                tenant_id='tenant_b',
                account_name='Main Checking B',
                account_number='0987654321',
                bank_name='Bank B',
                current_balance=10000.0
            )
            
            db.session.add_all([
                account_a, gl_entry_a, bank_account_a,
                account_b, gl_entry_b, bank_account_b
            ])
            db.session.commit()
            
            return {
                'tenant_a': tenant_a,
                'tenant_b': tenant_b,
                'user_tenant_a': user_tenant_a,
                'user_tenant_b': user_tenant_b
            }
    
    def test_tenant_data_isolation(self, client, setup_tenants):
        """Test that tenants cannot access each other's data"""
        
        # Test accessing tenant A data with tenant A context
        response = client.get('/api/finance/chart-of-accounts', 
                            headers={'X-Tenant-ID': 'tenant_a', 'X-User-ID': 'user_1'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['account_name'] == 'Cash Account A'
        assert data[0]['tenant_id'] == 'tenant_a'
        
        # Test accessing tenant B data with tenant B context
        response = client.get('/api/finance/chart-of-accounts',
                            headers={'X-Tenant-ID': 'tenant_b', 'X-User-ID': 'user_2'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['account_name'] == 'Cash Account B'
        assert data[0]['tenant_id'] == 'tenant_b'
        
        # Test that tenant A cannot access tenant B's data
        response = client.get('/api/finance/chart-of-accounts',
                            headers={'X-Tenant-ID': 'tenant_a', 'X-User-ID': 'user_1'})
        
        assert response.status_code == 200
        data = response.get_json()
        # Should only see tenant A's data
        for account in data:
            assert account['tenant_id'] == 'tenant_a'
    
    def test_unauthorized_tenant_access(self, client, setup_tenants):
        """Test that users cannot access tenants they don't belong to"""
        
        # Try to access tenant B data with tenant A user
        response = client.get('/api/finance/chart-of-accounts',
                            headers={'X-Tenant-ID': 'tenant_b', 'X-User-ID': 'user_1'})
        
        # Should be denied access
        assert response.status_code == 403
        data = response.get_json()
        assert 'Access denied' in data['error']
    
    def test_missing_tenant_context(self, client, setup_tenants):
        """Test that requests without tenant context are rejected"""
        
        response = client.get('/api/finance/chart-of-accounts')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Tenant context required' in data['error']
    
    def test_invalid_tenant_id(self, client, setup_tenants):
        """Test that invalid tenant IDs are rejected"""
        
        response = client.get('/api/finance/chart-of-accounts',
                            headers={'X-Tenant-ID': 'invalid_tenant', 'X-User-ID': 'user_1'})
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Invalid tenant' in data['error']
    
    def test_tenant_module_access(self, client, setup_tenants):
        """Test that tenants can only access their activated modules"""
        
        # Activate finance module for tenant A only
        with client.application.app_context():
            module_a = TenantModule(
                tenant_id='tenant_a',
                module_name='finance',
                enabled=True,
                activated_at=datetime.utcnow()
            )
            db.session.add(module_a)
            db.session.commit()
        
        # Tenant A should have access to finance module
        response = client.get('/api/finance/chart-of-accounts',
                            headers={'X-Tenant-ID': 'tenant_a', 'X-User-ID': 'user_1'})
        assert response.status_code == 200
        
        # Tenant B should not have access to finance module
        response = client.get('/api/finance/chart-of-accounts',
                            headers={'X-Tenant-ID': 'tenant_b', 'X-User-ID': 'user_2'})
        assert response.status_code == 403
        data = response.get_json()
        assert 'Module access required' in data['error']
    
    def test_tenant_settings_isolation(self, client, setup_tenants):
        """Test that tenant settings are isolated"""
        
        # Create settings for tenant A
        with client.application.app_context():
            from modules.core.tenant_models import TenantSettings
            
            setting_a = TenantSettings(
                tenant_id='tenant_a',
                setting_key='currency',
                setting_value='USD',
                setting_type='string'
            )
            setting_b = TenantSettings(
                tenant_id='tenant_b',
                setting_key='currency',
                setting_value='EUR',
                setting_type='string'
            )
            
            db.session.add(setting_a)
            db.session.add(setting_b)
            db.session.commit()
        
        # Get settings for tenant A
        response = client.get('/api/tenant/tenants/tenant_a/settings',
                            headers={'X-Tenant-ID': 'tenant_a', 'X-User-ID': 'user_1'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['setting_value'] == 'USD'
        
        # Get settings for tenant B
        response = client.get('/api/tenant/tenants/tenant_b/settings',
                            headers={'X-Tenant-ID': 'tenant_b', 'X-User-ID': 'user_2'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['setting_value'] == 'EUR'
    
    def test_cross_tenant_data_creation(self, client, setup_tenants):
        """Test that data cannot be created for other tenants"""
        
        # Try to create data for tenant B using tenant A context
        new_account_data = {
            'account_code': '2000',
            'account_name': 'Unauthorized Account',
            'account_type': 'Liability',
            'is_active': True
        }
        
        response = client.post('/api/finance/chart-of-accounts',
                            headers={'X-Tenant-ID': 'tenant_a', 'X-User-ID': 'user_1'},
                            json=new_account_data)
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verify the account was created with tenant A's ID, not tenant B's
        assert data['id'] is not None
        
        # Verify in database that the account has tenant A's ID
        with client.application.app_context():
            account = ChartOfAccounts.query.get(data['id'])
            assert account.tenant_id == 'tenant_a'
    
    def test_tenant_switching(self, client, setup_tenants):
        """Test that users can switch between their tenants"""
        
        # Create user that belongs to both tenants
        with client.application.app_context():
            user_tenant_ab = UserTenant(
                user_id='user_3',
                tenant_id='tenant_a',
                role='user',
                is_default=False
            )
            user_tenant_ba = UserTenant(
                user_id='user_3',
                tenant_id='tenant_b',
                role='user',
                is_default=True
            )
            
            db.session.add(user_tenant_ab)
            db.session.add(user_tenant_ba)
            db.session.commit()
        
        # Switch to tenant A
        response = client.post('/api/tenant/switch-tenant/tenant_a',
                            headers={'X-Tenant-ID': 'tenant_b', 'X-User-ID': 'user_3'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['tenant_id'] == 'tenant_a'
        
        # Switch to tenant B
        response = client.post('/api/tenant/switch-tenant/tenant_b',
                            headers={'X-Tenant-ID': 'tenant_a', 'X-User-ID': 'user_3'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['tenant_id'] == 'tenant_b'
    
    def test_tenant_permissions(self, client, setup_tenants):
        """Test that tenant-specific permissions work correctly"""
        
        # Create user with limited permissions for tenant A
        with client.application.app_context():
            limited_user_tenant = UserTenant(
                user_id='limited_user',
                tenant_id='tenant_a',
                role='user',
                is_default=True,
                permissions=['finance.accounts.read']  # Only read permission
            )
            
            db.session.add(limited_user_tenant)
            db.session.commit()
        
        # Should be able to read accounts
        response = client.get('/api/finance/chart-of-accounts',
                            headers={'X-Tenant-ID': 'tenant_a', 'X-User-ID': 'limited_user'})
        assert response.status_code == 200
        
        # Should not be able to create accounts
        new_account_data = {
            'account_code': '3000',
            'account_name': 'Test Account',
            'account_type': 'Asset',
            'is_active': True
        }
        
        response = client.post('/api/finance/chart-of-accounts',
                            headers={'X-Tenant-ID': 'tenant_a', 'X-User-ID': 'limited_user'},
                            json=new_account_data)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Permission required' in data['error']

if __name__ == '__main__':
    pytest.main([__file__])












