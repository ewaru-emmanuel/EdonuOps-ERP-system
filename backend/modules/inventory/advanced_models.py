from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, and_, or_
from sqlalchemy import TypeDecorator, String
import json

# Conditional JSON type that works with both PostgreSQL and SQLite
class JSONType(TypeDecorator):
    impl = String
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None
    
    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None

# ============================================================================
# SYSTEM CONFIGURATION - PROGRESSIVE COMPLEXITY
# ============================================================================

class InventorySystemConfig(db.Model):
    """System configuration for progressive complexity tiers"""
    __tablename__ = 'inventory_system_config'
    id = db.Column(db.Integer, primary_key=True)
    
    # Complexity Tier (1=Inventory Only, 2=Basic Location, 3=Advanced WMS)
    complexity_tier = db.Column(db.Integer, default=1)
    
    # Feature Flags
    enable_location_tracking = db.Column(db.Boolean, default=False)
    enable_warehouse_hierarchy = db.Column(db.Boolean, default=False)
    enable_mobile_wms = db.Column(db.Boolean, default=False)
    enable_advanced_analytics = db.Column(db.Boolean, default=False)
    
    # UI Configuration
    show_warehouse_operations = db.Column(db.Boolean, default=False)
    show_location_management = db.Column(db.Boolean, default=False)
    show_advanced_reports = db.Column(db.Boolean, default=False)
    
    # Business Context
    business_type = db.Column(db.String(50))  # retail, wholesale, manufacturing, etc.
    inventory_size = db.Column(db.String(20))  # small, medium, large
    warehouse_count = db.Column(db.Integer, default=1)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# CORE INVENTORY MODELS - UNIVERSAL ACROSS ALL TIERS
# ============================================================================

class UnitOfMeasure(db.Model):
    """Multi-level Unit of Measure management"""
    __tablename__ = 'inventory_uom'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # EA, CS, PLT
    name = db.Column(db.String(100), nullable=False)  # Each, Case, Pallet
    description = db.Column(db.Text)
    is_base_unit = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UOMConversion(db.Model):
    """UoM conversion factors"""
    __tablename__ = 'inventory_uom_conversions'
    id = db.Column(db.Integer, primary_key=True)
    from_uom_id = db.Column(db.Integer, db.ForeignKey('inventory_uom.id'), nullable=False)
    to_uom_id = db.Column(db.Integer, db.ForeignKey('inventory_uom.id'), nullable=False)
    conversion_factor = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    from_uom = db.relationship('UnitOfMeasure', foreign_keys=[from_uom_id])
    to_uom = db.relationship('UnitOfMeasure', foreign_keys=[to_uom_id])

class ProductCategory(db.Model):
    """Enhanced product categories with hierarchy"""
    __tablename__ = 'inventory_product_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('inventory_product_categories.id'))
    is_active = db.Column(db.Boolean, default=True)
    abc_class = db.Column(db.String(1))  # A, B, C for ABC analysis
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # User isolation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    children = db.relationship('ProductCategory', backref=db.backref('parent', remote_side=[id]))

