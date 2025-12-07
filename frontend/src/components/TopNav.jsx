import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Badge,
  Menu,
  MenuItem,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  Close,
  Person as PersonIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  AdminPanelSettings as AdminPanelSettingsIcon,
  Logout as LogoutIcon,
  ReportProblem as ReportProblemIcon,
  WarningAmber as WarningAmberIcon,
  MailOutline as MailOutlineIcon,
  Attachment as AttachmentIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import TenantSwitcher from './TenantSwitcher';
import apiClient from '../services/apiClient';

const TopNav = ({ variant = 'public', onModuleClick, zIndex, sidebarOpen, setSidebarOpen }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { isAuthenticated, logout: authLogout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Authenticated variant state
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [notificationsAnchor, setNotificationsAnchor] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [readIds, setReadIds] = useState(() => {
    try {
      const raw = localStorage.getItem('edonuops.notifications.readIds');
      return new Set(raw ? JSON.parse(raw) : []);
    } catch {
      return new Set();
    }
  });

  // Load notifications for authenticated variant - only if user is authenticated
  useEffect(() => {
    if (variant === 'authenticated' && isAuthenticated) {
      // Check if token exists before loading notifications
      const token = localStorage.getItem('sessionToken') || localStorage.getItem('access_token');
      if (token) {
        loadNotifications();
        const interval = setInterval(loadNotifications, 60000);
        return () => clearInterval(interval);
      }
    }
  }, [variant, isAuthenticated]);

  const loadNotifications = async () => {
    try {
      let gapItems = [];
      try {
        const gapsResp = await apiClient.get('/api/procurement/integration/gaps');
        gapItems = (gapsResp?.gaps || []).map(g => ({
          id: `gap-${g.po_number}-${g.item_id}`,
          type: 'integration_gap',
          message: `PO ${g.po_number} · Item ${g.item_id} missing product mapping`,
          href: '/inventory'
        }));
      } catch (e) {
        // Silently ignore gaps errors - might be permission issue or endpoint not available
        console.debug('Could not load integration gaps:', e.message);
      }
      
      let ticketItems = [];
      try {
        const ticketsResp = await apiClient.get('/api/crm/tickets');
        const now = new Date();
        ticketItems = (ticketsResp || []).filter(t => {
          const isOpen = !['resolved', 'closed'].includes((t.status || '').toLowerCase());
          const breachedFlag = (t.sla_status || '').toLowerCase() === 'breached';
          const overdue = t.due_at ? (new Date(t.due_at) < now) : false;
          return isOpen && (breachedFlag || overdue);
        }).map(t => ({
          id: `ticket-${t.id}`,
          type: 'ticket_sla',
          message: `Ticket #${t.id || ''} ${t.subject ? '· ' + t.subject : ''} SLA at risk/overdue`,
          href: '/crm'
        }));
      } catch (e) {
        // Silently ignore ticket errors
        console.debug('Could not load tickets:', e.message);
      }
      
      setNotifications([...gapItems, ...ticketItems]);
    } catch (e) {
      // Silently ignore all notification errors - don't break the app
      console.debug('Error loading notifications:', e.message);
    }
  };

  const getIconForType = (type) => {
    switch (type) {
      case 'integration_gap':
        return <ReportProblemIcon fontSize="small" color="warning" />;
      case 'ticket_sla':
        return <WarningAmberIcon fontSize="small" color="error" />;
      case 'csv_import':
        return <MailOutlineIcon fontSize="small" color="info" />;
      case 'kb_attachment':
        return <AttachmentIcon fontSize="small" color="primary" />;
      default:
        return <NotificationsIcon fontSize="small" />;
    }
  };

  const persistReadIds = (ids) => {
    try { localStorage.setItem('edonuops.notifications.readIds', JSON.stringify(Array.from(ids))); } catch {}
  };

  const markRead = (id) => {
    setReadIds(prev => {
      const next = new Set(prev);
      next.add(id);
      persistReadIds(next);
      return next;
    });
  };

  const markAllRead = () => {
    setReadIds(prev => {
      const next = new Set(prev);
      notifications.forEach(n => next.add(n.id));
      persistReadIds(next);
      return next;
    });
  };

  const unreadCount = notifications.filter(n => !readIds.has(n.id)).length;

  const handleStartTrial = () => {
    if (isAuthenticated) {
      navigate('/dashboard');
    } else {
      navigate('/register');
    }
    setMobileMenuOpen(false);
  };

  const handleModuleClick = (moduleId) => {
    if (onModuleClick) {
      onModuleClick(moduleId);
    }
    setMobileMenuOpen(false);
  };

  const handleNavigation = (path) => {
    navigate(path);
    setMobileMenuOpen(false);
  };

  // Public variant menu items - defined after handlers
  const publicMenuItems = [
    { label: 'Financials', action: () => handleModuleClick('financials') },
    { label: 'Inventory', action: () => handleModuleClick('inventory') },
    { label: 'CRM', action: () => handleModuleClick('crm') },
    { label: 'Login', action: () => handleNavigation('/login') },
    { label: 'Sign Up', action: () => handleNavigation('/register'), variant: 'outlined' },
    { label: 'Start Free Trial', action: handleStartTrial, variant: 'contained' }
  ];

  const handleUserMenuOpen = (event) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  const openNotifications = (e) => setNotificationsAnchor(e.currentTarget);
  const closeNotifications = () => setNotificationsAnchor(null);

  const handleLogout = () => {
    authLogout();
    localStorage.removeItem('currentTenant');
    localStorage.removeItem('user_logged_in');
    localStorage.removeItem('edonuops_visitor_id');
    localStorage.removeItem('edonuops_session_id');
    localStorage.removeItem('edonuops_session_expiry');
    handleUserMenuClose();
    window.location.href = '/login';
  };

  // Determine AppBar styling based on variant
  const appBarSx = variant === 'public' 
    ? { 
        bgcolor: 'rgba(255,255,255,0.98)', 
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
        boxShadow: '0 1px 2px rgba(0,0,0,0.04)'
      }
    : { 
        backgroundColor: '#ffffff',
        color: '#1a1a1a',
        borderBottom: '1px solid rgba(0, 0, 0, 0.08)',
        boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
        zIndex: zIndex || (isMobile ? theme.zIndex.appBar : (theme.zIndex.drawer + 1))
      };

  // Render authenticated variant content
  const renderAuthenticatedContent = () => (
    <>
      <Typography 
        variant="h6" 
        component="div" 
        sx={{ 
          flexGrow: 1, 
          fontWeight: 500,
          color: '#1a1a1a',
          fontSize: '1.25rem',
          letterSpacing: '0.01em'
        }}
      >
        EdonuOps Enterprise
      </Typography>

      {!isMobile ? (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <TenantSwitcher />
          <IconButton color="inherit" onClick={openNotifications} title="Notifications">
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
          <IconButton color="inherit" onClick={handleUserMenuOpen}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
              <PersonIcon />
            </Avatar>
          </IconButton>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton 
            onClick={() => {
              if (setSidebarOpen) {
                setSidebarOpen(!sidebarOpen);
              } else {
                setMobileMenuOpen(true);
              }
            }}
            sx={{ color: '#202124' }}
            title="Toggle menu"
          >
            <MenuIcon />
          </IconButton>
          <IconButton color="inherit" onClick={openNotifications} title="Notifications" size="small">
            <Badge badgeContent={unreadCount} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
          <IconButton color="inherit" onClick={handleUserMenuOpen} size="small">
            <Avatar sx={{ width: 28, height: 28, bgcolor: 'primary.main' }}>
              <PersonIcon />
            </Avatar>
          </IconButton>
        </Box>
      )}
    </>
  );

  // Render public variant content
  const renderPublicContent = () => (
    <>
      <Typography 
        variant="h6" 
        component="div" 
        sx={{ flexGrow: 1, fontWeight: 'bold', color: 'primary.main' }}
      >
        EdonuOps
      </Typography>
      
      {!isMobile ? (
        <Box sx={{ display: 'flex', gap: 2 }}>
          {publicMenuItems.map((item, index) => (
            <Button
              key={index}
              color="inherit"
              variant={item.variant || 'text'}
              onClick={item.action}
              sx={item.variant === 'outlined' ? {
                color: 'primary.main',
                borderColor: 'primary.main'
              } : {}}
            >
              {item.label}
            </Button>
          ))}
        </Box>
      ) : (
        <IconButton 
          onClick={() => setMobileMenuOpen(true)}
          sx={{ color: 'primary.main' }}
        >
          <MenuIcon />
        </IconButton>
      )}
    </>
  );

  return (
    <>
      <AppBar 
        position="fixed" 
        color="transparent" 
        elevation={0} 
        sx={appBarSx}
      >
        <Toolbar sx={{ minHeight: 64, px: { xs: 2, md: 3 } }}>
          {variant === 'authenticated' ? renderAuthenticatedContent() : renderPublicContent()}
        </Toolbar>
      </AppBar>

      {/* Mobile Menu Drawer - Public Variant */}
      {variant === 'public' && (
        <Drawer
          anchor="right"
          open={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
          sx={{
            '& .MuiDrawer-paper': {
              width: 280,
              pt: 2
            }
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 2, pb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
              Menu
            </Typography>
            <IconButton onClick={() => setMobileMenuOpen(false)}>
              <Close />
            </IconButton>
          </Box>
          
          <List>
            {publicMenuItems.map((item, index) => (
              <ListItem 
                key={index}
                button
                onClick={item.action}
                sx={{
                  py: 1.5,
                  px: 2,
                  '&:hover': {
                    bgcolor: 'action.hover'
                  }
                }}
              >
                <ListItemText 
                  primary={item.label}
                  primaryTypographyProps={{
                    fontWeight: item.variant === 'contained' ? 600 : 400,
                    color: item.variant === 'contained' ? 'primary.main' : 'text.primary'
                  }}
                />
              </ListItem>
            ))}
          </List>
        </Drawer>
      )}

      {/* Mobile Menu Drawer - Authenticated Variant */}
      {variant === 'authenticated' && isMobile && (
        <Drawer
          anchor="right"
          open={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
          sx={{
            '& .MuiDrawer-paper': {
              width: 280,
              pt: 2
            }
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', px: 2, pb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
              Menu
            </Typography>
            <IconButton onClick={() => setMobileMenuOpen(false)}>
              <Close />
            </IconButton>
          </Box>
          
          <List>
            <ListItem button onClick={() => { setMobileMenuOpen(false); openNotifications({ currentTarget: document.body }); }}>
              <ListItemIcon>
                <Badge badgeContent={unreadCount} color="error">
                  <NotificationsIcon />
                </Badge>
              </ListItemIcon>
              <ListItemText primary="Notifications" />
            </ListItem>
            <Divider />
            <ListItem button onClick={() => { setMobileMenuOpen(false); navigate('/profile'); }}>
              <ListItemIcon><PersonIcon /></ListItemIcon>
              <ListItemText primary="Profile" />
            </ListItem>
            <ListItem button onClick={() => { setMobileMenuOpen(false); navigate('/dashboard/settings'); }}>
              <ListItemIcon><SettingsIcon /></ListItemIcon>
              <ListItemText primary="Dashboard Settings" />
            </ListItem>
            <ListItem button onClick={() => { setMobileMenuOpen(false); navigate('/admin/settings'); }}>
              <ListItemIcon><AdminPanelSettingsIcon /></ListItemIcon>
              <ListItemText primary="Administrative Settings" />
            </ListItem>
            <Divider />
            <ListItem button onClick={handleLogout}>
              <ListItemIcon><LogoutIcon /></ListItemIcon>
              <ListItemText primary="Logout" />
            </ListItem>
          </List>
        </Drawer>
      )}

      {/* User Menu Dropdown - Authenticated Variant */}
      {variant === 'authenticated' && (
        <Menu
          anchorEl={userMenuAnchor}
          open={Boolean(userMenuAnchor)}
          onClose={handleUserMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem onClick={() => {
            handleUserMenuClose();
            navigate('/profile');
          }}>
            <ListItemIcon>
              <PersonIcon fontSize="small" />
            </ListItemIcon>
            Profile
          </MenuItem>
          <MenuItem onClick={() => {
            handleUserMenuClose();
            navigate('/dashboard/settings');
          }}>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            Dashboard Settings
          </MenuItem>
          <MenuItem onClick={() => {
            handleUserMenuClose();
            navigate('/admin/settings');
          }}>
            <ListItemIcon>
              <AdminPanelSettingsIcon fontSize="small" />
            </ListItemIcon>
            Administrative Settings
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleLogout}>
            <ListItemIcon>
              <LogoutIcon fontSize="small" />
            </ListItemIcon>
            Logout
          </MenuItem>
        </Menu>
      )}

      {/* Notifications Menu - Authenticated Variant */}
      {variant === 'authenticated' && (
        <Menu
          anchorEl={notificationsAnchor}
          open={Boolean(notificationsAnchor)}
          onClose={closeNotifications}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          transformOrigin={{ vertical: 'top', horizontal: 'right' }}
        >
          <MenuItem onClick={() => { closeNotifications(); navigate('/notifications'); }} sx={{ fontWeight: 600 }}>
            View all
          </MenuItem>
          {notifications.length > 0 && <MenuItem onClick={markAllRead} disabled={unreadCount === 0}>Mark all as read</MenuItem>}
          {notifications.length > 0 && <Divider />}
          {notifications.length === 0 && (
            <MenuItem disabled>No notifications</MenuItem>
          )}
          {notifications.map((n) => (
            <MenuItem
              key={n.id}
              onClick={() => { markRead(n.id); closeNotifications(); navigate(n.href); }}
              sx={{ opacity: readIds.has(n.id) ? 0.6 : 1 }}
            >
              <ListItemIcon>
                {getIconForType(n.type)}
              </ListItemIcon>
              <ListItemText
                primary={n.message}
                secondary={n.type === 'integration_gap' ? 'Action needed' : (readIds.has(n.id) ? 'Read' : undefined)}
              />
            </MenuItem>
          ))}
        </Menu>
      )}
    </>
  );
};

export default TopNav;
