import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Container,
  Paper,
  InputAdornment,
  IconButton,
  LinearProgress
} from '@mui/material';
import {
  Lock as LockIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import { apiClient } from '../utils/apiClient';

const PasswordReset = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: ''
  });

  const [validation, setValidation] = useState({
    password: { valid: true, message: '' },
    confirmPassword: { valid: true, message: '' }
  });

  useEffect(() => {
    if (token) {
      validateToken();
    } else {
      setError('No password reset token provided');
    }
  }, [token]);

  const validateToken = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post('/api/auth/validate-token', {
        token: token,
        type: 'password_reset'
      });

      // apiClient returns JSON directly, not wrapped in data
      if (response && response.valid === true) {
        setUserInfo(response.user);
      } else {
        // Handle case where valid is false (shouldn't happen with 200 status, but handle it)
        setError(response?.message || 'Invalid or expired password reset token');
      }
    } catch (err) {
      console.error('Token validation error:', err);
      // Handle both error response formats
      let errorMessage = 'Token validation failed';
      if (err.response) {
        // Try to get message from error response
        const errorData = err.response.data || {};
        errorMessage = errorData.message || errorData.error || errorMessage;
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const validateField = (field, value) => {
    let valid = true;
    let message = '';

    switch (field) {
      case 'password':
        if (!value || value.length < 8) {
          valid = false;
          message = 'Password must be at least 8 characters long';
        } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])/.test(value)) {
          valid = false;
          message = 'Password must contain uppercase, lowercase, number, and special character';
        }
        break;
      case 'confirmPassword':
        if (!value || value !== formData.password) {
          valid = false;
          message = 'Passwords do not match';
        }
        break;
    }

    setValidation(prev => ({
      ...prev,
      [field]: { valid, message }
    }));

    return valid;
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    validateField(field, value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate all fields
    const isPasswordValid = validateField('password', formData.password);
    const isConfirmPasswordValid = validateField('confirmPassword', formData.confirmPassword);

    if (!isPasswordValid || !isConfirmPasswordValid) {
      setError('Please fix the validation errors before submitting');
      return;
    }

    setLoading(true);
    try {
      await apiClient.post('/api/auth/reset-password', {
        token: token,
        password: formData.password
      });

      setSuccess('Password reset successfully!');
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);

    } catch (err) {
      console.error('Password reset error:', err);
      const errorMessage = err.response?.data?.message || err.response?.data?.error || err.message || 'Password reset failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getPasswordStrength = (password) => {
    if (!password) return { strength: 0, label: '', color: '' };
    
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[@$!%*?&]/.test(password)) strength++;

    const labels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['error', 'error', 'warning', 'success', 'success'];
    
    return {
      strength: (strength / 5) * 100,
      label: labels[strength - 1] || '',
      color: colors[strength - 1] || 'error'
    };
  };

  const passwordStrength = getPasswordStrength(formData.password);

  if (!token) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <ErrorIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            Invalid Reset Link
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            This password reset link is invalid or has expired.
          </Typography>
          <Button variant="contained" onClick={() => navigate('/login')}>
            Go to Login
          </Button>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <SecurityIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" component="h1" gutterBottom>
            Reset Your Password
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {loading ? 'Validating reset link...' : userInfo ? 'Enter your new password below' : 'Please wait while we validate your reset link'}
          </Typography>
        </Box>

        {loading && !userInfo && (
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <CircularProgress sx={{ mb: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Validating your password reset link...
            </Typography>
          </Box>
        )}

        {userInfo && (
          <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1, mb: 3 }}>
            <Typography variant="body2" color="text.secondary">
              <strong>Account:</strong> {userInfo.username} ({userInfo.email})
            </Typography>
          </Box>
        )}

        {loading && userInfo && <LinearProgress sx={{ mb: 3 }} />}

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert 
            severity="success" 
            sx={{ mb: 3 }}
            icon={<CheckCircleIcon />}
          >
            {success}
          </Alert>
        )}

        {userInfo && !success && !loading && (
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="New Password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              error={!validation.password.valid}
              helperText={validation.password.message}
              margin="normal"
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                    >
                      {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            
            {formData.password && (
              <Box sx={{ mt: 1, mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Password Strength: {passwordStrength.label}
                </Typography>
                <Box sx={{ mt: 0.5 }}>
                  <Box
                    sx={{
                      height: 4,
                      bgcolor: 'grey.200',
                      borderRadius: 2,
                      overflow: 'hidden'
                    }}
                  >
                    <Box
                      sx={{
                        height: '100%',
                        width: `${passwordStrength.strength}%`,
                        bgcolor: `${passwordStrength.color}.main`,
                        transition: 'width 0.3s ease'
                      }}
                    />
                  </Box>
                </Box>
              </Box>
            )}

            <TextField
              fullWidth
              label="Confirm New Password"
              type={showConfirmPassword ? 'text' : 'password'}
              value={formData.confirmPassword}
              onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
              error={!validation.confirmPassword.valid}
              helperText={validation.confirmPassword.message}
              margin="normal"
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <LockIcon />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      edge="end"
                    >
                      {showConfirmPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <Box sx={{ mt: 4, textAlign: 'center' }}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={loading || !validation.password.valid || !validation.confirmPassword.valid}
                sx={{ minWidth: 200 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Reset Password'}
              </Button>
            </Box>
          </Box>
        )}

        {success && (
          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              You will be redirected to the login page in a few seconds...
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/login')}
              size="large"
            >
              Continue to Login
            </Button>
          </Box>
        )}

        {!userInfo && !loading && (
          <Box sx={{ textAlign: 'center', mt: 3 }}>
            <Button
              variant="outlined"
              onClick={() => navigate('/login')}
            >
              Go to Login
            </Button>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default PasswordReset;