class InventoryProduct(db.Model):
    """Advanced product management - UNIVERSAL ACROSS ALL TIERS"""
    __tablename__ = 'inventory_products'
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=True)
    product_id = db.Column(db.String(50), unique=True, nullable=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_product_categories.id'))
    
    # Product Type and Tracking
    product_type = db.Column(db.String(20), default='standard')  # standard, serialized, lot_tracked
    track_serial_numbers = db.Column(db.Boolean, default=False)
    track_lots = db.Column(db.Boolean, default=False)
    track_expiry = db.Column(db.Boolean, default=False)
    
    # UoM Management
    base_uom_id = db.Column(db.Integer, db.ForeignKey('inventory_uom.id'), nullable=False)
    purchase_uom_id = db.Column(db.Integer, db.ForeignKey('inventory_uom.id'))
    sales_uom_id = db.Column(db.Integer, db.ForeignKey('inventory_uom.id'))
    
    # Costing
    cost_method = db.Column(db.String(20), default='FIFO')  # FIFO, LIFO, Average, Standard
    standard_cost = db.Column(db.Float, default=0.0)
    current_cost = db.Column(db.Float, default=0.0)
    
    # Multi-currency support
    cost_currency = db.Column(db.String(3), default='USD')
    base_currency_cost = db.Column(db.Float, default=0.0)
    
    # Inventory Control
    min_stock_level = db.Column(db.Float, default=0.0)
    max_stock_level = db.Column(db.Float, default=0.0)
    reorder_point = db.Column(db.Float, default=0.0)
    reorder_quantity = db.Column(db.Float, default=0.0)
    lead_time_days = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # User isolation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('ProductCategory', backref='products')
    base_uom = db.relationship('UnitOfMeasure', foreign_keys=[base_uom_id])
    purchase_uom = db.relationship('UnitOfMeasure', foreign_keys=[purchase_uom_id])
    sales_uom = db.relationship('UnitOfMeasure', foreign_keys=[sales_uom_id])

class ProductVariant(db.Model):
    """Product variants (Size, Color, etc.)"""
    __tablename__ = 'inventory_product_variants'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    variant_sku = db.Column(db.String(50), unique=True, nullable=False)
    variant_name = db.Column(db.String(200), nullable=False)
    attributes = db.Column(JSONType)  # {"size": "L", "color": "Red"}
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('InventoryProduct', backref='variants')

# ============================================================================
# TIER 1: INVENTORY ONLY - SIMPLE WAREHOUSE MANAGEMENT
# ============================================================================

class SimpleWarehouse(db.Model):
    """Tier 1: Simple warehouse names for basic inventory tracking"""
    __tablename__ = 'inventory_simple_warehouses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # "Main Store", "Backroom", "Online Stock"
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================================
# TIER 2: BASIC LOCATION TRACKING
# ============================================================================

class BasicLocation(db.Model):
    """Tier 2: Simple location tracking without complex hierarchy"""
    __tablename__ = 'inventory_basic_locations'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'), nullable=False)
    location_code = db.Column(db.String(50), nullable=False)  # "Aisle 1", "Shelf B", "Bin 3"
    location_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location_type = db.Column(db.String(20), default='storage')  # storage, receiving, shipping
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    warehouse = db.relationship('SimpleWarehouse', backref='basic_locations')

# ============================================================================
# TIER 3: ADVANCED WMS - FULL HIERARCHY
# ============================================================================

class AdvancedWarehouse(db.Model):
    """Tier 3: Advanced warehouse with full hierarchy"""
    __tablename__ = 'inventory_advanced_warehouses'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(100))
    
    # Capacity Management
    total_capacity = db.Column(db.Float, default=0.0)
    used_capacity = db.Column(db.Float, default=0.0)
    capacity_uom_id = db.Column(db.Integer, db.ForeignKey('inventory_uom.id'))
    
    # Warehouse Type
    warehouse_type = db.Column(db.String(20), default='storage')  # storage, cross_dock, production
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # User isolation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    capacity_uom = db.relationship('UnitOfMeasure', backref='advanced_warehouses')

class Zone(db.Model):
    """Tier 3: Warehouse zones"""
    __tablename__ = 'inventory_zones'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_warehouses.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    zone_type = db.Column(db.String(20), default='storage')  # storage, picking, receiving, shipping
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    warehouse = db.relationship('AdvancedWarehouse', backref='zones')

