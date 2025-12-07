import React, { useState, useEffect } from 'react';
import {
  Box, TextField, Button, MenuItem, Stack, Alert, Chip, FormControl, InputLabel, Select, Checkbox, ListItemText
} from '@mui/material';
import { useCoA } from '../context/CoAContext';
import apiClient from '../../../services/apiClient';

const accountTypes = ['asset', 'liability', 'equity', 'revenue', 'expense'];

const CoAForm = ({ selectedAccount, onDone, allAccounts = [], showAccountCodes = false }) => {
  const { addAccount, updateAccount } = useCoA();
  const [form, setForm] = useState({
    code: '',
    name: '',
    category: '',
    type: '',
    description: '',
    parent_id: null,
    isActive: true,
    notes: '',
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (selectedAccount) {
      setForm({
        code: selectedAccount.code || '',
        name: selectedAccount.account_name || selectedAccount.name || '',
        category: selectedAccount.category || '',
        type: selectedAccount.account_type || selectedAccount.type || '',
        description: selectedAccount.description || '',
        parent_id: selectedAccount.parent_id || null,
        isActive: selectedAccount.is_active !== false,
        notes: selectedAccount.notes || '',
      });
    } else {
      setForm({ 
        code: '',
        name: '', 
        category: '', 
        type: '', 
        description: '',
        parent_id: null,
        isActive: true,
        notes: ''
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
      if (!form.name.trim()) {
        throw new Error('Account name is required');
      }
      if (!form.type) {
        throw new Error('Account type is required');
      }

      // Prepare data for API
      const accountData = {
        name: form.name,
        type: form.type,
        code: form.code || undefined,
        description: form.description || undefined,
        parent_id: form.parent_id || null,
        is_active: form.isActive,
        notes: form.notes || undefined
      };

      // Save via API
      if (selectedAccount) {
        await apiClient.put(`/api/finance/double-entry/accounts/${selectedAccount.id}`, accountData);
        setSuccess('Account updated successfully!');
      } else {
        await apiClient.post('/api/finance/double-entry/accounts', accountData);
        setSuccess('Account created successfully!');
        setForm({ 
          code: '',
          name: '', 
          category: '', 
          type: '', 
          description: '',
          parent_id: null,
          isActive: true
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

        {showAccountCodes && (
          <TextField 
            label="Account Code" 
            name="code" 
            value={form.code} 
            onChange={(e) => setForm({ ...form, code: e.target.value })}
            disabled={submitting || !!selectedAccount} // Disable when editing (code shouldn't change)
            helperText={selectedAccount ? "Account code cannot be changed after creation" : "Optional - leave blank for auto-generation"}
            sx={{ fontFamily: 'monospace' }}
          />
        )}

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
          fullWidth
        >
          {accountTypes.map((type) => (
            <MenuItem key={type} value={type}>
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </MenuItem>
          ))}
        </TextField>

        {allAccounts.length > 0 && (
          <FormControl fullWidth>
            <InputLabel>Parent Account (Optional)</InputLabel>
            <Select
              value={form.parent_id || ''}
              onChange={(e) => setForm({ ...form, parent_id: e.target.value || null })}
              label="Parent Account (Optional)"
              disabled={submitting}
            >
              <MenuItem value="">None (Top Level)</MenuItem>
              {allAccounts
                .filter(acc => !selectedAccount || acc.id !== selectedAccount.id) // Don't allow self as parent
                .map((account) => (
                  <MenuItem key={account.id} value={account.id}>
                    {account.account_name || account.name}
                  </MenuItem>
                ))}
            </Select>
          </FormControl>
        )}

        <TextField 
          label="Description" 
          name="description" 
          value={form.description} 
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          multiline
          rows={2}
          placeholder="Optional description for this account"
          disabled={submitting}
        />

        <TextField 
          label="Notes" 
          name="notes" 
          value={form.notes} 
          onChange={(e) => setForm({ ...form, notes: e.target.value })}
          multiline
          rows={3}
          placeholder="Additional notes, documentation, or reference information"
          disabled={submitting}
          helperText="Use this field to store account-specific notes, documentation links, or reference information"
        />

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