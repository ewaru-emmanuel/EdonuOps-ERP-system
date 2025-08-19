import React, { useState, useEffect } from 'react';
import {
  Box, TextField, Button, MenuItem, Stack, Alert, Chip, FormControl, InputLabel, Select, Checkbox, ListItemText
} from '@mui/material';
import { useCoA } from '../context/CoAContext';

const accountTypes = ['asset', 'liability', 'equity', 'revenue', 'expense'];

const CoAForm = ({ selectedAccount, onDone }) => {
  const { createAccount, updateAccount, dimensions, isAccountCodeUnique, getAccountHierarchy } = useCoA();
  const [form, setForm] = useState({
    code: '',
    name: '',
    type: '',
    currency: 'USD',
    parentId: null,
    allowed_dimensions: [],
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (selectedAccount) {
      setForm({
        code: selectedAccount.code,
        name: selectedAccount.name,
        type: selectedAccount.type,
        currency: selectedAccount.currency || 'USD',
        parentId: selectedAccount.parent_id || null,
        allowed_dimensions: selectedAccount.allowed_dimensions || [],
      });
    } else {
      setForm({ 
        code: '', 
        name: '', 
        type: '', 
        currency: 'USD',
        parentId: null,
        allowed_dimensions: [] 
      });
    }
    setError(null);
    setSuccess(null);
  }, [selectedAccount]);

  const handleSubmit = async () => {
    if (submitting) return;
    
    setError(null);
    setSubmitting(true);
    
    try {
      // Basic validation
      if (!form.code.trim()) {
        throw new Error('Account code is required');
      }
      if (!form.name.trim()) {
        throw new Error('Account name is required');
      }
      if (!form.type) {
        throw new Error('Account type is required');
      }
      
      // Code format validation
      if (!/^\d+$/.test(form.code)) {
        throw new Error('Account code must be numeric');
      }
      
      // Check uniqueness
      if (!isAccountCodeUnique(form.code, selectedAccount?.id)) {
        throw new Error('Account code already exists');
      }

      // Save
      if (selectedAccount) {
        await updateAccount(selectedAccount.id, form);
        setSuccess('Account updated successfully!');
      } else {
        await createAccount(form);
        setSuccess('Account created successfully!');
        setForm({ 
          code: '', 
          name: '', 
          type: '', 
          currency: 'USD',
          parentId: null,
          allowed_dimensions: [] 
        });
      }
      
      // Close form after short delay
      setTimeout(() => {
        onDone?.();
      }, 1500);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box mt={2}>
      <Stack spacing={2}>
        {error && <Alert severity="error">{error}</Alert>}
        {success && <Alert severity="success">{success}</Alert>}

        <TextField
          label="Account Code*"
          name="code"
          value={form.code}
          onChange={(e) => setForm({ ...form, code: e.target.value })}
          error={!!error && error.includes('code')}
          helperText="Numeric only (e.g., 1000, 1001, 2000)"
          disabled={submitting}
        />

        <TextField 
          label="Account Name*" 
          name="name" 
          value={form.name} 
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          error={!!error && error.includes('name')}
          disabled={submitting}
        />

        <TextField 
          select 
          label="Account Type*" 
          name="type" 
          value={form.type} 
          onChange={(e) => setForm({ ...form, type: e.target.value })}
          error={!!error && error.includes('type')}
          disabled={submitting}
        >
          {accountTypes.map((type) => (
            <MenuItem key={type} value={type}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </MenuItem>
          ))}
        </TextField>

        <TextField 
          select 
          label="Currency" 
          name="currency" 
          value={form.currency} 
          onChange={(e) => setForm({ ...form, currency: e.target.value })}
          disabled={submitting}
        >
          {['USD', 'EUR', 'GBP', 'CAD', 'AUD'].map((currency) => (
            <MenuItem key={currency} value={currency}>
              {currency}
            </MenuItem>
          ))}
        </TextField>

        <TextField 
          select 
          label="Parent Account" 
          name="parentId" 
          value={form.parentId || ''} 
          onChange={(e) => setForm({ ...form, parentId: e.target.value || null })}
          disabled={submitting}
          helperText="Leave empty for top-level accounts"
        >
          <MenuItem value="">None (Top Level)</MenuItem>
          {getAccountHierarchy && getAccountHierarchy()
            .filter(acc => acc.id !== selectedAccount?.id) // Don't allow self as parent
            .map((account) => (
              <MenuItem key={account.id} value={account.id}>
                {account.displayName}
              </MenuItem>
            ))}
        </TextField>

        <FormControl fullWidth>
          <InputLabel>Allowed Dimensions</InputLabel>
          <Select
            multiple
            value={form.allowed_dimensions}
            onChange={(e) => setForm({ ...form, allowed_dimensions: e.target.value })}
            renderValue={(selected) => selected.map(id => dimensions.find(d => d.id === id)?.name).join(', ')}
            disabled={submitting}
          >
            {dimensions.map((dim) => (
              <MenuItem key={dim.id} value={dim.id}>
                <Checkbox checked={form.allowed_dimensions.includes(dim.id)} />
                <ListItemText primary={dim.name} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button 
          variant="contained" 
          onClick={handleSubmit}
          disabled={submitting}
        >
          {submitting ? 'Saving...' : (selectedAccount ? 'Update Account' : 'Create Account')}
        </Button>
      </Stack>
    </Box>
  );
};

export default CoAForm;