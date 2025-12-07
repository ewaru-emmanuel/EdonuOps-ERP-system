import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../services/apiClient';
import {
  Box, Container, Typography, Button, TextField, Paper, Alert, CircularProgress,
  LinearProgress, Chip, IconButton, InputAdornment, Breadcrumbs, Link, Stepper, Step, StepLabel
} from '@mui/material';
import {
  PersonAdd, Visibility, VisibilityOff, CheckCircle, Error, Person, Home, Login, Dashboard, Refresh, Email
} from '@mui/icons-material';

function EnhancedRegister() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    phoneNumber: ''
  });
  
  const [passwordStrength, setPasswordStrength] = useState({
    score: 0,
    label: '',
    color: 'error',
    requirements: {
      length: false,
      uppercase: false,
      lowercase: false,
      number: false,
      special: false
    }
  });
  
  const [errors, setErrors] = useState({});
  const [infoMessage, setInfoMessage] = useState(null);
  const [showResendButton, setShowResendButton] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [verificationEmail, setVerificationEmail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const navigate = useNavigate();

  // Password strength checker
  const checkPasswordStrength = (password) => {
    const requirements = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
    };

    const score = Object.values(requirements).filter(Boolean).length;
    let label, color;

    if (score < 3) {
      label = 'Weak';
      color = 'error';
    } else if (score < 5) {
      label = 'Medium';
      color = 'warning';
    } else {
      label = 'Strong';
      color = 'success';
    }

    setPasswordStrength({ score, label, color, requirements });
    return score >= 3; // Minimum medium strength required
  };

  // Handle input changes
  const handleChange = (field) => (event) => {
    const value = event.target.value;
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific errors
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }

    // Check password strength
    if (field === 'password') {
      checkPasswordStrength(value);
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

    // Username validation
    if (!formData.username.trim()) {
      newErrors.username = 'Username is required';
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    // First Name validation
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'First name is required';
    } else if (formData.firstName.length < 2) {
      newErrors.firstName = 'First name must be at least 2 characters';
    }

    // Last Name validation
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Last name is required';
    } else if (formData.lastName.length < 2) {
      newErrors.lastName = 'Last name must be at least 2 characters';
    }

    // Phone Number validation
    if (!formData.phoneNumber.trim()) {
      newErrors.phoneNumber = 'Phone number is required';
    } else if (!/^[\+]?[1-9][\d]{0,15}$/.test(formData.phoneNumber.replace(/[\s\-\(\)]/g, ''))) {
      newErrors.phoneNumber = 'Please enter a valid phone number';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (passwordStrength.score < 5) {
      newErrors.password = 'Password must meet all requirements (8+ chars, uppercase, lowercase, number, special character)';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }


    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle resend verification email
  const handleResendVerification = async () => {
    if (!verificationEmail) return;
    
    setResendLoading(true);
    setErrors({});
    
    try {
      await apiClient.post('/api/auth/resend-verification', {
        email: verificationEmail
      });
      
      setInfoMessage({
        message: `Verification email sent successfully to ${verificationEmail}. Please check your inbox.`,
        field: 'email',
        type: 'verification_sent',
        email: verificationEmail
      });
      
      // Hide resend button again and show it after 5 seconds
      setShowResendButton(false);
      setTimeout(() => {
        setShowResendButton(true);
      }, 5000);
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.response?.data?.message || 'Failed to resend verification email';
      setErrors({ email: errorMessage });
    } finally {
      setResendLoading(false);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});
    setInfoMessage(null);
    setShowResendButton(false);
    setVerificationEmail(null);

    try {
      // Register user
      const userResponse = await apiClient.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirmPassword,
        first_name: formData.firstName,
        last_name: formData.lastName,
        phone_number: formData.phoneNumber,
        role: 'user' // Will be set to admin during onboarding
      });

      // Check if email verification was sent
      if (userResponse.email_verification_sent) {
        // Navigate to verification page with email info
        navigate('/verify-email', { 
          state: { 
            email: formData.email,
            message: userResponse.message 
          } 
        });
      } else {
        alert('Registration successful! Please login to continue with onboarding.');
        navigate('/login');
      }

    } catch (err) {
      console.error('Registration error:', err);
      
      // Handle 409 CONFLICT responses (email/username exists)
      if (err.status === 409 || err.response?.status === 409) {
        const errorData = err.response?.data || err.data;
        
        // Check if email exists but not verified
        if (errorData?.info === 'email_not_verified' && errorData?.can_resend) {
          const email = errorData?.email || formData.email;
          const message = errorData?.message || 'A verification email has been sent. Please check your inbox.';
          
          // Navigate to EmailVerification page (same page used for first-time registration)
          navigate('/verify-email', {
            state: {
              email: email,
              message: message,
              fromUnverifiedEmail: true
            }
          });
        } else {
          // Regular conflict (email/username exists and verified)
          const message = errorData?.message || 'An account with this information already exists. Please login instead.';
          
          setInfoMessage({
            message: message,
            field: errorData?.field || 'email',
            suggestion: errorData?.suggestion || 'login'
          });
          
          if (errorData?.field === 'email') {
            setErrors({ email: 'This email is already registered' });
          } else if (errorData?.field === 'username') {
            setErrors({ username: 'This username is already taken' });
          }
        }
      } else if (err.status === 400 || err.response?.status === 400) {
        const errorData = err.response?.data || err.data;
        if (errorData.errors) {
          // Map backend field names to frontend field names
          const mappedErrors = {};
          Object.keys(errorData.errors).forEach(key => {
            if (key === 'first_name') mappedErrors.firstName = errorData.errors[key];
            else if (key === 'last_name') mappedErrors.lastName = errorData.errors[key];
            else if (key === 'phone_number') mappedErrors.phoneNumber = errorData.errors[key];
            else if (key === 'confirm_password') mappedErrors.confirmPassword = errorData.errors[key];
            else mappedErrors[key] = errorData.errors[key];
          });
          setErrors(mappedErrors);
        } else {
          setErrors({ general: errorData.message || 'Registration failed' });
        }
      } else {
        // Handle other errors
        const errorMessage = err.response?.data?.message || err.message || 'Registration failed. Please try again.';
        setErrors({ general: errorMessage });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', py: 4 }}>
      <Paper elevation={3} sx={{ p: 4, width: '100%', maxWidth: 600 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4 }}>
          <PersonAdd color="primary" sx={{ fontSize: 48, mb: 2 }} />
          <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
            Create Your Account
          </Typography>
          <Typography variant="body1" color="text.secondary" textAlign="center">
            Join our ERP platform and set up your company during onboarding
          </Typography>
        </Box>

        {/* Breadcrumb Navigation */}
        <Box sx={{ mb: 4 }}>
          <Stepper activeStep={1} alternativeLabel>
            <Step>
              <StepLabel 
                icon={<Home />}
                onClick={() => navigate('/')}
                sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}
              >
                Home
              </StepLabel>
            </Step>
            <Step>
              <StepLabel 
                icon={<PersonAdd />}
                sx={{ color: 'primary.main', fontWeight: 'bold' }}
              >
                Register
              </StepLabel>
            </Step>
            <Step>
              <StepLabel 
                icon={<Login />}
                sx={{ color: 'text.disabled' }}
              >
                Login
              </StepLabel>
            </Step>
            <Step>
              <StepLabel 
                icon={<Dashboard />}
                sx={{ color: 'text.disabled' }}
              >
                Dashboard
              </StepLabel>
            </Step>
          </Stepper>
        </Box>
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          {infoMessage && (
            <Alert 
              severity={infoMessage.type === 'verification_sent' ? 'info' : 'info'}
              icon={infoMessage.type === 'verification_sent' ? <Email /> : undefined}
              sx={{ mb: 3 }}
              action={
                infoMessage.type === 'verification_sent' && showResendButton ? (
                  <Button 
                    color="inherit" 
                    size="small" 
                    onClick={handleResendVerification}
                    disabled={resendLoading}
                    startIcon={resendLoading ? <CircularProgress size={16} /> : <Refresh />}
                    sx={{ textTransform: 'none', fontWeight: 500 }}
                  >
                    {resendLoading ? 'Sending...' : 'Resend Email'}
                  </Button>
                ) : infoMessage.suggestion === 'login' ? (
                  <Button 
                    color="inherit" 
                    size="small" 
                    onClick={() => navigate('/login')}
                    sx={{ textTransform: 'none', fontWeight: 500 }}
                  >
                    Go to Login
                  </Button>
                ) : null
              }
            >
              <Box>
                <Typography variant="body1" sx={{ mb: 0.5, fontWeight: 500 }}>
                  {infoMessage.message}
                </Typography>
                {infoMessage.type === 'verification_sent' && (
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Please check your inbox and spam folder. If you don't receive the email within a few minutes, click the resend button.
                  </Typography>
                )}
                {infoMessage.suggestion === 'login' && (
                  <Typography variant="body2" color="text.secondary">
                    If this is your account, please login to continue. If you forgot your password, you can reset it from the login page.
                  </Typography>
                )}
              </Box>
            </Alert>
          )}
          
          {errors.general && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {errors.general}
            </Alert>
          )}

          {/* Personal Information */}
          <Typography variant="h6" gutterBottom sx={{ mt: 3, mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Person color="primary" />
            Personal Information
          </Typography>

          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              label="Username"
              value={formData.username}
              onChange={handleChange('username')}
              error={!!errors.username}
              helperText={errors.username}
              required
            />
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={formData.email}
              onChange={handleChange('email')}
              error={!!errors.email}
              helperText={errors.email}
              required
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              label="First Name"
              value={formData.firstName}
              onChange={handleChange('firstName')}
              error={!!errors.firstName}
              helperText={errors.firstName}
              required
            />
            <TextField
              fullWidth
              label="Last Name"
              value={formData.lastName}
              onChange={handleChange('lastName')}
              error={!!errors.lastName}
              helperText={errors.lastName}
              required
            />
          </Box>

          <TextField
            fullWidth
            label="Phone Number"
            value={formData.phoneNumber}
            onChange={handleChange('phoneNumber')}
            error={!!errors.phoneNumber}
            helperText={errors.phoneNumber}
            required
            placeholder="+1 (555) 123-4567"
            sx={{ mb: 2 }}
          />

          {/* Password Section */}
          <Box sx={{ mb: 2 }}>
            <TextField
              fullWidth
              label="Password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={handleChange('password')}
              error={!!errors.password}
              helperText={errors.password}
              required
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                )
              }}
            />
            
            {/* Password Requirements */}
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Password must contain: 8+ characters, uppercase, lowercase, number, and special character (!@#$%^&*)
            </Typography>
            
            {/* Password Strength Indicator */}
            {formData.password && (
              <Box sx={{ mt: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Typography variant="body2">Password Strength:</Typography>
                  <Chip 
                    label={passwordStrength.label} 
                    color={passwordStrength.color}
                    size="small"
                  />
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={(passwordStrength.score / 5) * 100} 
                  color={passwordStrength.color}
                  sx={{ height: 4, borderRadius: 2 }}
                />
                
                {/* Password Requirements */}
                <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {Object.entries(passwordStrength.requirements).map(([key, met]) => (
                    <Box key={key} sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      {met ? <CheckCircle color="success" fontSize="small" /> : <Error color="error" fontSize="small" />}
                      <Typography variant="caption" color={met ? 'success.main' : 'error.main'}>
                        {key === 'length' ? '8+ characters' :
                         key === 'uppercase' ? 'Uppercase' :
                         key === 'lowercase' ? 'Lowercase' :
                         key === 'number' ? 'Number' : 'Special char'}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </Box>
            )}
          </Box>

          <TextField
            fullWidth
            label="Confirm Password"
            type={showConfirmPassword ? 'text' : 'password'}
            value={formData.confirmPassword}
            onChange={handleChange('confirmPassword')}
            error={!!errors.confirmPassword}
            helperText={errors.confirmPassword}
            required
            sx={{ mb: 3 }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowConfirmPassword(!showConfirmPassword)} edge="end">
                    {showConfirmPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />


          {/* Submit Button */}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            size="large"
            disabled={loading || passwordStrength.score < 5}
            sx={{ mt: 3, mb: 2, py: 1.5 }}
          >
            {loading ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={20} color="inherit" />
                <Typography>Creating Account...</Typography>
              </Box>
            ) : (
              'Create Account'
            )}
          </Button>

          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Already have an account?{' '}
              <Button 
                variant="text" 
                onClick={() => navigate('/login')}
                sx={{ textTransform: 'none' }}
              >
                Sign in here
              </Button>
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}

export default EnhancedRegister;
