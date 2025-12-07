# UserManagement Component - Complete Data Requirements

## 📋 Summary

UserManagement component fetches data from **3 main endpoints** on page load:
1. `/api/admin/users` - List of all users
2. `/api/admin/roles` - List of all roles (for dropdowns)
3. `/api/admin/stats` - User statistics (for dashboard cards)

---

## 1. GET `/api/admin/users`
**Purpose:** Fetch all users with their details

**Backend Route:** `backend/modules/core/user_management_routes.py:16`

**Expected Response:**
```json
{
  "users": [
    {
      "id": 28,
      "username": "emmanuel",
      "email": "apolloemmanuel01@gmail.com",
      "role": "admin",  // from user.role.role_name
      "role_id": 2,
      "organization": null,  // from Organization.name (if exists)
      "organization_id": null,  // from user.organization_id (if column exists)
      "is_active": true,
      "created_at": "2025-11-26T...",
      "last_login": null,
      "permission_count": 5,  // from PermissionManager.get_user_permissions()
      "modules": ["finance", "crm"]  // from PermissionManager.get_user_modules()
    }
  ],
  "total_count": 1
}
```

**Fields Used in Frontend:**
- `users[].id` - User ID (for actions)
- `users[].username` - Username (displayed in table)
- `users[].email` - Email (displayed in table)
- `users[].role` - Role name (displayed in table as Chip)
- `users[].organization` - Organization name (displayed in table, shows "Default" if null)
- `users[].is_active` - Status (Active/Inactive Chip)
- `users[].permission_count` - Number of permissions (displayed as Chip with tooltip)
- `users[].modules` - List of accessible modules (shown in view dialog)
- `users[].created_at` - Creation date (shown in view dialog)
- `users[].last_login` - Last login date (shown in view dialog)
- `users[].role_id` - Used when editing user (form select)
- `users[].organization_id` - Used when editing user (defaults to 1 if null)

**Backend Code Issues:**
- ✅ **FIXED:** `user.organization` access removed (line 29-42)
- ⚠️ **POTENTIAL:** `user.role.role_name` (line 51) - If `user.role` is None, this will fail
- ✅ **FIXED:** `organization` - Returns null if not exists
- ✅ **FIXED:** `organization_id` - Returns null if not exists
- ⚠️ **POTENTIAL:** `PermissionManager.get_user_permissions()` (line 62) - Could fail
- ⚠️ **POTENTIAL:** `PermissionManager.get_user_modules()` (line 64) - Could fail

---

## 2. GET `/api/admin/roles`
**Purpose:** Fetch all roles for dropdown selection

**Backend Route:** `backend/modules/core/user_management_routes.py:369`

**Expected Response:**
```json
{
  "roles": [
    {
      "id": 1,
      "role_name": "user",
      "permission_count": 3,
      "user_count": 0,
      "permissions": null
    },
    {
      "id": 2,
      "role_name": "admin",
      "permission_count": 10,
      "user_count": 1,
      "permissions": null
    }
  ],
  "total_count": 5
}
```

**Fields Used in Frontend:**
- `roles[].id` - Role ID (used in form select value)
- `roles[].role_name` - Role name (displayed in dropdown: "admin (10 permissions)")
- `roles[].permission_count` - Number of permissions (displayed in dropdown)

**Backend Code:**
- Queries `Role.query.all()`
- Counts users per role: `User.query.filter_by(role_id=role.id).count()`
- Counts permissions: `RolePermission.query.filter_by(role_id=role.id).count()`

**Potential Issues:**
- ✅ Should work fine - simple queries

---

## 3. GET `/api/admin/stats`
**Purpose:** Fetch user statistics for dashboard cards

**Backend Route:** `backend/modules/core/user_management_routes.py:466`

**Expected Response:**
```json
{
  "total_users": 1,
  "active_users": 1,
  "inactive_users": 0,
  "recent_logins": 1,
  "role_distribution": [
    {"role": "admin", "count": 1},
    {"role": "user", "count": 0}
  ]
}
```

**Fields Used in Frontend:**
- `stats.total_users` - Total users count (displayed in card)
- `stats.active_users` - Active users count (displayed in card)
- `stats.inactive_users` - Inactive users count (displayed in card)
- `stats.recent_logins` - Recent logins count (displayed in card)

**Backend Code:**
- `User.query.count()` - Total users
- `User.query.filter_by(is_active=True).count()` - Active users (with fallback)
- `User.query.filter(User.last_login >= seven_days_ago).count()` - Recent logins (with fallback)
- Role distribution via JOIN query

**Potential Issues:**
- ✅ Has fallbacks for missing columns
- ✅ Should work fine

---

## Additional API Calls (User Actions)

### 4. POST `/api/admin/users`
**Purpose:** Create new user

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "role_id": 2,
  "organization_id": 1
}
```

**Potential Issues:**
- `organization_id: 1` is hardcoded in frontend - might not exist

---

### 5. PUT `/api/admin/users/{user_id}`
**Purpose:** Update existing user

**Request Body:**
```json
{
  "username": "updateduser",
  "email": "updated@example.com",
  "role_id": 2,
  "organization_id": 1
  // password is optional
}
```

---

### 6. DELETE `/api/admin/users/{user_id}`
**Purpose:** Delete user

**Potential Issues:**
- Need to check if this endpoint exists and works correctly

---

## Summary of All Data Fetched

1. **Users List** - `/api/admin/users`
   - User details (id, username, email, role, organization, status)
   - Permission count
   - Accessible modules
   - Created/last login dates

2. **Roles List** - `/api/admin/roles`
   - All available roles for dropdown

3. **Statistics** - `/api/admin/stats`
   - Total/active/inactive user counts
   - Recent logins count

4. **User Actions** - POST/PUT/DELETE `/api/admin/users`
   - Create, update, delete users

---

## Known Issues

1. ✅ **FIXED:** `user.organization` attribute access (removed)
2. ⚠️ **POTENTIAL:** `user.role.role_name` - if `user.role` is None
3. ⚠️ **POTENTIAL:** `PermissionManager.get_user_permissions()` - could fail
4. ⚠️ **POTENTIAL:** `PermissionManager.get_user_modules()` - could fail
5. ⚠️ **POTENTIAL:** Hardcoded `organization_id: 1` in frontend forms