class Aisle(db.Model):
    """Tier 3: Warehouse aisles"""
    __tablename__ = 'inventory_aisles'
    id = db.Column(db.Integer, primary_key=True)
    zone_id = db.Column(db.Integer, db.ForeignKey('inventory_zones.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    zone = db.relationship('Zone', backref='aisles')

class Rack(db.Model):
    """Tier 3: Warehouse racks"""
    __tablename__ = 'inventory_racks'
    id = db.Column(db.Integer, primary_key=True)
    aisle_id = db.Column(db.Integer, db.ForeignKey('inventory_aisles.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    aisle = db.relationship('Aisle', backref='racks')

class Level(db.Model):
    """Tier 3: Rack levels"""
    __tablename__ = 'inventory_levels'
    id = db.Column(db.Integer, primary_key=True)
    rack_id = db.Column(db.Integer, db.ForeignKey('inventory_racks.id'), nullable=False)
    level_number = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    rack = db.relationship('Rack', backref='levels')

class AdvancedLocation(db.Model):
    """Tier 3: Specific storage locations (bins) with full hierarchy"""
    __tablename__ = 'inventory_advanced_locations'
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('inventory_levels.id'), nullable=False)
    location_code = db.Column(db.String(20), unique=True, nullable=False)  # A01-B02-C03
    location_name = db.Column(db.String(100), nullable=False)
    
    # Location Barcode (CRITICAL for mobile WMS)
    barcode = db.Column(db.String(50), unique=True, nullable=False)  # Physical barcode on bin
    
    # Location Properties
    location_type = db.Column(db.String(20), default='storage')  # storage, picking, receiving, shipping, quarantine, bulk_storage
    max_capacity = db.Column(db.Float, default=0.0)
    current_capacity = db.Column(db.Float, default=0.0)
    capacity_uom_id = db.Column(db.Integer, db.ForeignKey('inventory_uom.id'))
    
    # Capacity Constraints
    max_weight = db.Column(db.Float, default=0.0)
    max_volume = db.Column(db.Float, default=0.0)
    current_weight = db.Column(db.Float, default=0.0)
    current_volume = db.Column(db.Float, default=0.0)
    
    # Location Status
    is_active = db.Column(db.Boolean, default=True)
    is_restricted = db.Column(db.Boolean, default=False)
    is_overflow = db.Column(db.Boolean, default=False)
    
    # Operational Intelligence Metrics
    popularity_score = db.Column(db.Float, default=0.0)
    last_activity = db.Column(db.DateTime)
    activity_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    level = db.relationship('Level', backref='advanced_locations')
    capacity_uom = db.relationship('UnitOfMeasure', backref='advanced_locations')

# ============================================================================
# UNIVERSAL STOCK LEVELS - ADAPTS TO ALL TIERS
# ============================================================================

class StockLevel(db.Model):
    """Universal stock levels that adapt to complexity tier"""
    __tablename__ = 'inventory_stock_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('inventory_product_variants.id'))
    
    # TIER 1: Simple warehouse tracking (location_id = NULL)
    simple_warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'))
    
    # TIER 2: Basic location tracking
    basic_location_id = db.Column(db.Integer, db.ForeignKey('inventory_basic_locations.id'))
    
    # TIER 3: Advanced location tracking
    advanced_location_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_locations.id'))
    
    lot_batch_id = db.Column(db.Integer, db.ForeignKey('inventory_lot_batches.id'))
    
    # Quantities (Real-time, updated by transactions)
    quantity_on_hand = db.Column(db.Float, default=0.0)
    quantity_allocated = db.Column(db.Float, default=0.0)  # Reserved for orders
    quantity_available = db.Column(db.Float, default=0.0)  # On hand - allocated
    quantity_in_transit = db.Column(db.Float, default=0.0)
    
    # Costing
    unit_cost = db.Column(db.Float, default=0.0)
    total_value = db.Column(db.Float, default=0.0)
    cost_currency = db.Column(db.String(3), default='USD')
    base_currency_unit_cost = db.Column(db.Float, default=0.0)
    base_currency_total_value = db.Column(db.Float, default=0.0)
    
    # Last Updated
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # User isolation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='stock_levels')
    variant = db.relationship('ProductVariant', backref='stock_levels')
    simple_warehouse = db.relationship('SimpleWarehouse', backref='stock_levels')
    basic_location = db.relationship('BasicLocation', backref='stock_levels')
    advanced_location = db.relationship('AdvancedLocation', backref='stock_levels')
    lot_batch = db.relationship('LotBatch', backref='stock_levels')

# ============================================================================
# UNIVERSAL TRANSACTIONS - ADAPTS TO ALL TIERS
# ============================================================================

class InventoryTransaction(db.Model):
    """Universal inventory transactions that adapt to complexity tier"""
    __tablename__ = 'inventory_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(20), nullable=False)  # receive, issue, transfer, adjustment, count
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Product Information
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('inventory_product_variants.id'))
    lot_batch_id = db.Column(db.Integer, db.ForeignKey('inventory_lot_batches.id'))
    
    # TIER 1: Simple warehouse tracking
    from_simple_warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'))
    to_simple_warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'))
    
    # TIER 2: Basic location tracking
    from_basic_location_id = db.Column(db.Integer, db.ForeignKey('inventory_basic_locations.id'))
    to_basic_location_id = db.Column(db.Integer, db.ForeignKey('inventory_basic_locations.id'))
    
    # TIER 3: Advanced location tracking
    from_advanced_location_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_locations.id'))
    to_advanced_location_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_locations.id'))
    
    # Quantities
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, default=0.0)
    total_cost = db.Column(db.Float, default=0.0)
    
    # Multi-currency support
    transaction_currency = db.Column(db.String(3), default='USD')
    exchange_rate = db.Column(db.Float, default=1.0)
    base_currency_unit_cost = db.Column(db.Float, default=0.0)
    base_currency_total_cost = db.Column(db.Float, default=0.0)
    
    # Reference Information
    reference_number = db.Column(db.String(50))  # PO, SO, Transfer, etc.
    reference_type = db.Column(db.String(20))  # purchase_order, sales_order, transfer, adjustment
    notes = db.Column(db.Text)
    
    # User tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # User isolation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('InventoryProduct', backref='transactions')
    variant = db.relationship('ProductVariant', backref='transactions')
    lot_batch = db.relationship('LotBatch', backref='transactions')
    
    # Tier 1 relationships
    from_simple_warehouse = db.relationship('SimpleWarehouse', foreign_keys=[from_simple_warehouse_id], backref='outgoing_transactions')
    to_simple_warehouse = db.relationship('SimpleWarehouse', foreign_keys=[to_simple_warehouse_id], backref='incoming_transactions')
    
    # Tier 2 relationships
    from_basic_location = db.relationship('BasicLocation', foreign_keys=[from_basic_location_id], backref='outgoing_transactions')
    to_basic_location = db.relationship('BasicLocation', foreign_keys=[to_basic_location_id], backref='incoming_transactions')
    
    # Tier 3 relationships
    from_advanced_location = db.relationship('AdvancedLocation', foreign_keys=[from_advanced_location_id], backref='outgoing_transactions')
    to_advanced_location = db.relationship('AdvancedLocation', foreign_keys=[to_advanced_location_id], backref='incoming_transactions')

# ============================================================================
# TRACKING MODELS - UNIVERSAL ACROSS ALL TIERS
# ============================================================================

class SerialNumber(db.Model):
    """Serial number tracking"""
    __tablename__ = 'inventory_serial_numbers'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('inventory_product_variants.id'))
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    
    # Location tracking adapts to tier
    simple_warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_simple_warehouses.id'))
    basic_location_id = db.Column(db.Integer, db.ForeignKey('inventory_basic_locations.id'))
    advanced_location_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_locations.id'))
    
    current_status = db.Column(db.String(20), default='available')  # available, reserved, sold
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('InventoryProduct', backref='serial_numbers')
    variant = db.relationship('ProductVariant', backref='serial_numbers')
    simple_warehouse = db.relationship('SimpleWarehouse', backref='serial_numbers')
    basic_location = db.relationship('BasicLocation', backref='serial_numbers')
    advanced_location = db.relationship('AdvancedLocation', backref='serial_numbers')

