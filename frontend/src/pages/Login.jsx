import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Link,
  InputAdornment,
  IconButton
} from '@mui/material';
import {
  Email as EmailIcon,
  Lock as LockIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  PersonAdd as PersonAddIcon,
  Login as LoginIcon,
  Security as SecurityIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { apiClient } from '../utils/apiClient';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetLoading, setResetLoading] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);
  const [resetSuccessEmail, setResetSuccessEmail] = useState('');
  const [resetError, setResetError] = useState('');
  
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const success = await login(email, password);
      if (success) {
        navigate('/dashboard');
      } else {
        setError('Invalid email or password');
      }
    } catch (err) {
      if (err.response?.data?.email_verification_required) {
        setError('Please verify your email address before logging in. Check your email for verification instructions.');
      } else {
        setError('Invalid email or password');
      }
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordReset = async () => {
    if (!resetEmail) {
      setResetError('Please enter your email address');
      return;
    }

    setResetLoading(true);
    setResetError('');
    setResetSuccess(false);
    setResetSuccessEmail('');

    try {
      const response = await apiClient.post('/api/auth/request-password-reset', {
        email: resetEmail
      });
      
      // Show success with email address
      if (response.email) {
        setResetSuccessEmail(response.email);
        setResetSuccess(true);
      } else {
        // Fallback if email not in response
        setResetSuccessEmail(resetEmail);
        setResetSuccess(true);
      }
    } catch (err) {
      console.error('Password reset error:', err);
      const errorMessage = err.response?.data?.error || err.response?.data?.message || err.message || 'Failed to send password reset email';
      setResetError(errorMessage);
      setResetSuccess(false);
    } finally {
      setResetLoading(false);
    }
  };

  const handleResendReset = () => {
    setResetSuccess(false);
    setResetSuccessEmail('');
    setResetError('');
    handlePasswordReset();
  };

  const openResetDialog = () => {
    setResetDialogOpen(true);
    setResetEmail(email); // Pre-fill with login email
    setResetError('');
    setResetSuccess(false);
    setResetSuccessEmail('');
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Card sx={{ width: '100%', boxShadow: 3 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <LoginIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
              <Typography component="h1" variant="h4" align="center" gutterBottom>
                Welcome Back
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Sign in to your EdonuOps ERP account
              </Typography>
            </Box>
            
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email address"
                InputProps={{
                  startAdornment: (
                    <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                }}
                helperText="Use the email address you registered with"
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                InputProps={{
                  startAdornment: (
                    <LockIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  ),
                  endAdornment: (
                    <IconButton
                      onClick={() => setShowPassword(!showPassword)}
                      edge="end"
                      aria-label="toggle password visibility"
                    >
                      {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                    </IconButton>
                  ),
                }}
                helperText="Your password is encrypted and secure"
              />
              
              <Box sx={{ textAlign: 'right', mt: 1 }}>
                <Link
                  component="button"
                  variant="body2"
                  onClick={openResetDialog}
                  sx={{ textDecoration: 'none' }}
                >
                  Forgot your password?
                </Link>
              </Box>
              
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2, py: 1.5 }}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <LoginIcon />}
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </Button>
              
              {/* Sign Up Section */}
              <Box sx={{ textAlign: 'center', mt: 3, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Don't have an account?
                </Typography>
                <Button
                  variant="outlined"
                  fullWidth
                  onClick={() => navigate('/register')}
                  startIcon={<PersonAddIcon />}
                  sx={{ py: 1.5 }}
                >
                  Create New Account
                </Button>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Box>
      
      {/* Password Reset Dialog */}
      <Dialog open={resetDialogOpen} onClose={() => setResetDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
          {resetSuccess ? (
            <CheckCircleIcon sx={{ fontSize: 48, color: 'success.main', mb: 1, display: 'block', mx: 'auto' }} />
          ) : (
            <SecurityIcon sx={{ fontSize: 32, color: 'primary.main', mb: 1, display: 'block', mx: 'auto' }} />
          )}
          {resetSuccess ? 'Check Your Email' : 'Reset Your Password'}
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 1 }}>
            {resetSuccess ? (
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: 'text.primary' }}>
                  Password Reset Link Sent
                </Typography>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  A password reset link has been sent to:
                </Typography>
                <Box
                  sx={{
                    bgcolor: 'primary.50',
                    border: '1px solid',
                    borderColor: 'primary.200',
                    borderRadius: 2,
                    p: 2,
                    mb: 3
                  }}
                >
                  <Typography
                    variant="body1"
                    sx={{
                      fontWeight: 600,
                      color: 'primary.main',
                      wordBreak: 'break-word'
                    }}
                  >
                    {resetSuccessEmail}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Please check your inbox and click the link to reset your password. The link will expire in 1 hour.
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Didn't receive the email? Check your spam folder or click resend below.
                </Typography>
              </Box>
            ) : (
              <>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3, textAlign: 'center' }}>
                  Enter your email address and we'll send you a secure link to reset your password.
                </Typography>
                
                {resetError && (
                  <Alert severity="error" sx={{ mb: 2 }}>
                    {resetError}
                  </Alert>
                )}
                
                <TextField
                  fullWidth
                  label="Email Address"
                  type="email"
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                  margin="normal"
                  required
                  disabled={resetLoading}
                  InputProps={{
                    startAdornment: (
                      <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    ),
                  }}
                />
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 1, justifyContent: resetSuccess ? 'space-between' : 'flex-end' }}>
          {resetSuccess && (
            <Button
              onClick={handleResendReset}
              variant="outlined"
              startIcon={<RefreshIcon />}
              disabled={resetLoading}
              sx={{ mr: 'auto' }}
            >
              {resetLoading ? 'Sending...' : 'Resend Link'}
            </Button>
          )}
          <Button
            onClick={() => {
              setResetDialogOpen(false);
              setResetSuccess(false);
              setResetSuccessEmail('');
              setResetError('');
              setResetEmail('');
            }}
            variant={resetSuccess ? 'contained' : 'outlined'}
          >
            {resetSuccess ? 'Close' : 'Cancel'}
          </Button>
          {!resetSuccess && (
            <Button
              onClick={handlePasswordReset}
              variant="contained"
              disabled={resetLoading || !resetEmail}
              startIcon={resetLoading ? <CircularProgress size={16} /> : <SecurityIcon />}
            >
              {resetLoading ? 'Sending...' : 'Send Reset Link'}
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Login;