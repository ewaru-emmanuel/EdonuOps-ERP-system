#!/usr/bin/env python3
"""
Advanced Inventory Database Initialization Script
Creates all inventory tables and seeds with enterprise-grade sample data
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from modules.inventory.advanced_models import (
    UnitOfMeasure, UOMConversion, ProductCategory, Product, ProductVariant,
    SerialNumber, LotBatch, AdvancedWarehouse, Zone, Aisle, Rack, Level, Location,
    StockLevel, AdvancedInventoryTransaction, PickList, PickListLine, CycleCount,
    CycleCountLine, BillOfMaterials, Kit, PurchaseOrder,
    PurchaseOrderLine, GoodsReceipt, GoodsReceiptLine, SalesOrder,
    SalesOrderLine, LandedCost, LandedCostAllocation, Supplier,
    WarehouseActivity, PredictiveStockout, PickerPerformance
)

def init_database():
    """Initialize the inventory database with all tables"""
    print("🏭 Initializing Advanced Inventory Database...")
    
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        print("🗑️  Dropping existing tables...")
        db.drop_all()
        
        print("🏗️  Creating new tables...")
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Seed with sample data
        print("🌱 Seeding sample data...")
        seed_sample_data()
        
        print("🎉 Advanced Inventory Database initialization complete!")

def seed_sample_data():
    """Seed the database with enterprise-grade sample data"""
    
    # Create Unit of Measures
    print("📏 Creating Units of Measure...")
    uoms = [
        UnitOfMeasure(name='Each', code='EA', description='Individual unit'),
        UnitOfMeasure(name='Box', code='BOX', description='Box of items'),
        UnitOfMeasure(name='Pallet', code='PAL', description='Pallet of items'),
        UnitOfMeasure(name='Kilogram', code='KG', description='Weight in kilograms'),
        UnitOfMeasure(name='Liter', code='L', description='Volume in liters'),
        UnitOfMeasure(name='Meter', code='M', description='Length in meters')
    ]
    
    for uom in uoms:
        db.session.add(uom)
    db.session.commit()
    
    # Create UOM Conversions
    print("🔄 Creating UOM Conversions...")
    conversions = [
        UOMConversion(from_uom_id=1, to_uom_id=2, conversion_factor=12.0, description='12 each = 1 box'),
        UOMConversion(from_uom_id=2, to_uom_id=3, conversion_factor=50.0, description='50 boxes = 1 pallet'),
        UOMConversion(from_uom_id=1, to_uom_id=4, conversion_factor=0.5, description='1 each = 0.5 kg'),
    ]
    
    for conv in conversions:
        db.session.add(conv)
    db.session.commit()
    
    # Create Product Categories
    print("📂 Creating Product Categories...")
    categories = [
        ProductCategory(name='Electronics', description='Electronic devices and components', abc_classification='A'),
        ProductCategory(name='Clothing', description='Apparel and accessories', abc_classification='B'),
        ProductCategory(name='Home & Garden', description='Home improvement and garden supplies', abc_classification='C'),
        ProductCategory(name='Automotive', description='Automotive parts and accessories', abc_classification='B'),
        ProductCategory(name='Sports & Outdoors', description='Sports equipment and outdoor gear', abc_classification='C')
    ]
    
    for cat in categories:
        db.session.add(cat)
    db.session.commit()
    
    # Create Products
    print("📦 Creating Products...")
    products = [
        Product(
            sku='LAPTOP-001',
            name='Laptop Pro X1',
            description='High-performance laptop for professionals',
            category_id=1,
            base_uom_id=1,
            cost_price=1200.00,
            selling_price=1500.00,
            min_stock_level=10,
            max_stock_level=100,
            reorder_point=15,
            tracking_type='serial',
            is_active=True
        ),
        Product(
            sku='MOUSE-001',
            name='Wireless Mouse',
            description='Ergonomic wireless mouse',
            category_id=1,
            base_uom_id=1,
            cost_price=25.00,
            selling_price=35.00,
            min_stock_level=50,
            max_stock_level=500,
            reorder_point=75,
            tracking_type='lot',
            is_active=True
        ),
        Product(
            sku='TSHIRT-001',
            name='Cotton T-Shirt',
            description='Comfortable cotton t-shirt',
            category_id=2,
            base_uom_id=1,
            cost_price=8.00,
            selling_price=15.00,
            min_stock_level=100,
            max_stock_level=1000,
            reorder_point=150,
            tracking_type='none',
            is_active=True
        ),
        Product(
            sku='TOOL-001',
            name='Hammer',
            description='Standard claw hammer',
            category_id=3,
            base_uom_id=1,
            cost_price=15.00,
            selling_price=25.00,
            min_stock_level=20,
            max_stock_level=200,
            reorder_point=30,
            tracking_type='none',
            is_active=True
        ),
        Product(
            sku='OIL-001',
            name='Motor Oil 5W-30',
            description='Synthetic motor oil',
            category_id=4,
            base_uom_id=5,
            cost_price=8.00,
            selling_price=12.00,
            min_stock_level=50,
            max_stock_level=500,
            reorder_point=75,
            tracking_type='lot',
            is_active=True
        )
    ]
    
    for product in products:
        db.session.add(product)
    db.session.commit()
    
    # Create Product Variants
    print("🎨 Creating Product Variants...")
    variants = [
        ProductVariant(
            product_id=1,
            sku='LAPTOP-001-16GB',
            name='Laptop Pro X1 - 16GB RAM',
            attributes={'ram': '16GB', 'storage': '512GB SSD'},
            cost_price=1300.00,
            selling_price=1600.00
        ),
        ProductVariant(
            product_id=1,
            sku='LAPTOP-001-32GB',
            name='Laptop Pro X1 - 32GB RAM',
            attributes={'ram': '32GB', 'storage': '1TB SSD'},
            cost_price=1500.00,
            selling_price=1800.00
        ),
        ProductVariant(
            product_id=2,
            sku='MOUSE-001-BLACK',
            name='Wireless Mouse - Black',
            attributes={'color': 'Black'},
            cost_price=25.00,
            selling_price=35.00
        ),
        ProductVariant(
            product_id=2,
            sku='MOUSE-001-WHITE',
            name='Wireless Mouse - White',
            attributes={'color': 'White'},
            cost_price=25.00,
            selling_price=35.00
        )
    ]
    
    for variant in variants:
        db.session.add(variant)
    db.session.commit()
    
    # Create Warehouse Hierarchy
    print("🏢 Creating Warehouse Hierarchy...")
    warehouse = Warehouse(
        name='Main Distribution Center',
        code='MDC-001',
        address='123 Warehouse Blvd, Industrial City, IC 12345',
        contact_person='John Warehouse',
        contact_email='warehouse@company.com',
        contact_phone='555-0123',
        capacity_sqft=50000,
        is_active=True
    )
    db.session.add(warehouse)
    db.session.commit()
    
    # Create Zones
    zones = [
        Zone(name='Zone A', warehouse_id=warehouse.id, description='Electronics and high-value items'),
        Zone(name='Zone B', warehouse_id=warehouse.id, description='Clothing and apparel'),
        Zone(name='Zone C', warehouse_id=warehouse.id, description='Home and garden supplies'),
        Zone(name='Zone D', warehouse_id=warehouse.id, description='Automotive parts'),
        Zone(name='Zone E', warehouse_id=warehouse.id, description='Bulk storage and pallets')
    ]
    
    for zone in zones:
        db.session.add(zone)
    db.session.commit()
    
    # Create Aisles
    aisles = []
    for zone in zones:
        for i in range(1, 4):  # 3 aisles per zone
            aisle = Aisle(
                name=f'{zone.name}-Aisle-{i:02d}',
                zone_id=zone.id,
                description=f'Aisle {i} in {zone.name}'
            )
            aisles.append(aisle)
            db.session.add(aisle)
    db.session.commit()
    
    # Create Racks
    racks = []
    for aisle in aisles:
        for i in range(1, 6):  # 5 racks per aisle
            rack = Rack(
                name=f'{aisle.name}-Rack-{i:02d}',
                aisle_id=aisle.id,
                description=f'Rack {i} in {aisle.name}'
            )
            racks.append(rack)
            db.session.add(rack)
    db.session.commit()
    
    # Create Levels
    levels = []
    for rack in racks:
        for i in range(1, 4):  # 3 levels per rack
            level = Level(
                name=f'{rack.name}-Level-{i}',
                rack_id=rack.id,
                description=f'Level {i} in {rack.name}'
            )
            levels.append(level)
            db.session.add(level)
    db.session.commit()
    
    # Create Locations
    print("📍 Creating Storage Locations...")
    locations = []
    for level in levels:
        for i in range(1, 6):  # 5 locations per level
            location = Location(
                name=f'{level.name}-Loc-{i:02d}',
                level_id=level.id,
                barcode=f'LOC-{level.id:03d}-{i:02d}',
                location_type='PICKING' if i <= 3 else 'BULK_STORAGE',
                max_weight=1000.0,
                max_volume=2.0,
                popularity_score=random.uniform(0.1, 1.0)
            )
            locations.append(location)
            db.session.add(location)
    db.session.commit()
    
    # Create Suppliers
    print("🏭 Creating Suppliers...")
    suppliers = [
        Supplier(
            name='TechCorp Electronics',
            code='TECH-001',
            contact_person='Sarah Tech',
            email='orders@techcorp.com',
            phone='555-0101',
            address='456 Tech Street, Tech City, TC 54321',
            payment_terms='Net 30',
            is_active=True
        ),
        Supplier(
            name='Fashion Forward',
            code='FASH-001',
            contact_person='Mike Fashion',
            email='orders@fashionforward.com',
            phone='555-0102',
            address='789 Fashion Ave, Style City, SC 67890',
            payment_terms='Net 45',
            is_active=True
        ),
        Supplier(
            name='Home Depot Supply',
            code='HOME-001',
            contact_person='Lisa Home',
            email='orders@homedepot.com',
            phone='555-0103',
            address='321 Home Street, Home City, HC 13579',
            payment_terms='Net 30',
            is_active=True
        )
    ]
    
    for supplier in suppliers:
        db.session.add(supplier)
    db.session.commit()
    
    # Create Customers
    print("👥 Creating Customers...")
    customers = [
        Customer(
            name='ABC Corporation',
            code='CUST-001',
            contact_person='John Customer',
            email='orders@abccorp.com',
            phone='555-0201',
            address='123 Business Blvd, Business City, BC 11111',
            credit_limit=50000.00,
            payment_terms='Net 30',
            is_active=True
        ),
        Customer(
            name='XYZ Retail',
            code='CUST-002',
            contact_person='Jane Retail',
            email='orders@xyzretail.com',
            phone='555-0202',
            address='456 Retail Road, Retail City, RC 22222',
            credit_limit=25000.00,
            payment_terms='Net 15',
            is_active=True
        )
    ]
    
    for customer in customers:
        db.session.add(customer)
    db.session.commit()
    
    # Create Stock Levels
    print("📊 Creating Stock Levels...")
    stock_levels = []
    for product in products:
        for location in random.sample(locations, 3):  # 3 random locations per product
            stock_level = StockLevel(
                product_id=product.id,
                location_id=location.id,
                quantity_on_hand=random.randint(10, 100),
                quantity_reserved=random.randint(0, 10),
                quantity_available=random.randint(5, 50),
                last_updated=datetime.utcnow()
            )
            stock_levels.append(stock_level)
            db.session.add(stock_level)
    db.session.commit()
    
    # Create Sample Inventory Transactions
    print("📝 Creating Sample Transactions...")
    transaction_types = ['receipt', 'issue', 'transfer_in', 'transfer_out', 'adjustment_positive', 'adjustment_negative']
    
    for i in range(50):  # Create 50 sample transactions
        product = random.choice(products)
        location = random.choice(locations)
        transaction_type = random.choice(transaction_types)
        quantity = random.randint(1, 20)
        
        transaction = InventoryTransaction(
            product_id=product.id,
            location_id=location.id,
            transaction_type=transaction_type,
            quantity=quantity,
            transaction_date=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            reference_number=f'TXN-{i+1:04d}',
            processed_by=f'User-{random.randint(1, 5)}',
            processing_time_seconds=random.uniform(0.5, 3.0)
        )
        db.session.add(transaction)
    db.session.commit()
    
    # Create Sample Pick Lists
    print("📋 Creating Sample Pick Lists...")
    pick_lists = []
    for i in range(10):
        pick_list = PickList(
            reference_number=f'PICK-{i+1:04d}',
            assigned_to=f'Picker-{random.randint(1, 5)}',
            status=random.choice(['pending', 'in_progress', 'completed']),
            priority=random.choice(['low', 'medium', 'high']),
            created_date=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
            due_date=datetime.utcnow() + timedelta(days=random.randint(1, 3))
        )
        pick_lists.append(pick_list)
        db.session.add(pick_list)
    db.session.commit()
    
    # Create Pick List Items
    for pick_list in pick_lists:
        for i in range(random.randint(1, 5)):  # 1-5 items per pick list
            product = random.choice(products)
            location = random.choice(locations)
            
            pick_item = PickListLine(
                pick_list_id=pick_list.id,
                product_id=product.id,
                location_id=location.id,
                quantity_requested=random.randint(1, 10),
                quantity_picked=0,
                status='pending'
            )
            db.session.add(pick_item)
    db.session.commit()
    
    # Create Sample Warehouse Activities
    print("🏃 Creating Sample Warehouse Activities...")
    activity_types = ['pick', 'put', 'cycle_count', 'maintenance', 'training']
    
    for i in range(100):
        activity = WarehouseActivity(
            user_id=f'User-{random.randint(1, 10)}',
            activity_type=random.choice(activity_types),
            location_id=random.choice(locations).id,
            activity_date=datetime.utcnow() - timedelta(hours=random.randint(0, 24)),
            duration_minutes=random.randint(5, 60),
            efficiency_score=random.uniform(0.7, 1.0)
        )
        db.session.add(activity)
    db.session.commit()
    
    # Create Sample Predictive Stockouts
    print("⚠️  Creating Sample Predictive Alerts...")
    for product in products[:3]:  # First 3 products
        stockout = PredictiveStockout(
            product_id=product.id,
            location_id=random.choice(locations).id,
            predicted_stockout_date=datetime.utcnow() + timedelta(days=random.randint(1, 14)),
            confidence_score=random.uniform(0.7, 0.95),
            current_stock_level=random.randint(5, 20),
            daily_consumption_rate=random.uniform(1.0, 5.0),
            alert_level='medium'
        )
        db.session.add(stockout)
    db.session.commit()
    
    # Create Sample Picker Performance
    print("📈 Creating Sample Picker Performance...")
    for i in range(10):
        performance = PickerPerformance(
            picker_id=f'Picker-{i+1}',
            date=datetime.utcnow().date(),
            total_picks=random.randint(50, 200),
            total_time_minutes=random.randint(240, 480),
            accuracy_rate=random.uniform(0.95, 0.99),
            efficiency_score=random.uniform(0.8, 1.0),
            average_pick_time_seconds=random.uniform(30, 120)
        )
        db.session.add(performance)
    db.session.commit()
    
    print("✅ Sample data seeding completed!")

if __name__ == '__main__':
    init_database()
