import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Box,
  CssBaseline,
  useTheme,
  useMediaQuery,
  Fade,
  Slide
} from '@mui/material';
import RefinedNavigation from './RefinedNavigation';
import SimplifiedTopBar from './SimplifiedTopBar';
import { useUserPreferences } from '../hooks/useUserPreferences';
import apiClient from '../services/apiClient';

const RefinedLayout = ({ children, user, onLogout }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();
  
  const [sidebarOpen, setSidebarOpen] = useState(!isMobile);
  const [notifications, setNotifications] = useState([]);
  const [readIds, setReadIds] = useState(new Set());
  
  const { selectedModules } = useUserPreferences();

  // Handle sidebar toggle
  const handleSidebarToggle = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Load notifications
  const loadNotifications = async () => {
    try {
      const gapsResp = await apiClient.get('/api/procurement/integration/gaps');
      const gapItems = (gapsResp?.gaps || []).map(g => ({
        id: `gap-${g.po_number}-${g.item_id}`,
        type: 'integration_gap',
        message: `PO ${g.po_number} · Item ${g.item_id} missing product mapping`,
        href: '/inventory'
      }));

      // CRM ticket SLA alerts
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
      } catch (_) {
        // ignore ticket errors to avoid blocking other alerts
      }

      setNotifications([...gapItems, ...ticketItems]);
    } catch (e) {
      // ignore
    }
  };

  // Load read notification IDs from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem('edonuops.notifications.readIds');
      if (stored) {
        setReadIds(new Set(JSON.parse(stored)));
      }
    } catch (e) {
      // ignore
    }
  }, []);

  // Load notifications on mount and set up polling
  useEffect(() => {
    loadNotifications();
    const interval = setInterval(loadNotifications, 60000);
    return () => clearInterval(interval);
  }, []);

  // Handle notification click
  const handleNotificationClick = (notification) => {
    // Mark as read
    setReadIds(prev => {
      const next = new Set(prev);
      next.add(notification.id);
      try {
        localStorage.setItem('edonuops.notifications.readIds', JSON.stringify(Array.from(next)));
      } catch (e) {
        // ignore
      }
      return next;
    });

    // Navigate if href is provided
    if (notification.href) {
      window.location.href = notification.href;
    }
  };

  // Calculate unread count
  const unreadCount = notifications.filter(n => !readIds.has(n.id)).length;

  // Auto-close sidebar on mobile when route changes
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  }, [location.pathname, isMobile]);

  // Adjust sidebar state based on screen size
  useEffect(() => {
    if (isMobile) {
      setSidebarOpen(false);
    } else {
      setSidebarOpen(true);
    }
  }, [isMobile]);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <CssBaseline />
      
      {/* Navigation Sidebar */}
      <RefinedNavigation
        open={sidebarOpen}
        onToggle={handleSidebarToggle}
        notifications={notifications}
        unreadCount={unreadCount}
        selectedModules={selectedModules}
        onNotificationClick={handleNotificationClick}
      />

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          marginLeft: sidebarOpen ? 0 : '-280px',
          width: '100%'
        }}
      >
        {/* Top Bar */}
        <SimplifiedTopBar
          onMenuToggle={handleSidebarToggle}
          sidebarOpen={sidebarOpen}
          notifications={notifications}
          unreadCount={unreadCount}
          user={user}
          onLogout={onLogout}
          onNotificationClick={handleNotificationClick}
        />

        {/* Page Content */}
        <Box
          sx={{
            flexGrow: 1,
            p: 3,
            pt: 10, // Account for top bar
            backgroundColor: 'background.default',
            minHeight: 'calc(100vh - 64px)',
            overflow: 'auto'
          }}
        >
          <Fade in timeout={300}>
            <Box>
              {children}
            </Box>
          </Fade>
        </Box>
      </Box>
    </Box>
  );
};

export default RefinedLayout;




