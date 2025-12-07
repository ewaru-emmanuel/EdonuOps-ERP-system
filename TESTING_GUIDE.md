# Comprehensive Testing Guide
## ERP System - Production Readiness Testing

This guide will help you systematically test all the features and updates we've implemented.

---

## Pre-Testing Checklist

### 1. Backend Status
- ✅ Backend server running (`python run.py`)
- ✅ No critical errors in console
- ✅ All blueprints registered successfully

### 2. Frontend Status
- ✅ Frontend server running (`npm start` in frontend directory)
- ✅ No compilation errors
- ✅ Can access login page

### 3. Database
- ✅ Database is accessible
- ✅ At least one admin user exists
- ✅ Test tenant data available (optional)

---

## Testing Phases

### Phase 1: Authentication & Basic Access
**Goal:** Verify login and basic navigation work

#### Test 1.1: Login
1. Navigate to login page
2. Log in with admin credentials
3. **Expected:** Successfully logged in, redirected to dashboard
4. **Check:** Token stored in localStorage (`access_token`)

#### Test 1.2: Navigation
1. Check if main navigation menu appears
2. Navigate to different modules (Finance, Inventory, CRM, etc.)
3. **Expected:** All modules accessible, no 404 errors

---

### Phase 2: Permission Management UI
**Goal:** Test the new Permission Management interface

#### Test 2.1: Access Permission Management
1. Navigate to Admin Settings (usually in user menu or admin section)
2. Click on "Permissions" tab
3. **Expected:** Permission Management UI loads without errors
4. **Check:** You see two tabs: "Role Permissions" and "User Roles"

#### Test 2.2: View Permissions
1. In "Role Permissions" tab, verify:
   - List of permissions grouped by module (finance, inventory, crm, etc.)
   - List of roles (admin, user, etc.) as columns
   - Checkboxes showing permission assignments
2. **Expected:** All permissions and roles displayed correctly

#### Test 2.3: View Roles
1. Check the roles displayed
2. **Expected:** At least "admin" role visible
3. **Note:** Admin role should be locked (no edit/delete buttons)

#### Test 2.4: Create New Role
1. Click "Create Role" button
2. Enter role name (e.g., "Accountant", "Manager")
3. Click "Create"
4. **Expected:** 
   - Role appears in the table
   - Success message displayed
   - New role column added to permissions table

#### Test 2.5: Assign Permissions to Role
1. Find a permission (e.g., "finance.journal.create")
2. Check the checkbox under your new role
3. **Expected:**
   - Checkbox becomes checked
   - Success message appears
   - Permission persists after page refresh

#### Test 2.6: Remove Permission from Role
1. Uncheck a permission checkbox
2. **Expected:**
   - Checkbox becomes unchecked
   - Success message appears
   - Change persists after refresh

#### Test 2.7: Edit Role Name
1. Click edit icon on a role (not admin)
2. Change the role name
3. Click "Update"
4. **Expected:** Role name updates successfully

#### Test 2.8: Delete Role
1. Click delete icon on a role (not admin)
2. Confirm deletion
3. **Expected:**
   - Role removed from table
   - Success message displayed
   - Role column removed from permissions table

#### Test 2.9: User Roles Tab
1. Switch to "User Roles" tab
2. **Expected:**
   - List of all users displayed
   - Current role shown for each user
   - Dropdown to change user roles

#### Test 2.10: Assign Role to User
1. Select a role from dropdown for a user
2. **Expected:**
   - Role updates immediately
   - Success message displayed
   - Change persists after refresh

---

### Phase 3: Route Protection (RBAC)
**Goal:** Verify that routes are properly protected by permissions

#### Test 3.1: Test with Admin User
1. Ensure you're logged in as admin
2. Try accessing various endpoints:
   - Create journal entry
   - View reports
   - Manage inventory
   - Access CRM features
3. **Expected:** All operations succeed (admin has all permissions)

#### Test 3.2: Test with Limited Role User
1. Create a new user with limited role (e.g., "Viewer")
2. Assign only read permissions to this role:
   - `finance.reports.read`
   - `inventory.products.read`
   - `crm.contacts.read`
3. Log in as this user
4. Try to:
   - **Read operations:** Should succeed
   - **Create operations:** Should fail with 403 Forbidden
   - **Update operations:** Should fail with 403 Forbidden
   - **Delete operations:** Should fail with 403 Forbidden

#### Test 3.3: Test Permission Enforcement
1. As limited user, try to:
   - Create a journal entry → Should fail
   - View financial reports → Should succeed
   - Create a product → Should fail
   - View products → Should succeed
2. **Expected:** API returns 403 Forbidden for unauthorized actions

#### Test 3.4: Test Frontend Permission Checks
1. As limited user, check UI:
   - Buttons for create/edit/delete should be hidden or disabled
   - Read-only views should be accessible
2. **Expected:** UI reflects user permissions

---

### Phase 4: Tenant Isolation
**Goal:** Verify multi-tenant data isolation

#### Test 4.1: Create Test Data in Tenant A
1. Log in as user in Tenant A
2. Create some test data:
   - Create an account
   - Create a journal entry
   - Create a product
3. Note the IDs/names of created items

#### Test 4.2: Switch to Tenant B
1. Log in as user in Tenant B (or switch tenant if supported)
2. Try to access the data created in Tenant A
3. **Expected:** Cannot see Tenant A's data

