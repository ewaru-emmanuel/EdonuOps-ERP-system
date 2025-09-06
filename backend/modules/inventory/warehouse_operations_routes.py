from flask import Blueprint, request, jsonify
from app import db
from modules.inventory.advanced_models import WarehouseActivity, AdvancedWarehouse, AdvancedLocation
from modules.inventory.models import StockMovement, Warehouse, Product
from datetime import datetime, timedelta

warehouse_ops_bp = Blueprint('warehouse_operations', __name__)

@warehouse_ops_bp.route('/pick-lists', methods=['GET'])
def get_pick_lists():
    """Get all pick lists"""
    try:
        pick_lists = [
            {
                'id': 1,
                'pick_list_number': 'PL-2024-001',
                'assigned_to': 'John Smith',
                'status': 'in_progress',
                'total_lines': 15,
                'completed_lines': 8,
                'priority': 'high'
            },
            {
                'id': 2,
                'pick_list_number': 'PL-2024-002',
                'assigned_to': 'Sarah Johnson',
                'status': 'pending',
                'total_lines': 12,
                'completed_lines': 0,
                'priority': 'normal'
            }
        ]
        return jsonify(pick_lists)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/pick-lists/<int:pick_list_id>', methods=['GET'])
def get_pick_list_details(pick_list_id):
    """Get detailed information for a specific pick list"""
    try:
        # Mock data for pick list details
        pick_list_details = {
            'id': pick_list_id,
            'pick_list_number': f'PL-2024-{pick_list_id:03d}',
            'warehouse_id': 1,
            'assigned_to': 'John Smith',
            'status': 'in_progress',
            'pick_date': datetime.now().isoformat(),
            'completed_at': None,
            'lines': [
                {
                    'id': 1,
                    'product_id': 1,
                    'product_name': 'Laptop Pro X1',
                    'quantity_ordered': 5,
                    'quantity_picked': 3,
                    'status': 'in_progress',
                    'location': 'A1-B2-C3',
                    'picked_at': None
                },
                {
                    'id': 2,
                    'product_id': 2,
                    'product_name': 'Wireless Mouse',
                    'quantity_ordered': 10,
                    'quantity_picked': 10,
                    'status': 'completed',
                    'location': 'A2-B1-C4',
                    'picked_at': datetime.now().isoformat()
                }
            ],
            'total_lines': 2,
            'completed_lines': 1
        }
        
        return jsonify(pick_list_details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/pick-lists/<int:pick_list_id>/assign', methods=['POST'])
def assign_pick_list(pick_list_id):
    """Assign a pick list to a picker"""
    try:
        data = request.get_json()
        picker_name = data.get('picker_name')
        
        if not picker_name:
            return jsonify({'error': 'Picker name is required'}), 400
        
        # Mock assignment - in real implementation, this would update the database
        return jsonify({'message': f'Pick list {pick_list_id} assigned to {picker_name} successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/cycle-counts', methods=['GET'])
def get_cycle_counts():
    """Get all cycle counts"""
    try:
        cycle_counts = [
            {
                'id': 1,
                'count_number': 'CC-2024-001',
                'count_type': 'cycle',
                'assigned_to': 'Mike Wilson',
                'status': 'completed',
                'total_lines': 50,
                'completed_lines': 50
            },
            {
                'id': 2,
                'count_number': 'CC-2024-002',
                'count_type': 'full',
                'assigned_to': 'Lisa Brown',
                'status': 'in_progress',
                'total_lines': 200,
                'completed_lines': 75
            }
        ]
        return jsonify(cycle_counts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/cycle-counts', methods=['POST'])
def create_cycle_count():
    """Create a new cycle count"""
    try:
        data = request.get_json()
        
        cycle_count = CycleCount(
            count_number=f"CC-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            warehouse_id=data.get('warehouse_id'),
            count_type=data.get('count_type', 'cycle'),
            assigned_to=data.get('assigned_to'),
            status='pending',
            created_date=datetime.utcnow()
        )
        
        db.session.add(cycle_count)
        db.session.commit()
        
        return jsonify({
            'message': 'Cycle count created successfully',
            'id': cycle_count.id,
            'count_number': cycle_count.count_number
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/live-activity', methods=['GET'])
def get_warehouse_live_activity():
    """Get live warehouse activity"""
    try:
        activities = [
            {
                'id': 1,
                'user_name': 'John Smith',
                'activity_type': 'Pick Completed',
                'activity_timestamp': datetime.utcnow().isoformat(),
                'location_name': 'Zone A - Aisle 1',
                'efficiency_score': 92.5
            },
            {
                'id': 2,
                'user_name': 'Sarah Johnson',
                'activity_type': 'Cycle Count',
                'activity_timestamp': (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                'location_name': 'Zone B - Aisle 3',
                'efficiency_score': 88.3
            }
        ]
        return jsonify(activities)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@warehouse_ops_bp.route('/activity-log', methods=['POST'])
def log_warehouse_activity():
    """Log a new warehouse activity"""
    try:
        data = request.get_json()
        
        activity = WarehouseActivity(
            warehouse_id=data.get('warehouse_id'),
            user_id=data.get('user_id'),
            user_name=data.get('user_name'),
            activity_type=data.get('activity_type'),
            activity_timestamp=datetime.utcnow(),
            location_name=data.get('location_name'),
            efficiency_score=data.get('efficiency_score'),
            duration_seconds=data.get('duration_seconds'),
            activity_details=data.get('activity_details')
        )
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({'message': 'Activity logged successfully', 'id': activity.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Inter-Warehouse Transfers
# -----------------------------

_TRANSFERS = []  # in-memory store for transfer orders {id, number, from_warehouse_id, to_warehouse_id, status, lines}

@warehouse_ops_bp.route('/transfers', methods=['POST', 'OPTIONS'])
def create_transfer():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        data = request.get_json() or {}
        from_wh = int(data.get('from_warehouse_id'))
        to_wh = int(data.get('to_warehouse_id'))
        if not from_wh or not to_wh or from_wh == to_wh:
            return jsonify({'error': 'Invalid warehouses'}), 400
        lines_in = data.get('lines') or []
        if not lines_in:
            return jsonify({'error': 'No lines provided'}), 400
        transfer_id = len(_TRANSFERS) + 1
        number = f"TR-{datetime.utcnow().strftime('%Y%m%d')}-{transfer_id:03d}"
        lines = []
        for idx, l in enumerate(lines_in, start=1):
            lines.append({
                'id': idx,
                'product_id': int(l.get('product_id') or 0),
                'quantity': float(l.get('quantity') or 0),
                'shipped_quantity': 0.0,
                'received_quantity': 0.0
            })
        rec = {
            'id': transfer_id,
            'number': number,
            'from_warehouse_id': from_wh,
            'to_warehouse_id': to_wh,
            'status': 'draft',  # draft -> in_transit -> completed
            'created_at': datetime.utcnow().isoformat(),
            'lines': lines
        }
        _TRANSFERS.append(rec)
        return jsonify(rec), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@warehouse_ops_bp.route('/transfers', methods=['GET', 'OPTIONS'])
def list_transfers():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        return jsonify(_TRANSFERS), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@warehouse_ops_bp.route('/transfers/<int:transfer_id>/ship', methods=['POST', 'OPTIONS'])
def ship_transfer(transfer_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        data = request.get_json() or {}
        lines_req = data.get('lines') or []
        tr = next((t for t in _TRANSFERS if t['id'] == transfer_id), None)
        if not tr:
            return jsonify({'error': 'Transfer not found'}), 404
        if tr['status'] not in ('draft', 'in_transit'):
            return jsonify({'error': 'Cannot ship in current status'}), 400
        shipped = []
        for lr in lines_req:
            line = next((ln for ln in tr['lines'] if ln['id'] == lr.get('line_id')), None)
            if not line:
                continue
            qty = float(lr.get('quantity') or 0)
            if qty <= 0:
                continue
            # Post OUT movement from source warehouse at last known cost
            prod = Product.query.get(line['product_id'])
            unit_cost = float(prod.current_cost or prod.standard_cost or 0.0)
            try:
                mv = StockMovement(
                    product_id=line['product_id'],
                    warehouse_id=tr['from_warehouse_id'],
                    movement_type='TRANSFER',
                    quantity=-qty,
                    unit_cost=unit_cost,
                    total_cost=-qty * unit_cost,
                    reference_type='TRANSFER',
                    reference_id=transfer_id,
                    to_warehouse_id=tr['to_warehouse_id']
                )
                db.session.add(mv)
                db.session.commit()
            except Exception:
                db.session.rollback()
            line['shipped_quantity'] += qty
            shipped.append({'line_id': line['id'], 'quantity': qty})
        tr['status'] = 'in_transit'
        tr['updated_at'] = datetime.utcnow().isoformat()
        return jsonify({'message': 'Shipped', 'shipped': shipped, 'status': tr['status']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@warehouse_ops_bp.route('/transfers/<int:transfer_id>/receive', methods=['POST', 'OPTIONS'])
def receive_transfer(transfer_id: int):
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        data = request.get_json() or {}
        lines_req = data.get('lines') or []
        tr = next((t for t in _TRANSFERS if t['id'] == transfer_id), None)
        if not tr:
            return jsonify({'error': 'Transfer not found'}), 404
        if tr['status'] not in ('in_transit', 'draft'):
            return jsonify({'error': 'Cannot receive in current status'}), 400
        received = []
        for lr in lines_req:
            line = next((ln for ln in tr['lines'] if ln['id'] == lr.get('line_id')), None)
            if not line:
                continue
            qty = float(lr.get('quantity') or 0)
            if qty <= 0:
                continue
            prod = Product.query.get(line['product_id'])
            unit_cost = float(prod.current_cost or prod.standard_cost or 0.0)
            try:
                mv = StockMovement(
                    product_id=line['product_id'],
                    warehouse_id=tr['to_warehouse_id'],
                    movement_type='TRANSFER',
                    quantity=qty,
                    unit_cost=unit_cost,
                    total_cost=qty * unit_cost,
                    reference_type='TRANSFER',
                    reference_id=transfer_id,
                    from_warehouse_id=tr['from_warehouse_id']
                )
                db.session.add(mv)
                db.session.commit()
            except Exception:
                db.session.rollback()
            line['received_quantity'] += qty
            received.append({'line_id': line['id'], 'quantity': qty})
        # Completed if all received
        if all((ln['received_quantity'] or 0) >= (ln['quantity'] or 0) for ln in tr['lines']):
            tr['status'] = 'completed'
        tr['updated_at'] = datetime.utcnow().isoformat()
        return jsonify({'message': 'Received', 'received': received, 'status': tr['status']}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Valuation by warehouse (approximate)
# -----------------------------

@warehouse_ops_bp.route('/valuation/warehouse', methods=['GET', 'OPTIONS'])
def warehouse_valuation():
    if request.method == 'OPTIONS':
        return ('', 200)
    try:
        # Compute on-hand per warehouse by summing StockMovement quantities
        rows = db.session.query(
            StockMovement.warehouse_id,
            db.func.sum(StockMovement.quantity).label('qty'),
            db.func.avg(StockMovement.unit_cost).label('avg_cost')
        ).group_by(StockMovement.warehouse_id).all()
        data = []
        for wh_id, qty, avg_cost in rows:
            wh = Warehouse.query.get(wh_id)
            value = float(qty or 0) * float(avg_cost or 0)
            data.append({
                'warehouse_id': wh_id,
                'warehouse_name': wh.name if wh else f'WH-{wh_id}',
                'on_hand': float(qty or 0),
                'avg_cost': round(float(avg_cost or 0), 4),
                'valuation_base': round(value, 2)
            })
        return jsonify({'warehouses': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
