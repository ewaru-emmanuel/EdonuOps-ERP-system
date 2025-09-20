import React, { useState } from 'react';
import {
  Box, Typography, Card, CardContent, TextField, Button, Alert,
  List, ListItem, ListItemIcon, ListItemText, Chip, LinearProgress
} from '@mui/material';
import {
  CheckCircle, Cancel, Security, Visibility, VisibilityOff, Refresh
} from '@mui/icons-material';
import apiClient from '../services/apiClient';

const PasswordPolicyTester = ({ onPasswordValidated, initialPassword = '' }) => {
  const [password, setPassword] = useState(initialPassword);
  const [username, setUsername] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testPassword = async () => {
    if (!password) {
      setValidationResult({
        is_valid: false,
        errors: ['Password is required']
      });
      return;
    }

    setLoading(true);
    try {
      const response = await apiClient.post('/security/validate-password', {
        password: password,
        username: username || undefined
      });

      setValidationResult(response);
      
      // Call callback if provided
      if (onPasswordValidated) {
        onPasswordValidated(response.is_valid, response.errors);
      }
    } catch (error) {
      console.error('Password validation error:', error);
      setValidationResult({
        is_valid: false,
        errors: ['Failed to validate password']
      });
    } finally {
      setLoading(false);
    }
  };

  const generateStrongPassword = () => {
    const length = 12;
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    
    // Ensure at least one of each required character type
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    const special = '!@#$%^&*';
    
    password += lowercase[Math.floor(Math.random() * lowercase.length)];
    password += uppercase[Math.floor(Math.random() * uppercase.length)];
    password += numbers[Math.floor(Math.random() * numbers.length)];
    password += special[Math.floor(Math.random() * special.length)];
    
    // Fill the rest randomly
    for (let i = 4; i < length; i++) {
      password += charset[Math.floor(Math.random() * charset.length)];
    }
    
    // Shuffle the password
    setPassword(password.split('').sort(() => Math.random() - 0.5).join(''));
  };

  const getValidationIcon = (isValid) => {
    return isValid ? <CheckCircle color="success" /> : <Cancel color="error" />;
  };

  const getValidationColor = (isValid) => {
    return isValid ? 'success' : 'error';
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Security color="primary" />
          Password Policy Tester
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {/* Username field (optional) */}
          <TextField
            fullWidth
            label="Username (optional)"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            size="small"
            helperText="Enter username to check if password contains it"
          />

          {/* Password field */}
          <TextField
            fullWidth
            label="Password to Test"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            size="small"
            InputProps={{
              endAdornment: (
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    onClick={() => setShowPassword(!showPassword)}
                    sx={{ minWidth: 'auto', p: 0.5 }}
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </Button>
                  <Button
                    size="small"
                    onClick={generateStrongPassword}
                    sx={{ minWidth: 'auto', p: 0.5 }}
                    title="Generate strong password"
                  >
                    <Refresh />
                  </Button>
                </Box>
              )
            }}
            helperText="Enter a password to test against security policy"
          />

          {/* Test button */}
          <Button
            variant="contained"
            onClick={testPassword}
            disabled={loading || !password}
            startIcon={<Security />}
          >
            {loading ? 'Testing...' : 'Test Password'}
          </Button>

          {loading && <LinearProgress />}

          {/* Validation result */}
          {validationResult && (
            <Alert 
              severity={getValidationColor(validationResult.is_valid)}
              icon={getValidationIcon(validationResult.is_valid)}
            >
              <Typography variant="subtitle2" gutterBottom>
                Password Validation Result
              </Typography>
              <Typography variant="body2">
                {validationResult.is_valid 
                  ? 'Password meets all security requirements!' 
                  : 'Password does not meet security requirements.'
                }
              </Typography>
            </Alert>
          )}

          {/* Error details */}
          {validationResult && validationResult.errors && validationResult.errors.length > 0 && (
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle2" gutterBottom color="error">
                  Issues Found:
                </Typography>
                <List dense>
                  {validationResult.errors.map((error, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Cancel color="error" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={error}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Password strength indicator */}
          {password && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Password Strength Analysis:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                <Chip
                  label={`Length: ${password.length}`}
                  size="small"
                  color={password.length >= 8 ? 'success' : 'error'}
                  variant={password.length >= 8 ? 'filled' : 'outlined'}
                />
                <Chip
                  label="Uppercase"
                  size="small"
                  color={/[A-Z]/.test(password) ? 'success' : 'error'}
                  variant={/[A-Z]/.test(password) ? 'filled' : 'outlined'}
                />
                <Chip
                  label="Lowercase"
                  size="small"
                  color={/[a-z]/.test(password) ? 'success' : 'error'}
                  variant={/[a-z]/.test(password) ? 'filled' : 'outlined'}
                />
                <Chip
                  label="Numbers"
                  size="small"
                  color={/[0-9]/.test(password) ? 'success' : 'error'}
                  variant={/[0-9]/.test(password) ? 'filled' : 'outlined'}
                />
                <Chip
                  label="Special"
                  size="small"
                  color={/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password) ? 'success' : 'error'}
                  variant={/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password) ? 'filled' : 'outlined'}
                />
              </Box>
            </Box>
          )}

          {/* Tips */}
          <Alert severity="info">
            <Typography variant="subtitle2" gutterBottom>
              Password Tips:
            </Typography>
            <Typography variant="body2" component="div">
              • Use at least 8 characters<br/>
              • Include uppercase and lowercase letters<br/>
              • Include numbers and special characters<br/>
              • Avoid common words and patterns<br/>
              • Don't include your username
            </Typography>
          </Alert>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PasswordPolicyTester;

