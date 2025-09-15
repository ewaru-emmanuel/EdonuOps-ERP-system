import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Badge,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  ListItemIcon,
  ListItemText,
  Chip,
  Tooltip,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  TrendingUp as TrendingUpIcon,
  Email as EmailIcon,
  Mic as MicIcon,
  DataUsage as DataUsageIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon
} from '@mui/icons-material';

const SimplifiedTopBar = ({ 
  onMenuToggle, 
  sidebarOpen,
  notifications = [],
  unreadCount = 0,
  user = {},
  onLogout,
  onNotificationClick
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [notificationMenuAnchor, setNotificationMenuAnchor] = useState(null);

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const handleNotificationMenuOpen = (event) => {
    setNotificationMenuAnchor(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationMenuAnchor(null);
  };

  const handleLogout = () => {
    onLogout();
    handleUserMenuClose();
  };

  // Get icon for notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'integration_gap':
        return <WarningIcon fontSize="small" color="warning" />;
      case 'ticket_sla':
        return <WarningIcon fontSize="small" color="error" />;
      case 'csv_import':
        return <InfoIcon fontSize="small" color="info" />;
      case 'kb_attachment':
        return <InfoIcon fontSize="small" color="primary" />;
      default:
        return <NotificationsIcon fontSize="small" />;
    }
  };

  // Get notification color
  const getNotificationColor = (type) => {
    switch (type) {
      case 'integration_gap':
        return 'warning';
      case 'ticket_sla':
        return 'error';
      case 'csv_import':
        return 'info';
      case 'kb_attachment':
        return 'primary';
      default:
        return 'default';
    }
  };

  return (
    <AppBar 
      position="fixed" 
      sx={{ 
        zIndex: theme.zIndex.drawer + 1,
        backgroundColor: 'background.paper',
        color: 'text.primary',
        borderBottom: '1px solid',
        borderColor: 'divider',
        boxShadow: 'none'
      }}
    >
      <Toolbar sx={{ minHeight: 64 }}>
        {/* Menu Toggle */}
        <IconButton
          color="inherit"
          aria-label="toggle sidebar"
          onClick={onMenuToggle}
          edge="start"
          sx={{ 
            mr: 2,
            backgroundColor: 'action.hover',
            '&:hover': {
              backgroundColor: 'action.selected'
            }
          }}
        >
          <MenuIcon />
        </IconButton>

        {/* Page Title */}
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            flexGrow: 1,
            fontWeight: 600,
            color: 'text.primary'
          }}
        >
          {sidebarOpen ? '' : 'EdonuOps'}
        </Typography>

        {/* Right Side Actions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* AI Status Indicator */}
          <Tooltip title="AI Features Active">
            <Chip
              icon={<PsychologyIcon />}
              label="AI"
              size="small"
              color="primary"
              variant="outlined"
              sx={{ 
                height: 28,
                '& .MuiChip-icon': { fontSize: 16 }
              }}
            />
          </Tooltip>

          {/* Notifications */}
          <Tooltip title={`${unreadCount} unread notifications`}>
            <IconButton
              color="inherit"
              onClick={handleNotificationMenuOpen}
              sx={{
                backgroundColor: unreadCount > 0 ? 'error.50' : 'transparent',
                '&:hover': {
                  backgroundColor: unreadCount > 0 ? 'error.100' : 'action.hover'
                }
              }}
            >
              <Badge badgeContent={unreadCount} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User Menu */}
          <Tooltip title="User menu">
            <IconButton
              color="inherit"
              onClick={handleUserMenuOpen}
              sx={{
                backgroundColor: 'action.hover',
                '&:hover': {
                  backgroundColor: 'action.selected'
                }
              }}
            >
              <Avatar 
                sx={{ 
                  width: 32, 
                  height: 32,
                  backgroundColor: 'primary.main',
                  fontSize: '0.875rem'
                }}
              >
                {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>

        {/* User Menu Dropdown */}
        <Menu
          anchorEl={userMenuAnchor}
          open={Boolean(userMenuAnchor)}
          onClose={handleUserMenuClose}
          PaperProps={{
            sx: {
              mt: 1,
              minWidth: 200,
              '& .MuiMenuItem-root': {
                px: 2,
                py: 1
              }
            }
          }}
        >
          <MenuItem disabled>
            <ListItemIcon>
              <PersonIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText 
              primary={user.name || 'User'}
              secondary={user.role || 'Administrator'}
            />
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleUserMenuClose}>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Settings" />
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            <ListItemText primary="Logout" />
          </MenuItem>
        </Menu>

        {/* Notifications Menu */}
        <Menu
          anchorEl={notificationMenuAnchor}
          open={Boolean(notificationMenuAnchor)}
          onClose={handleNotificationMenuClose}
          PaperProps={{
            sx: {
              mt: 1,
              minWidth: 320,
              maxHeight: 400,
              overflow: 'auto'
            }
          }}
        >
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
              Notifications
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {unreadCount} unread notifications
            </Typography>
          </Box>

          {notifications.length === 0 ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <NotificationsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
              <Typography variant="body2" color="text.secondary">
                No notifications
              </Typography>
            </Box>
          ) : (
            notifications.slice(0, 10).map((notification, index) => (
              <MenuItem
                key={notification.id || index}
                onClick={() => {
                  if (onNotificationClick) {
                    onNotificationClick(notification);
                  }
                  handleNotificationMenuClose();
                }}
                sx={{
                  borderLeft: 3,
                  borderLeftColor: getNotificationColor(notification.type) + '.main',
                  '&:hover': {
                    backgroundColor: 'action.hover'
                  }
                }}
              >
                <ListItemIcon>
                  {getNotificationIcon(notification.type)}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {notification.message}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {notification.type.replace('_', ' ').toUpperCase()}
                    </Typography>
                  }
                />
              </MenuItem>
            ))
          )}

          {notifications.length > 10 && (
            <>
              <Divider />
              <MenuItem onClick={handleNotificationMenuClose}>
                <ListItemText 
                  primary="View all notifications"
                  sx={{ textAlign: 'center', color: 'primary.main' }}
                />
              </MenuItem>
            </>
          )}
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default SimplifiedTopBar;




