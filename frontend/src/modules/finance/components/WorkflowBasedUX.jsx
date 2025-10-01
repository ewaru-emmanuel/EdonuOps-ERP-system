import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Receipt as ReceiptIcon,
  ShoppingCart as ShoppingCartIcon,
  Payment as PaymentIcon,
  Inventory as InventoryIcon,
  TrendingUp as TrendingUpIcon,
  Business as BusinessIcon,
  Person as PersonIcon,
  AttachMoney as MoneyIcon,
  Info as InfoIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';

const WorkflowBasedUX = ({ onWorkflowComplete, accounts = [] }) => {
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [workflowData, setWorkflowData] = useState({});
  const [activeStep, setActiveStep] = useState(0);
  const [showWorkflowDialog, setShowWorkflowDialog] = useState(false);

  const workflows = [
    {
      id: 'record_sale',
      name: 'Record Sale',
      description: 'Process a customer sale with inventory',
      icon: <ShoppingCartIcon />,
      color: 'success',
      steps: [
        { label: 'Customer Details', fields: ['customer', 'date', 'reference'] },
        { label: 'Products Sold', fields: ['products', 'quantities', 'prices'] },
        { label: 'Payment Terms', fields: ['payment_method', 'due_date'] },
        { label: 'Review & Post', fields: ['review', 'confirm'] }
      ],
      accounts: ['4000', '5000', '1210', '1100'] // Sales Revenue, COGS, Inventory, AR
    },
    {
      id: 'purchase_inventory',
      name: 'Purchase Inventory',
      description: 'Record inventory purchase from vendor',
      icon: <InventoryIcon />,
      color: 'primary',
      steps: [
        { label: 'Vendor Details', fields: ['vendor', 'invoice_number', 'date'] },
        { label: 'Items Purchased', fields: ['items', 'quantities', 'costs'] },
        { label: 'Payment Terms', fields: ['payment_terms', 'due_date'] },
        { label: 'Review & Post', fields: ['review', 'confirm'] }
      ],
      accounts: ['1210', '2000'] // Inventory, Accounts Payable
    },
    {
      id: 'receive_payment',
      name: 'Receive Payment',
      description: 'Record customer payment received',
      icon: <PaymentIcon />,
      color: 'info',
      steps: [
        { label: 'Payment Details', fields: ['customer', 'amount', 'payment_method', 'bank_account'] },
        { label: 'Apply to Invoices', fields: ['invoices', 'amounts'] },
        { label: 'Review & Post', fields: ['review', 'confirm'] }
      ],
      accounts: ['1020', '1100'] // Cash, Accounts Receivable
    },
    {
      id: 'record_expense',
      name: 'Record Expense',
      description: 'Record business expense',
      icon: <ReceiptIcon />,
      color: 'warning',
      steps: [
        { label: 'Expense Details', fields: ['vendor', 'amount', 'category', 'date'] },
        { label: 'Payment Method', fields: ['payment_method', 'bank_account', 'reference'] },
        { label: 'Review & Post', fields: ['review', 'confirm'] }
      ],
      accounts: ['6000', '2000'] // Operating Expenses, Accounts Payable
    },
    {
      id: 'pay_vendor',
      name: 'Pay Vendor',
      description: 'Pay outstanding vendor invoice',
      icon: <MoneyIcon />,
      color: 'error',
      steps: [
        { label: 'Select Invoice', fields: ['vendor', 'invoice', 'amount'] },
        { label: 'Payment Method', fields: ['payment_method', 'bank_account', 'reference'] },
        { label: 'Review & Post', fields: ['review', 'confirm'] }
      ],
      accounts: ['2000', '1020'] // Accounts Payable, Cash
    }
  ];

  const handleWorkflowSelect = (workflow) => {
    setSelectedWorkflow(workflow);
    setWorkflowData({});
    setActiveStep(0);
    setShowWorkflowDialog(true);
  };

  const handleNext = () => {
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleComplete = () => {
    // Here you would process the workflow data and create journal entries
    onWorkflowComplete?.(selectedWorkflow.id, workflowData);
    setShowWorkflowDialog(false);
    setSelectedWorkflow(null);
    setWorkflowData({});
    setActiveStep(0);
  };

  const renderWorkflowCard = (workflow) => (
    <Card 
      key={workflow.id}
      sx={{ 
        height: '100%',
        cursor: 'pointer',
        transition: 'all 0.2s',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4
        }
      }}
      onClick={() => handleWorkflowSelect(workflow)}
    >
      <CardContent sx={{ textAlign: 'center', p: 3 }}>
        <Box sx={{ color: `${workflow.color}.main`, mb: 2 }}>
          {workflow.icon}
        </Box>
        <Typography variant="h6" gutterBottom>
          {workflow.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          {workflow.description}
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, flexWrap: 'wrap' }}>
          {workflow.accounts.map(accountCode => {
            const account = accounts.find(acc => acc.code === accountCode);
            return (
              <Chip
                key={accountCode}
                label={account?.name || accountCode}
                size="small"
                variant="outlined"
                color={workflow.color}
              />
            );
          })}
        </Box>
      </CardContent>
    </Card>
  );

  const renderWorkflowStep = () => {
    if (!selectedWorkflow) return null;

    const currentStep = selectedWorkflow.steps[activeStep];
    
    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          {currentStep.label}
        </Typography>
        
        {currentStep.fields.map(field => (
          <TextField
            key={field}
            fullWidth
            label={field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            value={workflowData[field] || ''}
            onChange={(e) => setWorkflowData(prev => ({
              ...prev,
              [field]: e.target.value
            }))}
            sx={{ mb: 2 }}
            variant="outlined"
          />
        ))}
      </Box>
    );
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Business Workflows
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Instead of thinking about accounts, think about what you want to do. 
          We'll handle the accounting behind the scenes.
        </Typography>
      </Box>

      {/* Workflow Cards */}
      <Grid container spacing={3}>
        {workflows.map(workflow => (
          <Grid item xs={12} sm={6} md={4} key={workflow.id}>
            {renderWorkflowCard(workflow)}
          </Grid>
        ))}
      </Grid>

      {/* Quick Actions */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quick Actions
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Card sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <TrendingUpIcon color="success" />
                <Box>
                  <Typography variant="subtitle1">View Dashboard</Typography>
                  <Typography variant="body2" color="text.secondary">
                    See your business performance at a glance
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6}>
            <Card sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <BusinessIcon color="primary" />
                <Box>
                  <Typography variant="subtitle1">Manage Customers</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Add and manage your customer information
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Workflow Dialog */}
      <Dialog 
        open={showWorkflowDialog} 
        onClose={() => setShowWorkflowDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {selectedWorkflow?.icon}
            {selectedWorkflow?.name}
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            {selectedWorkflow?.description}
          </Typography>

          {/* Stepper */}
          <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
            {selectedWorkflow?.steps.map((step, index) => (
              <Step key={step.label}>
                <StepLabel>{step.label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Step Content */}
          {renderWorkflowStep()}

          {/* Accounts Affected Preview */}
          <Alert severity="info" sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              This will affect the following accounts:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {selectedWorkflow?.accounts.map(accountCode => {
                const account = accounts.find(acc => acc.code === accountCode);
                return (
                  <Chip
                    key={accountCode}
                    label={`${accountCode} - ${account?.name || 'Unknown'}`}
                    size="small"
                    variant="outlined"
                  />
                );
              })}
            </Box>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowWorkflowDialog(false)}>
            Cancel
          </Button>
          <Button onClick={handleBack} disabled={activeStep === 0}>
            Back
          </Button>
          <Button 
            onClick={activeStep === selectedWorkflow?.steps.length - 1 ? handleComplete : handleNext}
            variant="contained"
          >
            {activeStep === selectedWorkflow?.steps.length - 1 ? 'Complete' : 'Next'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkflowBasedUX;

