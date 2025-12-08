import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Container,
  Paper,
  Divider
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Email as EmailIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import apiClient from '../services/apiClient';

// Static onboarding background component - no OnboardingWizard import needed
const StaticOnboardingBackground = () => {
  return (
    <Box sx={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      p: 4
    }}>
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', color: 'white' }}>
          <Typography variant="h2" component="h1" gutterBottom sx={{ fontWeight: 'bold', mb: 4 }}>
            Welcome to Your ERP System
          </Typography>
          <Typography variant="h5" sx={{ mb: 6, opacity: 0.9 }}>
            Complete your setup to get started
          </Typography>
          
          {/* Static steps */}
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 4, flexWrap: 'wrap' }}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ 
                width: 80, 
                height: 80, 
                borderRadius: '50%', 
                bgcolor: 'rgba(255,255,255,0.2)', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                mb: 2,
                mx: 'auto'
              }}>
                <Typography variant="h4">1</Typography>
              </Box>
              <Typography variant="h6">Company Setup</Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>Configure your business</Typography>
            </Box>
            
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ 
                width: 80, 
                height: 80, 
                borderRadius: '50%', 
                bgcolor: 'rgba(255,255,255,0.2)', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                mb: 2,
                mx: 'auto'
              }}>
                <Typography variant="h4">2</Typography>
              </Box>
              <Typography variant="h6">Modules</Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>Choose your features</Typography>
            </Box>
            
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ 
                width: 80, 
                height: 80, 
                borderRadius: '50%', 
                bgcolor: 'rgba(255,255,255,0.2)', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                mb: 2,
                mx: 'auto'
              }}>
                <Typography variant="h4">3</Typography>
              </Box>
              <Typography variant="h6">Ready to Go</Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>Start using your ERP</Typography>
            </Box>
          </Box>
        </Box>
      </Container>
    </Box>
  );
};

