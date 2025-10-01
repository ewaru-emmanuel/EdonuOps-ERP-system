import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../services/apiClient';
import {
  Box, Container, Typography, Button, TextField, Paper, Alert, CircularProgress,
  LinearProgress, Chip, IconButton, InputAdornment, Breadcrumbs, Link, Stepper, Step, StepLabel
} from '@mui/material';
import {
  PersonAdd, Visibility, VisibilityOff, CheckCircle, Error, Person, Home, Login, Dashboard
} from '@mui/icons-material';

function EnhancedRegister() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
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

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (passwordStrength.score < 3) {
      newErrors.password = 'Password must be at least medium strength';
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

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      // Register user
      const userResponse = await apiClient.register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        role: 'user' // Will be set to admin during onboarding
      });

      alert('Registration successful! Please login to continue with onboarding.');
      navigate('/login');

    } catch (err) {
      console.error('Registration error:', err);
      
      if (err.response?.status === 409) {
        setErrors({ email: 'An account with this email already exists' });
      } else if (err.response?.status === 400) {
        const errorData = err.response.data;
        if (errorData.errors) {
          setErrors(errorData.errors);
        } else {
          setErrors({ general: errorData.message || 'Registration failed' });
        }
      } else {
        setErrors({ general: err.message || 'Registration failed. Please try again.' });
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
            disabled={loading || passwordStrength.score < 3}
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
