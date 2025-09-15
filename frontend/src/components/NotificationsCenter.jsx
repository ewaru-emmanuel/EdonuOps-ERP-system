import React, { useEffect, useMemo, useState } from 'react';
import { Box, Typography, Paper, List, ListItemButton, ListItemIcon, ListItemText, Divider, Button, Chip } from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import ReportProblemIcon from '@mui/icons-material/ReportProblem';
import MailOutlineIcon from '@mui/icons-material/MailOutline';
import AttachmentIcon from '@mui/icons-material/Attachment';
import { useNavigate } from 'react-router-dom';
import apiClient from '../services/apiClient';

const NotificationsCenter = () => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState([]);
  const [readIds, setReadIds] = useState(() => {
    try {
      const raw = localStorage.getItem('edonuops.notifications.readIds');
      return new Set(raw ? JSON.parse(raw) : []);
    } catch {
      return new Set();
    }
  });

  const persistReadIds = (ids) => {
    try { localStorage.setItem('edonuops.notifications.readIds', JSON.stringify(Array.from(ids))); } catch {}
  };

  const getIconForType = (type) => {
    switch (type) {
      case 'integration_gap':
        return <ReportProblemIcon color="warning" />;
      case 'ticket_sla':
        return <WarningAmberIcon color="error" />;
      case 'csv_import':
        return <MailOutlineIcon color="info" />;
      case 'kb_attachment':
        return <AttachmentIcon color="primary" />;
      // Daily cycle notification types
      case 'daily_cycle_opening':
        return <NotificationsIcon color="info" />;
      case 'daily_cycle_closing':
        return <NotificationsIcon color="success" />;
      case 'daily_cycle_locked':
        return <WarningAmberIcon color="warning" />;
      case 'daily_cycle_unlocked':
        return <NotificationsIcon color="info" />;
      case 'daily_cycle_failed':
        return <ReportProblemIcon color="error" />;
      case 'adjustment_created':
        return <MailOutlineIcon color="info" />;
      case 'adjustment_applied':
        return <NotificationsIcon color="success" />;
      case 'adjustment_pending':
        return <WarningAmberIcon color="warning" />;
      case 'grace_period_expired':
        return <ReportProblemIcon color="warning" />;
      default:
        return <NotificationsIcon />;
    }
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

  const loadNotifications = async () => {
    const items = [];
    
    // Load existing notifications
    try {
      const gapsResp = await apiClient.get('/api/procurement/integration/gaps');
      (gapsResp?.gaps || []).forEach(g => items.push({
        id: `gap-${g.po_number}-${g.item_id}`,
        type: 'integration_gap',
        message: `PO ${g.po_number} · Item ${g.item_id} missing product mapping`,
        href: '/inventory'
      }));
    } catch {}
    
    try {
      const ticketsResp = await apiClient.get('/api/crm/tickets');
      const now = new Date();
      (ticketsResp || []).filter(t => {
        const isOpen = !['resolved', 'closed'].includes((t.status || '').toLowerCase());
        const breachedFlag = (t.sla_status || '').toLowerCase() === 'breached';
        const overdue = t.due_at ? (new Date(t.due_at) < now) : false;
        return isOpen && (breachedFlag || overdue);
      }).forEach(t => items.push({
        id: `ticket-${t.id}`,
        type: 'ticket_sla',
        message: `Ticket #${t.id || ''} ${t.subject ? '· ' + t.subject : ''} SLA at risk/overdue`,
        href: '/crm'
      }));
    } catch {}
    
    try {
      const importsResp = await apiClient.get('/api/crm/imports/errors');
      (importsResp?.errors || []).forEach((e, idx) => items.push({
        id: `import-${e.entity || 'crm'}-${idx}`,
        type: 'csv_import',
        message: `CSV import error${e.entity ? ' (' + e.entity + ')' : ''}: ${e.message || 'Check mapping/validation'}`,
        href: '/crm'
      }));
    } catch {}
    
    try {
      const kbResp = await apiClient.get('/api/crm/kb/attachments/flags');
      (kbResp?.flags || []).forEach(f => items.push({
        id: `kbflag-${f.id || f.filename}`,
        type: 'kb_attachment',
        message: `KB attachment flagged: ${f.filename || 'unknown'} (${f.reason || 'policy'})`,
        href: '/crm'
      }));
    } catch {}
    
    // Load daily cycle notifications (temporarily disabled until backend restart)
    const enableDailyCycleNotifications = false; // Set to true after backend restart
    
    if (enableDailyCycleNotifications) {
      try {
        const dailyCycleResp = await apiClient.get('/api/finance/daily-cycle/notifications/recent?hours_back=24&limit=20');
        if (dailyCycleResp?.success && dailyCycleResp.notifications) {
          dailyCycleResp.notifications.forEach(notification => {
            items.push({
              id: notification.id,
              type: notification.type,
              message: notification.message,
              href: notification.href || '/finance?feature=daily-cycle',
              severity: notification.severity,
              timestamp: notification.timestamp,
              action_required: notification.action_required || false
            });
          });
        }
      } catch (error) {
        console.error('Error loading daily cycle notifications:', error);
      }
      
      // Load critical daily cycle notifications
      try {
        const criticalResp = await apiClient.get('/api/finance/daily-cycle/notifications/critical');
        if (criticalResp?.success && criticalResp.critical_notifications) {
          criticalResp.critical_notifications.forEach(notification => {
            items.push({
              id: notification.id,
              type: notification.type,
              message: notification.message,
              href: notification.href || '/finance?feature=daily-cycle',
              severity: notification.severity,
              timestamp: notification.timestamp,
              action_required: notification.action_required || false
            });
          });
        }
      } catch (error) {
        console.error('Error loading critical daily cycle notifications:', error);
      }
    }
    
    setNotifications(items);
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const unreadCount = useMemo(() => notifications.filter(n => !readIds.has(n.id)).length, [notifications, readIds]);

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>Notifications</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip label={`${unreadCount} unread`} color={unreadCount ? 'error' : 'default'} variant={unreadCount ? 'filled' : 'outlined'} />
          <Button onClick={markAllRead} disabled={unreadCount === 0}>Mark all as read</Button>
        </Box>
      </Box>
      <Paper>
        <List>
          {notifications.length === 0 && (
            <ListItemButton disabled>
              <ListItemIcon><NotificationsIcon /></ListItemIcon>
              <ListItemText primary="You're all caught up" secondary="No notifications to show" />
            </ListItemButton>
          )}
          {notifications.map(n => (
            <React.Fragment key={n.id}>
              <ListItemButton onClick={() => { markRead(n.id); navigate(n.href); }} sx={{ opacity: readIds.has(n.id) ? 0.6 : 1 }}>
                <ListItemIcon>{getIconForType(n.type)}</ListItemIcon>
                <ListItemText primary={n.message} secondary={readIds.has(n.id) ? 'Read' : undefined} />
              </ListItemButton>
              <Divider component="li" />
            </React.Fragment>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default NotificationsCenter;



