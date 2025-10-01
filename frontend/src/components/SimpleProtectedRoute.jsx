import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Box, CircularProgress } from '@mui/material';

const SimpleProtectedRoute = ({ children }) => {
  const { isAuthenticated, initialized } = useAuth();

  // Wait for auth initialization to complete before checking authentication
  if (!initialized) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  // After initialization, check if authenticated
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

export default SimpleProtectedRoute;