class LotBatch(db.Model):
    """Lot/Batch tracking"""
    __tablename__ = 'inventory_lot_batches'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('inventory_product_variants.id'))
    lot_number = db.Column(db.String(100), nullable=False)
    batch_number = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    manufacture_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('InventoryProduct', backref='lot_batches')
    variant = db.relationship('ProductVariant', backref='lot_batches')

# ============================================================================
# BUSINESS RELATIONSHIPS - UNIVERSAL ACROSS ALL TIERS
# ============================================================================

class InventorySupplier(db.Model):
    """Supplier management for inventory"""
    __tablename__ = 'inventory_suppliers'
    id = db.Column(db.Integer, primary_key=True)
    supplier_code = db.Column(db.String(50), unique=True, nullable=False)
    supplier_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryCustomer(db.Model):
    """Customer management for inventory"""
    __tablename__ = 'inventory_customers'
    id = db.Column(db.Integer, primary_key=True)
    customer_code = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============================================================================
# COMPLIANCE & ANALYTICS - UNIVERSAL ACROSS ALL TIERS
# ============================================================================

class InventoryAuditTrail(db.Model):
    """Audit trail for inventory changes"""
    __tablename__ = 'inventory_audit_trail'
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    action = db.Column(db.String(20), nullable=False)  # create, update, delete
    old_values = db.Column(db.Text)
    new_values = db.Column(db.Text)
    user_id = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryReport(db.Model):
    """Inventory reports and analytics"""
    __tablename__ = 'inventory_reports'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False)  # stock_level, movement, valuation, etc.
    report_name = db.Column(db.String(200), nullable=False)
    report_data = db.Column(JSONType)
    generated_by = db.Column(db.String(100))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

