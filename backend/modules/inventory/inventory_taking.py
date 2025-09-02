import csv
import io
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file

inventory_taking_bp = Blueprint('inventory_taking', __name__)

# Mock data storage
inventory_counts = {}

@inventory_taking_bp.route('/export-template', methods=['GET'])
def export_template():
    """Export CSV template for inventory counting"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Item Code', 'Counted Quantity', 'Batch/Lot Number', 'Serial Number', 'Location/Bin', 'Item Status', 'Expiry Date', 'Manufacturing Date', 'Remarks'])
    writer.writerow(['SKU001', '', '', '', '', 'Good', '', '', ''])
    writer.writerow(['SKU002', '', '', '', '', 'Good', '', '', ''])
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'inventory_count_template_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@inventory_taking_bp.route('/counts', methods=['POST'])
def save_draft():
    """Save inventory count draft"""
    data = request.get_json()
    count_id = data.get('id') or f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    inventory_counts[count_id] = {
        **data,
        'id': count_id,
        'status': 'draft',
        'created_at': datetime.now().isoformat()
    }
    return jsonify({'success': True, 'count_id': count_id, 'message': 'Draft saved successfully'})

@inventory_taking_bp.route('/counts/<count_id>/submit', methods=['POST'])
def submit_count(count_id):
    """Submit final inventory count"""
    data = request.get_json()
    if count_id not in inventory_counts:
        return jsonify({'error': 'Count not found'}), 404
    inventory_counts[count_id].update({
        **data,
        'status': 'submitted',
        'submitted_at': datetime.now().isoformat()
    })
    return jsonify({'success': True, 'count_id': count_id, 'message': 'Count submitted successfully'})

@inventory_taking_bp.route('/import-csv', methods=['POST'])
def import_csv():
    """Import CSV file for inventory counting"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    content = file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(content))
    imported_items = []
    for row in csv_reader:
        item = {
            'itemCode': row.get('Item Code', '').strip(),
            'countedQuantity': float(row.get('Counted Quantity', 0) or 0),
            'batchLotNumber': row.get('Batch/Lot Number', '').strip(),
            'serialNumber': row.get('Serial Number', '').strip(),
            'locationBin': row.get('Location/Bin', '').strip(),
            'itemStatus': row.get('Item Status', 'good').strip().lower(),
            'expiryDate': row.get('Expiry Date', '').strip(),
            'manufacturingDate': row.get('Manufacturing Date', '').strip(),
            'itemRemarks': row.get('Remarks', '').strip()
        }
        imported_items.append(item)
    return jsonify({'success': True, 'imported_items': imported_items, 'total_imported': len(imported_items)})
