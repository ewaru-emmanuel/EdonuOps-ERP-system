import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions, Button, Box, Typography,
  Card, CardContent, Grid, Chip, IconButton, Tooltip, Alert, LinearProgress,
  List, ListItem, ListItemText, ListItemIcon, ListItemSecondaryAction, Divider,
  FormControl, InputLabel, Select, MenuItem, TextField, Switch, FormControlLabel,
  Accordion, AccordionSummary, AccordionDetails, Table, TableBody, TableCell, TableHead, TableRow
} from '@mui/material';
import {
  AccountBalance, Link, LinkOff, Sync, CheckCircle, Warning, Error, Info,
  ExpandMore, CloudSync, Security, Schedule, TrendingUp, TrendingDown,
  Refresh, Download, Upload, Settings, Visibility, VisibilityOff
} from '@mui/icons-material';
import { useRealTimeData } from '../../../hooks/useRealTimeData';
import apiClient from '../../../services/apiClient';

const BankFeedIntegration = ({ open, onClose, bankAccountId, onConnectionUpdate }) => {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [syncHistory, setSyncHistory] = useState([]);
  const [accountInfo, setAccountInfo] = useState(null);
  const [linkToken, setLinkToken] = useState(null);
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');

  // Data hooks
  const { data: bankAccounts, loading: bankAccountsLoading, refresh: refreshBankAccounts } = useRealTimeData('/api/finance/bank-accounts');

  useEffect(() => {
    if (open) {
      loadProviders();
      loadConnectionStatus();
    }
  }, [open, bankAccountId]);

  const loadProviders = async () => {
    try {
      const response = await apiClient.get('/api/finance/bank-feed/providers');
      setProviders(response.data.providers || []);
    } catch (err) {
      setError(err.message || 'Failed to load providers');
    }
  };

  const loadConnectionStatus = async () => {
    if (!bankAccountId) return;
    
    try {
      const bankAccount = bankAccounts?.find(acc => acc.id === bankAccountId);
      if (bankAccount?.provider) {
        setConnectionStatus('connected');
        setSelectedProvider(bankAccount.provider);
        setAccountInfo({
          provider: bankAccount.provider,
          connected_at: bankAccount.connected_at,
          last_sync: bankAccount.last_sync_at,
          sync_frequency: bankAccount.sync_frequency
        });
      } else {
        setConnectionStatus('disconnected');
      }
    } catch (err) {
      setError(err.message || 'Failed to load connection status');
    }
  };

  const handleProviderSelect = async (provider) => {
    setSelectedProvider(provider);
    setError(null);

    if (provider === 'plaid') {
      try {
        setLoading(true);
        const response = await apiClient.post('/api/finance/bank-feed/plaid/link-token');
        setLinkToken(response.data.link_token);
      } catch (err) {
        setError(err.message || 'Failed to create link token');
      } finally {
        setLoading(false);
      }
    }
  };

  const handlePlaidConnection = async (publicToken) => {
    try {
      setLoading(true);
      
      // Exchange public token for access token
      const tokenResponse = await apiClient.post('/api/finance/bank-feed/plaid/exchange-token', {
        public_token: publicToken
      });
      
      const accessToken = tokenResponse.data.access_token;
      
      // Get accounts
      const accountsResponse = await apiClient.post('/api/finance/bank-feed/plaid/accounts', {
        access_token: accessToken
      });
      
      setAccounts(accountsResponse.data.accounts || []);
      
    } catch (err) {
      setError(err.message || 'Failed to connect to Plaid');
    } finally {
      setLoading(false);
    }
  };

  const handleAccountSelect = async (externalAccountId) => {
    try {
      setLoading(true);
      
      await apiClient.post('/api/finance/bank-feed/connect-account', {
        bank_account_id: bankAccountId,
        provider: selectedProvider,
        access_token: linkToken, // This should be the access token
        external_account_id: externalAccountId
      });
      
      setConnectionStatus('connected');
      onConnectionUpdate?.();
      refreshBankAccounts?.();
      
    } catch (err) {
      setError(err.message || 'Failed to connect account');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      setLoading(true);
      
      const response = await apiClient.post('/api/finance/bank-feed/sync-transactions', {
        bank_account_id: bankAccountId,
        start_date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0]
      });
      
      setSyncHistory(prev => [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        transactions_created: response.data.transactions_created,
        total_transactions: response.data.total_transactions,
        status: 'success'
      }, ...prev]);
      
    } catch (err) {
      setError(err.message || 'Sync failed');
      setSyncHistory(prev => [{
        id: Date.now(),
        timestamp: new Date().toISOString(),
        status: 'error',
        error: err.message
      }, ...prev]);
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      setLoading(true);
      
      await apiClient.post('/api/finance/bank-feed/disconnect-account', {
        bank_account_id: bankAccountId
      });
      
      setConnectionStatus('disconnected');
      setAccountInfo(null);
      onConnectionUpdate?.();
      refreshBankAccounts?.();
      
    } catch (err) {
      setError(err.message || 'Failed to disconnect account');
    } finally {
      setLoading(false);
    }
  };

  const getProviderIcon = (provider) => {
    switch (provider) {
      case 'plaid': return <AccountBalance />;
      case 'yodlee': return <CloudSync />;
      case 'manual': return <Upload />;
      default: return <AccountBalance />;
    }
  };

  const getProviderColor = (provider) => {
    switch (provider) {
      case 'plaid': return 'primary';
      case 'yodlee': return 'secondary';
      case 'manual': return 'default';
      default: return 'default';
    }
  };

  const renderProviderSelection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Select Bank Feed Provider
      </Typography>
      <Grid container spacing={2}>
        {providers.map((provider) => (
          <Grid item xs={12} md={4} key={provider.id}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                border: selectedProvider === provider.id ? 2 : 1,
                borderColor: selectedProvider === provider.id ? 'primary.main' : 'divider'
              }}
              onClick={() => handleProviderSelect(provider.id)}
            >
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  {getProviderIcon(provider.id)}
                  <Typography variant="h6">{provider.name}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" mb={2}>
                  {provider.description}
                </Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {provider.features.map((feature) => (
                    <Chip 
                      key={feature} 
                      label={feature} 
                      size="small" 
                      variant="outlined"
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );

  const renderPlaidConnection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Connect to Plaid
      </Typography>
      <Alert severity="info" sx={{ mb: 2 }}>
        Click the button below to securely connect your bank account through Plaid.
        You'll be redirected to your bank's login page.
      </Alert>
      
      <Button 
        variant="contained" 
        size="large"
        onClick={() => {
          // In a real implementation, this would open Plaid Link
          // For now, we'll simulate the connection
          handlePlaidConnection('mock-public-token');
        }}
        disabled={loading}
        startIcon={<Link />}
        fullWidth
      >
        Connect Bank Account
      </Button>
    </Box>
  );

  const renderAccountSelection = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Select Account to Connect
      </Typography>
      <List>
        {accounts.map((account) => (
          <ListItem 
            key={account.account_id}
            button
            onClick={() => handleAccountSelect(account.account_id)}
          >
            <ListItemIcon>
              <AccountBalance />
            </ListItemIcon>
            <ListItemText
              primary={account.name}
              secondary={`${account.type} • ${account.subtype} • ${account.mask}`}
            />
            <ListItemSecondaryAction>
              <Button 
                size="small"
                onClick={() => handleAccountSelect(account.account_id)}
                disabled={loading}
              >
                Connect
              </Button>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  const renderConnectionStatus = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Connection Status
      </Typography>
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            {getProviderIcon(accountInfo.provider)}
            <Typography variant="h6">{accountInfo.provider.toUpperCase()}</Typography>
            <Chip 
              label="Connected" 
              color="success" 
              icon={<CheckCircle />}
            />
          </Box>
          
          <List dense>
            <ListItem>
              <ListItemText 
                primary="Connected At" 
                secondary={new Date(accountInfo.connected_at).toLocaleString()} 
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Last Sync" 
                secondary={accountInfo.last_sync ? new Date(accountInfo.last_sync).toLocaleString() : 'Never'} 
              />
            </ListItem>
            <ListItem>
              <ListItemText 
                primary="Sync Frequency" 
                secondary={accountInfo.sync_frequency} 
              />
            </ListItem>
          </List>
          
          <Box mt={2} display="flex" gap={2}>
            <Button 
              variant="outlined" 
              startIcon={<Sync />}
              onClick={handleSync}
              disabled={loading}
            >
              Sync Now
            </Button>
            <Button 
              variant="outlined" 
              color="error"
              startIcon={<LinkOff />}
              onClick={handleDisconnect}
              disabled={loading}
            >
              Disconnect
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );

  const renderSyncHistory = () => (
    <Accordion>
      <AccordionSummary expandIcon={<ExpandMore />}>
        <Typography variant="h6">Sync History</Typography>
      </AccordionSummary>
      <AccordionDetails>
        {syncHistory.length === 0 ? (
          <Typography color="text.secondary">No sync history available</Typography>
        ) : (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Timestamp</TableCell>
                <TableCell>Transactions</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {syncHistory.map((sync) => (
                <TableRow key={sync.id}>
                  <TableCell>{new Date(sync.timestamp).toLocaleString()}</TableCell>
                  <TableCell>
                    {sync.transactions_created || 0} / {sync.total_transactions || 0}
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={sync.status} 
                      size="small"
                      color={sync.status === 'success' ? 'success' : 'error'}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </AccordionDetails>
    </Accordion>
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={2}>
          <AccountBalance color="primary" />
          <Typography variant="h6">Bank Feed Integration</Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {connectionStatus === 'disconnected' && !selectedProvider && renderProviderSelection()}
        {connectionStatus === 'disconnected' && selectedProvider === 'plaid' && !accounts.length && renderPlaidConnection()}
        {connectionStatus === 'disconnected' && selectedProvider === 'plaid' && accounts.length > 0 && renderAccountSelection()}
        {connectionStatus === 'connected' && renderConnectionStatus()}
        
        {syncHistory.length > 0 && renderSyncHistory()}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        {connectionStatus === 'connected' && (
          <Button 
            variant="contained" 
            startIcon={<Sync />}
            onClick={handleSync}
            disabled={loading}
          >
            Sync Now
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default BankFeedIntegration;












