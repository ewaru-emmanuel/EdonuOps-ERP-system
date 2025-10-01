import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Button, IconButton, Fab, SwipeableDrawer,
  List, ListItem, ListItemText, ListItemIcon, ListItemSecondaryAction, Chip,
  Dialog, DialogTitle, DialogContent, DialogActions, Alert, LinearProgress,
  Grid, Avatar, Badge, Divider, Accordion, AccordionSummary, AccordionDetails,
  BottomNavigation, BottomNavigationAction, Paper, Tabs, Tab
} from '@mui/material';
import {
  AccountBalance, Sync, CompareArrows, CheckCircle, Warning, Error, Info,
  Add, Refresh, Settings, Notifications, TrendingUp, TrendingDown, Schedule,
  AttachMoney, Description, Receipt, ExpandMore, Close, Menu, Home, Assessment
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const MobileReconciliation = ({ isMobile = true }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [quickActions, setQuickActions] = useState([]);

  // Data hooks
  const { data: reconciliationSessions, loading: sessionsLoading, refresh: refreshSessions } = useRealTimeData('/api/finance/reconciliation-sessions');
  const { data: bankAccounts, loading: accountsLoading } = useRealTimeData('/api/finance/bank-accounts');
  const { data: notifications, loading: notificationsLoading } = useRealTimeData('/api/finance/reconciliation-notifications');

  useEffect(() => {
    if (isMobile) {
      loadQuickActions();
    }
  }, [isMobile]);

  const loadQuickActions = async () => {
    try {
      const response = await apiClient.get('/api/finance/quick-actions');
      setQuickActions(response.data.actions || []);
    } catch (err) {
      setError(err.message || 'Failed to load quick actions');
    }
  };

  const handleStartReconciliation = async (bankAccountId) => {
    try {
      setLoading(true);
      await apiClient.post('/api/finance/reconciliation-sessions', {
        bank_account_id: bankAccountId,
        statement_date: new Date().toISOString().split('T')[0],
        statement_balance: 0
      });
      await refreshSessions();
    } catch (err) {
      setError(err.message || 'Failed to start reconciliation');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = async (action) => {
    try {
      setLoading(true);
      await apiClient.post(`/api/finance/quick-actions/${action.id}/execute`);
      await refreshSessions();
    } catch (err) {
      setError(err.message || 'Failed to execute quick action');
    } finally {
      setLoading(false);
    }
  };

  const renderDashboard = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Reconciliation Dashboard
      </Typography>
      
      {/* Quick Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" color="primary">
                {reconciliationSessions?.filter(s => s.status === 'completed').length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Completed
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6}>
          <Card>
            <CardContent sx={{ textAlign: 'center', py: 2 }}>
              <Typography variant="h4" color="warning.main">
                {reconciliationSessions?.filter(s => s.status === 'pending').length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Pending
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Typography variant="h6" gutterBottom>
        Quick Actions
      </Typography>
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {quickActions.map((action) => (
          <Grid item xs={6} key={action.id}>
            <Card 
              sx={{ cursor: 'pointer' }}
              onClick={() => handleQuickAction(action)}
            >
              <CardContent sx={{ textAlign: 'center', py: 2 }}>
                <Avatar sx={{ bgcolor: action.color, mx: 'auto', mb: 1 }}>
                  {action.icon}
                </Avatar>
                <Typography variant="body2" fontWeight="medium">
                  {action.title}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Recent Sessions */}
      <Typography variant="h6" gutterBottom>
        Recent Sessions
      </Typography>
      <List>
        {reconciliationSessions?.slice(0, 5).map((session) => (
          <ListItem 
            key={session.id}
            button
            onClick={() => {
              setSelectedSession(session);
              setDetailDialogOpen(true);
            }}
          >
            <ListItemIcon>
              <AccountBalance />
            </ListItemIcon>
            <ListItemText
              primary={session.bank_account_name}
              secondary={`${session.statement_date} • ${session.status}`}
            />
            <ListItemSecondaryAction>
              <Chip 
                label={session.status} 
                size="small"
                color={session.status === 'completed' ? 'success' : 'warning'}
              />
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  const renderSessions = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Reconciliation Sessions
      </Typography>
      
      {reconciliationSessions?.map((session) => (
        <Card key={session.id} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2} mb={2}>
              <Avatar sx={{ bgcolor: 'primary.main' }}>
                <AccountBalance />
              </Avatar>
              <Box flex={1}>
                <Typography variant="h6">{session.bank_account_name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {session.statement_date}
                </Typography>
              </Box>
              <Chip 
                label={session.status} 
                size="small"
                color={session.status === 'completed' ? 'success' : 'warning'}
              />
            </Box>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Statement Balance
                </Typography>
                <Typography variant="h6">
                  ${(session.statement_balance || 0).toLocaleString()}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Difference
                </Typography>
                <Typography 
                  variant="h6" 
                  color={session.difference === 0 ? 'success.main' : 'error.main'}
                >
                  ${(session.difference || 0).toLocaleString()}
                </Typography>
              </Grid>
            </Grid>
            
            <Box mt={2} display="flex" gap={1}>
              <Button 
                size="small" 
                variant="outlined"
                onClick={() => {
                  setSelectedSession(session);
                  setDetailDialogOpen(true);
                }}
              >
                View Details
              </Button>
              {session.status === 'pending' && (
                <Button 
                  size="small" 
                  variant="contained"
                  onClick={() => handleStartReconciliation(session.bank_account_id)}
                >
                  Continue
                </Button>
              )}
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );

  const renderNotifications = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Notifications
      </Typography>
      
      {notifications?.map((notification) => (
        <Card key={notification.id} sx={{ mb: 2 }}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <Avatar sx={{ bgcolor: notification.color }}>
                {notification.icon}
              </Avatar>
              <Box flex={1}>
                <Typography variant="h6">{notification.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {notification.message}
                </Typography>
              </Box>
              <Chip 
                label={notification.type} 
                size="small"
                color={notification.severity}
              />
            </Box>
          </CardContent>
        </Card>
      ))}
    </Box>
  );

  const renderSessionDetail = () => {
    if (!selectedSession) return null;

    return (
      <Dialog 
        open={detailDialogOpen} 
        onClose={() => setDetailDialogOpen(false)}
        fullScreen={isMobile}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={2}>
            <AccountBalance />
            <Typography variant="h6">{selectedSession.bank_account_name}</Typography>
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Statement Balance
              </Typography>
              <Typography variant="h6">
                ${(selectedSession.statement_balance || 0).toLocaleString()}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Book Balance
              </Typography>
              <Typography variant="h6">
                ${(selectedSession.book_balance || 0).toLocaleString()}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Difference
              </Typography>
              <Typography 
                variant="h6" 
                color={selectedSession.difference === 0 ? 'success.main' : 'error.main'}
              >
                ${(selectedSession.difference || 0).toLocaleString()}
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6}>
              <Typography variant="subtitle2" color="text.secondary">
                Status
              </Typography>
              <Chip 
                label={selectedSession.status} 
                color={selectedSession.status === 'completed' ? 'success' : 'warning'}
              />
            </Grid>
          </Grid>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
          {selectedSession.status === 'pending' && (
            <Button 
              variant="contained"
              onClick={() => handleStartReconciliation(selectedSession.bank_account_id)}
            >
              Continue Reconciliation
            </Button>
          )}
        </DialogActions>
      </Dialog>
    );
  };

  const renderBottomNavigation = () => (
    <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1000 }}>
      <BottomNavigation
        value={activeTab}
        onChange={(event, newValue) => setActiveTab(newValue)}
        showLabels
      >
        <BottomNavigationAction 
          label="Dashboard" 
          icon={<Home />} 
        />
        <BottomNavigationAction 
          label="Sessions" 
          icon={<AccountBalance />} 
        />
        <BottomNavigationAction 
          label="Notifications" 
          icon={<Notifications />} 
        />
        <BottomNavigationAction 
          label="Reports" 
          icon={<Assessment />} 
        />
      </BottomNavigation>
    </Paper>
  );

  const renderFloatingActionButton = () => (
    <Fab
      color="primary"
      sx={{
        position: 'fixed',
        bottom: 80,
        right: 16,
        zIndex: 1000
      }}
      onClick={() => setDrawerOpen(true)}
    >
      <Add />
    </Fab>
  );

  const renderDrawer = () => (
    <SwipeableDrawer
      anchor="bottom"
      open={drawerOpen}
      onClose={() => setDrawerOpen(false)}
      onOpen={() => setDrawerOpen(true)}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        
        <List>
          <ListItem button onClick={() => {
            setDrawerOpen(false);
            // Handle start reconciliation
          }}>
            <ListItemIcon>
              <AccountBalance />
            </ListItemIcon>
            <ListItemText primary="Start New Reconciliation" />
          </ListItem>
          
          <ListItem button onClick={() => {
            setDrawerOpen(false);
            // Handle sync accounts
          }}>
            <ListItemIcon>
              <Sync />
            </ListItemIcon>
            <ListItemText primary="Sync Bank Accounts" />
          </ListItem>
          
          <ListItem button onClick={() => {
            setDrawerOpen(false);
            // Handle auto match
          }}>
            <ListItemIcon>
              <CompareArrows />
            </ListItemIcon>
            <ListItemText primary="Auto Match Transactions" />
          </ListItem>
        </List>
      </Box>
    </SwipeableDrawer>
  );

  return (
    <Box sx={{ pb: 7 }}> {/* Add padding for bottom navigation */}
      {loading && <LinearProgress />}
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Main Content */}
      {activeTab === 0 && renderDashboard()}
      {activeTab === 1 && renderSessions()}
      {activeTab === 2 && renderNotifications()}
      {activeTab === 3 && (
        <Box>
          <Typography variant="h6" gutterBottom>
            Reports
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Reports will be available here
          </Typography>
        </Box>
      )}

      {/* Floating Action Button */}
      {renderFloatingActionButton()}

      {/* Bottom Navigation */}
      {renderBottomNavigation()}

      {/* Drawer */}
      {renderDrawer()}

      {/* Session Detail Dialog */}
      {renderSessionDetail()}
    </Box>
  );
};

export default MobileReconciliation;