# ============================================================================
# ADVANCED WMS MODELS - TIER 3 ONLY
# ============================================================================

class WarehouseActivity(db.Model):
    """Warehouse activity tracking for advanced WMS"""
    __tablename__ = 'inventory_warehouse_activities'
    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_warehouses.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_locations.id'))
    user_id = db.Column(db.String(100))
    activity_type = db.Column(db.String(50), nullable=False)  # pick, putaway, transfer, count
    activity_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    efficiency_score = db.Column(db.Float, default=0.0)
    duration_seconds = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    warehouse = db.relationship('AdvancedWarehouse', backref='activities')
    location = db.relationship('AdvancedLocation', backref='activities')

class PredictiveStockout(db.Model):
    """Predictive stockout analysis"""
    __tablename__ = 'inventory_predictive_stockouts'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('inventory_products.id'), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_locations.id'))
    predicted_stockout_date = db.Column(db.Date, nullable=False)
    days_until_stockout = db.Column(db.Integer, nullable=False)
    current_stock = db.Column(db.Float, default=0.0)
    daily_consumption_rate = db.Column(db.Float, default=0.0)
    alert_level = db.Column(db.String(20), default='warning')  # info, warning, critical
    confidence_score = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    product = db.relationship('InventoryProduct', backref='predictive_stockouts')
    location = db.relationship('AdvancedLocation', backref='predictive_stockouts')

class PickerPerformance(db.Model):
    """Picker performance tracking"""
    __tablename__ = 'inventory_picker_performances'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('inventory_advanced_warehouses.id'), nullable=False)
    performance_date = db.Column(db.Date, nullable=False)
    total_picks = db.Column(db.Integer, default=0)
    total_items_picked = db.Column(db.Integer, default=0)
    total_pick_time_seconds = db.Column(db.Integer, default=0)
    efficiency_score = db.Column(db.Float, default=0.0)
    picks_per_hour = db.Column(db.Float, default=0.0)
    warehouse_average_picks_per_hour = db.Column(db.Float, default=0.0)
    accuracy_rate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    warehouse = db.relationship('AdvancedWarehouse', backref='picker_performances')
