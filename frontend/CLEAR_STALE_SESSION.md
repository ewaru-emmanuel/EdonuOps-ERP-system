# Clear Stale Session Data

## Problem:
After deleting all users from the database, your browser still has the old session token stored in localStorage. This makes the app think you're logged in, but the token is invalid.

## Solution:

### Option 1: Clear Browser Storage (Quick Fix)

1. **Open Browser Console:**
   - Press `F12` or `Ctrl+Shift+I` (Windows) / `Cmd+Option+I` (Mac)
   - Go to the "Console" tab

2. **Run this command:**
   ```javascript
   localStorage.clear();
   location.reload();
   ```

3. **Refresh the page** - You should now be logged out

### Option 2: Clear Specific Session Items

Run these commands in the browser console:

```javascript
localStorage.removeItem('sessionToken');
localStorage.removeItem('userId');
localStorage.removeItem('userEmail');
localStorage.removeItem('username');
localStorage.removeItem('userRole');
localStorage.removeItem('access_token');
location.reload();
```

### Option 3: Use Browser DevTools

1. Open DevTools (F12)
2. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
3. Expand "Local Storage"
4. Select your domain (http://localhost:3000)
5. Delete all items or specific session items
6. Refresh the page

---

After clearing, try accessing `/dashboard` - it should redirect you to login since you're not authenticated.

