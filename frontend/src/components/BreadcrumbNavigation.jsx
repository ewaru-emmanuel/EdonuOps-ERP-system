import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Typography, Breadcrumbs, Link } from '@mui/material';
import { Home, ChevronRight } from '@mui/icons-material';

const BreadcrumbNavigation = ({ sidebarOpen }) => {
  const location = useLocation();
  const navigate = useNavigate();

  // Don't show breadcrumb on dashboard and other top-level pages
  if (location.pathname === '/dashboard' || 
      location.pathname === '/dashboard/settings' || 
      location.pathname === '/admin/settings' || 
      location.pathname === '/notifications') {
    return null;
  }

  // Get current module name based on path
  const getModuleName = (pathname) => {
    if (pathname.startsWith('/finance')) return 'Finance';
    if (pathname.startsWith('/crm')) return 'CRM';
    if (pathname.startsWith('/inventory')) return 'Inventory';
    if (pathname.startsWith('/procurement')) return 'Procurement';
    if (pathname.startsWith('/admin')) return 'Admin';
    if (pathname.startsWith('/dashboard/settings')) return 'Dashboard Settings';
    if (pathname.startsWith('/notifications')) return 'Notifications';
    return 'Module';
  };

  const currentModule = getModuleName(location.pathname);

  const handleDashboardClick = (event) => {
    event.preventDefault();
    navigate('/dashboard');
  };

  // Only show breadcrumb when sidebar is open
  if (!sidebarOpen) {
    return null;
  }

  return (
    <Box sx={{ 
      px: 2, 
      py: 1, 
      borderBottom: '1px solid #e0e0e0',
      backgroundColor: '#fafafa'
    }}>
      <Breadcrumbs 
        separator={<ChevronRight fontSize="small" sx={{ color: '#5f6368' }} />}
        sx={{
          '& .MuiBreadcrumbs-separator': {
            margin: '0 4px'
          }
        }}
      >
        <Link
          component="button"
          variant="body2"
          onClick={handleDashboardClick}
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 0.5,
            color: '#1976d2',
            textDecoration: 'none',
            fontSize: '0.875rem',
            fontWeight: 400,
            '&:hover': {
              textDecoration: 'underline',
              color: '#1565c0'
            }
          }}
        >
          <Home fontSize="small" />
          Dashboard
        </Link>
        
        <Typography 
          variant="body2" 
          sx={{ 
            color: '#5f6368',
            fontSize: '0.875rem',
            fontWeight: 400
          }}
        >
          {currentModule}
        </Typography>
      </Breadcrumbs>
    </Box>
  );
};

export default BreadcrumbNavigation;
