import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Grid,
  Paper
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
  Security as SecurityIcon,
  Lock as LockIcon
} from '@mui/icons-material';

const PasswordPolicyTester = () => {
  const [password, setPassword] = useState('');
  const [policyResults, setPolicyResults] = useState([]);
  const [strength, setStrength] = useState(0);

  const passwordPolicies = [
    {
      name: 'Minimum Length',
      description: 'Password must be at least 8 characters long',
      test: (pwd) => pwd.length >= 8,
      weight: 1
    },
    {
      name: 'Uppercase Letter',
      description: 'Password must contain at least one uppercase letter',
      test: (pwd) => /[A-Z]/.test(pwd),
      weight: 1
    },
    {
      name: 'Lowercase Letter',
      description: 'Password must contain at least one lowercase letter',
      test: (pwd) => /[a-z]/.test(pwd),
      weight: 1
    },
    {
      name: 'Number',
      description: 'Password must contain at least one number',
      test: (pwd) => /\d/.test(pwd),
      weight: 1
    },
    {
      name: 'Special Character',
      description: 'Password must contain at least one special character',
      test: (pwd) => /[!@#$%^&*(),.?":{}|<>]/.test(pwd),
      weight: 1
    },
    {
      name: 'No Common Passwords',
      description: 'Password must not be a common password',
      test: (pwd) => {
        const commonPasswords = [
          'password', '123456', 'password123', 'admin', 'qwerty',
          'letmein', 'welcome', 'monkey', 'dragon', 'master',
          '123456789', 'abc123', 'password1', 'admin123'
        ];
        return !commonPasswords.includes(pwd.toLowerCase());
      },
      weight: 2
    },
    {
      name: 'No Sequential Characters',
      description: 'Password must not contain sequential characters',
      test: (pwd) => {
        const sequential = ['123', 'abc', 'qwe', 'asd', 'zxc'];
        return !sequential.some(seq => pwd.toLowerCase().includes(seq));
      },
      weight: 1
    },
    {
      name: 'No Repeated Characters',
      description: 'Password must not contain repeated characters',
      test: (pwd) => !/(.)\1{2,}/.test(pwd),
      weight: 1
    }
  ];

  const testPassword = (pwd) => {
    if (!pwd) {
      setPolicyResults([]);
      setStrength(0);
      return;
    }

    const results = passwordPolicies.map(policy => ({
      ...policy,
      passed: policy.test(pwd),
      score: policy.test(pwd) ? policy.weight : 0
    }));

    setPolicyResults(results);
    
    const totalScore = results.reduce((sum, result) => sum + result.score, 0);
    const maxScore = passwordPolicies.reduce((sum, policy) => sum + policy.weight, 0);
    const strengthPercentage = Math.round((totalScore / maxScore) * 100);
    setStrength(strengthPercentage);
  };

  const handlePasswordChange = (event) => {
    const newPassword = event.target.value;
    setPassword(newPassword);
    testPassword(newPassword);
  };

  const getStrengthColor = (strength) => {
    if (strength >= 80) return 'success';
    if (strength >= 60) return 'warning';
    return 'error';
  };

  const getStrengthLabel = (strength) => {
    if (strength >= 80) return 'Strong';
    if (strength >= 60) return 'Medium';
    if (strength >= 40) return 'Weak';
    return 'Very Weak';
  };

  const getPolicyIcon = (passed) => {
    return passed ? <CheckIcon color="success" /> : <CancelIcon color="error" />;
  };

  const getPolicyColor = (passed) => {
    return passed ? 'success' : 'error';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Password Policy Tester
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Test password strength and compliance with security policies.
      </Typography>

      <Grid container spacing={3}>
        {/* Password Input */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <LockIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Password Input
              </Typography>
              
              <TextField
                fullWidth
                label="Enter Password"
                type="password"
                value={password}
                onChange={handlePasswordChange}
                placeholder="Enter a password to test"
                sx={{ mb: 2 }}
              />
              
              {password && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Password Strength
                  </Typography>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Box sx={{ flexGrow: 1 }}>
                      <Box
                        sx={{
                          width: '100%',
                          height: 8,
                          backgroundColor: 'grey.300',
                          borderRadius: 1,
                          overflow: 'hidden'
                        }}
                      >
                        <Box
                          sx={{
                            width: `${strength}%`,
                            height: '100%',
                            backgroundColor: getStrengthColor(strength) === 'success' ? 'success.main' :
                                           getStrengthColor(strength) === 'warning' ? 'warning.main' : 'error.main',
                            transition: 'width 0.3s ease'
                          }}
                        />
                      </Box>
                    </Box>
                    
                    <Chip
                      label={`${strength}% - ${getStrengthLabel(strength)}`}
                      color={getStrengthColor(strength)}
                      size="small"
                    />
                  </Box>
                  
                  {strength >= 80 && (
                    <Alert severity="success" sx={{ mb: 2 }}>
                      <SecurityIcon sx={{ mr: 1 }} />
                      Password meets security requirements!
                    </Alert>
                  )}
                  
                  {strength < 80 && password && (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      Password needs improvement to meet security standards.
                    </Alert>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Policy Results */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Policy Compliance
              </Typography>
              
              {policyResults.length === 0 ? (
                <Typography color="text.secondary">
                  Enter a password to see policy compliance results.
                </Typography>
              ) : (
                <List dense>
                  {policyResults.map((policy, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        {getPolicyIcon(policy.passed)}
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">
                              {policy.name}
                            </Typography>
                            <Chip
                              label={policy.passed ? 'PASS' : 'FAIL'}
                              color={getPolicyColor(policy.passed)}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={policy.description}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Security Recommendations */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Security Recommendations
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, backgroundColor: 'success.50' }}>
                    <Typography variant="subtitle2" color="success.main" gutterBottom>
                      ✅ Best Practices
                    </Typography>
                    <List dense>
                      <ListItem sx={{ py: 0 }}>
                        <ListItemText 
                          primary="Use a mix of uppercase and lowercase letters"
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                      <ListItem sx={{ py: 0 }}>
                        <ListItemText 
                          primary="Include numbers and special characters"
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                      <ListItem sx={{ py: 0 }}>
                        <ListItemText 
                          primary="Make it at least 12 characters long"
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                      <ListItem sx={{ py: 0 }}>
                        <ListItemText 
                          primary="Use a unique password for each account"
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    </List>
                  </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Paper sx={{ p: 2, backgroundColor: 'error.50' }}>
                    <Typography variant="subtitle2" color="error.main" gutterBottom>
                      ❌ Avoid These
                    </Typography>
                    <List dense>
                      <ListItem sx={{ py: 0 }}>
                        <ListItemText 
                          primary="Don't use personal information"
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                      <ListItem sx={{ py: 0 }}>
                        <ListItemText 
                          primary="Avoid common words and patterns"
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                      <ListItem sx={{ py: 0 }}>
                        <ListItemText 
                          primary="Don't reuse passwords across accounts"
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                      <ListItem sx={{ py: 0 }}>
                        <ListItemText 
                          primary="Avoid keyboard patterns (qwerty, 123456)"
                          primaryTypographyProps={{ variant: 'body2' }}
                        />
                      </ListItem>
                    </List>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Test Examples */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Test Examples
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => setPassword('password123')}
                    sx={{ mb: 1 }}
                  >
                    Weak Password
                  </Button>
                  <Typography variant="caption" color="text.secondary">
                    Common password with numbers
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => setPassword('MyPass123!')}
                    sx={{ mb: 1 }}
                  >
                    Medium Password
                  </Button>
                  <Typography variant="caption" color="text.secondary">
                    Mixed case with special chars
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => setPassword('SecureP@ssw0rd2023!')}
                    sx={{ mb: 1 }}
                  >
                    Strong Password
                  </Button>
                  <Typography variant="caption" color="text.secondary">
                    Complex with all requirements
                  </Typography>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => setPassword('')}
                    sx={{ mb: 1 }}
                  >
                    Clear
                  </Button>
                  <Typography variant="caption" color="text.secondary">
                    Clear password field
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PasswordPolicyTester;




