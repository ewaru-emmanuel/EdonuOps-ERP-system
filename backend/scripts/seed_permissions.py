#!/usr/bin/env python3
"""
Permission Seeding Script
=========================

SECURITY: This script seeds all permissions from module_permission_mappings.py into the database.
Run this script to ensure all required permissions exist before granting them to roles.

Usage:
    python scripts/seed_permissions.py
"""

import os
import sys

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from modules.core.permission_seeder import seed_all_permissions

def main():
    """Main function to seed permissions"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("PERMISSION SEEDING SCRIPT")
        print("=" * 60)
        print()
        
        result = seed_all_permissions()
        
        print()
        print("=" * 60)
        print("SEEDING SUMMARY")
        print("=" * 60)
        print(f"Total permissions defined: {result['total']}")
        print(f"Permissions created: {result['created']}")
        print(f"Permissions already existed: {result['existing']}")
        
        if result['errors']:
            print(f"\n⚠️  Errors encountered: {len(result['errors'])}")
            for error in result['errors']:
                print(f"   - {error}")
        else:
            print("\n✅ No errors encountered")
        
        print()
        print("=" * 60)
        
        if result['errors']:
            sys.exit(1)
        else:
            sys.exit(0)

if __name__ == '__main__':
    main()

