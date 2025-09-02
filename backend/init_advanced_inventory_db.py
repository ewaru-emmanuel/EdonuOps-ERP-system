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

# Import only the advanced models to avoid conflicts
from app import create_app, db
from modules.inventory.advanced_models import (
    UnitOfMeasure, UOMConversion, ProductCategory, AdvancedProduct, ProductVariant,
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
        UOMConversion(from_uom_id=1, to_uom_id=2, conversion_factor=12.0),
        UOMConversion(from_uom_id=2, to_uom_id=3, conversion_factor=50.0),
        UOMConversion(from_uom_id=1, to_uom_id=4, conversion_factor=0.5),
    ]
    
    for conv in conversions:
        db.session.add(conv)
    db.session.commit()
    
    # Create Product Categories
    print("📂 Creating Product Categories...")
    categories = [
        ProductCategory(name='Electronics', description='Electronic devices and components', abc_class='A'),
        ProductCategory(name='Clothing', description='Apparel and accessories', abc_class='B'),
        ProductCategory(name='Home & Garden', description='Home improvement and garden supplies', abc_class='C'),
        ProductCategory(name='Automotive', description='Automotive parts and accessories', abc_class='B'),
        ProductCategory(name='Sports & Outdoors', description='Sports equipment and outdoor gear', abc_class='C')
    ]
    
    for cat in categories:
        db.session.add(cat)
    db.session.commit()
    
    # Create Products
    print("📦 Creating Products...")
    products = [
        AdvancedProduct(
            sku='LAPTOP-001',
            name='Laptop Pro X1',
            description='High-performance laptop for professionals',
            category_id=1,
            base_uom_id=1,
            purchase_uom_id=1,
            sales_uom_id=1,
            cost_method='FIFO',
            standard_cost=1200.0,
            current_cost=1200.0,
            min_stock=10.0,
            max_stock=100.0,
            reorder_point=15.0,
            reorder_quantity=50.0,
            lead_time_days=7,
            product_type='standard',
            track_serial_numbers=False,
            track_lots=False,
            track_expiry=False
        ),
        AdvancedProduct(
            sku='PHONE-001',
            name='Smartphone Galaxy S21',
            description='Latest smartphone with advanced features',
            category_id=1,
            base_uom_id=1,
            purchase_uom_id=1,
            sales_uom_id=1,
            cost_method='FIFO',
            standard_cost=800.0,
            current_cost=800.0,
            min_stock=20.0,
            max_stock=200.0,
            reorder_point=25.0,
            reorder_quantity=100.0,
            lead_time_days=5,
            product_type='standard',
            track_serial_numbers=True,
            track_lots=False,
            track_expiry=False
        ),
        AdvancedProduct(
            sku='TSHIRT-001',
            name='Cotton T-Shirt',
            description='Comfortable cotton t-shirt',
            category_id=2,
            base_uom_id=1,
            purchase_uom_id=2,
            sales_uom_id=1,
            cost_method='Average',
            standard_cost=15.0,
            current_cost=15.0,
            min_stock=50.0,
            max_stock=500.0,
            reorder_point=75.0,
            reorder_quantity=200.0,
            lead_time_days=3,
            product_type='standard',
            track_serial_numbers=False,
            track_lots=False,
            track_expiry=False
        )
    ]
    
    for product in products:
        db.session.add(product)
    db.session.commit()
    
    # Create Product Variants
    print("🎨 Creating Product Variants...")
    variants = [
        ProductVariant(
            product_id=3,
            variant_sku='TSHIRT-001-RED-L',
            variant_name='Red T-Shirt Large',
            attributes={'color': 'Red', 'size': 'L'},
            is_active=True
        ),
        ProductVariant(
            product_id=3,
            variant_sku='TSHIRT-001-BLUE-M',
            variant_name='Blue T-Shirt Medium',
            attributes={'color': 'Blue', 'size': 'M'},
            is_active=True
        )
    ]
    
    for variant in variants:
        db.session.add(variant)
    db.session.commit()
    
    # Create Warehouses
    print("🏢 Creating Warehouses...")
    warehouses = [
        AdvancedWarehouse(
            code='WH-MAIN',
            name='Main Warehouse',
            address='123 Industrial Blvd, City, State 12345',
            contact_person='John Manager',
            contact_phone='555-123-4567',
            contact_email='warehouse@company.com',
            warehouse_type='storage',
            total_capacity=10000.0,
            used_capacity=2000.0,
            capacity_uom_id=4
        ),
        AdvancedWarehouse(
            code='WH-NORTH',
            name='North Distribution Center',
            address='456 Distribution Ave, North City, State 67890',
            contact_person='Sarah Supervisor',
            contact_phone='555-987-6543',
            contact_email='north.warehouse@company.com',
            warehouse_type='cross_dock',
            total_capacity=5000.0,
            used_capacity=1000.0,
            capacity_uom_id=4
        )
    ]
    
    for warehouse in warehouses:
        db.session.add(warehouse)
    db.session.commit()
    
    # Create Zones
    print("🗺️  Creating Zones...")
    zones = [
        Zone(warehouse_id=1, code='ZA', name='Zone A - Electronics', description='High-value electronics storage'),
        Zone(warehouse_id=1, code='ZB', name='Zone B - Clothing', description='Apparel and accessories'),
        Zone(warehouse_id=1, code='ZC', name='Zone C - General', description='General merchandise'),
        Zone(warehouse_id=2, code='ZD', name='Zone A - Fast Moving', description='Fast-moving items'),
        Zone(warehouse_id=2, code='ZE', name='Zone B - Slow Moving', description='Slow-moving items')
    ]
    
    for zone in zones:
        db.session.add(zone)
    db.session.commit()
    
    # Create Aisles
    print("🛤️  Creating Aisles...")
    aisles = [
        Aisle(zone_id=1, code='AA1', name='Aisle A1'),
        Aisle(zone_id=1, code='AA2', name='Aisle A2'),
        Aisle(zone_id=2, code='AB1', name='Aisle B1'),
        Aisle(zone_id=2, code='AB2', name='Aisle B2'),
        Aisle(zone_id=3, code='AC1', name='Aisle C1'),
        Aisle(zone_id=4, code='AD1', name='Aisle D1'),
        Aisle(zone_id=5, code='AE1', name='Aisle E1')
    ]
    
    for aisle in aisles:
        db.session.add(aisle)
    db.session.commit()
    
    # Create Racks
    print("📚 Creating Racks...")
    racks = []
    for aisle in aisles:
        for i in range(1, 6):  # 5 racks per aisle
            rack = Rack(
                aisle_id=aisle.id,
                code=f'R{aisle.code}-{i}',
                name=f'Rack {aisle.name}-{i}'
            )
            racks.append(rack)
    
    for rack in racks:
        db.session.add(rack)
    db.session.commit()
    
    # Create Levels
    print("📊 Creating Levels...")
    levels = []
    for rack in racks:
        for i in range(1, 6):  # 5 levels per rack
            level = Level(
                rack_id=rack.id,
                level_number=i
            )
            levels.append(level)
    
    for level in levels:
        db.session.add(level)
    db.session.commit()
    
    # Create Locations
    print("📍 Creating Locations...")
    locations = []
    for level in levels:
        for i in range(1, 11):  # 10 locations per level
            location = Location(
                level_id=level.id,
                location_code=f'L{level.id:03d}-{i:02d}',
                location_name=f'Location Level {level.id} Bin {i:02d}',
                barcode=f'LOC{level.id:03d}{i:02d}',
                location_type='PICKING' if i <= 5 else 'BULK_STORAGE',
                max_weight=50.0,
                max_volume=5.0,
                popularity_score=random.uniform(0.1, 1.0)
            )
            locations.append(location)
    
    for location in locations:
        db.session.add(location)
    db.session.commit()
    
    # Create Suppliers
    print("🏭 Creating Suppliers...")
    suppliers = [
        Supplier(
            code='SUP-001',
            name='Tech Supplies Inc',
            contact_person='Mike Supplier',
            contact_phone='555-111-2222',
            contact_email='mike@techsupplies.com',
            address='789 Supplier St, Supplier City, State 11111',
            lead_time_days=7,
            payment_terms='Net 30',
            credit_limit=50000.0
        ),
        Supplier(
            code='SUP-002',
            name='Fashion Wholesale Co',
            contact_person='Lisa Fashion',
            contact_phone='555-333-4444',
            contact_email='lisa@fashionwholesale.com',
            address='321 Fashion Ave, Fashion City, State 22222',
            lead_time_days=5,
            payment_terms='Net 15',
            credit_limit=30000.0
        )
    ]
    
    for supplier in suppliers:
        db.session.add(supplier)
    db.session.commit()
    
    # Create Stock Levels
    print("📦 Creating Stock Levels...")
    stock_levels = []
    for product in products:
        for location in random.sample(locations, min(5, len(locations))):
            stock_level = StockLevel(
                product_id=product.id,
                location_id=location.id,
                quantity_on_hand=random.randint(10, 100),
                quantity_allocated=random.randint(0, 10),
                quantity_available=random.randint(5, 50),
                average_cost=product.current_cost,
                last_updated=datetime.utcnow()
            )
            stock_levels.append(stock_level)
    
    for stock_level in stock_levels:
        db.session.add(stock_level)
    db.session.commit()
    
    # Create Inventory Transactions
    print("📝 Creating Inventory Transactions...")
    transactions = []
    for stock_level in stock_levels:
        # Create some historical transactions
        for i in range(3):
            transaction = AdvancedInventoryTransaction(
                product_id=stock_level.product_id,
                to_location_id=stock_level.location_id if i == 0 else None,
                from_location_id=stock_level.location_id if i != 0 else None,
                transaction_type='receipt' if i == 0 else 'issue',
                quantity=random.randint(5, 20),
                unit_cost=stock_level.average_cost,
                total_cost=random.randint(5, 20) * stock_level.average_cost,
                uom_id=1,  # Each
                transaction_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                reference_number=f'TXN-{stock_level.product_id:03d}-{stock_level.location_id:03d}-{i:02d}',
                processed_by=1,
                processing_time_seconds=random.uniform(1.0, 5.0)
            )
            transactions.append(transaction)
    
    for transaction in transactions:
        db.session.add(transaction)
    db.session.commit()
    
    # Create Sales Orders first (required for pick lists)
    print("📋 Creating Sales Orders...")
    sales_orders = [
        SalesOrder(
            so_number='SO-001',
            customer_id=1,  # Admin user as customer
            warehouse_id=1,
            order_date=datetime.utcnow().date(),
            required_date=datetime.utcnow().date() + timedelta(days=7),
            status='confirmed',
            total_amount=1000.0,
            created_by=1
        ),
        SalesOrder(
            so_number='SO-002',
            customer_id=1,  # Admin user as customer
            warehouse_id=2,
            order_date=datetime.utcnow().date(),
            required_date=datetime.utcnow().date() + timedelta(days=5),
            status='confirmed',
            total_amount=1500.0,
            created_by=1
        )
    ]
    
    for sales_order in sales_orders:
        db.session.add(sales_order)
    db.session.commit()
    
    # Create Pick Lists
    print("📋 Creating Pick Lists...")
    pick_lists = [
        PickList(
            pick_list_number='PL-001',
            warehouse_id=1,
            sales_order_id=1,
            assigned_to=1,
            pick_date=datetime.utcnow().date(),
            status='in_progress',
            started_at=datetime.utcnow(),
            total_pick_time_seconds=300.0,
            picks_per_hour=20.0
        ),
        PickList(
            pick_list_number='PL-002',
            warehouse_id=2,
            sales_order_id=2,
            assigned_to=1,
            pick_date=datetime.utcnow().date(),
            status='draft'
        )
    ]
    
    for pick_list in pick_lists:
        db.session.add(pick_list)
    db.session.commit()
    
    # Create Sales Order Lines first (required for pick list lines)
    print("📋 Creating Sales Order Lines...")
    sales_order_lines = []
    for i, sales_order in enumerate(sales_orders):
        for j in range(3):  # 3 lines per order
            product = random.choice(products)
            qty = random.randint(1, 10)
            unit_price = product.current_cost * 1.2  # 20% markup
            sales_order_line = SalesOrderLine(
                sales_order_id=sales_order.id,
                product_id=product.id,
                quantity_ordered=qty,
                unit_price=unit_price,
                total_price=qty * unit_price,
                uom_id=1,  # Each
                status='open'
            )
            sales_order_lines.append(sales_order_line)
    
    for sales_order_line in sales_order_lines:
        db.session.add(sales_order_line)
    db.session.commit()
    
    # Create Pick List Lines
    print("📋 Creating Pick List Lines...")
    pick_list_lines = []
    for i, pick_list in enumerate(pick_lists):
        # Get sales order lines for this pick list's sales order
        relevant_lines = [line for line in sales_order_lines if line.sales_order_id == pick_list.sales_order_id]
        for sales_order_line in relevant_lines:
            location = random.choice(locations)
            
            pick_line = PickListLine(
                pick_list_id=pick_list.id,
                sales_order_line_id=sales_order_line.id,
                product_id=sales_order_line.product_id,
                pick_location_id=location.id,
                quantity_to_pick=sales_order_line.quantity_ordered,
                quantity_picked=0,
                status='pending',
                pick_sequence=len(pick_list_lines) + 1
            )
            pick_list_lines.append(pick_line)
    
    for pick_line in pick_list_lines:
        db.session.add(pick_line)
    db.session.commit()
    
    # Create Warehouse Activities
    print("🏃 Creating Warehouse Activities...")
    activities = []
    for i in range(20):
        activity = WarehouseActivity(
            warehouse_id=random.choice([1, 2]),
            location_id=random.choice(locations).id,
            user_id=random.randint(1, 3),
            activity_type=random.choice(['pick', 'putaway', 'transfer', 'cycle_count']),
            activity_timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 24)),
            efficiency_score=random.uniform(0.7, 1.0),
            duration_seconds=random.randint(30, 300),
            items_processed=random.randint(1, 20)
        )
        activities.append(activity)
    
    for activity in activities:
        db.session.add(activity)
    db.session.commit()
    
    # Create Predictive Stockouts
    print("⚠️  Creating Predictive Stockouts...")
    stockouts = []
    for product in products:
        if random.random() < 0.3:  # 30% chance of stockout prediction
            location = random.choice(locations)
            stockout = PredictiveStockout(
                product_id=product.id,
                location_id=location.id,
                predicted_stockout_date=datetime.utcnow().date() + timedelta(days=random.randint(1, 30)),
                current_stock=random.randint(5, 20),
                daily_consumption_rate=random.uniform(0.5, 2.0),
                days_until_stockout=random.randint(1, 30),
                alert_level='medium' if random.random() < 0.5 else 'high'
            )
            stockouts.append(stockout)
    
    for stockout in stockouts:
        db.session.add(stockout)
    db.session.commit()
    
    # Create Picker Performance
    print("🏆 Creating Picker Performance...")
    performances = []
    for user_id in range(1, 4):
        total_picks = random.randint(50, 200)
        total_time = random.uniform(4.0, 8.0) * 3600  # convert to seconds
        performance = PickerPerformance(
            user_id=user_id,
            warehouse_id=random.choice([1, 2]),
            performance_date=datetime.utcnow().date(),
            total_picks=total_picks,
            total_items_picked=total_picks * random.randint(1, 3),
            total_pick_time_seconds=total_time,
            picks_per_hour=total_picks / (total_time / 3600),
            efficiency_score=random.uniform(0.7, 1.0)
        )
        performances.append(performance)
    
    for performance in performances:
        db.session.add(performance)
    db.session.commit()
    
    print("✅ Sample data seeding completed!")

if __name__ == '__main__':
    init_database()
