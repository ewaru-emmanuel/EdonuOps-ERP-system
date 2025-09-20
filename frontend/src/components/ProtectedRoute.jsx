import React, { useMemo, useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Box, CircularProgress, Typography } from '@mui/material';

const ProtectedRoute = ({ children, requireAuth = true }) => {
  const { isAuthenticated, loading, initialized } = useAuth();
  const location = useLocation();
  const [timeoutReached, setTimeoutReached] = useState(false);

  // Set a timeout to prevent infinite loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setTimeoutReached(true);
    }, 5000); // 5 second timeout

    return () => clearTimeout(timer);
  }, []);

  // Memoize the authentication decision to prevent infinite loops
  const authDecision = useMemo(() => {
    if ((loading || !initialized) && !timeoutReached) {
      return 'loading';
    }
    
    // If timeout reached and still loading, assume not authenticated
    if (timeoutReached && (loading || !initialized)) {
      return requireAuth ? 'redirect-to-login' : 'render-children';
    }
    
    if (requireAuth && !isAuthenticated) {
      return 'redirect-to-login';
    }
    
    if (isAuthenticated && (location.pathname === '/login' || location.pathname === '/register')) {
      return 'redirect-to-dashboard';
    }
    
    return 'render-children';
  }, [loading, initialized, isAuthenticated, requireAuth, location.pathname, timeoutReached]);

  // Handle each case
  switch (authDecision) {
    case 'loading':
      return (
        <Box 
          sx={{ 
            display: 'flex', 
            flexDirection: 'column',
            justifyContent: 'center', 
            alignItems: 'center', 
            minHeight: '100vh',
            gap: 2
          }}
        >
          <CircularProgress />
          <Typography variant="body2" color="text.secondary">
            Checking authentication...
          </Typography>
        </Box>
      );
    
    case 'redirect-to-login':
      return <Navigate to="/login" state={{ from: location }} replace />;
    
    case 'redirect-to-dashboard':
      return <Navigate to="/dashboard" replace />;
    
    case 'render-children':
    default:
      return children;
  }
};

export default ProtectedRoute;
