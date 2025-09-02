import React, { useState, useEffect } from 'react';
import { Alert, Button, Box, Typography } from '@mui/material';
import { Refresh, CheckCircle, Error } from '@mui/icons-material';
import apiClient from '../../services/apiClient';

const BackendStatusChecker = () => {
  const [status, setStatus] = useState('checking');
  const [message, setMessage] = useState('Checking backend connection...');

  const checkBackend = async () => {
    setStatus('checking');
    setMessage('Checking backend connection...');
    
    try {
      console.log('🔍 Checking backend health...');
      
      // Check if backend is running
      const healthData = await apiClient.healthCheck();
      console.log('✅ Backend health check successful:', healthData);
      
      // Test a finance endpoint
      const financeData = await apiClient.get('/finance/ar');
      console.log('✅ Finance endpoint test successful:', financeData);
      setStatus('success');
      setMessage(`Backend is running and responsive. Finance endpoints working. (${financeData.length} records available)`);
    } catch (error) {
      console.error('❌ Backend connection failed:', error);
      setStatus('error');
      
      setMessage('Cannot connect to backend. Please ensure backend is running.');
    }
  };

  useEffect(() => {
    checkBackend();
  }, []);

  const getAlertSeverity = () => {
    switch (status) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'info';
    }
  };

  const getIcon = () => {
    switch (status) {
      case 'success': return <CheckCircle />;
      case 'error': return <Error />;
      default: return <Refresh />;
    }
  };

  return (
    <Box sx={{ mb: 2 }}>
      <Alert 
        severity={getAlertSeverity()} 
        icon={getIcon()}
        action={
          <Button 
            color="inherit" 
            size="small" 
            onClick={checkBackend}
            startIcon={<Refresh />}
            disabled={status === 'checking'}
          >
            {status === 'checking' ? 'Checking...' : 'Recheck'}
          </Button>
        }
      >
        <Typography variant="body2">
          <strong>Backend Status:</strong> {message}
        </Typography>
        
        {status === 'error' && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
              🔧 <strong>To fix:</strong> Run `cd backend && python run.py` in your terminal
            </Typography>
          </Box>
        )}
      </Alert>
    </Box>
  );
};

export default BackendStatusChecker;





