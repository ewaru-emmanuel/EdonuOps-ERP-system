from app import db
from datetime import datetime
# Remove PostgreSQL-specific import for SQLite compatibility

class Category(db.Model):
    __tablename__ = 'product_categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # User isolation
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Multi-tenancy support
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('product_categories.id'))
    price = db.Column(db.Float, default=0.0)  # Selling price
    unit = db.Column(db.String(20), default='pcs')  # pcs, kg, m, etc.
    cost_method = db.Column(db.String(20), default='FIFO')  # FIFO, Weighted Average
    standard_cost = db.Column(db.Float, default=0.0)
    current_cost = db.Column(db.Float, default=0.0)
    current_stock = db.Column(db.Float, default=0.0)  # Current stock quantity
    min_stock = db.Column(db.Float, default=0.0)
    max_stock = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')  # active, inactive, discontinued
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # User isolation
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Multi-tenancy support
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = db.relationship('Category', backref='products')
    inventory_transactions = db.relationship('BasicInventoryTransaction', backref='product')

class BasicInventoryTransaction(db.Model):
    __tablename__ = 'basic_inventory_transactions'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # IN, OUT, ADJUSTMENT
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    reference_type = db.Column(db.String(50))  # PO, SO, ADJUSTMENT, etc.
    reference_id = db.Column(db.Integer)  # ID of the reference document
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), default=1)
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Multi-tenancy support
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    warehouse = db.relationship('Warehouse', backref='basic_inventory_transactions')

class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # IN, OUT, TRANSFER, ADJUSTMENT
    quantity = db.Column(db.Float, nullable=False)
    unit_cost = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    reference_type = db.Column(db.String(50))  # PO, SO, TRANSFER, ADJUSTMENT
    reference_id = db.Column(db.Integer)
    from_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))  # For transfers
    to_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'))  # For transfers
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Multi-tenancy support
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    product = db.relationship('Product', backref='stock_movements')
    warehouse = db.relationship('Warehouse', foreign_keys=[warehouse_id], backref='stock_movements')
    from_warehouse = db.relationship('Warehouse', foreign_keys=[from_warehouse_id])
    to_warehouse = db.relationship('Warehouse', foreign_keys=[to_warehouse_id])

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))  # Added location field
    capacity = db.Column(db.Integer)  # Added capacity field
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # User isolation
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Multi-tenancy support
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
