#!/usr/bin/env python3
"""
Script to check all users in the database and their settings
"""

import sqlite3
import json
import os
from datetime import datetime

def check_database_connection():
    """Check if database exists and is accessible"""
    db_path = 'backend/edonuops.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def get_table_info(conn):
    """Get information about all tables in the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    return [table[0] for table in tables]

def get_user_count(conn):
    """Get total number of users"""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    return cursor.fetchone()[0]

def get_all_users(conn):
    """Get all users with their basic information"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id, 
            username, 
            email, 
            is_active,
            role_id,
            organization_id
        FROM users 
        ORDER BY id DESC
    """)
    return cursor.fetchall()

def get_user_preferences(conn, user_id):
    """Get user preferences for a specific user"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            selected_modules,
            module_settings,
            dashboard_layout,
            default_currency,
            timezone,
            date_format,
            theme,
            language,
            notifications_enabled,
            industry,
            business_size,
            company_name,
            created_at,
            updated_at
        FROM user_preferences 
        WHERE user_id = ?
    """, (str(user_id),))
    return cursor.fetchall()

def get_user_modules(conn, user_id):
    """Get user module settings"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            module_id,
            is_active,
            is_enabled,
            permissions,
            activated_at,
            deactivated_at
        FROM user_modules 
        WHERE user_id = ?
        ORDER BY module_id
    """, (user_id,))
    return cursor.fetchall()

def get_user_roles(conn, user_id):
    """Get user roles and permissions"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            ur.role_id,
            r.name as role_name,
            r.permissions,
            ur.granted_at,
            ur.expires_at,
            ur.is_active
        FROM user_roles ur
        LEFT JOIN security_roles r ON ur.role_id = r.id
        WHERE ur.user_id = ?
        ORDER BY ur.granted_at DESC
    """, (user_id,))
    return cursor.fetchall()

def get_organizations(conn):
    """Get all organizations"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id,
            name,
            code,
            is_active,
            created_at
        FROM organizations 
        ORDER BY created_at DESC
    """)
    return cursor.fetchall()

def get_roles(conn):
    """Get all roles"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            id,
            name,
            permissions,
            created_at
        FROM security_roles 
        ORDER BY name
    """)
    return cursor.fetchall()

def format_json_value(value):
    """Format JSON values for display"""
    if value is None:
        return None
    try:
        if isinstance(value, str):
            return json.loads(value)
        return value
    except:
        return value

def main():
    print("Checking Database Users and Settings")
    print("=" * 50)
    
    # Connect to database
    conn = check_database_connection()
    if not conn:
        return
    
    try:
        # Get basic database info
        tables = get_table_info(conn)
        print(f"Database contains {len(tables)} tables:")
        for table in sorted(tables):
            print(f"   - {table}")
        print()
        
        # Get user count
        user_count = get_user_count(conn)
        print(f"Total Users: {user_count}")
        print()
        
        if user_count == 0:
            print("No users found in the database")
            return
        
        # Get all users
        users = get_all_users(conn)
        print("USER DETAILS:")
        print("=" * 50)
        
        for user in users:
            user_id, username, email, is_active, role_id, org_id = user
            
            print(f"\nUser ID: {user_id}")
            print(f"   Username: {username}")
            print(f"   Email: {email}")
            print(f"   Active: {'Yes' if is_active else 'No'}")
            print(f"   Role ID: {role_id}")
            print(f"   Organization ID: {org_id}")
            
            # Get user preferences
            preferences = get_user_preferences(conn, user_id)
            if preferences:
                print(f"\n   Preferences:")
                for pref in preferences:
                    selected_modules, module_settings, dashboard_layout, default_currency, timezone, date_format, theme, language, notifications_enabled, industry, business_size, company_name, created_at, updated_at = pref
                    
                    if selected_modules:
                        print(f"      - Selected Modules: {format_json_value(selected_modules)}")
                    if module_settings:
                        print(f"      - Module Settings: {format_json_value(module_settings)}")
                    if dashboard_layout:
                        print(f"      - Dashboard Layout: {format_json_value(dashboard_layout)}")
                    if default_currency:
                        print(f"      - Default Currency: {default_currency}")
                    if timezone:
                        print(f"      - Timezone: {timezone}")
                    if date_format:
                        print(f"      - Date Format: {date_format}")
                    if theme:
                        print(f"      - Theme: {theme}")
                    if language:
                        print(f"      - Language: {language}")
                    if notifications_enabled is not None:
                        print(f"      - Notifications: {'Enabled' if notifications_enabled else 'Disabled'}")
                    if industry:
                        print(f"      - Industry: {industry}")
                    if business_size:
                        print(f"      - Business Size: {business_size}")
                    if company_name:
                        print(f"      - Company Name: {company_name}")
                    if created_at:
                        print(f"      - Created: {created_at}")
                    if updated_at:
                        print(f"      - Updated: {updated_at}")
            else:
                print(f"\n   Preferences: None")
            
            # Get user modules
            modules = get_user_modules(conn, user_id)
            if modules:
                print(f"\n   Modules ({len(modules)} items):")
                for module in modules:
                    module_id, is_active, is_enabled, permissions, activated_at, deactivated_at = module
                    print(f"      - {module_id}: {'Active' if is_active else 'Inactive'}")
                    print(f"        Enabled: {'Yes' if is_enabled else 'No'}")
                    print(f"        Activated: {activated_at}")
                    if permissions:
                        print(f"        Permissions: {format_json_value(permissions)}")
            else:
                print(f"\n   Modules: None")
            
            # Get user roles
            roles = get_user_roles(conn, user_id)
            if roles:
                print(f"\n   Roles ({len(roles)} items):")
                for role in roles:
                    role_id, role_name, permissions, granted_at, expires_at, is_active = role
                    print(f"      - {role_name or 'Unknown Role'}: {'Active' if is_active else 'Inactive'}")
                    print(f"        Granted: {granted_at}")
                    if expires_at:
                        print(f"        Expires: {expires_at}")
                    if permissions:
                        print(f"        Permissions: {format_json_value(permissions)}")
            else:
                print(f"\n   Roles: None")
        
        # Get organizations
        organizations = get_organizations(conn)
        if organizations:
            print(f"\nORGANIZATIONS ({len(organizations)} total):")
            print("=" * 50)
            for org in organizations:
                org_id, name, code, is_active, created_at = org
                print(f"   - {name} (ID: {org_id})")
                print(f"     Code: {code}")
                print(f"     Active: {'Yes' if is_active else 'No'}")
                print(f"     Created: {created_at}")
        
        # Get roles
        roles = get_roles(conn)
        if roles:
            print(f"\nSYSTEM ROLES ({len(roles)} total):")
            print("=" * 50)
            for role in roles:
                role_id, name, permissions, created_at = role
                print(f"   - {name} (ID: {role_id})")
                if permissions:
                    print(f"     Permissions: {format_json_value(permissions)}")
                print(f"     Created: {created_at}")
        
        print(f"\nDatabase check completed successfully!")
        print(f"Summary: {user_count} users, {len(organizations)} organizations, {len(roles)} roles")
        
    except Exception as e:
        print(f"Error during database check: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
