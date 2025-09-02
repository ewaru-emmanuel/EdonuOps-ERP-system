import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Container, Button, Card, CardContent, Grid,
  Stepper, Step, StepLabel, Chip, Alert, Paper, useTheme,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  FormControl, InputLabel, Select, MenuItem, Checkbox, FormControlLabel,
  RadioGroup, Radio, List, ListItem, ListItemText, ListItemIcon,
  Divider, LinearProgress, IconButton, Tooltip
} from '@mui/material';
import {
  Business, Rocket, Settings, Analytics, Inventory, 
  AccountBalance, People, Assessment, SkipNext, ArrowForward,
  CheckCircle, Info, Warning, TrendingUp, Speed, Security
} from '@mui/icons-material';
import uiLanguageService from '../services/UILanguageService';
import apiClient from '../services/apiClient';

const OnboardingHub = ({ onComplete, onSkip }) => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [discoveryData, setDiscoveryData] = useState({
    industry: 'retail',
    business_size: 'small',
    pain_points: [],
    goals: []
  });
  const [analysis, setAnalysis] = useState(null);
  const [selectedModules, setSelectedModules] = useState([]);
  const [showQuickStart, setShowQuickStart] = useState(false);

  const steps = [
    'Business Discovery',
    'Module Configuration',
    'Setup & Launch'
  ];

  // Industry options
  const industries = [
    { value: 'retail', label: 'Retail & E-commerce', icon: <Business /> },
    { value: 'manufacturing', label: 'Manufacturing', icon: <Inventory /> },
    { value: 'wholesale', label: 'Wholesale & Distribution', icon: <Analytics /> },
    { value: 'services', label: 'Professional Services', icon: <People /> },
    { value: 'healthcare', label: 'Healthcare & Medical', icon: <Security /> }
  ];

  // Business sizes
  const businessSizes = [
    { value: 'startup', label: 'Startup (1-10 employees)', time: '10 minutes' },
    { value: 'small', label: 'Small Business (11-50 employees)', time: '15 minutes' },
    { value: 'medium', label: 'Growing Business (51-200 employees)', time: '20 minutes' },
    { value: 'enterprise', label: 'Enterprise (200+ employees)', time: 'Contact Sales' }
  ];

  // Pain points
  const painPoints = [
    { value: 'inventory_issues', label: 'Lost items, stockouts, overstock' },
    { value: 'financial_chaos', label: 'Manual bookkeeping, cash flow issues' },
    { value: 'customer_loss', label: 'Poor customer service, lost sales' },
    { value: 'team_management', label: 'Payroll issues, performance tracking' },
    { value: 'data_insights', label: 'No visibility into business performance' },
    { value: 'production_issues', label: 'Quality problems, production delays' }
  ];

  // Business goals
  const businessGoals = [
    { value: 'grow_revenue', label: 'Increase revenue and profitability' },
    { value: 'improve_efficiency', label: 'Streamline operations and reduce costs' },
    { value: 'scale_business', label: 'Scale operations and expand' },
    { value: 'customer_satisfaction', label: 'Improve customer experience' },
    { value: 'team_productivity', label: 'Boost team productivity and morale' }
  ];

  // Available modules with dynamic language
  const getAvailableModules = () => {
    const labels = uiLanguageService.getFormLabels();
    const features = uiLanguageService.getFeatureNames();
    
    return [
      { 
        id: 'inventory', 
        name: features.inventory, 
        icon: <Inventory />, 
        description: `Track stock, manage ${labels.location.toLowerCase()}, optimize supply chain` 
      },
      { 
        id: 'finance', 
        name: 'Financial Management', 
        icon: <AccountBalance />, 
        description: 'Accounting, multi-currency, AI-powered insights' 
      },
      { 
        id: 'crm', 
        name: 'Customer Relationship', 
        icon: <People />, 
        description: 'Sales, marketing, customer service automation' 
      },
      { 
        id: 'hr', 
        name: 'Human Resources', 
        icon: <People />, 
        description: 'Payroll, performance, recruitment management' 
      },
      { 
        id: 'analytics', 
        name: 'Business Intelligence', 
        icon: <Analytics />, 
        description: 'Advanced reporting, dashboards, AI insights' 
      },
      { 
        id: 'manufacturing', 
        name: 'Manufacturing', 
        icon: <Inventory />, 
        description: 'Production planning, quality control, workflow' 
      }
    ];
  };

  const handleNext = () => {
    if (activeStep === 0) {
      // Analyze business needs
      analyzeBusinessNeeds();
    } else if (activeStep === 1) {
      // Configure modules
      configureModules();
    } else {
      // Complete setup
      completeSetup();
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const analyzeBusinessNeeds = async () => {
    setLoading(true);
    try {
      const result = await apiClient.analyzeBusinessNeeds(discoveryData);
      setAnalysis(result.analysis);
      
      // Update UI language based on complexity level
      if (result.analysis && result.analysis.complexity) {
        uiLanguageService.setComplexityLevel(result.analysis.complexity);
      }
      
      setActiveStep(1);
    } catch (error) {
      console.error('Error analyzing business needs:', error);
    } finally {
      setLoading(false);
    }
  };

  const configureModules = async () => {
    setLoading(true);
    try {
      await apiClient.configureModules({
        modules: selectedModules,
        industry: discoveryData.industry,
        business_size: discoveryData.business_size
      });
      setActiveStep(2);
    } catch (error) {
      console.error('Error configuring modules:', error);
    } finally {
      setLoading(false);
    }
  };

  const completeSetup = () => {
    onComplete({
      discoveryData,
      selectedModules,
      analysis
    });
  };

  const handleQuickStart = async () => {
    setLoading(true);
    try {
      const result = await apiClient.quickStart({
        industry: discoveryData.industry,
        business_size: discoveryData.business_size
      });
      onComplete(result);
    } catch (error) {
      console.error('Error in quick start:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderBusinessDiscovery = () => (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Tell Us About Your Business
      </Typography>
      
      {/* Industry Selection */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            What industry are you in?
          </Typography>
          <Grid container spacing={2}>
            {industries.map((industry) => (
              <Grid item xs={12} sm={6} key={industry.value}>
                <Card 
                  variant={discoveryData.industry === industry.value ? 'elevation' : 'outlined'}
                  sx={{ 
                    cursor: 'pointer',
                    border: discoveryData.industry === industry.value ? `2px solid ${theme.palette.primary.main}` : '1px solid',
                    '&:hover': { borderColor: theme.palette.primary.main }
                  }}
                  onClick={() => setDiscoveryData({ ...discoveryData, industry: industry.value })}
                >
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <Box sx={{ mb: 1 }}>{industry.icon}</Box>
                    <Typography variant="body1" fontWeight="medium">
                      {industry.label}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Business Size */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            How large is your business?
          </Typography>
          <FormControl component="fieldset" fullWidth>
            <RadioGroup
              value={discoveryData.business_size}
              onChange={(e) => setDiscoveryData({ ...discoveryData, business_size: e.target.value })}
            >
              {businessSizes.map((size) => (
                <FormControlLabel
                  key={size.value}
                  value={size.value}
                  control={<Radio />}
                  label={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                      <Typography>{size.label}</Typography>
                      <Chip 
                        label={size.time} 
                        size="small" 
                        color={size.value === 'enterprise' ? 'warning' : 'primary'}
                      />
                    </Box>
                  }
                  sx={{ width: '100%', mb: 1 }}
                />
              ))}
            </RadioGroup>
          </FormControl>
        </CardContent>
      </Card>

      {/* Pain Points */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            What are your biggest challenges? (Select all that apply)
          </Typography>
          <Grid container spacing={2}>
            {painPoints.map((point) => (
              <Grid item xs={12} sm={6} key={point.value}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={discoveryData.pain_points.includes(point.value)}
                      onChange={(e) => {
                        const newPainPoints = e.target.checked
                          ? [...discoveryData.pain_points, point.value]
                          : discoveryData.pain_points.filter(p => p !== point.value);
                        setDiscoveryData({ ...discoveryData, pain_points: newPainPoints });
                      }}
                    />
                  }
                  label={point.label}
                />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Business Goals */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            What are your main business goals? (Select all that apply)
          </Typography>
          <Grid container spacing={2}>
            {businessGoals.map((goal) => (
              <Grid item xs={12} sm={6} key={goal.value}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={discoveryData.goals.includes(goal.value)}
                      onChange={(e) => {
                        const newGoals = e.target.checked
                          ? [...discoveryData.goals, goal.value]
                          : discoveryData.goals.filter(g => g !== goal.value);
                        setDiscoveryData({ ...discoveryData, goals: newGoals });
                      }}
                    />
                  }
                  label={goal.label}
                />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );

  const renderModuleConfiguration = () => (
    <Box>
      {analysis && (
        <>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
            Your Recommended Configuration
          </Typography>
          
          {/* Analysis Summary */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>Business Profile</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Industry: {analysis.industry.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Size: {analysis.business_size.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Complexity: {analysis.complexity}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>Expected Benefits</Typography>
                  <Typography variant="body2" color="text.secondary">
                    ROI: {analysis.estimated_roi.estimated_roi}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Payback: {analysis.estimated_roi.payback_period}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Efficiency: {analysis.estimated_roi.efficiency_gain}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Priority Issues */}
          {analysis.priority_issues.length > 0 && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom color="warning.main">
                  Priority Issues to Address
                </Typography>
                <List>
                  {analysis.priority_issues.map((issue, index) => (
                    <ListItem key={index}>
                      <ListItemIcon>
                        <Warning color="warning" />
                      </ListItemIcon>
                      <ListItemText
                        primary={issue.issue}
                        secondary={issue.solution}
                      />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          )}

          {/* Module Selection */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Select Modules for Your Business
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                We recommend: {analysis.recommended_modules.join(', ')}
              </Typography>
              
              <Grid container spacing={2}>
                {getAvailableModules().map((module) => (
                  <Grid item xs={12} sm={6} md={4} key={module.id}>
                    <Card 
                      variant={selectedModules.includes(module.id) ? 'elevation' : 'outlined'}
                      sx={{ 
                        cursor: 'pointer',
                        border: selectedModules.includes(module.id) ? `2px solid ${theme.palette.primary.main}` : '1px solid',
                        '&:hover': { borderColor: theme.palette.primary.main }
                      }}
                      onClick={() => {
                        const newModules = selectedModules.includes(module.id)
                          ? selectedModules.filter(m => m !== module.id)
                          : [...selectedModules, module.id];
                        setSelectedModules(newModules);
                      }}
                    >
                      <CardContent sx={{ textAlign: 'center', py: 2 }}>
                        <Box sx={{ mb: 1 }}>{module.icon}</Box>
                        <Typography variant="h6" gutterBottom>
                          {module.name}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {module.description}
                        </Typography>
                        {analysis.recommended_modules.includes(module.id) && (
                          <Chip 
                            label="Recommended" 
                            size="small" 
                            color="success" 
                            sx={{ mt: 1 }}
                          />
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );

  const renderSetupAndLaunch = () => (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Almost Ready! Let's Get You Started
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Your Configuration Summary
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Selected Modules: {selectedModules.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Setup Time: {analysis?.setup_time || '15-20 minutes'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Complexity: {analysis?.complexity || 'simple'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">
                Industry: {analysis?.industry?.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Business Size: {analysis?.business_size?.name}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Estimated ROI: {analysis?.estimated_roi?.estimated_roi}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          Your system will be configured with industry best practices. 
          You can customize settings and add more modules later as your business grows.
        </Typography>
      </Alert>

      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={<Rocket />}
          onClick={completeSetup}
          sx={{ minWidth: 200 }}
        >
          Launch My System
        </Button>
        
        <Button
          variant="outlined"
          size="large"
          startIcon={<Settings />}
          onClick={() => setShowQuickStart(true)}
          sx={{ minWidth: 200 }}
        >
          Customize Settings
        </Button>
      </Box>
    </Box>
  );

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderBusinessDiscovery();
      case 1:
        return renderModuleConfiguration();
      case 2:
        return renderSetupAndLaunch();
      default:
        return null;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
          🚀 Welcome to EdonuOps
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          Let's configure your business system in just a few minutes
        </Typography>
        
        {/* Quick Start Option */}
        <Box sx={{ mt: 3 }}>
          <Button
            variant="outlined"
            startIcon={<Speed />}
            onClick={() => setShowQuickStart(true)}
            sx={{ mr: 2 }}
          >
            Quick Start (5 min)
          </Button>
          
          <Button
            variant="text"
            startIcon={<SkipNext />}
            onClick={onSkip}
            color="text.secondary"
          >
            Skip Setup, Take Me to App
          </Button>
        </Box>
      </Box>

      {/* Progress Stepper */}
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {/* Loading Progress */}
      {loading && (
        <Box sx={{ mb: 3 }}>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
            Analyzing your business needs...
          </Typography>
        </Box>
      )}

      {/* Step Content */}
      <Box sx={{ mb: 4 }}>
        {renderStepContent()}
      </Box>

      {/* Navigation */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button
          disabled={activeStep === 0}
          onClick={handleBack}
          sx={{ minWidth: 120 }}
        >
          Back
        </Button>
        
        <Box>
          {activeStep < steps.length - 1 ? (
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={loading}
              endIcon={<ArrowForward />}
              sx={{ minWidth: 120 }}
            >
              {activeStep === 0 ? 'Analyze & Continue' : 'Next'}
            </Button>
          ) : null}
        </Box>
      </Box>

      {/* Quick Start Dialog */}
      <Dialog open={showQuickStart} onClose={() => setShowQuickStart(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          Quick Start Configuration
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Get started in just 5 minutes with a basic configuration tailored to your industry.
          </Typography>
          
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              You can always add more features and customize settings later as your business grows.
            </Typography>
          </Alert>
          
          <Typography variant="body2" color="text.secondary">
            Industry: {discoveryData.industry}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Business Size: {discoveryData.business_size}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowQuickStart(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={handleQuickStart}
            disabled={loading}
            startIcon={<Rocket />}
          >
            Start in 5 Minutes
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default OnboardingHub;
