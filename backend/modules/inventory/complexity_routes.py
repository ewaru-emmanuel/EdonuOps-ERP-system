"""
Progressive Complexity Routes
API endpoints for managing the three-tier system
"""

from flask import Blueprint, request, jsonify
from app import db
from .complexity_service import ProgressiveComplexityService
from .advanced_models import (
    InventorySystemConfig, SimpleWarehouse, BasicLocation, AdvancedWarehouse
)

# Create blueprint
complexity_bp = Blueprint('complexity', __name__)

# ============================================================================
# SYSTEM CONFIGURATION ROUTES
# ============================================================================

@complexity_bp.route('/system/config', methods=['GET'])
def get_system_config():
    """Get current system configuration"""
    try:
        config = ProgressiveComplexityService.get_system_config()
        return jsonify({
            'status': 'success',
            'config': config
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@complexity_bp.route('/system/config', methods=['POST'])
def set_system_config():
    """Set system configuration and complexity tier"""
    try:
        data = request.get_json()
        tier = data.get('complexity_tier', 1)
        business_context = data.get('business_context', {})
        
        config = ProgressiveComplexityService.set_complexity_tier(tier, business_context)
        
        return jsonify({
            'status': 'success',
            'config': config,
            'message': f'System configured for Tier {tier}'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@complexity_bp.route('/system/ui-config', methods=['GET'])
def get_ui_configuration():
    """Get UI configuration based on complexity tier"""
    try:
        ui_config = ProgressiveComplexityService.get_ui_configuration()
        return jsonify({
            'status': 'success',
            'ui_config': ui_config
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ONBOARDING ROUTES
# ============================================================================

@complexity_bp.route('/onboarding/setup', methods=['POST'])
def setup_onboarding():
    """Setup system based on onboarding choices"""
    try:
        data = request.get_json()
        
        # Extract onboarding data
        business_type = data.get('business_type', 'retail')
        inventory_size = data.get('inventory_size', 'small')
        warehouse_count = data.get('warehouse_count', 1)
        location_needs = data.get('location_needs', 'none')  # none, basic, advanced
        
        # Determine tier based on needs
        if location_needs == 'none':
            tier = 1
        elif location_needs == 'basic':
            tier = 2
        elif location_needs == 'advanced':
            tier = 3
        else:
            tier = 1
        
        business_context = {
            'business_type': business_type,
            'inventory_size': inventory_size,
            'warehouse_count': warehouse_count
        }
        
        # Set system configuration
        config = ProgressiveComplexityService.set_complexity_tier(tier, business_context)
        
        # Create default warehouses based on tier
        if tier == 1:
            # Create simple warehouses
            default_warehouses = ['Main Store', 'Backroom', 'Online Stock']
            for warehouse_name in default_warehouses[:warehouse_count]:
                warehouse = SimpleWarehouse(name=warehouse_name, description=f'Default {warehouse_name}')
                db.session.add(warehouse)
        
        elif tier == 2:
            # Create simple warehouses with basic locations
            default_warehouses = ['Main Store', 'Backroom', 'Online Stock']
            for i, warehouse_name in enumerate(default_warehouses[:warehouse_count]):
                warehouse = SimpleWarehouse(name=warehouse_name, description=f'Default {warehouse_name}')
                db.session.add(warehouse)
                db.session.flush()  # Get the ID
                
                # Add basic locations
                basic_locations = ['Aisle 1', 'Shelf A', 'Shelf B', 'Storage Area']
                for location_name in basic_locations:
                    location = BasicLocation(
                        warehouse_id=warehouse.id,
                        location_code=location_name.replace(' ', '_').upper(),
                        location_name=location_name,
                        description=f'Default location in {warehouse_name}'
                    )
                    db.session.add(location)
        
        elif tier == 3:
            # Create advanced warehouse structure
            warehouse = AdvancedWarehouse(
                code='MAIN',
                name='Main Warehouse',
                description='Primary distribution center',
                warehouse_type='storage'
            )
            db.session.add(warehouse)
            db.session.flush()
            
            # Add zones, aisles, racks, levels, and locations
            # This would be a more complex setup for advanced WMS
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'config': config,
            'message': f'System setup complete for {business_type} business (Tier {tier})'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# TIER-SPECIFIC ROUTES
# ============================================================================

@complexity_bp.route('/tier1/warehouses', methods=['GET'])
def get_simple_warehouses():
    """Get simple warehouses for Tier 1"""
    try:
        warehouses = SimpleWarehouse.query.filter_by(is_active=True).all()
        return jsonify([{
            'id': warehouse.id,
            'name': warehouse.name,
            'description': warehouse.description
        } for warehouse in warehouses]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@complexity_bp.route('/tier1/warehouses', methods=['POST'])
def create_simple_warehouse():
    """Create simple warehouse for Tier 1"""
    try:
        data = request.get_json()
        warehouse = SimpleWarehouse(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(warehouse)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'warehouse': {
                'id': warehouse.id,
                'name': warehouse.name,
                'description': warehouse.description
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@complexity_bp.route('/tier2/locations', methods=['GET'])
def get_basic_locations():
    """Get basic locations for Tier 2"""
    try:
        locations = BasicLocation.query.join(SimpleWarehouse).filter(
            BasicLocation.is_active == True
        ).all()
        
        return jsonify([{
            'id': location.id,
            'location_code': location.location_code,
            'location_name': location.location_name,
            'description': location.description,
            'warehouse': {
                'id': location.warehouse.id,
                'name': location.warehouse.name
            }
        } for location in locations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@complexity_bp.route('/tier2/locations', methods=['POST'])
def create_basic_location():
    """Create basic location for Tier 2"""
    try:
        data = request.get_json()
        location = BasicLocation(
            warehouse_id=data['warehouse_id'],
            location_code=data['location_code'],
            location_name=data['location_name'],
            description=data.get('description', ''),
            location_type=data.get('location_type', 'storage')
        )
        db.session.add(location)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'location': {
                'id': location.id,
                'location_code': location.location_code,
                'location_name': location.location_name,
                'warehouse_id': location.warehouse_id
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ============================================================================
# STOCK LEVEL ROUTES - TIER-ADAPTIVE
# ============================================================================

@complexity_bp.route('/stock-levels', methods=['GET'])
def get_adaptive_stock_levels():
    """Get stock levels adapted to current complexity tier"""
    try:
        product_id = request.args.get('product_id', type=int)
        warehouse_id = request.args.get('warehouse_id', type=int)
        
        stock_levels = ProgressiveComplexityService.get_stock_levels(product_id, warehouse_id)
        
        return jsonify({
            'status': 'success',
            'stock_levels': stock_levels,
            'count': len(stock_levels)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@complexity_bp.route('/transactions', methods=['POST'])
def create_adaptive_transaction():
    """Create stock transaction adapted to current complexity tier"""
    try:
        data = request.get_json()
        result = ProgressiveComplexityService.create_stock_transaction(data)
        
        return jsonify(result), 200 if result['status'] == 'success' else 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# UPGRADE ROUTES
# ============================================================================

@complexity_bp.route('/upgrade/tier', methods=['POST'])
def upgrade_complexity_tier():
    """Upgrade system to next complexity tier"""
    try:
        data = request.get_json()
        current_tier = data.get('current_tier', 1)
        target_tier = data.get('target_tier', current_tier + 1)
        
        if target_tier <= current_tier:
            return jsonify({'error': 'Target tier must be higher than current tier'}), 400
        
        if target_tier > 3:
            return jsonify({'error': 'Maximum tier is 3'}), 400
        
        # Set new tier
        config = ProgressiveComplexityService.set_complexity_tier(target_tier)
        
        return jsonify({
            'status': 'success',
            'config': config,
            'message': f'System upgraded from Tier {current_tier} to Tier {target_tier}'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

