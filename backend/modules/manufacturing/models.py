# backend/modules/manufacturing/models.py

from app import db
from datetime import datetime
# Use db.JSON for SQLite compatibility

class BillOfMaterials(db.Model):
    """Bill of Materials for manufacturing"""
    __tablename__ = 'bill_of_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    version = db.Column(db.String(50), default='1.0')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bom_items = db.relationship('BOMItem', backref='bom', lazy=True, cascade='all, delete-orphan')
    production_orders = db.relationship('ProductionOrder', backref='bom', lazy=True)

class BOMItem(db.Model):
    """Individual items in a Bill of Materials"""
    __tablename__ = 'bom_items'
    
    id = db.Column(db.Integer, primary_key=True)
    bom_id = db.Column(db.Integer, db.ForeignKey('bill_of_materials.id'), nullable=False)
    component_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit_of_measure = db.Column(db.String(50), default='pcs')
    scrap_factor = db.Column(db.Float, default=0.0)  # Percentage of scrap
    lead_time = db.Column(db.Integer, default=0)  # Days
    cost = db.Column(db.Float, default=0.0)
    sequence = db.Column(db.Integer, default=0)
    
    # Relationships
    component = db.relationship('Product', foreign_keys=[component_id])

class ProductionOrder(db.Model):
    """Production orders for manufacturing"""
    __tablename__ = 'production_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(100), unique=True, nullable=False)
    bom_id = db.Column(db.Integer, db.ForeignKey('bill_of_materials.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    completed_quantity = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='planned')  # planned, in_progress, completed, cancelled
    priority = db.Column(db.Integer, default=5)  # 1-10, 1 being highest
    planned_start_date = db.Column(db.DateTime)
    planned_end_date = db.Column(db.DateTime)
    actual_start_date = db.Column(db.DateTime)
    actual_end_date = db.Column(db.DateTime)
    work_center_id = db.Column(db.Integer, db.ForeignKey('work_centers.id'))
    cost = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', foreign_keys=[product_id])
    work_center = db.relationship('WorkCenter', foreign_keys=[work_center_id])
    operations = db.relationship('ProductionOperation', backref='production_order', lazy=True, cascade='all, delete-orphan')

class WorkCenter(db.Model):
    """Work centers for production"""
    __tablename__ = 'work_centers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Float, default=0.0)  # Hours per day
    efficiency = db.Column(db.Float, default=100.0)  # Percentage
    cost_per_hour = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductionOperation(db.Model):
    """Individual operations in a production order"""
    __tablename__ = 'production_operations'
    
    id = db.Column(db.Integer, primary_key=True)
    production_order_id = db.Column(db.Integer, db.ForeignKey('production_orders.id'), nullable=False)
    operation_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    work_center_id = db.Column(db.Integer, db.ForeignKey('work_centers.id'))
    planned_hours = db.Column(db.Float, default=0.0)
    actual_hours = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='planned')  # planned, in_progress, completed
    sequence = db.Column(db.Integer, default=0)
    setup_time = db.Column(db.Float, default=0.0)
    run_time = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    work_center = db.relationship('WorkCenter', foreign_keys=[work_center_id])

class MaterialRequirementsPlan(db.Model):
    """Material Requirements Planning records"""
    __tablename__ = 'material_requirements_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    gross_requirements = db.Column(db.Float, default=0.0)
    scheduled_receipts = db.Column(db.Float, default=0.0)
    projected_on_hand = db.Column(db.Float, default=0.0)
    net_requirements = db.Column(db.Float, default=0.0)
    planned_order_receipts = db.Column(db.Float, default=0.0)
    planned_order_releases = db.Column(db.Float, default=0.0)
    safety_stock = db.Column(db.Float, default=0.0)
    lead_time = db.Column(db.Integer, default=0)
    lot_size = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', foreign_keys=[product_id])

class SupplyChainNode(db.Model):
    """Supply chain network nodes"""
    __tablename__ = 'supply_chain_nodes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    node_type = db.Column(db.String(50), nullable=False)  # supplier, warehouse, factory, customer
    location = db.Column(db.String(200))
    country = db.Column(db.String(100))
    region = db.Column(db.String(100))
    capacity = db.Column(db.Float, default=0.0)
    lead_time = db.Column(db.Integer, default=0)  # Days
    cost_per_unit = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    coordinates = db.Column(db.JSON)  # Latitude/Longitude
    contact_info = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupplyChainLink(db.Model):
    """Connections between supply chain nodes"""
    __tablename__ = 'supply_chain_links'
    
    id = db.Column(db.Integer, primary_key=True)
    from_node_id = db.Column(db.Integer, db.ForeignKey('supply_chain_nodes.id'), nullable=False)
    to_node_id = db.Column(db.Integer, db.ForeignKey('supply_chain_nodes.id'), nullable=False)
    transport_mode = db.Column(db.String(50))  # truck, ship, air, rail
    lead_time = db.Column(db.Integer, default=0)  # Days
    cost_per_unit = db.Column(db.Float, default=0.0)
    capacity = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    from_node = db.relationship('SupplyChainNode', foreign_keys=[from_node_id])
    to_node = db.relationship('SupplyChainNode', foreign_keys=[to_node_id])

class QualityControl(db.Model):
    """Quality control records"""
    __tablename__ = 'quality_control'
    
    id = db.Column(db.Integer, primary_key=True)
    production_order_id = db.Column(db.Integer, db.ForeignKey('production_orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    inspection_date = db.Column(db.DateTime, nullable=False)
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quantity_inspected = db.Column(db.Float, nullable=False)
    quantity_passed = db.Column(db.Float, default=0.0)
    quantity_failed = db.Column(db.Float, default=0.0)
    defect_types = db.Column(db.JSON)  # Store defect details
    notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')  # pending, passed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    production_order = db.relationship('ProductionOrder', foreign_keys=[production_order_id])
    product = db.relationship('Product', foreign_keys=[product_id])
    inspector = db.relationship('User', foreign_keys=[inspector_id])

class MaintenanceSchedule(db.Model):
    """Equipment maintenance schedules"""
    __tablename__ = 'maintenance_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)  # preventive, corrective, predictive
    scheduled_date = db.Column(db.DateTime, nullable=False)
    completed_date = db.Column(db.DateTime)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    description = db.Column(db.Text)
    cost = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='scheduled')  # scheduled, in_progress, completed, overdue
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', foreign_keys=[equipment_id])
    technician = db.relationship('User', foreign_keys=[technician_id])

class Equipment(db.Model):
    """Manufacturing equipment"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    equipment_type = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    manufacturer = db.Column(db.String(200))
    installation_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    location = db.Column(db.String(200))
    work_center_id = db.Column(db.Integer, db.ForeignKey('work_centers.id'))
    status = db.Column(db.String(50), default='operational')  # operational, maintenance, broken, retired
    capacity = db.Column(db.Float, default=0.0)
    efficiency = db.Column(db.Float, default=100.0)
    cost = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    work_center = db.relationship('WorkCenter', foreign_keys=[work_center_id])
    maintenance_schedules = db.relationship('MaintenanceSchedule', backref='equipment_ref', lazy=True)

# User model is defined in core.models