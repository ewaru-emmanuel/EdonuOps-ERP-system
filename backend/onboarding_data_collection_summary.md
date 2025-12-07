# Onboarding Data Collection & Saving - Analysis & Updates

## 📊 Data Collected During Onboarding

### From OnboardingWizard.jsx:
1. **Business Profile:**
   - `companyName` → Maps to `company_name` in users table
   - `industry` → Maps to `industry` in users table
   - `employeeCount` → Maps to `company_size` in users table
   - `annualRevenue` → (stored in onboarding_progress.data JSONB)
   - `challenges` → (stored in onboarding_progress.data JSONB)

2. **Selected Modules:**
   - Array of module IDs (stored via module activation API)

3. **CoA Template:**
   - Selected template (stored in onboarding_progress.data JSONB)

4. **Organization Setup:**
   - organizationType, departments, userPermissions, teamMembers
   - (stored in onboarding_progress.data JSONB)

### From OnboardingHub.jsx:
1. **Discovery Data:**
   - `industry` → Maps to `industry` in users table
   - `business_size` → Maps to `company_size` in users table
   - `pain_points` → (stored in onboarding_progress.data JSONB)
   - `goals` → (stored in onboarding_progress.data JSONB)

## ✅ Updates Made

### 1. Added Tenant Helpers (Like CoA)
- Imported `get_current_user_tenant_id` and `get_current_user_id`
- All onboarding routes now use tenant-aware pattern

### 2. Updated `complete_onboarding_step`:
- ✅ Uses tenant helpers
- ✅ Validates user belongs to tenant
- ✅ Maps frontend field names to database columns
- ✅ Stores challenges/pain_points in onboarding_progress.data JSONB
- ✅ Updates users table with company_name, company_size, industry

### 3. Updated `update_user_profile`:
- ✅ Uses tenant helpers
- ✅ Validates user belongs to tenant
- ✅ Maps frontend field names to database columns

### 4. Updated `complete_onboarding`:
- ✅ Uses tenant helpers
- ✅ Validates user belongs to tenant

## 🔄 How It Works Now (Like CoA)

1. **Tenant Context:** Gets tenant_id and user_id from JWT (same as CoA)
2. **Validation:** Ensures user belongs to tenant before any updates
3. **Data Storage:**
   - Company fields → `users` table (company_name, company_size, industry)
   - Complex data → `onboarding_progress` table (data JSONB column)
4. **Error Handling:** Proper rollback and error messages

## 📝 Next Steps

1. ✅ Backend updated to use tenant helpers
2. ⏳ Frontend needs to call `/api/onboarding/step/company_info` endpoint
3. ⏳ Test data collection and saving
4. ⏳ Verify data appears in users table and onboarding_progress table


