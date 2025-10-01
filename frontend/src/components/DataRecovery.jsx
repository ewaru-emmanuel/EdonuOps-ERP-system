import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Divider,
  Grid,
  Paper
} from '@mui/material';
import {
  Backup as BackupIcon,
  Restore as RestoreIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';
import dataBackup from '../services/dataBackup';
import dataPersistence from '../services/dataPersistence';

const DataRecovery = () => {
  const { user } = useAuth();
  const [backups, setBackups] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  const [restoreDialog, setRestoreDialog] = useState(false);
  const [selectedBackup, setSelectedBackup] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (user) {
      loadBackups();
      loadStats();
    }
  }, [user]);

  const loadBackups = () => {
    if (user) {
      const userBackups = dataBackup.getUserBackups(user.id);
      setBackups(userBackups);
    }
  };

  const loadStats = () => {
    if (user) {
      const backupStats = dataBackup.getBackupStats(user.id);
      setStats(backupStats);
    }
  };

  const handleCreateBackup = async () => {
    if (!user) return;
    
    setLoading(true);
    setMessage('');
    
    try {
      const backupKey = await dataBackup.createUserBackup(user.id);
      if (backupKey) {
        setMessage('Backup created successfully!');
        setMessageType('success');
        loadBackups();
        loadStats();
      } else {
        setMessage('Failed to create backup');
        setMessageType('error');
      }
    } catch (error) {
      setMessage(`Error creating backup: ${error.message}`);
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  };

  const handleRestoreBackup = async (backupKey) => {
    if (!user) return;
    
    setLoading(true);
    setMessage('');
    
    try {
      const success = await dataBackup.restoreUserBackup(user.id, backupKey);
      if (success) {
        setMessage('Data restored successfully! Please refresh the page.');
        setMessageType('success');
        
        // Trigger data restoration event
        window.dispatchEvent(new CustomEvent('userDataRestored', {
          detail: { userId: user.id, fromBackup: true }
        }));
      } else {
        setMessage('Failed to restore backup');
        setMessageType('error');
      }
    } catch (error) {
      setMessage(`Error restoring backup: ${error.message}`);
      setMessageType('error');
    } finally {
      setLoading(false);
      setRestoreDialog(false);
      setSelectedBackup(null);
    }
  };

  const handleExportData = () => {
    if (!user) return;
    
    const success = dataBackup.exportUserData(user.id);
    if (success) {
      setMessage('Data exported successfully!');
      setMessageType('success');
    } else {
      setMessage('Failed to export data');
      setMessageType('error');
    }
  };

  const handleImportData = (event) => {
    const file = event.target.files[0];
    if (!file || !user) return;
    
    setLoading(true);
    setMessage('');
    
    dataBackup.importUserData(user.id, file)
      .then(success => {
        if (success) {
          setMessage('Data imported successfully! Please refresh the page.');
          setMessageType('success');
          
          // Trigger data restoration event
          window.dispatchEvent(new CustomEvent('userDataRestored', {
            detail: { userId: user.id, fromImport: true }
          }));
        } else {
          setMessage('Failed to import data');
          setMessageType('error');
        }
      })
      .catch(error => {
        setMessage(`Error importing data: ${error.message}`);
        setMessageType('error');
      })
      .finally(() => {
        setLoading(false);
        event.target.value = ''; // Reset file input
      });
  };

  const handleDeleteBackup = (backupKey) => {
    localStorage.removeItem(backupKey);
    setMessage('Backup deleted successfully');
    setMessageType('success');
    loadBackups();
    loadStats();
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (!user) {
    return (
      <Box p={3}>
        <Alert severity="warning">
          Please log in to access data recovery features.
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>
        Data Recovery & Backup
      </Typography>
      
      <Typography variant="body1" color="textSecondary" paragraph>
        Manage your data backups and recovery options. Your data is automatically saved, 
        but you can create manual backups for extra safety.
      </Typography>

      {message && (
        <Alert severity={messageType} sx={{ mb: 3 }}>
          {message}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Backup Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Backup Statistics
              </Typography>
              {stats ? (
                <Box>
                  <Typography variant="body2" color="textSecondary">
                    Total Backups: {stats.totalBackups}
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    Total Size: {formatFileSize(stats.totalSize)}
                  </Typography>
                  {stats.newestBackup && (
                    <Typography variant="body2" color="textSecondary">
                      Latest: {formatDate(stats.newestBackup)}
                    </Typography>
                  )}
                </Box>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No backup statistics available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Box display="flex" flexDirection="column" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<BackupIcon />}
                  onClick={handleCreateBackup}
                  disabled={loading}
                  fullWidth
                >
                  Create Backup
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportData}
                  fullWidth
                >
                  Export Data
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  component="label"
                  fullWidth
                >
                  Import Data
                  <input
                    type="file"
                    accept=".json"
                    hidden
                    onChange={handleImportData}
                  />
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Backup List */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Available Backups
              </Typography>
              
              {loading && <LinearProgress sx={{ mb: 2 }} />}
              
              {backups.length === 0 ? (
                <Alert severity="info">
                  No backups available. Create your first backup to get started.
                </Alert>
              ) : (
                <List>
                  {backups.map((backup, index) => (
                    <React.Fragment key={backup.key}>
                      <ListItem>
                        <ListItemText
                          primary={
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="subtitle1">
                                Backup #{backups.length - index}
                              </Typography>
                              {index === 0 && (
                                <Chip
                                  label="Latest"
                                  color="primary"
                                  size="small"
                                />
                              )}
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="textSecondary">
                                Created: {formatDate(backup.timestamp)}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                Size: {formatFileSize(backup.size)}
                              </Typography>
                              <Typography variant="body2" color="textSecondary">
                                Data Types: {backup.dataTypes.join(', ')}
                              </Typography>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          <IconButton
                            edge="end"
                            onClick={() => {
                              setSelectedBackup(backup);
                              setRestoreDialog(true);
                            }}
                            title="Restore this backup"
                          >
                            <RestoreIcon />
                          </IconButton>
                          <IconButton
                            edge="end"
                            onClick={() => handleDeleteBackup(backup.key)}
                            title="Delete this backup"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                      {index < backups.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Restore Confirmation Dialog */}
      <Dialog
        open={restoreDialog}
        onClose={() => setRestoreDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Confirm Data Restoration</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will replace your current data with the backup data. 
            This action cannot be undone.
          </Alert>
          {selectedBackup && (
            <Box>
              <Typography variant="body1" gutterBottom>
                <strong>Backup Details:</strong>
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Created: {formatDate(selectedBackup.timestamp)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Size: {formatFileSize(selectedBackup.size)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Data Types: {selectedBackup.dataTypes.join(', ')}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRestoreDialog(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => selectedBackup && handleRestoreBackup(selectedBackup.key)}
            color="primary"
            variant="contained"
          >
            Restore
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DataRecovery;