#### Test 4.3: Verify Data Isolation
1. In Tenant B, create similar data with same names/codes
2. **Expected:** 
   - Can create data with same names (different tenant_id)
   - Data is completely separate
   - No conflicts or cross-tenant visibility

#### Test 4.4: Test Tenant-Scoped Queries
1. In Tenant A, query all accounts
2. **Expected:** Only see accounts with Tenant A's tenant_id
3. Repeat for other entities (journal entries, products, etc.)

---

### Phase 5: Automated Backups
**Goal:** Verify backup system is working

#### Test 5.1: Check Backup Service
1. Check if backup service files exist:
   - `backend/services/automated_backup_service.py`
   - `backend/services/backup_scheduler.py`
2. **Expected:** Files exist

#### Test 5.2: Manual Backup Test
1. In backend, run backup manually (if script exists):
   ```python
   from services.automated_backup_service import BackupService
   service = BackupService()
   service.create_backup()
   ```
2. **Expected:** Backup file created in backup directory

#### Test 5.3: Verify Backup Files
1. Check backup directory (usually `backend/backups/`)
2. **Expected:** 
   - Backup files exist
   - Files have timestamps
   - Files are not empty

---

### Phase 6: API Endpoint Testing
**Goal:** Verify all protected endpoints work correctly

#### Test 6.1: Finance Endpoints
Test these endpoints (with appropriate permissions):
- `GET /api/finance/accounts` - List accounts
- `POST /api/finance/accounts` - Create account (requires `finance.accounts.create`)
- `GET /api/finance/journal` - List journal entries
- `POST /api/finance/journal` - Create journal entry (requires `finance.journal.create`)
- `GET /api/finance/reports/*` - Financial reports (requires `finance.reports.read`)

#### Test 6.2: Inventory Endpoints
- `GET /api/inventory/products` - List products
- `POST /api/inventory/products` - Create product (requires `inventory.products.create`)
- `GET /api/inventory/stock` - Stock levels (requires `inventory.stock.read`)

#### Test 6.3: CRM Endpoints
- `GET /api/crm/contacts` - List contacts
- `POST /api/crm/contacts` - Create contact (requires `crm.contacts.create`)
- `GET /api/crm/leads` - List leads (requires `crm.leads.read`)

#### Test 6.4: Permission Endpoints
- `GET /api/core/permissions` - List all permissions
- `GET /api/core/permissions/roles` - List roles with permissions
- `POST /api/core/permissions/roles` - Create role (requires admin)
- `PUT /api/core/permissions/roles/{id}` - Update role permissions
- `DELETE /api/core/permissions/roles/{id}` - Delete role

---

### Phase 7: Error Handling
**Goal:** Verify proper error handling

#### Test 7.1: Unauthorized Access
1. Try to access protected endpoint without token
2. **Expected:** 401 Unauthorized

#### Test 7.2: Insufficient Permissions
1. Try to perform action without required permission
2. **Expected:** 403 Forbidden with clear error message

#### Test 7.3: Invalid Data
1. Try to create record with invalid data
2. **Expected:** 400 Bad Request with validation errors

#### Test 7.4: Not Found
1. Try to access non-existent resource
2. **Expected:** 404 Not Found

---

### Phase 8: Performance & Load
**Goal:** Basic performance checks

#### Test 8.1: Page Load Times
1. Navigate to different pages
2. Check browser DevTools Network tab
3. **Expected:** Pages load in reasonable time (< 3 seconds)

#### Test 8.2: API Response Times
1. Make API calls and check response times
2. **Expected:** Most API calls complete in < 1 second

#### Test 8.3: Database Query Performance
1. Test queries with large datasets
2. **Expected:** Queries complete without timeout

---

## Testing Checklist Summary

### Critical Features (Must Test)
- [ ] Login/Logout
- [ ] Permission Management UI (all CRUD operations)
- [ ] Role assignment to users
- [ ] Route protection (403 errors for unauthorized)
- [ ] Tenant isolation (data separation)

### Important Features (Should Test)
- [ ] All major API endpoints
- [ ] Error handling (401, 403, 404, 400)
- [ ] Data persistence (refresh page, data still there)
- [ ] UI responsiveness

### Nice to Have (Optional)
- [ ] Backup system
- [ ] Performance metrics
- [ ] Edge cases

---

## Common Issues & Solutions

### Issue: Permission Management UI not loading
**Solution:** 
- Check browser console for errors
- Verify backend is running
- Check API endpoint `/api/core/permissions` is accessible

### Issue: 403 Forbidden on all requests
**Solution:**
- Check if user has any role assigned
- Verify permissions are assigned to role
- Check JWT token is valid

### Issue: Can't see other tenant's data (but should)
**Solution:**
- This is correct behavior! Tenant isolation is working
- To test cross-tenant, use different user accounts

### Issue: Changes not persisting
**Solution:**
- Check browser console for API errors
- Verify backend database connection
- Check if transaction is committed

---

## Reporting Test Results

Document any issues found:
1. **What you tested:** (e.g., "Creating a new role")
2. **Expected behavior:** (e.g., "Role should be created and appear in table")
3. **Actual behavior:** (e.g., "Error message appeared, role not created")
4. **Steps to reproduce:** (detailed steps)
5. **Screenshots/Logs:** (if available)

---

## Next Steps After Testing

1. **If all tests pass:** System is ready for production use
2. **If issues found:** Document and prioritize fixes
3. **If performance issues:** Consider optimization
4. **If security concerns:** Review and harden

---

**Happy Testing! 🚀**

