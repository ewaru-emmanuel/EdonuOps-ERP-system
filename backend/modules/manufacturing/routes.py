# backend/modules/manufacturing/routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from modules.manufacturing.models import (
    BillOfMaterials, BOMItem, ProductionOrder, WorkCenter, 
    ProductionOperation, MaterialRequirementsPlan, SupplyChainNode,
    SupplyChainLink, QualityControl, MaintenanceSchedule, Equipment
)
from modules.inventory.models import Product
import uuid

bp = Blueprint('manufacturing', __name__, url_prefix='/api/manufacturing')

# Sample data for initial state
boms = []
bom_items = []
production_orders = []
work_centers = []
production_operations = []
mrp_records = []
supply_chain_nodes = []
supply_chain_links = []
quality_controls = []
maintenance_schedules = []
equipment = []

# Bill of Materials endpoints
@bp.route('/boms', methods=['GET'])
def get_boms():
    """Get all Bill of Materials"""
    product_id = request.args.get('product_id', type=int)
    
    filtered_boms = boms
    if product_id:
        filtered_boms = [bom for bom in boms if bom.get('product_id') == product_id]
    
    return jsonify(filtered_boms)

@bp.route('/boms', methods=['POST'])
def create_bom():
    """Create a new Bill of Materials"""
    data = request.get_json()
    
    new_bom = {
        "id": len(boms) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "product_id": data.get('product_id'),
        "version": data.get('version', '1.0'),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    boms.append(new_bom)
    return jsonify(new_bom), 201

@bp.route('/boms/<int:bom_id>/items', methods=['GET'])
def get_bom_items(bom_id):
    """Get items for a specific BOM"""
    items = [item for item in bom_items if item.get('bom_id') == bom_id]
    return jsonify(items)

@bp.route('/boms/<int:bom_id>/items', methods=['POST'])
def add_bom_item(bom_id):
    """Add an item to a BOM"""
    data = request.get_json()
    
    new_item = {
        "id": len(bom_items) + 1,
        "bom_id": bom_id,
        "component_id": data.get('component_id'),
        "quantity": data.get('quantity'),
        "unit_of_measure": data.get('unit_of_measure', 'pcs'),
        "scrap_factor": data.get('scrap_factor', 0.0),
        "lead_time": data.get('lead_time', 0),
        "cost": data.get('cost', 0.0),
        "sequence": data.get('sequence', 0)
    }
    
    bom_items.append(new_item)
    return jsonify(new_item), 201

# Production Orders endpoints
@bp.route('/production-orders', methods=['GET'])
def get_production_orders():
    """Get all production orders"""
    status = request.args.get('status')
    work_center_id = request.args.get('work_center_id', type=int)
    
    filtered_orders = production_orders
    if status:
        filtered_orders = [order for order in filtered_orders if order.get('status') == status]
    if work_center_id:
        filtered_orders = [order for order in filtered_orders if order.get('work_center_id') == work_center_id]
    
    return jsonify(filtered_orders)

@bp.route('/production-orders', methods=['POST'])
def create_production_order():
    """Create a new production order"""
    data = request.get_json()
    
    # Generate order number
    order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{len(production_orders) + 1:03d}"
    
    new_order = {
        "id": len(production_orders) + 1,
        "order_number": order_number,
        "bom_id": data.get('bom_id'),
        "product_id": data.get('product_id'),
        "quantity": data.get('quantity'),
        "completed_quantity": data.get('completed_quantity', 0.0),
        "status": data.get('status', 'planned'),
        "priority": data.get('priority', 5),
        "planned_start_date": data.get('planned_start_date'),
        "planned_end_date": data.get('planned_end_date'),
        "work_center_id": data.get('work_center_id'),
        "cost": data.get('cost', 0.0),
        "notes": data.get('notes'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    production_orders.append(new_order)
    return jsonify(new_order), 201

@bp.route('/production-orders/<int:order_id>', methods=['PUT'])
def update_production_order(order_id):
    """Update a production order"""
    data = request.get_json()
    order = next((o for o in production_orders if o['id'] == order_id), None)
    
    if order:
        order.update(data)
        order['updated_at'] = datetime.utcnow().isoformat()
        return jsonify(order)
    
    return jsonify({"error": "Production order not found"}), 404

# Work Centers endpoints
@bp.route('/work-centers', methods=['GET'])
def get_work_centers():
    """Get all work centers"""
    return jsonify(work_centers)

@bp.route('/work-centers', methods=['POST'])
def create_work_center():
    """Create a new work center"""
    data = request.get_json()
    
    new_work_center = {
        "id": len(work_centers) + 1,
        "name": data.get('name'),
        "description": data.get('description'),
        "capacity": data.get('capacity', 0.0),
        "efficiency": data.get('efficiency', 100.0),
        "cost_per_hour": data.get('cost_per_hour', 0.0),
        "is_active": data.get('is_active', True),
        "location": data.get('location'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    work_centers.append(new_work_center)
    return jsonify(new_work_center), 201

# Material Requirements Planning endpoints
@bp.route('/mrp', methods=['GET'])
def get_mrp():
    """Get Material Requirements Planning data"""
    product_id = request.args.get('product_id', type=int)
    
    filtered_mrp = mrp_records
    if product_id:
        filtered_mrp = [mrp for mrp in mrp_records if mrp.get('product_id') == product_id]
    
    return jsonify(filtered_mrp)

@bp.route('/mrp/calculate', methods=['POST'])
def calculate_mrp():
    """Calculate MRP for products"""
    data = request.get_json()
    product_ids = data.get('product_ids', [])
    
    # Mock MRP calculation
    mrp_results = []
    for product_id in product_ids:
        mrp_result = {
            "product_id": product_id,
            "period_start": datetime.now().date().isoformat(),
            "period_end": (datetime.now() + timedelta(days=30)).date().isoformat(),
            "gross_requirements": 100.0,
            "scheduled_receipts": 50.0,
            "projected_on_hand": 25.0,
            "net_requirements": 25.0,
            "planned_order_receipts": 30.0,
            "planned_order_releases": 30.0,
            "safety_stock": 10.0,
            "lead_time": 7,
            "lot_size": 50.0
        }
        mrp_results.append(mrp_result)
        mrp_records.append(mrp_result)
    
    return jsonify(mrp_results)

# Supply Chain endpoints
@bp.route('/supply-chain/nodes', methods=['GET'])
def get_supply_chain_nodes():
    """Get supply chain nodes"""
    node_type = request.args.get('node_type')
    
    filtered_nodes = supply_chain_nodes
    if node_type:
        filtered_nodes = [node for node in supply_chain_nodes if node.get('node_type') == node_type]
    
    return jsonify(filtered_nodes)

@bp.route('/supply-chain/nodes', methods=['POST'])
def create_supply_chain_node():
    """Create a new supply chain node"""
    data = request.get_json()
    
    new_node = {
        "id": len(supply_chain_nodes) + 1,
        "name": data.get('name'),
        "node_type": data.get('node_type'),
        "location": data.get('location'),
        "country": data.get('country'),
        "region": data.get('region'),
        "capacity": data.get('capacity', 0.0),
        "lead_time": data.get('lead_time', 0),
        "cost_per_unit": data.get('cost_per_unit', 0.0),
        "is_active": data.get('is_active', True),
        "coordinates": data.get('coordinates'),
        "contact_info": data.get('contact_info'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    supply_chain_nodes.append(new_node)
    return jsonify(new_node), 201

@bp.route('/supply-chain/links', methods=['GET'])
def get_supply_chain_links():
    """Get supply chain links"""
    return jsonify(supply_chain_links)

@bp.route('/supply-chain/links', methods=['POST'])
def create_supply_chain_link():
    """Create a new supply chain link"""
    data = request.get_json()
    
    new_link = {
        "id": len(supply_chain_links) + 1,
        "from_node_id": data.get('from_node_id'),
        "to_node_id": data.get('to_node_id'),
        "transport_mode": data.get('transport_mode'),
        "lead_time": data.get('lead_time', 0),
        "cost_per_unit": data.get('cost_per_unit', 0.0),
        "capacity": data.get('capacity', 0.0),
        "is_active": data.get('is_active', True),
        "created_at": datetime.utcnow().isoformat()
    }
    
    supply_chain_links.append(new_link)
    return jsonify(new_link), 201

# Quality Control endpoints
@bp.route('/quality-control', methods=['GET'])
def get_quality_controls():
    """Get quality control records"""
    status = request.args.get('status')
    product_id = request.args.get('product_id', type=int)
    
    filtered_qc = quality_controls
    if status:
        filtered_qc = [qc for qc in quality_controls if qc.get('status') == status]
    if product_id:
        filtered_qc = [qc for qc in quality_controls if qc.get('product_id') == product_id]
    
    return jsonify(filtered_qc)

@bp.route('/quality-control', methods=['POST'])
def create_quality_control():
    """Create a new quality control record"""
    data = request.get_json()
    
    new_qc = {
        "id": len(quality_controls) + 1,
        "production_order_id": data.get('production_order_id'),
        "product_id": data.get('product_id'),
        "inspection_date": data.get('inspection_date', datetime.utcnow().isoformat()),
        "inspector_id": data.get('inspector_id'),
        "quantity_inspected": data.get('quantity_inspected'),
        "quantity_passed": data.get('quantity_passed', 0.0),
        "quantity_failed": data.get('quantity_failed', 0.0),
        "defect_types": data.get('defect_types', {}),
        "notes": data.get('notes'),
        "status": data.get('status', 'pending'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    quality_controls.append(new_qc)
    return jsonify(new_qc), 201

# Equipment and Maintenance endpoints
@bp.route('/equipment', methods=['GET'])
def get_equipment():
    """Get all equipment"""
    status = request.args.get('status')
    work_center_id = request.args.get('work_center_id', type=int)
    
    filtered_equipment = equipment
    if status:
        filtered_equipment = [eq for eq in equipment if eq.get('status') == status]
    if work_center_id:
        filtered_equipment = [eq for eq in equipment if eq.get('work_center_id') == work_center_id]
    
    return jsonify(filtered_equipment)

@bp.route('/equipment', methods=['POST'])
def create_equipment():
    """Create new equipment"""
    data = request.get_json()
    
    new_equipment = {
        "id": len(equipment) + 1,
        "name": data.get('name'),
        "equipment_type": data.get('equipment_type'),
        "model": data.get('model'),
        "serial_number": data.get('serial_number'),
        "manufacturer": data.get('manufacturer'),
        "installation_date": data.get('installation_date'),
        "warranty_expiry": data.get('warranty_expiry'),
        "location": data.get('location'),
        "work_center_id": data.get('work_center_id'),
        "status": data.get('status', 'operational'),
        "capacity": data.get('capacity', 0.0),
        "efficiency": data.get('efficiency', 100.0),
        "cost": data.get('cost', 0.0),
        "created_at": datetime.utcnow().isoformat()
    }
    
    equipment.append(new_equipment)
    return jsonify(new_equipment), 201

@bp.route('/maintenance-schedules', methods=['GET'])
def get_maintenance_schedules():
    """Get maintenance schedules"""
    status = request.args.get('status')
    equipment_id = request.args.get('equipment_id', type=int)
    
    filtered_schedules = maintenance_schedules
    if status:
        filtered_schedules = [sched for sched in maintenance_schedules if sched.get('status') == status]
    if equipment_id:
        filtered_schedules = [sched for sched in maintenance_schedules if sched.get('equipment_id') == equipment_id]
    
    return jsonify(filtered_schedules)

@bp.route('/maintenance-schedules', methods=['POST'])
def create_maintenance_schedule():
    """Create a new maintenance schedule"""
    data = request.get_json()
    
    new_schedule = {
        "id": len(maintenance_schedules) + 1,
        "equipment_id": data.get('equipment_id'),
        "maintenance_type": data.get('maintenance_type'),
        "scheduled_date": data.get('scheduled_date'),
        "technician_id": data.get('technician_id'),
        "description": data.get('description'),
        "cost": data.get('cost', 0.0),
        "status": data.get('status', 'scheduled'),
        "priority": data.get('priority', 'normal'),
        "created_at": datetime.utcnow().isoformat()
    }
    
    maintenance_schedules.append(new_schedule)
    return jsonify(new_schedule), 201

# Analytics and Reporting endpoints
@bp.route('/analytics/production-summary', methods=['GET'])
def get_production_summary():
    """Get production summary analytics"""
    summary = {
        "total_orders": len(production_orders),
        "orders_in_progress": len([o for o in production_orders if o.get('status') == 'in_progress']),
        "orders_completed": len([o for o in production_orders if o.get('status') == 'completed']),
        "total_work_centers": len(work_centers),
        "active_work_centers": len([wc for wc in work_centers if wc.get('is_active')]),
        "total_equipment": len(equipment),
        "operational_equipment": len([eq for eq in equipment if eq.get('status') == 'operational']),
        "pending_maintenance": len([sched for sched in maintenance_schedules if sched.get('status') == 'scheduled']),
        "quality_pass_rate": 95.5  # Mock calculation
    }
    
    return jsonify(summary)

@bp.route('/analytics/supply-chain-map', methods=['GET'])
def get_supply_chain_map():
    """Get supply chain network map data"""
    map_data = {
        "nodes": supply_chain_nodes,
        "links": supply_chain_links,
        "statistics": {
            "total_nodes": len(supply_chain_nodes),
            "total_links": len(supply_chain_links),
            "suppliers": len([n for n in supply_chain_nodes if n.get('node_type') == 'supplier']),
            "warehouses": len([n for n in supply_chain_nodes if n.get('node_type') == 'warehouse']),
            "factories": len([n for n in supply_chain_nodes if n.get('node_type') == 'factory']),
            "customers": len([n for n in supply_chain_nodes if n.get('node_type') == 'customer'])
        }
    }
    
    return jsonify(map_data)

# Initialize sample data
def init_sample_data():
    """Initialize sample manufacturing data"""
    global boms, bom_items, production_orders, work_centers, equipment, supply_chain_nodes
    
    # Sample work centers
    work_centers.extend([
        {
            "id": 1,
            "name": "Assembly Line A",
            "description": "Main assembly line for electronics",
            "capacity": 8.0,
            "efficiency": 95.0,
            "cost_per_hour": 150.0,
            "is_active": True,
            "location": "Building 1, Floor 2",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": 2,
            "name": "Packaging Station",
            "description": "Product packaging and labeling",
            "capacity": 6.0,
            "efficiency": 90.0,
            "cost_per_hour": 80.0,
            "is_active": True,
            "location": "Building 1, Floor 1",
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample BOMs
    boms.extend([
        {
            "id": 1,
            "name": "Laptop Assembly BOM",
            "description": "Bill of materials for laptop assembly",
            "product_id": 1,
            "version": "1.0",
            "is_active": True,
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample production orders
    production_orders.extend([
        {
            "id": 1,
            "order_number": "PO-20240814-001",
            "bom_id": 1,
            "product_id": 1,
            "quantity": 100,
            "completed_quantity": 0,
            "status": "planned",
            "priority": 5,
            "planned_start_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "planned_end_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "work_center_id": 1,
            "cost": 0.0,
            "notes": "Initial production run",
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample equipment
    equipment.extend([
        {
            "id": 1,
            "name": "Robotic Arm A1",
            "equipment_type": "Assembly Robot",
            "model": "KUKA KR-1000",
            "serial_number": "RB-001-2024",
            "manufacturer": "KUKA Robotics",
            "installation_date": "2024-01-15",
            "warranty_expiry": "2027-01-15",
            "location": "Assembly Line A",
            "work_center_id": 1,
            "status": "operational",
            "capacity": 100.0,
            "efficiency": 98.0,
            "cost": 150000.0,
            "created_at": datetime.utcnow().isoformat()
        }
    ])
    
    # Sample supply chain nodes
    supply_chain_nodes.extend([
        {
            "id": 1,
            "name": "Main Factory",
            "node_type": "factory",
            "location": "Shanghai, China",
            "country": "China",
            "region": "Asia",
            "capacity": 10000.0,
            "lead_time": 0,
            "cost_per_unit": 0.0,
            "is_active": True,
            "coordinates": {"lat": 31.2304, "lng": 121.4737},
            "contact_info": {"phone": "+86-21-1234-5678", "email": "factory@company.com"},
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": 2,
            "name": "Component Supplier A",
            "node_type": "supplier",
            "location": "Shenzhen, China",
            "country": "China",
            "region": "Asia",
            "capacity": 5000.0,
            "lead_time": 7,
            "cost_per_unit": 25.0,
            "is_active": True,
            "coordinates": {"lat": 22.3193, "lng": 114.1694},
            "contact_info": {"phone": "+86-755-8765-4321", "email": "supplier@components.com"},
            "created_at": datetime.utcnow().isoformat()
        }
    ])

# Initialize sample data when module loads
init_sample_data()