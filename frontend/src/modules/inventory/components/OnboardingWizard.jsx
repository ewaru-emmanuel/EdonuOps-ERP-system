import React, { useState } from 'react';
import {
  Box, Typography, Stepper, Step, StepLabel, Button, Card, CardContent,
  FormControl, FormControlLabel, Radio, RadioGroup, TextField, Select,
  MenuItem, InputLabel, Alert, Chip, Grid, Paper, useTheme
} from '@mui/material';
import {
  Store, Warehouse, Business, TrendingUp, Settings,
  CheckCircle, ArrowForward, ArrowBack
} from '@mui/icons-material';
import apiClient from '../../../services/apiClient';

const OnboardingWizard = ({ onComplete, onCancel }) => {
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [formData, setFormData] = useState({
    business_type: 'retail',
    inventory_size: 'small',
    warehouse_count: 1,
    location_needs: 'none',
    business_name: '',
    industry: 'retail'
  });

  const steps = [
    'Business Type',
    'Inventory Size',
    'Location Needs',
    'Review & Setup'
  ];

  const businessTypes = [
    { value: 'retail', label: 'Retail Store', icon: <Store />, description: 'Brick-and-mortar or online retail' },
    { value: 'wholesale', label: 'Wholesale', icon: <Warehouse />, description: 'B2B distribution and wholesale' },
    { value: 'manufacturing', label: 'Manufacturing', icon: <Business />, description: 'Production and manufacturing' },
    { value: 'ecommerce', label: 'E-commerce', icon: <TrendingUp />, description: 'Online-only business' }
  ];

  const inventorySizes = [
    { value: 'small', label: 'Small (< 1,000 items)', description: 'Boutique, small shop, startup' },
    { value: 'medium', label: 'Medium (1,000 - 10,000 items)', description: 'Growing business, multiple locations' },
    { value: 'large', label: 'Large (10,000+ items)', description: 'Enterprise, distribution center' }
  ];

  const locationNeeds = [
    { 
      value: 'none', 
      label: 'Simple Inventory Tracking', 
      description: 'Just track what you have per warehouse',
      tier: 1,
      features: ['Basic product management', 'Stock level monitoring', 'Simple reports']
    },
    { 
      value: 'basic', 
      label: 'Basic Location Management', 
      description: 'Organize items in specific areas (shelves, aisles)',
      tier: 2,
      features: ['Location-based tracking', 'Basic operations', 'Enhanced reports']
    },
    { 
      value: 'advanced', 
      label: 'Advanced Warehouse Management', 
      description: 'Full warehouse optimization with mobile WMS',
      tier: 3,
      features: ['Full warehouse hierarchy', 'Mobile WMS', 'Advanced analytics', 'Barcode scanning']
    }
  ];

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = async () => {
    try {
      const result = await apiClient.setupInventoryComplexity(formData);
      onComplete(result);
    } catch (error) {
      console.error('Error during setup:', error);
    }
  };

  const renderBusinessTypeStep = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        What type of business are you?
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        This helps us configure the system for your specific needs.
      </Typography>
      
      <FormControl component="fieldset" fullWidth>
        <RadioGroup
          value={formData.business_type}
          onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
        >
          {businessTypes.map((type) => (
            <Card key={type.value} sx={{ mb: 2, cursor: 'pointer' }}>
              <CardContent>
                <FormControlLabel
                  value={type.value}
                  control={<Radio />}
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      {type.icon}
                      <Box>
                        <Typography variant="h6">{type.label}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {type.description}
                        </Typography>
                      </Box>
                    </Box>
                  }
                  sx={{ width: '100%', m: 0 }}
                />
              </CardContent>
            </Card>
          ))}
        </RadioGroup>
      </FormControl>
    </Box>
  );

  const renderInventorySizeStep = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        How large is your inventory?
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        This helps us optimize performance for your scale.
      </Typography>
      
      <FormControl component="fieldset" fullWidth>
        <RadioGroup
          value={formData.inventory_size}
          onChange={(e) => setFormData({ ...formData, inventory_size: e.target.value })}
        >
          {inventorySizes.map((size) => (
            <Card key={size.value} sx={{ mb: 2, cursor: 'pointer' }}>
              <CardContent>
                <FormControlLabel
                  value={size.value}
                  control={<Radio />}
                  label={
                    <Box>
                      <Typography variant="h6">{size.label}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {size.description}
                      </Typography>
                    </Box>
                  }
                  sx={{ width: '100%', m: 0 }}
                />
              </CardContent>
            </Card>
          ))}
        </RadioGroup>
      </FormControl>
      
      <Box sx={{ mt: 3 }}>
        <FormControl fullWidth>
          <InputLabel>Number of Warehouses/Locations</InputLabel>
          <Select
            value={formData.warehouse_count}
            onChange={(e) => setFormData({ ...formData, warehouse_count: e.target.value })}
            label="Number of Warehouses/Locations"
          >
            <MenuItem value={1}>1 Location</MenuItem>
            <MenuItem value={2}>2 Locations</MenuItem>
            <MenuItem value={3}>3 Locations</MenuItem>
            <MenuItem value={4}>4+ Locations</MenuItem>
          </Select>
        </FormControl>
      </Box>
    </Box>
  );

  const renderLocationNeedsStep = () => (
    <Box>
      <Typography variant="h5" gutterBottom>
        How do you manage your physical inventory?
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Choose the level of detail you need for location tracking.
      </Typography>
      
      <FormControl component="fieldset" fullWidth>
        <RadioGroup
          value={formData.location_needs}
          onChange={(e) => setFormData({ ...formData, location_needs: e.target.value })}
        >
          {locationNeeds.map((need) => (
            <Card key={need.value} sx={{ mb: 2, cursor: 'pointer' }}>
              <CardContent>
                <FormControlLabel
                  value={need.value}
                  control={<Radio />}
                  label={
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <Typography variant="h6">{need.label}</Typography>
                        <Chip 
                          label={`Tier ${need.tier}`} 
                          size="small" 
                          color={need.tier === 1 ? 'primary' : need.tier === 2 ? 'secondary' : 'success'}
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {need.description}
                      </Typography>
                      <Box>
                        {need.features.map((feature, index) => (
                          <Chip
                            key={index}
                            label={feature}
                            size="small"
                            variant="outlined"
                            sx={{ mr: 1, mb: 1 }}
                          />
                        ))}
                      </Box>
                    </Box>
                  }
                  sx={{ width: '100%', m: 0 }}
                />
              </CardContent>
            </Card>
          ))}
        </RadioGroup>
      </FormControl>
    </Box>
  );

  const renderReviewStep = () => {
    const selectedLocationNeed = locationNeeds.find(n => n.value === formData.location_needs);
    const selectedBusinessType = businessTypes.find(b => b.value === formData.business_type);
    const selectedInventorySize = inventorySizes.find(s => s.value === formData.inventory_size);

    return (
      <Box>
        <Typography variant="h5" gutterBottom>
          Review Your Configuration
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Here's what we'll set up for you:
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Business Profile
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Business Type</Typography>
                <Typography variant="body1">{selectedBusinessType?.label}</Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Inventory Size</Typography>
                <Typography variant="body1">{selectedInventorySize?.label}</Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Locations</Typography>
                <Typography variant="body1">{formData.warehouse_count} location(s)</Typography>
              </Box>
            </Paper>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                System Configuration
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Complexity Tier</Typography>
                <Chip 
                  label={`Tier ${selectedLocationNeed?.tier}`} 
                  color={selectedLocationNeed?.tier === 1 ? 'primary' : selectedLocationNeed?.tier === 2 ? 'secondary' : 'success'}
                />
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Features</Typography>
                <Box sx={{ mt: 1 }}>
                  {selectedLocationNeed?.features.map((feature, index) => (
                    <Chip
                      key={index}
                      label={feature}
                      size="small"
                      variant="outlined"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              </Box>
            </Paper>
          </Grid>
        </Grid>
        
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body2">
            You can always upgrade to a higher tier later as your business grows. 
            Your data will seamlessly migrate to the new configuration.
          </Typography>
        </Alert>
      </Box>
    );
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderBusinessTypeStep();
      case 1:
        return renderInventorySizeStep();
      case 2:
        return renderLocationNeedsStep();
      case 3:
        return renderReviewStep();
      default:
        return null;
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      
      <Box sx={{ mb: 4 }}>
        {renderStepContent()}
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button
          disabled={activeStep === 0}
          onClick={handleBack}
          startIcon={<ArrowBack />}
        >
          Back
        </Button>
        
        <Box>
          <Button
            variant="outlined"
            onClick={onCancel}
            sx={{ mr: 2 }}
          >
            Cancel
          </Button>
          
          {activeStep === steps.length - 1 ? (
            <Button
              variant="contained"
              onClick={handleSubmit}
              endIcon={<CheckCircle />}
            >
              Complete Setup
            </Button>
          ) : (
            <Button
              variant="contained"
              onClick={handleNext}
              endIcon={<ArrowForward />}
            >
              Next
            </Button>
          )}
        </Box>
      </Box>
    </Box>
  );
};

export default OnboardingWizard;
