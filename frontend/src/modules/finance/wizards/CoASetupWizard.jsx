import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stepper,
  Step,
  StepLabel,
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Checkbox,
  FormControlLabel,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Business as BusinessIcon,
  Factory as FactoryIcon,
  Computer as TechIcon,
  MedicalServices as HealthIcon,
  School as EducationIcon,
  Restaurant as RestaurantIcon,
  Construction as ConstructionIcon,
  LocalShipping as LogisticsIcon,
  AccountBalance as FinanceIcon,
  Storefront as RetailIcon,
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  DragIndicator as DragIcon,
  Psychology as AIIcon,
  Timeline as AnalyticsIcon,
  ImportExport as ImportIcon,
  CheckCircle as CheckIcon,
  Lightbulb as LightbulbIcon
} from '@mui/icons-material';

const CoASetupWizard = ({ open, onClose, onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [setupData, setSetupData] = useState({
    businessType: '',
    industry: '',
    template: 'blank',
    customAccounts: [],
    selectedAccounts: new Set(),
    aiSuggestions: true,
    importData: null
  });
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [previewAccounts, setPreviewAccounts] = useState([]);

  const steps = [
    'Business Profile',
    'Template Selection', 
    'Account Customization',
    'AI Enhancement',
    'Review & Deploy'
  ];

  // Industry templates with icons and descriptions
  const industryTemplates = [
    {
      id: 'blank',
      name: 'Start from Scratch',
      icon: <AddIcon />,
      description: 'Build your CoA from the ground up with full flexibility',
      accounts: 0,
      color: '#6B7280'
    },
    {
      id: 'manufacturing',
      name: 'Manufacturing',
      icon: <FactoryIcon />,
      description: 'Work-in-progress, raw materials, finished goods tracking',
      accounts: 156,
      color: '#EF4444',
      features: ['Inventory Tracking', 'Cost Centers', 'WIP Accounts']
    },
    {
      id: 'technology',
      name: 'Technology/SaaS',
      icon: <TechIcon />,
      description: 'R&D, subscription revenue, cloud infrastructure costs',
      accounts: 142,
      color: '#3B82F6',
      features: ['ARR Tracking', 'R&D Capitalization', 'Cloud Cost Centers']
    },
    {
      id: 'healthcare',
      name: 'Healthcare',
      icon: <HealthIcon />,
      description: 'Patient billing, insurance, medical equipment depreciation',
      accounts: 178,
      color: '#10B981',
      features: ['Insurance Billing', 'Equipment Tracking', 'Patient Revenue']
    },
    {
      id: 'retail',
      name: 'Retail/E-commerce',
      icon: <RetailIcon />,
      description: 'Inventory, POS systems, customer loyalty programs',
      accounts: 134,
      color: '#F59E0B',
      features: ['Multi-location', 'Inventory Valuation', 'Customer Analytics']
    },
    {
      id: 'construction',
      name: 'Construction',
      icon: <ConstructionIcon />,
      description: 'Project-based accounting, equipment, subcontractor costs',
      accounts: 167,
      color: '#8B5CF6',
      features: ['Project Costing', 'Equipment Depreciation', 'Job Progress']
    },
    {
      id: 'finance',
      name: 'Financial Services',
      icon: <FinanceIcon />,
      description: 'Regulatory compliance, loan tracking, fee income',
      accounts: 203,
      color: '#EC4899',
      features: ['Regulatory Ready', 'Risk Management', 'Fee Tracking']
    }
  ];

  // AI-powered account suggestions
  const aiSuggestions = [
    {
      account: 'Digital Marketing Expenses',
      reason: 'Based on your industry, most companies track digital marketing separately',
      confidence: 95,
      category: 'Expenses'
    },
    {
      account: 'Subscription Software',
      reason: 'Tech companies typically have significant SaaS tool expenses',
      confidence: 88,
      category: 'Expenses'
    },
    {
      account: 'Customer Acquisition Costs',
      reason: 'Essential for tracking marketing ROI and customer lifetime value',
      confidence: 92,
      category: 'Expenses'
    }
  ];

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleTemplateSelect = (templateId) => {
    setSetupData(prev => ({ ...prev, template: templateId }));
    // Load template accounts for preview
    loadTemplatePreview(templateId);
  };

  const loadTemplatePreview = async (templateId) => {
    if (templateId === 'blank') {
      setPreviewAccounts([]);
      return;
    }
    
    setLoading(true);
    try {
      // Simulate API call to get template accounts
      const response = await fetch(`/finance/coa/templates/${templateId}`);
      const data = await response.json();
      setPreviewAccounts(data.accounts || []);
    } catch (error) {
      console.error('Failed to load template preview:', error);
      setPreviewAccounts([]);
    }
    setLoading(false);
  };

  const renderBusinessProfile = () => (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Tell us about your business
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Business Type</InputLabel>
            <Select
              value={setupData.businessType}
              onChange={(e) => setSetupData(prev => ({ ...prev, businessType: e.target.value }))}
            >
              <MenuItem value="startup">Startup</MenuItem>
              <MenuItem value="small_business">Small Business</MenuItem>
              <MenuItem value="medium_enterprise">Medium Enterprise</MenuItem>
              <MenuItem value="large_corporation">Large Corporation</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Annual Revenue (USD)"
            placeholder="e.g., 1,000,000"
            value={setupData.revenue}
            onChange={(e) => setSetupData(prev => ({ ...prev, revenue: e.target.value }))}
          />
        </Grid>
        <Grid item xs={12}>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Business Description"
            placeholder="Briefly describe what your business does..."
            value={setupData.description}
            onChange={(e) => setSetupData(prev => ({ ...prev, description: e.target.value }))}
          />
        </Grid>
      </Grid>
    </Box>
  );

  const renderTemplateSelection = () => (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Choose Your Starting Point
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Select an industry template or start from scratch. You can customize everything later.
      </Typography>
      
      <Grid container spacing={2}>
        {industryTemplates.map((template) => (
          <Grid item xs={12} md={6} lg={4} key={template.id}>
            <Card
              sx={{
                cursor: 'pointer',
                border: setupData.template === template.id ? 2 : 1,
                borderColor: setupData.template === template.id ? 'primary.main' : 'divider',
                '&:hover': { borderColor: 'primary.main' }
              }}
              onClick={() => handleTemplateSelect(template.id)}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ color: template.color, mr: 1 }}>
                    {template.icon}
                  </Box>
                  <Typography variant="h6">{template.name}</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {template.description}
                </Typography>
                {template.accounts > 0 && (
                  <Chip
                    size="small"
                    label={`${template.accounts} accounts`}
                    color="primary"
                    variant="outlined"
                  />
                )}
                {template.features && (
                  <Box sx={{ mt: 1 }}>
                    {template.features.map((feature, index) => (
                      <Chip
                        key={index}
                        size="small"
                        label={feature}
                        sx={{ mr: 0.5, mb: 0.5 }}
                        variant="outlined"
                      />
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {setupData.template !== 'blank' && previewAccounts.length > 0 && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Template Preview
          </Typography>
          <Card sx={{ maxHeight: 300, overflow: 'auto' }}>
            <List dense>
              {previewAccounts.slice(0, 10).map((account, index) => (
                <ListItem key={index}>
                  <ListItemText
                    primary={account.name}
                    secondary={account.type}
                  />
                  <Chip size="small" label={account.category} />
                </ListItem>
              ))}
              {previewAccounts.length > 10 && (
                <ListItem>
                  <ListItemText primary={`... and ${previewAccounts.length - 10} more accounts`} />
                </ListItem>
              )}
            </List>
          </Card>
        </Box>
      )}
    </Box>
  );

  const renderCustomization = () => (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Customize Your Chart of Accounts
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Add, remove, or modify accounts to fit your specific needs.
      </Typography>

      <Tabs value={0} sx={{ mb: 2 }}>
        <Tab label="Suggested Accounts" />
        <Tab label="Custom Accounts" />
        <Tab label="Import Data" />
      </Tabs>

      <Alert severity="info" sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <LightbulbIcon sx={{ mr: 1 }} />
          Pro Tip: You can always add or modify accounts later. Start with the essentials.
        </Box>
      </Alert>

      {/* Account categories */}
      <Box>
        {['Assets', 'Liabilities', 'Equity', 'Revenue', 'Expenses'].map((category) => (
          <Accordion key={category}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">{category}</Typography>
              <Chip size="small" label="12 accounts" sx={{ ml: 1 }} />
            </AccordionSummary>
            <AccordionDetails>
              <List dense>
                {/* Sample accounts - would be dynamic */}
                <ListItem>
                  <ListItemIcon>
                    <Checkbox />
                  </ListItemIcon>
                  <ListItemText
                    primary="Cash and Cash Equivalents"
                    secondary="1000 - Current Assets"
                  />
                  <ListItemSecondaryAction>
                    <IconButton size="small">
                      <EditIcon />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              </List>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    </Box>
  );

  const renderAIEnhancement = () => (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        AI-Powered Enhancements
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Let our AI analyze your business and suggest additional accounts and optimizations.
      </Typography>

      <FormControlLabel
        control={
          <Checkbox
            checked={setupData.aiSuggestions}
            onChange={(e) => setSetupData(prev => ({ ...prev, aiSuggestions: e.target.checked }))}
          />
        }
        label="Enable AI-powered account suggestions and analytics"
      />

      {setupData.aiSuggestions && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="subtitle1" gutterBottom>
            AI Suggestions for Your Business
          </Typography>
          {aiSuggestions.map((suggestion, index) => (
            <Card key={index} sx={{ mb: 2 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="subtitle2">{suggestion.account}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {suggestion.reason}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                      <Chip size="small" label={suggestion.category} />
                      <Box sx={{ ml: 2, display: 'flex', alignItems: 'center' }}>
                        <AIIcon sx={{ fontSize: 16, mr: 0.5 }} />
                        <Typography variant="caption">
                          {suggestion.confidence}% confidence
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                  <Button size="small" variant="outlined">
                    Add Account
                  </Button>
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}
    </Box>
  );

  const renderReview = () => (
    <Box sx={{ py: 2 }}>
      <Typography variant="h6" gutterBottom>
        Review & Deploy
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Review your Chart of Accounts setup before deployment.
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                Setup Summary
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText primary="Template" secondary={setupData.template} />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Total Accounts" secondary="127 accounts" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="AI Enhancements" secondary={setupData.aiSuggestions ? 'Enabled' : 'Disabled'} />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" gutterBottom>
                What's Next?
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemIcon><CheckIcon color="success" /></ListItemIcon>
                  <ListItemText primary="Create Chart of Accounts" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><AnalyticsIcon /></ListItemIcon>
                  <ListItemText primary="Set up analytics and reporting" />
                </ListItem>
                <ListItem>
                  <ListItemIcon><ImportIcon /></ListItemIcon>
                  <ListItemText primary="Import existing data (optional)" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return renderBusinessProfile();
      case 1:
        return renderTemplateSelection();
      case 2:
        return renderCustomization();
      case 3:
        return renderAIEnhancement();
      case 4:
        return renderReview();
      default:
        return 'Unknown step';
    }
  };

  const handleComplete = async () => {
    setLoading(true);
    try {
      // Deploy the Chart of Accounts
      await onComplete(setupData);
      onClose();
    } catch (error) {
      console.error('Failed to deploy CoA:', error);
    }
    setLoading(false);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        EdonuOps Chart of Accounts Setup
        <Typography variant="body2" color="text.secondary">
          Build a world-class Chart of Accounts in minutes
        </Typography>
      </DialogTitle>
      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {loading && <LinearProgress sx={{ mb: 2 }} />}

        {getStepContent(activeStep)}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button disabled={activeStep === 0} onClick={handleBack}>
          Back
        </Button>
        {activeStep === steps.length - 1 ? (
          <Button variant="contained" onClick={handleComplete} disabled={loading}>
            Deploy Chart of Accounts
          </Button>
        ) : (
          <Button variant="contained" onClick={handleNext}>
            Next
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CoASetupWizard;

