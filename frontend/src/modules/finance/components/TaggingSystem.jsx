import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  IconButton,
  Badge,
  CircularProgress
} from '@mui/material';
import {
  Label as LabelIcon,
  AccountBalance as LedgerIcon,
  Analytics as AnalyticsIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon
} from '@mui/icons-material';
import { apiClient } from '../../../utils/apiClient';

const TaggingSystem = ({ accountCode, onTagsChange, initialTags = {} }) => {
  const [tagCategories, setTagCategories] = useState([]);
  const [accountRules, setAccountRules] = useState(null);
  const [tags, setTags] = useState(initialTags);
  const [validation, setValidation] = useState({ isValid: true, errors: [] });
  const [suggestions, setSuggestions] = useState({});
  const [loading, setLoading] = useState(false);
  const [showDistinction, setShowDistinction] = useState(false);
  const [distinction, setDistinction] = useState(null);

  useEffect(() => {
    if (accountCode) {
      loadAccountRules();
      loadSuggestions();
    }
    loadTagCategories();
    loadDistinction();
  }, [accountCode]);

  const loadTagCategories = async () => {
    try {
      const response = await apiClient.get('/api/finance/tagging/categories');
      setTagCategories(response.data.categories || []);
    } catch (err) {
      console.error('Error loading tag categories:', err);
    }
  };

  const loadAccountRules = async () => {
    if (!accountCode) return;
    
    try {
      setLoading(true);
      const response = await apiClient.get(`/api/finance/tagging/rules/account/${accountCode}`);
      setAccountRules(response.data);
    } catch (err) {
      console.error('Error loading account rules:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSuggestions = async () => {
    if (!accountCode) return;
    
    try {
      const response = await apiClient.post('/api/finance/tagging/suggestions', {
        account_code: accountCode,
        partial_tags: tags
      });
      setSuggestions(response.data.suggestions || {});
    } catch (err) {
      console.error('Error loading suggestions:', err);
    }
  };

  const loadDistinction = async () => {
    try {
      const response = await apiClient.get('/api/finance/tagging/distinction');
      setDistinction(response.data);
    } catch (err) {
      console.error('Error loading distinction:', err);
    }
  };

  const validateTags = async () => {
    if (!accountCode) return;
    
    try {
      const response = await apiClient.post('/api/finance/tagging/validate', {
        account_code: accountCode,
        tags: tags
      });
      
      setValidation({
        isValid: response.data.is_valid,
        errors: response.data.errors || []
      });
      
      return response.data.is_valid;
    } catch (err) {
      console.error('Error validating tags:', err);
      return false;
    }
  };

  const handleTagChange = (categoryId, value) => {
    const newTags = { ...tags, [categoryId]: value };
    setTags(newTags);
    onTagsChange?.(newTags);
    
    // Auto-validate after a short delay
    setTimeout(() => {
      validateTags();
    }, 500);
  };

  const handleSuggestionSelect = (categoryId, suggestion) => {
    handleTagChange(categoryId, suggestion);
  };

  const getCategoryInfo = (categoryId) => {
    return tagCategories.find(cat => cat.id === categoryId);
  };

  const isRequired = (categoryId) => {
    return accountRules?.required_tags?.some(tag => tag.id === categoryId) || false;
  };

  const isOptional = (categoryId) => {
    return accountRules?.optional_tags?.some(tag => tag.id === categoryId) || false;
  };

  const renderTagInput = (categoryId) => {
    const category = getCategoryInfo(categoryId);
    if (!category) return null;

    const isRequiredField = isRequired(categoryId);
    const isOptionalField = isOptional(categoryId);
    const categorySuggestions = suggestions[categoryId] || [];
    const validationRules = category.validation_rules || {};

    return (
      <Box key={categoryId} sx={{ mb: 2 }}>
        <FormControl fullWidth>
          <InputLabel>
            {category.name}
            {isRequiredField && ' *'}
            {isOptionalField && !isRequiredField && ' (Optional)'}
          </InputLabel>
          <Select
            value={tags[categoryId] || ''}
            onChange={(e) => handleTagChange(categoryId, e.target.value)}
            label={`${category.name}${isRequiredField ? ' *' : ''}`}
            error={isRequiredField && !tags[categoryId]}
          >
            <MenuItem value="">
              <em>Select {category.name}</em>
            </MenuItem>
            {categorySuggestions.map(suggestion => (
              <MenuItem 
                key={suggestion} 
                value={suggestion}
                onClick={() => handleSuggestionSelect(categoryId, suggestion)}
              >
                {suggestion}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        {category.description && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            {category.description}
          </Typography>
        )}
        
        {validationRules.max_length && (
          <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
            Max length: {validationRules.max_length} characters
          </Typography>
        )}
        
        {validationRules.allowed_values && (
          <Box sx={{ mt: 1 }}>
            <Typography variant="caption" color="text.secondary" display="block">
              Allowed values:
            </Typography>
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 0.5 }}>
              {validationRules.allowed_values.map(value => (
                <Chip
                  key={value}
                  label={value}
                  size="small"
                  variant="outlined"
                  onClick={() => handleSuggestionSelect(categoryId, value)}
                />
              ))}
            </Box>
          </Box>
        )}
      </Box>
    );
  };

  const renderValidationErrors = () => {
    if (validation.errors.length === 0) return null;

    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Validation Errors:
        </Typography>
        {validation.errors.map((error, index) => (
          <Typography key={index} variant="body2" display="block">
            • {error}
          </Typography>
        ))}
      </Alert>
    );
  };

  const renderAccountRules = () => {
    if (!accountRules) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Tagging Rules for {accountRules.account_name} ({accountRules.account_code})
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Required Tags ({accountRules.total_required})
              </Typography>
              {accountRules.required_tags.length > 0 ? (
                <List dense>
                  {accountRules.required_tags.map(tag => (
                    <ListItem key={tag.id}>
                      <ListItemIcon>
                        <CheckCircleIcon color="error" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={tag.name}
                        secondary={tag.description}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No required tags for this account
                </Typography>
              )}
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>
                Optional Tags ({accountRules.total_optional})
              </Typography>
              {accountRules.optional_tags.length > 0 ? (
                <List dense>
                  {accountRules.optional_tags.map(tag => (
                    <ListItem key={tag.id}>
                      <ListItemIcon>
                        <InfoIcon color="info" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={tag.name}
                        secondary={tag.description}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No optional tags for this account
                </Typography>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const renderDistinctionDialog = () => {
    if (!distinction) return null;

    return (
      <Dialog
        open={showDistinction}
        onClose={() => setShowDistinction(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Ledger Accounts vs Tags - Understanding the Difference
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <LedgerIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Ledger Accounts</Typography>
                  </Box>
                  <Typography variant="body2" paragraph>
                    {distinction.ledger_accounts.description}
                  </Typography>
                  <Typography variant="subtitle2" gutterBottom>
                    Characteristics:
                  </Typography>
                  <List dense>
                    {distinction.ledger_accounts.characteristics.map((char, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <CheckCircleIcon color="primary" />
                        </ListItemIcon>
                        <ListItemText primary={char} />
                      </ListItem>
                    ))}
                  </List>
                  <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                    Examples:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {distinction.ledger_accounts.examples.map(example => (
                      <Chip key={example} label={example} size="small" />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <LabelIcon color="secondary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Tags</Typography>
                  </Box>
                  <Typography variant="body2" paragraph>
                    {distinction.tags.description}
                  </Typography>
                  <Typography variant="subtitle2" gutterBottom>
                    Characteristics:
                  </Typography>
                  <List dense>
                    {distinction.tags.characteristics.map((char, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <InfoIcon color="secondary" />
                        </ListItemIcon>
                        <ListItemText primary={char} />
                      </ListItem>
                    ))}
                  </List>
                  <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                    Examples:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {distinction.tags.examples.map(example => (
                      <Chip key={example} label={example} size="small" color="secondary" />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="h6" gutterBottom>
            Key Rules
          </Typography>
          <List>
            {distinction.rules.map((rule, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <WarningIcon color="warning" />
                </ListItemIcon>
                <ListItemText primary={rule} />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDistinction(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6">
          Transaction Tagging
        </Typography>
        <Button
          variant="outlined"
          startIcon={<InfoIcon />}
          onClick={() => setShowDistinction(true)}
        >
          Learn About Tags
        </Button>
      </Box>

      {/* Account Rules */}
      {renderAccountRules()}

      {/* Validation Errors */}
      {renderValidationErrors()}

      {/* Tag Inputs */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Required Tags
          </Typography>
          {accountRules?.required_tags?.map(tag => renderTagInput(tag.id))}
          
          {accountRules?.optional_tags && accountRules.optional_tags.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Optional Tags
              </Typography>
              {accountRules.optional_tags.map(tag => renderTagInput(tag.id))}
            </>
          )}
        </CardContent>
      </Card>

      {/* Current Tags Summary */}
      {Object.keys(tags).length > 0 && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Tags
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {Object.entries(tags).map(([categoryId, value]) => {
                const category = getCategoryInfo(categoryId);
                return (
                  <Chip
                    key={categoryId}
                    label={`${category?.name || categoryId}: ${value}`}
                    color={isRequired(categoryId) ? 'error' : 'default'}
                    variant={isRequired(categoryId) ? 'filled' : 'outlined'}
                    onDelete={() => handleTagChange(categoryId, '')}
                  />
                );
              })}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Distinction Dialog */}
      {renderDistinctionDialog()}
    </Box>
  );
};

export default TaggingSystem;


