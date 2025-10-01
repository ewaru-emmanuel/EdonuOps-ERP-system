import React, { useEffect, useState, useCallback } from 'react';
import {
  Grid, TextField, IconButton, Tooltip, Typography, 
  Autocomplete, Box, Chip, Stack, CircularProgress,
  Alert, Divider, Paper
} from '@mui/material';
import { AddCircle, RemoveCircle, Link, LinkOff, Search } from '@mui/icons-material';
import { useAuth } from '../../../context/AuthContext';
import apiClient from '../../../services/apiClient';
import { useCoA } from '../context/CoAContext';
import { debounce } from 'lodash';

const GLLineItems = ({ lineItems, onChange, onAdd, onRemove, readOnly = false }) => {
  const { user } = useAuth();
  const { dimensions } = useCoA();
  const [accounts, setAccounts] = useState([]);
  const [sourceDocs, setSourceDocs] = useState([]);
  const [loadingAccounts, setLoadingAccounts] = useState(false);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const [linkedDocs, setLinkedDocs] = useState({});

  // Load initial data
  useEffect(() => {
    setLoadingAccounts(true);
    setLoadingDocs(true);
    
    Promise.all([
      apiClient.get('/finance/accounts?limit=50'),
      apiClient.get('/finance/source_documents?limit=50'),
    ]).then(([accountsRes, docsRes]) => {
      setAccounts(accountsRes.data);
      setSourceDocs(docsRes.data);
    }).finally(() => {
      setLoadingAccounts(false);
      setLoadingDocs(false);
    });
  }, [apiClient]);

  // AI-powered account suggestions
  const fetchAccountSuggestions = useCallback(debounce(async (searchTerm) => {
    if (!searchTerm) return;
    
    setSuggestionsLoading(true);
    try {
      const res = await apiClient.post('/finance/ai/account-suggestions', {
        search_term: searchTerm,
        existing_lines: lineItems
      });
      setAiSuggestions(res.data.suggestions);
    } catch (error) {
      console.error('AI suggestion error:', error);
    } finally {
      setSuggestionsLoading(false);
    }
  }, 500), [apiClient, lineItems]);

  // Handle account search
  const handleAccountSearch = (searchTerm) => {
    if (searchTerm.length > 2) {
      fetchAccountSuggestions(searchTerm);
    }
  };

  // Handle account selection
  const handleChange = (idx, field, value) => {
    const updated = [...lineItems];
    updated[idx][field] = value;

    // Auto-fill account details when account code changes
    if (field === 'account_code') {
      const acc = accounts.find(a => a.code === value) || 
                 aiSuggestions.find(a => a.code === value);
      if (acc) {
        updated[idx].account_name = acc.name;
        updated[idx].account_id = acc.id;
        updated[idx].allowed_dimensions = acc.allowed_dimensions || [];
        
        // Auto-fill dimensions if this account typically uses specific values
        if (acc.common_dimensions) {
          updated[idx].dimensions = { ...updated[idx].dimensions, ...acc.common_dimensions };
        }
      }
    }

    // Validation: only debit OR credit
    if (field === 'debit_amount' && value) updated[idx].credit_amount = '';
    if (field === 'credit_amount' && value) updated[idx].debit_amount = '';

    onChange(updated);
  };

  // Handle dimension change
  const handleDimensionChange = (idx, dimId, value) => {
    const updated = [...lineItems];
    updated[idx].dimensions = updated[idx].dimensions || {};
    updated[idx].dimensions[dimId] = value;
    onChange(updated);
  };

  // Toggle document linking
  const toggleDocLink = (idx, doc) => {
    setLinkedDocs(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
    
    if (!linkedDocs[idx] && doc) {
      handleChange(idx, 'source_doc', doc);
    } else {
      handleChange(idx, 'source_doc', null);
    }
  };

  // Search for source documents
  const searchSourceDocs = useCallback(debounce(async (searchTerm) => {
    if (!searchTerm) return;
    setLoadingDocs(true);
    try {
      const res = await apiClient.get(`/finance/source_documents?search=${searchTerm}`);
      setSourceDocs(res.data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoadingDocs(false);
    }
  }, 500), [apiClient]);

  return (
    <Stack spacing={2}>
      {lineItems.map((line, idx) => (
        <Paper key={idx} variant="outlined" sx={{ p: 2 }}>
          <Grid container spacing={2} alignItems="center">
            {/* Account Selection */}
            <Grid item xs={12} sm={3}>
              <Autocomplete
                options={[...accounts, ...aiSuggestions].map(a => a.code)}
                value={line.account_code || null}
                onChange={(_, newVal) => handleChange(idx, 'account_code', newVal)}
                onInputChange={(_, value) => handleAccountSearch(value)}
                disabled={readOnly}
                loading={loadingAccounts || suggestionsLoading}
                isOptionEqualToValue={(option, value) => option === value}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Account Code"
                    size="small"
                    fullWidth
                    required
                    error={!line.account_code}
                    InputProps={{
                      ...params.InputProps,
                      endAdornment: (
                        <>
                          {loadingAccounts || suggestionsLoading ? (
                            <CircularProgress color="inherit" size={20} />
                          ) : null}
                          {params.InputProps.endAdornment}
                        </>
                      ),
                    }}
                  />
                )}
                renderOption={(props, option) => {
                  const account = [...accounts, ...aiSuggestions].find(a => a.code === option);
                  return (
                    <li {...props} key={option}>
                      <Stack>
                        <Typography variant="body2">{option}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {account?.name}
                        </Typography>
                        {aiSuggestions.some(a => a.code === option) && (
                          <Chip label="AI Suggestion" size="small" sx={{ mt: 0.5 }} />
                        )}
                      </Stack>
                    </li>
                  );
                }}
              />
            </Grid>

            {/* Account Name */}
            <Grid item xs={12} sm={2}>
              <TextField
                label="Account Name"
                size="small"
                fullWidth
                value={line.account_name || ''}
                disabled
              />
            </Grid>

            {/* Dynamic Dimensions */}
            <Grid item xs={12} sm={3}>
              <Stack spacing={1}>
                {line.allowed_dimensions?.map(dimId => {
                  const dimension = dimensions.find(d => d.id === dimId);
                  if (!dimension) return null;
                  
                  return (
                    <Autocomplete
                      key={dimId}
                      options={dimension.values || []}
                      value={line.dimensions?.[dimId] || null}
                      onChange={(_, newVal) => handleDimensionChange(idx, dimId, newVal)}
                      disabled={readOnly}
                      isOptionEqualToValue={(option, value) => option === value}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label={dimension.name}
                          size="small"
                          fullWidth
                        />
                      )}
                      renderOption={(props, option) => (
                        <li {...props} key={option}>
                          <Stack>
                            <Typography>{option}</Typography>
                            {dimension.descriptions?.[option] && (
                              <Typography variant="caption" color="text.secondary">
                                {dimension.descriptions[option]}
                              </Typography>
                            )}
                          </Stack>
                        </li>
                      )}
                    />
                  );
                })}
                {(!line.allowed_dimensions || line.allowed_dimensions.length === 0) && (
                  <Typography variant="caption" color="text.secondary">
                    No dimensions required
                  </Typography>
                )}
              </Stack>
            </Grid>

            {/* Source Document Linking */}
            <Grid item xs={12} sm={3}>
              <Stack spacing={1}>
                <Autocomplete
                  options={sourceDocs}
                  getOptionLabel={(doc) => `${doc.type} #${doc.number} - ${doc.description}`}
                  value={line.source_doc || null}
                  onChange={(_, newVal) => handleChange(idx, 'source_doc', newVal)}
                  onInputChange={(_, value) => searchSourceDocs(value)}
                  disabled={readOnly}
                  loading={loadingDocs}
                  isOptionEqualToValue={(option, value) => option.id === value?.id}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Source Document"
                      size="small"
                      fullWidth
                      InputProps={{
                        ...params.InputProps,
                        startAdornment: (
                          <>
                            <Tooltip title={linkedDocs[idx] ? "Unlink document" : "Link document"}>
                              <IconButton
                                size="small"
                                onClick={() => toggleDocLink(idx, line.source_doc)}
                                color={linkedDocs[idx] ? "primary" : "default"}
                              >
                                {linkedDocs[idx] ? <Link /> : <LinkOff />}
                              </IconButton>
                            </Tooltip>
                            {params.InputProps.startAdornment}
                          </>
                        ),
                        endAdornment: (
                          <>
                            {loadingDocs ? (
                              <CircularProgress color="inherit" size={20} />
                            ) : (
                              <Search />
                            )}
                            {params.InputProps.endAdornment}
                          </>
                        ),
                      }}
                    />
                  )}
                  renderOption={(props, option) => (
                    <li {...props} key={option.id}>
                      <Stack>
                        <Typography variant="subtitle2">
                          {option.type} #{option.number}
                        </Typography>
                        <Typography variant="body2">{option.description}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(option.date).toLocaleDateString()} • ${option.amount}
                        </Typography>
                      </Stack>
                    </li>
                  )}
                />
                {line.source_doc && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label="Linked"
                      size="small"
                      color="success"
                      variant="outlined"
                      icon={<Link fontSize="small" />}
                    />
                    <Typography variant="caption">
                      {line.source_doc.type} #{line.source_doc.number}
                    </Typography>
                  </Box>
                )}
              </Stack>
            </Grid>

            {/* Debit/Credit */}
            <Grid item xs={6} sm={1}>
              <TextField
                label="Debit"
                type="number"
                size="small"
                fullWidth
                value={line.debit_amount || ''}
                onChange={(e) => handleChange(idx, 'debit_amount', e.target.value)}
                disabled={readOnly}
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>
            <Grid item xs={6} sm={1}>
              <TextField
                label="Credit"
                type="number"
                size="small"
                fullWidth
                value={line.credit_amount || ''}
                onChange={(e) => handleChange(idx, 'credit_amount', e.target.value)}
                disabled={readOnly}
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>

            {/* Add/Remove */}
            {!readOnly && (
              <Grid item xs={12} sm={1}>
                <Box display="flex" gap={1} justifyContent="flex-end">
                  <Tooltip title="Add line">
                    <IconButton onClick={onAdd} color="primary" size="small">
                      <AddCircle />
                    </IconButton>
                  </Tooltip>
                  {lineItems.length > 1 && (
                    <Tooltip title="Remove line">
                      <IconButton 
                        onClick={() => onRemove(idx)} 
                        color="error" 
                        size="small"
                      >
                        <RemoveCircle />
                      </IconButton>
                    </Tooltip>
                  )}
                </Box>
              </Grid>
            )}
          </Grid>

          {/* AI Suggestions Panel */}
          {aiSuggestions.length > 0 && idx === lineItems.length - 1 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  AI Suggestions
                </Typography>
                <Stack spacing={1}>
                  {aiSuggestions.map((suggestion, i) => (
                    <Paper 
                      key={i} 
                      variant="outlined" 
                      sx={{ p: 1, cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}
                      onClick={() => {
                        handleChange(idx, 'account_code', suggestion.code);
                        setAiSuggestions([]);
                      }}
                    >
                      <Stack direction="row" justifyContent="space-between">
                        <Typography variant="body2">
                          <strong>{suggestion.code}</strong> - {suggestion.name}
                        </Typography>
                        <Chip 
                          label={`${suggestion.confidence}% match`} 
                          size="small" 
                          color={
                            suggestion.confidence > 80 ? 'success' :
                            suggestion.confidence > 60 ? 'warning' : 'default'
                          }
                        />
                      </Stack>
                      {suggestion.reason && (
                        <Typography variant="caption" color="text.secondary">
                          {suggestion.reason}
                        </Typography>
                      )}
                    </Paper>
                  ))}
                </Stack>
              </Box>
            </>
          )}
        </Paper>
      ))}
    </Stack>
  );
};

export default GLLineItems;