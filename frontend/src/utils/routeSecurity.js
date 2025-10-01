/**
 * Route Security Utilities
 * Ensures proper authentication for all ERP routes
 */

// Define public routes that don't require authentication
export const PUBLIC_ROUTES = [
  '/',
  '/login',
  '/register'
];

// Define all protected routes that require authentication
export const PROTECTED_ROUTES = [
  '/dashboard',
  '/dashboard/settings',
  '/admin/settings',
  '/notifications',
  '/finance',
  '/crm',
  '/procurement',
  '/inventory',
  '/profile',
  '/onboarding'
];

/**
 * Check if a route is public (doesn't require authentication)
 */
export const isPublicRoute = (pathname) => {
  return PUBLIC_ROUTES.includes(pathname);
};

/**
 * Check if a route is protected (requires authentication)
 */
export const isProtectedRoute = (pathname) => {
  return PROTECTED_ROUTES.some(route => pathname.startsWith(route));
};

/**
 * Check if access to a route should be allowed
 */
export const isRouteAccessible = (pathname, isAuthenticated) => {
  // Public routes are always accessible
  if (isPublicRoute(pathname)) {
    return true;
  }
  
  // Protected routes require authentication
  if (isProtectedRoute(pathname)) {
    return isAuthenticated;
  }
  
  // Unknown routes are treated as protected
  return isAuthenticated;
};

/**
 * Get the appropriate redirect route for unauthorized access
 */
export const getRedirectRoute = (pathname, isAuthenticated) => {
  if (!isAuthenticated && !isPublicRoute(pathname)) {
    return '/login';
  }
  
  if (isAuthenticated && (pathname === '/login' || pathname === '/register')) {
    return '/dashboard';
  }
  
  return null;
};











