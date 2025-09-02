#!/usr/bin/env python3
"""
Test script for Inventory Taking functionality
"""

import requests
import json
import csv
import io

BASE_URL = "http://localhost:5000"

def test_inventory_taking_endpoints():
    """Test all inventory taking endpoints"""
    
    print("🧪 Testing Inventory Taking Endpoints...")
    
    # Test 1: Export Template
    print("\n1. Testing Export Template...")
    try:
        response = requests.get(f"{BASE_URL}/api/inventory/taking/export-template")
        if response.status_code == 200:
            print("✅ Export Template: SUCCESS")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            print(f"   Content-Length: {len(response.content)} bytes")
        else:
            print(f"❌ Export Template: FAILED - Status {response.status_code}")
    except Exception as e:
        print(f"❌ Export Template: ERROR - {e}")
    
    # Test 2: Save Draft
    print("\n2. Testing Save Draft...")
    try:
        draft_data = {
            "warehouse": "WH001",
            "inventoryDate": "2024-01-15",
            "countingMethod": "full_count",
            "counterName": "John Doe",
            "inventoryReason": "regular",
            "freezeInventory": False,
            "cycleCountGroup": "",
            "generalNotes": "Test count",
            "items": [
                {
                    "itemCode": "SKU001",
                    "itemName": "Test Product",
                    "countedQuantity": 100,
                    "systemQuantity": 95,
                    "variance": 5,
                    "variancePercentage": 5.26
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/inventory/taking/counts",
            json=draft_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Save Draft: SUCCESS")
            print(f"   Count ID: {result.get('count_id')}")
            print(f"   Message: {result.get('message')}")
            count_id = result.get('count_id')
        else:
            print(f"❌ Save Draft: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            count_id = None
    except Exception as e:
        print(f"❌ Save Draft: ERROR - {e}")
        count_id = None
    
    # Test 3: Submit Count (if we have a count_id)
    if count_id:
        print(f"\n3. Testing Submit Count (ID: {count_id})...")
        try:
            submit_data = {
                "warehouse": "WH001",
                "inventoryDate": "2024-01-15",
                "countingMethod": "full_count",
                "counterName": "John Doe",
                "inventoryReason": "regular",
                "freezeInventory": False,
                "cycleCountGroup": "",
                "generalNotes": "Test count - submitted",
                "items": [
                    {
                        "itemCode": "SKU001",
                        "itemName": "Test Product",
                        "countedQuantity": 100,
                        "systemQuantity": 95,
                        "variance": 5,
                        "variancePercentage": 5.26
                    }
                ]
            }
            
            response = requests.post(
                f"{BASE_URL}/api/inventory/taking/counts/{count_id}/submit",
                json=submit_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Submit Count: SUCCESS")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"❌ Submit Count: FAILED - Status {response.status_code}")
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"❌ Submit Count: ERROR - {e}")
    
    # Test 4: Import CSV
    print("\n4. Testing Import CSV...")
    try:
        # Create a test CSV file
        csv_data = io.StringIO()
        writer = csv.writer(csv_data)
        writer.writerow(['Item Code', 'Counted Quantity', 'Batch/Lot Number', 'Serial Number', 'Location/Bin', 'Item Status', 'Expiry Date', 'Manufacturing Date', 'Remarks'])
        writer.writerow(['SKU002', '50', 'BATCH001', '', 'A1-01', 'Good', '2024-12-31', '2024-01-01', 'Test item'])
        writer.writerow(['SKU003', '25', 'BATCH002', '', 'B2-03', 'Good', '2024-06-30', '2024-01-01', 'Another test item'])
        
        csv_content = csv_data.getvalue().encode('utf-8')
        
        files = {'file': ('test_inventory.csv', csv_content, 'text/csv')}
        response = requests.post(f"{BASE_URL}/api/inventory/taking/import-csv", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Import CSV: SUCCESS")
            print(f"   Total Imported: {result.get('total_imported')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Import CSV: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Import CSV: ERROR - {e}")
    
    print("\n🎉 Inventory Taking Tests Complete!")

if __name__ == "__main__":
    test_inventory_taking_endpoints()