const EmailVerification = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [userInfo, setUserInfo] = useState(null);
  const [userEmail, setUserEmail] = useState(null);
  const [fromRegistration, setFromRegistration] = useState(false);
  const [verificationAttempted, setVerificationAttempted] = useState(false);

  useEffect(() => {
    // Check if user came from registration or unverified email (has state with email)
    if (location.state?.email) {
      setFromRegistration(true);
      setUserEmail(location.state.email);
      setSuccess(location.state.message || 'A verification email has been sent. Please check your inbox to verify your account.');
    } else if (token && !verificationAttempted) {
      // User came from email link - only verify once
      setVerificationAttempted(true);
      // Call verifyEmail directly - don't include it in dependencies to prevent re-renders
      const verify = async () => {
        setLoading(true);
        setError(null);
        setSuccess(null);
        
        try {
          const response = await apiClient.post('/api/auth/verify-email', {
            token: token
          });

          console.log('📧 Verification response:', response);

          // apiClient.post returns the JSON directly, not wrapped in .data
          // Check if already verified or newly verified
          if (response.already_verified || response.user) {
            const userInfo = response.user;
            if (userInfo) {
              setUserInfo(userInfo);
              setUserEmail(userInfo.email);
            }
            
            // Auto-login: Store token and user info if access token is provided
            if (response.access_token) {
              // Store authentication data IMMEDIATELY
              localStorage.setItem('sessionToken', response.access_token);
              localStorage.setItem('access_token', response.access_token);
              localStorage.setItem('userId', userInfo?.id?.toString() || '');
              localStorage.setItem('userEmail', userInfo?.email || '');
              localStorage.setItem('username', userInfo?.username || '');
              if (userInfo?.role) {
                localStorage.setItem('userRole', userInfo.role);
              }
              if (userInfo?.tenant_id) {
                localStorage.setItem('tenantId', userInfo.tenant_id);
              }
              if (userInfo) {
                localStorage.setItem('user', JSON.stringify(userInfo));
              }
              
              // Verify token is stored before proceeding
              const storedToken = localStorage.getItem('sessionToken');
              if (!storedToken) {
                console.error('❌ Failed to store authentication token');
                setError('Failed to store authentication token. Please try logging in manually.');
                return;
              }
              
              console.log('✅ Authentication token stored successfully');
              
              // Trigger auth context update and wait a moment for it to process
              window.dispatchEvent(new CustomEvent('auth:login', { detail: userInfo }));
              
              const message = response.already_verified 
                ? '✅ Your email is already verified! Redirecting to onboarding...'
                : '✅ Email verified successfully! Redirecting to onboarding...';
              
              setSuccess(message);
              
              // Give AuthContext time to update before redirecting
              // Also ensure token is available for apiClient
              setTimeout(() => {
                // Double-check token is still available before redirect
                const verifyToken = localStorage.getItem('sessionToken');
                if (verifyToken) {
                  console.log('✅ Token verified, redirecting to onboarding');
                  navigate('/onboarding');
                } else {
                  console.error('❌ Token missing on redirect, redirecting to login instead');
                  navigate('/login');
                }
              }, 2000); // Increased to 2 seconds to ensure AuthContext updates
            } else {
              // No token (already verified scenario) - redirect to login
              const message = response.already_verified 
                ? '✅ Your email is already verified! Redirecting to login...'
                : '✅ Email verified successfully! Redirecting to login...';
              
              setSuccess(message);
              
              setTimeout(() => {
                navigate('/login');
              }, 2000);
            }
          } else {
            setSuccess('✅ Email verified successfully!');
            setTimeout(() => {
              navigate('/login');
            }, 2000);
          }
        } catch (err) {
          console.error('❌ Email verification error:', err);
          const errorMessage = err.response?.data?.error || err.response?.data?.message || err.message || 'Email verification failed';
          setError(errorMessage);
        } finally {
          setLoading(false);
        }
      };
      
      verify();
    } else if (!location.state?.email && !token) {
      // No email or token - redirect to register
      navigate('/register');
    }
  }, [token, location.state, verificationAttempted, navigate]);

  const verifyEmail = async () => {
    // Prevent multiple verification attempts
    if (verificationAttempted && !error && !success) {
      return;
    }
    
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      // Verify the email directly
      const response = await apiClient.post('/api/auth/verify-email', {
        token: token
      });

      console.log('📧 Verification response:', response);

      // apiClient.post returns the JSON directly, not wrapped in .data
      // Check if already verified or newly verified
      if (response.already_verified || response.user) {
        const userInfo = response.user;
        if (userInfo) {
          setUserInfo(userInfo);
          setUserEmail(userInfo.email);
        }
        
        // Auto-login: Store token and user info if access token is provided
        if (response.access_token) {
          // Store authentication data
          localStorage.setItem('sessionToken', response.access_token);
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('userId', userInfo?.id?.toString() || '');
          localStorage.setItem('userEmail', userInfo?.email || '');
          localStorage.setItem('username', userInfo?.username || '');
          if (userInfo?.role) {
            localStorage.setItem('userRole', userInfo.role);
          }
          if (userInfo?.tenant_id) {
            localStorage.setItem('tenantId', userInfo.tenant_id);
          }
          if (userInfo) {
            localStorage.setItem('user', JSON.stringify(userInfo));
          }
          
          // Trigger auth context update
          window.dispatchEvent(new CustomEvent('auth:login', { detail: userInfo }));
          
          const message = response.already_verified 
            ? '✅ Your email is already verified! Redirecting to onboarding...'
            : '✅ Email verified successfully! Redirecting to onboarding...';
          
          setSuccess(message);
          
          // Redirect to onboarding page after 1.5 seconds
          setTimeout(() => {
            navigate('/onboarding');
          }, 1500);
        } else {
          // No token (already verified scenario) - redirect to login
          const message = response.already_verified 
            ? '✅ Your email is already verified! Redirecting to login...'
            : '✅ Email verified successfully! Redirecting to login...';
          
          setSuccess(message);
          
          setTimeout(() => {
            navigate('/login');
          }, 2000);
        }
      } else {
        setSuccess('✅ Email verified successfully!');
        // Fallback to login page
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      }

    } catch (err) {
      const errorMessage = err.response?.data?.error || err.response?.data?.message || 'Email verification failed';
      setError(errorMessage);
      
      // If we have user email from validation, we can still offer resend
      if (userEmail) {
        setUserInfo({ email: userEmail });
      }
    } finally {
      setLoading(false);
    }
  };

  const resendVerification = async () => {
    const emailToUse = userEmail || userInfo?.email;
    
    if (!emailToUse) {
      setError('No email address available for resending verification');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      await apiClient.post('/api/auth/resend-verification', {
        email: emailToUse
      });
      setSuccess('✅ Verification email sent successfully!');
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.response?.data?.message || 'Failed to resend verification email';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ position: 'relative', minHeight: '100vh' }}>
      {/* Onboarding Wizard as Background */}
      <Box sx={{ 
        position: 'absolute', 
        top: 0, 
        left: 0, 
        right: 0, 
        bottom: 0,
        opacity: 0.3,
        zIndex: 0
      }}>
        <StaticOnboardingBackground />
      </Box>
      
      {/* Verification Card Overlay */}
      <Box sx={{ 
        position: 'relative', 
        zIndex: 1, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        minHeight: '100vh',
        p: 2
      }}>
        <Container maxWidth="sm">
          <Card elevation={8} sx={{ 
            p: 4, 
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            borderRadius: 3
          }}>
            <CardContent>
              {fromRegistration && userEmail ? (
                <>
                  <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <CheckCircleIcon sx={{ fontSize: 64, color: 'success.main', mb: 3 }} />
                    <Typography variant="body1" sx={{ color: 'text.primary', fontSize: '1rem', lineHeight: 1.6 }}>
                      A verification email has been sent to <strong>'{userEmail}'</strong>. Please check your inbox to verify your account.
                    </Typography>
                  </Box>

                  {loading && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
                      <CircularProgress />
                    </Box>
                  )}

                  {error && (
                    <Alert severity="error" sx={{ mb: 3 }}>
                      {error}
                    </Alert>
                  )}

                  <Box sx={{ textAlign: 'center', mt: 4 }}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={resendVerification}
                      disabled={loading}
                      startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <RefreshIcon />}
                      sx={{ 
                        textTransform: 'none', 
                        fontWeight: 500,
                        px: 4,
                        py: 1.5,
                        borderRadius: 2,
                        minWidth: 160
                      }}
                    >
                      {loading ? 'Sending...' : 'Resend Email'}
                    </Button>
                  </Box>
                </>
              ) : (
                <>
                  <Box sx={{ textAlign: 'center', mb: 4 }}>
                    <EmailIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
                    <Typography variant="h4" component="h1" gutterBottom>
                      Email Verification
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      Verifying your email address...
                    </Typography>
                  </Box>

              {loading && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
                  <CircularProgress />
                </Box>
              )}

              {error && (
                <Alert 
                  severity="error" 
                  sx={{ mb: 3 }}
                  action={
                    (userEmail || userInfo?.email) && (
                      <Button
                        color="inherit"
                        size="small"
                        onClick={resendVerification}
                        disabled={loading}
                        startIcon={<RefreshIcon />}
                      >
                        Resend
                      </Button>
                    )
                  }
                >
                  {error}
                </Alert>
              )}

              {success && (
                <Alert 
                  severity="success" 
                  sx={{ mb: 3 }}
                  icon={<CheckCircleIcon />}
                  action={
                    fromRegistration && userEmail && (
                      <Button
                        color="inherit"
                        size="small"
                        onClick={resendVerification}
                        disabled={loading}
                        startIcon={<RefreshIcon />}
                        sx={{ textTransform: 'none', fontWeight: 500 }}
                      >
                        Resend Email
                      </Button>
                    )
                  }
                >
                  {success}
                </Alert>
              )}

              {userInfo && success && (
                <Box sx={{ mt: 3 }}>
                  <Divider sx={{ mb: 3 }} />
                  <Typography variant="h6" gutterBottom>
                    Account Details
                  </Typography>
                  <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Username:</strong> {userInfo.username || 'N/A'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Email:</strong> {userEmail || userInfo.email || 'N/A'}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    You will be redirected to onboarding in a few seconds...
                  </Typography>
                </Box>
              )}

              {!loading && !success && !error && (
                <Box sx={{ textAlign: 'center', mt: 3 }}>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/login')}
                    sx={{ mr: 2 }}
                  >
                    Go to Login
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => navigate('/register')}
                  >
                    Register Again
                  </Button>
                </Box>
              )}

              {success && (
                <Box sx={{ textAlign: 'center', mt: 3 }}>
                  <Button
                    variant="contained"
                    onClick={() => navigate('/login')}
                    size="large"
                  >
                    Continue to Login
                  </Button>
                </Box>
              )}
                </>
              )}
            </CardContent>
          </Card>
        </Container>
      </Box>
    </Box>
  );
};

export default EmailVerification;
