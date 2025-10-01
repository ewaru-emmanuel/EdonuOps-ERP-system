import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, List, ListItem, ListItemText,
  ListItemIcon, Chip, IconButton, Tooltip, Alert, LinearProgress,
  Button, Dialog, DialogTitle, DialogContent, DialogActions,
  Table, TableBody, TableCell, TableHead, TableRow, Paper,
  Accordion, AccordionSummary, AccordionDetails, Grid, Avatar
} from '@mui/material';
import {
  Notifications, CheckCircle, Warning, Error, Info, Schedule,
  TrendingUp, TrendingDown, Refresh, Settings, Close, ExpandMore,
  AccountBalance, Sync, CompareArrows, Assessment, Timeline
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const ReconciliationNotifications = ({ open, onClose }) => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  // Data hooks
  const { data: reconciliationSessions, loading: sessionsLoading, refresh: refreshSessions } = useRealTimeData('/api/finance/reconciliation-sessions');
  const { data: bankAccounts, loading: accountsLoading } = useRealTimeData('/api/finance/bank-accounts');

  useEffect(() => {
    if (open) {
      loadNotifications();
    }
  }, [open]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get reconciliation alerts
      const alertsResponse = await apiClient.get('/api/finance/reconciliation-alerts');
      const alerts = alertsResponse.data.alerts || [];

      // Get overdue reconciliations
      const overdueResponse = await apiClient.get('/api/finance/overdue-reconciliations');
      const overdue = overdueResponse.data.overdue || [];

      // Get pending reconciliations
      const pendingResponse = await apiClient.get('/api/finance/pending-reconciliations');
      const pending = pendingResponse.data.pending || [];

      // Combine all notifications
      const allNotifications = [
        ...alerts.map(alert => ({ ...alert, type: 'alert' })),
        ...overdue.map(item => ({ ...item, type: 'overdue' })),
        ...pending.map(item => ({ ...item, type: 'pending' }))
      ];

      setNotifications(allNotifications);
    } catch (err) {
      setError(err.message || 'Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationClick = (notification) => {
    setSelectedNotification(notification);
    setDetailDialogOpen(true);
  };

  const handleDismissNotification = async (notificationId) => {
    try {
      await apiClient.post(`/api/finance/notifications/${notificationId}/dismiss`);
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
    } catch (err) {
      setError(err.message || 'Failed to dismiss notification');
    }
  };

  const handleStartReconciliation = async (bankAccountId) => {
    try {
      // Start reconciliation process
      await apiClient.post('/api/finance/reconciliation-sessions', {
        bank_account_id: bankAccountId,
        statement_date: new Date().toISOString().split('T')[0],
        statement_balance: 0 // This would be fetched from bank
      });
      
      // Refresh data
      await refreshSessions();
      setDetailDialogOpen(false);
    } catch (err) {
      setError(err.message || 'Failed to start reconciliation');
    }
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'alert': return <Warning color="warning" />;
      case 'overdue': return <Error color="error" />;
      case 'pending': return <Info color="info" />;
      default: return <Notifications />;
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'alert': return 'warning';
      case 'overdue': return 'error';
      case 'pending': return 'info';
      default: return 'default';
    }
  };

  const getNotificationSeverity = (type) => {
    switch (type) {
      case 'alert': return 'warning';
      case 'overdue': return 'error';
      case 'pending': return 'info';
      default: return 'info';
    }
  };

  const renderNotificationList = () => (
    <List>
      {notifications.map((notification) => (
        <ListItem 
          key={notification.id}
          button
          onClick={() => handleNotificationClick(notification)}
        >
          <ListItemIcon>
            {getNotificationIcon(notification.type)}
          </ListItemIcon>
          <ListItemText
            primary={notification.title}
            secondary={notification.message}
          />
          <Box display="flex" alignItems="center" gap={1}>
            <Chip 
              label={notification.type} 
              size="small" 
              color={getNotificationColor(notification.type)}
            />
            <Tooltip title="Dismiss">
              <IconButton 
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDismissNotification(notification.id);
                }}
              >
                <Close />
              </IconButton>
            </Tooltip>
          </Box>
        </ListItem>
      ))}
    </List>
  );

  const renderNotificationDetail = () => {
    if (!selectedNotification) return null;

    return (
      <Dialog open={detailDialogOpen} onClose={() => setDetailDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            {getNotificationIcon(selectedNotification.type)}
            <Typography variant="h6">{selectedNotification.title}</Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Alert severity={getNotificationSeverity(selectedNotification.type)} sx={{ mb: 2 }}>
            {selectedNotification.message}
          </Alert>
          
          {selectedNotification.type === 'overdue' && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Overdue Reconciliation Details
              </Typography>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Bank Account</TableCell>
                    <TableCell>Last Reconciliation</TableCell>
                    <TableCell>Days Overdue</TableCell>
                    <TableCell>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {selectedNotification.accounts?.map((account) => (
                    <TableRow key={account.id}>
                      <TableCell>{account.account_name}</TableCell>
                      <TableCell>
                        {account.last_reconciliation ? 
                          new Date(account.last_reconciliation).toLocaleDateString() : 
                          'Never'
                        }
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={`${account.days_overdue} days`}
                          color={account.days_overdue > 30 ? 'error' : 'warning'}
                        />
                      </TableCell>
                      <TableCell>
                        <Button 
                          size="small"
                          variant="outlined"
                          onClick={() => handleStartReconciliation(account.id)}
                        >
                          Start Reconciliation
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          )}
          
          {selectedNotification.type === 'pending' && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Pending Reconciliation Details
              </Typography>
              <Grid container spacing={2}>
                {selectedNotification.sessions?.map((session) => (
                  <Grid item xs={12} md={6} key={session.id}>
                    <Card>
                      <CardContent>
                        <Box display="flex" alignItems="center" gap={2} mb={2}>
                          <AccountBalance />
                          <Typography variant="h6">{session.bank_account_name}</Typography>
                        </Box>
                        <List dense>
                          <ListItem>
                            <ListItemText 
                              primary="Statement Date" 
                              secondary={session.statement_date} 
                            />
                          </ListItem>
                          <ListItem>
                            <ListItemText 
                              primary="Status" 
                              secondary={
                                <Chip 
                                  label={session.status} 
                                  size="small" 
                                  color={session.status === 'completed' ? 'success' : 'warning'}
                                />
                              } 
                            />
                          </ListItem>
                          <ListItem>
                            <ListItemText 
                              primary="Difference" 
                              secondary={`$${session.difference?.toLocaleString() || '0'}`} 
                            />
                          </ListItem>
                        </List>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
          {selectedNotification.type === 'overdue' && (
            <Button 
              variant="contained"
              onClick={() => {
                // Handle bulk reconciliation
                setDetailDialogOpen(false);
              }}
            >
              Start All Reconciliations
            </Button>
          )}
        </DialogActions>
      </Dialog>
    );
  };

  const renderSummary = () => {
    const alertCount = notifications.filter(n => n.type === 'alert').length;
    const overdueCount = notifications.filter(n => n.type === 'overdue').length;
    const pendingCount = notifications.filter(n => n.type === 'pending').length;

    return (
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <Warning />
                </Avatar>
                <Box>
                  <Typography variant="h4">{alertCount}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'error.main' }}>
                  <Error />
                </Avatar>
                <Box>
                  <Typography variant="h4">{overdueCount}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Overdue
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <Info />
                </Avatar>
                <Box>
                  <Typography variant="h4">{pendingCount}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Pending
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box>
      {loading && <LinearProgress sx={{ mb: 2 }} />}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {renderSummary()}
      
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Reconciliation Notifications</Typography>
            <Box display="flex" gap={1}>
              <Tooltip title="Refresh">
                <IconButton onClick={loadNotifications} disabled={loading}>
                  <Refresh />
                </IconButton>
              </Tooltip>
              <Tooltip title="Settings">
                <IconButton>
                  <Settings />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
          
          {notifications.length === 0 ? (
            <Box textAlign="center" py={4}>
              <Notifications sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                No Notifications
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All reconciliations are up to date
              </Typography>
            </Box>
          ) : (
            renderNotificationList()
          )}
        </CardContent>
      </Card>
      
      {renderNotificationDetail()}
    </Box>
  );
};

export default ReconciliationNotifications;












