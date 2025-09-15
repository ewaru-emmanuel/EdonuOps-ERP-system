import React, { useState, useEffect } from 'react';
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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  IconButton,
  CircularProgress,
  Divider
} from '@mui/material';
import {
  Public as PublicIcon,
  AccountBalance as AccountBalanceIcon,
  Receipt as ReceiptIcon,
  TrendingUp as TrendingUpIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon,
  Flag as FlagIcon,
  CurrencyExchange as CurrencyIcon,
  Description as FormIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { apiClient } from '../../../utils/apiClient';

const LocalizationManager = ({ onCountryChange, selectedCountry = 'US' }) => {
  const [countries, setCountries] = useState([]);
  const [compliancePack, setCompliancePack] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showSetupDialog, setShowSetupDialog] = useState(false);
  const [selectedIndustries, setSelectedIndustries] = useState([]);
  const [selectedModules, setSelectedModules] = useState([]);
  const [setupConfig, setSetupConfig] = useState(null);

  useEffect(() => {
    loadCountries();
    if (selectedCountry) {
      loadCompliancePack(selectedCountry);
    }
  }, [selectedCountry]);

  const loadCountries = async () => {
    try {
      const response = await apiClient.get('/api/finance/localization/countries');
      setCountries(response.data.countries || []);
    } catch (err) {
      setError('Failed to load countries');
      console.error('Error loading countries:', err);
    }
  };

  const loadCompliancePack = async (countryCode) => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/finance/localization/countries/${countryCode}/compliance`);
      setCompliancePack(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to load compliance pack');
      console.error('Error loading compliance pack:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCountryChange = (countryCode) => {
    onCountryChange?.(countryCode);
    loadCompliancePack(countryCode);
  };

  const handleSetupCompliance = async () => {
    try {
      const response = await apiClient.post(`/api/finance/localization/countries/${selectedCountry}/setup`, {
        industries: selectedIndustries,
        modules: selectedModules
      });
      
      setSetupConfig(response.data);
      setShowSetupDialog(true);
    } catch (err) {
      setError('Failed to setup compliance');
      console.error('Error setting up compliance:', err);
    }
  };

  const renderCountryCard = (country) => (
    <Card 
      key={country.code}
      sx={{ 
        cursor: 'pointer',
        border: selectedCountry === country.code ? 2 : 1,
        borderColor: selectedCountry === country.code ? 'primary.main' : 'divider',
        '&:hover': { boxShadow: 4 }
      }}
      onClick={() => handleCountryChange(country.code)}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <FlagIcon sx={{ fontSize: 32 }} />
          <Box>
            <Typography variant="h6">{country.name}</Typography>
            <Typography variant="body2" color="text.secondary">
              {country.code} • {country.currency} • {country.accounting_standard}
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip label={country.currency} size="small" icon={<CurrencyIcon />} />
          <Chip label={country.accounting_standard} size="small" />
        </Box>
      </CardContent>
    </Card>
  );

  const renderCompliancePack = () => {
    if (!compliancePack) return null;

    return (
      <Box>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            {compliancePack.country_name} Compliance Pack
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph>
            Complete compliance package for {compliancePack.country_name} including 
            CoA templates, statutory modules, tax rates, and compliance forms.
          </Typography>
        </Box>

        {/* Overview Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <AccountBalanceIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h4">{Object.keys(compliancePack.coa_templates).length}</Typography>
                <Typography variant="body2" color="text.secondary">
                  CoA Templates
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <SettingsIcon color="secondary" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h4">{Object.keys(compliancePack.statutory_modules).length}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Statutory Modules
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <TrendingUpIcon color="success" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h4">{Object.keys(compliancePack.tax_rates).length}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Tax Rates
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <FormIcon color="warning" sx={{ fontSize: 40, mb: 1 }} />
                <Typography variant="h4">{Object.keys(compliancePack.compliance_forms).length}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Compliance Forms
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* CoA Templates */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Chart of Accounts Templates</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {Object.entries(compliancePack.coa_templates).map(([industry, template]) => (
                <Grid item xs={12} sm={6} md={4} key={industry}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {template.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {template.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Chip label={`${template.account_count} accounts`} size="small" />
                        <Chip label={industry} size="small" color="primary" />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </AccordionDetails>
        </Accordion>

        {/* Statutory Modules */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Statutory Modules</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <List>
              {Object.entries(compliancePack.statutory_modules).map(([moduleId, module]) => (
                <ListItem key={moduleId}>
                  <ListItemIcon>
                    <CheckCircleIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={module.name}
                    secondary={module.description}
                  />
                  <ListItemSecondaryAction>
                    <Chip label={`${module.compliance_forms.length} forms`} size="small" />
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>

        {/* Tax Rates */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Tax Rates</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Tax Type</TableCell>
                    <TableCell align="right">Rate</TableCell>
                    <TableCell>Description</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(compliancePack.tax_rates).map(([taxType, taxData]) => (
                    <TableRow key={taxType}>
                      <TableCell>{taxType.replace('_', ' ').toUpperCase()}</TableCell>
                      <TableCell align="right">
                        {(taxData.rate * 100).toFixed(2)}%
                      </TableCell>
                      <TableCell>{taxData.description}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>

        {/* Compliance Forms */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">Compliance Forms</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <List>
              {Object.entries(compliancePack.compliance_forms).map(([formId, formData]) => (
                <ListItem key={formId}>
                  <ListItemIcon>
                    <FormIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary={formData.name}
                    secondary={`${formData.frequency} • Due: ${formData.due_date}`}
                  />
                  <ListItemSecondaryAction>
                    <Chip label={formData.frequency} size="small" color="primary" />
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </AccordionDetails>
        </Accordion>

        {/* Setup Button */}
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => setShowSetupDialog(true)}
            startIcon={<SettingsIcon />}
          >
            Setup {compliancePack.country_name} Compliance
          </Button>
        </Box>
      </Box>
    );
  };

  const renderSetupDialog = () => {
    if (!compliancePack) return null;

    return (
      <Dialog
        open={showSetupDialog}
        onClose={() => setShowSetupDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Setup {compliancePack.country_name} Compliance
        </DialogTitle>
        <DialogContent>
          <Typography variant="body1" paragraph>
            Select the industries and statutory modules you need for your business.
          </Typography>

          {/* Industry Selection */}
          <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
            Select Industries
          </Typography>
          <Grid container spacing={1}>
            {Object.entries(compliancePack.coa_templates).map(([industry, template]) => (
              <Grid item xs={12} sm={6} key={industry}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={selectedIndustries.includes(industry)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedIndustries([...selectedIndustries, industry]);
                        } else {
                          setSelectedIndustries(selectedIndustries.filter(i => i !== industry));
                        }
                      }}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2">{template.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {template.account_count} accounts
                      </Typography>
                    </Box>
                  }
                />
              </Grid>
            ))}
          </Grid>

          <Divider sx={{ my: 2 }} />

          {/* Module Selection */}
          <Typography variant="h6" gutterBottom>
            Select Statutory Modules
          </Typography>
          <Grid container spacing={1}>
            {Object.entries(compliancePack.statutory_modules).map(([moduleId, module]) => (
              <Grid item xs={12} sm={6} key={moduleId}>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={selectedModules.includes(moduleId)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedModules([...selectedModules, moduleId]);
                        } else {
                          setSelectedModules(selectedModules.filter(m => m !== moduleId));
                        }
                      }}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2">{module.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {module.compliance_forms.length} forms required
                      </Typography>
                    </Box>
                  }
                />
              </Grid>
            ))}
          </Grid>

          {/* Setup Summary */}
          {setupConfig && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Setup Summary:
              </Typography>
              <Typography variant="body2">
                • {setupConfig.estimated_accounts} accounts will be created
              </Typography>
              <Typography variant="body2">
                • {setupConfig.compliance_forms_required.length} compliance forms will be required
              </Typography>
              <Typography variant="body2">
                • Currency: {setupConfig.currency}
              </Typography>
              <Typography variant="body2">
                • Accounting Standard: {setupConfig.accounting_standard}
              </Typography>
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSetupDialog(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleSetupCompliance}
            variant="contained"
            disabled={selectedIndustries.length === 0}
          >
            Setup Compliance
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Country Selection */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Country & Compliance Setup
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Select your country to get a complete compliance package tailored to your local requirements.
        </Typography>
        
        <Grid container spacing={2}>
          {countries.map(renderCountryCard)}
        </Grid>
      </Box>

      {/* Compliance Pack Details */}
      {renderCompliancePack()}

      {/* Setup Dialog */}
      {renderSetupDialog()}
    </Box>
  );
};

export default LocalizationManager;


