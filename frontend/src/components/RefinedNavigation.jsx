import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  Tooltip,
  Divider,
  Collapse,
  useTheme,
  useMediaQuery,
  Avatar,
  Chip,
  Badge
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  AccountBalance as FinanceIcon,
  People as CRMIcon,
  Inventory as InventoryIcon,
  ShoppingCart as ProcurementIcon,
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  Settings as SettingsIcon,
  AdminPanelSettings as AdminPanelSettingsIcon,
  Notifications as NotificationsIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  TrendingUp as TrendingUpIcon,
  Email as EmailIcon,
  Mic as MicIcon,
  DataUsage as DataUsageIcon
} from '@mui/icons-material';

const RefinedNavigation = ({ 
  open, 
  onToggle, 
  notifications = [], 
  unreadCount = 0,
  selectedModules = [],
  onNotificationClick 
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();
  const navigate = useNavigate();
  
  const [expandedSections, setExpandedSections] = useState({});
  const [hoveredItem, setHoveredItem] = useState(null);

  // Navigation structure - simplified and organized
  const navigationItems = [
    {
      id: 'dashboard',
      title: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/dashboard',
      moduleId: 'dashboard'
    },
    {
      id: 'crm',
      title: 'CRM',
      icon: <CRMIcon />,
      path: '/crm',
      moduleId: 'crm',
      badge: unreadCount > 0 ? unreadCount : null,
      children: [
        {
          id: 'crm-contacts',
          title: 'Contacts',
          path: '/crm/contacts',
          icon: <People as PeopleIcon />
        },
        {
          id: 'crm-leads',
          title: 'Leads',
          path: '/crm/leads',
          icon: <TrendingUpIcon />
        },
        {
          id: 'crm-opportunities',
          title: 'Opportunities',
          path: '/crm/opportunities',
          icon: <TrendingUpIcon />
        },
        {
          id: 'crm-ai-features',
          title: 'AI Features',
          path: '/crm/ai',
          icon: <PsychologyIcon />,
          badge: 'NEW',
          badgeColor: 'success'
        }
      ]
    },
    {
      id: 'finance',
      title: 'Finance',
      icon: <FinanceIcon />,
      path: '/finance',
      moduleId: 'financials'
    },
    {
      id: 'inventory',
      title: 'Inventory',
      icon: <InventoryIcon />,
      path: '/inventory',
      moduleId: 'inventory'
    },
    {
      id: 'procurement',
      title: 'Procurement',
      icon: <ProcurementIcon />,
      path: '/procurement',
      moduleId: 'procurement'
    }
  ];

  // Settings and admin items
  const settingsItems = [
    {
      id: 'dashboard-settings',
      title: 'Dashboard Settings',
      icon: <SettingsIcon />,
      path: '/dashboard/settings'
    },
    {
      id: 'admin-settings',
      title: 'Admin Settings',
      icon: <AdminPanelSettingsIcon />,
      path: '/admin/settings'
    }
  ];

  // Check if module is enabled
  const isModuleEnabled = (moduleId) => {
    return selectedModules.includes(moduleId);
  };

  // Handle navigation
  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      onToggle(); // Close drawer on mobile after navigation
    }
  };

  // Toggle section expansion
  const toggleSection = (sectionId) => {
    setExpandedSections(prev => ({
      ...prev,
      [sectionId]: !prev[sectionId]
    }));
  };

  // Check if current path is active
  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  // Render navigation item
  const renderNavItem = (item, level = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedSections[item.id];
    const isItemActive = isActive(item.path);
    const isEnabled = !item.moduleId || isModuleEnabled(item.moduleId);

    if (!isEnabled) return null;

    return (
      <React.Fragment key={item.id}>
        <ListItem 
          disablePadding 
          sx={{ 
            pl: level * 2,
            '&:hover': {
              backgroundColor: 'action.hover'
            }
          }}
        >
          <ListItemButton
            onClick={() => {
              if (hasChildren) {
                toggleSection(item.id);
              } else {
                handleNavigation(item.path);
              }
            }}
            onMouseEnter={() => setHoveredItem(item.id)}
            onMouseLeave={() => setHoveredItem(null)}
            sx={{
              minHeight: 48,
              backgroundColor: isItemActive ? 'primary.50' : 'transparent',
              borderRight: isItemActive ? 3 : 0,
              borderRightColor: 'primary.main',
              '&:hover': {
                backgroundColor: isItemActive ? 'primary.100' : 'action.hover'
              }
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: open ? 56 : 24,
                color: isItemActive ? 'primary.main' : 'inherit',
                transition: 'all 0.2s ease'
              }}
            >
              {item.icon}
            </ListItemIcon>
            
            {open && (
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: isItemActive ? 600 : 400,
                        color: isItemActive ? 'primary.main' : 'inherit'
                      }}
                    >
                      {item.title}
                    </Typography>
                    {item.badge && (
                      <Chip
                        label={item.badge}
                        size="small"
                        color={item.badgeColor || 'primary'}
                        sx={{ 
                          height: 20, 
                          fontSize: '0.7rem',
                          '& .MuiChip-label': { px: 1 }
                        }}
                      />
                    )}
                  </Box>
                }
              />
            )}

            {hasChildren && open && (
              <Box sx={{ ml: 'auto' }}>
                {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </Box>
            )}
          </ListItemButton>
        </ListItem>

        {/* Render children */}
        {hasChildren && open && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children.map(child => renderNavItem(child, level + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  // Tooltip for collapsed items
  const renderCollapsedItem = (item) => {
    const isItemActive = isActive(item.path);
    const isEnabled = !item.moduleId || isModuleEnabled(item.moduleId);

    if (!isEnabled) return null;

    return (
      <Tooltip key={item.id} title={item.title} placement="right" arrow>
        <ListItem disablePadding>
          <ListItemButton
            onClick={() => handleNavigation(item.path)}
            sx={{
              minHeight: 48,
              justifyContent: 'center',
              backgroundColor: isItemActive ? 'primary.50' : 'transparent',
              borderRight: isItemActive ? 3 : 0,
              borderRightColor: 'primary.main',
              '&:hover': {
                backgroundColor: isItemActive ? 'primary.100' : 'action.hover'
              }
            }}
          >
            <Badge 
              badgeContent={item.badge} 
              color="error"
              invisible={!item.badge}
            >
              <ListItemIcon
                sx={{
                  minWidth: 'auto',
                  color: isItemActive ? 'primary.main' : 'inherit'
                }}
              >
                {item.icon}
              </ListItemIcon>
            </Badge>
          </ListItemButton>
        </ListItem>
      </Tooltip>
    );
  };

  const drawerWidth = open ? 240 : 60;

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'permanent'}
      open={open}
      onClose={onToggle}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          overflowX: 'hidden',
          borderRight: '1px solid',
          borderColor: 'divider',
          backgroundColor: 'background.paper'
        },
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          justifyContent: open ? 'space-between' : 'center',
          minHeight: 64
        }}
      >
        {open && (
          <Box>
            <Typography 
              variant="h6" 
              sx={{ 
                fontWeight: 'bold', 
                color: 'primary.main',
                fontSize: '1.1rem'
              }}
            >
              EdonuOps
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Simple ERP Platform
            </Typography>
          </Box>
        )}
        
        <IconButton 
          onClick={onToggle}
          sx={{ 
            ml: open ? 1 : 0,
            backgroundColor: 'action.hover',
            '&:hover': {
              backgroundColor: 'action.selected'
            }
          }}
        >
          {open ? <ChevronLeftIcon /> : <ChevronRightIcon />}
        </IconButton>
      </Box>

      {/* Navigation Items */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <List sx={{ px: 1, py: 2 }}>
          {open ? (
            // Expanded view
            navigationItems.map(item => renderNavItem(item))
          ) : (
            // Collapsed view
            navigationItems.map(item => renderCollapsedItem(item))
          )}
        </List>

        <Divider sx={{ mx: 2 }} />

        {/* Settings Section */}
        <List sx={{ px: 1, py: 2 }}>
          {open ? (
            settingsItems.map(item => renderNavItem(item))
          ) : (
            settingsItems.map(item => renderCollapsedItem(item))
          )}
        </List>
      </Box>

      {/* Footer - Module Status */}
      {open && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: 'success.main'
              }}
            />
            <Typography variant="caption" color="text.secondary">
              {selectedModules.length} modules active
            </Typography>
          </Box>
          <Typography variant="caption" color="text.secondary">
            Simple • Fast • Reliable
          </Typography>
        </Box>
      )}
    </Drawer>
  );
};

export default RefinedNavigation;




